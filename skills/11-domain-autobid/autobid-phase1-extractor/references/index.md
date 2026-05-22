# Phase1 引用索引

## 入口

第一阶段只负责读标提取并回写结构化结果。不要读取 phase2 文档，也不要直接生成最终投标文件。

## 路由

| 任务 | 读取 | 何时跳转 |
|---|---|---|
| 前附表完整提取 | `phase1-preschedule.md` | 需要输出 `output.preschedule` 时 |
| 单字段/引用链查值 | `phase1-preschedule-field-lookup.md` | 某字段显示“见附件/见某章”或位置未知时 |
| 投标人资格要求 | `phase1-qualifications.md` | 要提取资格条件、证明材料、附件引用时 |
| 评标办法与评分细则 | `phase1-scoring.md` | 要提取报价算法、权重、商务/技术评分时 |

## 工具跳转

需要机械操作时读取 `../../autobid-office-tools/SKILL.md`：

- 结构定位：`../../autobid-office-tools/references/docx-inspect.md`
- DOCX 表格：`../../autobid-office-tools/references/docx-table.md`
- XLSX 附件：`../../autobid-office-tools/references/xlsx-table.md`
- 结果持久化：`../../autobid-office-tools/references/task-store.md`
- 拆分或导出章节：`../../autobid-office-tools/references/docx-split.md`

## 完成态

phase1 输出必须写回 store 或显式文件。以下状态不能给 phase2 消费：

- 只拆出章节，未提取字段。
- 只读了前附表主表，引用字段未解开。
- 资格/评分只做自然语言摘要，没有来源范围。
- 未决项没有 `pending_human`、`pending_asset` 或 `not_found` 标注。

## 返回

完成后返回 `../../autobid-orchestrator/SKILL.md`，由主控决定是否进入 phase2。
