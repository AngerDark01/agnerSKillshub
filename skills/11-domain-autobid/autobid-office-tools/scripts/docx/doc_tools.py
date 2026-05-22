"""
scripts/docx/doc_tools.py
=========================
三个能力，统一坐标（body_idx），纯 Python / lxml / zipfile。

能力一：inspect(docx_path)
    读结构和内容。返回 body 元素列表 + 候选节点 + 内容预览。
    所有定位坐标均为 body_idx（body 直属子元素的序号，段落和表格共享）。

能力二：split_by_range(docx_path, start, end, out_path)
    按 body_idx 范围提取子文档。
    agent 先调 inspect 识别边界，再调这个工具切。

能力三：join_by_manifest(manifest, out_path)
    按清单拼接，支持两种输入：
      模式A：[{"source": "orig.docx", "start": 0, "end": 100}, ...]  从同一/不同原始文件按范围取
      模式B：["part1.docx", "part2.docx", ...]                       多个已修改子文档按顺序拼

三个工具用同一套 body_idx 坐标，split 切出的范围可以直接喂给 join。
"""

import zipfile
import json
import re
import copy
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from lxml import etree

W  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


# ══════════════════════════════════════════════════════════════
# 内部工具函数
# ══════════════════════════════════════════════════════════════

def _resolve_source(source: str) -> Tuple[bytes, List[str]]:
    """
    统一读取入口：source 可以是 .docx 文件路径，也可以是 unpacked_dir 目录路径。

    返回 (doc_bytes, names)：
        doc_bytes  word/document.xml 的原始字节
        names      ZIP 成员名列表（unpacked_dir 时模拟，仅包含实际存在的文件名）
    """
    p = Path(source)
    if p.is_dir():
        # unpacked 目录模式：直接读 word/document.xml
        xml_path = p / "word" / "document.xml"
        if not xml_path.exists():
            raise ValueError(f"{source} 不是有效的 unpacked 目录（缺少 word/document.xml）")
        doc_bytes = xml_path.read_bytes()
        # 模拟 names：扫描目录下所有文件，转为相对路径
        names = [str(f.relative_to(p)).replace("\\", "/") for f in p.rglob("*") if f.is_file()]
        return doc_bytes, names
    else:
        # .docx ZIP 模式
        with zipfile.ZipFile(str(p)) as zf:
            names = zf.namelist()
            doc_bytes = zf.read("word/document.xml")
        return doc_bytes, names


def _read_body_children(docx_path: str) -> Tuple[etree._Element, List[etree._Element], Optional[etree._Element]]:
    """
    读取 docx 的 document.xml，返回：
      (body_element, body_children_list, doc_level_sectPr_or_None)

    body_children_list 是 body 的直属子元素列表，
    不包含末尾独立的 sectPr（Word 规范：body 最后一个元素可能是裸 sectPr）。
    body_idx = 该列表的下标。
    """
    with zipfile.ZipFile(docx_path) as zf:
        doc_bytes = zf.read("word/document.xml")

    tree = etree.fromstring(doc_bytes)
    body = tree.find("w:body", NS)
    if body is None:
        raise ValueError(f"{docx_path}: document.xml 中找不到 w:body")

    all_children = list(body)
    doc_sectPr = None

    # Word 规范：body 最后一个直属子元素如果是裸 sectPr，它是文档级页面设置，不计入内容
    if all_children and all_children[-1].tag == f"{{{W}}}sectPr":
        doc_sectPr = all_children[-1]
        children = all_children[:-1]
    else:
        children = all_children

    return body, children, doc_sectPr


