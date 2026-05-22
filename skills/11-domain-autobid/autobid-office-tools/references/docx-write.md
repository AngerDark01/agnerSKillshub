---
name: docx-write
description: >
  当已经确认写入目标 `para_id`，并需要把内容写入 DOCX 时使用。覆盖四类核心场景：
  占位符替换 `replace_text`、空段落填充 `fill_paragraph`、空白章节自由写入
  `insert_paragraphs`、批量格式统一 `reformat_paragraphs`。调用任何写入工具前，
  都应先通过 `docx-inspect` 获得稳定的 `para_id`。
---

# DOCX 写入

## 概述

写入操作全部在 `unpacked_dir` 上进行：先把 DOCX 解包为 XML 目录，写入工具直接修改 XML，最后再打包回 DOCX。

在写入阶段，`inspect`、`find_by_regex`、`read_body_xml` 都可以直接读取 `unpacked_dir`，因此可以交替执行“读一段、写一段、再确认一段”，不需要每次都重新打包。

写入类工具统一以 `para_id` 作为目标定位键。没有稳定 `para_id` 时，不应直接调用写入工具。

## 解包与打包

使用 `scripts/docx/pack_tools.py`：

```python
from scripts.docx.pack_tools import unpack, pack

unpack("input.docx", "unpacked/")
pack("unpacked/", "output.docx", original="input.docx")
# → {"status": "ok"|"error", "message": str}
```

`unpack` 的职责：

- 解压 DOCX
- 对 XML 做 pretty-print
- 合并相邻同格式 `<w:r>`，避免占位符被拆碎
- 处理已知的智能引号等兼容问题

`pack` 的职责：

- 校验 XML 结构
- 自动修复已知问题
- 重新打包为可交付 DOCX

建议始终传入 `original`，这样可以获得段落数变化对比。若打包失败，应先读报错信息，再修 XML，最后重新执行 `pack`。

## 工作流

```
unpack("input.docx", "unpacked/")
    ↓
inspect("unpacked/")                     查看当前状态
find_by_regex("unpacked/", pattern)      定位目标
replace_text("unpacked/", para_id, ...)  执行写入
inspect("unpacked/")                     确认效果
fill_paragraph("unpacked/", para_id, ...)
insert_paragraphs("unpacked/", ...)
reformat_paragraphs("unpacked/", ...)
    ↓
pack("unpacked/", "output.docx", original="input.docx")
```

典型迭代：

```python
# 先找还剩哪些占位符
hits = find_by_regex("unpacked/", r"\[.+?\]")

# 逐个填写，每次写完都可以再次确认
for h in hits["hits"]:
    replace_text("unpacked/", h["para_id"], h["text"], actual_value)

# 全部处理完成后再打包
pack("unpacked/", "output.docx", original="input.docx")
```

## 工具导入

```python
from scripts.docx.write_tools import (
    list_paragraphs,
    delete_body_elements,
    delete_paragraphs,
    overwrite_paragraph_text,
    replace_text,
    fill_paragraph,
    insert_paragraphs,
    reformat_paragraphs,
    read_node_xml,
)
```

补充说明：

- `delete_body_elements(unpacked_dir, body_indices)` 用于按 `body_idx` 删除整段顶层节点，常见于条件分支裁剪。
- `delete_paragraphs(unpacked_dir, para_ids)` 用于按 `para_id` 精细删除具体段落。

## replace_text：替换占位符文本

适用场景：

- `<w:t>` 中已经有明确文本
- 只想替换文字，不改变原有 `<w:rPr>` 格式

```python
result = replace_text(
    unpacked_dir = "unpacked/",
    para_id      = "7EBF197C",
    old_text     = "[招标代理机构]",
    new_text     = "国网青海省电力公司物资分公司",
)
# → {"status": "ok"|"not_found", "replaced": int, "detail": str}
```

使用规则：

- 当占位符已经出现在 `<w:t>` 中时，优先用它。
- `status == "not_found"` 时，不要立刻怀疑目标错了，先用 `read_node_xml` 看 run 是否被进一步拆分。

