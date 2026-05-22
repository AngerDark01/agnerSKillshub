---
name: state-management-architect
description: "Designs state management architecture for React applications. Chooses the right tool for each state category (server state vs client state vs UI state), prevents over-engineering, and fixes common state management problems. Triggers: \"state management\", \"too much Redux\", \"should I use Redux\", \"React Query setup\", \"Zustand vs Context\", \"how to manage state\", \"state architecture\"."
---

# State Management Architect

Designs the right state management strategy for React applications. The most common mistake is using one solution for all state — the key is matching the tool to the state category.

**Announce at start:** "I'm using the state-management-architect skill."

---

## The Four State Categories

Every piece of state belongs to exactly one category. Use a different tool for each:

| Category | Definition | Right Tool |
|---|---|---|
| **Server state** | Data that lives on the server, fetched async | React Query / SWR |
| **Global client state** | UI state shared across many components | Zustand |
| **Form state** | Input values, validation, submission | React Hook Form |
| **Local UI state** | Ephemeral component-level state | useState / useReducer |

---

## Decision Framework

```
Is this data from an API / server?
  └─ Yes → Server State → Use React Query or SWR
        (handles: caching, background sync, loading/error states, deduplication)

Is this UI-only state?
  ├─ Used by only 1-2 components → useState / useReducer
  ├─ Shared by 3-5 nearby components → Lift state + prop drilling
  ├─ Shared across the whole app → Zustand (or Jotai)
  └─ Complex multi-step form → React Hook Form

"My state is complex" test:
  → If you need to undo/redo → useReducer
  → If you need time-travel debugging → Redux Toolkit (rare)
  → If you need state machines → XState
```

---

## Server State: React Query

The default choice for all API data.

```typescript
// Installation
// npm install @tanstack/react-query

// Setup (app root)
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,   // data stays fresh for 5 min
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router />
    </QueryClientProvider>
  )
}
```

```typescript
// Fetching
export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],           // unique cache key
    queryFn: () => fetchUser(id),     // async fetch function
    enabled: !!id,                    // conditional fetch
  })
}

// In component
function UserProfile({ id }: { id: string }) {
  const { data: user, isLoading, error } = useUser(id)

  if (isLoading) return <Skeleton />
  if (error) return <ErrorMessage error={error} />
  return <div>{user.name}</div>
}
```

```typescript
// Mutations (create/update/delete)
export function useUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: UpdateUserInput) => updateUser(data),
    onSuccess: (updatedUser) => {
      // Update cache immediately (no refetch needed)
      queryClient.setQueryData(['user', updatedUser.id], updatedUser)
      // Or invalidate to force refetch:
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })
}
```

### React Query Patterns

**Query keys — be consistent:**
```typescript
// Organize as arrays: [entity, id?, filters?]
['users']                          // list
['users', '123']                   // single item
['users', '123', 'posts']          // related data
['users', { status: 'active' }]    // filtered list
```

**Parallel queries:**
```typescript
function Dashboard({ userId }: { userId: string }) {
  const userQuery = useQuery({ queryKey: ['user', userId], queryFn: ... })
  const postsQuery = useQuery({ queryKey: ['posts', userId], queryFn: ... })
  // Both fire in parallel!
}
```

**Dependent queries:**
```typescript
const userQuery = useQuery({ queryKey: ['user', id], queryFn: ... })
const postsQuery = useQuery({
  queryKey: ['posts', userQuery.data?.teamId],
  queryFn: () => fetchPostsByTeam(userQuery.data!.teamId),
  enabled: !!userQuery.data?.teamId,  // only runs after user loads
})
```

---

## Global Client State: Zustand

For UI state that multiple components need — theme, sidebar state, shopping cart, notifications.

```typescript
// Installation: npm install zustand

// stores/uiStore.ts
import { create } from 'zustand'

interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  setSidebarOpen: (open: boolean) => void
  toggleTheme: () => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  theme: 'light',
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleTheme: () => set((state) => ({
    theme: state.theme === 'light' ? 'dark' : 'light'
  })),
}))

// Usage — only re-renders when sidebarOpen changes
function Sidebar() {
  const isOpen = useUIStore(state => state.sidebarOpen)
  // ...
}
```

**Feature slices (for larger stores):**
```typescript
// Separate concern into slices, combine in root store
import { createCartSlice } from './cartSlice'
import { createUserSlice } from './userSlice'

export const useStore = create<CartSlice & UserSlice>()((...a) => ({
  ...createCartSlice(...a),
  ...createUserSlice(...a),
}))
```

**Zustand with persistence:**
```typescript
import { persist } from 'zustand/middleware'

const useCartStore = create<CartState>()(
  persist(
    (set) => ({ items: [], addItem: (item) => set(s => ({ items: [...s.items, item] })) }),
    { name: 'cart-storage' }  // key in localStorage
  )
)
```

---

## Form State: React Hook Form

For any form with more than 2 fields.

```typescript
// npm install react-hook-form zod @hookform/resolvers

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type FormValues = z.infer<typeof schema>

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(data: FormValues) {
    await login(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} aria-invalid={!!errors.email} />
      {errors.email && <p role="alert">{errors.email.message}</p>}

      <input type="password" {...register('password')} />
      {errors.password && <p role="alert">{errors.password.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Log in'}
      </button>
    </form>
  )
}
```

---

## Local UI State: useState / useReducer

**useState** for simple independent state:
```typescript
const [isOpen, setIsOpen] = useState(false)
const [selectedTab, setSelectedTab] = useState<'overview' | 'details'>('overview')
```

**useReducer** for complex related state:
```typescript
type State = { step: number; data: Partial<FormData>; error: string | null }
type Action =
  | { type: 'NEXT_STEP'; data: Partial<FormData> }
  | { type: 'PREV_STEP' }
  | { type: 'SET_ERROR'; error: string }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'NEXT_STEP':
      return { ...state, step: state.step + 1, data: { ...state.data, ...action.data } }
    case 'PREV_STEP':
      return { ...state, step: state.step - 1 }
    case 'SET_ERROR':
      return { ...state, error: action.error }
  }
}
```

---

## Common Anti-Patterns

```typescript
// ❌ Using Redux for server data (use React Query instead)
dispatch(fetchUser(id))  // manual loading/error state management

// ❌ Storing derived data in state
const [fullName, setFullName] = useState('')  // when you have firstName + lastName
const fullName = `${firstName} ${lastName}`  // just compute it

// ❌ Duplicating server data in local state
const [user, setUser] = useState(null)
useEffect(() => { fetchUser().then(setUser) }, [])  // use useQuery instead

// ❌ useState for complex form validation
const [emailError, setEmailError] = useState('')
const [passwordError, setPasswordError] = useState('')  // use React Hook Form
```

---

*Sources: Vercel composition-patterns skill, Zustand docs, TanStack Query docs, React Hook Form docs*
