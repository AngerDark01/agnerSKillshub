"""
scripts/docx/table_tools.py
===========================
DOCX 文档内表格的读取和写入工具。

这是基础设施层工具，不绑定任何业务字段名。
agent 先用 list_tables 看表头，自主判断列语义，再用列序号操作。

工具一：list_tables(source)
    列出文档所有表格的 body_idx、尺寸和列名（带序号）。

工具二：extract_table_rows(source, body_idx, match, header_row)
    按 {列序号: 值} 条件精确提取匹配行，返回字段字典列表。

工具三：insert_kv_table(unpacked_dir, anchor_para_id, data, position, title)
    在指定段落前/后插入一个两列 key-value 表格。

工具四：read_table(source, body_idx, ...)
    读取整张表，支持多段落单元格和续行合并。

工具五：fit_table_to_page(unpacked_dir, body_idx, ...)
    按所在 section 的可用页宽重算表格宽度，避免横向超页。
"""

import random
import zipfile
from pathlib import Path
from lxml import etree

W   = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"


# ══════════════════════════════════════════════════════════════
# 内部
# ══════════════════════════════════════════════════════════════

def _load_body_children(source: str):
    p = Path(source)
    if p.is_dir():
        doc_bytes = (p / "word" / "document.xml").read_bytes()
    else:
        with zipfile.ZipFile(str(p)) as zf:
            doc_bytes = zf.read("word/document.xml")
    tree = etree.fromstring(doc_bytes)
    body = tree.find(f"{{{W}}}body")
    children = list(body)
    if children and children[-1].tag == f"{{{W}}}sectPr":
        children = children[:-1]
    return children


def _load_document_tree(unpacked_dir: str):
    xml_path = Path(unpacked_dir) / "word" / "document.xml"
    tree = etree.parse(str(xml_path))
    root = tree.getroot()
    body = root.find(f"{{{W}}}body")
    return tree, xml_path, body


def _row_texts(row) -> list[str]:
    return [
        "".join(t.text or "" for t in c.findall(f".//{{{W}}}t")).strip()
        for c in row.findall(f"{{{W}}}tc")
    ]


def _cell_paras(cell) -> list[str]:
    """提取单元格内所有段落的文字，返回非空段落列表"""
    return [
        "".join(t.text or "" for t in p.findall(f".//{{{W}}}t")).strip()
        for p in cell.findall(f"{{{W}}}p")
        if "".join(t.text or "" for t in p.findall(f".//{{{W}}}t")).strip()
    ]


def _new_para_id() -> str:
    return hex(random.randint(1, 0x7FFFFFFE))[2:].upper().zfill(8)


def _to_int(value) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _active_sectpr_for_body_idx(body: etree._Element, body_idx: int):
    children = list(body)
    body_sectpr = None
    if children and children[-1].tag == f"{{{W}}}sectPr":
        body_sectpr = children[-1]
        children = children[:-1]

    if body_idx < 0 or body_idx >= len(children):
        raise IndexError(f"body_idx={body_idx} 超出范围（共 {len(children)} 个 body 元素）")

    active = None
    for idx, child in enumerate(children):
        if idx > body_idx:
            break
        if child.tag == f"{{{W}}}p":
            pPr = child.find(f"{{{W}}}pPr")
            if pPr is not None:
                sectPr = pPr.find(f"{{{W}}}sectPr")
                if sectPr is not None:
                    active = sectPr
        elif child.tag == f"{{{W}}}sectPr":
            active = child

    return active if active is not None else body_sectpr


def _usable_page_width_twips(sectPr: etree._Element) -> int | None:
    if sectPr is None:
        return None

    pgSz = sectPr.find(f"{{{W}}}pgSz")
    pgMar = sectPr.find(f"{{{W}}}pgMar")
    if pgSz is None or pgMar is None:
        return None

    page_w = _to_int(pgSz.get(f"{{{W}}}w"))
    left = _to_int(pgMar.get(f"{{{W}}}left"))
    right = _to_int(pgMar.get(f"{{{W}}}right"))
    if None in (page_w, left, right):
        return None

    usable = page_w - left - right
    return usable if usable > 0 else None


