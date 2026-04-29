# Base Card Structure

> Applies to: `button`, `media-player`, `climate`, `cover`, `select`  
> Partial: `separator`, `calendar`  
> Does NOT apply to: `pop-up`, `horizontal-buttons-stack`

Source: `src/components/base-card/create.js` + `src/components/base-card/styles.css`

---

## DOM hierarchy

```
.bubble-<type>-container  .bubble-container          ← mainContainer
[.with-bottom-buttons]                               ← added when bottom sub-buttons OR main_buttons_position: bottom
└── .bubble-<type>  .bubble-wrapper                  ← cardWrapper
    ├── .bubble-background                           ← background (prepended; has tap-action feedback)
    ├── .bubble-content-container                    ← contentContainer
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container  ← iconContainer
    │   │   ├── ha-icon.bubble-main-icon
    │   │   │         .bubble-icon  .icon            ← actual icon element
    │   │   ├── div.bubble-entity-picture            ← entity picture (optional, shown when image available)
    │   │   │      .entity-picture
    │   │   └── .bubble-icon-feedback-container      ← only created when icon has a tap action
    │   │       .bubble-feedback-container
    │   │       └── .bubble-icon-feedback
    │   │           .bubble-feedback-element
    │   │           .feedback-element
    │   └── .bubble-name-container  .name-container  ← nameContainer
    │       ├── .bubble-name  .name
    │       └── .bubble-state  .state                ← state text (optional; hidden by default on some button types)
    ├── .bubble-feedback-container                   ← only created when card background has a tap action
    │   .feedback-container
    │   └── .bubble-feedback-element  .feedback-element
    ├── .bubble-buttons-container                    ← buttonsContainer (card-type-specific content inside)
    └── [sub-button containers — see below]
```

---

## Runtime state classes

Applied to **`mainContainer`** (`.bubble-<type>-container`):

| Class | When |
|-------|------|
| `.is-on` | Entity state is considered "on" |
| `.is-off` | Entity state is considered "off" |
| `.is-unavailable` | Entity state is `unavailable` |
| `.with-bottom-buttons` | Bottom sub-buttons exist OR `main_buttons_position: bottom` |
| `.large` | `card_layout: large` or section view |
| `.rows-2` | `card_layout: large-2-rows` |

Applied to **`cardWrapper`** (`.bubble-wrapper`):

| Class | When |
|-------|------|
| `.fixed-top` | Bottom sub-button group exists — pins content area to top of card |
| `.full-width` | `card_layout: large` with bottom-fixed buttons |
| `.bottom-fixed` | Main buttons moved to bottom position |
| `.fixed-top` | Any bottom group or `main_buttons_position: bottom` |

---

## Key CSS variables (base-card scope)

These are the variables you can set at theme level or card level to affect all cards sharing the base structure:

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-border-radius` | `calc(var(--row-height,56px)/2)` | Card corner radius |
| `--bubble-main-background-color` | `var(--secondary-background-color)` | Card background fill |
| `--bubble-icon-background-color` | `var(--secondary-background-color)` | Icon container background |
| `--bubble-icon-border-radius` | `var(--bubble-border-radius, 50%)` | Icon container corner radius |
| `--bubble-accent-color` | HA default | Active state highlight |
| `--bubble-box-shadow` | `none` | Card shadow |
| `--bubble-border` | `none` | Card border |
| `--mdc-icon-size` | (HA default ~24px) | Icon size — set on `.bubble-icon` |
| `--row-height` | `56px` | Grid row height (section view) |
| `--row-size` | `1` | Number of rows card spans |
| `--row-gap` | `8px` | Gap between rows |

Card-type-specific overrides follow the pattern `--bubble-<card-type>-<property>`, e.g.:
- `--bubble-button-border-radius` overrides only button cards
- `--bubble-media-player-border-radius` overrides only media player

---

## CSS layout notes

- `.bubble-container` — `position: relative; overflow: hidden; height: 50px` (base)
- `.bubble-wrapper` — `position: absolute; display: flex; align-items: center; height/width: 100%; justify-content: space-between`
- `.bubble-content-container` — `display: contents` (normal) or `display: flex` (when `fixed-top`)
- `.bubble-name-container` — `flex-grow: 1; margin: 0 16px 0 4px`
- `.bubble-buttons-container` — `display: flex; margin-right: 8px; gap: 4px`

---

## Sub-buttons — v3.1+ sectioned schema

> **Always use this schema.** The old flat array format is legacy and deprecated.

```yaml
sub_button:
  main_layout: inline        # inline (default) | rows — how groups stack in the top area
  bottom_layout: inline      # inline (default) | rows — same for the bottom area
  main:
    - entity: light.desk     # individual button (auto-grouped when needed)
      name: Desk
    - group:                 # explicit group
        - entity: light.a
          name: A
        - entity: light.b
          name: B
      buttons_layout: inline # inline (default) | column — buttons within this group
      name: Group label
  bottom:
    - entity: sensor.temp
    - group:
        - entity: light.c
      buttons_layout: inline
      justify_content: center  # fill (default) | start | center | end