## fill_paragraph：填充空段落

适用场景：

- `<w:p>` 已存在
- 但其中没有任何 `<w:r>`
- 需要在原位置补一段文字

```python
result = fill_paragraph(
    unpacked_dir = "unpacked/",
    para_id      = "572CFCA4",
    text         = "QHPG-2024-001",
    inherit_from = None,   # 可指定参考段落
    font         = None,   # 可显式覆盖字体
    size         = None,   # 可显式覆盖字号，单位为 half-points
)
# → {"status": "ok"|"not_found"|"not_empty", "detail": str}
```

格式继承优先级：

1. `font` / `size` 显式传参
2. `inherit_from` 指定参考段落
3. 自动从同一 `<w:tc>` 中相邻段落推断
4. 不写 `<w:rPr>`，交给 Word 样式继承

如果返回 `not_empty`，说明段落已经有内容，应改用 `replace_text` 或 `overwrite_paragraph_text`。

## insert_paragraphs：在空白章节中自由写入

适用场景：

- 标题与下一个标题之间没有内容
- 或标题后紧跟 `sectPr`
- 需要从零生成一段或多段新内容

```python
result = insert_paragraphs(
    unpacked_dir   = "unpacked/",
    anchor_para_id = "1C4B942B",
    position       = "after",
    paragraphs = [
        {
            "text":              "本章节所提供的支撑材料，旨在佐证投标人的履约能力。",
            "font":              "宋体",
            "size":              24,
            "line_spacing":      360,
            "bold":              False,
            "align":             "left",
            "first_line_indent": True,
        },
        {
            "text": "一、合同业绩支撑材料",
            "bold": True,
            "first_line_indent": False,
        },
        {
            "text": "投标人提供近三年内已完成的同类项目合同复印件。",
        },
    ],
)
# → {"status": "ok"|"not_found", "inserted": int, "para_ids": list[str]}
```

规则：

- 同一逻辑块的多段内容，尽量一次调用完成。
- 返回结果中的 `para_ids` 是新生成段落的定位键，后续若还要继续调整格式或删除，应先记录下来。

常用字号与行距参考：

| Word 标注 | `size` | `line_spacing` |
|---|---|---|
| 小四（12pt） | 24 | — |
| 四号（14pt） | 28 | — |
| 单倍行距 | — | 240 |
| 1.5 倍行距 | — | 360 |
| 双倍行距 | — | 480 |

## reformat_paragraphs：统一段落格式

适用场景：

- 文字内容是对的
- 但字体、字号、行距、段前段后等格式不统一

```python
result = reformat_paragraphs(
    unpacked_dir  = "unpacked/",
    font          = "宋体",
    size          = 24,
    line_spacing  = 360,
    para_ids      = None,           # None 表示全篇
    skip_para_ids = [
        "4B6B8B6C",
        "2295C810",
        "42EC3B59",
    ],
    skip_empty    = True,
)
# → {"status": "ok", "total": int, "modified": int, "skipped": int}
```

规则：

- `skip_para_ids` 必须认真维护，至少排除标题、签名线、盖章线、分页控制段落。
- 这个工具会统一清理一些常见的行距和字距遗留属性。
- 如果只想处理局部段落，就显式传 `para_ids`，不要默认整篇全改。

## overwrite_paragraph_text：整段重写

适用场景：

- 一个段落的文字被拆在多个 run 中
- 或下划线占位较复杂
- 你真正想做的是“整段重写”，而不是“替换其中一个 token”

```python
result = overwrite_paragraph_text(
    unpacked_dir = "unpacked/",
    para_id      = "5A51F5D0",
    text         = "项目名称：国网青海省电力公司2026年第二次（282602）物资公开招标采购",
)
```

## delete_paragraphs：删除具体段落

适用场景：

- 某个段落在语义上已经明确应删除
- 只需要一个机械删除动作

```python
result = delete_paragraphs(
    unpacked_dir = "unpacked/",
    para_ids     = ["4B6B8B6C"],
)
```

典型用途：

