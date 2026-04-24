---
name: frontend-performance-analyzer
description: "Analyzes frontend performance: Core Web Vitals, render-blocking resources, bundle size, network waterfalls, and JavaScript execution. Produces prioritized optimization recommendations with measurable impact. Triggers: \"analyze performance\", \"why is this slow\", \"improve Web Vitals\", \"performance audit\", \"LCP is bad\", \"CLS issues\", \"TTI optimization\", \"profile this\"."
---

# Frontend Performance Analyzer

Analyzes frontend performance across all dimensions: loading, interactivity, visual stability, and runtime rendering. Produces prioritized, measurable optimizations.

**Announce at start:** "I'm using the frontend-performance-analyzer skill."

---

## Core Web Vitals — Targets

| Metric | Good | Needs Work | Poor | What it measures |
|---|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5-4.0s | > 4.0s | Loading performance |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200-500ms | > 500ms | Interactivity |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1-0.25 | > 0.25 | Visual stability |
| **FCP** (First Contentful Paint) | ≤ 1.8s | 1.8-3.0s | > 3.0s | Time to first content |
| **TTFB** (Time to First Byte) | ≤ 800ms | 800-1800ms | > 1800ms | Server response |

---

## Analysis Phases

### Phase 1: Diagnose with Tools

```bash
# Lighthouse CI audit
npx lighthouse https://yoursite.com --view

# Bundle analysis
npx webpack-bundle-analyzer stats.json      # Webpack
npx vite-bundle-visualizer                   # Vite
npx @next/bundle-analyzer                    # Next.js

# Core Web Vitals in production
# Install web-vitals package and log to analytics
```

```typescript
// Add to app entry point for production monitoring
import { onLCP, onINP, onCLS, onFCP, onTTFB } from 'web-vitals'

onLCP(console.log)
onINP(console.log)
onCLS(console.log)
```

### Phase 2: LCP Analysis

LCP = how fast the largest visible element loads.

**Common causes and fixes:**

| Cause | Diagnosis | Fix |
|---|---|---|
| Slow server response | TTFB > 800ms | CDN, caching, edge computing |
| Render-blocking CSS | CSS in `<head>` delays paint | Critical CSS inline, defer non-critical |
| Large hero image | Image > 200KB | WebP, `srcset`, `fetchpriority="high"` |
| Client-side rendering | HTML is empty | SSR or static generation |
| Fonts cause FOIT | Text invisible until font loads | `font-display: swap`, preload fonts |

**Quick wins:**
```html
<!-- Preload LCP image -->
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high" />

<!-- Preload critical fonts -->
<link rel="preload" as="font" href="/fonts/brand.woff2" crossorigin />

<!-- Hero image -->
<img
  src="/hero.webp"
  alt="Hero"
  fetchpriority="high"
  loading="eager"    <!-- NOT lazy for above-fold -->
  width="1200"
  height="600"       <!-- prevent CLS -->
/>
```

### Phase 3: CLS Analysis

CLS = unexpected layout shifts.

**Common causes and fixes:**

| Cause | Fix |
|---|---|
| Images without dimensions | Always set `width` and `height` on `<img>` |
| Ads/embeds without space | Reserve space with aspect-ratio CSS |
| Dynamically injected content | Reserve space before content loads |
| Web fonts causing text reflow | `font-display: optional` or match fallback metrics |
| Animations on layout properties | Use `transform` only |

```css
/* Reserve aspect ratio space */
.media-container {
  aspect-ratio: 16 / 9;
  width: 100%;
}

/* Font size adjustment to prevent shift */
@font-face {
  font-family: 'Brand';
  src: url('/fonts/brand.woff2') format('woff2');
  font-display: swap;
  /* Match fallback metrics with font-face override */
  ascent-override: 90%;
  descent-override: 20%;
  line-gap-override: 0%;
}
```

### Phase 4: INP Analysis

INP = responsiveness to user interactions.

**Common causes:**
- Long tasks blocking the main thread (> 50ms tasks)
- Expensive synchronous operations in event handlers
- Too many re-renders triggered by a single interaction

**Diagnosis:**
```javascript
// Chrome DevTools Performance tab → Interactions
// Look for long tasks (red triangles in the timeline)

// Or programmatically:
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.duration > 50) {
      console.warn('Long task:', entry.duration, 'ms', entry)
    }
  }
})
observer.observe({ entryTypes: ['longtask'] })
```

**Fixes:**
```typescript
// Break up long synchronous work
async function processLargeList(items: Item[]) {
  const results = []
  for (let i = 0; i < items.length; i++) {
    results.push(processItem(items[i]))
    // Yield to main thread every 100 items
    if (i % 100 === 0) {
      await new Promise(resolve => setTimeout(resolve, 0))
    }
  }
  return results
}

// Debounce expensive operations
const debouncedSearch = useMemo(
  () => debounce(search, 300),
  [search]
)
```

### Phase 5: Bundle Analysis

```bash
# Find what's making your bundle large
# After running bundle analyzer, look for:
# 1. Duplicated packages (multiple versions of the same library)
# 2. Large dependencies that could be replaced
# 3. Code that's always loaded but only sometimes needed
```

**Common bundle issues:**

| Issue | Fix |
|---|---|
| Moment.js (70KB) | Replace with date-fns or Day.js |
| lodash (full) | Import individually: `import get from 'lodash/get'` |
| Large icon library | Import only used icons, or use SVG sprite |
| Barrel file imports | Import directly from file, not index |
| Route-level code not split | Dynamic imports for each route |

```typescript
// ❌ Barrel file causes entire lib to load
import { Button, Input, Modal } from '@/components'

// ✅ Direct import — tree-shakeable
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'

// ✅ Dynamic import for code splitting
const HeavyChart = lazy(() => import('./HeavyChart'))
```

---

## Optimization Priority Matrix

| Impact | Effort | Priority |
|---|---|---|
| Fix render-blocking resources | High | Low | **Do first** |
| Add image dimensions (fix CLS) | High | Very Low | **Do first** |
| Lazy load below-fold images | High | Low | **Do first** |
| Code split routes | High | Medium | **Do next** |
| Preload LCP resource | High | Low | **Do next** |
| Replace large dependencies | Medium | Medium | Plan |
| Add service worker cache | Medium | High | Plan |
| Font optimization | Medium | Low | Do next |

---

## Report Template

```
## Performance Audit: [URL/Component]

### Core Web Vitals (measured)
- LCP: X.Xs  [🟢 Good / 🟡 Needs Work / 🔴 Poor]
- INP: Xms   [...]
- CLS: X.XX  [...]

### Critical Issues (fix immediately)
1. [LCP] Hero image not preloaded
   - Impact: ~800ms LCP improvement
   - Fix: Add <link rel="preload"> for hero.webp

### Major Issues
2. [Bundle] moment.js included (72KB gzipped)
   - Impact: ~15% JS parse time reduction
   - Fix: Replace with date-fns (7KB) or Day.js (2KB)

### Quick Wins
3. [CLS] 6 images missing width/height attributes
   - Impact: CLS 0.28 → ~0.05
   - Fix: Add dimensions to all <img> tags
```

---

*Sources: Vercel react-best-practices skill, web.dev performance docs, Chrome DevTools documentation*
