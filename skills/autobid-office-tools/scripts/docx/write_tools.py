"""
scripts/docx/write_tools.py
===========================
在 unpack/pack 流程中，对已解包的 word/document.xml 做写入操作。

前置条件：已用 unpack.py 解包到 unpacked_dir，操作完成后用 pack.py 重新打包。

四个工具，对应四类写入场景：

    replace_text(unpacked_dir, para_id, old_text, new_text)
        场景：挖空填入。替换段落内的占位符文字，完整保留原有格式。

    overwrite_paragraph_text(unpacked_dir, para_id, text, inherit_from_first_run=True)
        场景：整段重写。适用于一个段落被拆成多个 run / 下划线占位时，
        直接把该段正文改写成新的单段文本。

    delete_paragraphs(unpacked_dir, para_ids)
        场景：删除已确定不保留的提示标题或空白段。

    delete_body_elements(unpacked_dir, body_indices)
        场景：删除已确定不保留的正文节点（段落或表格），用于条件分支裁剪。

    fill_paragraph(unpacked_dir, para_id, text, inherit_from=None)
        场景：空单元格/空段落写入。向无 <w:r> 的空段落注入内容，
        格式从指定 para_id 节点继承，或自动从相邻节点推断。

    insert_paragraphs(unpacked_dir, anchor_para_id, position, paragraphs)
        场景：大块空白区域自由写入。在锚点段落前/后批量插入新段落。
        格式由调用方通过 paragraphs 参数完整描述。

    reformat_paragraphs(unpacked_dir, para_ids, font, size, line_spacing,
                        first_line_indent=True, skip_empty=True)
        场景：批量格式统一。修改指定段落的字体、字号、行距，
        para_ids=None 时作用于全文所有段落。

设计原则：
    - 工具只做"怎么改"，不判断"该改哪里"——定位由 agent 通过 inspect/find_by_regex 完成
    - 每个工具返回结构化结果，agent 可据此决定是否继续或回滚
    - 不修改 <w:tblPr>/<w:tcPr> 等表格结构属性，只操作段落内容层
"""

import random
import re
from pathlib import Path
from typing import List, Optional
from lxml import etree

W   = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
NS  = {"w": W, "w14": W14}

FONT_ATTRS = ["ascii", "hAnsi", "eastAsia", "cs"]

PPR_AFTER_SPACING_TAGS = {
    "ind",
    "contextualSpacing",
    "mirrorIndents",
    "suppressOverlap",
    "jc",
    "textDirection",
    "textAlignment",
    "textboxTightWrap",
    "outlineLvl",
    "divId",
    "cnfStyle",
    "rPr",
    "sectPr",
    "pPrChange",
}


# ══════════════════════════════════════════════════════════════
# 内部工具
# ══════════════════════════════════════════════════════════════

def _load(unpacked_dir: str) -> tuple[etree._Element, Path]:
    path = Path(unpacked_dir) / "word" / "document.xml"
    tree = etree.parse(str(path))
    return tree, path


def _save(tree: etree._Element, path: Path) -> None:
    tree.write(str(path), xml_declaration=True, encoding="UTF-8",
               standalone=True, pretty_print=True)


def _body_paragraphs(tree) -> list:
    """返回 body 下所有 <w:p>，以 paraId 为 key 的 dict"""
    root = tree.getroot()
    body = root.find(f"{{{W}}}body")
    result = {}
    for elem in body.iter(f"{{{W}}}p"):
        pid = elem.get(f"{{{W14}}}paraId")
        if pid:
            result[pid] = elem
    return result


