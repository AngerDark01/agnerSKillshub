"""
pack_tools.py
=============
对 `scripts/office/` 中 unpack/pack 运行时脚本的封装。

解决原始脚本依赖 CWD 的问题：原脚本用裸包导入（from helpers import ...，
from validators import ...），只能在 scripts/office/ 目录下运行。
本模块在调用前将 scripts/office/ 注入 sys.path，使其可从任意位置调用。

用法：
    from scripts.docx.pack_tools import unpack, pack

    result = unpack("input.docx", "unpacked/")
    result = pack("unpacked/", "output.docx", original="input.docx")

前提：
    `scripts/office/` 目录（含 helpers/、validators/、schemas/）须与本文件
    位于同一个项目布局下。如需自定义，设置 DOCX_SCRIPTS_DIR 环境变量。
"""

import os
import sys
import importlib
from pathlib import Path


# ── 定位 scripts/office/ ──────────────────────────────────────────────────────

def _get_office_dir() -> Path:
    env = os.environ.get("DOCX_SCRIPTS_DIR")
    if env:
        p = Path(env)
        if p.is_dir():
            return p.resolve()
        raise RuntimeError(f"DOCX_SCRIPTS_DIR={env} 不存在或不是目录")

    # 兼容两种布局：
    # 1. scripts/docx/pack_tools.py + scripts/office/
    # 2. 其他调用方通过 DOCX_SCRIPTS_DIR 明确指定
    here = Path(__file__).parent.resolve()
    candidates = [
        here.parent / "office",
        here / "office",
        here.parent.parent / "scripts" / "office",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()

    raise RuntimeError(
        f"找不到 scripts/office/ 目录（在 {here} 下查找）。\n"
        "请将 scripts/office/ 放在本文件旁边，或设置 DOCX_SCRIPTS_DIR 环境变量。"
    )


def _inject_office_path() -> Path:
    """将 scripts/office/ 注入 sys.path（幂等）。返回该目录路径。"""
    office_dir = _get_office_dir()
    office_str = str(office_dir)
    if office_str not in sys.path:
        sys.path.insert(0, office_str)
    return office_dir


# ── unpack ────────────────────────────────────────────────────────────────────

def unpack(
    input_file: str,
    output_dir: str,
    merge_runs: bool = True,
    simplify_redlines: bool = True,
) -> dict:
    """
    解包 DOCX/PPTX/XLSX 为可编辑的 XML 目录。

    参数：
        input_file:        源文件路径（.docx / .pptx / .xlsx）
        output_dir:        解包目标目录（不存在会自动创建）
        merge_runs:        合并相邻格式相同的 <w:r>（DOCX only，默认 True）
        simplify_redlines: 合并同作者的相邻修订（DOCX only，默认 True）

    返回：
        {"status": "ok" | "error", "message": str}
    """
    _inject_office_path()

    # 重新导入确保拿到注入后的模块
    if "unpack" in sys.modules:
        del sys.modules["unpack"]
    unpack_mod = importlib.import_module("unpack")

    _, message = unpack_mod.unpack(
        input_file=str(input_file),
        output_directory=str(output_dir),
        merge_runs=merge_runs,
        simplify_redlines=simplify_redlines,
    )

    status = "error" if message.startswith("Error") else "ok"
    return {"status": status, "message": message}


# ── pack ──────────────────────────────────────────────────────────────────────

def pack(
    unpacked_dir: str,
    output_file: str,
    original: str | None = None,
    validate: bool = True,
) -> dict:
    """
    将已编辑的解包目录重新打包为 DOCX/PPTX/XLSX。

    参数：
        unpacked_dir:  解包目录路径
        output_file:   输出文件路径（.docx / .pptx / .xlsx）
        original:      原始文件路径，用于验证段落数差异（推荐传入）
        validate:      是否运行 schema 验证 + 自动修复（默认 True）

    返回：
        {"status": "ok" | "error", "message": str}

    pack 会打印验证结果到 stdout，包括：
        Auto-repaired N issue(s)
        Paragraphs: 18 → 21 (+3)
        All validations PASSED!
    """
    _inject_office_path()

    if "pack" in sys.modules:
        del sys.modules["pack"]
    pack_mod = importlib.import_module("pack")

    _, message = pack_mod.pack(
        input_directory=str(unpacked_dir),
        output_file=str(output_file),
        original_file=str(original) if original else None,
        validate=validate,
    )

    status = "error" if message.startswith("Error") else "ok"
    return {"status": status, "message": message}