def _scale_ints(values: list[int], target_total: int) -> list[int]:
    if not values:
        return []
    if target_total <= 0:
        return values[:]

    clean = [max(0, int(v)) for v in values]
    current_total = sum(clean)
    if current_total <= 0:
        base = target_total // len(clean)
        remainder = target_total - base * len(clean)
        scaled = [base] * len(clean)
        for i in range(remainder):
            scaled[i] += 1
        return scaled

    numerators = [target_total * v for v in clean]
    scaled = [n // current_total for n in numerators]
    remainder = target_total - sum(scaled)
    order = sorted(
        range(len(clean)),
        key=lambda i: (numerators[i] % current_total, clean[i]),
        reverse=True,
    )
    for i in order[:remainder]:
        scaled[i] += 1
    return scaled


def _table_current_width_twips(tbl: etree._Element) -> int | None:
    tblGrid = tbl.find(f"{{{W}}}tblGrid")
    if tblGrid is not None:
        grid_vals = []
        for gc in tblGrid.findall(f"{{{W}}}gridCol"):
            width = _to_int(gc.get(f"{{{W}}}w"))
            if width is not None:
                grid_vals.append(width)
        if grid_vals and sum(grid_vals) > 0:
            return sum(grid_vals)

    row_sums = []
    for tr in tbl.findall(f"{{{W}}}tr"):
        total = 0
        found = False
        for tc in tr.findall(f"{{{W}}}tc"):
            tcPr = tc.find(f"{{{W}}}tcPr")
            tcW = tcPr.find(f"{{{W}}}tcW") if tcPr is not None else None
            if tcW is None or tcW.get(f"{{{W}}}type") != "dxa":
                continue
            width = _to_int(tcW.get(f"{{{W}}}w"))
            if width is None:
                continue
            total += width
            found = True
        if found and total > 0:
            row_sums.append(total)

    return max(row_sums) if row_sums else None


# ══════════════════════════════════════════════════════════════
# 工具一：list_tables
# ══════════════════════════════════════════════════════════════

def list_tables(source: str) -> dict:
    """
    列出文档中所有表格的 body_idx、尺寸和列名。

    source 可以是 .docx 路径 或 unpacked_dir 目录。

    返回：
        {
          "count": int,
          "tables": [
            {
              "body_idx":        int,
              "rows":            int,
              "cols":            int,
              "headers_indexed": list[str],  # "[0]列名" 格式
              "header_row2":     list[str]   # 第二行（如有双行表头）
            }
          ]
        }
    """
    children = _load_body_children(source)
    tables = []

    for body_idx, el in enumerate(children):
        if el.tag != f"{{{W}}}tbl":
            continue
        rows = el.findall(f".//{{{W}}}tr")
        if not rows:
            continue
        header  = _row_texts(rows[0])
        header2 = _row_texts(rows[1]) if len(rows) > 1 else []
        tables.append({
            "body_idx":        body_idx,
            "rows":            len(rows),
            "cols":            len(header),
            "headers_indexed": [f"[{i}]{h}" for i, h in enumerate(header)],
            "header_row2":     header2,
        })

    return {"count": len(tables), "tables": tables}


# ══════════════════════════════════════════════════════════════
# 工具二：extract_table_rows
# ══════════════════════════════════════════════════════════════

def extract_table_rows(
    source: str,
    body_idx: int,
    match: dict,
    header_row: int = 0,
) -> dict:
    """
    从指定表格中提取匹配行，返回字段字典列表。

    参数：
        source:     .docx 路径 或 unpacked_dir 目录
        body_idx:   表格的 body_idx（从 list_tables 获取）
        match:      {列序号(int): 目标值(str)}，精确匹配，多条件取 AND
                    列序号从 list_tables 的 headers_indexed 中读取
        header_row: 表头所在行（默认 0）

    返回：
        {
          "status":  "ok" | "not_found" | "ambiguous",
          "count":   int,
          "headers": list[str],
          "rows":    list[dict],  # 每行为 {列名: 值} 字典
          "detail":  str
        }

    注意：
        match key 必须是列序号（int），不接受字符串列名。
        先用 list_tables 确认列序号，再调用此工具。
    """
    children = _load_body_children(source)

    if body_idx >= len(children):
        return {"status": "not_found", "count": 0, "headers": [], "rows": [],
                "detail": f"body_idx={body_idx} 超出范围（共 {len(children)} 个元素）"}

    tbl = children[body_idx]
    if tbl.tag != f"{{{W}}}tbl":
        return {"status": "not_found", "count": 0, "headers": [], "rows": [],
                "detail": f"body_idx={body_idx} 处不是表格"}

    rows = tbl.findall(f".//{{{W}}}tr")
    headers = _row_texts(rows[header_row]) if header_row < len(rows) else []

    hits = []
    for row in rows[header_row + 1:]:
        cells = _row_texts(row)
        if not any(cells):
            continue
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))

        if all(
            str(val).strip() == cells[col_idx].strip()
            for col_idx, val in match.items()
            if col_idx < len(cells)
        ):
            hits.append(dict(zip(headers, cells)))

    if not hits:
        return {"status": "not_found", "count": 0, "headers": headers, "rows": [],
                "detail": f"未找到匹配行，条件: {match}"}

    status = "ok" if len(hits) == 1 else "ambiguous"
    return {"status": status, "count": len(hits),
            "headers": headers, "rows": hits,
            "detail": f"找到 {len(hits)} 行"}


