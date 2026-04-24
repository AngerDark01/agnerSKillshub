# ITERATION LOG — [项目名称]

> **规则：** 每轮分两段写入，A（阅读前声明）→ 阅读 → C（阅读后记录）。
> 不允许先读再补写 A 段。不允许合并多轮为一条记录。
> Coverage 表备注栏：每个文件必须写具体发现，不允许多文件写相同备注。

---

## [初始化] YYYY-MM-DD

**操作：** 运行 `rg --files` 生成清单，创建 CODEBASE.md 和本文件骨架
**文件总数：** N 个源码文件
**下一轮计划：** 第1轮粗览 — 只读目录结构和配置文件，不读任何源码

### 覆盖进度总表（此处建立，后续每轮只更新变化的行）

> 状态：PENDING / 浅读 / (partial) / (conflict) / 深度完整

| 文件路径 | 状态 | 阅读轮次 | 阅读次数 | 备注（具体发现，不能与其他文件相同） |
|---------|------|---------|---------|--------------------------------------|
| main.py | PENDING | — | 0 | |
| src/settings.py | PENDING | — | 0 | |
| src/database.py | PENDING | — | 0 | |
| src/core/state.py | PENDING | — | 0 | |
| ... | ... | ... | ... | |

---

## [第1轮] YYYY-MM-DD ← 粗览轮：只读配置，不读源码

### A. 本轮目标（阅读前声明）

**目标：**
- `README.md`（了解项目定位和启动方式）
- `requirements.txt` / `package.json`（识别技术栈和版本）
- `start.sh` / `start_frontend.sh`（了解启动命令和端口）
- 目录树（`find . -type f`，只看结构，不打开源码文件）

**选择原因：** 第1轮固定粗览，建立文件地图。
**本轮想弄清楚：** 项目是什么？主要目录结构？运行几个进程？用什么框架版本？

---

### C. 本轮发现（阅读后记录）

**关键发现：**
- (verified) 后端：Python 3.11 + FastAPI + LangGraph + SQLAlchemy，端口 8000
- (verified) 前端：React 18 + TypeScript + ReactFlow + Vite，端口 5173
- (verified) 共 80 个源文件，核心业务在 src/core/nodes/（15个节点文件）

**修订的旧结论：** 无（首轮）

**新疑问：**
- main.py 直接处理业务还是纯路由转发？
- pipeline 是线性还是有分支？

**更新了 CODEBASE.md：**
- §1 概览（技术栈+版本号+端口）
- §2 目录结构图骨架（每文件注释待后续补充）

**覆盖进度更新（仅本轮阅读的文件）：**

| 文件路径 | 前状态 | 现状态 | 阅读次数 | 备注（具体发现） |
|---------|-------|-------|---------|----------------|
| README.md | PENDING | 深度完整 | 1 | 项目定位：SOP→工作流图；启动方式确认；无安装依赖说明，需手动装 |
| requirements.txt | PENDING | 深度完整 | 1 | Python 3.11；FastAPI 0.110；LangGraph 0.1.0；langchain-openai 0.1.x |
| start.sh | PENDING | 深度完整 | 1 | uvicorn main:app --port 8000 --reload；无 workers 配置 |
| start_frontend.sh | PENDING | 深度完整 | 1 | vite dev --port 5173；代理配置在 vite.config.ts |
| app/vite.config.ts | PENDING | 深度完整 | 1 | proxy: /api → http://localhost:8000；无其他特殊配置 |

**下一轮计划：** 第2轮 — 读 main.py + src/core/state.py + app/api.ts + app/types.ts，建立前后端接口面

---

## [第2轮] YYYY-MM-DD ← 入口与接口轮

### A. 本轮目标（阅读前声明）

**目标：**
- `main.py`（路由全貌、业务逻辑分布、线程启动方式）
- `src/core/state.py`（PipelineState 所有字段名和类型）
- `app/api.ts`（前端发出哪些请求、参数结构）
- `app/types.ts`（前后端共享类型定义）

