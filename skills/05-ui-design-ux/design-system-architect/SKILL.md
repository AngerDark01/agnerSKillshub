---
name: design-system-architect
description: "Designs and audits design system foundations: design tokens (color, spacing, typography, shadow), component APIs, and theming architecture. Use when building a new design system, auditing an existing one for consistency, or planning a migration from hardcoded styles to tokens. Triggers: \"design system\", \"design tokens\", \"theming\", \"audit our styles\", \"build a component library\", \"spacing system\", \"typography scale\"."
---

# Design System Architect

Designs the foundational layer of a design system: tokens, scales, component contracts, and theming strategy. A well-designed design system is invisible to users but makes every future component faster and more consistent to build.

**Announce at start:** "I'm using the design-system-architect skill."

---

## The Three Layers

Every design system has three layers. Address them in order:

```
Layer 1: Tokens      — The raw values (primitives)
Layer 2: Semantics   — Named for purpose, not appearance
Layer 3: Components  — Built from semantic tokens
```

Never build components that reference primitive tokens directly. Always go through semantic tokens.

---

## Layer 1: Primitive Tokens (Design DNA)

### Color Primitives

Define a numbered scale for each hue (avoid semantic names here):

```css
:root {
  /* Gray scale */
  --gray-0:   #ffffff;
  --gray-50:  #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --gray-950: #030712;

  /* Brand — derive from your brand color */
  --brand-50:  #eff6ff;
  --brand-100: #dbeafe;
  /* ... 200 through 950 */
  --brand-600: #2563eb;  /* primary action */
  --brand-700: #1d4ed8;  /* hover */

  /* Semantic hues */
  --red-500: #ef4444;
  --green-500: #22c55e;
  --yellow-500: #eab308;
}
```

### Spacing Scale

Use a base-4 or base-8 system (never arbitrary values):

```css
:root {
  --space-0:  0;
  --space-1:  4px;   /* 0.25rem */
  --space-2:  8px;   /* 0.5rem  */
  --space-3:  12px;  /* 0.75rem */
  --space-4:  16px;  /* 1rem    */
  --space-5:  20px;  /* 1.25rem */
  --space-6:  24px;  /* 1.5rem  */
  --space-8:  32px;  /* 2rem    */
  --space-10: 40px;  /* 2.5rem  */
  --space-12: 48px;  /* 3rem    */
  --space-16: 64px;  /* 4rem    */
  --space-20: 80px;  /* 5rem    */
  --space-24: 96px;  /* 6rem    */
}
```

### Typography Scale

Modular scale (ratio 1.25 = Major Third, or 1.333 = Perfect Fourth):

```css
:root {
  /* Size scale */
  --text-xs:   0.75rem;   /* 12px */
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  1.875rem;  /* 30px */
  --text-4xl:  2.25rem;   /* 36px */
  --text-5xl:  3rem;      /* 48px */

  /* Weight */
  --font-normal:   400;
  --font-medium:   500;
  --font-semibold: 600;
  --font-bold:     700;

  /* Line height */
  --leading-tight:  1.25;
  --leading-snug:   1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;

  /* Families */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

### Border Radius + Shadow

```css
:root {
  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-xl:   16px;
  --radius-2xl:  24px;
  --radius-full: 9999px;

  --shadow-sm:  0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl:  0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}
```

---

## Layer 2: Semantic Tokens

Named for purpose, reference primitives:

```css
:root {
  /* Backgrounds */
  --color-bg:           var(--gray-0);
  --color-bg-subtle:    var(--gray-50);
  --color-bg-muted:     var(--gray-100);

  /* Surfaces (cards, panels) */
  --color-surface:      var(--gray-0);
  --color-surface-raised: var(--gray-50);

  /* Text */
  --color-text:         var(--gray-900);
  --color-text-muted:   var(--gray-500);
  --color-text-subtle:  var(--gray-400);
  --color-text-on-fill: var(--gray-0);

  /* Borders */
  --color-border:       var(--gray-200);
  --color-border-strong: var(--gray-400);

  /* Actions */
  --color-action:       var(--brand-600);
  --color-action-hover: var(--brand-700);
  --color-action-text:  var(--gray-0);

  /* States */
  --color-error:        var(--red-500);
  --color-success:      var(--green-500);
  --color-warning:      var(--yellow-500);

  /* Focus ring */
  --color-focus-ring:   var(--brand-600);

  /* Spacing aliases (optional) */
  --spacing-page-x:     var(--space-6);
  --spacing-card:       var(--space-5);
  --spacing-section:    var(--space-16);
}

/* Dark mode: only semantic tokens change, primitives stay */
[data-theme="dark"] {
  --color-bg:           var(--gray-950);
  --color-bg-subtle:    var(--gray-900);
  --color-surface:      var(--gray-900);
  --color-text:         var(--gray-50);
  --color-text-muted:   var(--gray-400);
  --color-border:       var(--gray-800);
}
```

---

## Layer 3: Component Contract Design

For each component, define the API before implementation:

```typescript
// Button contract example
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'destructive'
type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps {
  variant?: ButtonVariant   // default: 'primary'
  size?: ButtonSize         // default: 'md'
  loading?: boolean         // shows spinner, disables interaction
  disabled?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  fullWidth?: boolean
  // NOT: color, backgroundColor, fontSize — use variants instead
}
```

**Rules for component APIs:**
- Prefer `variant` over direct style props — keeps system consistent
- Boolean props for binary states (`disabled`, `loading`, `fullWidth`)
- Never accept raw color values — only semantic token names
- Document the "why" for each variant (when to use primary vs secondary)

---

## Audit Checklist

When auditing an existing codebase for design system consistency:

```
□ No hardcoded hex colors (grep for #[0-9a-fA-F]{3,6})
□ No hardcoded pixel spacing (grep for [0-9]+px outside of 0px)
□ No hardcoded font sizes
□ All colors reference semantic tokens
□ Dark mode works by switching token layer only
□ Typography follows defined scale (no arbitrary sizes)
□ Spacing between components uses scale values
□ All interactive elements have focus styles
□ Components accept only documented props
```

---

## Deliverables

1. **Token file** — Complete CSS custom properties (or JSON for Style Dictionary / Tokens Studio)
2. **Semantic token map** — Table mapping each semantic token to its primitive
3. **Component API specs** — TypeScript interfaces for each component
4. **Theming strategy** — How dark mode / brand customization works
5. **Migration plan** — Steps to move from hardcoded styles to tokens

---

*Sources: Tailwind CSS token approach, Radix UI design primitives, Style Dictionary spec, Material Design 3 token system*
