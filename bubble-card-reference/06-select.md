# Select Card

> `card_type: select`  
> Source: `src/cards/select/create.js` + `styles.css` + `changes.js`

Uses the full base structure with minimal additions. See [01-base-structure.md](01-base-structure.md) for the shared DOM.

---

## Full DOM hierarchy

The select card is almost identical to the button card DOM. The key difference is that single-tap on the card background opens a dropdown (not toggle), and a dropdown component is added for the option list.

```
.bubble-select-container  .bubble-container          ← mainContainer
.bubble-select-card-container                        ← extra class added
[.with-bottom-buttons]
[.is-on | .is-off | .is-unavailable]
[.large | .rows-2]
│
└── .bubble-select  .bubble-wrapper
    ├── .bubble-background                           ← cursor: pointer (CSS)
    │   [tap: opens dropdown — tap_action forced to "none"; actual open is via dropdown component]
    │
    ├── .bubble-content-container
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container
    │   │   ├── ha-icon.bubble-main-icon  .bubble-icon  .icon
    │   │   └── div.bubble-entity-picture  .entity-picture
    │   └── .bubble-name-container  .name-container
    │       ├── .bubble-name  .name
    │       └── .bubble-state  .state
    │           [shows current selected option]
    │
    ├── .bubble-feedback-container  .feedback-container
    │   └── .bubble-feedback-element  .feedback-element
    │
    ├── .bubble-buttons-container                    ← display: flex (normal, not contents)
    │   [dropdown arrow element appended here by dropdown component]
    │
    ├── .bubble-sub-button-container                 ← top sub-buttons (when configured)
    └── .bubble-sub-button-bottom-container          ← bottom sub-buttons (when configured)
```

The dropdown itself is rendered by the dropdown component and appears as an absolutely-positioned overlay outside the card's flow when open.

---

## Key behavioural differences from button

- **Single tap** on the card background is forced to `action: none` by the select card code (to prevent double-firing). The dropdown component handles the actual open.
- **Double-tap and hold** can still be configured via `button_action`.
- The state text (`.bubble-state`) shows the **current selected option**.
- `overflow: inherit` on `.bubble-container` (not `overflow: hidden`) — needed to allow the dropdown overlay to escape the card boundaries.

---

## CSS variable override (select-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| (inherits all base + button variables) | — | — |

The select card's CSS only adds two rules on top of base:

```css
.bubble-container {
    overflow: inherit;      /* allows dropdown to overflow card boundary */
    transition: border 0.3s ease;
}
.bubble-background {
    cursor: pointer;
}
```

---

## Key CSS targeting patterns

```css
/* Card container — note overflow: inherit vs other cards' overflow: hidden */
.bubble-select-container { ... }

/* Background — has cursor: pointer already */
.bubble-select .bubble-background { ... }

/* Current option shown in state */
.bubble-select .bubble-state { ... }

/* Icon */
.bubble-select .bubble-icon-container { ... }
.bubble-select .bubble-icon { ... }

/* Dropdown arrow (rendered by dropdown component) */
.bubble-select .bubble-dropdown-arrow { ... }

/* Cancel sub-button icon bleed */
.bubble-sub-button .bubble-icon { color: inherit !important; --mdc-icon-size: 16px !important; }
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Card background | `.bubble-select .bubble-background` | `background-color` |
| Option name text | `.bubble-select .bubble-name` | `font-size`, `color` |
| Selected option text | `.bubble-select .bubble-state` | `font-size`, `opacity` |
| Icon container | `.bubble-select .bubble-icon-container` | `background-color`, `border-radius` |
| Icon | `.bubble-select .bubble-icon` | `--mdc-icon-size`, `color` |
| Card height | `.bubble-select-container` | `height` or `grid_options: rows` |
