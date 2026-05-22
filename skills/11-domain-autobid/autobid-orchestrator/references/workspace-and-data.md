# Workspace 与 Data 规则

## 当前项目 workspace

当前项目输入优先来自活跃 workspace 的 `input/` 目录。

```text
input/files/      原始招标文件、招标公告、投标须知、货物清单、技术规范书等
input/upstream/   上游阶段产物
input/standards/  当前项目格式规范、标准封面、页眉页脚、logo、标准件
input/assets/     当前项目专属素材
meta/             阶段元数据、章节树、task store、经验记录
output/           最终或阶段输出
```

如用户未指定 workspace，先定位或询问，不能默认写到 `Data/`。

## 公共 Data 空间

`/home/aseit/桌面/bid_doc/Data` 是跨项目共用空间。

```text
Data/modules/   可复用模板模块
Data/material/  企业公共资料、证照、介绍、扫描件、说明书等
```

只读原则：

- phase1 默认不依赖 `Data/` 做读标判断。
- phase2 可读取 `Data/modules/` 和 `Data/material/` 作为模板或资料来源。
- 项目中间产物、章节树、task store、最终文件写回当前 workspace，不写回 `Data/`。

## 默认填写口径

若用户未另行推翻，phase2 对以下结论性判断默认按正向口径成文：

- 是否满足招标文件要求：`满足`
- 是否符合资格或评分条件：`符合`
- 是否存在相关情形：`无相关情形`

仍禁止臆造：

- 签字、签章、日期。
- 个人敏感信息。
- 真实证照编号。
- 硬参数、检测数据。
- 不存在的附件材料或扫描件。

## 写回规则

任何已确认结论都必须写回 workspace：

- phase1 提取结果写回 task store 或显式文件。
- phase2 目录、保留/删除、重编号、处理模式写回章节树。
- 用户确认过的约束写入 `关键约束与经验` 或等价元数据。

不要把关键决策只留在聊天上下文。
