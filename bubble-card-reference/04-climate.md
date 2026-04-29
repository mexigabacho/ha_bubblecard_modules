# Climate Card

> `card_type: climate`  
> Source: `src/cards/climate/create.js` + `styles.css` + `changes.js`

Uses the full base structure. See [01-base-structure.md](01-base-structure.md) for the shared DOM.

---

## Full DOM hierarchy

```
.bubble-climate-container  .bubble-container         ← mainContainer
[.with-bottom-buttons]
[.is-on | .is-off | .is-unavailable]
[.large | .rows-2]
│
└── .bubble-climate  .bubble-wrapper
    ├── .bubble-background  .bubble-color-background  ← background; "color-background" is a backward-compat alias
    │   [background-color set dynamically by JS based on HVAC mode]
    │
    ├── .bubble-content-container
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container
    │   │   ├── ha-icon.bubble-main-icon  .bubble-icon  .icon
    │   │   │   [color set by JS to HVAC mode color]
    │   │   └── div.bubble-entity-picture  .entity-picture
    │   └── .bubble-name-container  .name-container
    │       ├── .bubble-name  .name
    │       └── .bubble-state  .state
    │
    ├── .bubble-feedback-container  .feedback-container
    │   └── .bubble-feedback-element  .feedback-element
    │
    ├── .bubble-buttons-container                     ← holds temperature controls
    │   │
    │   ├── .bubble-temperature-container             ← single-target temperature (most entities)
    │   │   [.hidden]  ← when hide_temperature: true or unavailable
    │   │   ├── .bubble-climate-minus-button
    │   │   │   ├── ha-icon.bubble-climate-minus-button-icon
    │   │   │   └── ha-ripple
    │   │   ├── .bubble-temperature-display  .bubble-climate-temp-display
    │   │   └── .bubble-climate-plus-button
    │   │       ├── ha-icon.bubble-climate-plus-button-icon
    │   │       └── ha-ripple
    │   │
    │   └── .bubble-target-temperature-container      ← dual-target temperature (heat_cool mode)
    │       [.hidden]  ← when both targets hidden
    │       ├── .bubble-low-temp-container
    │       │   [.hidden]  ← when hide_target_temp_low: true
    │       │   [color: var(--state-climate-heat-color)]
    │       │   ├── .bubble-climate-minus-button
    │       │   ├── .bubble-low-temperature-display  .bubble-climate-temp-display
    │       │   └── .bubble-climate-plus-button
    │       └── .bubble-high-temp-container
    │           [.hidden]  ← when hide_target_temp_high: true
    │           [color: var(--state-climate-cool-color)]
    │           ├── .bubble-climate-minus-button
    │           ├── .bubble-high-temperature-display  .bubble-climate-temp-display
    │           └── .bubble-climate-plus-button
    │
    ├── .bubble-sub-button-container                  ← top sub-buttons (when configured)
    └── .bubble-sub-button-bottom-container           ← bottom sub-buttons (when configured)
```

---

## Runtime behaviour

### Background color

`changeStyle()` sets `background-color` on `.bubble-background.bubble-color-background` dynamically via `getClimateColor()`:

| HVAC mode | Color variable used |
|-----------|-------------------|
| `heat` | `var(--state-climate-heat-color)` |
| `cool` | `var(--state-climate-cool-color)` |
| `heat_cool` / `auto` | `var(--state-climate-auto-color)` |
| `dry` | `var(--state-climate-dry-color)` |
| `fan_only` | `var(--state-climate-fan_only-color)` |
| `off` | transparent / none |

These are HA theme variables — defined by your HA theme.

### Temperature display

- `changeTemperature()` updates `.bubble-temperature-display` text
- `changeTargetTempLow()` / `changeTargetTempHigh()` update the dual containers
- The containers are toggled `.hidden` based on entity state and config options

### Tap-warning animation

When user taps +/− at the temperature limit, the mainContainer gets inline `animation: tap-warning 0.4s` for a shake effect. The keyframe is defined in the card's styles:

```css
@keyframes tap-warning {
    10%, 90% { transform: translateX(-1px); }
    20%, 80% { transform: translateX(1px); }
    30%, 50%, 70% { transform: translateX(-2px); }
    40%, 60% { transform: translateX(2px); }
}
```

---

## `full-width` layout (large layout with bottom-fixed buttons)

In large layout, when buttons are positioned at the bottom, temperature containers become full-width:

```css
.full-width > .bubble-temperature-container,
.full-width > .bubble-target-temperature-container { ... }
.full-width .bubble-climate-minus-button,
.full-width .bubble-climate-plus-button { flex: 1; }
.full-width .bubble-climate-temp-display { flex: 1; height: 36px; }
```

---

## CSS variables (climate-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-climate-button-background-color` | `var(--bubble-secondary-background-color)` | Temperature container bg |
| `--bubble-climate-background-color` | (set by JS per HVAC mode) | Background fill override |
| `--bubble-sub-button-border-radius` | `var(--bubble-border-radius)` | Temperature button radius |
| `--state-climate-heat-color` | HA theme | Low-temp container text color |
| `--state-climate-cool-color` | HA theme | High-temp container text color |

---

## Key CSS targeting patterns

```css
/* Background — color driven by JS, you can override */
.bubble-climate .bubble-color-background {
    background-color: rgba(59, 130, 246, 0.3) !important;
}

/* Temperature containers */
.bubble-temperature-container { ... }
.bubble-target-temperature-container { ... }
.bubble-low-temp-container { ... }
.bubble-high-temp-container { ... }

/* Temperature display value text */
.bubble-climate-temp-display { ... }

/* +/- buttons */
.bubble-climate-minus-button,
.bubble-climate-plus-button { ... }

/* +/- button icons */
.bubble-climate-minus-button-icon,
.bubble-climate-plus-button-icon { --mdc-icon-size: 16px; }

/* State-reactive */
.is-on .bubble-color-background { ... }   /* entity is on */
.is-off .bubble-color-background { ... }  /* entity is off */

/* Cancel sub-button icon bleed */
.bubble-sub-button .bubble-icon { color: inherit !important; --mdc-icon-size: 16px !important; }
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Background fill (override JS) | `.bubble-climate .bubble-color-background` | `background-color` |
| Temperature container bg | `.bubble-temperature-container` | `background-color` |
| Temp display text size | `.bubble-climate-temp-display` | `font-size` |
| +/- button size | `.bubble-climate-minus-button` | `width`, `height` |
| +/- icon size | `.bubble-climate-minus-button-icon` | `--mdc-icon-size` |
| Low-temp color | `.bubble-low-temp-container` | `color` |
| High-temp color | `.bubble-high-temp-container` | `color` |
| Icon color (HVAC mode) | set by JS via `getClimateColor()` | override with `.bubble-icon-container { color: X !important }` |
| Card height | `.bubble-climate-container` | `height` or `grid_options: rows` |