def _zip_copy_replace_document(src_path: str, out_path: str, new_doc_bytes: bytes):
    """
    以 src_path 为模板复制整个 ZIP，只替换 word/document.xml。
    保留所有 styles / numbering / media / embeddings / relationships。
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src_path, 'r') as src_zip:
        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
            for name in src_zip.namelist():
                if name == "word/document.xml":
                    out_zip.writestr(name, new_doc_bytes)
                else:
                    out_zip.writestr(name, src_zip.read(name))


def _build_new_document_xml(
    template_tree: etree._Element,
    new_children: List[etree._Element],
    fallback_sectPr: Optional[etree._Element],
) -> bytes:
    """
    用新的子元素列表替换 body 内容，确保末尾有合法 sectPr，序列化返回。
    """
    # 找末尾的 sectPr：优先取 new_children 中最后一段 pPr 里内联的 sectPr
    final_sectPr = None
    if new_children:
        last = new_children[-1]
        if last.tag == f"{{{W}}}p":
            pPr = last.find("w:pPr", NS)
            if pPr is not None:
                inline = pPr.find("w:sectPr", NS)
                if inline is not None:
                    final_sectPr = copy.deepcopy(inline)
                    pPr.remove(inline)  # 从 pPr 摘出，改为文档末尾独立节点

    if final_sectPr is None and fallback_sectPr is not None:
        final_sectPr = copy.deepcopy(fallback_sectPr)

    # 不在原大树上原地清空 body。该操作在大文档上非常慢。
    new_root = etree.Element(template_tree.tag, nsmap=template_tree.nsmap)
    for key, value in template_tree.attrib.items():
        new_root.set(key, value)
    body = etree.SubElement(new_root, f"{{{W}}}body")

    for child in new_children:
        body.append(child)
    if final_sectPr is not None:
        body.append(final_sectPr)

    return etree.tostring(new_root, xml_declaration=True,
                          encoding="UTF-8", standalone=True)


# ══════════════════════════════════════════════════════════════
# 能力一：inspect
# ══════════════════════════════════════════════════════════════

def inspect(
    source: str,
    body_range: Optional[Tuple[int, int]] = None,
    include_elements: bool = False,
    skeleton_text_max: int = 25,
) -> dict:
    """
    读取文档结构和内容。

    参数：
        source:            .docx 文件路径 或 unpacked_dir 目录路径
                           两种形态均支持，unpack 后继续 inspect 可看到最新写入状态
        body_range:        (start, end) 只分析这个范围；None = 全文
        include_elements:  True 时返回当前扫描范围内的 body_elements 列表
                           信号不足时 AI 读这个列表自己判断边界
        skeleton_text_max: skeleton 短行阈值（默认 25 字）；
                           skeleton 始终返回，无需额外参数

    返回 dict：
        file_info         文件基础统计
        signals           结构信号（含置信度和证据）
        candidate_nodes   基于信号自动划分的候选节点
        content_previews  各节点内容采样
        skeleton          短行骨架视图，默认路径；AI 先看这个推正则，
                          不够用再用 body_range 局部扩展，
                          最坏情况才用 include_elements=True 分批全量
        body_elements     当前扫描范围内的 body 元素序列（include_elements=True 时）
                          每个段落元素包含 para_id 字段，可直接传给 write tools
    """
    # ── 读取并解析 document.xml ────────────────────────────
    doc_bytes, names = _resolve_source(source)

    tree = etree.fromstring(doc_bytes)
    body = tree.find("w:body", NS)
    all_children = list(body)

    # 末尾裸 sectPr 不计入 body_idx
    if all_children and all_children[-1].tag == f"{{{W}}}sectPr":
        children = all_children[:-1]
    else:
        children = all_children

    # ── 构建 body 元素列表 ─────────────────────────────────
    elements = _parse_elements(children)

    # 应用 body_range 过滤
    rng_start = body_range[0] if body_range else 0
    rng_end   = body_range[1] if body_range else len(elements)
    scoped = [e for e in elements if rng_start <= e["body_idx"] < rng_end]

    # ── 信号检测 ──────────────────────────────────────────
    signals = _detect_signals(elements)  # 全文检测，信号是文件级的

    # ── 候选节点划分 ──────────────────────────────────────
    candidate_nodes = _build_candidate_nodes(scoped, signals)

    # ── 内容预览 ──────────────────────────────────────────
    previews = _build_previews(elements, candidate_nodes)

    # ── 文件信息 ──────────────────────────────────────────
    p_count    = sum(1 for e in elements if e["type"] == "p")
    tbl_count  = sum(1 for e in elements if e["type"] == "tbl")
    sect_count = sum(1 for e in elements if e["type"] == "p" and e["has_sectPr"])

    _src = Path(source).resolve()
    file_info = {
        "source": str(_src),
        "source_type": "unpacked_dir" if _src.is_dir() else "docx",
        "filename": _src.name,
        "total_body_elements": len(elements),
        "para_count":  p_count,
        "table_count": tbl_count,
        "sectPr_count": sect_count,
        "has_numbering":  "word/numbering.xml" in names,
        "has_embeddings": any(n.startswith("word/embeddings/") for n in names),
        "scanned_range": [rng_start, rng_end],
    }

    # ── 骨架视图：短行候选（默认返回，无需额外参数）──────────────
    # 规则：段落 + 有文本 + 文本长度 < skeleton_text_max + 无 outline_level 缩进
    # 约 30–80 条，供 AI 在不撑爆上下文的前提下快速推导正则
    # 过滤规则：
    #   1. 段落类型
    #   2. 有文本，且文本长度 < skeleton_text_max
    #   3. 无 outline_level（排除正文缩进段）
    #   4. 含至少 2 个汉字或英文字母（排除纯占位行："日期："、"地址："等）
    _HAN_ALNUM = re.compile(r"[一-鿿A-Za-z]")
    skeleton = [
        {
            "body_idx":      e["body_idx"],
            "style":         e["style"],
            "outline_level": e["outline_level"],
            "text":          e["text"],
        }
        for e in scoped
        if e["type"] == "p"
        and e["text"]
        and len(e["text"]) < skeleton_text_max
        and (e["outline_level"] is None or e["outline_level"] >= 8)  # ol 0-7 是真正的标题/缩进层级，9=正文伪标记允许通过
        and len(_HAN_ALNUM.findall(e["text"])) >= 4   # 至少4个实意字符
    ]

    result = {
        "file_info":       file_info,
        "signals":         signals,
        "candidate_nodes": candidate_nodes,
        "content_previews": previews,
        "skeleton":        skeleton,
    }
    if include_elements:
        result["body_elements"] = scoped
    return result


def _parse_elements(children: List[etree._Element]) -> List[dict]:
    """把 body 子元素列表转为结构化 dict 列表"""
    elements = []
    para_seq = 0
    for body_idx, child in enumerate(children):
        tag = child.tag.split("}")[-1]

        if tag == "p":
            pPr = child.find("w:pPr", NS)
            style = ol = instr = None
            has_sectPr = has_fld = False

            if pPr is not None:
                ps = pPr.find("w:pStyle", NS)
                if ps is not None:
                    style = ps.get(f"{{{W}}}val")
                ov = pPr.find("w:outlineLvl", NS)
                if ov is not None:
                    try: ol = int(ov.get(f"{{{W}}}val", "9"))
                    except ValueError: pass
                has_sectPr = pPr.find("w:sectPr", NS) is not None

            flds = child.findall(".//w:fldChar", NS)
            has_fld = bool(flds)
            instrs = child.findall(".//w:instrText", NS)
            if instrs:
                instr = " ".join(t.text or "" for t in instrs).strip() or None

            full_text = "".join(t.text or "" for t in child.findall(".//w:t", NS))

            W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
            para_id = child.get(f"{{{W14}}}paraId")

            elements.append({
                "body_idx":     body_idx,
                "type":         "p",
                "para_seq":     para_seq,
                "para_id":      para_id,        # w14:paraId，write tools 的定位键
                "style":        style,
                "outline_level": ol,
                "text":         full_text[:150] if full_text else None,
                "text_len":     len(full_text),
                "has_sectPr":   has_sectPr,
                "has_fldChar":  has_fld,
                "instr_text":   instr,
            })
            para_seq += 1

        elif tag == "tbl":
            rows = child.findall(".//w:tr", NS)
            def row_cells(row):
                return [("".join(t.text or "" for t in c.findall(".//w:t", NS)))[:25]
                        for c in row.findall("w:tc", NS)]
            first_row = row_cells(rows[0]) if rows else []
            last_row  = row_cells(rows[-1]) if len(rows) > 1 else []
            col_count = len(rows[0].findall("w:tc", NS)) if rows else 0
            elements.append({
                "body_idx":   body_idx,
                "type":       "tbl",
                "tbl_rows":   len(rows),
                "tbl_cols":   col_count,
                "first_row":  first_row[:6],
                "last_row":   last_row[:6],
            })
        else:
            elements.append({"body_idx": body_idx, "type": tag})

    return elements


def _detect_signals(elements: List[dict]) -> List[dict]:
    """检测结构信号，只报告原始观测，不含业务语义解释"""
    p_elems = [e for e in elements if e["type"] == "p"]
    signals = []

    # 1. outline_level
    ol_hits = [e for e in p_elems if e.get("outline_level") is not None
               and e["outline_level"] < 6]
    ol_levels = sorted(set(e["outline_level"] for e in ol_hits))
    signals.append({
        "type": "outline_level",
        "confidence": 0.95 if len(ol_hits) >= 2 else 0.0,
        "count": len(ol_hits),
        "levels": ol_levels,
        "evidence": [{"body_idx": e["body_idx"], "level": e["outline_level"],
                      "text": e["text"]} for e in ol_hits[:4]],
        "note": "最可靠的层级信号，不依赖样式名",
    })

    # 2. 中文章节标题正则
    ZH  = re.compile(r"^第([一二三四五六七八九十百\d]+)[章节篇]")
    ATT = re.compile(r"^附件([一二三四五六七八九十\d]+)")
    zh_hits = []
    for e in p_elems:
        t = (e["text"] or "").strip()
        for pat, match_type in ((ZH, "chapter"), (ATT, "appendix")):
            m = pat.match(t)
            if m:
                # 不在工具层做去重；目录/正文/分册重复标题都交给 AI 判断
                zh_hits.append({
                    "body_idx": e["body_idx"],
                    "text": t[:60],
                    "style": e.get("style"),
                    "match_type": match_type,
                    "heading_key": m.group(0)[:6],  # 例如“第一章”“附件一”
                })
                break
    zh_hits.sort(key=lambda x: x["body_idx"])
    signals.append({
        "type": "zh_heading_regex",
        "confidence": 0.90 if len(zh_hits) >= 2 else 0.0,
        "count": len(zh_hits),
        "evidence": zh_hits,   # 不截断，全部返回
        "note": "仅适用中文文档；不做去重，目录/正文/分册重复标题由 AI 自行判断",
    })

    # 3. sectPr 分布
    sect_hits = [e for e in p_elems if e.get("has_sectPr")]
    density = len(sect_hits) / max(len(elements), 1)
    signals.append({
        "type": "sectPr",
        "confidence": 0.5,
        "count": len(sect_hits),
        "density": round(density, 4),
        "evidence": [{"body_idx": e["body_idx"], "text": e["text"]} for e in sect_hits[:5]],
        "note": f"密度={density:.3f}，{'高密度：可能是页面格式节点' if density > 0.02 else '低密度：可能与内容边界对应'}",
    })

    # 4. 样式分布（给 AI 参考）
    style_dist = {}
    for e in p_elems:
        s = e.get("style")
        if s and (e.get("text") or "").strip():
            style_dist.setdefault(s, {"count": 0, "examples": []})
            style_dist[s]["count"] += 1
            if len(style_dist[s]["examples"]) < 2:
                style_dist[s]["examples"].append(
                    {"body_idx": e["body_idx"], "text": (e["text"] or "")[:40]})
    signals.append({
        "type": "style_distribution",
        "confidence": 0.7 if style_dist else 0.0,
        "count": len(style_dist),
        "distribution": style_dist,
        "note": "样式编号在不同文件含义不同，需结合 outline_level 解释",
    })

    return signals


def _build_candidate_nodes(scoped: List[dict], signals: List[dict]) -> List[dict]:
    """
    基于信号划分候选节点。
    优先：zh_heading_regex（标准章节）> outline_level=0 > 单节点兜底。
    """
    if not scoped:
        return []

    sig_map = {s["type"]: s for s in signals}
    scope_start = scoped[0]["body_idx"]
    scope_end   = scoped[-1]["body_idx"] + 1

    def make_node(start, end, title_hint, signal_used, confidence):
        block = [e for e in scoped if start <= e["body_idx"] < end]
        return {
            "body_start":  start,
            "body_end":    end,
            "title_hint":  title_hint,
            "signal_used": signal_used,
            "confidence":  confidence,
            "para_count":  sum(1 for e in block if e["type"] == "p"),
            "table_count": sum(1 for e in block if e["type"] == "tbl"),
            "sectPr_count": sum(1 for e in block
                                if e["type"] == "p" and e.get("has_sectPr")),
        }

    # 尝试 zh_heading_regex
    zh_sig = sig_map.get("zh_heading_regex", {})
    anchors = []
    if zh_sig.get("confidence", 0) >= 0.7:
        anchors = [a for a in zh_sig["evidence"]
                   if scope_start <= a["body_idx"] < scope_end]

    # 回退：outline_level = 最高级
    if not anchors:
        ol_sig = sig_map.get("outline_level", {})
        if ol_sig.get("confidence", 0) >= 0.7 and ol_sig.get("levels"):
            min_lvl = ol_sig["levels"][0]
            anchors = [{"body_idx": e["body_idx"], "text": e["text"]}
                       for e in scoped
                       if e["type"] == "p" and e.get("outline_level") == min_lvl]

    if not anchors:
        # 兜底：整体单节点
        return [make_node(scope_start, scope_end, None, "fallback", 0.3)]

    nodes = []
    cuts = sorted(a["body_idx"] for a in anchors)
    title_map = {a["body_idx"]: (a.get("text") or "").strip()[:80] for a in anchors}

    # 锚点前的前言区
    if cuts[0] > scope_start:
        nodes.append(make_node(scope_start, cuts[0], None, "preamble", 0.7))

    for i, cp in enumerate(cuts):
        end_cp = cuts[i + 1] if i + 1 < len(cuts) else scope_end
        nodes.append(make_node(cp, end_cp, title_map.get(cp), zh_sig.get("type", "signal"), 0.90))

    return nodes


def _build_previews(elements: List[dict], nodes: List[dict]) -> List[dict]:
    """为每个节点生成内容采样预览（头3+中2+尾2段 + 所有表格首行）"""
    previews = []
    for node in nodes:
        scope = [e for e in elements
                 if node["body_start"] <= e["body_idx"] < node["body_end"]]
        paras = [e for e in scope
                 if e["type"] == "p" and (e.get("text") or "").strip()]
        tbls  = [e for e in scope if e["type"] == "tbl"]

        # 采样段落
        n = len(paras)
        sampled_idxs = set()
        for e in paras[:3]:       sampled_idxs.add(e["body_idx"])
        for e in paras[-2:]:      sampled_idxs.add(e["body_idx"])
        if n > 5:
            mid = n // 2
            for e in paras[mid:mid+2]: sampled_idxs.add(e["body_idx"])

        sampled_paras = [
            {"body_idx": e["body_idx"], "style": e.get("style"),
             "outline_level": e.get("outline_level"), "text": e["text"]}
            for e in paras if e["body_idx"] in sampled_idxs
        ]

        previews.append({
            "body_start":  node["body_start"],
            "body_end":    node["body_end"],
            "title_hint":  node["title_hint"],
            "paragraphs":  sampled_paras,
            "tables": [{"body_idx": t["body_idx"], "rows": t["tbl_rows"],
                        "cols": t["tbl_cols"], "first_row": t["first_row"]}
                       for t in tbls],
        })
    return previews


# ══════════════════════════════════════════════════════════════
# 能力二：split_by_range
# ══════════════════════════════════════════════════════════════

def split_by_range(
    docx_path: str,
    start: int,
    end: int,
    out_path: str,
) -> dict:
    """
    按 body_idx 范围提取子文档。

    参数：
        docx_path: 源 docx 路径
        start:     body_idx 起始（含）
        end:       body_idx 结束（不含）
        out_path:  输出 docx 路径

    返回：
        {"out_path", "body_range", "para_count", "table_count", "has_sectPr"}
    """
    docx_path = str(Path(docx_path).resolve())

    with zipfile.ZipFile(docx_path) as zf:
        doc_bytes = zf.read("word/document.xml")

    tree = etree.fromstring(doc_bytes)
    body = tree.find("w:body", NS)
    all_children = list(body)

    # 分离文档级 sectPr
    if all_children and all_children[-1].tag == f"{{{W}}}sectPr":
        doc_sectPr = all_children[-1]
        children = all_children[:-1]
    else:
        doc_sectPr = None
        children = all_children

    # 范围校验
    max_idx = len(children)
    if start < 0 or end > max_idx or start >= end:
        raise ValueError(f"无效范围 [{start}, {end})，文档共 {max_idx} 个 body 元素")

    # 深拷贝目标范围的子元素
    target = [copy.deepcopy(children[i]) for i in range(start, end)]

    # 统计
    para_count  = sum(1 for c in target if c.tag == f"{{{W}}}p")
    table_count = sum(1 for c in target if c.tag == f"{{{W}}}tbl")

    # 构建新 document.xml 并写出
    new_doc_bytes = _build_new_document_xml(tree, target, doc_sectPr)
    _zip_copy_replace_document(docx_path, out_path, new_doc_bytes)

    has_sectPr = any(
        c.tag == f"{{{W}}}p" and
        c.find("w:pPr/w:sectPr", NS) is not None
        for c in target
    )

    print(f"[split] body[{start}:{end}] → {out_path}  "
          f"(p={para_count}, tbl={table_count})")
    return {
        "out_path":    out_path,
        "body_range":  [start, end],
        "para_count":  para_count,
        "table_count": table_count,
        "has_sectPr":  has_sectPr,
    }


# ══════════════════════════════════════════════════════════════
# 能力三：join_by_manifest
# ══════════════════════════════════════════════════════════════

def join_by_manifest(
    manifest: List[Union[str, dict]],
    out_path: str,
) -> dict:
    """
    按清单拼接，支持两种模式（可混用）：

    模式A（范围引用）：
        {"source": "orig.docx", "start": 100, "end": 200}
        从指定 docx 按 body_idx 范围取内容

    模式B（整体合并）：
        "part1.docx"  或  {"source": "part1.docx"}
        取整个 docx 的全部 body 内容

    拼接规则：
        - 样式/字体/numbering 以第一个 source 文件为基准（合并其余文件缺少的部分）
        - sectPr 处理：各 source 的内联 sectPr 保留（分节），最终末尾加一个 sectPr
        - 所有内容按清单顺序顺序追加

    参数：
        manifest:  清单列表
        out_path:  输出路径

    返回：
        {"out_path", "sources_count", "total_para_count", "total_table_count"}
    """
    if not manifest:
        raise ValueError("manifest 不能为空")

    # 规范化清单
    items = []
    for entry in manifest:
        if isinstance(entry, str):
            items.append({"source": entry, "start": None, "end": None})
        elif isinstance(entry, dict):
            items.append({
                "source": entry["source"],
                "start":  entry.get("start"),
                "end":    entry.get("end"),
            })
        else:
            raise ValueError(f"manifest 项类型不支持: {type(entry)}")

    # ── 以第一个 source 为基准 ZIP ──────────────────────────
    first_source = items[0]["source"]
    all_new_children = []
    total_para = total_tbl = 0

    for item in items:
        src = item["source"]
        with zipfile.ZipFile(src) as zf:
            doc_bytes = zf.read("word/document.xml")

        tree = etree.fromstring(doc_bytes)
        body = tree.find("w:body", NS)
        all_children = list(body)

        # 分离文档级 sectPr
        if all_children and all_children[-1].tag == f"{{{W}}}sectPr":
            children = all_children[:-1]
            src_sectPr = all_children[-1]
        else:
            children = all_children
            src_sectPr = None

        # 确定范围
        s = item["start"] if item["start"] is not None else 0
        e = item["end"]   if item["end"]   is not None else len(children)
        s = max(0, s)
        e = min(len(children), e)

        segment = [copy.deepcopy(children[i]) for i in range(s, e)]

        # 统计
        total_para += sum(1 for c in segment if c.tag == f"{{{W}}}p")
        total_tbl  += sum(1 for c in segment if c.tag == f"{{{W}}}tbl")

        all_new_children.extend(segment)

    # ── 读取基准文件的 tree，替换 body ──────────────────────
    with zipfile.ZipFile(first_source) as zf:
        base_doc_bytes = zf.read("word/document.xml")

    base_tree = etree.fromstring(base_doc_bytes)
    base_body = base_tree.find("w:body", NS)
    base_all  = list(base_body)
    base_sectPr = base_all[-1] if base_all and base_all[-1].tag == f"{{{W}}}sectPr" else None

    new_doc_bytes = _build_new_document_xml(base_tree, all_new_children, base_sectPr)
    _zip_copy_replace_document(first_source, out_path, new_doc_bytes)

    print(f"[join] {len(items)} 段 → {out_path}  "
          f"(p={total_para}, tbl={total_tbl})")
    return {
        "out_path":          out_path,
        "sources_count":     len(items),
        "total_para_count":  total_para,
        "total_table_count": total_tbl,
    }


# ══════════════════════════════════════════════════════════════
# 便捷：读取节点的原始 body XML（debug 用）
# ══════════════════════════════════════════════════════════════

def read_body_xml(source: str, start: int, end: int) -> str:
    """返回 body[start:end] 的原始 XML 字符串，供调试。
    source 可以是 .docx 路径或 unpacked_dir 目录路径。"""
    doc_bytes, _ = _resolve_source(source)
    tree = etree.fromstring(doc_bytes)
    body = tree.find("w:body", NS)
    all_ch = list(body)
    if all_ch and all_ch[-1].tag == f"{{{W}}}sectPr":
        all_ch = all_ch[:-1]
    segment = all_ch[start:end]
    return "\n".join(etree.tostring(c, pretty_print=True).decode() for c in segment)


# ══════════════════════════════════════════════════════════════
# 能力四：find_by_regex
# ══════════════════════════════════════════════════════════════

# 内置模板：常见文档结构的正则
BUILTIN_PATTERNS = {
    "zh_chapter":    r"^第[一二三四五六七八九十百\d]+[章节篇]",   # 中文章节
    "zh_appendix":   r"^附件[一二三四五六七八九十\d]+",           # 中文附件
    "zh_section":    r"^[一二三四五六七八九十]+、\S",             # 中文一、二、三级小节
    "en_chapter":    r"^Chapter\s+\d+",                          # 英文 Chapter N
    "en_section":    r"^\d+\.\s+[A-Z]",                         # 英文 1. Title
    "en_appendix":   r"^Appendix\s+[A-Z\d]",                    # 英文 Appendix A
    "numbered_bold": r"^\d+[\.\、]\d*\s*\S{1,20}$",             # 短数字编号行
}


def find_by_regex(
    source: str,
    pattern: str = "",
    body_range: Optional[Tuple[int, int]] = None,
    flags: int = 0,
    use_builtin: Optional[str] = None,
) -> dict:
    r"""
    用正则在 body 段落文本中查找锚点。
    source 可以是 .docx 路径或 unpacked_dir 目录路径。

    参数：
        source:      .docx 文件路径 或 unpacked_dir 目录路径
        pattern:     正则表达式字符串（AI 自定义）；use_builtin 非空时忽略此参数
        body_range:  限制扫描范围 (start, end)；None = 全文
        flags:       re 标志，如 re.IGNORECASE
        use_builtin: 使用内置模板名（见 BUILTIN_PATTERNS），优先于 pattern

    返回：
        {
          "pattern":  实际使用的正则
          "hits": [
            {"body_idx": int, "para_id": str|None, "text": str, "style": str|None}
          ]
          "count": int
        }

    典型用法：
        find_by_regex(path, r"^[A-Z][^a-z]{0,30}$")    # 全大写短行 → 可能是英文标题
        find_by_regex("unpacked/", r"\[.+?\]")         # unpack 后继续查找
        find_by_regex(path, use_builtin="en_chapter")    # 用内置模板
    """
    if use_builtin:
        if use_builtin not in BUILTIN_PATTERNS:
            raise ValueError(
                f"未知内置模板 '{use_builtin}'，可用: {list(BUILTIN_PATTERNS.keys())}"
            )
        actual_pattern = BUILTIN_PATTERNS[use_builtin]
    else:
        actual_pattern = pattern

    compiled = re.compile(actual_pattern, flags)

    doc_bytes, _ = _resolve_source(source)
    tree = etree.fromstring(doc_bytes)
    body = tree.find("w:body", NS)
    all_children = list(body)
    if all_children and all_children[-1].tag == f"{{{W}}}sectPr":
        all_children = all_children[:-1]

    rng_start = body_range[0] if body_range else 0
    rng_end   = body_range[1] if body_range else len(all_children)

    hits = []
    for body_idx, child in enumerate(all_children):
        if not (rng_start <= body_idx < rng_end):
            continue
        if child.tag != f"{{{W}}}p":
            continue
        text = "".join(t.text or "" for t in child.findall(f".//{{{W}}}t"))
        t = text.strip()
        if not t:
            continue
        if compiled.search(t):
            pPr = child.find("w:pPr", NS)
            style = None
            if pPr is not None:
                ps = pPr.find("w:pStyle", NS)
                if ps is not None:
                    style = ps.get(f"{{{W}}}val")
            W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
            para_id = child.get(f"{{{W14}}}paraId")
            hits.append({"body_idx": body_idx, "para_id": para_id, "text": t[:80], "style": style})

    return {
        "pattern": actual_pattern,
        "hits":    hits,
        "count":   len(hits),
    }


def list_builtin_patterns() -> dict:
    """列出所有内置正则模板，供 AI 参考选用"""
    return BUILTIN_PATTERNS
