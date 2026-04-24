---
name: bundle-size-optimizer
description: "Analyzes and reduces JavaScript bundle size through dependency auditing, code splitting, tree shaking, and import optimization. Targets measurable reductions in initial bundle weight. Triggers: \"bundle is too large\", \"reduce bundle size\", \"optimize imports\", \"tree shaking\", \"code splitting\", \"too much JavaScript\", \"slow initial load\"."
---

# Bundle Size Optimizer

Systematic reduction of JavaScript bundle size. Every KB of JavaScript has a cost: download, parse, and execution time — especially on mobile networks.

**Announce at start:** "I'm using the bundle-size-optimizer skill."

---

## Baseline Measurement

Before optimizing, measure:

```bash
# Webpack
ANALYZE=true npm run build
# Opens webpack-bundle-analyzer in browser

# Vite
npx vite-bundle-visualizer

# Next.js
ANALYZE=true next build
# Or: npx @next/bundle-analyzer

# Quick size check (gzipped)
find .next -name "*.js" | xargs gzip -l | sort -k2 -n | tail -20
```

**Target budgets:**
| Page type | Initial JS (gzipped) |
|---|---|
| Landing page | < 100KB |
| SPA page | < 150KB |
| Feature-rich app | < 250KB |
| Total page weight | < 1MB |

---

## Phase 1: Eliminate Heavy Dependencies

### Dependency Audit

```bash
# Find largest dependencies
npx cost-of-modules

# Check bundle impact of a specific package
npx bundlephobia moment
```

### Common Replacements

| Remove | Weight | Replace with | Weight | Savings |
|---|---|---|---|---|
| moment | 72KB | date-fns | 6KB (per fn) | ~66KB |
| moment | 72KB | Day.js | 2KB | ~70KB |
| lodash (full) | 71KB | lodash-es (tree-shaken) | varies | 40-60KB |
| lodash | 71KB | native JS | 0KB | 71KB |
| axios | 11KB | native fetch | 0KB | 11KB |
| classnames | 1KB | clsx | 0.3KB | 0.7KB |
| animate.css | 78KB | custom CSS | ~1KB | 77KB |
| faker (dev) | 1MB | bundled in dev only | 0KB in prod | 1MB |

```bash
# Check if lodash is imported as full bundle
grep -r "from 'lodash'" src/
# If found, change to:
grep -r "from 'lodash/get'" src/
```

### Polyfill Audit

```bash
# Check what babel-polyfill is adding
# Add browserslist to package.json
"browserslist": ["> 1%", "last 2 versions", "not IE 11"]

# Then check polyfills are targeted
npx browserslist
```

---

## Phase 2: Fix Import Patterns

### Barrel File Problem

Barrel files (`index.ts` that re-exports everything) can prevent tree shaking:

```typescript
// ❌ Imports entire library
import { Button } from '@/components'
// components/index.ts re-exports 50 components → all 50 load

// ✅ Direct import — only Button loads
import { Button } from '@/components/Button'
```

**Diagnosis:**
```bash
# Find barrel imports
grep -r "from '@/components'" src/ | grep -v "components/"
```

### Icon Library Optimization

```typescript
// ❌ Imports ALL icons (huge)
import * as Icons from 'react-icons/fi'
import { FiSearch } from 'react-icons'

// ✅ Direct import
import { FiSearch } from 'react-icons/fi'

// ✅ Even better: SVG sprite or inline SVG
// Only the icons you actually use
```

### Date Library

```typescript
// ❌ Entire moment.js
import moment from 'moment'
const formatted = moment(date).format('YYYY-MM-DD')

// ✅ date-fns — only imports used functions
import { format } from 'date-fns'
const formatted = format(date, 'yyyy-MM-dd')

// ✅ Native (for simple cases)
const formatted = new Date(date).toISOString().split('T')[0]
```

---

## Phase 3: Code Splitting

### Route-Level Splitting (highest impact)

```typescript
// React Router
import { lazy, Suspense } from 'react'
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))

function Router() {
  return (
    <Suspense fallback={<PageSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  )
}
```

### Component-Level Splitting

```typescript
// Split large, conditionally-rendered components
const HeavyDataGrid = lazy(() => import('./HeavyDataGrid'))
const RichTextEditor = lazy(() => import('./RichTextEditor'))
const ChartLibrary = lazy(() => import('./ChartLibrary'))

// Use only when needed
{isEditorOpen && (
  <Suspense fallback={<EditorSkeleton />}>
    <RichTextEditor />
  </Suspense>
)}
```

### Dynamic Imports for Features

```typescript
// Load feature on demand
async function onExportClick() {
  const { exportToPDF } = await import('./exportToPDF')
  await exportToPDF(data)
}
```

---

## Phase 4: Production Build Optimization

### Verify Tree Shaking is Working

```javascript
// vite.config.ts / webpack.config.js
// Ensure libraries are marked as side-effect free
// Check package.json of your deps for "sideEffects": false
```

### Compression

```bash
# Verify gzip/brotli is enabled on your server/CDN
# Check response headers: Content-Encoding: br (brotli) or gzip
curl -I -H "Accept-Encoding: br,gzip" https://yoursite.com

# Vite builds brotli by default
# Next.js enables gzip by default
```

### Preloading Critical Chunks

```html
<!-- Preload the chunk for the current route -->
<link rel="preload" as="script" href="/_next/static/chunks/dashboard.js" />

<!-- Prefetch likely next navigation -->
<link rel="prefetch" as="script" href="/_next/static/chunks/settings.js" />
```

---

## Phase 5: Monitoring

Set up bundle size CI checks:

```yaml
# .github/workflows/bundle-size.yml
- name: Check bundle size
  run: npx bundlewatch
# bundlewatch.config.js
module.exports = {
  files: [{ path: '.next/static/chunks/*.js', maxSize: '150 kB' }]
}
```

---

## Optimization Report Template

```
## Bundle Analysis: [App/Route]

### Current State
- Initial bundle: XKB gzipped
- Largest chunks: [list top 5]

### Issues Found

1. [High Impact] moment.js (72KB) — replace with date-fns
   Current: moment().format()
   Fix: import { format } from 'date-fns'
   Savings: ~66KB gzipped

2. [Medium] No route-level code splitting
   All X pages load on initial visit
   Fix: Wrap routes with React.lazy()
   Savings: ~40% reduction in initial bundle

3. [Low] lodash imported as full bundle (71KB)
   Grep found: import { get, set } from 'lodash'
   Fix: import get from 'lodash/get'
   Savings: ~60KB

### Expected Result After Fixes
- Initial bundle: ~XKB gzipped (X% reduction)
- LCP improvement: ~Xs
```

---

*Sources: Vercel react-best-practices skill, bundlephobia.com, web.dev bundle optimization guides*
