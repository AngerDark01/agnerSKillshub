"""
scripts/docx/layout_tools.py
============================
在 unpack/pack 流程中，对 section / 页边距 / 页眉页脚 / logo 相关资源做底层操作。

设计原则：
    - 只做 XML / 关系 / 资源复制，不写死任何业务章节
    - 目标文档与模板文档都使用 unpack 后的目录
    - 版式和页眉页脚可分开复用：
        1. copy_section_layout          复制页边距、页码、标题页等 section 布局
        2. copy_header_footer_template  复制页眉页脚 XML 及其依赖图片/logo
"""

from __future__ import annotations

import copy
import posixpath
import re
from pathlib import Path
from typing import Optional

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"

NS_W = {"w": W, "r": R}
REL_TAG = f"{{{PR}}}Relationship"


def _w_tag(local: str) -> str:
    return f"{{{W}}}{local}"


def _w_attr(local: str) -> str:
    return f"{{{W}}}{local}"

LAYOUT_CHILD_TAGS = {
    "type",
    "pgSz",
    "pgMar",
    "paperSrc",
    "pgBorders",
    "lnNumType",
    "pgNumType",
    "cols",
    "formProt",
    "vAlign",
    "noEndnote",
    "titlePg",
    "textDirection",
    "bidi",
    "rtlGutter",
    "docGrid",
    "printerSettings",
}


def _xml_path(unpacked_dir: str, relpath: str) -> Path:
    return Path(unpacked_dir) / relpath


def _load_xml(path: Path) -> etree._ElementTree:
    return etree.parse(str(path))