- 删除 `XX格式`
- 删除 `XX模板`
- 删除 `示例`
- 删除已经确认无效的提示段

注意：这个工具不负责判断“该不该删”，只负责执行已经确认的删除动作。

## delete_body_elements：删除顶层节点

适用场景：

- 需要按 `body_idx` 删除整个顶层段落或表格
- 常见于条件分支删除、整块裁剪

```python
result = delete_body_elements(
    unpacked_dir = "unpacked/",
    body_indices = [12, 13, 14],
)
```

与 `delete_paragraphs` 的区别：

- `delete_body_elements` 面向顶层结构块
- `delete_paragraphs` 面向已知 `para_id` 的具体段落

## list_paragraphs：盘点全部段落

适用场景：

- 需要先拿到稳定的 `para_id -> 文本` 清单
- 或写入目标位于表格单元格内部，而 `inspect` 只展示了顶层段落

```python
result = list_paragraphs(
    unpacked_dir  = "unpacked/",
    include_empty = True,
)
# → {"status": "ok", "count": int, "paragraphs": [
#      {"index": 0, "para_id": "7EBF197C", "text": "项目名称：...", "is_empty": False}
#    ]}
```

## read_node_xml：调试查看原始节点

```python
result = read_node_xml("unpacked/", "7EBF197C")
# → {"status": "ok"|"not_found", "xml": str}
```

仅在这些情况下使用：

- `replace_text` 返回 `not_found`
- 需要确认真实的 run 拆分方式
- 需要在设置 `inherit_from` 前先看参考节点的细节

它是调试工具，不是常规主流程工具。

## 决策表

| 观察到的情况 | 应使用的工具 |
|---|---|
| `<w:t>` 已有占位符文本 | `replace_text` |
| `<w:p>` 存在但没有 `<w:r>` | `fill_paragraph` |
| 标题后完全空白，需要从零生成内容 | `insert_paragraphs` |
| 文字正确但格式混乱 | `reformat_paragraphs` |
| 整段被拆成多个 run，需要整段改写 | `overwrite_paragraph_text` |
| 段落已经确认应删除 | `delete_paragraphs` |
| 顶层块已经确认应删除 | `delete_body_elements` |
| 不确定真实 run 结构 | `read_node_xml` |

## 示例

### 承诺函：占位符替换 + 格式统一

```python
replace_text("unpacked/", "7EBF197C", "[招标代理机构]", "国网青海省电力公司物资分公司")
replace_text("unpacked/", "1AA343DE", "[投标人名称]", "青海华电新能源工程有限公司")
replace_text("unpacked/", "1AA343DE", "（招标编号/分标编号/包号）", "QHPG-2024-001/A-01")

reformat_paragraphs(
    "unpacked/", font="宋体", size=24, line_spacing=360,
    skip_para_ids=["4B6B8B6C", "2295C810", "294DE2F7", "42EC3B59", "1184A894"],
)
```

### 保证金表：空单元格填充

```python
fill_paragraph("unpacked/", "572CFCA4", "QHPG-2024-001")
fill_paragraph("unpacked/", "13936600", "A")
fill_paragraph("unpacked/", "4D9FDCD9", "01")
fill_paragraph("unpacked/", "5D54AE9A", "青海格尔木光伏电站设备采购")
fill_paragraph("unpacked/", "1085ECE5", "50")
fill_paragraph("unpacked/", "56B493CD", "承诺函方式")
```

### 空白章节：自由写入

```python
insert_paragraphs("unpacked/", "1C4B942B", "after", [
    {"text": "本章节所提供的支撑材料，旨在佐证投标人在商务评分各项指标中的实际履约能力。"},
    {"text": "一、合同业绩支撑材料", "bold": True, "first_line_indent": False},
    {"text": "投标人提供近三年内已完成的同类项目合同复印件，包括合同编号、签约金额及发包单位名称，并加盖公章。"},
    {"text": "二、财务状况支撑材料", "bold": True, "first_line_indent": False},
    {"text": "投标人提供经会计师事务所审计的最近两个会计年度财务报告。"},
])
```
