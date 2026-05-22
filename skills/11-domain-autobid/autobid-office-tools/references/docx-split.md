---
name: docx-split
description: >
  当 `body_idx` 边界已经确定，需要把内容拆成独立 DOCX，或按清单重新拼回文档时使用。
  这个流程文档默认前置依赖 `docx-inspect`。它只执行已确定的边界，不负责决定该从哪里切。
---

# DOCX 拆分与拼接

## 概述

这个流程文档负责结构性操作：

- 按范围拆出独立 DOCX
- 按清单把多个部分重新拼回一个文档

它严格执行执行代理已经确定的边界，不做重新识别，也不做猜测。

## 依赖关系

要求 `docx-inspect` 已经给出稳定的 `body_idx` 范围。

## 工具

```python
from scripts.docx.split_tools import split_by_range, join_by_manifest
```

### split_by_range：按范围拆出新 DOCX

```python
result = split_by_range(
    docx_path = "full.docx",
    start     = 10,               # body_idx，含起点
    end       = 45,               # body_idx，不含终点
    out_path  = "chapter_06.docx"
)
# → {
#     "out_path": str,
#     "body_range": [int, int],
#     "para_count": int,
#     "table_count": int,
#     "has_sectPr": bool
#   }
```

### join_by_manifest：按清单重新拼接

输入支持两种模式，并且可以混用：

```python
# 模式 A：直接从源文件提取指定范围
manifest = [
    {"source": "full.docx", "start": 0,   "end": 10},
    {"source": "full.docx", "start": 45,  "end": 120},
]

# 模式 B：按顺序合并已经修改过的子文档
manifest = [
    "chapter_01.docx",
    "chapter_06_filled.docx",
    "chapter_12.docx",
]

# 两种模式可以混用
result = join_by_manifest(manifest, out_path="final.docx")
# → {
#     "out_path": str,
#     "sources_count": int,
#     "total_para_count": int,
#     "total_table_count": int
#   }
```

**样式基线**：`manifest` 的第一个条目会把自己的 `styles.xml` 和 `numbering.xml` 贡献给输出文件。应把样式最完整的文档放在第一位。

## 工作流

```
docx-inspect → 得到稳定的 body_idx 范围
    ↓
split_by_range(docx_path, start, end, out_path)
    ↓
检查：para_count 和 table_count 是否合理
      首个关键标题是否出现在预期位置
      边界是否需要清理
    ↓
[如有需要，再把拆出的章节交给写入流程]
    ↓
join_by_manifest([...], out_path)
    ↓
检查最终拼接结果
```

## 拆分规则

- 拆分不负责决定结构，只严格遵循已确认的 `body_idx` 范围。
- 如果执行代理认为重复标题属于同一个语义章节，那么拆分结果中保留重复标题是允许的。
- 细粒度拆分和粗粒度拆分遵循同一逻辑：先检查，再决定，再拆分。
- 对独立输出的章节或表格，应先拆，再做边界清理，不要为了躲避分页而预先改动源范围。
- 边界清理必须很克制：
  - 新文件开头如果继承了导致空白首页的分页符，可以删
  - 新文件末尾如果只剩一个边界性分页符且导致空白尾页，可以删
  - 内容内部本来就存在的分页符应保留
  - 对“看起来空白”的段落，必须先确认其中没有图形、嵌入对象或其他非文本内容，再决定是否删除

## 结果校验

每次拆分或拼接后，都应校验：

- `para_count` 和 `table_count` 是否合理
- 首个关键标题是否出现在预期位置
- 是否发生边界漂移；不确定时可对输出再次执行 `inspect`
- 对独立输出文件，最好渲染首页和尾页，检查是否因为继承边界分页而产生空白页

## 递归使用

先把整份 DOCX 拆成大章节，再继续检查每个章节，决定是否继续拆分或直接写入。能力不变，只是输入范围更小。

## 典型模式：拆章、填写、回拼

```python
# 1. inspect full_bid.docx，识别全部章节

# 2. 拆出各章节
for ch_num, (start, end) in chapter_ranges.items():
    split_by_range("full_bid.docx", start, end, f"chapter_{ch_num:02d}.docx")

# 3. 对需要填写的章节执行写入
#    例如 chapter_06.docx -> chapter_06_filled.docx

# 4. 重新拼接
manifest = [f"chapter_{i:02d}_filled.docx" if i in fill_targets
            else f"chapter_{i:02d}.docx"
            for i in range(1, 13)]
join_by_manifest(manifest, out_path="final_bid.docx")
```
