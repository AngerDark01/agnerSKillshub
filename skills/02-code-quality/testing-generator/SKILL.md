---
name: testing-generator
description: "Generates unit tests, component tests, and integration tests for frontend code. Follows testing best practices: test behavior not implementation, meaningful assertions, edge case coverage. Triggers: \"write tests for this\", \"generate unit tests\", \"test this component\", \"add tests\", \"write test cases\", \"improve test coverage\"."
---

# Testing Generator

Generates comprehensive, maintainable tests for frontend code. Tests behavior and user interactions — not implementation details.

**Announce at start:** "I'm using the testing-generator skill."

---

## Testing Philosophy

**Test what users do, not how code works.**

```tsx
// ❌ Tests implementation (fragile)
expect(component.state.isOpen).toBe(true)
expect(wrapper.find('Button').prop('onClick')).toBeDefined()

// ✅ Tests behavior (resilient)
await userEvent.click(screen.getByRole('button', { name: 'Open menu' }))
expect(screen.getByRole('menu')).toBeVisible()
```

**The testing trophy (from Kent C. Dodds):**
- Unit tests: pure functions, utilities, hooks
- Integration tests: component interactions, form flows
- E2E tests: critical paths (login, checkout, key workflows)

Focus most effort on integration tests — they give the best confidence-to-cost ratio.

---

## Framework Setup

### Vitest + React Testing Library (recommended for Vite projects)

```bash
npm install -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
  },
})

// src/test/setup.ts
import '@testing-library/jest-dom'
```

### Jest + React Testing Library (CRA / Next.js)

```bash
npm install -D @testing-library/react @testing-library/user-event @testing-library/jest-dom
```

---

## Test Patterns

### Component Rendering Tests

```tsx
import { render, screen } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('renders with label', () => {
    render(<Button>Submit</Button>)
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument()
  })

  it('shows spinner and disables when loading', () => {
    render(<Button loading>Submit</Button>)
    const btn = screen.getByRole('button')
    expect(btn).toBeDisabled()
    expect(screen.getByRole('status')).toBeInTheDocument() // spinner
  })

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when disabled', async () => {
    const handleClick = vi.fn()
    render(<Button disabled onClick={handleClick}>Click me</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(handleClick).not.toHaveBeenCalled()
  })
})
```

### Form Tests (Integration)

```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from './LoginForm'

describe('LoginForm', () => {
  it('submits with valid credentials', async () => {
    const onSubmit = vi.fn()
    render(<LoginForm onSubmit={onSubmit} />)

    await userEvent.type(screen.getByLabelText('Email'), 'user@example.com')
    await userEvent.type(screen.getByLabelText('Password'), 'secret123')
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }))

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'secret123',
    })
  })

  it('shows validation errors for empty submission', async () => {
    render(<LoginForm onSubmit={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }))

    expect(screen.getByText('Email is required')).toBeInTheDocument()
    expect(screen.getByText('Password is required')).toBeInTheDocument()
  })

  it('shows error for invalid email format', async () => {
    render(<LoginForm onSubmit={vi.fn()} />)
    await userEvent.type(screen.getByLabelText('Email'), 'notanemail')
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }))

    expect(screen.getByText('Enter a valid email address')).toBeInTheDocument()
  })
})
```

### Custom Hook Tests

```tsx
import { renderHook, act } from '@testing-library/react'
import { useCounter } from './useCounter'

describe('useCounter', () => {
  it('starts at initial value', () => {
    const { result } = renderHook(() => useCounter(5))
    expect(result.current.count).toBe(5)
  })

  it('increments', () => {
    const { result } = renderHook(() => useCounter(0))
    act(() => result.current.increment())
    expect(result.current.count).toBe(1)
  })

  it('does not exceed max', () => {
    const { result } = renderHook(() => useCounter(10, { max: 10 }))
    act(() => result.current.increment())
    expect(result.current.count).toBe(10)
  })
})
```

### Async Tests (API calls)

```tsx
import { render, screen, waitFor } from '@testing-library/react'
import { server } from '../mocks/server'  // MSW
import { http, HttpResponse } from 'msw'
import { UserProfile } from './UserProfile'

describe('UserProfile', () => {
  it('displays user name after loading', async () => {
    render(<UserProfile userId="123" />)

    // Loading state
    expect(screen.getByRole('status')).toBeInTheDocument()  // spinner

    // Loaded state
    await screen.findByText('Jane Doe')  // waits for element
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('displays error message on API failure', async () => {
    server.use(
      http.get('/api/users/:id', () =>
        HttpResponse.json({ error: 'Not found' }, { status: 404 })
      )
    )

    render(<UserProfile userId="999" />)
    await screen.findByText('Failed to load user')
  })
})
```

### Accessibility Tests

```tsx
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { Modal } from './Modal'

expect.extend(toHaveNoViolations)

describe('Modal accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(
      <Modal isOpen title="Confirm action">
        <p>Are you sure?</p>
        <button>Confirm</button>
        <button>Cancel</button>
      </Modal>
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('traps focus inside modal', async () => {
    render(
      <Modal isOpen title="Test">
        <button>First</button>
        <button>Last</button>
      </Modal>
    )
    const buttons = screen.getAllByRole('button')
    // Tab from last button should cycle back to first
    await userEvent.tab()
    expect(buttons[0]).toHaveFocus()
  })
})
```

---

## Test Coverage Strategy

For each component/feature, generate tests in this order:

1. **Happy path** — core functionality works
2. **Empty/null states** — no data, no props
3. **Loading states** — async operations in progress
4. **Error states** — API failures, validation errors
5. **Edge cases** — very long text, special characters, zero/max values
6. **Interaction flows** — user journey through the feature
7. **Accessibility** — keyboard navigation, screen reader

---

## Mocking Patterns

```tsx
// Mock a module
vi.mock('../api/users', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: '1', name: 'Jane' })
}))

// Mock a hook
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ user: { id: '1', role: 'admin' }, isLoading: false })
}))

// Spy on a function
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
// ... test ...
consoleSpy.mockRestore()
```

---

*Sources: Anthropic webapp-testing skill, Testing Library docs, Kent C. Dodds testing philosophy*
