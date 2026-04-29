# Horizontal Buttons Stack Card

> `card_type: horizontal-buttons-stack`  
> Source: `src/cards/horizontal-buttons-stack/create.js` + `styles.css` + `changes.js`

Does **not** use the base structure at all. A fixed-position navigation bar that renders at the bottom of the viewport. Buttons are positioned absolutely inside a scroll container.

---

## Full DOM hierarchy

```
context.card  (the HA `ha-card` element)
  classes added: .horizontal-buttons-stack-card
  [.has-gradient]         ← added unless hide_gradient: true
  [.editor]               ← in dashboard editor mode
  │
  └── .card-content       (HA's built-in scroll wrapper inside ha-card)
      state classes:
        [.is-scrolled]    ← when scrollLeft > 0
        [.is-maxed-scroll] ← when scrolled to the end
      [.is-scrollable]    ← when content is wider than card
      │
      └── .bubble-horizontal-buttons-stack-card-container
          .horizontal-buttons-stack-container             ← cardContainer
          │
          ├── .bubble-button  .bubble-button-1  .button  .<link-hash>   ← button 1 (1-indexed)
          │   [.highlight]    ← when current view URL matches this button's link
          │   ├── ha-icon.bubble-icon  .icon
          │   ├── .bubble-name  .name
          │   ├── .bubble-background-color  .background-color  ← border + light color tint
          │   ├── .bubble-background  .background             ← card background fill
          │   └── ha-ripple
          │
          ├── .bubble-button  .bubble-button-2  .button  .<link-hash>   ← button 2
          │   [same structure]
          │
          └── ... (as many buttons as configured, N-indexed)
```

### Gradient overlay (pseudo-element)

When `.has-gradient` is present:

```css
.has-gradient.horizontal-buttons-stack-card::before {
    content: '';
    position: absolute;
    top: -32px;
    background: linear-gradient(0deg, var(--bubble-horizontal-buttons-stack-background-color, ...) 50%, transparent);
    width: 200%;
    height: 100px;
    pointer-events: none;
}
```

This creates the fade gradient above the HBS bar.

---

## Button identification

Each button gets three identifying classes:
1. `.bubble-button-N` — 1-indexed position (e.g. `.bubble-button-1`)
2. `.button` — generic
3. `.<link-hash>` — derived from the `N_link` value, e.g. if `1_link: '#living-room'` → class `living-room`

---

## Runtime behaviour

### Button positioning

Buttons are positioned **absolutely** inside the container using `transform: translateX(Npx)`. `placeButtons()` measures each button's `offsetWidth`, saves it to `localStorage`, and accumulates positions:

```
button[0].transform = translateX(0)
button[1].transform = translateX(button[0].width + 12)
button[2].transform = translateX(button[0].width + button[1].width + 24)
```

The container's `width` is set to the total accumulated width. This is why buttons don't use flexbox — absolute positioning allows the animated reordering.

### Auto-ordering

When `auto_order: true`, buttons with active PIR sensors sort to the front, ordered by `last_updated`. Buttons with no PIR sensor go to the end. Sorting uses `sortButtons()`.

### Highlight

`.highlight` class is added when `location.pathname` or `location.hash` matches the button's link. Combined with a CSS `animation: pulse 1.4s infinite alternate` (brightness oscillation).

### Scroll masking

`.card-content` has a `mask-image` gradient that hides buttons at the edges:
- Neutral: fades in at 28px from left, fades out at 28px from right
- `.is-scrolled`: removes left fade (already past the start)
- `.is-maxed-scroll`: removes right fade (already at the end)

---

## CSS variables (HBS-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-horizontal-buttons-stack-background-color` | `var(--bubble-secondary-background-color)` | Button background fill + gradient color |
| `--bubble-horizontal-buttons-stack-border-radius` | `var(--bubble-border-radius, 32px)` | Button corner radius |
| `--desktop-width` | `500px` | Max width of card content on desktop |

---

## Key CSS targeting patterns

```css
/* The fixed bar itself */
.horizontal-buttons-stack-card { ... }

/* Scroll container */
.card-content { ... }

/* All buttons */
.bubble-horizontal-buttons-stack-card-container .bubble-button { ... }

/* Specific button by index */
.bubble-button-1 { ... }
.bubble-button-3 { ... }

/* Specific button by link hash (e.g. link: '#living-room') */
.living-room { ... }

/* Active/highlighted button */
.bubble-button.highlight { ... }

/* Button icon */
.horizontal-buttons-stack-card .bubble-icon { --mdc-icon-size: 20px; }

/* Button name label */
.horizontal-buttons-stack-card .bubble-name { ... }

/* Button background color overlay (border + light tint) */
.bubble-background-color { ... }

/* Button background fill */
.horizontal-buttons-stack-card .bubble-background { ... }

/* Gradient above bar */
.has-gradient.horizontal-buttons-stack-card::before { ... }
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Button height | `.horizontal-buttons-stack-card .bubble-button` | `height` (default 50px) |
| Button corner radius | `.bubble-button` | `border-radius` or `--bubble-horizontal-buttons-stack-border-radius` |
| Button background fill | `.bubble-background` | `background-color` |
| Button border/tint color | `.bubble-background-color` | `background-color`, `border-color` |
| Active button style | `.bubble-button.highlight` | `animation`, `background-color` |
| Icon size | `.bubble-icon` | `--mdc-icon-size` |
| Name text | `.bubble-name` | `font-size`, `display: none` to hide |
| Gradient above bar | `.has-gradient.horizontal-buttons-stack-card::before` | `background`, `height` |
| Bar position from bottom | `.horizontal-buttons-stack-card` | `bottom` (default 16px) |
| Bar height | `.horizontal-buttons-stack-card` | `height` (default 51px) |
| Max width | `--desktop-width` | CSS variable |
| Scroll fade width | `.card-content mask-image` | Modify via CSS override |

---

## Important notes for module development

- This card type has **no sub-button system** — sub-buttons are not supported.
- Buttons are **not in a flexbox or grid** — they are absolutely positioned. Do not apply flex/grid rules to the container expecting layout changes.
- The `<link-hash>` class on each button (e.g. `.living-room` from `#living-room`) is the most reliable selector for targeting a specific button.
- The HBS card is a **globally fixed element** — its CSS affects the whole viewport. Scope all selectors tightly.
- `ha-card` on this card type has `border-radius: 0` (set in styles) and no background.
