---
name: microinteraction-designer
description: "Designs and implements micro-interactions: hover effects, loading states, transitions, animations, and feedback moments that make interfaces feel alive and responsive. Use when polishing UI components, adding motion to interactions, or making a UI feel more delightful. Triggers: \"add animations\", \"make it feel more alive\", \"loading states\", \"hover effects\", \"transition between states\", \"micro-interactions\", \"animate this\"."
---

# Microinteraction Designer

Designs and implements the small, purposeful animations and state transitions that separate polished UIs from flat ones. Every interaction should provide feedback; every state change should be perceivable.

**Announce at start:** "I'm using the microinteraction-designer skill."

---

## The Four Parts of Every Microinteraction

Every microinteraction has: **Trigger → Rules → Feedback → Loops/Modes**

1. **Trigger** — What initiates it? (user action, system event, condition)
2. **Rules** — What happens? (exactly one defined behavior)
3. **Feedback** — What does the user perceive? (visual, motion, sometimes sound)
4. **Loops/Modes** — Does it repeat? Does it change over time?

Always design all four before writing any code.

---

## Interaction Catalog

### Loading States

**Skeleton screens** (preferred over spinners for content):
```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**Button loading state:**
- Disable the button immediately on click (prevent double-submit)
- Replace label with spinner + "Loading..."
- Maintain button dimensions (no layout shift)
- Restore original state on completion/error

**Progressive loading:**
- Show partial content as it arrives
- Prioritize above-the-fold content
- Blur-in or fade-in loaded sections

### Hover Effects

**Principles:**
- Duration: 150-250ms for hover in, slightly longer (200-300ms) for hover out
- Use `cubic-bezier(0.4, 0, 0.2, 1)` (material ease) or `ease-out` for most interactions
- Hover feedback must be immediate (never delay the start)
- Never animate layout-triggering properties (width, height, top, left) — use transform instead

**Card hover:**
```css
.card {
  transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}
```

**Button hover:**
```css
.btn {
  transition: background-color 150ms ease-out, transform 100ms ease-out;
}
.btn:hover { background-color: var(--color-primary-hover); }
.btn:active { transform: scale(0.97); }
```

### State Transitions

**Appear/Disappear (modals, toasts, dropdowns):**
- In: fade + translate (move toward final position)
- Out: fade only (or reverse of in) — shorter duration
- Always use `visibility` + `opacity` together (not `display: none` which can't be animated)

```css
.modal {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}
.modal.visible {
  opacity: 1;
  transform: translateY(0) scale(1);
}
```

**Tab/Page transitions:**
- Slide in from direction of navigation (forward = right→left, back = left→right)
- Cross-fade for unrelated context switches
- Duration: 250-350ms

**Form field states:**
```css
/* Focus */
.input { transition: border-color 150ms, box-shadow 150ms; }
.input:focus { border-color: var(--color-focus); box-shadow: 0 0 0 3px var(--color-focus-ring); }

/* Error shake */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}
.input.error { animation: shake 400ms ease-in-out; }
```

### Feedback Moments

**Success confirmation:**
- Checkmark draw animation (SVG stroke-dashoffset)
- Color transition to success green
- Brief scale pulse: scale(1) → scale(1.08) → scale(1) over 300ms

**Error feedback:**
- Shake animation on the offending field
- Color transition to error red
- Keep error message stable (don't animate it in aggressively)

**Scroll progress:**
- Thin progress bar at top (2-3px) — pure CSS with `animation-timeline: scroll()`
- Or sticky header that changes appearance on scroll

---

## Motion Principles

**Use GPU-accelerated properties only:**
- `transform` (translate, scale, rotate)
- `opacity`
- `filter` (blur, brightness) — with care on mobile

**Avoid animating:** `width`, `height`, `top`, `left`, `margin`, `padding` — these cause layout recalculation.

**Timing guidelines:**
| Interaction | Duration |
|---|---|
| Hover feedback | 100-150ms |
| Button press | 80-120ms |
| Appear/disappear | 150-250ms |
| Page transition | 250-350ms |
| Choreographed sequence | 400-600ms |
| Attention-getting | 500-800ms |

**Stagger for lists:**
```css
.item:nth-child(1) { animation-delay: 0ms; }
.item:nth-child(2) { animation-delay: 60ms; }
.item:nth-child(3) { animation-delay: 120ms; }
/* etc. — cap stagger at ~50ms per item */
```

---

## Accessibility

- Always respect `prefers-reduced-motion`:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
- Never use animation as the *only* way to communicate state change (color + text still required)
- Looping animations must be pausable

---

## React / Framer Motion

For complex sequences, use Framer Motion:
```tsx
import { motion, AnimatePresence } from 'framer-motion'

// Appear/disappear
<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.2 }}
    />
  )}
</AnimatePresence>

// Staggered list
const container = { animate: { transition: { staggerChildren: 0.06 } } }
const item = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 } }
```

---

*Sources: Dan Saffer "Microinteractions", Framer Motion docs, Web Animations API spec*
