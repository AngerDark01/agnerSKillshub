---
name: frontend-code-reviewer
description: "Reviews frontend code (React/Vue/HTML/CSS) for code quality, accessibility compliance, performance anti-patterns, and UX issues. Produces categorized findings with specific fixes. Triggers: \"review this frontend code\", \"check this component\", \"accessibility audit\", \"review my CSS\", \"check this React code\", \"code review\", \"frontend review\"."
---

# Frontend Code Reviewer

Systematic review of frontend code against quality, accessibility, performance, and UX standards. Every finding is specific (file:line), categorized by severity, and includes an actionable fix.

**Announce at start:** "I'm using the frontend-code-reviewer skill."

---

## Review Dimensions

### 1. Accessibility (WCAG 2.1 AA)

**Semantic HTML:**
```
❌ <div onClick={handleClick}>Submit</div>
✅ <button type="button" onClick={handleClick}>Submit</button>

❌ <div className="heading">Title</div>
✅ <h2>Title</h2>

❌ <img src="logo.png" />
✅ <img src="logo.png" alt="Company logo" />
   <img src="decorative.png" alt="" role="presentation" />
```

**Keyboard navigation:**
- Every interactive element reachable via Tab
- Logical tab order (matches visual order)
- `Escape` closes modals/dropdowns
- `Enter`/`Space` activates buttons
- Arrow keys navigate lists/menus

**ARIA:**
- Don't add ARIA when native HTML semantics suffice
- Required: `aria-label` on icon buttons, `aria-expanded` on disclosure widgets, `role="alert"` on live error messages
- `aria-describedby` to associate help text with inputs
- `aria-invalid="true"` on invalid form fields

**Color and contrast:**
- Text: 4.5:1 minimum (AA) / 7:1 (AAA)
- Large text (≥ 18pt normal / ≥ 14pt bold): 3:1 minimum
- UI components and focus indicators: 3:1 minimum
- Never use color as the **only** differentiator

**Forms:**
```
❌ <input placeholder="Email" />  (no label)
✅ <label htmlFor="email">Email</label>
   <input id="email" type="email" aria-describedby="email-hint" />
   <p id="email-hint">We'll never share your email</p>
```

### 2. React Code Quality

**Hook rules:**
- No hooks inside conditionals, loops, or nested functions
- `useEffect` dependencies array complete (no missing deps)
- Cleanup functions for subscriptions, timers, event listeners

```tsx
// ❌ Missing cleanup
useEffect(() => {
  document.addEventListener('keydown', handler)
}, [])

// ✅ Cleanup
useEffect(() => {
  document.addEventListener('keydown', handler)
  return () => document.removeEventListener('keydown', handler)
}, [])
```

**State management:**
- No derived state in `useState` (compute from existing state)
- `useReducer` for complex state logic with >2 related state updates
- No unnecessary state — if it can be computed, compute it

**Props:**
- Destructure props at function signature
- Default values in destructuring, not inside the function body
- No `any` types — every prop typed explicitly

**Key prop:**
```tsx
// ❌ Index as key (breaks on reorder/remove)
{items.map((item, i) => <Item key={i} {...item} />)}

// ✅ Stable unique id
{items.map(item => <Item key={item.id} {...item} />)}
```

### 3. CSS / Styling

**Specificity:**
- Avoid `!important` (almost always a sign of specificity conflict)
- Prefer class selectors over element+class chains: `.card-title` not `.card h2`
- BEM or CSS Modules to prevent conflicts

**Layout:**
- No absolute positioning for layout (use flex/grid)
- No fixed heights that break with dynamic content
- Test with long content / translated text (German text ≈ 30% longer)

**Responsive:**
- Mobile-first media queries (`min-width`, not `max-width`)
- No `px` for breakpoints if accessibility matters (use `em`)
- `min-content` / `max-content` for intrinsic sizing

**Performance:**
```css
/* ❌ Triggers layout */
.box:hover { width: 110%; height: 110%; }

/* ✅ GPU-only */
.box:hover { transform: scale(1.1); }
```

### 4. Performance

**Rendering:**
- No inline function/object creation in JSX (causes unnecessary re-renders)
```tsx
// ❌ New object on every render
<Component style={{ color: 'red' }} />

// ✅ Stable reference
const style = { color: 'red' }  // outside component, or useMemo
<Component style={style} />
```

**Images:**
- `loading="lazy"` on below-fold images
- `width` and `height` attributes set (prevents CLS)
- WebP format with fallback
- `srcSet` for responsive images

**Data fetching:**
- No fetch inside render (use hooks, React Query, SWR)
- Parallel requests with `Promise.all` where possible
- No waterfall: avoid fetch-then-fetch patterns

---

## Review Output Format

```markdown
## Frontend Code Review: [Component/File Name]

### Summary
X accessibility issues (Y critical), X code quality issues, X performance issues

---

### 🔴 Critical

**[A11y] Icon button has no accessible name**
- Location: `Button.tsx:42`
- Issue: `<button><SearchIcon /></button>` — screen readers announce "button" with no context
- Fix: Add `aria-label="Search"` or visible text with `sr-only` class
```

**[A11y] Form inputs not associated with labels**
- Location: `LoginForm.tsx:18,24`
- Issue: `placeholder` is not a substitute for `<label>`
- Fix:
```tsx
<label htmlFor="email">Email</label>
<input id="email" type="email" />
```

---

### 🟠 Major

**[React] Missing useEffect cleanup causes memory leak**
- Location: `useWebSocket.ts:35`
- Issue: WebSocket connection never closed on unmount
- Fix: Return cleanup function: `return () => ws.close()`

---

### 🟡 Minor

**[CSS] Hover effect animates `left` property (triggers layout)**
- Location: `nav.module.css:67`
- Issue: `left: 0 → left: 4px` causes reflow on every frame
- Fix: `transform: translateX(4px)` instead

---

### 🔵 Enhancements

**[Performance] Images missing `loading="lazy"`**
- Location: `ProductGrid.tsx:89-103`
- Impact: Loads all product images immediately, even below fold
- Fix: Add `loading="lazy"` to all `<img>` below first viewport
```

---

## Automated Checks to Recommend

Suggest adding to CI:
- `axe-core` / `jest-axe` for accessibility
- `eslint-plugin-jsx-a11y` for React a11y linting
- `lighthouse-ci` for performance regression
- `stylelint` for CSS quality

---

*Sources: Vercel web-design-guidelines skill, WCAG 2.1, React docs, web.dev performance guides*