def list_paragraphs(
    unpacked_dir: str,
    include_empty: bool = True,
) -> dict:
    """
    列出 document body 下所有段落（含表格单元格内段落）。

    适用场景：
    - agent 需要先看到 paraId 与当前文本，再决定调用 replace/fill/reformat
    - 不想每次都手写 XML 遍历
    """
    tree, _ = _load(unpacked_dir)
    root = tree.getroot()
    body = root.find(f"{{{W}}}body")
    items = []
    for idx, elem in enumerate(body.iter(f"{{{W}}}p")):
        pid = elem.get(f"{{{W14}}}paraId")
        texts = [t.text or "" for t in elem.iter(f"{{{W}}}t")]
        text = "".join(texts)
        if not include_empty and not text.strip():
            continue
        items.append({
            "index": idx,
            "para_id": pid,
            "text": text,
            "is_empty": not bool(text.strip()),
        })
    return {"status": "ok", "count": len(items), "paragraphs": items}


def _new_para_id() -> str:
    """生成合法的 8 位十六进制 paraId（< 0x80000000）"""
    return hex(random.randint(1, 0x7FFFFFFE))[2:].upper().zfill(8)


def _clone_rPr(source_elem: etree._Element) -> Optional[etree._Element]:
    """从一个 <w:p> 中提取第一个 <w:r> 的 <w:rPr>，深拷贝返回"""
    from copy import deepcopy
    for r in source_elem.findall(f"{{{W}}}r"):
        rPr = r.find(f"{{{W}}}rPr")
        if rPr is not None:
            return deepcopy(rPr)
    # 没有 run，从 pPr/rPr 取段落级默认格式
    pPr = source_elem.find(f"{{{W}}}pPr")
    if pPr is not None:
        rPr = pPr.find(f"{{{W}}}rPr")
        if rPr is not None:
            return deepcopy(rPr)
    return None


def _first_run_rpr(source_elem: etree._Element) -> Optional[etree._Element]:
    for r in source_elem.findall(f"{{{W}}}r"):
        rPr = r.find(f"{{{W}}}rPr")
        if rPr is not None:
            return rPr
    return None


def _build_rPr(font: str, size: int) -> etree._Element:
    """从头构建一个 <w:rPr>"""
    rPr = etree.Element(f"{{{W}}}rPr")
    rFonts = etree.SubElement(rPr, f"{{{W}}}rFonts")
    for attr in FONT_ATTRS:
        rFonts.set(f"{{{W}}}{attr}", font)
    sz = etree.SubElement(rPr, f"{{{W}}}sz")
    sz.set(f"{{{W}}}val", str(size))
    szCs = etree.SubElement(rPr, f"{{{W}}}szCs")
    szCs.set(f"{{{W}}}val", str(size))
    return rPr


def _set_font_size(rPr: etree._Element, font: str, size: int) -> None:
    """就地修改 rPr 的字体和字号"""
    rFonts = rPr.find(f"{{{W}}}rFonts")
    if rFonts is None:
        rFonts = etree.SubElement(rPr, f"{{{W}}}rFonts")
    for attr in FONT_ATTRS:
        rFonts.set(f"{{{W}}}{attr}", font)
    # 清掉 hint，避免字体提示覆盖设置
    if f"{{{W}}}hint" in rFonts.attrib:
        del rFonts.attrib[f"{{{W}}}hint"]

    for tag in ["sz", "szCs"]:
        el = rPr.find(f"{{{W}}}{tag}")
        if el is None:
            el = etree.SubElement(rPr, f"{{{W}}}{tag}")
        el.set(f"{{{W}}}val", str(size))


def _set_spacing(pPr: etree._Element, line: int,
                 before: Optional[int] = None,
                 after: Optional[int] = None) -> None:
    """就地修改 pPr 的行距，保留其他 spacing 属性"""
    spacing = pPr.find(f"{{{W}}}spacing")
    if spacing is None:
        spacing = etree.Element(f"{{{W}}}spacing")
        insert_idx = None
        for idx, child in enumerate(list(pPr)):
            local = etree.QName(child).localname
            if local in PPR_AFTER_SPACING_TAGS:
                insert_idx = idx
                break
        if insert_idx is None:
            pPr.append(spacing)
        else:
            pPr.insert(insert_idx, spacing)
    spacing.set(f"{{{W}}}line", str(line))
    spacing.set(f"{{{W}}}lineRule", "auto")
    # 清掉 exact 模式残留的 beforeLines/afterLines
    for attr in [f"{{{W}}}beforeLines", f"{{{W}}}afterLines"]:
        if attr in spacing.attrib:
            del spacing.attrib[attr]
    if before is not None:
        spacing.set(f"{{{W}}}before", str(before))
    if after is not None:
        spacing.set(f"{{{W}}}after", str(after))


