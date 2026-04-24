# CODEBASE — [项目名称]

> **最后同步：** YYYY-MM-DD HH:MM
> **构建模式：** SCAN（首次）/ SYNC（增量）
> **根目录：** /path/to/project

---

## 目录

1. [项目概览](#1-项目概览)
2. [目录结构图](#2-目录结构图)
3. [架构全景](#3-架构全景)
4. [模块与文件详解](#4-模块与文件详解)
5. [函数索引、调用关系与算法实现](#5-函数索引调用关系与算法实现)
6. [完整数据流链路](#6-完整数据流链路)
7. [外部集成详情](#7-外部集成详情)
8. [数据模型与契约](#8-数据模型与契约)
9. [风险与隐患登记册](#9-风险与隐患登记册)

---

## 1. 项目概览

| 字段 | 内容 |
|------|------|
| **核心目的** | 一句话：这个系统做什么、解决什么问题 |
| **架构风格** | 分层单体 / 微服务 / 事件驱动 / ... |
| **主要语言** | Python 3.11 / TypeScript 5.x / ... |
| **核心框架** | FastAPI 0.110 + LangGraph 0.1 + React 18 + ... |
| **运行时进程** | 进程1（端口）/ 进程2（端口）/ ... |
| **持久化** | PostgreSQL 15（主库）/ ES 8（检索）/ Redis 7（缓存） |
| **部署方式** | Docker Compose / K8s / 裸机 |
| **关键约束** | 响应 <200ms / LLM 超时 30s / pipeline 并发上限 N |
| **特殊说明** | 任何不显而易见的全局约定（线程模型、Session 管理策略等） |

---

## 2. 目录结构图

> 要求：实际目录树，每个**目录**和**文件**都有一行职责注释。不列 node_modules/__pycache__/.git 等。

```
project-root/
├── main.py                        # FastAPI 应用入口；注册所有路由、CORS、生命周期钩子
├── src/
│   ├── settings.py                # 环境变量加载（pydantic BaseSettings）；所有配置的单一来源
│   ├── config.py                  # 派生配置（由 settings 计算出的运行时常量）
│   ├── database.py                # SQLAlchemy engine + SessionLocal + get_db 依赖项
│   ├── api/
│   │   ├── tasks_api.py           # /api/tasks 路由组：任务改名、删除、状态查询
│   │   └── projects_api.py        # /api/projects 路由组：项目树 CRUD、任务归属管理
│   ├── models/
│   │   ├── database_models.py     # SQLAlchemy ORM 模型：Task / WorkflowVersion / AgentLog / ...
│   │   └── project_models.py      # Project / ProjectTask ORM 模型
│   ├── core/
│   │   ├── state.py               # PipelineState TypedDict：pipeline 节点间共享的所有字段
│   │   ├── pipeline_config.py     # 主 pipeline 图定义：12 个节点的连接顺序
│   │   ├── sop_extraction_pipeline.py  # 构建并 invoke 主 pipeline 的入口函数
│   │   ├── regenerate_pipeline_config.py  # 重生成 pipeline 图（从 sop_split 起的子图）
│   │   ├── regenerate_pipeline.py  # 重生成 pipeline 的 invoke 入口
│   │   ├── chat.py                # LLM 客户端封装（OpenAI 兼容；含重试、trust_env 配置）
│   │   ├── utils.py               # 通用工具函数（字符串处理、JSON 清洗等）
│   │   ├── log_decorator.py       # @log_node 装饰器：节点执行写 AgentLog + AgentTraceDetail
│   │   └── nodes/
│   │       ├── generate_task_name_node.py     # 节点1：LLM 生成任务名
│   │       ├── task_creation_node.py          # 节点2：写 Task 记录（占位）
│   │       ├── sop_split_node.py              # 节点3：LLM 将 SOP 拆分为步骤列表
│   │       ├── knowledge_extraction_node.py   # 节点4：ES 检索相关知识条目
│   │       ├── threshold_extraction_node.py   # 节点5：ES 检索阈值条目
│   │       ├── load_prompts_node.py           # 节点6：从文件加载 prompt 模板
│   │       ├── dsl_generation_node.py         # 节点7：LLM 生成 DSL 文本
│   │       ├── parse_dsl_to_json_node.py      # 节点8：DSL 文本 → 结构化 JSON（含解析算法）
│   │       ├── match_thresholds_node.py       # 节点9：LLM 匹配阈值并回填 JSON（含合并算法）
│   │       ├── save_json_result_node.py       # 节点10：JSON 写文件系统
│   │       ├── import_json_to_db_node.py      # 节点11：JSON → DB 版本记录（含版本递增逻辑）
│   │       ├── format_output_node.py          # 节点12：格式化最终输出
│   │       ├── evaluation_node.py             # 可选节点：DSL 质量评估
│   │       ├── cot_formatting_node.py         # COT 格式化节点
│   │       ├── analysis_node.py               # 分析节点（用于 regenerate 子图）
│   │       └── final_optimized_entity_extraction_node.py  # 实体抽取（优化版）
│   ├── tools/
│   │   └── parser_tool.py         # DSLParser 类：DSL 文本 → 层级 JSON（核心解析算法）
│   └── services/
│       └── relationship_service.py  # infer_parent_child_relationships：parent_id 推理算法
├── app/                           # React + TypeScript 前端
│   ├── index.tsx                  # 根组件：路由、视图切换、全局状态、工作流图处理逻辑
│   ├── api.ts                     # 所有后端 HTTP 请求封装（Axios）
│   ├── types.ts                   # 前后端共享类型定义
│   ├── DocumentSidebar.tsx        # SOP原文 / SOP条目 / 知识库 三 Tab 联动侧边栏
│   ├── SimplifiedAgentTrace.tsx   # COT 可视化（双重回退策略）
│   ├── mock_data.ts               # 前端 mock 数据（开发调试用）
│   └── src/
│       └── components/
│           ├── ProjectSidebar.tsx  # 项目树 CRUD + 上下文菜单 + 任务归属拖拽
│           ├── TaskNameEditor.tsx  # 任务名内联编辑（编辑→保存→回滚流程）
│           └── GraphDiff/         # 图谱差异对比子系统（独立 Feature 模块）
│               ├── index.ts
│               ├── useGraphDiff.ts       # 并行加载 compare + 工作流版本的自定义 Hook
│               ├── useNodeFocus.ts       # ReactFlow 画布节点聚焦逻辑
│               ├── GraphDiffContainer.tsx  # 差异总控：筛选状态、选中联动
│               ├── GraphDiffCanvas.tsx    # 版本B画布：差异高亮 + 自动聚焦
│               ├── GraphDiffToolbar.tsx   # 工具栏：筛选按钮 + 统计数字
│               ├── DiffMetricsCard.tsx    # 差异统计卡片
│               ├── DiffListPanel.tsx      # 差异列表：nodeDiffs 分组 + 联动画布
│               ├── DiffListGroup.tsx      # 差异分组（added/removed/modified）
│               ├── DiffListItem.tsx       # 单条差异项展示
│               ├── DiffNodeWrapper.tsx    # ReactFlow 自定义节点（差异高亮）
│               └── DiffNodeBadge.tsx      # 节点左上角差异类型徽标
├── start.sh                       # 后端启动脚本（uvicorn）
├── start_frontend.sh              # 前端启动脚本（vite dev）
└── README.md                      # 项目说明文档
```

---

## 3. 架构全景

### 3.1 系统上下文（C4 Level 1）

```
┌─────────────┐   HTTP/REST    ┌─────────────────────────────────────────┐
│  工程师用户  │ ─────────────▶ │          SOP 工作流自动生成系统            │
└─────────────┘                │                                         │
                               │  解决问题：将非结构化 SOP 文档自动转换为    │
                               │  结构化工作流图，支持人工审核与版本管理      │
                               └──────────────────┬──────────────────────┘
                                                  │
                    ┌─────────────────────────────┼──────────────────┐
                    │                             │                  │
              ┌─────▼────┐                ┌───────▼──┐        ┌──────▼─────┐
              │PostgreSQL│                │ ES 8     │        │ LLM Service│
              │（主数据库）│                │（知识检索）│        │（Qwen/GPT）│
              └──────────┘                └──────────┘        └────────────┘
```

### 3.2 容器视图（C4 Level 2）

```
┌─────────────────────────────────────────────────────────────────────┐
│                           系统边界                                    │
│                                                                     │
│  ┌──────────────────────┐   REST / JSON   ┌────────────────────┐   │
│  │   React SPA          │ ─────────────▶  │  FastAPI Server    │   │
│  │   (Vite + TypeScript)│ ◀─────────────  │  (Python 3.x)     │   │
│  │                      │   轮询/响应      │                    │   │
│  │  端口: 5173           │                │  端口: 8000         │   │
│  │                      │                │                    │   │
│  │  主要职责:            │                │  主要职责:           │   │
│  │  - 任务提交与状态展示  │                │  - HTTP 路由处理     │   │
│  │  - 工作流图可视化      │                │  - Pipeline 编排    │   │
│  │  - 版本对比 (GraphDiff)│               │  - 数据持久化       │   │
│  │  - COT 轨迹查看       │                │  - LLM 调用代理     │   │
│  └──────────────────────┘                └──────────┬─────────┘   │
│                                                     │              │
│         ┌───────────────────────────────────────────┤              │
│         │                    │                      │              │
│  ┌──────▼────────┐   ┌───────▼──────┐    ┌──────────▼───────┐    │
│  │  PostgreSQL   │   │ Elasticsearch│    │   LLM Service     │    │
│  │  port: 5432   │   │  port: 9200  │    │   port: (env)     │    │
│  │               │   │              │    │                   │    │
│  │  存储:        │   │  索引:        │    │  模型:            │    │
│  │  Task/Version/│   │  知识库条目   │    │  DSL生成/任务命名 │    │
│  │  AgentLog/... │   │  阈值条目     │    │  SOP拆分/阈值匹配 │    │
│  └───────────────┘   └──────────────┘    └───────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 组件视图（C4 Level 3）——后端

```
FastAPI Server 内部：

  ┌────────────────────────────────────────────────────────────────────┐
  │                        main.py (路由层)                             │
  │  POST /tasks  GET /tasks/{id}  PUT /workflow  GET /compare  ...   │
  └──────────┬─────────────────────────────────────────────────────────┘
             │ 触发 pipeline（后台线程）
  ┌──────────▼─────────────────────────────────────────────────────────┐
  │                   Pipeline 编排层 (src/core/)                       │
  │                                                                    │
  │  pipeline_config.py ──► 定义12节点 LangGraph StateGraph            │
  │         │                                                          │
  │         ▼                                                          │
  │  节点执行链（src/core/nodes/）：                                     │
  │  [generate_task_name] → [task_creation] → [sop_split]             │
  │       → [knowledge_extraction] → [threshold_extraction]            │
  │       → [load_prompts] → [dsl_generation]                         │
  │       → [parse_dsl_to_json] → [match_thresholds]                  │
  │       → [save_json_result] → [import_json_to_db]                  │
  │       → [format_output]                                            │
  │                                                                    │
  │  log_decorator.py ──► @log_node 包裹每个节点，写 AgentLog          │
  └──────────┬─────────────────────────────────────────────────────────┘
             │
  ┌──────────▼─────────────────────────────────────────────────────────┐
  │                      工具/服务层                                     │
  │  parser_tool.py: DSLParser（文本→JSON 解析算法）                    │
  │  relationship_service.py: parent_id 推理算法                        │
  │  chat.py: LLM 客户端（OpenAI 兼容，含重试）                          │
  └──────────┬─────────────────────────────────────────────────────────┘
             │
  ┌──────────▼─────────────────────────────────────────────────────────┐
  │                     数据层 (src/models/ + src/database.py)          │
  │  database_models.py: Task / WorkflowVersion / AgentLog / ...      │
  │  project_models.py:  Project / ProjectTask                         │
  └────────────────────────────────────────────────────────────────────┘
```

### 3.4 组件视图（C4 Level 3）——前端

```
React SPA 内部：

  ┌─────────────────────────────────────────────────────────────┐
  │  app/index.tsx（根组件 + 视图路由 + 全局状态）                  │
  │                                                             │
  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
  │  │ Dashboard   │  │ AgentTrace   │  │ WorkflowEditor   │  │
  │  │ 视图        │  │ 视图         │  │ 视图              │  │
  │  └─────────────┘  └──────────────┘  └──────────────────┘  │
  │                                                             │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │  GraphDiff 子系统（独立 Feature）                      │   │
  │  │  Container → Canvas（ReactFlow）+ ListPanel + Toolbar │   │
  │  │  useGraphDiff Hook（并行请求编排）                      │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                             │
  │  ┌─────────────┐  ┌────────────────┐  ┌────────────────┐  │
  │  │ProjectSidebar│ │DocumentSidebar │  │SimplifiedAgent │  │
  │  │（项目树CRUD）│  │（三Tab联动）    │  │Trace（COT可视化）│  │
  │  └─────────────┘  └────────────────┘  └────────────────┘  │
  │                                                             │
  │  app/api.ts（HTTP 请求封装）  app/types.ts（类型定义）        │
  └─────────────────────────────────────────────────────────────┘
```

---

## 4. 模块与文件详解

> **格式要求（每个文件必须独立一节，不允许合并）：**
> - **职责：** 1–3句话，说清楚这个文件存在的原因和边界
> - **关键导出：** 对外暴露的函数/类/变量，每项一行，含一句说明
> - **对外依赖：** 依赖的内部模块（非第三方库）
> - **注意事项：** 不显而易见的约定、限制、已知陷阱
>
> ❌ 不合格写法：`- parser_tool.py: DSL解析`（多文件合并一行）
> ✓ 合格写法：每个文件一个 `### \`filename\`` 独立小节（见下方示例）

---

### `main.py`

**职责：** FastAPI 应用入口。定义所有核心 HTTP 端点（任务 CRUD、workflow 版本管理、版本对比、审批、重生成）；同时包含部分业务逻辑（`_build_node_diff_result`、`update_task_workflow`）。

**注意：** 路由层直接内嵌了较重的业务逻辑，是 R-004 风险的来源。

**关键导出：**
- `app: FastAPI` — uvicorn 启动目标
- `create_task()` — 任务创建 + pipeline 线程启动
- `get_task()` — 任务状态查询（前端轮询入口）
- `update_task_workflow()` — 保存用户手动编辑的 DSL
- `compare_workflow_versions()` — 调用 `_build_node_diff_result` 计算图差异
- `approve_task()` / `regenerate_task()` — 审批 / 重生成
- `_build_node_diff_result()` — 核心差异算法（见 §5）

**依赖：** `src/core/sop_extraction_pipeline.py`、`src/services/relationship_service.py`、`src/models/database_models.py`、`src/database.py`

---

### `src/core/state.py`

**职责：** 定义 `PipelineState` TypedDict，是所有 pipeline 节点之间传递数据的唯一共享载体。

**关键字段（全量）：**

```python
class PipelineState(TypedDict, total=False):
    # 任务标识
    db_task_id: str                 # 写库后的 Task.id
    db_version_id: str              # 写库后的 WorkflowVersion.id
    task_name: str                  # LLM 生成的任务名

    # SOP 处理
    sop_text: str                   # 原始 SOP 输入
    sop_split_data: List[dict]      # sop_split_node 输出：步骤列表

    # 检索结果
    knowledge_base_data: List[dict] # ES 知识库检索结果
    threshold_info: List[dict]      # ES 阈值检索结果（未匹配前）

    # Prompt
    prompts: dict                   # load_prompts_node 加载的所有 prompt 模板

    # DSL 生成
    dsl_text: str                   # dsl_generation_node 输出的原始 DSL 文本
    dsl_json: dict                  # parse_dsl_to_json_node 解析后的结构化 JSON

    # 阈值匹配
    threshold_matched_result: dict  # match_thresholds_node 输出：回填阈值后的 DSL JSON

    # 分析与评估
    analysis_results: dict          # analysis_node 输出
    evaluation_result: dict         # evaluation_node 输出

    # COT
    cot_reasoning: str              # cot_formatting_node 输出

    # 错误标记
    error: Optional[str]            # 任意节点写入，pipeline 可据此短路
```

---

### `src/core/pipeline_config.py`

**职责：** 使用 LangGraph `StateGraph` 定义主 pipeline 的节点连接顺序。

**节点顺序（已验证，12节点线性链）：**

```
START
  → generate_task_name_node
  → task_creation_node
  → sop_split_node
  → knowledge_extraction_node
  → threshold_extraction_node
  → load_prompts_node
  → dsl_generation_node
  → parse_dsl_to_json_node
  → match_thresholds_node
  → save_json_result_node
  → import_json_to_db_node
  → format_output_node
  → END
```

**图结构：** 严格线性，无条件分支（evaluation_node 和 analysis_node 在重生成子图中使用，不在主链路）。

---

### `src/tools/parser_tool.py`

**职责：** `DSLParser` 类，将 LLM 输出的 DSL 文本解析为层级化 JSON 结构。这是整个系统中最核心的算法实现之一。

**核心算法详见 §5 `DSLParser.parse()`。**

---

### `src/services/relationship_service.py`

**职责：** `infer_parent_child_relationships()` 函数，在用户手动编辑 DSL 后推理节点的 parent_id 并重建 children 关系树。算法详见 §5。

---

### `src/core/nodes/match_thresholds_node.py`

**职责：** Pipeline 节点9。调用 LLM 将检索到的阈值条目匹配到 DSL JSON 中对应的操作步骤，再通过 `merge_thresholds_to_json()` 将匹配结果回填进 JSON 结构。

**算法详见 §5 `merge_thresholds_to_json()`。**

---

### `src/core/nodes/import_json_to_db_node.py`

**职责：** Pipeline 节点11。将最终 DSL JSON 写入 `workflow_versions` 表，并更新 `task.status`。包含版本递增逻辑。

**关键逻辑：**
- 查询 `MAX(version_number) WHERE task_id=?`，新版本 = max + 1
- 写入 `WorkflowVersion`（含 `nodes_data`、`cot_reasoning`、`knowledge_base_data`、`sop_split_data`、`stats`）
- 更新 `task.status = "Pending Review"`
- 写入 `sop_split` 关联（将 `sop_split_data` 分别存储到各 nodes_data 条目的 sop_split 字段）

---

### `src/core/log_decorator.py`

**职责：** `@log_node` 装饰器，包裹每个 pipeline 节点的 `execute` 方法。

**装饰逻辑：**
1. 节点执行前：写 `AgentLog`（task_id、node_name、status="running"、started_at）
2. 节点正常结束：更新 `AgentLog.status="success"`、`finished_at`、`duration`
3. 节点抛出异常：更新 `AgentLog.status="failed"`、`error_message`；同时写 `AgentTraceDetail`（含完整 traceback）
4. 异常继续向上传播（不吞异常）

---

### `app/index.tsx`

**职责：** 前端根组件。承载全局状态（任务列表、当前任务、视图模式）、前端路由逻辑、ReactFlow 工作流图的 nodes/edges 转换与布局逻辑。

**状态管理模式：** 纯 `useState` + `useEffect`，无 Redux/Zustand，全局状态集中在此文件。这是 R-012 风险来源（单文件承压过重）。

**(partial)** 详细函数级分析待补充（文件约 2000+ 行）

---

### `app/src/components/GraphDiff/useGraphDiff.ts`

**职责：** GraphDiff 功能的数据编排层。并行发起两个请求（compare API + 两个版本的 workflow），合并结果供 UI 消费。

**核心逻辑：** 见 §5 `useGraphDiff()`。

---

## 5. 函数索引、调用关系与算法实现

> **格式要求（每个非平凡函数必须包含）：**
> - **签名**：代码块格式，含参数名/类型/默认值/返回类型
> - **算法实现**：若含算法逻辑，必须用**编号步骤**展开，不允许用"调用X完成Y"代替
> - **副作用**：精确到 DB 表名+操作类型、HTTP endpoint、文件路径
> - **失败行为**：异常类型、触发条件、是否传播、降级路径
> - **调用关系**：`Called by: 函数名` / `Calls: 函数名`
>
> ❌ 不合格写法（只写函数名+一句话）：
> ```
> match_thresholds_node() → LLM阈值匹配 + merge_thresholds_to_json()
> ```
> ✓ 合格写法（见下方各函数示例，有签名+编号步骤+副作用+失败行为）

---

### `DSLParser.parse()` — `src/tools/parser_tool.py`

```python
def parse(self, dsl_text: str) -> dict:
    """将 LLM 输出的 DSL 文本解析为层级化 workflow JSON"""
```

**算法实现（四阶段流水线）：**

**阶段1 — extract_dsl：** 从原始 LLM 输出中提取 DSL 块。
- 用正则匹配 ` ```dsl ... ``` ` 代码块
- 若无代码块标记，尝试直接解析整个文本
- 清洗：去除 BOM、统一换行符、去除行尾空白

**阶段2 — parse_dsl：** 将 DSL 文本解析为节点列表。
- 按行扫描，识别节点声明格式：`[节点类型] 节点名称`
- 识别缩进层级（每级 2 空格或 4 空格，自适应检测）
- 构建中间表示：`List[{type, name, indent_level, raw_line}]`
- 特殊处理：多行节点内容（节点描述跨行时合并）

**阶段3 — parse_path_table：** 解析路径关系表（PATH 块）。
- DSL 可选包含 PATH 块，描述节点间的顺序约束
- 格式：`A → B → C`（支持 `→`、`->` 两种箭头）
- 输出：`Dict[str, List[str]]`（父节点 → 子节点列表的映射）

**阶段4 — build_hierarchy：** 将扁平节点列表 + 路径关系合并为层级 JSON。
- 优先使用 PATH 表确定父子关系
- PATH 表缺失时，回退到缩进层级推断父子关系
- 处理特殊节点类型：`CONDITION`（条件分支）、`LOOP`（循环）、`PARALLEL`（并行）
- 输出格式：`{nodes: [{id, type, name, children: [...], ...}], edges: [...]}`

**失败行为：**
- DSL 格式错误 → 抛出 `DSLParseError`，节点捕获后写 `error` 到 state
- PATH 表与节点列表不一致 → 记录警告日志，忽略无效 PATH 条目，继续处理

**调用关系：**
- Called by: `parse_dsl_to_json_node.py::execute`
- Calls: `extract_dsl()`, `parse_dsl()`, `parse_path_table()`, `build_hierarchy()`

---

### `infer_parent_child_relationships()` — `src/services/relationship_service.py`

```python
def infer_parent_child_relationships(
    nodes: List[dict],          # 用户编辑后的节点列表（可能缺失 parent_id）
    edges: List[dict]           # 用户编辑后的边列表（source → target）
) -> List[dict]:                # 返回：每个节点都有正确 parent_id 和 children 的节点列表
```

**算法实现（图遍历 + 树重建）：**

**步骤1 — 构建邻接表：** 从 `edges` 列表构建 `{source_id: [target_id]}` 的有向邻接表。

**步骤2 — 找根节点：** 找出没有任何 edge 指向自己的节点（入度为 0），作为树的根节点。若多个根节点存在，取 position.y 最小的（最靠上）作为真正根节点，其余视为孤立节点。

**步骤3 — BFS/DFS 遍历：** 从根节点开始广度优先遍历邻接表，为每个节点设置 `parent_id`（父节点 id）。

**步骤4 — 重建 children 列表：** 反向遍历，为每个节点聚合 `children: [child_id, ...]`。

**步骤5 — 处理孤立节点：** 不在树中的节点（孤立）设 `parent_id = null`，`children = []`。

**边界情况：**
- 环路检测：若遍历中发现已访问节点（环路），记录警告并跳过
- 节点不在 edges 中：保留原有 parent_id（用户可能手动设置）

**调用关系：**
- Called by: `main.py::update_task_workflow`
- Calls: 无（纯计算，无外部依赖）

---

### `merge_thresholds_to_json()` — `src/core/nodes/match_thresholds_node.py`

```python
def merge_thresholds_to_json(
    dsl_json: dict,                    # parse_dsl_to_json_node 输出的结构化 JSON
    threshold_matched_result: dict     # LLM 输出的匹配结果：{step_name: [threshold_item, ...]}
) -> dict:                             # 返回：阈值已回填进对应节点的 dsl_json
```

**算法实现（递归树遍历 + 名称模糊匹配）：**

**步骤1 — 建立匹配索引：** 将 `threshold_matched_result` 的 key（步骤名）做归一化（去除空格、转小写、去除标点），建立 `{normalized_name: [threshold_items]}` 索引。

**步骤2 — 递归遍历 DSL 节点树：** 对 `dsl_json.nodes` 中的每个节点（含子节点），将节点 `name` 做同样归一化后，在索引中查找匹配项。

**步骤3 — 模糊匹配策略（按优先级）：**
1. 精确匹配（归一化后完全相同）
2. 包含匹配（节点名包含步骤名，或步骤名包含节点名）
3. 编辑距离匹配（Levenshtein 距离 ≤ 2）

**步骤4 — 回填：** 匹配成功的节点，在其 JSON 对象中新增 `thresholds: [...]` 字段。

**步骤5 — 未匹配记录：** 将未成功匹配的阈值条目记录到 `state.error_thresholds`（不阻断 pipeline）。

**调用关系：**
- Called by: `match_thresholds_node.py::execute`
- Calls: `levenshtein_distance()`（utils.py 中的纯函数）

---

### `_build_node_diff_result()` — `main.py`

```python
def _build_node_diff_result(
    workflow_a: dict,    # 版本A的 nodes_data（完整 JSON）
    workflow_b: dict,    # 版本B的 nodes_data（完整 JSON）
) -> GraphDiffResult:   # 包含 nodeDiffs / edgeDiffs / metrics / moveGroups
```

**算法实现（集合运算 + 内容比对）：**

**步骤1 — 节点 ID 集合运算：**
```
only_in_A = set(A.node_ids) - set(B.node_ids)  → removed
only_in_B = set(B.node_ids) - set(A.node_ids)  → added
in_both   = set(A.node_ids) & set(B.node_ids)  → 需进一步比对
```

**步骤2 — 内容变更检测：** 对 `in_both` 中的每个节点，逐字段比对（name、type、thresholds、position）。有任意字段变化 → 标记为 `modified`。

**步骤3 — 位置移动检测（moveGroups）：** 对 `modified` 节点中仅 position 变化（name/type/thresholds 不变）的，归入 `moveGroups`（前端可据此区分"内容变化"与"纯移动"）。

**步骤4 — 边差异：** 对边做同样集合运算（以 `source+target` 为边的唯一标识）。

**步骤5 — metrics 计算：**
```python
metrics = {
    "nodeCountBefore": len(A.nodes),
    "nodeCountAfter":  len(B.nodes),
    "addedCount":      len(added),
    "removedCount":    len(removed),
    "modifiedCount":   len(modified) - len(moveGroups),
    "movedCount":      len(moveGroups),
}
```

**调用关系：**
- Called by: `main.py::compare_workflow_versions`
- Calls: 无（纯计算）

---

### `run_sop_extraction_pipeline()` — `src/core/sop_extraction_pipeline.py`

```python
def run_sop_extraction_pipeline(
    sop_text: str,
    task_id: str,        # 前端传入的临时 ID（写库前占位用）
    db_url: str,         # 数据库连接串（线程内重新建连，避免跨线程 Session 问题）
) -> None
```

**行为：**
1. 在当前线程内创建独立 `SessionLocal()`（不复用主线程 Session）
2. 构建初始 `PipelineState{sop_text, task_id, ...}`
3. 调用 `compiled_graph.invoke(state)`（同步阻塞，等待12个节点全部完成）
4. `finally` 块：关闭 Session

**副作用：**
- DB 写：Task（通过 task_creation_node）
- DB 写：WorkflowVersion（通过 import_json_to_db_node）
- DB 写：AgentLog × N条（每节点一条，通过 log_decorator）
- 文件写：JSON 文件（通过 save_json_result_node）
- LLM 调用：多次（task_name / sop_split / dsl_generation / match_thresholds）

**失败行为：** 任何节点未捕获异常 → LangGraph 终止 invoke → `finally` 中更新 `task.status = "Failed"`

**注意：** 此函数在后台线程中运行，禁止直接使用主线程的任何 SQLAlchemy Session 对象。

---

### `useGraphDiff()` — `app/src/components/GraphDiff/useGraphDiff.ts`

```typescript
function useGraphDiff(
    taskId: string,
    versionA: number,
    versionB: number,
): {
    diffResult: GraphDiffResult | null,
    workflowA: WorkflowData | null,
    workflowB: WorkflowData | null,
    isLoading: boolean,
    error: Error | null,
}
```

**算法实现（并行请求 + 结果合并）：**

```typescript
// 并行发起3个请求，避免串行等待
const [compareResult, wfA, wfB] = await Promise.all([
    api.compareWorkflowVersions(taskId, versionA, versionB),
    api.getWorkflow(taskId, versionA),
    api.getWorkflow(taskId, versionB),
]);
```

**状态机：** `idle → loading → success | error`（通过 `useReducer` 管理，避免 race condition）

**Race condition 防护：** 使用 `AbortController` + cleanup function，组件卸载或参数变更时取消进行中的请求。

---

### 关键调用路径

```
用户提交任务 → 前端
  TaskList.tsx::handleCreate
    └─ api.ts::createTask (POST /api/tasks)
        └─ main.py::create_task
            ├─ db.add(Task{status="Initializing"}) + db.commit()
            └─ Thread(target=run_sop_extraction_pipeline).start()
                └─ sop_extraction_pipeline.py::run_sop_extraction_pipeline
                    └─ compiled_graph.invoke(state)
                        ├─ generate_task_name_node::execute → LLM
                        ├─ task_creation_node::execute → DB(Task INSERT)
                        ├─ sop_split_node::execute → LLM
                        ├─ knowledge_extraction_node::execute → ES
                        ├─ threshold_extraction_node::execute → ES
                        ├─ load_prompts_node::execute → 文件系统
                        ├─ dsl_generation_node::execute → LLM
                        ├─ parse_dsl_to_json_node::execute
                        │   └─ DSLParser.parse() → [四阶段算法]
                        ├─ match_thresholds_node::execute → LLM
                        │   └─ merge_thresholds_to_json() → [模糊匹配算法]
                        ├─ save_json_result_node::execute → 文件系统
                        ├─ import_json_to_db_node::execute → DB(WorkflowVersion INSERT)
                        └─ format_output_node::execute

用户查看差异对比 → 前端
  GraphDiffContainer.tsx 渲染时
    └─ useGraphDiff(taskId, versionA, versionB)
        └─ Promise.all([compareAPI, getWorkflowA, getWorkflowB])
            └─ main.py::compare_workflow_versions
                └─ _build_node_diff_result(wfA, wfB)
                    └─ [集合运算+内容比对算法]

用户手动编辑保存 → 前端
  WorkflowEditor 中保存操作
    └─ api.ts::saveWorkflow (PUT /api/tasks/{id}/workflow)
        └─ main.py::update_task_workflow
            └─ relationship_service.py::infer_parent_child_relationships
                └─ [图遍历+树重建算法]
            └─ db.add(WorkflowVersion{created_by="user"}) + db.commit()
```

---

## 6. 完整数据流链路

> 每条 Flow 展示：触发点 → 每一跳（文件::函数 + 入参 + 出参 + 副作用）→ 最终结果。

---

### F-001：用户提交任务 → Pipeline 自动生成 DSL → 前端感知

**触发：** 用户在 Dashboard 填写 SOP 文本并点击提交

```
① 用户操作
   文件: app/index.tsx 或 TaskList 视图中的提交逻辑
   动作: 收集 {title, sop_text, project_id}，调用 createTask

② 前端 HTTP 请求
   文件: app/api.ts::createTask
   动作: POST /api/tasks，body={title, sop_text, project_id}

③ 后端接收，创建占位任务，启动后台线程
   文件: main.py::create_task
   入参: CreateTaskRequest{title, sop_text, project_id}
   动作:
     a. INSERT INTO tasks (title, sop_text, status="Initializing") → 获得 task.id
     b. Thread(target=run_sop_extraction_pipeline, args=(sop_text, task.id, db_url)).start()
        ⚠️ 注意：传入 db_url 字符串而非 db Session（避免跨线程 Session 复用）
   出参: TaskResponse{id, status="Initializing", ...}
   HTTP: 201 立即返回（不等 pipeline 完成）

④ 前端开始轮询
   文件: app/index.tsx（useEffect + setInterval）
   动作: 每 2s → GET /api/tasks/{id}
         当 status ∈ {"Pending Review", "Failed"} → 停止轮询，刷新视图

⑤ 后台线程：Pipeline 执行（12节点串行）

   ⑤-1 [generate_task_name_node]
        文件: src/core/nodes/generate_task_name_node.py::execute
        入参: state{sop_text}
        动作: LLM 调用（prompt: generate_task_name.txt + sop_text 前N字）
        出参: state{task_name: "xxx设备故障处理流程"}
        副作用: 写 AgentLog（node="generate_task_name", status=success/failed）

   ⑤-2 [task_creation_node]
        文件: src/core/nodes/task_creation_node.py::execute
        入参: state{task_name, task_id(临时)}
        动作: UPDATE tasks SET title=task_name WHERE id=task_id
             OR 确认 Task 记录已存在（幂等）
        出参: state{db_task_id: "uuid"}
        副作用: DB UPDATE tasks

   ⑤-3 [sop_split_node]
        文件: src/core/nodes/sop_split_node.py::execute
        入参: state{sop_text, prompts.sop_split}
        动作: LLM 调用，将 SOP 拆分为操作步骤列表
        出参: state{sop_split_data: [{step_id, step_name, content, ...}, ...]}
        副作用: 写 AgentLog

   ⑤-4 [knowledge_extraction_node]
        文件: src/core/nodes/knowledge_extraction_node.py::execute
        入参: state{sop_split_data}
        动作: 对每个 step，查询 ES 知识库索引（BM25 检索）
        出参: state{knowledge_base_data: [{step_id, docs: [...]}]}
        副作用: ES 读操作；写 AgentLog；ES 失败时 knowledge_base_data=[]（降级）

   ⑤-5 [threshold_extraction_node]
        文件: src/core/nodes/threshold_extraction_node.py::execute
        入参: state{sop_split_data}
        动作: 对每个 step，查询 ES 阈值索引
        出参: state{threshold_info: [{step_id, thresholds: [...]}]}
        副作用: ES 读操作；写 AgentLog

   ⑤-6 [load_prompts_node]
        文件: src/core/nodes/load_prompts_node.py::execute
        动作: 从 src/prompts/*.txt 读取所有 prompt 模板
        出参: state{prompts: {dsl_generation: "...", threshold_matching: "...", ...}}
        副作用: 文件系统读操作

   ⑤-7 [dsl_generation_node]
        文件: src/core/nodes/dsl_generation_node.py::execute
        入参: state{sop_split_data, knowledge_base_data, prompts.dsl_generation}
        动作: LLM 调用（大型 prompt，含 SOP 步骤 + 知识库 + few-shot 示例）
        出参: state{dsl_text: "```dsl\n[STEP]...\n```"}
        副作用: LLM API 调用（最耗时节点，约 10~30s）；写 AgentLog + AgentTraceDetail（含完整 prompt）

   ⑤-8 [parse_dsl_to_json_node]
        文件: src/core/nodes/parse_dsl_to_json_node.py::execute
        入参: state{dsl_text}
        动作: 调用 DSLParser.parse(dsl_text)（见 §5 算法详解）
        出参: state{dsl_json: {nodes: [...], edges: [...]}}
        副作用: 写 AgentLog；解析失败时 state{error: "DSLParseError: ..."}

   ⑤-9 [match_thresholds_node]
        文件: src/core/nodes/match_thresholds_node.py::execute
        入参: state{dsl_json, threshold_info, prompts.threshold_matching}
        动作:
          a. LLM 调用：将 threshold_info 中的条目匹配到 dsl_json 中的对应步骤
          b. merge_thresholds_to_json(dsl_json, llm_output)（见 §5 算法）
        出参: state{threshold_matched_result: {nodes: [...带thresholds字段...], edges: [...]}}
        副作用: LLM API 调用；写 AgentLog

   ⑤-10 [save_json_result_node]
         文件: src/core/nodes/save_json_result_node.py::execute
         入参: state{threshold_matched_result, db_task_id}
         动作: 将 JSON 写入文件系统（路径: output/{task_id}/result.json）
         副作用: 文件系统写操作；⚠️ 路径含硬编码旧目录（R-006）

   ⑤-11 [import_json_to_db_node]
         文件: src/core/nodes/import_json_to_db_node.py::execute
         入参: state{threshold_matched_result, db_task_id, sop_split_data, cot_reasoning, knowledge_base_data}
         动作:
           a. SELECT MAX(version_number) FROM workflow_versions WHERE task_id=?
           b. INSERT INTO workflow_versions (task_id, version=max+1, nodes_data=threshold_matched_result,
                 sop_split_data, cot_reasoning, knowledge_base_data, stats, created_by="system")
           c. UPDATE tasks SET status="Pending Review", current_version_id=new_version.id
         出参: state{db_version_id: "uuid"}
         副作用: DB 写操作（workflow_versions INSERT + tasks UPDATE）

   ⑤-12 [format_output_node]
         文件: src/core/nodes/format_output_node.py::execute
         动作: 整理最终输出格式（供 pipeline 调用方检查用）
         副作用: 写 AgentLog（pipeline 完成标记）

⑥ 前端轮询感知完成
   下一次 GET /api/tasks/{id} 返回 status="Pending Review"
   前端停止轮询，展示工作流图和审批按钮
```

---

### F-002：用户手动编辑 DSL → 保存新版本

**触发：** 用户在 WorkflowEditor 中拖拽/编辑节点后点击保存

```
① 用户操作
   文件: app/index.tsx（WorkflowEditor 视图中的保存逻辑）
   动作: 收集当前 ReactFlow 的 nodes 和 edges 状态，序列化为 DSL JSON

② 前端请求
   文件: app/api.ts::saveWorkflow
   动作: PUT /api/tasks/{id}/workflow，body={nodes, edges}

③ 后端处理
   文件: main.py::update_task_workflow
   动作:
     a. 调用 infer_parent_child_relationships(nodes, edges)（见 §5 算法）
        → 重建每个节点的 parent_id 和 children 字段
     b. SELECT MAX(version_number) FROM workflow_versions WHERE task_id=?
     c. INSERT INTO workflow_versions (version=max+1, nodes_data=result, created_by="user")
     d. UPDATE tasks SET current_version_id=new_version.id
   出参: WorkflowVersionResponse{id, version_number, created_at}
   副作用: DB 写（workflow_versions INSERT + tasks UPDATE）

④ 前端更新
   文件: app/index.tsx
   动作: 更新本地版本列表，展示新版本号
```

---

### F-003：版本对比（GraphDiff）

**触发：** 用户在版本列表选择两个版本，点击对比

```
① 用户选择版本A和版本B

② 前端并行请求（useGraphDiff Hook）
   文件: app/src/components/GraphDiff/useGraphDiff.ts::useGraphDiff
   动作: Promise.all([
     api.compareWorkflowVersions(taskId, vA, vB),  → GET /compare?v1=vA&v2=vB
     api.getWorkflow(taskId, vA),                   → GET /workflow?version=vA
     api.getWorkflow(taskId, vB),                   → GET /workflow?version=vB
   ])

③ 后端计算差异
   文件: main.py::compare_workflow_versions
   动作: 查询两个版本的 nodes_data，调用 _build_node_diff_result(wfA, wfB)（见 §5 算法）
   出参: GraphDiffResult{nodeDiffs, edgeDiffs, metrics, moveGroups}

④ 前端渲染
   文件: GraphDiffContainer.tsx → GraphDiffCanvas.tsx + DiffListPanel.tsx
   动作:
     - DiffListPanel 按 added/removed/modified 分组展示节点差异列表
     - GraphDiffCanvas 在版本B的 ReactFlow 画布上高亮差异节点（DiffNodeWrapper）
     - 用户点击列表项 → useNodeFocus 驱动画布自动 fitView 聚焦到目标节点
```

---

### F-004：重生成（Regenerate）

**触发：** 用户对已有任务点击"重生成"

```
① 前端请求
   文件: app/api.ts::regenerateTask
   动作: POST /api/tasks/{id}/regenerate

② 后端启动重生成线程
   文件: main.py::regenerate_task
   动作:
     a. 读取当前 task 的 sop_text（不重新输入）
     b. Thread(target=run_regenerate_pipeline, args=(task.sop_text, task.id, db_url)).start()
     c. 立即返回（202 Accepted）

③ 重生成 Pipeline（从 sop_split 起，跳过 generate_task_name 和 task_creation）
   文件: src/core/regenerate_pipeline.py::run_regenerate_pipeline
   节点链: [analysis_node] → [sop_split] → [knowledge_extraction] → ...（同 F-001 ⑤-3 起）
   结果: 新版本写入 workflow_versions（version 递增）

④ 前端轮询感知（同 F-001 ④）
```

---

## 7. 外部集成详情

| 集成 | 入口位置 | 连接配置 | 失败行为 | 重试策略 | 备注 |
|------|---------|---------|---------|---------|------|
| PostgreSQL | `src/database.py::get_db` | URL from `settings.DATABASE_URL`，SQLAlchemy 默认连接池 | `OperationalError` 向上传播，request 级事务回滚 | 无 | 多线程场景下每线程独立 Session（R-005 已修复方向） |
| LLM Service | `src/core/chat.py::Chat` | base_url from env，`trust_env=False`，`max_retries=2`，timeout=30s | 超时/失败经 2 次重试后抛出，节点捕获后写 error | 2次（httpx 内置） | 不同节点使用不同 prompt，共用同一 Chat 客户端 |
| Elasticsearch | knowledge/threshold 节点内 | host from env，timeout=10s | 连接失败 → 返回空列表，写 warning 日志，pipeline 继续（降级） | 无 | 降级后 DSL 质量可能下降但不中断 |
| 文件系统 | `save_json_result_node` | 硬编码路径 `output/{task_id}/` | 路径异常 → 节点失败 → pipeline Failed | 无 | ⚠️ R-006：路径含旧目录，生产环境需配置化 |

---

## 8. 数据模型与契约

### 8.1 核心 ORM 模型

#### `Task`

```python
class Task(Base):
    __tablename__ = "tasks"
    id: str              # UUID，主键
    title: str           # 任务名，NOT NULL
    sop_text: str        # 原始 SOP，TEXT
    status: str          # 见下方状态机（无 DB 约束，仅应用层）
    project_id: str      # FK → projects.id（可为 NULL）
    current_version_id: str  # FK → workflow_versions.id（最新激活版本）
    created_at / updated_at: datetime

# 状态机：
# Initializing → [pipeline 启动后] Running
# Running → [import_json_to_db_node 成功] Pending Review
# Running → [任意节点未捕获异常] Failed
# Pending Review → [approve_task] Approved
# Pending Review → [reject] Rejected
# 任意 → [regenerate_task] Running（重新进入）
```

#### `WorkflowVersion`

```python
class WorkflowVersion(Base):
    __tablename__ = "workflow_versions"
    id: str
    task_id: str         # FK → tasks.id
    version_number: int  # 从 1 递增
    nodes_data: dict     # JSON：完整 DSL（含 nodes、edges、thresholds 回填后）
    sop_split_data: dict # JSON：SOP 拆分结果，与 nodes 对应
    cot_reasoning: str   # COT 推理链文本
    knowledge_base_data: dict  # JSON：检索到的知识库条目
    stats: dict          # JSON：节点数、边数、评估分数等
    created_by: str      # "system"（pipeline）或 "user"（手动编辑）
    created_at: datetime
```

#### `AgentLog` / `AgentTraceDetail`

```python
class AgentLog(Base):
    __tablename__ = "agent_logs"
    id: str
    task_id: str          # FK → tasks.id
    node_name: str        # 节点标识符
    status: str           # "running" / "success" / "failed"
    started_at / finished_at: datetime
    duration_ms: int
    error_message: str    # 节点失败时填写

class AgentTraceDetail(Base):
    __tablename__ = "agent_trace_details"
    id: str
    log_id: str           # FK → agent_logs.id
    prompt: str           # 完整 prompt（TEXT，可能较大）
    response: str         # 完整 LLM 响应
    token_count: int
```

### 8.2 前端类型契约（`app/types.ts` 关键类型）

```typescript
// 任务（主体）
interface Task {
    id: string;
    title: string;
    status: TaskStatus;
    sop_text: string;
    current_version?: WorkflowVersion;
    project_id?: string;
}

type TaskStatus = "Initializing" | "Running" | "Pending Review"
                | "Approved" | "Failed" | "Rejected" | "Cancelled";

// 版本对比结果
interface GraphDiffResult {
    nodeDiffs: {
        added: NodeData[];
        removed: NodeData[];
        modified: {node: NodeData; changedFields: string[]}[];
    };
    edgeDiffs: {added: EdgeData[]; removed: EdgeData[]};
    moveGroups: {nodeId: string; from: Position; to: Position}[];
    metrics: {
        nodeCountBefore: number; nodeCountAfter: number;
        addedCount: number; removedCount: number;
        modifiedCount: number; movedCount: number;
    };
}
```

---

## 9. 风险与隐患登记册

### P0 — 系统级（数据损坏 / 崩溃）

#### [R-005] `regenerate_task` 后台线程可能复用请求 Session

**位置：** `main.py::regenerate_task`
**风险：** 若传入的 db Session 是请求级 Session，后台线程结束前请求 Session 被关闭 → `DetachedInstanceError` 或静默数据损坏
**触发条件：** 高并发重生成时必现
**状态：** `run_sop_extraction_pipeline` 已改为传入 `db_url`（字符串）并在线程内建立独立 Session；`regenerate_task` 是否同步修复需确认 **(conflict)**
**建议：** 统一要求所有后台线程函数接收 `db_url: str` 而非 `db: Session`

---

### P1 — 用户可见问题

#### [R-002] `create_task` 线程异常不回写占位任务状态

**位置：** `main.py::create_task` 中线程启动逻辑
**风险：** pipeline 启动前崩溃（如 db_url 错误）→ task 永远停在 "Initializing"，前端无限轮询
**建议：** 在 `Thread.start()` 外包裹 try/except，失败时立即更新 `task.status = "Failed"`

#### [R-007] ES 工具失败无统一降级标记

**位置：** `knowledge_extraction_node.py`、`threshold_extraction_node.py`
**风险：** ES 失败静默返回空列表，后续节点无法感知数据是否可信，DSL 质量下降无告警
**建议：** 在 state 中写 `knowledge_retrieval_failed: bool` / `threshold_retrieval_failed: bool`，供后续节点决策

---

### P2 — 可维护性隐患

#### [R-004] `main.py` 路由层内嵌重业务逻辑

**位置：** `main.py`：`_build_node_diff_result`、`update_task_workflow` 等函数直接在路由文件中
**风险：** 文件过重，业务逻辑难以单测，与路由耦合
**建议：** 拆分至 `src/services/diff_service.py`、`src/services/workflow_service.py`

#### [R-006] Pipeline 输出路径硬编码

**位置：** `save_json_result_node.py`
**建议：** 改为从 `settings.OUTPUT_DIR` 读取

#### [R-008] AgentTraceDetail 存储完整 prompt/response，可能暴露敏感信息

**位置：** `log_decorator.py`
**建议：** 生产环境配置脱敏策略（截断超长 prompt、过滤敏感关键词）

#### [R-009] settings.py 默认 DB 配置可能误连开发库

**位置：** `src/settings.py`
**建议：** 生产启动时校验 `DATABASE_URL` 非默认值

#### [R-010] `useGraphDiff` 与 `api.getWorkflow` 调用签名待编译确认

**位置：** `app/src/components/GraphDiff/useGraphDiff.ts`
**状态：** **(conflict)** — 运行时行为与类型签名可能存在漂移，需 TS 编译验证

#### [R-011] `ProjectSidebar` 状态管理分支过多

**位置：** `app/src/components/ProjectSidebar.tsx`
**建议：** 抽离为状态机（useReducer），减少 boolean flag 数量

#### [R-012] `app/index.tsx` 单文件过重（2000+ 行）

**位置：** `app/index.tsx`
**风险：** 全局状态与多个视图耦合，难以维护和测试
**建议：** 按视图拆分子组件，使用 Context 或轻量状态库管理全局状态
