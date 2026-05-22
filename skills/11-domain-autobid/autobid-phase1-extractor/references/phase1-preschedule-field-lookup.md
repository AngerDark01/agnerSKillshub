---
name: phase1-preschedule-field-lookup
description: >
  当 `preschedule` 或其他第一阶段提取任务需要定位某个字段值，但它的真实存放位置未知
  或在不同文档中的位置不稳定时使用。只要遇到“见招标公告”“见附件”“详见附表”等
  引用语，就按这个流程文档定义的回退链路继续查找：DOCX 表格 → DOCX 全文 → XLSX
  附件 → 标注缺失。
---

# 字段查找

## 概述

当一个字段值「藏在」某个表格、正文段落或附件中时，使用此技能按优先级逐路径查找，
直到找到有效数据或确认数据缺失。

**适用于任何字段**，不绑定具体字段名。同一套路径逻辑可用于：
限价、交货期、交货地点、资质要求、评分标准参数、合同条款……

默认查找范围应是当前活跃 workspace `input/files/` 下的项目文件及其附件。

`Data/` 是共享公共数据空间，不是这类字段取值的首选来源；只有当任务目标本身就是复用企业模板或公共资料时，才转去读取 `Data/`。

## 微流程边界

- 本文件是“单字段查值”微流程，不是全文阅读许可
- 调用方每次只可带入：
  - 一个字段
  - 或一个条款
- 不得把整张前附表的全部 unresolved 项一次性带入
- 如果当前字段引用链先指向招标公告，则先只读招标公告相关范围；未证实指向附件前，不得先把全部附件扫一遍

每次查找的最小返回结构应为：

- `field`
- `value`
- `source_file`
- `source_locator`
- `confidence`
- `status(resolved / reference / missing)`

字段查找完成后，只把结构化结果回写给调用方；查找过程中读取的正文片段、附件预览、表头猜测，不应继续带入下一个字段。

## 判断「有效值」vs「引用」

找到的文本若属于以下情况，视为**引用**而非有效值，继续走下一条路径：

| 文本模式 | 含义 |
|---|---|
| 见招标公告 / 见招标公告第N条 | 值在招标公告中 |
| 见投标人须知前附表 | 值在前附表中（若当前就是前附表则为循环引用） |
| 见第N章 / 详见第N章 | 值在其他章节 |
| 见附件 / 详见附表 / 另附 | 值在附件中 |
| 空白 / — / / / 无 / 不适用 | 无数据 |

有效值：具体的文字、数字、日期、地点等非引用内容。

---

## 四条路径

### 路径 1：DOCX 表格

```python
# 1a. 列出所有表格，找可能承载目标字段的表格
from scripts.docx.table_tools import list_tables, extract_table_rows

tables = list_tables(source)
# → 由执行代理查看 headers_indexed，判断哪个表格含目标字段

# 1b. 用列序号提取
r = extract_table_rows(source, body_idx=N, match={col_a: key_val, col_b: key_val2})
# → r["status"] == "ok" 且值非引用 → 使用，停止
# → r["status"] == "not_found" 或值是引用 → 继续路径 2
```

---

### 路径 2：DOCX 全文搜索

```python
from scripts.docx.inspect_tools import find_by_regex, inspect

# 先在已知区域内搜索，例如招标公告范围
hits = find_by_regex(source, pattern=r"目标字段名关键词")
# → 找到且值非引用 → 使用，停止

# 如果找到的仍是引用，或根本没找到，再扩大到全文
hits = find_by_regex(source, pattern=r"目标字段名关键词")

# inspect 细读可疑 body_range
r = inspect(source, body_range=(s, e), include_elements=True)
# → 在 body_elements 中逐行判断
```

---

### 路径 3：XLSX 附件

```python
from scripts.xlsx.table_tools import inspect_xlsx, extract_xlsx_rows, summarize_xlsx_field

# 3a. 先看列名，再自行判断语义
info  = inspect_xlsx(xlsx_path)
sheet = info['sheets'][0]
# → 由执行代理查看 headers_indexed + preview，判断哪列含目标字段

# 3b. 单行结果
r = extract_xlsx_rows(xlsx_path, sheet['name'],
                      match={match_col: key_val})
value = r['rows'][0]['目标列名']   # 由执行代理根据列名决定取哪列

# 3c. 多行结果（一个匹配条件对应多行）
r = summarize_xlsx_field(xlsx_path, sheet['name'],
                         match={match_col: key_val},
                         target_cols=[col_a, col_b])
value = r['fields']['列名']['summary']  # 去重汇总后的字符串
```

---

### 路径 4：标注缺失

所有路径均无有效值时，在文档中写入标注而非留空：

```python
from scripts.docx.write_tools import replace_text

replace_text(unpacked_dir, para_id, current_text,
    "【⚠数据缺失】已查 DOCX 表格、全文、附件，未找到该字段。建议人工确认。")
```

---

## 流程图

```
需要字段 F 的值
        │
        ▼
路径1: DOCX 表格
  list_tables → 找含 F 的表格
  extract_table_rows → 精确行
        │ 找到有效值? ──→ 使用 ✓
        │ 否（引用/未找到）
        ▼
路径2: DOCX 全文搜索
  find_by_regex → 含 F 的段落
  inspect → 细读可疑区域
        │ 找到有效值? ──→ 使用 ✓
        │ 否
        ▼
路径3: XLSX 附件
  inspect_xlsx → 看列名
  extract_xlsx_rows / summarize_xlsx_field
        │ 找到有效值? ──→ 使用 ✓
        │ 否
        ▼
路径4: 标注缺失 【⚠数据缺失】
```

---

## 关键原则

**不要硬编码字段名映射。** 每次都先看实际列名（`headers_indexed`），
由执行代理判断哪列对应目标语义。同一字段在不同文件里可能叫：
「交货期」/「供货期」/「首批交货日期+末批交货日期」，
「交货地点」/「交货地址」/「收货地点」。
工具提供结构，执行代理负责判断。

**路径不跳跃。** 找到引用（「见招标公告」）时，要去对应位置查，
不要直接跳到附件。引用链可能是：前附表 → 招标公告 → 概况表。

**多行时汇总。** 同一个匹配条件可能对应多行（如一个标包发往多个地点）。
用 `summarize_xlsx_field` 去重汇总，不要只取第一行。