# ══════════════════════════════════════════════════════════════
# 工具一：replace_text
# ══════════════════════════════════════════════════════════════

def replace_text(
    unpacked_dir: str,
    para_id: str,
    old_text: str,
    new_text: str,
) -> dict:
    """
    在指定段落内替换占位符文字，完整保留该 <w:r> 的格式。

    适用场景：挖空填入，如 "[招标代理机构]" → "国网青海省电力公司物资分公司"

    参数：
        unpacked_dir:  解包后的目录
        para_id:       目标段落的 w14:paraId
        old_text:      要替换的原文字（精确匹配某个 <w:t> 的文本内容）
        new_text:      替换后的文字

    返回：
        {
          "status": "ok" | "not_found" | "ambiguous",
          "para_id": str,
          "replaced": int,   # 实际替换次数
          "detail": str
        }
    """
    tree, path = _load(unpacked_dir)
    paras = _body_paragraphs(tree)

    if para_id not in paras:
        return {"status": "not_found", "para_id": para_id,
                "replaced": 0, "detail": f"paraId={para_id} 不存在"}

    p = paras[para_id]
    replaced = 0
    for t_elem in p.iter(f"{{{W}}}t"):
        if t_elem.text and old_text in t_elem.text:
            t_elem.text = t_elem.text.replace(old_text, new_text)
            # 有前后空格时保留 xml:space
            if t_elem.text != t_elem.text.strip():
                t_elem.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            replaced += 1

    if replaced == 0:
        return {"status": "not_found", "para_id": para_id,
                "replaced": 0, "detail": f"段落内未找到文字: {old_text!r}"}

    _save(tree, path)
    return {"status": "ok", "para_id": para_id,
            "replaced": replaced, "detail": f"{old_text!r} → {new_text!r}"}


def overwrite_paragraph_text(
    unpacked_dir: str,
    para_id: str,
    text: str,
    inherit_from_first_run: bool = True,
) -> dict:
    """
    整段重写段落文字。

    适用场景：
    - 一个段落被拆成多个 run，replace_text 无法整段替换
    - 原段落是下划线占位，最终要改写成新的完整文本
    """
    tree, path = _load(unpacked_dir)
    paras = _body_paragraphs(tree)
    if para_id not in paras:
        return {"status": "not_found", "para_id": para_id, "detail": f"paraId={para_id} 不存在"}

    p = paras[para_id]
    rPr_template = None
    if inherit_from_first_run:
        first_rpr = _first_run_rpr(p)
        if first_rpr is not None:
            rPr_template = etree.fromstring(etree.tostring(first_rpr))

    for child in list(p):
        if child.tag == f"{{{W}}}r":
            p.remove(child)

    r = etree.SubElement(p, f"{{{W}}}r")
    if rPr_template is not None:
        r.append(rPr_template)
    t = etree.SubElement(r, f"{{{W}}}t")
    t.text = text
    if text != text.strip():
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    _save(tree, path)
    return {"status": "ok", "para_id": para_id, "detail": f"段落已整体改写为 {text!r}"}


