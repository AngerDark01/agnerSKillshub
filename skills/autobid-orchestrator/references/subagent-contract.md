# Subagent 协作契约

## 强制使用条件

本技能默认强制采用主从 subagent 调度。

- 主 agent 只负责阶段冻结、任务拆分、下发、长期等待、验收和继续调度。
- 主 agent 不直接执行正文提取、查值、写稿、拼装等稳定任务。
- 若当前环境不能创建或等待 subagent，返回 `blocked_by_subagent_unavailable`，不得退化成主线程一锅端。
- 若用户明确禁止 subagent，则返回 `blocked_by_user_no_subagent`，等待用户改口或缩小到一个叶子机械动作。

## 角色

| 角色 | 职责 |
|---|---|
| 主控代理 | 阶段路由、门禁、任务包、等待、验收、最终汇报 |
| 文件级 manager | 单个商务/技术文件的章节树、局部拆分、局部验收 |
| 章节组 manager | 一个 group_node 或多个稳定 sibling 的分派与组装 |
| 叶子 worker | 单个不可再拆章节或一个极小机械动作 |

## 拆分规则

- 当前范围包含多个稳定章节、多个文件、多个处理模式时，当前代理不是叶子 worker，必须继续拆。
- 当前范围包含多个稳定子任务、多个章节组或多个输出件时，必须继续拆给独立 subagent。
- `preschedule`、`qualifications`、`scoring` 不混在一个 worker。
- 商务文件和技术文件不共用同一个 manager。
- 大章节、补充文件组、投标保证金组等默认继续拆到章节组或叶子 worker。
- 未到叶子范围的 agent 不得越权直接落工具。
- 叶子 worker 也必须先读取任务包列出的对应 md 文档，再执行。

## 等待与回收

- 长任务按分钟级等待，不按秒级短轮询判断失败。
- 主 agent 必须长期等待关键路径 worker。一次等待超时但没有最终状态时，继续等待或保持后台运行，不得关闭、回收或重派同一任务。
- 未返回 `done`、`blocked`、`failed` 或等价最终状态，不得提前关闭任何关键路径 worker。
- 只有三种情况允许回收：worker 明确返回最终状态；用户改变任务范围；父节点确认该 worker 输出已被新的任务包完全替代。
- 非关键路径也避免 busy-poll，把主控时间用于检查其他回写产物。
- 父节点只根据 worker 状态回报和 workspace 中已写回的产物推进，不根据“等待太久”推断失败。

## 状态回报节奏

子 agent 必须定期向父节点发送状态，不得长时间沉默。

必须回报的时机：

- 开工后：说明已读取哪些 md 文档、当前负责范围、计划回写位置。
- 每完成一个可验证小步骤：说明已写回产物、未决项和下一步。
- 进入长工具操作前：说明将执行什么、预计影响哪些文件。
- 长任务进行中：至少每 10-15 分钟回报一次；如果平台不支持定时消息，则在每个工具调用结束后立即回报。
- 发现阻塞时：立即返回 `blocked`，说明缺什么、卡在哪个门禁、建议下一跳。
- 结束时：返回 `done`、`blocked`、`partial` 或 `failed`。

状态回报格式：

```markdown
status: running | done | blocked | partial | failed
role: file_manager | group_manager | leaf_worker
scope: [当前负责范围]
docs_read:
  - [已读取的 SKILL.md/reference]
artifacts_written:
  - [store key 或文件路径]
pending:
  - [未决项]
next:
  - [下一步]
validation:
  - [已执行或计划执行的验证]
```

## 模型规则

默认继承当前会话模型和推理档位。下发 subagent 时不要显式指定模型名称。只有用户明确指定，或平台能力边界有必要时，才显式覆盖模型。

## Worker 最小汇报

每个 worker 回报必须包含：

- 当前阶段和负责范围。
- 已读取的对应 md 文档。
- 已写回的 store key 或文件路径。
- 未决项。
- 下一步建议。
- 实际做过的验证。