# ══════════════════════════════════════════════════════════════
# 工具三：insert_kv_table
# ══════════════════════════════════════════════════════════════

def insert_kv_table(
    unpacked_dir: str,
    anchor_para_id: str,
    data: dict,
    position: str = "before",
    title: str = "",
) -> dict:
    """
    在指定段落前/后插入一个两列 key-value 表格。

    data 是任意 {键: 值} 字典，与业务字段无关。

    参数：
        unpacked_dir:   解包目录
        anchor_para_id: 锚点段落的 w14:paraId
        data:           {str: str} 字典，按顺序插入为表格行
        position:       "before" | "after"
        title:          表格标题（留空则不添加标题行）

    返回：
        {"status": "ok" | "not_found", "detail": str}
    """
    xml_path = Path(unpacked_dir) / "word" / "document.xml"
    tree = etree.parse(str(xml_path))
    root = tree.getroot()
    body = root.find(f"{{{W}}}body")

    anchor = next(
        (el for el in body.iter(f"{{{W}}}p")
         if el.get(f"{{{W14}}}paraId") == anchor_para_id),
        None
    )
    if anchor is None:
        return {"status": "not_found", "detail": f"paraId={anchor_para_id} 未找到"}

    anchor_top = anchor
    while anchor_top.getparent() is not None and anchor_top.getparent() != body:
        anchor_top = anchor_top.getparent()

    insert_idx = list(body).index(anchor_top)
    if position == "after":
        insert_idx += 1

    tbl = _build_kv_table(title, data)
    if title:
        p_title = _build_para(f"【{title}】", bold=True)
        body.insert(insert_idx, tbl)
        body.insert(insert_idx, p_title)
    else:
        body.insert(insert_idx, tbl)

    tree.write(str(xml_path), xml_declaration=True, encoding="UTF-8",
               standalone=True, pretty_print=True)

    return {"status": "ok",
            "detail": f"已在 {position} 位置插入 {len(data)} 行的 KV 表格"}


def _build_para(text: str, bold: bool = False) -> etree._Element:
    p = etree.Element(f"{{{W}}}p")
    p.set(f"{{{W14}}}paraId", _new_para_id())
    r = etree.SubElement(p, f"{{{W}}}r")
    if bold:
        rPr = etree.SubElement(r, f"{{{W}}}rPr")
        etree.SubElement(rPr, f"{{{W}}}b")
        etree.SubElement(rPr, f"{{{W}}}bCs")
    t = etree.SubElement(r, f"{{{W}}}t")
    t.text = text
    return p