def delete_paragraphs(
    unpacked_dir: str,
    para_ids: list[str],
) -> dict:
    """
    删除指定段落。

    适用场景：
    - 删除“XX格式 / XX模板 / 示例”提示段
    - 删除已明确不保留的说明段
    """
    tree, path = _load(unpacked_dir)
    paras = _body_paragraphs(tree)
    deleted = []
    missing = []
    for para_id in para_ids:
        p = paras.get(para_id)
        if p is None:
            missing.append(para_id)
            continue
        parent = p.getparent()
        if parent is not None:
            parent.remove(p)
            deleted.append(para_id)

    _save(tree, path)
    status = "ok" if not missing else "partial"
    return {
        "status": status,
        "deleted": deleted,
        "missing": missing,
        "detail": f"删除 {len(deleted)} 个段落",
    }


def delete_body_elements(
    unpacked_dir: str,
    body_indices: list[int],
) -> dict:
    """
    删除 document body 下指定索引的顶层节点（支持段落 / 表格）。

    适用场景：
    - 条件分支中整段删除不适用说明
    - 删除整个表格或说明块
    - 基于 inspect 的 body_idx 做机械裁剪
    """
    tree, path = _load(unpacked_dir)
    root = tree.getroot()
    body = root.find(f"{{{W}}}body")
    children = list(body)
    if children and children[-1].tag == f"{{{W}}}sectPr":
        children = children[:-1]

    deleted = []
    missing = []
    for idx in sorted(set(body_indices), reverse=True):
        if idx < 0 or idx >= len(children):
            missing.append(idx)
            continue
        elem = children[idx]
        deleted.append({
            "body_idx": idx,
            "tag": elem.tag.rsplit("}", 1)[-1],
        })
        body.remove(elem)

    _save(tree, path)
    status = "ok" if not missing else "partial"
    return {
        "status": status,
        "deleted": list(reversed(deleted)),
        "missing": sorted(missing),
        "detail": f"删除 {len(deleted)} 个 body 节点",
    }


# ══════════════════════════════════════════════════════════════
# 工具二：fill_paragraph
# ══════════════════════════════════════════════════════════════

def fill_paragraph(
    unpacked_dir: str,
    para_id: str,
    text: str,
    inherit_from: Optional[str] = None,
    font: Optional[str] = None,
    size: Optional[int] = None,
) -> dict:
    """
    向空段落（无 <w:r> 的 <w:p>）注入文字内容。

    适用场景：表格空单元格填写、空白行填入。

    格式优先级：
        1. font/size 参数（agent 明确指定）
        2. inherit_from 指定的 paraId 节点的 rPr
        3. 同一 <w:tc> 内其他段落的 rPr（自动推断，仅表格场景）
        4. 兜底：不附加任何 rPr，由 Word 样式继承决定

    参数：
        unpacked_dir:  解包后的目录
        para_id:       目标空段落的 w14:paraId
        text:          要写入的文字
        inherit_from:  格式来源段落的 paraId（可选）
        font:          字体名，覆盖继承（可选）
        size:          字号，half-point 单位，如 24=小四（可选）

    返回：
        {"status": "ok"|"not_found"|"not_empty", "para_id": str, "detail": str}
    """
    from copy import deepcopy

    tree, path = _load(unpacked_dir)
    paras = _body_paragraphs(tree)

    if para_id not in paras:
        return {"status": "not_found", "para_id": para_id,
                "detail": f"paraId={para_id} 不存在"}

    p = paras[para_id]

    # 检查是否已有内容
    existing_runs = p.findall(f"{{{W}}}r")
    has_text = any(
        t.text and t.text.strip()
        for r in existing_runs
        for t in r.findall(f"{{{W}}}t")
    )
    if has_text:
        return {"status": "not_empty", "para_id": para_id,
                "detail": "段落已有内容，请用 replace_text 修改"}

    # 确定格式
    rPr = None
    if inherit_from and inherit_from in paras:
        rPr = _clone_rPr(paras[inherit_from])
    elif inherit_from is None:
        # 自动推断：找同一 <w:tc> 内其他有内容的 <w:p>
        root = tree.getroot()
        for tc in root.iter(f"{{{W}}}tc"):
            tc_paras = tc.findall(f"{{{W}}}p")
            para_ids_in_tc = [
                q.get(f"{{{W14}}}paraId") for q in tc_paras
            ]
            if para_id in para_ids_in_tc:
                for q in tc_paras:
                    if q.get(f"{{{W14}}}paraId") != para_id:
                        candidate = _clone_rPr(q)
                        if candidate is not None:
                            rPr = candidate
                            break
                break

    # 应用 font/size 覆盖
    if font or size:
        if rPr is None:
            rPr = _build_rPr(font or "宋体", size or 24)
        else:
            _set_font_size(rPr, font or "宋体", size or 24)

    # 构建 <w:r>
    r = etree.SubElement(p, f"{{{W}}}r")
    if rPr is not None:
        r.insert(0, rPr)
    t = etree.SubElement(r, f"{{{W}}}t")
    t.text = text
    if text != text.strip():
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    _save(tree, path)
    return {"status": "ok", "para_id": para_id,
            "detail": f"已写入: {text!r}"}


