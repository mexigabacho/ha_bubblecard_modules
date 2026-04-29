# Cover Card

> `card_type: cover`  
> Source: `src/cards/cover/create.js` + `styles.css` + `changes.js`

Uses the full base structure. See [01-base-structure.md](01-base-structure.md) for the shared DOM.

---

## Full DOM hierarchy

```
.bubble-cover-container  .bubble-container            ← mainContainer
[.with-bottom-buttons]
[.is-on | .is-off | .is-unavailable]
[.large | .rows-2]
│
└── .bubble-cover  .bubble-wrapper
    ├── .bubble-background
    │
    ├── .bubble-content-container
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container
    │   │   ├── ha-icon.bubble-main-icon  .bubble-icon  .icon
    │   │   │   [icon changes between icon_open / icon_close based on position]
    │   │   └── div.bubble-entity-picture  .entity-picture
    │   └── .bubble-name-container  .name-container
    │       ├── .bubble-name  .name
    │       └── .bubble-state  .state
    │
    ├── .bubble-feedback-container  .feedback-container
    │   └── .bubble-feedback-element  .feedback-element
    │
    ├── .bubble-buttons-container                     ← also gets backward-compat aliases:
    │   .bubble-buttons  .buttons-container
    │   │
    │   ├── .bubble-cover-button  .bubble-button  .bubble-open  .button  .open
    │   │   [.disabled]  ← when cover is fully open (current_position === 100)
    │   │   ├── .bubble-feedback-container
    │   │   │   └── .bubble-feedback-element  .feedback-element
    │   │   ├── ha-icon.bubble-cover-button-icon  .bubble-icon-open
    │   │   │   [icon: mdi:arrow-up or mdi:arrow-expand-horizontal for curtains]
    │   │   └── ha-ripple
    │   │
    │   ├── .bubble-cover-button  .bubble-button  .bubble-stop  .button  .stop
    │   │   [display: none]  ← when entity doesn't support STOP feature
    │   │   ├── .bubble-feedback-container
    │   │   │   └── .bubble-feedback-element  .feedback-element
    │   │   ├── ha-icon.bubble-cover-button-icon  .bubble-icon-stop
    │   │   └── ha-ripple
    │   │
    │   └── .bubble-cover-button  .bubble-button  .bubble-close  .button  .close
    │       [.disabled]  ← when cover is fully closed (current_position === 0)
    │       ├── .bubble-feedback-container
    │       │   └── .bubble-feedback-element  .feedback-element
    │       ├── ha-icon.bubble-cover-button-icon  .bubble-icon-close
    │       │   [icon: mdi:arrow-down or mdi:arrow-collapse-horizontal for curtains]
    │       └── ha-ripple
    │
    ├── .bubble-sub-button-container                  ← top sub-buttons (when configured)
    └── .bubble-sub-button-bottom-container           ← bottom sub-buttons (when configured)
```

---

## Runtime behaviour

### Icon changes

`changeCoverIcons()` runs on every state update:

- Main icon: `mdi:arrow-up` / `mdi:arrow-down` swapped based on whether cover is fully open
- For `device_class: curtain`: `mdi:arrow-expand-horizontal` / `mdi:arrow-collapse-horizontal`
- Custom icons: `icon_open`, `icon_close`, `icon_up`, `icon_down` config keys

### Disabled state

Buttons get `.disabled` when at limits:
- `.bubble-open.disabled` when `current_position === 100` (fully open)
- `.bubble-close.disabled` when `current_position === 0` (fully closed)

CSS: `opacity: 0.3 !important; pointer-events: none !important; cursor: none !important`

### Feature support

Stop button is hidden (`display: none`) when the entity's `supported_features` bitmask does not include STOP (bit 8). Open/close disable at limits only when `current_position` attribute is defined.

---

## CSS variables (cover-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-cover-button-background-color` | transparent | Button background color |
| `--bubble-cover-buttons-border-radius` | `var(--bubble-border-radius)` | Button corner radius |

---

## Key CSS targeting patterns

```css
/* All three action buttons */
.bubble-cover-button { ... }

/* Individual buttons by semantic class */
.bubble-open { ... }
.bubble-stop { ... }
.bubble-close { ... }

/* Button icons */
.bubble-cover-button-icon { --mdc-icon-size: 20px; }
.bubble-icon-open { ... }
.bubble-icon-stop { ... }
.bubble-icon-close { ... }

/* Disabled state */
.bubble-cover-button.disabled { ... }   /* already has opacity 0.3 from styles */

/* State-reactive — is-on when cover state is 'open' */
.is-on .bubble-background { ... }

/* Cancel sub-button icon bleed */
.bubble-sub-button .bubble-icon { color: inherit !important; --mdc-icon-size: 16px !important; }
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Action button size | `.bubble-cover-button` | `width`, `height` |
| Action button shape | `.bubble-cover-button` | `border-radius` |
| Action button bg | `.bubble-cover-button` | `background-color` |
| Button icon size | `.bubble-cover-button-icon` | `--mdc-icon-size` |
| Open button only | `.bubble-open` | any property |
| Stop button only | `.bubble-stop` | any property |
| Close button only | `.bubble-close` | any property |
| Disabled style | `.bubble-cover-button.disabled` | `opacity` |
| Gap between buttons | `.bubble-buttons-container` | `gap` |
| Card background | `.bubble-background` | `background-color` |
| Card height | `.bubble-cover-container` | `height` or `grid_options: rows` |
