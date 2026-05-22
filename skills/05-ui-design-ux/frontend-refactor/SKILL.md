---
name: frontend-refactor
description: "Refactors React components and hooks to improve composition, reduce prop drilling, eliminate boolean prop explosion, and enforce clean separation of concerns. Uses composition patterns over configuration. Triggers: \"refactor this component\", \"too many props\", \"simplify this\", \"split this component\", \"extract this logic\", \"hooks refactor\", \"component is too big\"."
---

# Frontend Refactor

Systematic refactoring of React components toward clean composition, reusable hooks, and maintainable architecture. Applies proven patterns; avoids premature abstraction.

**Announce at start:** "I'm using the frontend-refactor skill."

---

## When to Refactor (Smell Detection)

Refactor when you see:
- **Boolean prop explosion**: `<Button primary large outline loading disabled icon />` — 6+ boolean props means you need variants
- **Render prop hell**: `renderHeader`, `renderFooter`, `renderItem` — use composition (children) instead
- **God components**: 200+ lines in a single component — split by concern
- **Prop drilling**: passing props through 3+ components that don't use them — use context or composition
- **Duplicate logic**: same `useEffect`, `useState` pattern repeated — extract to custom hook
- **Mixed concerns**: data fetching + UI rendering in same component — separate them

---

## Refactoring Patterns

### Pattern 1: Boolean Props → Variants

**Before (smell):**
```tsx
<Button primary large disabled />
<Button secondary small />
<Button destructive outline />
```

**After (composition):**
```tsx
type Variant = 'primary' | 'secondary' | 'destructive' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

<Button variant="primary" size="lg" disabled />
<Button variant="secondary" size="sm" />
<Button variant="destructive" />
```

Rule: If you have more than 2-3 related booleans, use a `variant` or `size` enum.

### Pattern 2: Render Props → Children Composition

**Before (smell):**
```tsx
<Card
  renderHeader={() => <h2>Title</h2>}
  renderBody={() => <p>Content</p>}
  renderFooter={() => <Button>Action</Button>}
/>
```

**After (slot composition):**
```tsx
<Card>
  <Card.Header><h2>Title</h2></Card.Header>
  <Card.Body><p>Content</p></Card.Body>
  <Card.Footer><Button>Action</Button></Card.Footer>
</Card>
```

Implementation:
```tsx
function Card({ children }: { children: ReactNode }) {
  return <div className={styles.card}>{children}</div>
}
Card.Header = function CardHeader({ children }: { children: ReactNode }) {
  return <div className={styles.header}>{children}</div>
}
// etc.
```

### Pattern 3: Extract Custom Hooks

**Before (smell):**
```tsx
function UserProfile() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    fetchUser(id)
      .then(setUser)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [id])

  // ...render
}
```

**After (hook extraction):**
```tsx
// hooks/useUser.ts
function useUser(id: string) {
  const [state, setState] = useState<{
    data: User | null
    loading: boolean
    error: Error | null
  }>({ data: null, loading: false, error: null })

  useEffect(() => {
    setState(s => ({ ...s, loading: true }))
    fetchUser(id)
      .then(data => setState({ data, loading: false, error: null }))
      .catch(error => setState(s => ({ ...s, loading: false, error })))
  }, [id])

  return state
}

// UserProfile.tsx — now only renders
function UserProfile({ id }: { id: string }) {
  const { data: user, loading, error } = useUser(id)
  // just rendering logic here
}
```

### Pattern 4: Eliminate Prop Drilling with Context

**Before (drill smell):**
```tsx
<App theme={theme}>
  <Layout theme={theme}>
    <Sidebar theme={theme}>
      <NavItem theme={theme} />  {/* theme not used here */}
    </Sidebar>
  </Layout>
</App>
```

**After (context):**
```tsx
const ThemeContext = createContext<Theme>('light')
export const useTheme = () => useContext(ThemeContext)

// Root
<ThemeContext.Provider value={theme}>
  <App />
</ThemeContext.Provider>

// NavItem (uses theme directly, no prop drilling)
function NavItem() {
  const theme = useTheme()
  // ...
}
```

**When NOT to use context:** For UI state local to a component subtree, use state lifting + composition. Context is for truly global/shared state.

### Pattern 5: Split Large Components by Concern

Rule: One component, one responsibility.

**Before:** `UserDashboard.tsx` (300 lines, fetches data, renders charts, handles modals)

**After:**
```
UserDashboard/
  index.tsx              ← orchestrator, no logic
  UserDashboard.tsx      ← layout composition
  useUserDashboard.ts    ← all data fetching and state
  UserStats.tsx          ← stats section
  UserActivity.tsx       ← activity section
  UserSettings.tsx       ← settings section
```

---

## Refactoring Workflow

1. **Read first** — understand what the component does completely before touching it
2. **Write tests** — if no tests exist, add snapshot/behavior tests before refactoring
3. **Extract one concern at a time** — don't refactor and add features simultaneously
4. **Verify after each step** — run tests after every extraction
5. **Never change behavior** — refactoring should produce identical output

---

## Anti-Patterns to Avoid During Refactor

- **Over-abstracting**: Don't create a base component if there are only 2 variants
- **Premature hooks**: Don't extract a custom hook if the logic is used in only one place
- **Breaking the API**: If a component is used externally, maintain backward compatibility or create a new component alongside
- **Fixing other things**: If you notice a bug while refactoring, file it separately. One change at a time.

---

*Sources: Vercel composition-patterns skill, React documentation, Kent C. Dodds component patterns*
