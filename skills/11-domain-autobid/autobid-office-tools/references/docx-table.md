---
name: docx-table
description: >
  当需要在 DOCX 中定位表格、理解列结构、按条件提取行，或把整张表读成结构化数据时使用。
  永远先调用 `list_tables` 查看实际列名和列序号。适用于字段可能藏在表格里，或需要把整张表转成结构化结果的场景。
---

# DOCX 表格

## 概述

在 DOCX 文档内操作表格的基础设施工具。不绑定任何业务字段名。

**核心约定**：先 `list_tables` 看实际列名和序号，由执行代理判断哪张表含目标数据，
再用列序号操作。不猜列名，不假设表格结构。

## 工具

```python
from scripts.docx.table_tools import (
    list_tables,
    extract_table_rows,
    read_table,
    insert_kv_table,
    fit_table_to_page,
)
```

---

### list_tables：列出所有表格

```python
r = list_tables("file.docx")      # 或 list_tables("unpacked/")
# →
# {
#   "count": int,
#   "tables": [
#     {
#       "body_idx": int,
#       "rows": int, "cols": int,
#       "headers_indexed": ["[0]列名A", "[1]列名B", ...],
#       "header_row2": [...]
#     }
#   ]
# }
```

**始终首先调用**。根据 `headers_indexed` 自主判断哪张表含目标数据，
决定用哪个 body_idx、哪些列序号。

---

### extract_table_rows：按列序号提取匹配行

```python
r = extract_table_rows(
    source   = "file.docx",
    body_idx = 79,
    match    = {2: "目标值A", 3: "目标值B"},  # 列序号(int): 精确值
)
# → {"status": "ok"|"not_found"|"ambiguous", "count": int,
#    "headers": list, "rows": list[dict]}
```

适合：按条件查找特定行（如按分标名称+包号找一行）。
match key 必须是列序号（int），精确匹配。

---

### read_table：把整张表读成结构化数据

```python
r = read_table(
    source             = "unpacked/",
    body_idx           = 1,       # 从 list_tables 获取
    header_row         = 0,       # 表头所在行
    key_col            = 0,       # 哪列为空时视为续行（默认第0列）
    merge_continuation = True,    # 是否合并续行
    para_sep           = "\n",    # 多段落连接符
)
# →
# {
#   "status": "ok" | "not_found",
#   "headers": list[str],
#   "merged_rows": [              # 续行已合并的结果
#     {
#       "列名":        str,        # 多段落用 para_sep 连接
#       "列名_paras":  list[str]   # 保留段落边界
#     }
#   ],
#   "rows": [...]                 # 未合并的原始行（含 is_continuation 标记）
# }
```

适合：读整张表，尤其是：
- KV 型表格（条款号/名称/内容，有续行）
- 评分标准表、资质要求表
- 任何需要完整读取后再筛选的表格

**续行合并规则**：`key_col` 指定的列为空时，该行视为上一行的续行，
内容追加到上一行对应列的 `_paras` 列表中。执行代理可根据实际表格结构
调整 `key_col`（不一定是第0列）。

**多段落**：每个单元格内的多个段落，文字用 `para_sep` 连接存入主字段，
同时保留在 `列名_paras` 列表中供需要区分段落语义的场景使用。

---

### insert_kv_table：插入 KV 表格

```python
r = insert_kv_table(
    unpacked_dir   = "unpacked/",
    anchor_para_id = "14D14AEF",
    data           = {"键A": "值A", "键B": "值B"},
    position       = "after",
    title          = "可选标题",
)
# → {"status": "ok"|"not_found", "detail": str}
```

---

### fit_table_to_page：把超页表格压回页面宽度

```python
r = fit_table_to_page(
    unpacked_dir = "unpacked/",
    body_idx     = 79,      # 从 list_tables / inspect 获取
)
# → {
#   "status": "ok" | "skipped" | "not_found",
#   "current_width_twips": int,
#   "target_width_twips": int,
#   "scale_factor": float,
# }
```

适合：
- 拆出来的单表 DOCX 横向超页
- 原表使用固定 `tblGrid/tcW` 宽度，需要按当前 section 页宽同比缩放

注意：
- 这是写操作，只接受 `unpacked/` 目录，不直接改 `.docx`
- 常见调用顺序是 `unpack -> fit_table_to_page -> pack`

---

## 调用顺序

```
list_tables(source)
    ↓ 看 headers_indexed，自主判断目标表

提取特定行:
    extract_table_rows(source, body_idx, match={列序号: 值})
    → status==ok → rows[0] 取目标列值
    → not_found  → 返回上层，按 `../../autobid-phase1-extractor/references/phase1-preschedule-field-lookup.md` 继续下一路径

读整张表:
    read_table(source, body_idx, key_col=N)
    → merged_rows 按需筛选或全量存入 task_store
```
