---
name: ui-style-analyst
description: 深度分析任意产品/网站的 UI 设计风格，控制真实 Chrome 浏览器多维度采集，提炼设计 DNA，输出可直接复用的 design-dna.md。当用户说「分析 XX 的设计风格」「帮我借鉴 XX 的 UI」「我想做成 Linear/Notion/Stripe 那种感觉」「学习某个产品的设计」「提取某个网站的设计语言」时立即触发。不要让用户手动截图或复制 CSS。
---

# UI Style Analyst

像资深设计师一样系统拆解一个产品的设计风格，沉淀成可复用的设计知识。

## 前置检查

```bash
skills/chrome-cdp/scripts/cdp list
```

如果报错，先执行 **chrome-cdp-setup** skill 完成初始化。

---

## 工作流程

### 第一阶段：定位目标

```bash
# 列出所有标签页，找到目标产品
skills/chrome-cdp/scripts/cdp list
```

记录目标标签页的 `targetId` 前缀（后续用 `<T>` 代替）。

如果目标页面未打开：

```bash
skills/chrome-cdp/scripts/cdp open https://目标网站.com
# 等待页面加载，Chrome 弹框点「允许」，再 list 确认新 targetId
skills/chrome-cdp/scripts/cdp list
```

---

### 第二阶段：系统采集

按顺序执行，**不要跳步骤**。

#### 2.1 首屏采集

```bash
# 截图
skills/chrome-cdp/scripts/cdp shot <T> /tmp/ui-shot-home.png

# 语义结构（优先用 snap，比 html 精简）
skills/chrome-cdp/scripts/cdp snap <T>

# 提取所有 CSS 自定义变量（设计 token）
skills/chrome-cdp/scripts/cdp eval <T> "JSON.stringify(
  Array.from(document.styleSheets)
    .flatMap(s => { try { return Array.from(s.cssRules) } catch(e) { return [] } })
    .flatMap(r => r.cssText ? [r.cssText] : [])
    .join(' ')
    .match(/--[\\w-]+:\\s*[^;]+/g) || []
)"

# 关键元素计算样式
skills/chrome-cdp/scripts/cdp eval <T> "
const els = ['body','h1','h2','p','a','button','nav','header'];
const result = {};
els.forEach(sel => {
  const el = document.querySelector(sel);
  if (!el) return;
  const s = getComputedStyle(el);
  result[sel] = {
    bg: s.backgroundColor, color: s.color,
    font: s.fontFamily, fontSize: s.fontSize, fontWeight: s.fontWeight,
    borderRadius: s.borderRadius, boxShadow: s.boxShadow,
    letterSpacing: s.letterSpacing, lineHeight: s.lineHeight
  };
});
JSON.stringify(result, null, 2)"
```

#### 2.2 滚动探索

```bash
# 滚动到中部截图
skills/chrome-cdp/scripts/cdp eval <T> 'window.scrollTo(0, document.body.scrollHeight * 0.4)'
skills/chrome-cdp/scripts/cdp shot <T> /tmp/ui-shot-mid.png

# 滚动到底部截图
skills/chrome-cdp/scripts/cdp eval <T> 'window.scrollTo(0, document.body.scrollHeight)'
skills/chrome-cdp/scripts/cdp shot <T> /tmp/ui-shot-bottom.png

# 回顶部
skills/chrome-cdp/scripts/cdp eval <T> 'window.scrollTo(0, 0)'
```

#### 2.3 探索关键子页面

```bash
# 功能页
skills/chrome-cdp/scripts/cdp nav <T> https://目标.com/features
skills/chrome-cdp/scripts/cdp shot <T> /tmp/ui-shot-features.png

# 定价页（设计语言最集中的地方）
skills/chrome-cdp/scripts/cdp nav <T> https://目标.com/pricing
skills/chrome-cdp/scripts/cdp shot <T> /tmp/ui-shot-pricing.png

# 登录后 Dashboard（如果已登录）
skills/chrome-cdp/scripts/cdp nav <T> https://目标.com/dashboard
skills/chrome-cdp/scripts/cdp shot <T> /tmp/ui-shot-dashboard.png
```

找不到的页面跳过，根据实际 URL 结构灵活调整。

#### 2.4 深层 token 提取

回首页后执行：

```bash
skills/chrome-cdp/scripts/cdp nav <T> https://目标.com
skills/chrome-cdp/scripts/cdp eval <T> "
const tokens = { colors: new Set(), fonts: new Set(), radii: new Set(), shadows: new Set(), transitions: new Set() };
document.querySelectorAll('*').forEach(el => {
  const s = getComputedStyle(el);
  if (s.backgroundColor !== 'rgba(0, 0, 0, 0)') tokens.colors.add(s.backgroundColor);
  if (s.color) tokens.colors.add(s.color);
  if (s.fontFamily) tokens.fonts.add(s.fontFamily.split(',')[0].trim());
  if (s.borderRadius && s.borderRadius !== '0px') tokens.radii.add(s.borderRadius);
  if (s.boxShadow && s.boxShadow !== 'none') tokens.shadows.add(s.boxShadow);
  if (s.transition && s.transition !== 'all 0s ease 0s') tokens.transitions.add(s.transition);
});
JSON.stringify({
  colors: [...tokens.colors].slice(0, 30),
  fonts: [...tokens.fonts],
  radii: [...tokens.radii].slice(0, 10),
  shadows: [...tokens.shadows].slice(0, 5),
  transitions: [...tokens.transitions].slice(0, 5)
}, null, 2)"
```

---

### 第三阶段：专业分析

> 读取 `skills/ui-style-analyst/references/analysis-framework.md`，按照其中七个维度逐项分析。

基于所有截图和 token 数据填写每个维度。**禁止写「简洁」「现代」「大气」等空泛词**，每条必须有具体数值或可引用描述支撑。

---

### 第四阶段：输出

将分析结果写入 `design-dna.md`，格式见 `skills/ui-style-analyst/references/output-template.md`。

输出必须满足：
- 色值写具体 hex 或 rgb
- 字体写完整 font-family 字符串
- 包含「设计约束语言」段落（可直接粘贴给 AI 作为 prompt）
- 包含可直接使用的 CSS variables 代码块

---

## 参考文件

- `skills/ui-style-analyst/references/analysis-framework.md` — 七维度分析框架（第三阶段必读）
- `skills/ui-style-analyst/references/output-template.md` — 输出格式模板（第四阶段必读）
