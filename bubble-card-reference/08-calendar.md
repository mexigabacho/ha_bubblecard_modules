# Calendar Card

> `card_type: calendar`  
> Source: `src/cards/calendar/create.js` + `styles.css` + `changes.js`

Does **not** use the base card elements (`withBaseElements: false`). Only `mainContainer` is created by the base; all calendar content is added separately. Sub-buttons are supported.

---

## Full DOM hierarchy

```
.bubble-calendar-container  .bubble-container        ← mainContainer (from base; no base elements)
[.with-bottom-buttons]
│
├── .bubble-calendar-content                         ← prepended by calendar (before sub-buttons)
│   [.can-scroll-top]                               ← mask-image fade applied at top when scrollable
│   [.can-scroll-bottom]                            ← mask-image fade applied at bottom when scrollable
│   │
│   └── [per-day blocks, built dynamically by changeEvents()]
│       .bubble-day-wrapper
│       [+ .bubble-day-wrapper::before — 2px separator line between days]
│       ├── .bubble-day-chip                        ← 42×42px circle with day number + month
│       │   [.is-active]                            ← added when chip is today's date
│       │   ├── .bubble-day-number                  ← e.g. "29"
│       │   └── .bubble-day-month                   ← e.g. "Apr"
│       │
│       └── .bubble-day-events                      ← event list for this day
│           └── .bubble-event                       ← one per event
│               ├── .bubble-event-time              ← "9:00 AM" or "All day"
│               ├── .bubble-event-color             ← 12×12px colored dot
│               └── .bubble-event-name-wrapper
│                   ├── .bubble-event-name          ← event title (truncated)
│                   └── .bubble-event-place         ← location (optional)
│                       ├── .bubble-event-place-icon
│                       └── [text]
│
├── .bubble-sub-button-container                     ← top sub-buttons; `position: sticky; top: 0`
└── .bubble-sub-button-bottom-container              ← bottom sub-buttons (when configured)
```

> **Note**: There is no `.bubble-background`, `.bubble-icon-container`, `.bubble-name-container`, or `.bubble-buttons-container`. The calendar card is entirely its own content.

---

## Calendar height

The card height is set via a CSS custom property at creation time:

```js
elements.mainContainer.style.setProperty(
    '--bubble-calendar-height',
    `${(context.config.rows ?? 1) * 56}px`
);
```

The container height: `var(--bubble-calendar-height, 56px)`. Set `rows:` in the card config to control this.

---

## Scroll masking

The `.bubble-calendar-content` has scroll-fade masks applied dynamically:

```css
.can-scroll-top    → top fade mask (transparent to black)
.can-scroll-bottom → bottom fade mask (black to transparent)
.can-scroll-top.can-scroll-bottom → both fades simultaneously
```

These are toggled by a scroll observer as the user scrolls. The mask size is controlled by `--bubble-calendar-mask-size` (default 16px).

---

## Event rendering details

- Events are fetched via HA's calendar API and grouped by day
- Colors come from the `entity.color` field in the card YAML config per calendar entity
- `is-active` class on `.bubble-day-chip` highlights today
- A `::before` pseudo-element on `.bubble-day-wrapper + .bubble-day-wrapper` draws the 2px separator line between day groups

---

## CSS variables (calendar-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-calendar-height` | `56px × rows` | Card height (set by JS) |
| `--bubble-calendar-mask-size` | `16px` | Height of scroll fade masks |
| `--bubble-calendar-border-radius` | `var(--bubble-border-radius, 32px)` | Event + chip corner radius |
| `--bubble-event-background-color` | transparent | Event row background |
| `--bubble-event-background-image` | none | Event row background image |
| `--bubble-button-icon-background-color` | secondary bg | Day chip background |
| `--bubble-button-icon-border-radius` | 50% | Day chip shape |

---

## Key CSS targeting patterns

```css
/* Card container */
.bubble-calendar-container { ... }
.bubble-calendar-content { overflow: scroll; }

/* Day group */
.bubble-day-wrapper { ... }

/* Day chip (today highlighted with .is-active) */
.bubble-day-chip { background-color: rgba(59, 130, 246, 0.2) !important; }
.bubble-day-chip.is-active { background-color: var(--bubble-accent-color) !important; }
.bubble-day-number { ... }
.bubble-day-month { ... }

/* Event row */
.bubble-event { background-color: rgba(255,255,255,0.05) !important; }
.bubble-event-time { ... }
.bubble-event-name { ... }
.bubble-event-color { ... }  /* the colored dot */
.bubble-event-place { ... }

/* Day separator line */
.bubble-day-wrapper + .bubble-day-wrapper::before {
    background-color: rgba(255,255,255,0.1) !important;
}

/* Sub-button container is sticky on calendars */
.bubble-calendar-container .bubble-sub-button-container {
    position: sticky !important;
    top: 0;
}
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Card height | `--bubble-calendar-height` CSS var | Set via `rows:` in card config |
| Event row background | `.bubble-event` | `background-color` |
| Event name font | `.bubble-event-name` | `font-size`, `font-weight` |
| Event time | `.bubble-event-time` | `font-size`, `opacity` |
| Event color dot | `.bubble-event-color` | `border-radius`, `width`, `height` |
| Day chip shape | `.bubble-day-chip` | `border-radius` |
| Today chip highlight | `.bubble-day-chip.is-active` | `background-color` |
| Day number size | `.bubble-day-number` | `font-size` |
| Day month label | `.bubble-day-month` | `font-size` |
| Separator between days | `.bubble-day-wrapper + .bubble-day-wrapper::before` | `background-color`, `height` |
| Scroll fade size | `--bubble-calendar-mask-size` | `16px` default |
