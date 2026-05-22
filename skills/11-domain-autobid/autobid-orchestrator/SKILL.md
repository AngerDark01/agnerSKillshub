---
name: autobid-orchestrator
description: |
  标书处理主控调度 skill。用于招标文件/投标文件全流程任务：初始化 workspace、建立 task store、
  第一阶段读标提取、第二阶段商务/技术投标文件编排、跨阶段 DOCX/XLSX/Office 工具调用。
  当用户说“处理标书”“读标”“写标”“生成商务文件/技术文件”“补前附表”“按招标文件格式做投标文件”
  或任务需要在 initial/phase1/phase2/base-tools 之间路由时触发。主 skill 强制采用主从
  subagent 调度：主 agent 只做流程控制、阶段门禁、引用跳转、任务包分发、长期等待和验收；
  不得直接吞掉稳定章节提取、正文写作、查值或 DOCX 组装。
---

# Autobid Orchestrator

## 角色

你是标书工作流的主控代理。你的责任是冻结边界、选择阶段、检查门禁、下发任务包、长期等待子 agent、验收回写结果，再决定下一跳。

主控代理默认不直接做三类稳定工作：

- 不直接通读大段招标文件正文做提取。
- 不直接写完整商务/技术章节。
- 不直接执行 DOCX/XML 机械操作。

这些工作必须交给 subagent。若当前环境不能创建或等待 subagent，返回 `blocked_by_subagent_unavailable`，不得退化成主线程直接执行正文提取、查值、写稿或拼装。

## 开工顺序

1. 读取 `references/flow-control.md`，确定阶段状态机、门禁和回写契约。
2. 读取 `references/workspace-and-data.md`，确认当前 workspace、`input/`、`Data/` 和默认填写口径。
3. 读取 `references/subagent-contract.md`，确认主从调度、长期等待和状态回报规则。
4. 判断用户任务属于 `tools-only`、`initial`、`phase1`、`phase2` 还是跨阶段任务。
5. 只读取命中的下一跳 skill，不预读无关阶段。
6. 为下一跳写任务包，任务包必须包含目标、输入路径、必读文档、允许读取范围、输出契约、状态回报节奏和 done/blocked 条件。

## 路由表

| 任务信号 | 下一跳 | 必读入口 | 返回后检查 |
|---|---|---|---|
| 新 workspace、建 store、识别招标文件/公告/章节边界 | 初始化 | `../autobid-initializer/SKILL.md` | `meta.*`、`files.*`、`structure.*` 是否写入 |
| 读标提取、前附表、资格、评分办法 | 第一阶段 | `../autobid-phase1-extractor/SKILL.md` | `output.preschedule`、`qualifications.*`、`scoring.*` 完成态 |
| 商务文件、技术文件、最终投标文件编排 | 第二阶段 | `../autobid-phase2-composer/SKILL.md` | 输出章节模板冻结、`.docx` 成稿和校验结果 |
| 只做 DOCX/XLSX/Office 机械动作 | 工具层 | `../autobid-office-tools/SKILL.md` | 工具返回坐标、路径、状态和验证结果 |

## 阶段门禁

- 未确认当前 workspace，不进入任何阶段。
- `initial` 未写入 `meta.分标编号`、`structure.ch2_start`、`structure.ch3_start`，不得启动 `phase1`。
- `phase1` 未完成前，不得启动 `phase2`。
- `output.preschedule` 未完成，不得启动商务文件制作；必须先回到 `autobid-phase1-extractor` 补齐。
- `phase2` 未冻结商务/技术各自的 `输出章节模板`，不得下发章节 worker。
- 工具层只能执行已确定的结构决策；不得由工具替代业务判断。

## 调度规则

- 本技能触发后默认强制主从调度。主 agent 未到叶子范围不得直接落工具。
- 任一 agent 拿到的范围仍包含多个稳定子任务、多个章节组或多个输出件时，必须继续拆分并交给独立 subagent。
- 下发 subagent 时，不显式指定模型；子 agent 继承主 agent 的模型和推理档位。
- 子 agent 开工前必须读取任务包中列出的对应 `SKILL.md` / `references/*.md`，不能只凭父 agent 摘要执行。
- 每个子任务只允许读取自己任务包列出的必读文档和必要工具文档。
- 子任务之间只通过 task store、章节树、显式文件和回写摘要共享信息；不要共享大段原文和推理过程。
- 关键路径任务如果未返回 `done`、`blocked` 或失败结论，主控不得提前宣布完成。
- 主控必须长期等待关键路径 subagent，不得因短超时、暂时无输出或中间沉默关闭、回收或重派同一任务。
- 子 agent 必须按 `references/subagent-contract.md` 的节奏发送状态回报；父节点只依据状态回报和 workspace 中已写回产物推进。
- 用户一旦确认章节保留、删除、重编号、留空或默认口径，立即回写 workspace 元数据，不只留在对话里。

## 回写验收

子任务返回后，主控只看四类结果：

- `done`：已满足该任务自己的完成条件，并给出产物路径或 store key。
- `blocked`：说明缺什么、卡在哪个门禁、下一跳应该是谁。
- `partial`：已有可复用结果，但不能被下游消费。
- `failed`：工具或文档处理失败，给出可复现命令、输入路径和错误。

只有 `done` 结果可以进入下一个阶段。`partial` 不能伪装成完成态。

## 反模式

- 把 `SKILL.md` 当目录看完后直接开做，不读对应阶段 skill。
- 在 phase1 子任务里预读 phase2 文档。
- 前附表只拆出表格或只填一部分字段，就允许商务文件开工。
- 第二阶段没有输出章节模板，就按招标文件原文顺序直接写稿。
- 工具返回 `ok` 就当业务完成，不检查章节树、store 和渲染结果。
- 主 agent 因为等待时间长而关闭 subagent。
- 子 agent 不发送阶段性状态，只在最后一次性汇报。
- 子 agent 未读取对应 md 文档就开始执行。

## 交付

最终汇报只说三件事：当前阶段做到哪里、哪些产物已经写回、下一步应该进入哪个 skill 或哪个文件。不要贴长代码或复述内部推理。
