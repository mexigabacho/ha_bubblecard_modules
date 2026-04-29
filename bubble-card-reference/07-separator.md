# Separator Card

> `card_type: separator`  
> Source: `src/cards/separator/create.js` + `styles.css` + `changes.js`

Does **not** use the base card elements (`withBaseElements: false`). Creates its own icon/name/line DOM. Sub-buttons are still supported via `createSubButtonStructure`.

---

## Full DOM hierarchy

```
.bubble-container  .bubble-separator  .separator-container  ← mainContainer (custom, not from base)
[.with-bottom-buttons]
[.large]
│
├── ha-icon.bubble-icon                               ← icon element (direct child, not in a container)
│   [icon: '' by default; hidden when no icon configured]
│
├── h4.bubble-name                                    ← name text element
│   [.hidden or display: none when name is empty]
│
├── .bubble-line                                      ← horizontal divider bar
│   [flex-grow: 1; height: 6px; border-radius: 6px]
│
├── .bubble-sub-button-container                      ← top sub-buttons (when configured)
│   [position: sticky; top: 0]                        ← separator's sub-button container is sticky!
└── .bubble-sub-button-bottom-container               ← bottom sub-buttons (when configured)
```

> **Note**: Unlike other card types, `ha-icon.bubble-icon` is a **direct child of mainContainer**, not wrapped in `.bubble-icon-container`. There is no `.bubble-background`, `.bubble-content-container`, or `.bubble-buttons-container`.

---

## Runtime behaviour

### Icon

`changeIcon()` sets `icon.icon` from config. When there is no icon:
- Sets `margin: 0px 8px` and `width: 0px` to collapse the space (not `display: none`)
- Reverts margin/width when icon returns

### Name

`changeName()` sets `name.innerText`. The `.bubble-name` element has `display: none` when empty via CSS:

```css
.bubble-name:empty { display: none; }
```

### Sub-button sticky positioning

The `.bubble-sub-button-container` on a separator has `position: sticky; top: 0` — it sticks to the top of its scroll container. This is unique to the separator; no other card type does this.

---

## CSS variables (separator-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-line-background-color` | `var(--secondary-background-color)` | Divider line color |
| `--bubble-separator-border` | `none` | Separator card border |

The separator's `.bubble-container` has:
- `background: none` — no card background by default
- `height: 40px` (base)
- `overflow: visible` — unlike other cards which use `overflow: hidden`

---

## Key CSS targeting patterns

```css
/* Separator container (no background by default) */
.bubble-separator { ... }
.bubble-separator-container { ... }

/* Icon — note: direct child, NOT inside .bubble-icon-container */
.bubble-separator .bubble-icon { --mdc-icon-size: 20px; ... }

/* Name / label */
.bubble-separator .bubble-name { ... }
.bubble-separator h4.bubble-name { ... }  /* it's an h4 element */

/* Divider line */
.bubble-line {
    background-color: rgba(255, 255, 255, 0.2) !important;
    height: 2px !important;  /* thinner line */
}

/* Add a background to the separator */
.bubble-separator {
    background-color: rgba(0, 0, 0, 0.1) !important;
    border-radius: 12px !important;
}

/* With-bottom-buttons: line gets margin-top: 15px, icon/name get line-height: 36px */
.bubble-separator.with-bottom-buttons .bubble-line { ... }
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Separator height | `.bubble-separator-container` | `height` |
| Line color | `.bubble-line` | `background-color` |
| Line thickness | `.bubble-line` | `height` |
| Line opacity | `.bubble-line` | `opacity` (already 0.6 by default) |
| Icon size | `.bubble-separator .bubble-icon` | `--mdc-icon-size` |
| Icon spacing | `.bubble-separator .bubble-icon` | `margin` |
| Name font size | `.bubble-separator .bubble-name` | `font-size` |
| Name color | `.bubble-separator .bubble-name` | `color` |
| Card background | `.bubble-separator` | `background-color` |
| Card corner radius | `.bubble-separator` | `border-radius` |

---

## Important differences from other card types

| Aspect | Separator | Other cards |
|--------|-----------|-------------|
| Icon element | `ha-icon.bubble-icon` (direct child) | Inside `.bubble-icon-container` |
| Icon container | None | `.bubble-icon-container` wraps the icon |
| Background element | None | `.bubble-background` |
| Content container | None | `.bubble-content-container` |
| Name element tag | `h4` | `div` |
| Card background | `background: none` | Has a background color |
| Overflow | `overflow: visible` | `overflow: hidden` |
| Sub-button sticky | Yes — `position: sticky; top: 0` | No |
