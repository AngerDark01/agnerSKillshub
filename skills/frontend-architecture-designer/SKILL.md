---
name: frontend-architecture-designer
description: "Designs scalable frontend application architectures: feature-based folder structure, module boundaries, data flow patterns, and component hierarchy. Use when starting a new project, restructuring an existing one, or planning a major refactor. Triggers: \"design the architecture\", \"structure the project\", \"how should we organize this\", \"frontend architecture\", \"project structure\", \"modular architecture\"."
---

# Frontend Architecture Designer

Designs frontend application architecture: folder structure, module boundaries, component hierarchy, and data flow. Good architecture makes the codebase easy to navigate, extend, and test.

**Announce at start:** "I'm using the frontend-architecture-designer skill."

---

## Architecture Principles

**1. Feature-First Organization**
Group by feature/domain, not by type. Files that change together live together.

**2. Clear Module Boundaries**
Each module owns its files. No circular dependencies. Public API via explicit exports.

**3. Dependency Direction**
`pages` → `features` → `shared` → `core`. Never invert this direction.

**4. Co-location**
Tests, styles, and types live next to the code they describe.

---

## Folder Structure by Project Size

### Small Project (< 20 screens)

```
src/
├── components/        ← shared, reusable UI components
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── Button.module.css
│   └── ...
├── pages/             ← route-level components
│   ├── Home.tsx
│   ├── Dashboard.tsx
│   └── Settings.tsx
├── hooks/             ← shared custom hooks
├── utils/             ← pure utility functions
├── api/               ← API layer (fetch functions, types)
├── types/             ← shared TypeScript types
└── App.tsx
```

### Medium Project (20-100 screens) — Feature-Based

```
src/
├── features/                    ← domain modules (most code lives here)
│   ├── auth/
│   │   ├── components/          ← auth-specific components
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── hooks/               ← auth-specific hooks
│   │   │   └── useAuth.ts
│   │   ├── api/                 ← auth API calls
│   │   │   └── auth.api.ts
│   │   ├── types.ts             ← auth-specific types
│   │   └── index.ts             ← public API (only export what's needed outside)
│   ├── products/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── index.ts
│   └── cart/
│       ├── components/
│       ├── hooks/
│       ├── store/               ← feature-level state
│       └── index.ts
├── shared/                      ← cross-feature, no domain knowledge
│   ├── components/              ← Button, Input, Modal, etc.
│   ├── hooks/                   ← useDebounce, useLocalStorage, etc.
│   ├── utils/                   ← formatDate, formatCurrency, etc.
│   └── types/                   ← utility types, API response types
├── pages/                       ← thin route components, compose features
│   ├── DashboardPage.tsx
│   └── ProductDetailPage.tsx
├── app/                         ← app-wide configuration
│   ├── router.tsx
│   ├── providers.tsx            ← context providers
│   └── store.ts                 ← global state setup (if needed)
└── main.tsx
```

### Large Project (100+ screens) — Domain-Driven

```
src/
├── domains/                     ← bounded contexts (DDD)
│   ├── catalog/                 ← product catalog bounded context
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── models/              ← domain models and business logic
│   │   ├── store/
│   │   └── index.ts             ← public API
│   └── orders/
│       └── ...
├── platform/                    ← cross-domain infrastructure
│   ├── api-client/              ← HTTP client, auth, error handling
│   ├── analytics/               ← tracking events
│   ├── feature-flags/           ← feature toggle system
│   └── monitoring/              ← error reporting
├── ui/                          ← design system components
│   ├── primitives/              ← Button, Input, Icon
│   ├── patterns/                ← DataTable, Modal, Form
│   └── layouts/                 ← Page, Sidebar, Grid
├── pages/
└── app/
```

---

## Module Boundary Rules

### Public API Pattern

Every feature module exports only what other modules need:

```typescript
// features/auth/index.ts — public API
export { LoginForm } from './components/LoginForm'
export { useAuth } from './hooks/useAuth'
export type { User, AuthState } from './types'

// What's NOT exported is internal to the feature:
// - AuthContext (internal)
// - validatePassword (internal utility)
// - authReducer (internal)
```

**Import rules:**
```typescript
// ✅ Import from feature's public API
import { useAuth } from '@/features/auth'

// ❌ Import from inside a feature you don't own
import { authReducer } from '@/features/auth/store/authReducer'

// ✅ Shared utilities are fine to import directly
import { formatDate } from '@/shared/utils/formatDate'
```

### Preventing Circular Dependencies

```
✅ Allowed dependency directions:
pages → features → shared → utils

❌ Circular (never):
features/cart → features/auth → features/cart

❌ Wrong direction:
shared → features  (shared must not know about features)
```

---

## Component Hierarchy Design

### Three-Tier Component Model

```
1. Pages (smart containers)
   - Compose features together
   - Connect to routing
   - Minimal UI logic

2. Feature components (domain-aware)
   - Contain business logic for one domain
   - Connected to feature state
   - Not reusable across features (that's fine)

3. UI components (domain-agnostic)
   - Pure presentation, highly reusable
   - No business logic
   - Take all data via props
   - Live in shared/components or ui/
```

---

## Data Flow Architecture

### Recommended Patterns by Complexity

| Complexity | Solution | When |
|---|---|---|
| Local UI state | `useState` / `useReducer` | Single component |
| Shared between siblings | Lift state to parent | < 3 levels deep |
| Feature-wide state | React Context or Zustand slice | Feature scope |
| Server state | React Query / SWR | API data |
| Global UI state | Zustand / Redux | Cross-feature UI |
| Global server cache | React Query | All server data |

**Colocation principle:** State should live as close to where it's used as possible.

---

## Architecture Decision Record Template

Document significant decisions:

```markdown
## ADR-001: Feature-Based Folder Structure

**Date:** YYYY-MM-DD
**Status:** Accepted

### Context
The project has grown to 50+ screens. File-type organization (all components in /components, all hooks in /hooks) makes it hard to find related files and understand feature boundaries.

### Decision
Adopt feature-based structure with explicit public APIs via index.ts barrel files.

### Consequences
+ Related files co-located → easier navigation
+ Clear module boundaries → easier to extract features
+ Explicit public API → easier to refactor internals
- More initial setup
- Need to enforce import rules (eslint-plugin-import)
```

---

## Enforcement Tools

```json
// .eslintrc.json — enforce import boundaries
{
  "rules": {
    "import/no-restricted-paths": ["error", {
      "zones": [
        {
          "target": "./src/shared",
          "from": "./src/features",
          "message": "shared must not import from features"
        }
      ]
    }]
  }
}
```

---

*Sources: Vercel composition-patterns skill, Bulletproof React architecture guide, DDD frontend patterns*