# ══════════════════════════════════════════════════════════════
# 工具三：insert_paragraphs
# ══════════════════════════════════════════════════════════════

def insert_paragraphs(
    unpacked_dir: str,
    anchor_para_id: str,
    position: str,
    paragraphs: list[dict],
) -> dict:
    """
    在锚点段落前/后批量插入新段落。

    适用场景：空白章节自由写入、在指定位置追加内容块。

    paragraphs 格式（列表，每项描述一个段落）：
        {
          "text":         str,              # 文字内容（必填）
          "font":         str,              # 字体，默认 "宋体"
          "size":         int,              # half-point，默认 24（小四）
          "line_spacing": int,              # line 值，默认 360（1.5倍）
          "bold":         bool,             # 是否加粗，默认 False
          "align":        str,              # "left"|"center"|"right"，默认 "left"
          "first_line_indent": bool,        # 首行缩进2字，默认 True
        }

    参数：
        unpacked_dir:   解包后的目录
        anchor_para_id: 锚点段落的 w14:paraId
        position:       "before" | "after"
        paragraphs:     段落描述列表

    返回：
        {"status": "ok"|"not_found", "inserted": int, "para_ids": list[str]}
    """
    tree, path = _load(unpacked_dir)
    root = tree.getroot()
    body = root.find(f"{{{W}}}body")
    paras = _body_paragraphs(tree)

    if anchor_para_id not in paras:
        return {"status": "not_found", "anchor_para_id": anchor_para_id,
                "inserted": 0, "detail": f"paraId={anchor_para_id} 不存在"}

    anchor = paras[anchor_para_id]
    anchor_index = list(body).index(anchor)
    insert_at = anchor_index if position == "before" else anchor_index + 1

    new_ids = []
    for i, para_spec in enumerate(paragraphs):
        text          = para_spec["text"]
        font          = para_spec.get("font", "宋体")
        size          = para_spec.get("size", 24)
        line_spacing  = para_spec.get("line_spacing", 360)
        bold          = para_spec.get("bold", False)
        align         = para_spec.get("align", "left")
        first_indent  = para_spec.get("first_line_indent", True)

        pid = _new_para_id()
        new_ids.append(pid)

        # 构建 <w:p>
        p = etree.Element(f"{{{W}}}p")
        p.set(f"{{{W14}}}paraId", pid)

        # <w:pPr>
        pPr = etree.SubElement(p, f"{{{W}}}pPr")
        _set_spacing(pPr, line_spacing, before=0, after=0)
        if first_indent:
            ind = etree.SubElement(pPr, f"{{{W}}}ind")
            ind.set(f"{{{W}}}firstLine", "480")
            ind.set(f"{{{W}}}firstLineChars", "200")
        if align != "left":
            jc = etree.SubElement(pPr, f"{{{W}}}jc")
            jc.set(f"{{{W}}}val", align)

        # <w:r>
        r = etree.SubElement(p, f"{{{W}}}r")
        rPr = _build_rPr(font, size)
        if bold:
            etree.SubElement(rPr, f"{{{W}}}b")
            etree.SubElement(rPr, f"{{{W}}}bCs")
        r.insert(0, rPr)
        t = etree.SubElement(r, f"{{{W}}}t")
        t.text = text
        if text != text.strip():
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

        body.insert(insert_at + i, p)

    _save(tree, path)
    return {"status": "ok", "inserted": len(paragraphs), "para_ids": new_ids}


