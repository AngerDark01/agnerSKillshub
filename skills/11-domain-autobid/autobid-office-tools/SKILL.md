---
name: autobid-office-tools
description: |
  标书 DOCX/XLSX/Office 底层工具 skill。用于机械读取、拆分、写入、合并、打包、校验 DOCX，
  读取 XLSX 附件，维护 task store。触发场景包括定位 body_idx/para_id、读表、按范围拆章、
  写入占位符、复制页眉页脚/section、合并文档、unpack/pack/validate、读取 Excel 清单。
  该 skill 只执行已确定的机械动作，不负责判断章节是否保留、字段是否满足、内容应如何成文。
---

# Autobid Office Tools

## 角色

工具层负责可靠执行 Office 文件操作。它向业务层返回坐标、结构化数据、输出路径和校验结果，不替代业务判断。

## 工具总则

- 先读后写：没有稳定 `body_idx`、`para_id`、表格序号或 sheet/列序号，不调用写入或拆分工具。
- DOCX 写入前先 unpack，写完 pack，最后 validate 或渲染检查。
- 表格读取先 inspect/list，再由业务代理判断列语义。
- 任何删除、重编号、章节保留/删除都必须由上层业务 skill 决定。
- 工具返回 `ok` 只表示机械动作完成，不表示业务任务完成。

## 脚本根目录

本 skill 自带脚本在：

```text
autobid-office-tools/scripts/
```

运行示例时，从 `autobid-office-tools/` 目录执行，或把该目录加入 `PYTHONPATH`，使 `from scripts...` 导入可用。

依赖见 `requirements.txt`。

## 引用路由

先读取 `references/index.md`，再按任务读取具体工具文档。

| 机械任务 | 读取 |
|---|---|
| DOCX 结构读取、正文坐标、正则锚点 | `references/docx-inspect.md` |
| 按 body_idx 拆分或按 manifest 拼接 | `references/docx-split.md` |
| unpack/pack | `references/docx-pack.md` |
| 占位符替换、段落填充、插入、删除、格式统一 | `references/docx-write.md` |
| DOCX 表格读取和写入 KV 表 | `references/docx-table.md` |
| section、页眉页脚、logo、页边距、页码 | `references/docx-layout.md` |
| unpacked 目录级 body 合并和媒体关系迁移 | `references/docx-merge.md` |
| XLSX 清单、附件表读取 | `references/xlsx-table.md` |
| task store 初始化、读写 key | `references/task-store.md` |

## 返回契约

工具调用完成后，返回给上层业务 skill：

- 输入路径和输出路径。
- 使用的工具 reference。
- 关键坐标：`body_idx`、`para_id`、table index、sheet name、column index。
- 结果状态：`ok`、`not_found`、`ambiguous`、`error`。
- 校验动作：再次 inspect、validate、渲染检查或人工可复核摘要。

如果工具发现业务决策缺失，返回 `blocked_by_missing_decision`，不要自行猜决策。

## 反模式

- 没有 `para_id` 就直接写 DOCX。
- 没有确认 `body_idx` 边界就拆章。
- 只看表头文本相似就认定字段语义。
- 只拼 `document.xml`，但章节含图片、页眉页脚或关系文件。
- pack 成功后不做 validate 或最小渲染/inspect 检查。
