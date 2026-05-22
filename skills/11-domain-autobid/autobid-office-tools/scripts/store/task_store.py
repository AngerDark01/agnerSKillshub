"""
scripts/store/task_store.py
===========================
任务级 metadata 存取。将提取结果以 JSON 文件持久化到磁盘，
供同一任务的不同步骤复用，避免重复查询。

生命周期：绑定到一次处理任务（通常是一个标包），存储在工作目录内。
格式：JSON 文件，key-value 结构，支持嵌套。

工具一：store_set(store_path, key, value)
    写入或更新一个字段。

工具二：store_get(store_path, key, default)
    读取一个字段，key 不存在时返回 default。

工具三：store_get_all(store_path)
    读取全部内容，返回完整字典。

工具四：store_init(work_dir, task_id)
    在工作目录下初始化一个 store 文件，返回 store_path。
    如果已存在则直接返回路径（不覆盖）。

设计原则：
    - 纯文件操作，无数据库依赖
    - key 支持点分隔路径（如 "meta.分标编号"）实现嵌套访问
    - 所有操作都返回完整的当前 store 内容，方便 agent 确认状态
"""

import json
from pathlib import Path
from datetime import datetime


def _load(store_path: str) -> dict:
    p = Path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(store_path: str, data: dict) -> None:
    p = Path(store_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_nested(data: dict, key: str):
    """支持点分隔的嵌套 key，如 "meta.分标编号" """
    parts = key.split(".")
    cur = data
    for part in parts:
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _set_nested(data: dict, key: str, value) -> dict:
    parts = key.split(".")
    cur = data
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value
    return data


# ══════════════════════════════════════════════════════════════
# 工具一：store_init
# ══════════════════════════════════════════════════════════════

def store_init(work_dir: str, task_id: str) -> dict:
    """
    在工作目录下初始化一个 store 文件。
    已存在则不覆盖，直接返回现有内容。

    参数：
        work_dir: 工作目录（如 unpacked/ 的上级，或任意任务目录）
        task_id:  任务标识，如 "282602_027_包1"

    返回：
        {
          "store_path": str,     # store 文件路径，传给其他工具
          "created":    bool,    # True=新建，False=已存在
          "data":       dict     # 当前内容
        }
    """
    store_path = str(Path(work_dir) / f".task_store_{task_id}.json")
    p = Path(store_path)

    if p.exists():
        data = _load(store_path)
        return {"store_path": store_path, "created": False, "data": data}

    data = {
        "_meta": {
            "task_id":    task_id,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    }
    _save(store_path, data)
    return {"store_path": store_path, "created": True, "data": data}


# ══════════════════════════════════════════════════════════════
# 工具二：store_set
# ══════════════════════════════════════════════════════════════

def store_set(store_path: str, key: str, value) -> dict:
    """
    写入或更新一个字段。

    参数：
        store_path: store 文件路径（从 store_init 获取）
        key:        字段名，支持点分隔嵌套，如 "meta.分标编号"
        value:      任意可 JSON 序列化的值（str/int/float/dict/list）

    返回：
        {"store_path": str, "key": str, "value": value, "data": dict}
    """
    data = _load(store_path)
    _set_nested(data, key, value)
    _save(store_path, data)
    return {"store_path": store_path, "key": key, "value": value, "data": data}


# ══════════════════════════════════════════════════════════════
# 工具三：store_get
# ══════════════════════════════════════════════════════════════

def store_get(store_path: str, key: str, default=None):
    """
    读取一个字段。key 不存在时返回 default。

    参数：
        store_path: store 文件路径
        key:        字段名，支持点分隔嵌套
        default:    key 不存在时的返回值

    返回：
        字段的值（任意类型），或 default
    """
    data = _load(store_path)
    result = _get_nested(data, key)
    return result if result is not None else default


# ══════════════════════════════════════════════════════════════
# 工具四：store_get_all
# ══════════════════════════════════════════════════════════════

def store_get_all(store_path: str) -> dict:
    """
    读取 store 的全部内容。

    返回：
        完整的 store 字典
    """
    return _load(store_path)


# ══════════════════════════════════════════════════════════════
# 工具五：store_set_many
# ══════════════════════════════════════════════════════════════

def store_set_many(store_path: str, updates: dict) -> dict:
    """
    批量写入多个字段，一次性保存，减少 IO 次数。

    参数：
        store_path: store 文件路径
        updates:    {key: value} 字典，key 支持点分隔嵌套

    返回：
        {"store_path": str, "updated_keys": list, "data": dict}
    """
    data = _load(store_path)
    for key, value in updates.items():
        _set_nested(data, key, value)
    _save(store_path, data)
    return {
        "store_path":   store_path,
        "updated_keys": list(updates.keys()),
        "data":         data,
    }
