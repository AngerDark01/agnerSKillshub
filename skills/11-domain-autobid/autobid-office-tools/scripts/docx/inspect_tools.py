"""Skill-scoped DOCX inspection entry points."""

from .doc_tools import find_by_regex, inspect, list_builtin_patterns, read_body_xml

__all__ = [
    "inspect",
    "read_body_xml",
    "find_by_regex",
    "list_builtin_patterns",
]
