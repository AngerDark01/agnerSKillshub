---
name: xlsx-table
description: >
  当需要读取 Excel（`.xlsx`）附件、识别列结构，并提取或汇总字段值时使用。
  永远先调用 `inspect_xlsx` 看真实列名和预览数据。常见于 DOCX 中没有找到目标值，但存在 xlsx 附件可供继续查找的场景。
---

# XLSX 表格

## 概述

读取 Excel 附件的基础设施工具。不绑定任何业务字段名。

**核心约定**：先 `inspect_xlsx` 看实际列名和序号，由执行代理判断列语义，
再用列序号提取。不猜列名，不用字符串匹配。

## 工具

```python
from scripts.xlsx.table_tools import (
    inspect_xlsx,
    extract_xlsx_rows,
    summarize_xlsx_field,
)
```

---

### inspect_xlsx：查看结构

```python
r = inspect_xlsx("file.xlsx")
sheet = r['sheets'][0]

# 关键输出：
sheet['name']              # sheet 名
sheet['headers_indexed']   # ["[0]列名A", "[1]列名B", ...]
sheet['preview']           # 前3行数据预览（字段字典列表）
```

**始终首先调用**。根据 `headers_indexed` 和 `preview` 理解列语义，
决定用哪些列序号做匹配和提取。

---

### extract_xlsx_rows：按列序号提取行

```python
r = extract_xlsx_rows(
    path       = "file.xlsx",
    sheet_name = "sheet名",        # 从 inspect_xlsx 获取
    match      = {0: "值A", 1: "值B"},  # 列序号(int): 精确匹配值
)
# →
# {
#   "status": "ok" | "not_found",
#   "count":  int,
#   "headers": list[str],
#   "rows":   list[dict],
#   "detail": str
# }
```

**match key 必须是列序号（int）**。
精确匹配（字符串相等，去首尾空白）。

---

### summarize_xlsx_field：多行字段汇总

```python
r = summarize_xlsx_field(
    path         = "file.xlsx",
    sheet_name   = "sheet名",
    match        = {0: "值A", 1: "值B"},
    target_cols  = [11, 12, 13],   # 要提取并汇总的列序号列表
    dedup        = True,            # 是否对每列值去重
)
# →
# {
#   "status": "ok" | "not_found",
#   "matched_rows": int,
#   "fields": {
#     "列名": {
#       "values":  list[str],   # 去重后的值列表
#       "summary": str          # "；"连接的汇总字符串
#     }
#   }
# }
```

适用场景：一组匹配条件对应多行（如一个标包有多条子记录），
需要把多行中的某些列汇总为一个可读字符串。

---

## 调用顺序

```
inspect_xlsx(path)
    ↓ 看 headers_indexed + preview，自主判断各列含义
    ↓ 确定匹配列序号和目标列序号

extract_xlsx_rows(path, sheet_name, match={列序号: 值})
    → 单行结果 → rows[0] 取目标列值

summarize_xlsx_field(path, sheet_name, match, target_cols=[...])
    → 多行结果 → fields["列名"]["summary"] 取汇总值
```
