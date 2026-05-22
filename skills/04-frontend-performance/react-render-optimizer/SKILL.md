---
name: react-render-optimizer
description: "Identifies and fixes unnecessary React re-renders using memoization, stable references, and proper component architecture. Targets measurable frame-rate improvements and reduced CPU usage. Triggers: \"component re-renders too much\", \"React is slow\", \"optimize re-renders\", \"memo\", \"useMemo\", \"useCallback\", \"React profiler\", \"sluggish UI\"."
---

# React Render Optimizer

Identifies and eliminates unnecessary React re-renders. Every unnecessary render wastes CPU, causes jank, and degrades battery life.

**Core rule:** Measure first. Never memoize blindly — premature optimization adds complexity without benefit.

**Announce at start:** "I'm using the react-render-optimizer skill."

---

## Step 1: Diagnose with Profiler

**Always measure before optimizing.**

```tsx
// Enable why-did-you-render in development
// npm install @welldone-software/why-did-you-render
// src/wdyr.ts (import at top of index.tsx)
import React from 'react'
if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = require('@welldone-software/why-did-you-render')
  whyDidYouRender(React, { trackAllPureComponents: true })
}
```

**React DevTools Profiler:**
1. Open React DevTools → Profiler tab
2. Click Record
3. Perform the interaction that feels slow
4. Stop recording
5. Look for components that rendered when they shouldn't have
6. Click the flame graph — the widest bars are the slowest renders

---

## Re-render Causes (Checklist)

### 1. Inline Object/Array/Function Creation

The #1 cause of unexpected re-renders.

```tsx
// ❌ New object reference on every parent render → child always re-renders
<UserCard style={{ padding: 16 }} options={['A', 'B']} onSave={() => save()} />

// ✅ Stable references
const cardStyle = { padding: 16 }           // outside component
const options = useMemo(() => ['A', 'B'], [])  // stable inside component
const handleSave = useCallback(() => save(), [save])
<UserCard style={cardStyle} options={options} onSave={handleSave} />
```

### 2. Context Value Not Memoized

```tsx
// ❌ New context value object on every render
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>  {/* new object every render */}
      {children}
    </ThemeContext.Provider>
  )
}

// ✅ Memoized value
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')
  const value = useMemo(() => ({ theme, setTheme }), [theme])
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}
```

### 3. Missing React.memo on Pure Components

```tsx
// ❌ Re-renders whenever parent re-renders
function UserAvatar({ user }: { user: User }) {
  return <img src={user.avatar} alt={user.name} />
}

// ✅ Only re-renders when user prop changes
const UserAvatar = React.memo(function UserAvatar({ user }: { user: User }) {
  return <img src={user.avatar} alt={user.name} />
})

// ✅ Custom comparison for complex objects
const UserAvatar = React.memo(
  ({ user }) => <img src={user.avatar} alt={user.name} />,
  (prev, next) => prev.user.id === next.user.id && prev.user.avatar === next.user.avatar
)
```

**When to use React.memo:**
- Component renders frequently
- Component receives same props often
- Component is expensive to render (heavy computation, many children)

**When NOT to use React.memo:**
- Component already renders rarely
- Props change every time anyway
- Component is simple (< 5 elements) — overhead exceeds benefit

### 4. Expensive Calculations Not Cached

```tsx
// ❌ Recalculates on every render
function ProductList({ products, filter }) {
  const filtered = products
    .filter(p => p.category === filter)
    .sort((a, b) => b.rating - a.rating)
  return filtered.map(p => <ProductCard key={p.id} product={p} />)
}

// ✅ Only recalculates when products or filter changes
function ProductList({ products, filter }) {
  const filtered = useMemo(() =>
    products
      .filter(p => p.category === filter)
      .sort((a, b) => b.rating - a.rating),
    [products, filter]
  )
  return filtered.map(p => <ProductCard key={p.id} product={p} />)
}
```

