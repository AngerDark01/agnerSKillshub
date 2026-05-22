# Office Tools 引用索引

## 读取决策

| 目标 | 先读 | 再读 |
|---|---|---|
| 确认章节边界、坐标、正则命中 | `docx-inspect.md` | 必要时 `docx-split.md` 或 `docx-write.md` |
| 按章节拆出 DOCX 或回拼 | `docx-split.md` | 边界不稳时回到 `docx-inspect.md` |
| 修改 DOCX 文本、段落、占位符 | `docx-write.md` | 需要坐标时先 `docx-inspect.md` |
| 读取或填写 DOCX 表格 | `docx-table.md` | 需要写 XML 时配合 `docx-write.md` |
| 复制版式、页眉页脚、section | `docx-layout.md` | 最后 `docx-pack.md` |
| 合并带媒体或关系的内容 | `docx-merge.md` | 最后 `docx-pack.md` |
| 解包、打包、校验 | `docx-pack.md` | 出错时检查 validate 输出 |
| 读取 Excel 附件 | `xlsx-table.md` | 由业务层判断列语义 |
| 持久化中间结果 | `task-store.md` | 由业务层定义 key |

## 工具调用边界

工具文档只负责“怎么做”，不负责“该不该做”。如果上层没有给出明确边界、坐标、字段或处理模式，先返回 `blocked_by_missing_decision`。

## 最小验证

- 读操作：返回可复核的结构摘要、坐标和来源范围。
- 写操作：写后再次 inspect 或读取目标节点确认。
- DOCX 产物：pack 后 validate；重要交付件尽量渲染或至少抽查首尾页结构。
- 表格提取：记录 sheet/table、列序号、匹配条件和行数。