# ══════════════════════════════════════════════════════════════
# 工具四：reformat_paragraphs
# ══════════════════════════════════════════════════════════════

def reformat_paragraphs(
    unpacked_dir: str,
    font: str,
    size: int,
    line_spacing: int,
    para_ids: Optional[list[str]] = None,
    skip_para_ids: Optional[list[str]] = None,
    skip_empty: bool = True,
) -> dict:
    """
    批量修改段落格式（字体、字号、行距）。

    适用场景：全文或指定段落的格式统一，如仿宋→宋体、行距改1.5倍。
    只修改 <w:pPr> 和 <w:r> 内的格式属性，不触碰文字内容和表格结构。

    参数：
        unpacked_dir:   解包后的目录
        font:           字体名，如 "宋体"
        size:           字号 half-point，如 24=小四、28=三号
        line_spacing:   行距 line 值，如 240=单倍、360=1.5倍、480=双倍
        para_ids:       指定段落 paraId 列表；None = 全文所有段落
        skip_para_ids:  跳过的 paraId 列表（标题、签字行等不改的段落）
        skip_empty:     True 时跳过无文字内容的空段落

    返回：
        {"status": "ok", "total": int, "modified": int, "skipped": int}
    """
    tree, path = _load(unpacked_dir)
    paras = _body_paragraphs(tree)
    skip_set = set(skip_para_ids or [])

    if para_ids is not None:
        targets = {pid: paras[pid] for pid in para_ids if pid in paras}
    else:
        targets = paras

    modified = skipped = 0

    for pid, p in targets.items():
        if pid in skip_set:
            skipped += 1
            continue

        if skip_empty:
            texts = [t.text or "" for t in p.iter(f"{{{W}}}t")]
            if not any(t.strip() for t in texts):
                skipped += 1
                continue

        # 修改 pPr
        pPr = p.find(f"{{{W}}}pPr")
        if pPr is not None:
            _set_spacing(pPr, line_spacing)
            pPr_rPr = pPr.find(f"{{{W}}}rPr")
            if pPr_rPr is not None:
                _set_font_size(pPr_rPr, font, size)
                kern = pPr_rPr.find(f"{{{W}}}kern")
                if kern is not None:
                    pPr_rPr.remove(kern)

        # 修改所有 run
        for r in p.findall(f"{{{W}}}r"):
            rPr = r.find(f"{{{W}}}rPr")
            if rPr is None:
                continue
            _set_font_size(rPr, font, size)
            kern = rPr.find(f"{{{W}}}kern")
            if kern is not None:
                rPr.remove(kern)

        modified += 1

    _save(tree, path)
    return {
        "status": "ok",
        "total": len(targets),
        "modified": modified,
        "skipped": skipped,
    }


# ══════════════════════════════════════════════════════════════
# 调试工具：read_node_xml
# ══════════════════════════════════════════════════════════════

def read_node_xml(unpacked_dir: str, para_id: str) -> dict:
    """
    返回单个段落的原始 XML 字符串，供 agent 调试确认格式细节。
    不用于常规流程，只在 inspect 信息不够时按需调用。

    返回：
        {"status": "ok"|"not_found", "para_id": str, "xml": str}
    """
    tree, _ = _load(unpacked_dir)
    paras = _body_paragraphs(tree)

    if para_id not in paras:
        return {"status": "not_found", "para_id": para_id, "xml": ""}

    xml_bytes = etree.tostring(paras[para_id], pretty_print=True, encoding="unicode")
    return {"status": "ok", "para_id": para_id, "xml": xml_bytes}
