# DOCX 打包与解包

规范代码位置：

- `scripts/docx/pack_tools.py`
- `scripts/office/`

当 `.docx` 需要解包为可编辑的 XML 工作目录，或在编辑完成后重新打包为可交付文件时，使用这个流程文档。

核心调用：

```python
from scripts.docx.pack_tools import unpack, pack
```

规则：

1. `scripts/office/` 是这一能力的运行时支持层，不是独立技能。
2. 一次任务通常只解包一次，后续由其他流程文档在同一个 `unpacked/` 目录上继续工作。
3. 只有在编辑完成后才执行 `pack`，且在条件允许时始终传入 `original`。