**选择原因：** 建立前后端交互面，才能沿调用链向内追踪。
**本轮想弄清楚：** 有哪些 API？PipelineState 有哪些字段？任务状态机是什么？

---

### C. 本轮发现（阅读后记录）

**关键发现：**
- (verified) main.py 含大量业务逻辑（`_build_node_diff_result`、`update_task_workflow`），不只是路由
- (verified) 任务线程启动：`threading.Thread(target=run_sop_extraction_pipeline)` 传入 db_url 字符串
- (verified) PipelineState 共 14 个字段（全量见 CODEBASE §8）
- (verified) 前端轮询：`setInterval(2000)` → `GET /api/tasks/{id}`

**修订的旧结论：** 原来以为 main.py 纯路由 → 现确认内嵌重业务，是 R-004 来源

**新疑问：**
- `_build_node_diff_result` 的差异算法具体怎么比较？用 id 还是 name 做主键？
- `regenerate_task` 是否也用 db_url 传入还是复用 session？（R-005 待确认）

**更新了 CODEBASE.md：**
- §3 架构全景（C4 Level 1 + 2 初稿）
- §4 main.py、state.py、api.ts、types.ts 各独立小节
- §8 数据模型（Task/WorkflowVersion ORM + PipelineState 字段表 + TaskStatus 枚举）

**覆盖进度更新：**

| 文件路径 | 前状态 | 现状态 | 阅读次数 | 备注（具体发现） |
|---------|-------|-------|---------|----------------|
| main.py | PENDING | 浅读 | 1 | 路由 12 个；含 _build_node_diff_result（差异算法）和 update_task_workflow（关系推理入口）；线程传 db_url 而非 session |
| src/core/state.py | PENDING | 深度完整 | 1 | PipelineState TypedDict，14字段，total=False；关键字段：db_task_id/dsl_json/threshold_matched_result/error；无复杂逻辑 |
| app/api.ts | PENDING | 深度完整 | 1 | 12个请求函数；baseURL 硬编码 http://localhost:8000（R-003）；无全局错误拦截 |
| app/types.ts | PENDING | 深度完整 | 1 | Task/WorkflowVersion/GraphDiffResult/COTStep 四个核心类型；TaskStatus 7种枚举值 |

**下一轮计划：** 第3轮 — 精读 `src/tools/parser_tool.py`（DSL解析算法，复杂，单独一轮）

---

## [第3轮] YYYY-MM-DD ← 算法精读轮：DSLParser

### A. 本轮目标（阅读前声明）

**目标：**
- `src/tools/parser_tool.py`（DSLParser 完整实现，逐行精读）

**选择原因：** 这是系统最核心的算法文件（LLM 输出 → 结构化 JSON），第2轮在 §5 占位但未展开，必须单独精读。
**本轮想弄清楚：**
- extract_dsl 怎么从 LLM 输出中提取 DSL 块？用正则还是分隔符？
- parse_dsl 如何识别节点类型和缩进层级？
- build_hierarchy 如何处理 PATH 表和缩进的冲突？
- 什么情况下会解析失败？异常如何传播？

---

### C. 本轮发现（阅读后记录）

**关键发现：**
- (verified) extract_dsl：正则 ` ```dsl\n(.*?)\n``` `（re.DOTALL），无标记时尝试直接解析全文
- (verified) parse_dsl：按行扫描，缩进用 `len(line) - len(line.lstrip())`，自动检测单位（2或4空格）
- (verified) build_hierarchy：PATH 表优先；PATH 缺失时降级为缩进推断；CONDITION/LOOP/PARALLEL 节点类型做特殊处理（children 语义不同）
- (verified) 失败时抛 `DSLParseError(message, raw_line)`，在 parse_dsl_to_json_node 中被捕获写入 state.error
- (inferred) PATH 表与节点列表不一致时忽略无效 PATH 条目（无日志记录，静默处理）

