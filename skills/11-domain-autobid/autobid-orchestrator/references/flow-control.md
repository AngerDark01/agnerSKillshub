# 流程控制与跳转

## 状态机

```text
用户请求
  -> workspace gate
  -> subagent gate
  -> intent routing
  -> tools-only | initial | phase1 | phase2
  -> child result
  -> gate check
  -> next route | done | blocked
```

主控代理每轮只推进一个明确阶段。跨阶段任务必须显式经过门禁，不允许“顺手继续”。

## 阶段关系

```text
initial
  -> phase1-preschedule
  -> phase1-qualifications
  -> phase1-scoring
  -> phase2-business / phase2-tech
  -> office-tools
```

`office-tools` 是被调用层，不主动反向进入业务阶段。

## 门禁表

| 进入阶段 | 前置条件 | 失败返回 |
|---|---|---|
| initial | 有 workspace 和 input/files | `blocked_by_workspace` |
| 任意非叶子任务 | 能创建并等待 subagent | `blocked_by_subagent_unavailable` |
| phase1 | `initial` 完成，store 有 `meta.*`、`files.*`、`structure.*` | `blocked_by_initial` |
| phase2-business | phase1 完成，尤其 `output.preschedule` 完成 | `blocked_by_preschedule` |
| phase2-tech | phase1 基础元数据与技术相关输入可用 | `blocked_by_phase1` |
| 章节 worker | 输出章节模板已冻结 | `blocked_by_unfrozen_template` |
| office write/split | 已有稳定坐标或 manifest | `blocked_by_missing_coordinates` |

## 任务包模板

下发给阶段 skill 或 worker 时，必须包含：

```markdown
## 任务目标
[只写当前 worker 的单一目标]

## 上游产物
- store: ...
- 章节树: ...
- 输入文件: ...

## 必读文档
- [skill/reference 路径]

## 调度约束
- 必须继承父 agent 模型和推理档位，不显式指定模型。
- 开工前必须读取上述 md 文档。
- 当前范围若仍包含多个稳定子任务、章节组或输出件，必须继续拆给 child subagent。
- 未到叶子范围不得直接落工具。
- 必须按状态回报节奏向父节点汇报。

## 允许读取范围
- [workspace 子目录或文件]

## 禁止读取/禁止越权
- [不相关阶段、其他章节、Data 写入等]

## 输出契约
- store key:
- 文件路径:
- 回写摘要:

## Done 条件
- [可验证条件]

## Blocked 条件
- [缺字段/缺材料/缺门禁时返回什么]
```

## 子任务返回格式

```markdown
status: done | blocked | partial | failed
stage: initial | phase1 | phase2 | tools
outputs:
  - [路径或 store key]
pending:
  - [未决项和原因]
next:
  - [建议下一跳]
validation:
  - [实际执行过的检查]
```

## 主控验收

主控只基于已写回的文件、store、章节树和工具校验推进。对话中的“我已经理解了”不是可消费产物。

如果结果是 `partial`，可以复用其中的结构化片段，但不得进入下游门禁。

## 常见跳转

- phase2 发现前附表字段缺失：跳回 `../../autobid-phase1-extractor/SKILL.md`，只补 `preschedule` 或单字段 lookup。
- phase2 发现需要 DOCX 坐标：跳到 `../../autobid-office-tools/SKILL.md`，读取 `../../autobid-office-tools/references/docx-inspect.md`。
- 工具发现坐标不稳定：返回业务层重新确认边界，不自行扩大范围。
- 章节 worker 发现目录冲突：回写章节树并返回文件级 manager，不自行改其他章节。
