---
name: figma-to-component
description: "Converts Figma designs (screenshots, descriptions, or exported assets) into production-ready React/Vue components that faithfully implement the design. Extracts design tokens from the design and maps them to code. Triggers: \"implement this Figma design\", \"convert this design to code\", \"build this from the mockup\", \"code this UI design\", \"implement the design spec\"."
---

# Figma to Component

Converts Figma designs into production-ready components with faithful implementation and clean code architecture.

**Announce at start:** "I'm using the figma-to-component skill."

---

## Input Formats

This skill works with:
1. **Screenshot/image** — visual representation of the design
2. **Figma description** — detailed text description of layout, colors, spacing
3. **Design spec** — explicit values (colors, typography, spacing from Figma Dev Mode)
4. **Combination** — image + extracted values

Ask the user to provide as much detail as possible, especially:
- Exact colors (hex values from Figma's Dev Mode)
- Font families, sizes, and weights
- Spacing values (use Figma's Dev Mode inspect panel)
- Component states (default, hover, active, disabled, error)
- Responsive behavior (how it adapts at different breakpoints)

---

## Extraction Process

### Step 1: Visual Inventory

Before writing code, list every visual element:

```
Layout:
  - Container width/max-width
  - Grid/flex structure
  - Gap between elements
  - Padding (outer/inner)

Typography:
  - Every text element: font-family, size, weight, color, line-height, letter-spacing

Colors:
  - Every unique color with hex value
  - Gradient stops if applicable
  - Shadow values (x, y, blur, spread, color)

Spacing:
  - All padding and margin values
  - Gap/gutter values

Border:
  - border-radius for each element
  - border width and color

Interactive states:
  - Hover styles
  - Focus styles
  - Active/pressed
  - Disabled
  - Error/validation
```

### Step 2: Map to Design Tokens

Map extracted values to design system tokens (if available) or create local tokens:

```css
/* Design-specific tokens (if no global design system) */
:root {
  /* Extract these exact values from the Figma file */
  --card-bg: #ffffff;
  --card-radius: 12px;
  --card-shadow: 0 4px 24px rgb(0 0 0 / 0.08);
  --card-padding: 24px;

  --heading-font: 'Inter', sans-serif;
  --heading-size: 24px;
  --heading-weight: 600;
  --heading-color: #111827;

  --body-font: 'Inter', sans-serif;
  --body-size: 14px;
  --body-weight: 400;
  --body-color: #6b7280;
}
```

### Step 3: Determine Component Structure

Break the design into a component tree:

```
<ProductCard>           ← root container
  <ProductCard.Image>   ← image section
  <ProductCard.Body>    ← content section
    <ProductCard.Badge> ← status indicator
    <ProductCard.Title>
    <ProductCard.Meta>
  <ProductCard.Footer>  ← actions
    <ProductCard.Price>
    <ProductCard.Button>
```

Identify:
- What is a reusable sub-component vs. a layout element?
- What data is dynamic (props) vs. structural?
- What states exist for each sub-component?

---

## Implementation

### Pixel-Perfect Priority Rules

1. **Get layout right first** — structure before decoration
2. **Typography next** — most impactful visual element
3. **Colors and backgrounds** — exact hex values from design
4. **Spacing** — use exact pixel values from Figma
5. **Shadows and borders** — fine details last
6. **States** — hover, focus, active, disabled

### Accepting Deviation

It's acceptable (and sometimes better) to deviate from Figma when:
- The design uses non-accessible colors → use accessible equivalent with same hue
- Magic numbers appear (e.g., 13px spacing) → snap to design system scale
- A static design doesn't account for dynamic content (overflow, empty states) → design defensively

Always document deviations with comments: `/* Adjusted from 13px to 12px (space-3) for design system consistency */`

---

## React Implementation Pattern

```tsx
interface CardProps {
  image: string
  imageAlt: string
  badge?: string
  title: string
  description: string
  price: string
  onAddToCart: () => void
}

export function Card({
  image, imageAlt, badge, title, description, price, onAddToCart
}: CardProps) {
  return (
    <article className={styles.card}>
      <div className={styles.imageWrapper}>
        <img src={image} alt={imageAlt} className={styles.image} loading="lazy" />
        {badge && <span className={styles.badge}>{badge}</span>}
      </div>
      <div className={styles.body}>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.description}>{description}</p>
      </div>
      <footer className={styles.footer}>
        <span className={styles.price}>{price}</span>
        <button
          type="button"
          className={styles.button}
          onClick={onAddToCart}
          aria-label={`Add ${title} to cart`}
        >
          Add to cart
        </button>
      </footer>
    </article>
  )
}
```

```css
/* card.module.css — exact values from Figma */
.card {
  background: var(--card-bg, #ffffff);
  border-radius: var(--card-radius, 12px);
  box-shadow: var(--card-shadow, 0 4px 24px rgb(0 0 0 / 0.08));
  overflow: hidden;
  transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgb(0 0 0 / 0.12);
}

/* ...all other extracted values */
```

---

## Deliverables

1. **Component file** — clean, typed React/Vue component
2. **Styles** — CSS module or Tailwind classes with exact design values
3. **Types** — TypeScript interface with all props documented
4. **States** — all visual states implemented (hover, focus, disabled, etc.)
5. **Notes** — any deviations from the design and why

---

## Responsive Implementation

If the design shows only one breakpoint, design defensively:

```css
/* Mobile-first */
.card { padding: 16px; }

@media (min-width: 768px) {
  .card { padding: 24px; }
}

@media (min-width: 1280px) {
  .card { padding: 32px; }
}
```

Always test with:
- Long text content (overflow handling)
- Missing images (placeholder handling)
- RTL text direction (if internationalization needed)

---

*Sources: Figma Dev Mode documentation, CSS pixel-perfect implementation patterns, React component architecture*
