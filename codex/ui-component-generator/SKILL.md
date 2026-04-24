---
name: ui-component-generator
description: "Generates production-grade, distinctive UI components for React or Vue with exceptional aesthetic quality. Avoids generic AI design patterns. Use when building web components, landing pages, dashboards, UI elements, or any frontend interface. Triggers: \"build this component\", \"create a UI for\", \"generate the frontend\", \"design this page\", \"make a landing page\", \"build a dashboard\", \"create this form\"."
---

# UI Component Generator

Generates distinctive, production-grade UI components that avoid generic "AI slop" aesthetics. Every component is built with intentional design direction, not default patterns.

**Announce at start:** "I'm using the ui-component-generator skill."

---

## Before Writing Any Code

Commit to a **BOLD aesthetic direction** before writing a single line:

1. **Purpose**: What problem does this solve? Who uses it?
2. **Tone**: Choose an extreme and own it:
   - Brutally minimal / editorial / typographic
   - Maximalist / layered / atmospheric
   - Retro-futuristic / terminal / tech-noir
   - Organic / natural / soft
   - Luxury / refined / Swiss grid
   - Playful / toy-like / expressive
   - Brutalist / raw / unconventional
3. **Differentiation**: What makes this unforgettable? What's the one detail someone remembers?
4. **Constraints**: Framework (React/Vue), CSS approach (Tailwind/CSS-in-JS/modules), accessibility requirements

**CRITICAL**: Commit to one direction and execute it with precision. Do not hedge toward safe defaults.

---

## Design Guidelines

### Typography (High Impact)
- Choose fonts that are **distinctive and characterful**
- Pair a display font with a refined body font
- **Avoid overused AI defaults:** Inter, Roboto, Arial, system-ui as the primary font
- Good alternatives: Instrument Serif, Cabinet Grotesk, Satoshi, Clash Display, Syne, Outfit, Plus Jakarta Sans
- Use font size/weight contrast boldly — don't make everything the same size

### Color & Atmosphere
- Commit to a **dominant color** with sharp accents
- Timid, even-distribution palettes are forgettable
- Use CSS custom properties for all colors
- Create atmosphere: gradient meshes, noise textures, layered transparencies, grain overlays
- **Avoid:** purple-gradient-on-white, generic blue CTAs, cookie-cutter neutral palettes

### Motion
- High-impact moments: page load staggered reveal, scroll-triggered entrance, hover state surprise
- Use `animation-delay` for staggered sequences
- `transform` and `opacity` only (never animate layout-triggering properties)
- Always include `@media (prefers-reduced-motion: reduce)` reset

### Spatial Composition
- **Be unexpected:** asymmetry, overlap, diagonal flow, grid-breaking elements
- Generous negative space OR controlled density — not timid in-between
- Visual hierarchy must be clear at a glance

---

## React Component Template

```tsx
// Component with design tokens, accessibility, and animation
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion' // optional

interface [ComponentName]Props {
  // Type all props explicitly
  variant?: 'default' | 'prominent' | 'subtle'
  // ...
}

export function [ComponentName]({ variant = 'default', ...props }: [ComponentName]Props) {
  return (
    <div
      className={styles.root}
      data-variant={variant}
      role="..."      // appropriate ARIA role
      aria-label="..."
    >
      {/* Content */}
    </div>
  )
}
```

**CSS Module pattern:**
```css
.root {
  /* Use semantic tokens, not raw values */
  color: var(--color-text);
  background: var(--color-surface);
  padding: var(--space-5) var(--space-6);
  border-radius: var(--radius-lg);
}

.root[data-variant="prominent"] {
  background: var(--color-action);
  color: var(--color-action-text);
}
```

---

## Production Checklist

Before delivering any component:

**Functionality**
- [ ] Works without JavaScript (progressive enhancement where applicable)
- [ ] Handles empty states
- [ ] Handles loading states
- [ ] Handles error states
- [ ] Handles long/overflow content

**Accessibility**
- [ ] Keyboard navigable (Tab, Enter, Escape, Arrow keys where appropriate)
- [ ] Visible focus indicator
- [ ] Correct ARIA roles and attributes
- [ ] Color is not the only information carrier
- [ ] Minimum 44×44px touch targets on mobile

**Aesthetics**
- [ ] No hardcoded colors (uses CSS variables)
- [ ] No generic font choices without justification
- [ ] Consistent with stated aesthetic direction
- [ ] Dark mode tested (if applicable)
- [ ] Responsive across 375px, 768px, 1280px

**Code Quality**
- [ ] No inline styles (except truly dynamic values)
- [ ] Props are typed
- [ ] No magic numbers — spacing from scale
- [ ] Animations respect `prefers-reduced-motion`

---

## Common Component Patterns

### Card
```tsx
// Elevated card with hover interaction
<article className={styles.card} tabIndex={0}>
  <header className={styles.cardHeader}>{/* ... */}</header>
  <div className={styles.cardBody}>{/* ... */}</div>
  <footer className={styles.cardFooter}>{/* ... */}</footer>
</article>
```

### Form Field
Always pair label + input + error message:
```tsx
<div className={styles.field}>
  <label htmlFor={id} className={styles.label}>{label}</label>
  <input
    id={id}
    aria-describedby={error ? `${id}-error` : undefined}
    aria-invalid={!!error}
    className={clsx(styles.input, error && styles.inputError)}
  />
  {error && (
    <p id={`${id}-error`} role="alert" className={styles.errorMessage}>
      {error}
    </p>
  )}
</div>
```

### Button
```tsx
<button
  type={type}
  disabled={disabled || loading}
  aria-disabled={disabled || loading}
  aria-busy={loading}
  className={clsx(styles.button, styles[variant], styles[size])}
>
  {loading && <Spinner aria-hidden />}
  <span>{children}</span>
</button>
```

---

## Tech Stack by Context

| Context | Preferred Stack |
|---|---|
| Claude.ai artifacts | React 18 + TypeScript + Tailwind + shadcn/ui |
| Next.js app | React 18 + TypeScript + Tailwind CSS modules |
| Vite SPA | React 18 + TypeScript + CSS modules |
| Plain HTML | Vanilla HTML/CSS/JS (no framework) |
| Vue project | Vue 3 + TypeScript + CSS modules |

---

*Sources: Anthropic frontend-design skill, Vercel AGENTS.md, shadcn/ui patterns, WCAG 2.1*
