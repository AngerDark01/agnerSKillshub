---
name: chrome-cdp
description: 控制本地 Chrome 浏览器（截图、点击、输入、执行 JS、提取 CSS）。需要用户明确要求操作 Chrome 时触发。依赖 chrome-cdp-setup 完成首次配置。
---

# Chrome CDP

通过 Chrome DevTools Protocol 直接控制本地 Chrome 浏览器，无需 Puppeteer，支持 100+ 标签页，保留用户登录态。

## 前置检查

使用前确认 chrome-cdp 环境已就绪：

```bash
skills/chrome-cdp/scripts/cdp list
```

如果报错，执行 chrome-cdp-setup skill 完成初始化。

---

## 命令参考

所有命令格式：`skills/chrome-cdp/scripts/cdp <命令> [参数]`

`<T>` = 目标标签页 targetId 前缀（从 `list` 输出中复制，≥8位）

### 基础操作

```bash
# 列出所有标签页（每次操作前先执行，确认 targetId）
skills/chrome-cdp/scripts/cdp list

# 截图（仅截可视区域）
skills/chrome-cdp/scripts/cdp shot <T>              # 保存到默认路径
skills/chrome-cdp/scripts/cdp shot <T> /tmp/out.png  # 指定路径

# 语义结构快照（比 html 命令更精简，优先用这个）
skills/chrome-cdp/scripts/cdp snap <T>

# 执行 JS 并返回结果
skills/chrome-cdp/scripts/cdp eval <T> 'document.title'
```

### 导航与交互

```bash
# 导航到 URL（等待页面加载完成）
skills/chrome-cdp/scripts/cdp nav <T> https://example.com

# 点击元素（CSS 选择器）
skills/chrome-cdp/scripts/cdp click <T> 'button[type=submit]'

# 点击坐标（CSS 像素，截图坐标 ÷ DPR）
skills/chrome-cdp/scripts/cdp clickxy <T> 320 240

# 输入文字（先 click 聚焦，再 type；跨域 iframe 也能用）
skills/chrome-cdp/scripts/cdp type <T> "要输入的文字"

# 打开新标签页
skills/chrome-cdp/scripts/cdp open https://example.com
```

### 数据提取

```bash
# 提取 HTML（整页或指定选择器）
skills/chrome-cdp/scripts/cdp html <T>
skills/chrome-cdp/scripts/cdp html <T> '.main-content'

# 网络性能数据
skills/chrome-cdp/scripts/cdp net <T>
```

### 滚动（通过 eval 实现）

```bash
skills/chrome-cdp/scripts/cdp eval <T> 'window.scrollTo(0, document.body.scrollHeight * 0.5)'
skills/chrome-cdp/scripts/cdp eval <T> 'window.scrollTo(0, document.body.scrollHeight)'
```

---

## 坐标换算

截图以设备原始分辨率保存（图片像素 = CSS 像素 × DPR）。

`shot` 命令会打印当前页面 DPR，点击时使用：
```
CSS 像素 = 截图像素 ÷ DPR
```

## 注意事项

- `list` 输出的 targetId 前缀至少用 8 位，避免歧义
- 新标签页首次访问会弹「允许调试？」弹框，需要用户在 Chrome 里点允许
- daemon 20 分钟无活动自动退出，之后首次命令会重新触发弹框
- 避免在 DOM 可能变化的情况下跨多个 `eval` 用下标选元素，应在单次 `eval` 中收集所有数据
