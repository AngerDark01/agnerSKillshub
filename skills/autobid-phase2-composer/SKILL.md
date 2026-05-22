---
name: autobid-phase2-composer
description: |
  标书第二阶段写标编排 skill。用于基于第一阶段结构化结果和招标文件“投标文件格式”
  制作商务文件、技术文件及最终可提交 DOCX：冻结输出章节模板、选择章节处理模式、
  分派商务/技术文件 manager、组装章节、统一格式并校验。触发词包括“生成商务文件”
  “生成技术文件”“写标”“按投标文件格式编排”“组装最终投标文件”。该 skill 不替代 phase1
  上游提取；上游未完成时必须回退补齐。
---

# Autobid Phase2 Composer

## 角色

第二阶段是写标编排。核心不是直接写正文，而是先冻结商务文件和技术文件各自的 `输出章节模板`，再按模板分派章节处理、资料挂载、格式统一和最终组装。

第二阶段强制主从 subagent 调度。主代理只做目录冻结、依赖门禁、任务包分发、长期等待、验收和最终组装；不得直接吞掉商务/技术正文写作、查值、资料挂载或 DOCX 拼装。

## 入口门禁

开工前必须检查：

- `phase1` 已完成，且 `output.preschedule`、`qualifications.*`、`scoring.*` 可消费。
- 当前 workspace 的 `input/files/`、`input/upstream/`、`input/standards/`、`input/assets/` 可定位。
- 商务文件或技术文件的目标范围明确。

如果商务文件依赖的 `preschedule` 未完成，返回 `blocked_by_preschedule`，下一跳是 `../autobid-phase1-extractor/SKILL.md`。

## 必读顺序

1. 读取 `references/index.md`，确定商务/技术/通用方法论路线。
2. 读取 `references/phase2-common-methodology.md`。
3. 读取 `references/phase2-mode-reference.md` 只做模式路由；不要预读 `references/modes/*.md`。
4. 按文件类型读取 `references/phase2-business-file.md` 或 `references/phase2-tech-file.md`。
5. 章节语义和模式确定后，只读取对应的单个 `references/modes/*.md`。
6. 需要机械处理时读取 `../autobid-office-tools/SKILL.md` 和对应工具 reference。

## 流程门禁

1. 定位 `投标文件组成目录` 与 `投标文件格式`。
2. 建立 `源章节清单`。
3. 建立并冻结 `输出章节模板`。
4. 回写章节树、父子关系、保留/删除/留空/重编号决策。
5. 分派文件级 manager。
6. 文件级 manager 继续分派章节组 manager 或叶子 worker。
7. 每章按模式处理并回写 done 状态。
8. 汇总组装、统一版式、渲染或校验最终 DOCX。

第3步未完成，不得进入第5步。没有 `输出章节模板`，任何正文写作都算越权。

第5步之后必须使用 subagent。若当前环境不能创建或等待 subagent，返回 `blocked_by_subagent_unavailable`，不得由主代理串行完成整份商务文件或技术文件。

## Subagent 运行规则

- 文件级 manager 只负责单个文件的章节树、章节分发、局部验收和回写。
- 章节组 manager 拿到 `group_node` 或多个稳定 sibling 时，必须继续拆给 child worker。
- 叶子 worker 只处理一个不可再拆章节或一个极小机械动作。
- 下发 subagent 时不显式指定模型；默认继承主 agent 的模型和推理档位。
- 每个 subagent 开工前必须读取任务包列出的 `references/index.md`、通用方法论、文件类型 reference、模式索引和命中的单模式文件。
- 每个 subagent 必须定期回报状态：开工后、每个可验证小步骤后、长工具操作前、每 10-15 分钟或每个工具调用结束后、阻塞时、结束时。
- 父节点必须长期等待关键路径 subagent；未返回 `done`、`blocked`、`partial` 或 `failed` 前，不得关闭、回收或重派同一任务。

## 处理模式

章节 worker 选择处理模式前必须读取 `references/phase2-mode-reference.md`。该文件只是路由索引，不承载所有模式细节。

选中模式后，只读取一个对应文件：

- `table_fill` -> `references/modes/table-fill.md`
- `template_fill` -> `references/modes/template-fill.md`
- `fixed_shell_image` -> `references/modes/fixed-shell-image.md`
- `module_docx` -> `references/modes/module-docx.md`
- `rule_generated` -> `references/modes/rule-generated.md`
- `group_assembled` -> `references/modes/group-assembled.md`
- `conditional_ignore` -> `references/modes/conditional-ignore.md`

模式选择由业务判断决定，工具只执行已确定动作。

## 默认口径

若用户未另行推翻，对“是否满足招标文件要求 / 是否符合资格或评分条件 / 是否存在相关情形”等结论性判断，默认按 `满足`、`符合`、`无相关情形` 成文。

但签字、签章、日期、个人敏感信息、证照编号、真实参数、检测数据和缺失附件不得臆造。

## Done 条件

单个章节或章节组 `done` 至少要求：

- 对应输出节点在章节树中状态为完成。
- 内容、资料、表格或留空原因已写入目标文档或 partial 文件。
- 来源和处理模式已回写 task store 或章节摘要。
- 格式规范已读取并应用。
- 如涉及 DOCX 输出，已有工具校验或渲染检查记录。

整阶段 `done` 至少要求：

- `商务文件.docx` 或 `技术文件.docx` 输出到 workspace。
- 章节树中无未解释的 required 节点。
- 最终组装结果经过校验，未发现缺页、错序、明显版式破坏或未替换占位符。

## 返回主控

完成后回到 `../autobid-orchestrator/SKILL.md`。返回摘要必须包含最终文件路径、章节树路径、仍需人工补充的材料和校验结果。
