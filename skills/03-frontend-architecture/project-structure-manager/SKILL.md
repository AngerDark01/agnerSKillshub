---
name: project-structure-manager
description: "Analyzes and improves frontend project structure: identifies module boundary violations, circular dependencies, misplaced files, and structural debt. Produces a migration plan. Triggers: \"audit project structure\", \"fix module boundaries\", \"organize the codebase\", \"find circular dependencies\", \"repo structure\", \"where should this file go\", \"project organization\"."
---

# Project Structure Manager

Analyzes existing project structure, identifies structural problems, and produces a concrete migration plan to a clean architecture.

**Announce at start:** "I'm using the project-structure-manager skill."

---

## Phase 1: Structural Audit

### Step 1: Map the Current Structure

```bash
# Visualize current structure (3 levels deep, no node_modules)
find src -not -path '*/node_modules/*' -not -path '*/.git/*' | \
  grep -v '__pycache__' | sort | head -100

# Count files by type
find src -name "*.tsx" | wc -l
find src -name "*.ts" -not -name "*.d.ts" | wc -l
find src -name "*.test.*" | wc -l

# Find largest directories
find src -type d | while read d; do
  echo "$(find "$d" -maxdepth 1 -type f | wc -l) $d"
done | sort -n | tail -20
```

### Step 2: Detect Common Problems

**Problem: God Directories**
```bash
# Directories with too many files (> 30 files = smell)
find src -type d | while read d; do
  count=$(find "$d" -maxdepth 1 -name "*.tsx" -o -name "*.ts" | wc -l)
  echo "$count $d"
done | sort -n | tail -10
```

**Problem: Circular Dependencies**
```bash
# Install madge: npm install -g madge
madge --circular src/
madge --image circular.svg src/  # visual graph
```

**Problem: Feature Code in Wrong Place**
```bash
# Find domain-specific code in shared/utils
grep -r "import.*auth" src/shared/  # auth logic in shared = ❌
grep -r "import.*product" src/components/  # product logic in generic components = ❌
```

**Problem: Missing Test Co-location**
```bash
# Find components without test files
for f in $(find src -name "*.tsx" | grep -v test | grep -v stories); do
  testfile="${f%.tsx}.test.tsx"
  if [ ! -f "$testfile" ]; then echo "No test: $f"; fi
done
```

**Problem: Deep Nesting**
```bash
# Find files nested more than 5 levels deep
find src -name "*.ts" | awk -F/ '{if(NF>7) print NF" "$0}' | sort -n
```

---

## Phase 2: Problem Classification

Classify each problem by severity:

### 🔴 Critical (breaks scalability)
- Circular dependencies between modules
- Shared module imports from feature modules
- God components > 500 lines with mixed concerns

### 🟠 Major (creates friction)
- Feature logic scattered across unrelated directories
- No clear module public API (everything exported from deep paths)
- Test files in separate `__tests__` directories instead of co-located

### 🟡 Minor (code smell)
- Inconsistent naming conventions
- Flat structure that will break as codebase grows
- Missing index.ts for feature modules

---

## Phase 3: Migration Plan

### Naming Conventions to Enforce

```
Components:        PascalCase.tsx        (UserCard.tsx)
Hooks:             camelCase.ts          (useUserCard.ts)
Utilities:         camelCase.ts          (formatDate.ts)
Types:             PascalCase.ts         (UserCard.types.ts)
Test files:        [name].test.tsx       (UserCard.test.tsx)
Story files:       [name].stories.tsx    (UserCard.stories.tsx)
CSS modules:       [name].module.css     (UserCard.module.css)
API functions:     [name].api.ts         (users.api.ts)
Store slices:      [name].store.ts       (users.store.ts)
```

### Module Public API Pattern

Every feature directory should have an `index.ts`:

```typescript
// features/auth/index.ts
// EXPORT: what other features need
export { LoginForm } from './components/LoginForm'
export { useAuth } from './hooks/useAuth'
export { AuthGuard } from './components/AuthGuard'
export type { User, AuthState } from './types'

// DO NOT EXPORT: internal implementation
// - authReducer (internal)
// - validateToken (internal util)
// - AuthContext (internal)
```

### Migration Sequence

When restructuring, always migrate in this safe order:

1. **Add new structure** — create target directories
2. **Create index.ts** for each module with new public API
3. **Migrate one feature at a time** — don't do everything at once
4. **Update imports** — use `codemod` or IDE refactor tools
5. **Verify no circular deps** — run `madge --circular src/` after each feature
6. **Remove old files** — only after imports are verified
7. **Add ESLint rules** — enforce boundaries after migration

### ESLint Import Rules

```javascript
// .eslintrc.js — enforce module boundaries
module.exports = {
  rules: {
    // Prevent importing from other features directly
    'no-restricted-imports': ['error', {
      patterns: [
        {
          group: ['../features/*/'],  // must import via index.ts
          message: 'Import from feature public API: @/features/[name]',
        },
      ],
    }],
    // Or use eslint-plugin-boundaries for granular control
  },
}
```

---

## Structural Debt Inventory Template

```markdown
## Project Structure Audit: [Project Name]

### Summary
- Files: X total (Y components, Z hooks, W utilities)
- Test coverage: X% (Y test files for Z source files)
- Circular dependencies: X chains found
- Module boundary violations: X found

### Critical Issues

1. **Circular dependency chain**
   - auth/hooks/useAuth → cart/cartUtils → auth/authHelpers
   - Fix: Move shared logic to shared/utils/authTokens.ts

2. **Shared module importing feature**
   - shared/components/Header imports from features/auth directly
   - Fix: Pass auth props as props, or use useAuth hook in pages layer

### Major Issues

3. **Scattered product domain logic**
   - Product-related files in: /components, /hooks, /utils, /api
   - Fix: Create features/products/ and consolidate

### Migration Plan

Phase 1 (Week 1): Fix circular deps (critical)
Phase 2 (Week 2-3): Create features/auth, features/products
Phase 3 (Week 4): Add ESLint boundary rules
Phase 4 (Ongoing): Migrate remaining features one at a time
```

---

## Quick Wins (No Migration Required)

```bash
# 1. Add path aliases to avoid relative import hell
# tsconfig.json
{
  "paths": {
    "@/*": ["./src/*"],
    "@features/*": ["./src/features/*"],
    "@shared/*": ["./src/shared/*"]
  }
}

# Then: import { Button } from '@shared/components/Button'
# Instead of: import { Button } from '../../../shared/components/Button'

# 2. Add barrel exports for existing feature directories
# features/auth/index.ts — just re-export existing files

# 3. Co-locate test files that are in __tests__ directories
# mv src/__tests__/UserCard.test.tsx src/components/UserCard/UserCard.test.tsx
```

---

*Sources: Bulletproof React architecture, feature-sliced design methodology, Nx monorepo architecture patterns*