```

### Auto-grouping rules (important for DOM targeting)

- Individual `main` buttons → auto-wrapped into one group `g_main_auto` when `main_layout: rows`, or when explicit groups also exist, or when any `bottom` items exist.
- Individual `bottom` buttons → `g_bottom_auto` when alone; each gets its own `g_bottom_individual_<n>` when mixed with explicit bottom groups (to preserve YAML order).

### Sub-button DOM structure

```
.bubble-wrapper
├── [base card content]
│
├── .bubble-sub-button-container                     ← top area; only present when sub_button config exists
│   [.groups-layout-inline | .groups-layout-rows]
│   [.fixed-top]                                    ← when card is in fixed-top mode
│   └── .bubble-sub-button-group
│       .position-top
│       .display-<inline|column>                    ← from buttons_layout of this group
│       .group-layout-<inline|rows>                 ← from main_layout
│       [data-group-id="g_main_0 | g_main_auto | ..."]
│       └── .bubble-sub-button  .bubble-sub-button-<n>  [.<name-class>]
│           [.is-select]  [.fill-width]  [.content-<layout>]  [.hidden]
│           [.background-on | .background-off]
│           ├── .bubble-feedback-container
│           │   └── .bubble-feedback-element  .feedback-element
│           └── .bubble-sub-button-name-container
│
└── .bubble-sub-button-bottom-container              ← bottom area; only present when bottom items exist
    [.groups-layout-inline | .groups-layout-rows]
    [.alignment-lanes-active]                        ← present in inline layout with alignment lanes
    [.with-main-buttons-bottom]                      ← when main buttons are also in bottom position
    │
    ├── .bubble-sub-button-alignment-lane             ← one per alignment zone (inline layout only)
    │   .lane-<start|center|fill|end>
    │   [.lane-expand]                               ← lane gets flex-grow when needed
    │   └── .bubble-sub-button-group
    │       .position-bottom
    │       .display-<inline|column>
    │       .group-layout-<inline|rows>
    │       .alignment-<start|center|fill|end>
    │       [.alignment-fill-auto]
    │       └── .bubble-sub-button  ...
    │
    └── [more alignment lanes]
```

### `justify_content` → alignment class mapping

| YAML value | Resulting class |
|------------|----------------|
| `fill` (default) | `alignment-fill` |
| `start` / `flex-start` / `left` | `alignment-start` |
| `center` | `alignment-center` |
| `end` / `flex-end` / `right` | `alignment-end` |
| `space-between` / `space-around` / `space-evenly` / `stretch` | `alignment-fill` |

**Alignment lane CSS `order`**: start=1, center=2, fill=3, end=4.

### Sub-button name → CSS class

The `name` field produces a class: lowercased, accents stripped, non-alphanumeric runs → `-`, leading/trailing `-` stripped.  
`name: "My Button"` → `.my-button`  
Use this to target a specific sub-button without affecting others.

### Sub-button CSS variables

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-sub-button-height` | `36px` | Height of sub-buttons |
| `--bubble-sub-button-border-radius` | `var(--bubble-border-radius, 18px)` | Sub-button corners |
| `--bubble-sub-button-background-color` | secondary bg | Off-state background |
| `--bubble-sub-button-light-background-color` | accent color | On-state background |
| `--bubble-sub-button-dark-text-color` | `rgb(0,0,0)` | Text on bright backgrounds |
| `--bubble-sub-button-justify-content` | `end` | Alignment within sub-button container |

---

## Targeting tips

```css
/* Main icon container — scoped to avoid sub-button bleed */
.bubble-button-card > .bubble-icon-container { ... }

/* Icon only — MUST cancel on sub-buttons */
.bubble-icon { size rule !important; }
.bubble-sub-button .bubble-icon { cancel rule !important; }

/* State-reactive */
.is-on .bubble-icon-container { ... }
.is-off .bubble-background { ... }
.is-unavailable .bubble-wrapper { ... }

/* Specific sub-button by name */
.my-button { ... }           /* targets sub-button named "My Button" */

/* Bottom sub-button area */
.bubble-sub-button-bottom-container .bubble-sub-button { ... }

/* Only top sub-buttons */
.bubble-sub-button-container .bubble-sub-button { ... }
```
