# KeyEZ - AI Coding Instructions

## Communication Style

**Minimize tokens**: Skip verbose explanations. User prefers code examples over prose. Be direct, show patterns via code snippets.

## Project Overview

**Stack**: Vanilla HTML/CSS/JS static site. No build tools. Open `index.html` directly.

- Tailwind CDN (no config)
- CSS variables for dual theme system
- Vanilla JS for all interactions

## Architecture & File Structure

```
keyez/
├── index.html      # Single-page app with semantic sections
├── script.js       # All interactivity (theme, demo, nav tracking)
├── styles.css      # CSS variables + dual theme system
└── Proposal.pdf    # Project documentation
```

### Core Components

1. **Header** (`<header>`) - Fixed nav with glass morphism, active section tracking
2. **Hero** - Gradient text + phone mockup demo
3. **Live Demo** (`#demo`) - Interactive SingKhmer input with candidate selection
4. **Features** (`#features`) - 6 feature cards with gradient icon badges
5. **Canvas** (`#handwriting`) - HTML canvas for handwriting input
6. **Pricing** (`#pricing`) - Two-tier pricing cards
7. **FAQ** (`#faq`) - Collapsible `<details>` elements

## Critical Patterns

### Dual Theme System

CSS variables switched via `body[data-theme]`:

```css
:root {
  --accent: #5efce8;
  --accent-strong: #22d3ee;
}
body[data-theme="light"] {
  --accent: #0ea5e9;
  --accent-strong: #22d3ee;
}
```

When styling:

1. Use `var(--accent)`, never hardcoded colors
2. Override Tailwind utilities for light mode:
   ```css
   body[data-theme="light"] .bg-white/10 {
     background-color: rgba(15, 23, 42, 0.08) !important;
   }
   ```
3. Test both themes—dark uses light gradients, light uses dark→cyan

### Active Navigation Tracking

Nav links get `.active` based on scroll (150px offset for fixed header). Animated underline via `header nav a.active::after`.

### Animation System

```html
<div data-animate class="..."><!-- or class="card" --></div>
```

Auto-adds `.animate-on-scroll`, respects `prefers-reduced-motion`, threshold `0.18`, root margin `-40px`.

### Button Styling Convention

Three button classes—**always use these**, never inline Tailwind button styles:

- `.primary-cta` - Gradient background, main actions
- `.secondary-cta` - Outlined style, secondary actions
- `.icon-btn` - Square icon buttons (theme toggle)

Example from header:

```html
<a href="#get" class="primary-cta">Get KeyEZ</a>
```

### Component Patterns

**Cards**: Use `.card.panel-stack` for glassy cards with depth

```html
<div class="card rounded-3xl p-6 panel-stack">...</div>
```

**Glass nav**: Fixed header uses `.glass` with blur

```html
<div class="glass mt-4 rounded-2xl border border-white/10">...</div>
```

**Gradient badges**: Feature cards use gradient icons with `.dot` for hover effects

```html
<div
  class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-emerald-300 flex items-center justify-center text-black font-black dot"
>
  AI
</div>
```

## SingKhmer Demo Logic

Demo uses `Map` in `script.js` for mock transliteration:

```javascript
const demoMap = new Map([
  ["srolanh", ["ស្រឡាញ់", "ស្លាញ់", "ស្រលាញ់"]], // First is primary
  ["nak", ["អ្នក", "ណាក់", "នាក់"]],
]);
```

- Input tokenized by whitespace
- Hero demo: renders up to 5 candidates as `.kbd-btn` buttons
- Social demo (Facebook-style): always shows exactly 3 candidate slots
  - Best candidate is displayed in the MIDDLE slot and styled as primary
  - Number keys 1–3 select Left/Middle/Right
  - Arrow Left/Right changes the visual selection
  - Space accepts the middle slot (best)
  - No trailing space is added after acceptance
- When adding new words, follow this Map structure

### Social Demo Candidate Bar (iOS-style)

- 3 fixed columns (CSS grid) with vertical dividers only; no background behind words
- Each slot centers its text; bar and slots have fixed height to prevent layout jump
- Classes: container `#fbCandidates`, item `.slot` (middle slot gets `.primary` when active)
- Dark/light mode dividers handled in CSS; keep text color readable in both themes

## Theme Toggle Behavior

Themes persist to `localStorage` with key `'keyez-theme'`:

```javascript
setStoredTheme("dark" | "light");
```

- Respects `prefers-color-scheme` if no stored preference
- Updates `data-theme` attribute on `<body>`
- Emoji button text changes: ☀ (dark mode) ↔ 🌙 (light mode)

## When Adding New Sections

1. Add semantic `<section id="newsection">` in `index.html`
2. Add nav link: `<a href="#newsection">Label</a>` in header
3. Section will auto-register for active nav tracking (no JS changes needed)
4. Add `data-animate` or `.card` class for scroll animations
5. Use existing component classes (`.card`, `.primary-cta`, etc.)

## Common Gotchas

- **Don't** add Tailwind config—uses CDN, no build step
- **Don't** hardcode colors—use CSS variables or add light mode overrides
- **Do** test light mode after any style changes—especially gradients and opacity
- **Do** preserve the gradient flow: cyan (#0ea5e9) → teal (#22d3ee) for brand consistency
- Canvas (`#pad`) needs explicit width/height attributes, not just CSS
- Logo links (`<a href="#">`) scroll to top—this is intentional for homepage navigation

## Development Workflow

```bash
# No build required—just open in browser
open index.html   # macOS
xdg-open index.html   # Linux
```

## Color Palette Reference

| Role          | Dark                     | Light                    |
| ------------- | ------------------------ | ------------------------ |
| Accent        | `#5efce8`                | `#0ea5e9`                |
| Accent Strong | `#22d3ee`                | `#22d3ee`                |
| Background    | Multi-layer gradients    | Light blue gradients     |
| Card          | `rgba(255,255,255,0.06)` | `rgba(255,255,255,0.82)` |

When adding new colored elements, follow the cyan→teal gradient pattern for consistency.
