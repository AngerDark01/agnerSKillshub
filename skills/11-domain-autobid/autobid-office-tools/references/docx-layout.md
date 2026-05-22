# DOCX 版式处理

规范代码位置：

- `scripts/docx/layout_tools.py`

当需要检查或统一 section 版式、页边距、页码、页眉页脚或 logo 资源时，使用这个流程文档。

核心调用：

```python
from scripts.docx.layout_tools import (
    inspect_sections,
    copy_section_layout,
    copy_header_footer_template,
    set_section_layout,
)
```

规则：

1. 这一流程文档只操作 `unpacked/` 目录，不直接处理原始 `.docx` 文件。
2. 版式复制与页眉页脚复制是两类独立操作，不能混为一体。
3. 工具只执行已经决定好的版式参数，不替代业务规则判断。
