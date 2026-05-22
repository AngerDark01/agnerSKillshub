# Mode: group_assembled

## 适用场景

- 多个子章节同属于一个 `group_node`。
- 最终交付时这些子章节应连续出现并作为一个大章节维护。

常见章节：`投标保证金组`、`补充文件组`、`技术评分点分组章节`。

## 必读工具

- 按 manifest 拼接：`../../../autobid-office-tools/references/docx-split.md`
- 带媒体关系合并：`../../../autobid-office-tools/references/docx-merge.md`
- 打包校验：`../../../autobid-office-tools/references/docx-pack.md`

## 标准动作

1. 若当前代理拿到的是整个 `group_node`，先把子章节拆给 child worker；自己只保留父级顺序和组装职责。
2. 先分别完成各个子章节。
3. 同组保留节点按 `输出章节模板` 连续重排子编号。
4. 由大章节文件统一处理父级标题、顺序和最终拼接。
5. 如子章节含图片或扫描件，执行关系级合并。

## 特殊规则

- 父级标题只在 `group_final` 中出现一次。
- `group_assembled` 常常对应一个章节组 manager，而不是一个单独执行整组内容的 worker。
- 子章节顺序确定后，编号也按保留顺序重排，不沿用被删除后的旧编号。
- 带媒体内容时，不能只拼 body，必须复制关系和媒体文件。
- 这类模式特别适合 `信息表 + 贴图证明`、`正文说明 + 扫描件附件` 的混合章节。

## Done 条件

- 每个 child partial 均为 `done` 或有明确删除/留空理由。
- 父级标题只出现一次。
- 子章节顺序和编号已按输出模板重排。
- 最终 group 文件完成关系级合并并通过校验。
