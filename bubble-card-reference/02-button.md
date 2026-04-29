# Button Card

> `card_type: button`  
> Source: `src/cards/button/create.js` + `styles.css` + `changes.js`

Uses the full base structure. See [01-base-structure.md](01-base-structure.md) for the shared DOM.

---

## Button types

| `button_type` | Default action | Notes |
|---------------|---------------|-------|
| `switch` (default) | `tap: toggle` | Background lights up when on |
| `state` | `tap: more-info`, icon: `tap: more-info` | Shows state text; no color background change |
| `name` | No actions | Display only; no color |
| `slider` | Horizontal drag to set value | Also adds `.bubble-button-slider-container` |

---

## Full DOM hierarchy

```
.bubble-button-container                             ← mainContainer
.bubble-container
.bubble-button-card-container                        ← backward-compat alias
[.bubble-button-slider-container]                    ← added when button_type=slider
[.with-bottom-buttons]
[.is-on | .is-off | .is-unavailable]
[.large | .rows-2]
│
└── .bubble-button  .bubble-wrapper  .bubble-button-card
    ├── .bubble-background  .bubble-button-background
    │   [tap-action feedback ripple if button_action configured]
    ├── .bubble-content-container
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container
    │   │   ├── ha-icon.bubble-main-icon  .bubble-icon  .icon
    │   │   ├── div.bubble-entity-picture  .entity-picture  (when image available)
    │   │   └── .bubble-icon-feedback-container  .bubble-feedback-container
    │   │       └── .bubble-icon-feedback  .bubble-feedback-element  .feedback-element
    │   └── .bubble-name-container  .name-container
    │       ├── .bubble-name  .name
    │       │   [.hidden]  ← when show_name: false
    │       └── .bubble-state  .state
    │           [.display-state]    ← when state/attribute visible
    │           [.state-without-name]  ← when showing state but not name
    │           [.hidden]           ← when show_state: false
    ├── .bubble-feedback-container  .feedback-container  (when button has tap_action)
    │   └── .bubble-feedback-element  .feedback-element
    ├── .bubble-buttons-container                    ← display: contents (no visual box)
    │   [card-type-specific main buttons — empty for basic button]
    ├── .bubble-sub-button-container                 ← top sub-buttons (when configured)
    └── .bubble-sub-button-bottom-container          ← bottom sub-buttons (when configured)
```

When `button_type: slider`, a slider structure is inserted inside `mainContainer` (before `cardWrapper`):

```
.bubble-range-slider                                 ← slider track + fill, full card overlay
    ├── .bubble-range-fill                           ← fill bar
    └── [touch/mouse event listeners]
```

---

## Runtime state classes

On `mainContainer` (`.bubble-button-card-container`):

| Class | When |
|-------|------|
| `.is-on` | Entity considered on |
| `.is-off` | Entity considered off |
| `.is-unavailable` | Entity unavailable |
| `.with-bottom-buttons` | Bottom sub-buttons or `main_buttons_position: bottom` |
| `.large` | Large card layout |
| `.rows-2` | Large-2-rows layout |
| `.bubble-button-slider-container` | `button_type: slider` |

On `cardWrapper` (`.bubble-button-card`):

| Class | When |
|-------|------|
| `.fixed-top` | Bottom group exists or `main_buttons_position: bottom` |
| `.full-width` | Large layout with bottom-fixed buttons |

---

## Icon stability — why and how {#icon-stability}

The `i` grid column is `auto`-sized — it stretches to fit the icon container. If you use `width: 100%` on `.bubble-icon-container`, the column size depends on the parent, causing reflow when state text or sub-buttons change width.

**Fix: equal `min-width` = `max-width` locks the column to exactly one size:**

```css
.bubble-button-card > .bubble-icon-container {
  min-width: 110px !important;
  max-width: 110px !important;
  /* Never use width: 100% — it creates reflow dependency on parent */
}
```

**`transform` vs negative margin for visual offset:**

```css
/* BAD — negative margin pulls element out of flow, grid recalculates */
margin-left: -20px !important;

/* GOOD — transform is layout-neutral; grid never sees the visual shift */
transform: translateX(-8px);
```

---

## CSS variables (button-specific)

