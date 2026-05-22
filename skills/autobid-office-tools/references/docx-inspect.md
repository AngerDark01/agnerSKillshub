---
name: docx-inspect
description: >
  当你在拆分、写入或提取内容之前，需要先理解 DOCX 结构时使用。适用于定位
  章节边界、占位符、空白单元格、空白章节等所有前置读取场景。通常应最先执行，
  因为 `docx-split` 与 `docx-write` 都依赖这里产出的坐标信息。
---

# DOCX 结构读取

## 概述

这个流程文档提供一种渐进式 DOCX 阅读策略。

文档往往很大，不适合一次读完。推荐顺序是：

先看粗粒度骨架 → 判断哪里已经明确、哪里仍有歧义 → 缩小到可疑范围细读 → 为下一步产出稳定坐标。

这里的工具直接读取 `.docx` 或已解包目录，不要求先 unpack。读取操作是无副作用的，可反复调用。

## 工具

```python
from scripts.docx.inspect_tools import (
    inspect,
    read_body_xml,
    find_by_regex,
    list_builtin_patterns,
)
```

`source` 参数在所有工具中统一接受两种形态：
- `.docx` 文件路径：适合在 unpack 前阅读
- `unpacked_dir` 目录路径：适合在 unpack 后确认，**读到的是写入后的最新状态**

写入阶段可以继续调用 inspect / find_by_regex 确认效果或定位下一个目标，无需重新 pack。

### inspect：渐进式结构读取

```python
# 第1轮：粗读，先看整份文档骨架
result = inspect("file.docx")          # 读 .docx
result = inspect("unpacked/")          # 读 unpacked_dir（写入后确认）

# 第2轮：缩小到某个 body_idx 范围细读
result = inspect("file.docx", body_range=(40, 80))

# 第3轮：必要时暴露范围内的全部元素
result = inspect("file.docx", body_range=(40, 80), include_elements=True)
```

**重点字段：**

| 字段 | 含义 | 何时使用 |
|---|---|---|
| `skeleton` | 长度较短的段落骨架，常见于标题、标签 | 一般先看这里，成本最低 |
| `candidate_nodes` | 自动识别出的章节或块起点 | 当骨架已能显示明显结构时使用 |
| `content_previews` | 每个候选块的抽样内容 | 用于确认候选边界是否正确 |
| `signals` | 结构信号，如大纲级别、标题正则、`sectPr` | 自动识别不稳定时参考 |
| `body_elements` | 指定范围内的完整元素列表 | 前两轮仍无法判断时再使用 |
| `file_info` | 段落数、表格数、来源类型等 | 每次都应先看 |

每个段落元素都带有 `para_id`，后续可以直接传给写入工具。

### read_body_xml：读取原始 XML

```python
xml_str = read_body_xml("file.docx", start=42, end=45)
xml_str = read_body_xml("unpacked/", start=42, end=45)  # 写入后看最新 XML
```

### find_by_regex：定位锚点

```python
hits = find_by_regex("file.docx",  pattern=r"\[.+?\]")  # unpack 前
hits = find_by_regex("unpacked/",  pattern=r"\[.+?\]")  # unpack 后继续定位
hits = find_by_regex("file.docx",  use_builtin="zh_chapter")
hits = find_by_regex("file.docx",  pattern=r"\[.+?\]", body_range=(10, 60))

patterns = list_builtin_patterns()
# → {"zh_chapter", "zh_appendix", "zh_section", "en_chapter",
#    "en_section", "en_appendix", "numbered_bold"}
```

返回结构：

```python
{
  "pattern": str,
  "hits": [
    {"body_idx": int, "para_id": str | None, "text": str, "style": str | None}
  ],
  "count": int
}
```

`para_id` 是读取层与写入层之间的桥接键。从 `find_by_regex` 或 `body_elements` 拿到后，可直接传给写入工具。

## 坐标体系

```
body_idx  →  整数，表示 body 直属子元素序号（段落和表格共用）
             用于：块导航、拆分范围、body_range 过滤

para_id   →  8位十六进制，来源于 w14:paraId，文档内唯一
             用于：写入工具的目标定位
             来源：find_by_regex 的命中结果或 body_elements
```

## 读取策略

三轮读取是一个漏斗。只要信息已经足够支撑下一步动作，就应立即停止，不要过读。

```
第1轮：skeleton + candidate_nodes
    成本低，返回短骨架和自动识别块。
    如果章节结构已清晰、边界已明确，可以停在这里。

第2轮：缩小 body_range
    成本中等，聚焦一个块。
    用于候选边界有歧义，或写入前需要进一步定位占位符。

第3轮：include_elements 或 read_body_xml
    成本更高，直接暴露原始元素细节。
    只有前两轮仍不能解决歧义时才使用。
```

## 工作流

```
inspect(docx_path)
  → 先看 skeleton，识别可疑范围
  → 对每个可疑范围继续：
      inspect(docx_path, body_range=(s, e))
        → 仍不清楚时再读 read_body_xml(docx_path, s, e)
  → 需要特定锚点时，调用 find_by_regex(docx_path, pattern)
  → 在拆出独立章节或表格前，检查起止边界 XML
    是否带有页分页、图形对象、书签或其他非文本内容
  → 为 docx-split 记录 body_idx 范围
  → 为 docx-write 记录 para_id
```

## 检查规则

- 永远先从第1轮开始，不要一上来就开 `include_elements`。
- 重复标题必须保留在视野里，目录标题、正文标题、模板分组标题可能同时存在，具体哪个有效由执行代理判断。
- `candidate_nodes` 只是建议，不是真实边界。
- 如果一个章节仍然太大，就继续在它的 `body_range` 内递归调用 `inspect`。
- 这个流程文档只负责读取，不负责解包。
- 如果边界附近出现“看起来空白”的段落，应读原始 XML 再判断，因为空白段落里可能挂着分页、图片、书签或内嵌对象。

## 期望输出

完成本流程文档后，执行代理应能明确给出：

- 主要块边界对应的 `body_idx` 范围，并说明哪些已经确定、哪些仍有歧义
- 后续写入目标对应的 `para_id`
- 哪些范围适合拆分，哪些范围适合直接写入

## 递归使用

先检查整份 DOCX → 拆出章节 → 再检查每个章节 → 继续拆分或写入。能力不变，只是每次处理的 `body_range` 更小。
