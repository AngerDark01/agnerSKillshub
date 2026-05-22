# Phase2 引用索引

## 入口

第二阶段只在 phase1 结构化结果完成后启动。核心动作是冻结商务/技术文件的 `输出章节模板`，再按模板分派处理。

## 必读组合

| 任务 | 必读 |
|---|---|
| 任意 phase2 任务 | `phase2-common-methodology.md` |
| 商务文件 | `phase2-business-file.md` |
| 技术文件 | `phase2-tech-file.md` |
| 章节处理模式选择 | `phase2-mode-reference.md` |
| 章节模式执行 | 只读取 `modes/` 下命中的一个模式文件 |

## 模式资源路由

`phase2-mode-reference.md` 只负责选择模式。选中后只读取一个具体模式文件：

- `table_fill` -> `modes/table-fill.md`
- `template_fill` -> `modes/template-fill.md`
- `fixed_shell_image` -> `modes/fixed-shell-image.md`
- `module_docx` -> `modes/module-docx.md`
- `rule_generated` -> `modes/rule-generated.md`
- `group_assembled` -> `modes/group-assembled.md`
- `conditional_ignore` -> `modes/conditional-ignore.md`

不要在章节 worker 开工时一次加载全部 `modes/*.md`。

## 工具跳转

需要机械操作时读取 `../../autobid-office-tools/SKILL.md`：

- 定位格式和章节：`../../autobid-office-tools/references/docx-inspect.md`
- 抽章和回拼：`../../autobid-office-tools/references/docx-split.md`
- 填写和删改：`../../autobid-office-tools/references/docx-write.md`
- 表格处理：`../../autobid-office-tools/references/docx-table.md`
- 版式复制：`../../autobid-office-tools/references/docx-layout.md`
- 带图片/关系合并：`../../autobid-office-tools/references/docx-merge.md`
- 打包校验：`../../autobid-office-tools/references/docx-pack.md`

## 上游跳转

如果缺少前附表字段、资格要求或评分参数，返回 `../../autobid-phase1-extractor/SKILL.md` 补齐。不要在 phase2 worker 里自行接管 phase1 全流程。

## 文件级 manager 规则

商务文件 manager 只管商务文件，技术文件 manager 只管技术文件。两者共享结构化元数据，但不共享大段正文上下文。

文件级 manager 在继续下发章节 worker 前，必须先完成：

- 本文件源章节清单。
- 本文件输出章节模板。
- 保留/删除/留空/重编号规则。
- required 节点和 blocked 节点标注。

## 返回

完成后返回 `../../autobid-orchestrator/SKILL.md`，附最终 docx、章节树、task store、校验结果和未决材料清单。