def _save_xml(tree: etree._ElementTree, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(
        str(path),
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
        pretty_print=True,
    )


def _rels_path_for_part(part_relpath: str) -> str:
    part = Path(part_relpath)
    return str(part.parent / "_rels" / f"{part.name}.rels").replace("\\", "/")


def _load_or_create_rels(unpacked_dir: str, rels_relpath: str) -> etree._ElementTree:
    path = _xml_path(unpacked_dir, rels_relpath)
    if path.exists():
        return _load_xml(path)
    root = etree.Element(f"{{{PR}}}Relationships", nsmap={None: PR})
    return etree.ElementTree(root)


def _find_rel(root: etree._Element, rel_id: str) -> Optional[etree._Element]:
    for rel in root.findall(REL_TAG):
        if rel.get("Id") == rel_id:
            return rel
    return None


def _next_rid(rels_root: etree._Element) -> str:
    max_id = 0
    for rel in rels_root.findall(REL_TAG):
        rid = rel.get("Id", "")
        m = re.fullmatch(r"rId(\d+)", rid)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return f"rId{max_id + 1}"


def _resolve_target(from_part_relpath: str, target: str) -> str:
    base = posixpath.dirname(from_part_relpath)
    return posixpath.normpath(posixpath.join(base, target))


def _relative_target(from_part_relpath: str, to_part_relpath: str) -> str:
    base = posixpath.dirname(from_part_relpath)
    rel = posixpath.relpath(to_part_relpath, start=base)
    return rel


def _content_types_tree(unpacked_dir: str) -> etree._ElementTree:
    return _load_xml(_xml_path(unpacked_dir, "[Content_Types].xml"))


def _ensure_content_type(
    template_unpacked_dir: str,
    target_unpacked_dir: str,
    src_part_relpath: str,
    dst_part_relpath: str,
) -> None:
    template_tree = _content_types_tree(template_unpacked_dir)
    target_tree = _content_types_tree(target_unpacked_dir)
    template_root = template_tree.getroot()
    target_root = target_tree.getroot()

    src_part_name = "/" + src_part_relpath
    dst_part_name = "/" + dst_part_relpath

    src_override = None
    for node in template_root.findall(f"{{{CT}}}Override"):
        if node.get("PartName") == src_part_name:
            src_override = node
            break

    if src_override is not None:
        exists = any(
            node.get("PartName") == dst_part_name
            for node in target_root.findall(f"{{{CT}}}Override")
        )
        if not exists:
            new_node = copy.deepcopy(src_override)
            new_node.set("PartName", dst_part_name)
            target_root.append(new_node)
            _save_xml(target_tree, _xml_path(target_unpacked_dir, "[Content_Types].xml"))
        return

    ext = Path(dst_part_relpath).suffix.lstrip(".").lower()
    if not ext:
        return

    target_has_default = any(
        node.get("Extension", "").lower() == ext
        for node in target_root.findall(f"{{{CT}}}Default")
    )
    if target_has_default:
        return

    src_default = None
    for node in template_root.findall(f"{{{CT}}}Default"):
        if node.get("Extension", "").lower() == ext:
            src_default = node
            break

    if src_default is not None:
        target_root.append(copy.deepcopy(src_default))
        _save_xml(target_tree, _xml_path(target_unpacked_dir, "[Content_Types].xml"))


def _next_part_name(target_unpacked_dir: str, prefix: str, suffix: str) -> str:
    idx = 1
    while True:
        relpath = f"word/{prefix}{idx}{suffix}"
        if not _xml_path(target_unpacked_dir, relpath).exists():
            return relpath
        idx += 1


def _copy_part_recursive(
    template_unpacked_dir: str,
    target_unpacked_dir: str,
    src_part_relpath: str,
    dst_part_relpath: str,
    copied: dict[str, str],
) -> str:
    src_part_relpath = src_part_relpath.replace("\\", "/")
    dst_part_relpath = dst_part_relpath.replace("\\", "/")

    if src_part_relpath in copied:
        return copied[src_part_relpath]

    src_path = _xml_path(template_unpacked_dir, src_part_relpath)
    dst_path = _xml_path(target_unpacked_dir, dst_part_relpath)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_bytes(src_path.read_bytes())
    copied[src_part_relpath] = dst_part_relpath

    _ensure_content_type(template_unpacked_dir, target_unpacked_dir, src_part_relpath, dst_part_relpath)

    src_rels_relpath = _rels_path_for_part(src_part_relpath)
    src_rels_path = _xml_path(template_unpacked_dir, src_rels_relpath)
    if not src_rels_path.exists():
        return dst_part_relpath

    src_rels_tree = _load_xml(src_rels_path)
    src_rels_root = src_rels_tree.getroot()
    dst_rels_tree = _load_or_create_rels(target_unpacked_dir, _rels_path_for_part(dst_part_relpath))
    dst_rels_root = dst_rels_tree.getroot()

    for child in list(dst_rels_root):
        dst_rels_root.remove(child)

    for rel in src_rels_root.findall(REL_TAG):
        new_rel = copy.deepcopy(rel)
        target = rel.get("Target")
        target_mode = rel.get("TargetMode")
        if target and target_mode != "External":
            resolved_src = _resolve_target(src_part_relpath, target)
            src_child_path = _xml_path(template_unpacked_dir, resolved_src)
            if src_child_path.exists():
                stem = Path(resolved_src).stem
                suffix = Path(resolved_src).suffix
                if stem.startswith("header"):
                    dst_child = _next_part_name(target_unpacked_dir, "header", suffix)
                elif stem.startswith("footer"):
                    dst_child = _next_part_name(target_unpacked_dir, "footer", suffix)
                elif "media/" in resolved_src:
                    dst_child = _next_part_name(target_unpacked_dir, "media/image", suffix)
                else:
                    prefix = Path(resolved_src).parent.name + "/" + stem
                    dst_child = _next_part_name(target_unpacked_dir, prefix, suffix)
                real_dst_child = _copy_part_recursive(
                    template_unpacked_dir,
                    target_unpacked_dir,
                    resolved_src,
                    dst_child,
                    copied,
                )
                new_rel.set("Target", _relative_target(dst_part_relpath, real_dst_child))
        dst_rels_root.append(new_rel)

    _save_xml(dst_rels_tree, _xml_path(target_unpacked_dir, _rels_path_for_part(dst_part_relpath)))
    return dst_part_relpath


def _find_sections(doc_tree: etree._ElementTree) -> list[dict]:
    root = doc_tree.getroot()
    body = root.find(f"{{{W}}}body")
    sections = []

    for child in list(body):
        if child.tag == f"{{{W}}}p":
            pPr = child.find(f"{{{W}}}pPr")
            sectPr = pPr.find(f"{{{W}}}sectPr") if pPr is not None else None
            if sectPr is not None:
                sections.append({"kind": "inline", "elem": sectPr, "parent": pPr})
        elif child.tag == f"{{{W}}}sectPr":
            sections.append({"kind": "body", "elem": child, "parent": body})

    return sections


def _ensure_last_body_sectpr(doc_tree: etree._ElementTree) -> dict:
    sections = _find_sections(doc_tree)
    if sections:
        return sections[-1]

    root = doc_tree.getroot()
    body = root.find(f"{{{W}}}body")
    sectPr = etree.SubElement(body, f"{{{W}}}sectPr")
    return {"kind": "body", "elem": sectPr, "parent": body}


def _summarize_sectpr(sectPr: etree._Element) -> dict:
    pgMar = sectPr.find("w:pgMar", NS_W)
    pgSz = sectPr.find("w:pgSz", NS_W)
    titlePg = sectPr.find("w:titlePg", NS_W)
    pgNumType = sectPr.find("w:pgNumType", NS_W)

    def ref_summary(tag: str) -> list[dict]:
        out = []
        for node in sectPr.findall(f"w:{tag}", NS_W):
            out.append({
                "type": node.get(f"{{{W}}}type"),
                "rId": node.get(f"{{{R}}}id"),
            })
        return out

    return {
        "page_size": dict(pgSz.attrib) if pgSz is not None else None,
        "page_margin": dict(pgMar.attrib) if pgMar is not None else None,
        "title_page": titlePg is not None,
        "page_number": dict(pgNumType.attrib) if pgNumType is not None else None,
        "headers": ref_summary("headerReference"),
        "footers": ref_summary("footerReference"),
    }


def inspect_sections(unpacked_dir: str) -> dict:
    """
    读取 unpacked 文档中的 section 信息。
    """
    doc_tree = _load_xml(_xml_path(unpacked_dir, "word/document.xml"))
    sections = _find_sections(doc_tree)

    result = []
    for idx, section in enumerate(sections):
        summary = _summarize_sectpr(section["elem"])
        summary["index"] = idx
        summary["kind"] = section["kind"]
        result.append(summary)

    return {"status": "ok", "sections": result, "count": len(result)}


def copy_section_layout(
    template_unpacked_dir: str,
    target_unpacked_dir: str,
    template_section_idx: int = -1,
    target_section_idx: int = -1,
    include_header_footer: bool = False,
) -> dict:
    """
    复制 section 布局属性。

    默认只复制页边距、页码、标题页、纸张等布局属性，不复制页眉页脚引用。
    """
    template_doc = _load_xml(_xml_path(template_unpacked_dir, "word/document.xml"))
    target_doc = _load_xml(_xml_path(target_unpacked_dir, "word/document.xml"))

    template_sections = _find_sections(template_doc)
    target_sections = _find_sections(target_doc)

    if not template_sections:
        return {"status": "not_found", "detail": "模板文档没有 sectPr"}

    template_section = template_sections[template_section_idx]
    if target_sections:
        target_section = target_sections[target_section_idx]
    else:
        target_section = _ensure_last_body_sectpr(target_doc)

    target_elem = target_section["elem"]
    template_elem = template_section["elem"]

    for child in list(target_elem):
        local = etree.QName(child).localname
        if include_header_footer or local in LAYOUT_CHILD_TAGS:
            target_elem.remove(child)

    if include_header_footer:
        for child in list(template_elem):
            target_elem.append(copy.deepcopy(child))
    else:
        for child in list(template_elem):
            local = etree.QName(child).localname
            if local in LAYOUT_CHILD_TAGS:
                target_elem.append(copy.deepcopy(child))

    for key in list(target_elem.attrib):
        del target_elem.attrib[key]
    for key, value in template_elem.attrib.items():
        target_elem.set(key, value)

    _save_xml(target_doc, _xml_path(target_unpacked_dir, "word/document.xml"))
    return {
        "status": "ok",
        "template_section_idx": template_section_idx,
        "target_section_idx": target_section_idx,
        "include_header_footer": include_header_footer,
        "section": _summarize_sectpr(target_elem),
    }


def copy_header_footer_template(
    template_unpacked_dir: str,
    target_unpacked_dir: str,
    template_section_idx: int = -1,
    target_section_idx: int = -1,
) -> dict:
    """
    复制模板文档的页眉页脚及其依赖资源。

    该函数只复制 header/footer 引用与相关 part，不改页边距等布局属性。
    """
    template_doc = _load_xml(_xml_path(template_unpacked_dir, "word/document.xml"))
    target_doc = _load_xml(_xml_path(target_unpacked_dir, "word/document.xml"))

    template_sections = _find_sections(template_doc)
    target_sections = _find_sections(target_doc)
    if not template_sections:
        return {"status": "not_found", "detail": "模板文档没有 sectPr"}

    template_section = template_sections[template_section_idx]
    if target_sections:
        target_section = target_sections[target_section_idx]
    else:
        target_section = _ensure_last_body_sectpr(target_doc)

    template_sectPr = template_section["elem"]
    target_sectPr = target_section["elem"]

    template_doc_rels = _load_or_create_rels(template_unpacked_dir, "word/_rels/document.xml.rels")
    target_doc_rels = _load_or_create_rels(target_unpacked_dir, "word/_rels/document.xml.rels")
    template_doc_rels_root = template_doc_rels.getroot()
    target_doc_rels_root = target_doc_rels.getroot()

    for child in list(target_sectPr):
        local = etree.QName(child).localname
        if local in {"headerReference", "footerReference"}:
            target_sectPr.remove(child)

    copied: dict[str, str] = {}
    new_refs = []

    for child in list(template_sectPr):
        local = etree.QName(child).localname
        if local not in {"headerReference", "footerReference"}:
            continue
        src_rid = child.get(f"{{{R}}}id")
        src_rel = _find_rel(template_doc_rels_root, src_rid)
        if src_rel is None:
            continue

        src_target = src_rel.get("Target")
        src_part_relpath = _resolve_target("word/document.xml", src_target)
        suffix = Path(src_part_relpath).suffix
        prefix = "header" if local == "headerReference" else "footer"
        dst_part_relpath = _next_part_name(target_unpacked_dir, prefix, suffix)
        dst_part_relpath = _copy_part_recursive(
            template_unpacked_dir,
            target_unpacked_dir,
            src_part_relpath,
            dst_part_relpath,
            copied,
        )

        new_rid = _next_rid(target_doc_rels_root)
        new_rel = etree.Element(REL_TAG)
        new_rel.set("Id", new_rid)
        new_rel.set("Type", src_rel.get("Type"))
        new_rel.set("Target", _relative_target("word/document.xml", dst_part_relpath))
        target_doc_rels_root.append(new_rel)

        new_ref = copy.deepcopy(child)
        new_ref.set(f"{{{R}}}id", new_rid)
        new_refs.append(new_ref)

    insert_pos = 0
    for ref in new_refs:
        target_sectPr.insert(insert_pos, ref)
        insert_pos += 1

    _save_xml(target_doc, _xml_path(target_unpacked_dir, "word/document.xml"))
    _save_xml(target_doc_rels, _xml_path(target_unpacked_dir, "word/_rels/document.xml.rels"))
    return {
        "status": "ok",
        "template_section_idx": template_section_idx,
        "target_section_idx": target_section_idx,
        "copied_parts": copied,
        "section": _summarize_sectpr(target_sectPr),
    }


def set_section_layout(
    unpacked_dir: str,
    section_idx: int = -1,
    page_margin_twips: dict | None = None,
    page_size_twips: dict | None = None,
    title_page: bool | None = None,
    page_number_start: int | None = None,
    page_number_format: str | None = None,
) -> dict:
    """
    显式设置 section 布局属性。

    设计目标：
    - 工具只负责把给定值写入 sectPr
    - 不决定“应该写什么值”
    - 适合由 agent 读取格式规范 JSON 后调用

    参数示例：
        page_margin_twips = {
            "top": 1474,
            "right": 1417,
            "bottom": 1247,
            "left": 1417,
            "header": 1134,
            "footer": 850,
        }
        page_size_twips = {"w": 11906, "h": 16838}
    """
    doc_tree = _load_xml(_xml_path(unpacked_dir, "word/document.xml"))
    sections = _find_sections(doc_tree)
    if sections:
        section = sections[section_idx]
    else:
        section = _ensure_last_body_sectpr(doc_tree)

    sectPr = section["elem"]

    if page_size_twips:
        pgSz = sectPr.find("w:pgSz", NS_W)
        if pgSz is None:
            pgSz = etree.SubElement(sectPr, _w_tag("pgSz"))
        for key in ("w", "h"):
            if key in page_size_twips and page_size_twips[key] is not None:
                pgSz.set(_w_attr(key), str(int(page_size_twips[key])))

    if page_margin_twips:
        pgMar = sectPr.find("w:pgMar", NS_W)
        if pgMar is None:
            pgMar = etree.SubElement(sectPr, _w_tag("pgMar"))
        for key in ("top", "right", "bottom", "left", "header", "footer", "gutter"):
            if key in page_margin_twips and page_margin_twips[key] is not None:
                pgMar.set(_w_attr(key), str(int(page_margin_twips[key])))

    if title_page is not None:
        title_page_elem = sectPr.find("w:titlePg", NS_W)
        if title_page:
            if title_page_elem is None:
                sectPr.insert(0, etree.Element(_w_tag("titlePg")))
        elif title_page_elem is not None:
            sectPr.remove(title_page_elem)

    if page_number_start is not None or page_number_format is not None:
        pg_num = sectPr.find("w:pgNumType", NS_W)
        if pg_num is None:
            pg_num = etree.SubElement(sectPr, _w_tag("pgNumType"))
        if page_number_start is not None:
            pg_num.set(_w_attr("start"), str(int(page_number_start)))
        if page_number_format is not None:
            pg_num.set(_w_attr("fmt"), str(page_number_format))

    _save_xml(doc_tree, _xml_path(unpacked_dir, "word/document.xml"))
    return {
        "status": "ok",
        "section_idx": section_idx,
        "section": _summarize_sectpr(sectPr),
    }