**When to use useMemo:**
- Filtering/sorting large arrays (> 100 items)
- Complex calculations (graph traversal, data transformation)
- Creating objects/arrays passed to memoized children
- Building derived data from multiple state values

**When NOT to use useMemo:**
- Simple calculations (string formatting, arithmetic)
- Arrays with < 20 items
- Values that change on every render anyway

### 5. useCallback for Stable Event Handlers

```tsx
// ❌ New function reference every render → child always re-renders
function Parent() {
  const [count, setCount] = useState(0)
  return (
    <>
      <Counter count={count} />
      <HeavyChild onAction={() => setCount(c => c + 1)} />  {/* new fn every render */}
    </>
  )
}

// ✅ Stable function reference
function Parent() {
  const [count, setCount] = useState(0)
  const handleAction = useCallback(() => setCount(c => c + 1), [])  // never changes
  return (
    <>
      <Counter count={count} />
      <HeavyChild onAction={handleAction} />
    </>
  )
}
```

**Only use useCallback when:**
- The function is passed as a prop to a memoized child
- The function is a dependency of another hook (useEffect, useMemo)

### 6. State Co-location

Move state down to the component that needs it:

```tsx
// ❌ Tooltip state in parent causes entire parent to re-render on hover
function Page() {
  const [tooltipVisible, setTooltipVisible] = useState(false)
  return (
    <div>
      <ExpensiveTable data={data} />  {/* re-renders on tooltip hover! */}
      <Tooltip
        visible={tooltipVisible}
        onShow={() => setTooltipVisible(true)}
        onHide={() => setTooltipVisible(false)}
      />
    </div>
  )
}

// ✅ Tooltip manages its own state
function Page() {
  return (
    <div>
      <ExpensiveTable data={data} />  {/* never re-renders on tooltip */}
      <Tooltip />  {/* manages its own visible state */}
    </div>
  )
}
```

### 7. List Rendering Optimization

```tsx
// ❌ All 1000 items re-render when any one changes
{items.map(item => <Item key={item.id} item={item} onUpdate={handleUpdate} />)}

// ✅ Virtualized list for long lists
import { FixedSizeList } from 'react-window'

function VirtualList({ items }) {
  const Row = useCallback(({ index, style }) => (
    <div style={style}>
      <Item item={items[index]} />
    </div>
  ), [items])

  return (
    <FixedSizeList
      height={600}
      width="100%"
      itemCount={items.length}
      itemSize={72}
    >
      {Row}
    </FixedSizeList>
  )
}
```

---

## Optimization Decision Tree

```
Is the component re-rendering too often?
  │
  ├─ Does it receive an inline object/array/function as prop?
  │   → Memoize with useMemo/useCallback in parent, or move outside component
  │
  ├─ Is it a pure component that doesn't need parent re-renders?
  │   → Wrap with React.memo
  │
  ├─ Is it doing expensive calculations?
  │   → Use useMemo for the calculation
  │
  ├─ Is a context value re-created on every render?
  │   → Memoize context value with useMemo
  │
  ├─ Is state stored too high in the tree?
  │   → Move state down (co-location)
  │
  └─ Is it a long list (100+ items)?
      → Use react-window or react-virtual
```

---

## Profiling Report Template

```
## React Render Analysis: [Component/Page]

### Problem
[Component name] renders X times per [interaction] when it should render Y times

### Root Cause
[e.g., "onSave prop is recreated on every parent render (inline arrow function)"]

### Evidence
React Profiler: X renders in Xms total for [Component]
why-did-you-render: "Re-rendered because props.onSave changed (function)"

### Fix
[Code change with before/after]

### Expected Improvement
[Component] renders: X → Y per interaction
Measured frame time: Xms → Yms
```

---

*Sources: Vercel react-best-practices skill + composition-patterns, React docs on optimization, Dan Abramov "Before You memo()"*
