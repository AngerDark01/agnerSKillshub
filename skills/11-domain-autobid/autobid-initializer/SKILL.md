---
name: autobid-initializer
description: |
  标书 workspace 初始化 skill。用于新项目开工、建立或重建 task store、登记 input/files 原始文件、
  识别招标文件/招标公告/投标须知/货物清单/技术规范书路径，并写入 meta/files/structure/delivery/contact/deadline
  等上游字段。通常由 autobid-orchestrator 在 phase1 前调用；当用户说“初始化标书项目”“建立 task store”
  “先识别招标文件结构”“定位第二章/第三章/前附表边界”时触发。
---

# Autobid Initializer

## 角色

初始化只负责把当前 workspace 的文件、基础字段和章节边界写进 task store。它不做前附表完整提取，不做资格/评分细读，也不进入 phase2 写标。

## 入口门禁

开工前必须确认：

- 当前活跃 workspace 路径。
- `input/files/` 下有哪些原始文件。
- 用户给出的分标名称、分标编号、包号或可用于匹配本标包的字段。
- task id 或可生成 task store 的工作目录。

缺少 workspace 或原始文件时，返回 `blocked`，不要猜测路径。

## 必读顺序

1. 读取 `references/initial.md` 获取详细字段和提取步骤。
2. 如需 DOCX 结构、表格、XLSX 或 store 工具，读取 `../autobid-office-tools/SKILL.md`。
3. 只按需读取工具层具体 reference，例如 `../autobid-office-tools/references/docx-inspect.md`、`../autobid-office-tools/references/docx-table.md`、`../autobid-office-tools/references/xlsx-table.md`、`../autobid-office-tools/references/task-store.md`。

## 执行流程

1. 用 task-store 初始化当前项目 store。
2. 登记 `files.*`，特别区分招标文件和独立招标公告。
3. 用 DOCX 结构读取定位第二章、第三章、前附表标题等 `structure.*`。
4. 从公告或清单提取本标包基础行、交货信息、联系方式和时间节点。
5. 将所有结果写回 store，不把关键结果只留在对话中。

## Done 条件

至少满足以下条件才可返回 `done`：

- `files.*` 中已登记当前项目核心原始文件路径。
- `meta.分标编号` 或等价标包身份字段已写入。
- `structure.ch2_start` 与 `structure.ch3_start` 已写入。
- 已明确哪些字段未找到，并使用 `pending_human`、`pending_asset` 或 `not_found` 标注。

## 返回主控

完成后回到 `../autobid-orchestrator/SKILL.md`。下一跳通常是 `../autobid-phase1-extractor/SKILL.md`。

返回摘要必须包含：

- store 路径。
- 已写入的关键 key。
- 未决字段及原因。
- 是否允许 phase1 启动。