| Variable | Controls |
|----------|----------|
| `--bubble-button-border-radius` | Overrides card border-radius for button only |
| `--bubble-button-background-color` | Background fill color (set by JS on card element, not stylesheet) |
| `--bubble-button-accent-color` | Active state color override |
| `--bubble-button-icon-background-color` | Icon container bg override |
| `--bubble-button-icon-border-radius` | Icon container border-radius override |

---

## Key CSS targeting patterns

```css
/* Card background — color changes applied here by JS */
.bubble-button-background { ... }

/* Icon container — scoped to prevent bleeding into sub-buttons */
.bubble-button-card > .bubble-icon-container { ... }
.bubble-button-card > .bubble-icon-container .bubble-icon { ... }

/* Cancel icon rules on sub-buttons (required if you style .bubble-icon) */
.bubble-sub-button .bubble-icon { color: inherit !important; --mdc-icon-size: 16px !important; }

/* Name */
.bubble-button-card .bubble-name { ... }

/* State text */
.bubble-button-card .bubble-state { ... }

/* Active state */
.is-on .bubble-button-background { ... }
.is-on .bubble-icon-container { ... }

/* Off state */
.is-off .bubble-button-background { ... }

/* Slider fill */
.bubble-button-card .bubble-range-fill { ... }
.bubble-button-card .bubble-range-slider { ... }
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Icon size | `.bubble-icon` | `--mdc-icon-size: Xpx` |
| Icon container size (stable) | `.bubble-button-card > .bubble-icon-container` | `min-width` + `max-width` (equal) |
| Icon container shape | `.bubble-button-card > .bubble-icon-container` | `border-radius` |
| Icon container background | `.bubble-button-card > .bubble-icon-container` | `background-color` |
| Card background color | `.bubble-button-background` | `background-color` |
| Active state color | `.is-on .bubble-button-background` | `background-color` (or use `--bubble-button-background-color` JS var) |
| Card corner radius | `.bubble-container` | `border-radius` |
| Card height (normal layout) | `.bubble-button-card-container` | `height` |
| Card height (section view) | Card YAML | `grid_options: rows: N` |
| Name font size | `.bubble-name` | `font-size` |
| State text | `.bubble-state` | `font-size`, `opacity`, `color` |
| Hide state | `.bubble-state` | `display: none` |
| Sub-button size | `.bubble-sub-button` | `min-width`, `height` |
| Sub-button icon | `.bubble-sub-button .bubble-icon` | `--mdc-icon-size` |
| Hide sub-button text | `.bubble-sub-button-name-container` | `display: none` |
| Slider fill color | `.bubble-range-fill` | `background-color` |
| Name position | `.bubble-name-container` | `justify-self`, `align-self` |

---

## Grid layout (normal vs large vs large-2-rows)

### Normal layout (`card_layout: normal`)

```
grid-template-areas:   "i  n  a"
grid-template-columns:  auto  1fr  auto
grid-template-rows:     50px
```

| Area | Element | Sizing |
|------|---------|--------|
| `i` | `.bubble-icon-container` | `auto` — shrinks to content |
| `n` | `.bubble-name-container` | `1fr` — fills remaining space |
| `a` | `.bubble-sub-button-container` | `auto` — shrinks to content |

### Large layout (`card_layout: large`)

- Height: `calc(var(--row-height,56px) * var(--row-size,1) + var(--row-gap,8px) * (var(--row-size,1) - 1))`
- Icon container: `min-width: 42px; min-height: 42px; margin-left: 8px`
- Adds `.large` class on mainContainer

### Large-2-rows layout

```
grid-template-areas:  "i  n  a"
                      "b  b  b"    ← sub-buttons in a full-width bottom row
```

Adds `.rows-2` class on mainContainer.

---

## Debugging tips

- **Inspect grid**: DevTools → `.bubble-button-card` → Layout tab → "Show area names". Look at resolved `grid-template-columns` in Computed.
- **Conflicting styles**: struck-through rules in DevTools Styles tab = overridden. If your rule loses despite `!important`, check stylesheet load order or specificity.
- **Icon shifting**: almost always caused by `width: 100%` or negative margin on `.bubble-icon-container`. Fix with equal `min-width`/`max-width`.
- **Large layout height**: if icon is taller than `calc(var(--row-height) * var(--row-size))`, it clips — either set `grid_options: rows: N` or reduce icon size.
- **Sub-button name class**: sub-button named `"Volume"` gets class `.volume`. Use `.volume .bubble-sub-button-icon` to target its icon specifically.
