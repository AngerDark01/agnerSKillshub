---
name: phase2-mode-reference
description: >
  第二阶段模式路由索引。用于在商务文件和技术文件生成时，先按章节语义选择处理模式，
  再只读取对应的单模式 reference，避免一次加载所有模式细节。
---

# 第二阶段模式路由索引

## 使用方式

选择处理模式时只先读本文件。确定模式后，立即跳到 `modes/` 下的对应文件；不要继续加载其他模式文件。

判断三件事：

1. 这个章节的语义是什么。
2. 这个章节更适合填表、抽模板、套模块、挂图片，还是规则生成。
3. 这个章节最终是单章输出、子章节 partial，还是一个大章节的最终组装结果。

## 输出作用域

| 作用域 | 含义 |
|---|---|
| `single_chapter` | 本章直接作为最终交付中的独立章节 |
| `child_partial` | 本章只是某个大章节内部的子产物，后续还要组装 |
| `group_final` | 本章本身就是某个大章节的最终维护单位 |
| `delete_or_blank` | 删除、留空或保留说明 |

## 模式路由表

| 模式 | 适用语义 | 常见作用域 | 选中后读取 |
|---|---|---|---|
| `table_fill` | 原表结构明确，主要工作是填值 | `single_chapter` | `modes/table-fill.md` |
| `template_fill` | 招标文件已有成熟模板，主要工作是删提示、补正文 | `single_chapter` / `child_partial` | `modes/template-fill.md` |
| `fixed_shell_image` | 固定标题壳 + 说明 + 图片/扫描件 | `single_chapter` / `child_partial` | `modes/fixed-shell-image.md` |
| `module_docx` | 已有完整 DOCX 模块可复用 | `single_chapter` / `group_final` | `modes/module-docx.md` |
| `rule_generated` | 无稳定模板，需按规则组织正文 | `single_chapter` / `child_partial` | `modes/rule-generated.md` |
| `group_assembled` | 同组子章节最终要合并为一个大章节 | `group_final` | `modes/group-assembled.md` |
| `conditional_ignore` | 章节明确不适用或仅保留空位 | `delete_or_blank` | `modes/conditional-ignore.md` |

## 选择优先级

当一个章节可能落在多个模式之间，按顺序判断：

1. 是否是明确表格，是则优先 `table_fill`。
2. 是否有稳定原文模板，是则优先 `template_fill`。
3. 是否本质是图片/扫描件壳子，是则优先 `fixed_shell_image`。
4. 是否已有成熟整章模块，是则优先 `module_docx`。
5. 是否只是大章节的最终组装动作，是则优先 `group_assembled`。
6. 是否明确不适用，是则使用 `conditional_ignore`。
7. 以上都不是，再考虑 `rule_generated`。

## Manager 边界

处理模式只定义章节怎么做，不决定代理层级。

- 如果当前范围仍是多个稳定章节、一个 `group_node` 或一整个文件，当前代理仍是 manager，必须继续拆分。
- 只有当前范围已经缩到单个稳定章节或一个极小机械动作，才读取具体模式文件并直接执行。
- 选中模式后，必须把 `mode`、`scope`、`source` 和 `done` 结果写回章节树或 task store。

## 反模式

- 选模式前就加载全部 `modes/*.md`。
- 因为选中 `group_assembled` 就让当前代理串行做完整个 group。
- 把 `module_docx` 当作跳过格式检查。
- 把缺资料误判为 `conditional_ignore`。
- 把 `rule_generated` 当自由发挥写作。
