# 输出模板：design-dna.md

> 将分析结果按照以下结构输出。所有数值必须具体，不允许出现「适中」「较小」等模糊描述。

---

```markdown
# [产品名] Design DNA
> 分析日期：YYYY-MM-DD
> 目标 URL：https://...
> 分析页面：首页 / 定价页 / Dashboard（列出实际访问的页面）

---

## 一、设计约束语言（直接可用于 AI 提示词）

> 这是整个文档最重要的部分。用自然语言描述这套设计的「神韵」，
> 让任何 AI 读完后都能在正确方向上生成 UI。

[在此填写 3~5 段设计约束语言，例如：]

这套设计押注于「克制的黑暗美学」——背景不是纯黑，而是 #16161a（带极微妙的紫调），
通过这个微妙的色相选择与纯黑区分开来。

整体设计语言的核心矛盾是「高密度信息 × 极低视觉噪音」。
它用 rgba(255,255,255,0.06) 这样几乎看不见的边框来划分区块，
拒绝使用实心分割线，因此在信息密集时依然保持呼吸感。

高级感的主要来源是两点：负字间距（大标题 letter-spacing: -0.03em）和
极细的边框透明度。这两个细节去掉任何一个，整体气质都会下降一档。

设计在动效上极度克制，hover 过渡只有 120ms，没有任何弹性动效，
这种「不表演」的克制本身就是一种高级感的来源。

---

## 二、色彩系统

### 背景层级
| 层级 | 用途 | 色值 |
|------|------|------|
| --bg-base | 页面底层背景 | #16161a |
| --bg-elevated | 卡片/面板 | #1e1e24 |
| --bg-hover | hover 状态背景 | rgba(255,255,255,0.04) |

### 文字层级
| 层级 | 用途 | 色值 |
|------|------|------|
| --text-primary | 主要文字 | #e8e8f0 |
| --text-secondary | 次要文字 | rgba(255,255,255,0.5) |
| --text-tertiary | 辅助说明 | rgba(255,255,255,0.3) |

### 品牌色 / 强调色
| 名称 | 色值 | 用途 |
|------|------|------|
| --accent-primary | #5e6ad2 | 主要 CTA 按钮、链接、选中状态 |
| --accent-glow | rgba(94,106,210,0.15) | 聚焦光晕、卡片高亮边框 |

### 边框
| 名称 | 色值 | 用途 |
|------|------|------|
| --border-subtle | rgba(255,255,255,0.06) | 区块分割 |
| --border-default | rgba(255,255,255,0.12) | 卡片边框 |
| --border-strong | rgba(255,255,255,0.2) | 强调边框、focus 状态 |

---

## 三、字体系统

### 字体选用
- **Display（标题）**：`'Cal Sans', 'Inter', sans-serif`
  - 风格特征：几何无衬线，字形较宽，适合大字号下的视觉锚点
- **Body（正文）**：`'Inter', -apple-system, sans-serif`
- **Mono（代码）**：`'JetBrains Mono', 'Fira Code', monospace`

### 字阶
| 级别 | 字号 | 字重 | letter-spacing | line-height | 用途 |
|------|------|------|---------------|-------------|------|
| Display XL | 56px | 700 | -0.03em | 1.1 | Hero 标题 |
| Display L | 40px | 700 | -0.02em | 1.15 | 页面主标题 |
| Heading | 24px | 600 | -0.01em | 1.3 | 章节标题 |
| Body | 15px | 400 | 0 | 1.6 | 正文 |
| Caption | 12px | 400 | 0.02em | 1.5 | 标签/说明 |

---

## 四、间距与圆角

### 间距单位
基础单位：**8px**

| Token | 值 | 典型用途 |
|-------|----|---------|
| --space-1 | 4px | 图标与文字间距 |
| --space-2 | 8px | 组件内部小间距 |
| --space-3 | 12px | 按钮 padding-y |
| --space-4 | 16px | 卡片内部 padding |
| --space-6 | 24px | 组件间距 |
| --space-8 | 32px | 区块间距 |
| --space-16 | 64px | 大区块 section gap |

### 圆角
| Token | 值 | 用途 |
|-------|----|------|
| --radius-sm | 4px | 标签、badge |
| --radius-md | 8px | 按钮、输入框 |
| --radius-lg | 12px | 卡片、面板 |
| --radius-xl | 16px | 大卡片、模态框 |

---

## 五、阴影与层次

```css
/* 卡片阴影（极克制） */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
--shadow-md: 0 4px 12px rgba(0,0,0,0.4);

/* 高亮边框代替阴影表达层级 */
--shadow-highlight: inset 0 1px 0 rgba(255,255,255,0.08);
```

---

## 六、动效规范

```css
/* 标准过渡（hover 状态切换） */
--transition-fast: 120ms ease;
--transition-base: 200ms ease;

/* 典型用法 */
.button { transition: background-color var(--transition-fast), border-color var(--transition-fast); }
.card   { transition: transform var(--transition-base), box-shadow var(--transition-base); }

/* hover 时卡片微微上移 */
.card:hover { transform: translateY(-2px); }
```

---

## 七、CSS Variables 完整代码块

> 直接复制到项目 `:root` 或 `[data-theme="dark"]` 下使用。

```css
:root {
  /* 背景 */
  --bg-base:     #16161a;
  --bg-elevated: #1e1e24;
  --bg-hover:    rgba(255, 255, 255, 0.04);

  /* 文字 */
  --text-primary:   #e8e8f0;
  --text-secondary: rgba(255, 255, 255, 0.5);
  --text-tertiary:  rgba(255, 255, 255, 0.3);

  /* 品牌色 */
  --accent:      #5e6ad2;
  --accent-glow: rgba(94, 106, 210, 0.15);

  /* 边框 */
  --border-subtle:  rgba(255, 255, 255, 0.06);
  --border-default: rgba(255, 255, 255, 0.12);
  --border-strong:  rgba(255, 255, 255, 0.20);

  /* 字体 */
  --font-display: 'Cal Sans', 'Inter', sans-serif;
  --font-body:    'Inter', -apple-system, sans-serif;
  --font-mono:    'JetBrains Mono', monospace;

  /* 间距 */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-6:  24px;
  --space-8:  32px;
  --space-16: 64px;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);

  /* 动效 */
  --transition-fast: 120ms ease;
  --transition-base: 200ms ease;
}
```

---

## 八、设计哲学总结（一段话版本）

> 这段话是最终的「设计 DNA 密码」，拿去告诉任何 AI，它能复现 70% 的神韵。

[填写在此]

---

## 九、「反直觉」设计决策记录

> 记录这个产品里「违反常规」但效果出色的设计选择，是学习价值最高的部分。

1. **[决策名称]**：[具体描述这个违反直觉的选择，以及为什么有效]
2. ...
```