**修订的旧结论：** 原以为是简单字符串分割 → 实际是四阶段流水线，有回退策略

**新疑问：** PATH 表中有环路时如何处理？代码里没看到环路检测

**更新了 CODEBASE.md：**
- §4 parser_tool.py 独立小节（职责/导出/注意事项）
- §5 DSLParser.parse() 完整算法步骤（四阶段，每阶段展开）
- §9 新增 R-013：PATH 表无环路检测（若 LLM 生成环路 DSL，解析结果不可预期）

**覆盖进度更新：**

| 文件路径 | 前状态 | 现状态 | 阅读次数 | 备注（具体发现） |
|---------|-------|-------|---------|----------------|
| src/tools/parser_tool.py | PENDING | 深度完整 | 1 | DSLParser 类，4个私有方法；最复杂点：build_hierarchy 的 PATH优先+缩进降级逻辑；DSLParseError 含 raw_line 便于调试；约320行 |

**下一轮计划：** 第4轮 — 精读 `src/services/relationship_service.py` + `main.py::_build_node_diff_result`（两个算法文件）

---

## [第N轮] YYYY-MM-DD

### A. 本轮目标（阅读前声明）

**目标：** `file.py`（原因：...）
**本轮想弄清楚：** [来自上一轮的具体疑问]

---

### C. 本轮发现（阅读后记录）

**关键发现：** ...
**修订的旧结论：** ...
**新疑问：** ...
**更新了 CODEBASE.md：** ...

**覆盖进度更新：**

| 文件路径 | 前状态 | 现状态 | 阅读次数 | 备注（具体发现） |
|---------|-------|-------|---------|----------------|
| file.py | PENDING | 深度完整 | 1 | [必须是这个文件的具体发现，不能与其他文件写一样的话] |

**下一轮计划：** ...

---

## [SYNC] YYYY-MM-DD HH:MM — 任务简述

### A. SYNC 范围声明（执行前写）

**触发任务：** [代码修改描述]
**直接变更文件：** [列出]
**预计连带影响：** [调用方/被调用方/共享模型/关联 Flow]

---

### C. SYNC 结果（执行后写）

**实际连带重读：** [列出，说明为什么需要重读]
**CODEBASE.md 更新：** §N（具体修改内容）

**覆盖进度更新：**

| 文件路径 | 前状态 | 现状态 | 阅读次数 | 备注 |
|---------|-------|-------|---------|------|
| changed_file.py | 深度完整 | 深度完整 | 2 | SYNC重读：函数签名变更，新增 timeout 参数，失败行为未变 |

**新增 Finding：** [若有]

---

## [收敛确认] YYYY-MM-DD

**收敛依据：** [连续N轮无结构性修改，Coverage 全部深度完整]

**修订旧结论汇总：**
- 第N轮：原认为 X → 确认为 Y

**Quality Gate 最终核查：**

| 检查项 | 结果 |
|--------|------|
| §2 每个具体文件有一行职责注释（无通配符省略） | ✓ / ✗ |
| §3 三层 C4 图有实际 ASCII 框图（非纯文字） | ✓ / ✗ |
| §4 每个源文件有独立 ### 小节（无合并描述） | ✓ / ✗ |
| §5 所有非平凡函数：有代码块签名 + 编号算法步骤 + 精确副作用 | ✓ / ✗ |
| §6 每条 Flow 每一跳独立展开（入参/出参/副作用） | ✓ / ✗ |
| §9 每条风险精确到函数名 + 有触发条件 | ✓ / ✗ |
| Coverage 表每文件备注各不相同且有实质内容 | ✓ / ✗ |
| CODEBASE.md 无覆盖进度表 | ✓ / ✗ |
| ITERATION_LOG 至少一条"修订旧结论" | ✓ / ✗ |
| 每轮均有 A（先声明）+ C（后记录）两段 | ✓ / ✗ |
