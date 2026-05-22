/**
 * CSS Injector — 注入到目标页面，提取设计 token
 * 被 extract.py 通过 page.evaluate() 调用
 */
(() => {
  const result = {
    cssVariables: {},
    computedStyles: {},
    typography: {},
    spacing: {},
    colors: [],
    borderRadius: {},
    shadows: {},
    transitions: {},
    meta: {
      url: window.location.href,
      title: document.title,
      timestamp: new Date().toISOString(),
    },
  };

  // ── 1. CSS Variables（设计系统的核心 token）──────────────────────
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.style) {
          for (const prop of rule.style) {
            if (prop.startsWith('--')) {
              result.cssVariables[prop] = rule.style.getPropertyValue(prop).trim();
            }
          }
        }
      }
    } catch (e) {
      // cross-origin stylesheet，跳过
    }
  }

  // ── 2. 关键元素的计算样式 ─────────────────────────────────────────
  const targets = {
    body: 'body',
    heading1: 'h1',
    heading2: 'h2',
    heading3: 'h3',
    paragraph: 'p',
    primaryButton: 'button, [class*="btn-primary"], [class*="button-primary"]',
    secondaryButton: '[class*="btn-secondary"], [class*="button-secondary"]',
    link: 'a',
    nav: 'nav',
    header: 'header',
    card: '[class*="card"], [class*="Card"]',
    input: 'input[type="text"], input[type="email"]',
    badge: '[class*="badge"], [class*="tag"], [class*="chip"]',
  };

  for (const [name, selector] of Object.entries(targets)) {
    const el = document.querySelector(selector);
    if (!el) continue;
    const cs = window.getComputedStyle(el);
    result.computedStyles[name] = {
      fontFamily: cs.fontFamily,
      fontSize: cs.fontSize,
      fontWeight: cs.fontWeight,
      lineHeight: cs.lineHeight,
      letterSpacing: cs.letterSpacing,
      color: cs.color,
      backgroundColor: cs.backgroundColor,
      borderRadius: cs.borderRadius,
      border: cs.border,
      boxShadow: cs.boxShadow,
      padding: cs.padding,
      margin: cs.margin,
      transition: cs.transition,
    };
  }

  // ── 3. 字体族收集 ─────────────────────────────────────────────────
  const fontSet = new Set();
  document.querySelectorAll('*').forEach(el => {
    const ff = window.getComputedStyle(el).fontFamily;
    if (ff) fontSet.add(ff);
  });
  result.typography.fontFamilies = [...fontSet].slice(0, 10);

  // ── 4. 颜色采样（从高频元素收集不重复的色值）──────────────────────
  const colorSet = new Set();
  document.querySelectorAll('h1,h2,h3,p,button,a,nav,header,[class*="btn"]').forEach(el => {
    const cs = window.getComputedStyle(el);
    [cs.color, cs.backgroundColor, cs.borderColor].forEach(c => {
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') colorSet.add(c);
    });
  });
  result.colors = [...colorSet].slice(0, 30);

  // ── 5. 圆角收集 ───────────────────────────────────────────────────
  const radiusSet = new Set();
  document.querySelectorAll('button,[class*="card"],[class*="modal"],input,img').forEach(el => {
    const r = window.getComputedStyle(el).borderRadius;
    if (r && r !== '0px') radiusSet.add(r);
  });
  result.borderRadius.values = [...radiusSet];

  // ── 6. 阴影收集 ───────────────────────────────────────────────────
  const shadowSet = new Set();
  document.querySelectorAll('[class*="card"],[class*="modal"],[class*="dropdown"],button').forEach(el => {
    const s = window.getComputedStyle(el).boxShadow;
    if (s && s !== 'none') shadowSet.add(s);
  });
  result.shadows.values = [...shadowSet];

  return JSON.stringify(result, null, 2);
})();