def _build_kv_table(title: str, data: dict) -> etree._Element:
    tbl = etree.Element(f"{{{W}}}tbl")

    tblPr = etree.SubElement(tbl, f"{{{W}}}tblPr")
    tblW  = etree.SubElement(tblPr, f"{{{W}}}tblW")
    tblW.set(f"{{{W}}}w", "5000")
    tblW.set(f"{{{W}}}type", "pct")
    tblBorders = etree.SubElement(tblPr, f"{{{W}}}tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        b = etree.SubElement(tblBorders, f"{{{W}}}{side}")
        b.set(f"{{{W}}}val", "single")
        b.set(f"{{{W}}}sz", "4")
        b.set(f"{{{W}}}color", "000000")

    tblGrid = etree.SubElement(tbl, f"{{{W}}}tblGrid")
    for w in [1800, 3200]:
        gc = etree.SubElement(tblGrid, f"{{{W}}}gridCol")
        gc.set(f"{{{W}}}w", str(w))

    if title:
        tr = etree.SubElement(tbl, f"{{{W}}}tr")
        tc = etree.SubElement(tr, f"{{{W}}}tc")
        tcPr = etree.SubElement(tc, f"{{{W}}}tcPr")
        span = etree.SubElement(tcPr, f"{{{W}}}gridSpan")
        span.set(f"{{{W}}}val", "2")
        shd = etree.SubElement(tcPr, f"{{{W}}}shd")
        shd.set(f"{{{W}}}val", "clear")
        shd.set(f"{{{W}}}color", "auto")
        shd.set(f"{{{W}}}fill", "D9D9D9")
        p = etree.SubElement(tc, f"{{{W}}}p")
        p.set(f"{{{W14}}}paraId", _new_para_id())
        pPr = etree.SubElement(p, f"{{{W}}}pPr")
        jc = etree.SubElement(pPr, f"{{{W}}}jc")
        jc.set(f"{{{W}}}val", "center")
        r = etree.SubElement(p, f"{{{W}}}r")
        rPr = etree.SubElement(r, f"{{{W}}}rPr")
        etree.SubElement(rPr, f"{{{W}}}b")
        t = etree.SubElement(r, f"{{{W}}}t")
        t.text = title

    for key, val in data.items():
        tr = etree.SubElement(tbl, f"{{{W}}}tr")
        for cell_text, width in [(str(key), 1800), (str(val), 3200)]:
            tc = etree.SubElement(tr, f"{{{W}}}tc")
            tcPr = etree.SubElement(tc, f"{{{W}}}tcPr")
            w_el = etree.SubElement(tcPr, f"{{{W}}}tcW")
            w_el.set(f"{{{W}}}w", str(width))
            w_el.set(f"{{{W}}}type", "dxa")
            p = etree.SubElement(tc, f"{{{W}}}p")
            p.set(f"{{{W14}}}paraId", _new_para_id())
            r = etree.SubElement(p, f"{{{W}}}r")
            t = etree.SubElement(r, f"{{{W}}}t")
            t.text = cell_text

    return tbl


# ══════════════════════════════════════════════════════════════
# 工具四：read_table
# ══════════════════════════════════════════════════════════════

def read_table(
    source: str,
    body_idx: int,
    header_row: int = 0,
    key_col: int = 0,
    merge_continuation: bool = True,
    para_sep: str = "\n",
) -> dict:
    """
    将整张表格读为结构化数据，支持多段落单元格和续行合并。

    适用于任何 key-value 型表格（前附表、评分标准、资质要求等），
    agent 先用 list_tables 看到所有表和列名，自主决定读哪张表。

    参数：
        source:             .docx 路径 或 unpacked_dir 目录
        body_idx:           表格的 body_idx（从 list_tables 获取）
        header_row:         表头所在行（默认 0）
        key_col:            判断续行的列序号（默认 0，即第一列为空视为续行）
        merge_continuation: True 时合并续行，False 时每行独立返回
        para_sep:           单元格内多段落的连接符（默认换行符）

    返回：
        {
          "status":  "ok" | "not_found",
          "body_idx": int,
          "headers":  list[str],          # 列名列表
          "rows": [                        # merge_continuation=False 时每行独立
            {
              "cells": list[str],          # 各列文字（多段落已用 para_sep 连接）
              "cells_paras": list[list],   # 各列的段落列表（保留段落边界）
              "is_continuation": bool      # 是否是续行
            }
          ],
          "merged_rows": [                 # merge_continuation=True 时的合并结果
            {
              col_name: str,               # 各列文字，续行内容已追加
              col_name + "_paras": list    # 各列的段落列表
            }
          ],
          "detail": str
        }
    """
    children = _load_body_children(source)

    if body_idx >= len(children):
        return {"status": "not_found", "body_idx": body_idx,
                "headers": [], "rows": [], "merged_rows": [],
                "detail": f"body_idx={body_idx} 超出范围"}

    tbl = children[body_idx]
    if tbl.tag != f"{{{W}}}tbl":
        return {"status": "not_found", "body_idx": body_idx,
                "headers": [], "rows": [], "merged_rows": [],
                "detail": f"body_idx={body_idx} 处不是表格"}

    all_rows = tbl.findall(f".//{{{W}}}tr")
    if header_row >= len(all_rows):
        return {"status": "not_found", "body_idx": body_idx,
                "headers": [], "rows": [], "merged_rows": [],
                "detail": f"header_row={header_row} 超出表格行数"}

    headers = _row_texts(all_rows[header_row])

    # 解析所有数据行
    raw_rows = []
    for row in all_rows[header_row + 1:]:
        cells_el = row.findall(f"{{{W}}}tc")
        cells_paras = [_cell_paras(c) for c in cells_el]
        cells_text  = [para_sep.join(ps) for ps in cells_paras]

        # 补齐列数
        while len(cells_text) < len(headers):
            cells_text.append("")
            cells_paras.append([])

        is_continuation = (
            merge_continuation
            and key_col < len(cells_text)
            and not cells_text[key_col].strip()
        )
        raw_rows.append({
            "cells":           cells_text,
            "cells_paras":     cells_paras,
            "is_continuation": is_continuation,
        })

    # 合并续行
    merged = []
    for raw in raw_rows:
        if not any(raw["cells"]):          # 完全空行跳过
            continue
        if raw["is_continuation"] and merged:
            last = merged[-1]
            for i, h in enumerate(headers):
                new_paras = raw["cells_paras"][i] if i < len(raw["cells_paras"]) else []
                if new_paras:
                    last[h + "_paras"].extend(new_paras)
                    last[h] = para_sep.join(last[h + "_paras"])
        else:
            row_dict = {}
            for i, h in enumerate(headers):
                row_dict[h]            = raw["cells"][i] if i < len(raw["cells"]) else ""
                row_dict[h + "_paras"] = raw["cells_paras"][i] if i < len(raw["cells_paras"]) else []
            merged.append(row_dict)

    return {
        "status":      "ok",
        "body_idx":    body_idx,
        "headers":     headers,
        "rows":        raw_rows,
        "merged_rows": merged,
        "detail":      f"共 {len(all_rows)-1} 数据行，合并后 {len(merged)} 行",
    }


# ══════════════════════════════════════════════════════════════
# 工具五：fit_table_to_page
# ══════════════════════════════════════════════════════════════

def fit_table_to_page(
    unpacked_dir: str,
    body_idx: int,
    target_width_twips: int | None = None,
    shrink_only: bool = True,
    allow_wrap: bool = True,
) -> dict:
    """
    按表格所在 section 的可用页宽重算既有表格宽度。

    典型用途：
    - split 提取出的独立表格宽度仍沿用原文固定值，导致横向超页
    - 需要在不重建表格的前提下，按比例压缩 tblGrid / tcW

    参数：
        unpacked_dir:        已解包目录
        body_idx:            目标表格 body_idx（与 inspect/list_tables 坐标一致）
        target_width_twips:  目标宽度；留空则自动读取该位置所在 section 的可用页宽
        shrink_only:         True 时仅在表格超页时收缩，不放大较窄表格
        allow_wrap:          True 时删除 tcPr 下的 noWrap/fitText，允许换行

    返回：
        {
          "status": "ok" | "not_found" | "skipped",
          "body_idx": int,
          "current_width_twips": int | None,
          "target_width_twips": int | None,
          "scale_factor": float | None,
          "grid_cols_updated": int,
          "cell_widths_updated": int,
          "detail": str,
        }
    """
    tree, xml_path, body = _load_document_tree(unpacked_dir)
    children = list(body)
    if children and children[-1].tag == f"{{{W}}}sectPr":
        content_children = children[:-1]
    else:
        content_children = children

    if body_idx < 0 or body_idx >= len(content_children):
        return {
            "status": "not_found",
            "body_idx": body_idx,
            "current_width_twips": None,
            "target_width_twips": None,
            "scale_factor": None,
            "grid_cols_updated": 0,
            "cell_widths_updated": 0,
            "detail": f"body_idx={body_idx} 超出范围（共 {len(content_children)} 个 body 元素）",
        }

    tbl = content_children[body_idx]
    if tbl.tag != f"{{{W}}}tbl":
        return {
            "status": "not_found",
            "body_idx": body_idx,
            "current_width_twips": None,
            "target_width_twips": None,
            "scale_factor": None,
            "grid_cols_updated": 0,
            "cell_widths_updated": 0,
            "detail": f"body_idx={body_idx} 处不是表格",
        }

    if target_width_twips is None:
        sectPr = _active_sectpr_for_body_idx(body, body_idx)
        target_width_twips = _usable_page_width_twips(sectPr)
    if target_width_twips is None:
        return {
            "status": "not_found",
            "body_idx": body_idx,
            "current_width_twips": None,
            "target_width_twips": None,
            "scale_factor": None,
            "grid_cols_updated": 0,
            "cell_widths_updated": 0,
            "detail": "无法确定目标页宽，请显式传入 target_width_twips",
        }

    current_width = _table_current_width_twips(tbl)
    if current_width is None or current_width <= 0:
        return {
            "status": "not_found",
            "body_idx": body_idx,
            "current_width_twips": current_width,
            "target_width_twips": target_width_twips,
            "scale_factor": None,
            "grid_cols_updated": 0,
            "cell_widths_updated": 0,
            "detail": "无法从 tblGrid/tcW 推断当前表格宽度",
        }

    if shrink_only and current_width <= target_width_twips:
        return {
            "status": "skipped",
            "body_idx": body_idx,
            "current_width_twips": current_width,
            "target_width_twips": target_width_twips,
            "scale_factor": 1.0,
            "grid_cols_updated": 0,
            "cell_widths_updated": 0,
            "detail": "表格当前宽度未超过页面可用宽度，无需调整",
        }

    scale_factor = target_width_twips / current_width

    tblPr = tbl.find(f"{{{W}}}tblPr")
    if tblPr is None:
        tblPr = etree.Element(f"{{{W}}}tblPr")
        tbl.insert(0, tblPr)

    tblW = tblPr.find(f"{{{W}}}tblW")
    if tblW is None:
        tblW = etree.SubElement(tblPr, f"{{{W}}}tblW")
    tblW.set(f"{{{W}}}type", "dxa")
    tblW.set(f"{{{W}}}w", str(int(target_width_twips)))

    tblLayout = tblPr.find(f"{{{W}}}tblLayout")
    if tblLayout is None:
        tblLayout = etree.SubElement(tblPr, f"{{{W}}}tblLayout")
    tblLayout.set(f"{{{W}}}type", "fixed")

    grid_cols_updated = 0
    tblGrid = tbl.find(f"{{{W}}}tblGrid")
    if tblGrid is not None:
        grid_nodes = tblGrid.findall(f"{{{W}}}gridCol")
        grid_vals = [_to_int(gc.get(f"{{{W}}}w")) or 0 for gc in grid_nodes]
        if grid_vals and sum(grid_vals) > 0:
            scaled_grid = _scale_ints(grid_vals, int(target_width_twips))
            for node, width in zip(grid_nodes, scaled_grid):
                node.set(f"{{{W}}}w", str(width))
            grid_cols_updated = len(grid_nodes)

    cell_widths_updated = 0
    for tc in tbl.findall(f".//{{{W}}}tc"):
        tcPr = tc.find(f"{{{W}}}tcPr")
        if tcPr is None:
            continue

        if allow_wrap:
            for tag in (f"{{{W}}}noWrap", f"{{{W}}}fitText"):
                for node in tcPr.findall(tag):
                    tcPr.remove(node)

        tcW = tcPr.find(f"{{{W}}}tcW")
        if tcW is None or tcW.get(f"{{{W}}}type") != "dxa":
            continue
        width = _to_int(tcW.get(f"{{{W}}}w"))
        if width is None or width <= 0:
            continue
        scaled_width = max(1, int(round(width * scale_factor)))
        tcW.set(f"{{{W}}}w", str(scaled_width))
        cell_widths_updated += 1

    tree.write(
        str(xml_path),
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
        pretty_print=True,
    )

    return {
        "status": "ok",
        "body_idx": body_idx,
        "current_width_twips": current_width,
        "target_width_twips": int(target_width_twips),
        "scale_factor": round(scale_factor, 6),
        "grid_cols_updated": grid_cols_updated,
        "cell_widths_updated": cell_widths_updated,
        "detail": f"已将表格宽度从 {current_width} twips 调整到 {int(target_width_twips)} twips",
    }
