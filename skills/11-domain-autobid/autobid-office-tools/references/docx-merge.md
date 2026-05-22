# DOCX 合并

规范代码位置：

- `scripts/docx/merge_tools.py`

当需要把一个已解包 DOCX 的 body 内容追加到另一个已解包 DOCX 中，并保留关系、媒体资源和内嵌引用时，使用这个流程文档。

核心调用：

```python
from scripts.docx.merge_tools import append_body_from_unpacked
```

规则：

1. 调用前必须先确定语义顺序，工具本身不负责判断章节先后。
2. 这个工具用于 `unpacked/` 层的 body 拼接。
3. 如果任务是整份文档按范围拆分或按清单重组，应使用 `docx-split` 流程文档。
