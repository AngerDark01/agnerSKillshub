---
name: initial
description: >
  初始化阶段，必须最先执行。负责初始化 task_store，写入 metadata、文件路径与
  关键章节边界，并为 `phase1-preschedule`、`phase1-qualifications` 与
  `phase1-scoring` 提供统一上游数据。后续阶段不再重复读取同一批源文档，而是统一
  从 store 中取值。
---

# 初始化阶段

## 职责

读文档、提取数据、写入 store。后续第一阶段与第二阶段子任务优先只读 store，不重复查文档。

## Workspace 输入

初始化阶段默认从当前活跃 workspace 的 `input/files/` 读取原始文件。

当前采用的新格式可参考：

- `/home/aseit/桌面/bid_doc/workspace_v4/input`

在这一阶段，优先识别并写入 `files.*` 的通常包括：

- 招标文件
- 招标公告
- 投标须知
- 货物清单
- 技术规范书

如果招标公告是独立文档，应把它和招标文件并列记录到 `files.*`，不要只假设招标公告一定内嵌在招标文件里。

`/home/aseit/桌面/bid_doc/Data` 是共享公共数据空间，不是初始化阶段的主输入来源；初始化阶段的主要任务是先把当前项目文件路径和基础结构识别清楚。

## 执行顺序

**1. 初始化 store**
用 `store_init(work_dir, task_id)` 建立 store，写入元数据和文件路径。

**2. 定位文档结构**
`inspect(招标文件)` 读 skeleton，找各章 body_idx 边界：
- `structure.ch2_start / ch2_end`（第二章）
- `structure.ch3_start / ch3_end`（第三章）
- `structure.fubiao_title_idx`（前附表标题位置）：用 `find_by_regex(pattern=r"投标人须知前附表$")` 定位

**3. 提取本标包基础行**
从招标公告概况表：`list_tables` → 找含「分标名称/分包」列的表 → `extract_table_rows` 按分标名称+包号精确匹配一行。
写入：`meta.序号 / 数量 / 单位 / 接受投标主体`

**4. 提取交货信息（如有货物清单 xlsx）**
`inspect_xlsx` 看列名 → 自主判断匹配列和目标列 → `summarize_xlsx_field` 提取。
写入：`delivery.首批交货日期 / 最后一批交货日期 / 交货地点 / 交货方式`

**5. 提取联系方式和时间节点**
从招标公告正文：`find_by_regex` 找联系人/电话/邮件/截止时间段落。
写入：`contact.招标人名称 / 代理机构名称 / 联系人 / 电话 / 邮件 / 地址`
写入：`deadline.招标文件获取截止 / 投标截止时间 / 开标时间`

## 完成标志

store 中以下 key 均已写入后，第一阶段可以启动：
`meta.分标编号` / `structure.ch2_start` / `structure.ch3_start`

## store key 规范

```
meta.*        分标编号/名称/包号/数量/单位/接受投标主体
files.*       当前 workspace 下各原始文件的绝对路径
structure.*   章节边界 body_idx
delivery.*    交货信息（来自 xlsx）
contact.*     招标人/代理机构联系方式
deadline.*    各时间节点
```
