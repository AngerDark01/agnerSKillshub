---
name: task-store
description: >
  当提取出的字段值需要在同一任务的多个步骤中复用，或后续步骤要读取前一步的提取结果时使用。
  只要执行代理得到了后面还会再次引用的关键信息，就应写入 task_store，避免重复查询同一批源文档。
---

# 任务级存储

## 概述

任务级元数据持久化工具。将提取结果以 JSON 文件存到磁盘，
同一任务的后续步骤直接读取，无需重复查询原始文档。

生命周期：一次任务（如处理一个标包）。文件存在工作目录下，
名称为 `.task_store_{task_id}.json`。

## 工具

```python
from scripts.store.task_store import (
    store_init,
    store_set,
    store_get,
    store_get_all,
    store_set_many,
)
```

---

### store_init：初始化 store

```python
r = store_init(
    work_dir = "/home/claude/task_027/",   # 工作目录
    task_id  = "282602_027_包1",           # 任务标识
)
# → {"store_path": str, "created": bool, "data": dict}
# store_path 传给其他所有工具
```

已存在则不覆盖，直接返回现有内容。

---

### store_set_many：批量写入

```python
store_set_many(store_path, {
    "meta.招标编号":    "282602",
    "meta.分标编号":    "282602-1104024-9999",
    "meta.分标名称":    "027变电站在线智能巡视系统",
    "meta.包号":        "包1",
    "delivery.交货地点": "青海省海北...",
    "price.最高限价合计": 660.97,
})
# → {"updated_keys": list, "data": dict}
```

key 支持点分隔嵌套（如 `"meta.分标编号"`）。一次调用批量写入，减少 IO。

---

### store_set：单字段写入

```python
store_set(store_path, "qualification.资质要求", "近三年具有同类产品销售业绩")
```

---

### store_get：读取单字段

```python
v = store_get(store_path, "meta.分标编号")
v = store_get(store_path, "不存在的key", default="N/A")
```

---

### store_get_all：读取全部

```python
data = store_get_all(store_path)
# → 完整字典，用于传给下一步或生成汇总
```

---

## 推荐的 key 命名规范

```
meta.*          基础标包信息（招标编号、分标编号、分标名称、包号、数量、单位）
delivery.*      交货信息（交货期、交货地点、交货方式）
price.*         价格信息（最高限价、各子项限价）
qualification.* 资质要求
scoring.*       评分信息（报价算法、权重、参数）
fubiao.*        前附表各条款提取结果
```

---

## 典型用法

```python
# 第1步（提取阶段）：提取并存储
r_init = store_init("task_027/", "282602_027_包1")
sp = r_init["store_path"]

row = extract_table_rows(SOURCE, 79, {2: "027变电站在线智能巡视系统", 3: "包1"})
store_set_many(sp, {
    "meta.分标编号":   row["rows"][0]["分标编号"],
    "meta.分标名称":   row["rows"][0]["分标名称"],
    "meta.接受投标主体": row["rows"][0]["接受的投标主体"],
})

# 第2步（写入阶段）：直接读取，不重新查询
fen_biao = store_get(sp, "meta.分标编号")
replace_text(unpacked, para_id, old, f"分标编号：{fen_biao}")
```
