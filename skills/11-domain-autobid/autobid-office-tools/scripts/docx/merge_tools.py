"""
scripts/docx/merge_tools.py
===========================
对 unpack 后的 DOCX document body 做低层拼接，并复制所需图片/关系资源。

设计原则：
    - 只做 body 元素与 document.xml.rels / media 的机械合并
    - 不做章节保留/删除/重编号等语义判断
    - 允许 AI 先决定“拼哪些段”，工具只负责安全追加
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Optional

from lxml import etree

from .layout_tools import (
    R,
    REL_TAG,
    _copy_part_recursive,
    _find_rel,
    _load_or_create_rels,
    _load_xml,
    _next_rid,
    _relative_target,
    _resolve_target,
    _save_xml,
    _w_tag,
    _xml_path,
)


def _document_tree(unpacked_dir: str) -> etree._ElementTree:
    return _load_xml(_xml_path(unpacked_dir, "word/document.xml"))


def _body_children_without_doc_sectpr(body: etree._Element) -> tuple[list[etree._Element], Optional[etree._Element]]:
    children = list(body)
    if children and children[-1].tag == _w_tag("sectPr"):
        return children[:-1], children[-1]
    return children, None


def _next_part_name_like(target_unpacked_dir: str, desired_relpath: str) -> str:
    desired_relpath = desired_relpath.replace("\\", "/")
    if not _xml_path(target_unpacked_dir, desired_relpath).exists():
        return desired_relpath

    path = Path(desired_relpath)
    parent = str(path.parent).replace("\\", "/")
    stem = path.stem
    suffix = path.suffix
    idx = 1
    while True:
        candidate_name = f"{stem}_{idx}{suffix}"
        candidate = f"{parent}/{candidate_name}" if parent not in ("", ".") else candidate_name
        if not _xml_path(target_unpacked_dir, candidate).exists():
            return candidate
        idx += 1


def _collect_rids(nodes: list[etree._Element]) -> set[str]:
    rid_set: set[str] = set()
    r_ns_prefix = f"{{{R}}}"
    for node in nodes:
        for elem in node.iter():
            for attr_name, attr_val in elem.attrib.items():
                if attr_name.startswith(r_ns_prefix) and attr_val:
                    rid_set.add(attr_val)
    return rid_set


def _rewrite_rids(nodes: list[etree._Element], rid_map: dict[str, str]) -> None:
    if not rid_map:
        return
    r_ns_prefix = f"{{{R}}}"
    for node in nodes:
        for elem in node.iter():
            for attr_name, attr_val in list(elem.attrib.items()):
                if attr_name.startswith(r_ns_prefix) and attr_val in rid_map:
                    elem.set(attr_name, rid_map[attr_val])


def append_body_from_unpacked(
    target_unpacked_dir: str,
    source_unpacked_dir: str,
    start: int | None = None,
    end: int | None = None,
) -> dict:
    """
    将 source 的 body 元素范围追加到 target 的 document body 末尾（末尾 sectPr 前）。

    参数：
        target_unpacked_dir: 目标 unpack 目录
        source_unpacked_dir: 来源 unpack 目录
        start/end:          来源 body child 范围，基于“去掉文档级 sectPr 后”的索引

    返回：
        {
          "status": "ok",
          "appended": N,
          "start": s,
          "end": e,
          "rid_map": {...},
          "copied_parts": {...}
        }
    """
    target_tree = _document_tree(target_unpacked_dir)
    source_tree = _document_tree(source_unpacked_dir)
    target_root = target_tree.getroot()
    source_root = source_tree.getroot()
    target_body = target_root.find(_w_tag("body"))
    source_body = source_root.find(_w_tag("body"))
    if target_body is None or source_body is None:
        raise RuntimeError("document.xml 缺少 w:body")

    target_children, target_sectpr = _body_children_without_doc_sectpr(target_body)
    source_children, _source_sectpr = _body_children_without_doc_sectpr(source_body)

    s = start if start is not None else 0
    e = end if end is not None else len(source_children)
    s = max(0, s)
    e = min(len(source_children), e)
    selected = [copy.deepcopy(source_children[i]) for i in range(s, e)]

    source_rels_tree = _load_or_create_rels(source_unpacked_dir, "word/_rels/document.xml.rels")
    source_rels_root = source_rels_tree.getroot()
    target_rels_tree = _load_or_create_rels(target_unpacked_dir, "word/_rels/document.xml.rels")
    target_rels_root = target_rels_tree.getroot()

    copied_parts: dict[str, str] = {}
    rid_map: dict[str, str] = {}

    for old_rid in sorted(_collect_rids(selected)):
        src_rel = _find_rel(source_rels_root, old_rid)
        if src_rel is None:
            continue

        new_rid = _next_rid(target_rels_root)
        new_rel = copy.deepcopy(src_rel)
        new_rel.set("Id", new_rid)

        if src_rel.get("TargetMode") == "External":
            target_rels_root.append(new_rel)
            rid_map[old_rid] = new_rid
            continue

        src_target = src_rel.get("Target")
        if not src_target:
            continue

        src_part_relpath = _resolve_target("word/document.xml", src_target)
        dst_part_relpath = _next_part_name_like(target_unpacked_dir, src_part_relpath)
        dst_part_relpath = _copy_part_recursive(
            source_unpacked_dir,
            target_unpacked_dir,
            src_part_relpath,
            dst_part_relpath,
            copied_parts,
        )
        new_rel.set("Target", _relative_target("word/document.xml", dst_part_relpath))
        target_rels_root.append(new_rel)
        rid_map[old_rid] = new_rid

    _rewrite_rids(selected, rid_map)

    if target_sectpr is not None:
        insert_at = list(target_body).index(target_sectpr)
    else:
        insert_at = len(list(target_body))
    for idx, node in enumerate(selected):
        target_body.insert(insert_at + idx, node)

    _save_xml(target_tree, _xml_path(target_unpacked_dir, "word/document.xml"))
    _save_xml(target_rels_tree, _xml_path(target_unpacked_dir, "word/_rels/document.xml.rels"))

    return {
        "status": "ok",
        "appended": len(selected),
        "start": s,
        "end": e,
        "rid_map": rid_map,
        "copied_parts": copied_parts,
    }
