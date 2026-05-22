---
name: autobid-phase1-extractor
description: |
  标书第一阶段读标提取 skill。用于从招标文件中提取第二阶段会复用的结构化结果：
  投标人须知前附表、投标人资格要求、评标办法、报价算法、商务/技术评分细则等。
  当用户说“读标”“提取前附表”“补 preschedule”“提取资格要求”“提取评分办法”
  或 phase2 因上游字段缺失需要回退补齐时触发。该 skill 只做 phase1 提取与回写，
  不预读 phase2 写标文档，不直接生成最终商务/技术投标文件。
---

# Autobid Phase1 Extractor

## 角色

第一阶段负责把后续反复使用的信息抽干净、写清楚、存下来。输出必须是 task store 或显式文件，不能只是自然语言摘要。

## 入口门禁

开工前检查：

- `initial` 已经完成，且 store 中存在 `meta.*`、`files.*`、`structure.*`。
- 当前任务要做全量 phase1，还是只补 `preschedule`、`qualifications` 或 `scoring`。
- 用户是否给了分标名称、包号、当前 workspace 和 store 路径。

如果 `initial` 未完成，返回 `blocked_by_initial` 给 `../autobid-orchestrator/SKILL.md`。

## 必读顺序

1. 先读取 `references/index.md`，确定子任务和引用跳转。
2. 只读取命中的子任务 reference。
3. 需要 DOCX/XLSX/store 工具时，再读取 `../autobid-office-tools/SKILL.md` 和对应工具 reference。
4. 不读取 `../autobid-phase2-composer/SKILL.md`，除非主控明确要求检查下游依赖名称。

## 子任务路由

| 子任务 | 读取 | 完成态 |
|---|---|---|
| 前附表 `preschedule` | `references/phase1-preschedule.md` | `output.preschedule` 达到完整可消费状态 |
| 字段回退查找 | `references/phase1-preschedule-field-lookup.md` | 单字段有值、引用解开或明确 pending |
| 投标人资格 | `references/phase1-qualifications.md` | `qualifications.*` 和独立提取文件完成 |
| 评标办法 | `references/phase1-scoring.md` | `scoring.*`、算法、权重、评分细则完成 |

## 调度规则

- 第一阶段默认强制主从调度。phase1 manager 只拆分、等待、验收和回写检查，不直接完成三个大任务。
- `preschedule`、`qualifications`、`scoring` 默认独立执行，不让一个 worker 混做多个大任务。
- 全量 phase1 必须至少拆成 `preschedule`、`qualifications`、`scoring` 三类独立 subagent；若只补单字段，也必须按字段 lookup 的叶子任务包执行。
- 任一 worker 发现当前范围仍包含多个字段组、章节组或输出件时，必须继续拆分，不得直接一锅端。
- 下发 subagent 时不显式指定模型；子 agent 继承当前会话模型和推理档位。
- 子 agent 开工前必须读取 `references/index.md` 和自己负责的子任务 reference。
- 子 agent 必须定期回报 `running/done/blocked/partial/failed` 状态，长期任务至少每 10-15 分钟或每个工具调用结束后回报一次。
- 子任务只能读取自己的 reference、必要工具文档和任务包允许的原始文件。
- 字段查找是微流程：一次只查一个字段，不把整张前附表的 unresolved 项全部带进去。
- 遇到“见附件/见附表/详见某章”，必须解引用；不能把引用文本当最终值。
- 任何结果只有到达 `done` 才允许 phase2 消费；`partial` 不能下放给第二阶段。
- 父节点必须长期等待关键路径 worker；未返回最终状态不得关闭或回收。

## Done 条件

全量 phase1 的 `done` 至少要求：

- `output.preschedule` 完整，且边界仅限前附表标题和主表；附件/限价表/货物清单只作为来源。
- `qualifications.*` 有资格要求、引用内容和来源范围。
- `scoring.*` 有评标办法、报价算法、权重参数和商务/技术评分细则。
- 不确定项已标为 `pending_human`、`pending_asset`、`not_found` 或 `【待确认】`。
- 所有下游要消费的结果已写入 store 或显式文件。

## 返回主控

完成后回到 `../autobid-orchestrator/SKILL.md`。若用户目标是写标，下一跳通常是 `../autobid-phase2-composer/SKILL.md`。

返回摘要必须包含：

- 哪些子任务 `done`。
- 哪些字段仍 `pending`。
- phase2-business 是否允许启动。
- store key 或输出文件路径。
