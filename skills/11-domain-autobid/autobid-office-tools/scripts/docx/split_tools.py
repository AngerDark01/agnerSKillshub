"""Skill-scoped DOCX split and join entry points."""

from .doc_tools import join_by_manifest, split_by_range

__all__ = [
    "split_by_range",
    "join_by_manifest",
]
