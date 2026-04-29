# CLAUDE.md — Bubble Card Modules Development Reference

This file is the authoritative development reference for this repository. All modules are YAML files that plug into [Bubble Card](https://github.com/Clooos/Bubble-Card) (v3.1.0+).

---

## Project layout

```
ha_bubblecard_modules/
└── <module_id>.yaml      # one file per module
```

Each file is a standalone module. The top-level key is the module ID (must be a valid YAML key, snake_case by convention). Module files go into `/config/bubble_card/modules/` on the HA host.

---

## Module YAML schema

```yaml
<module_id>:
  name: Human-readable name          # required
  version: '1.0'                     # string, semver or simple
  creator: Your Name                 # string
  link: https://…                    # optional URL to source/discussion
  supported:                         # omit to apply to all card types
    - button
    - calendar
    - climate
    - cover
    - horizontal-buttons-stack
    - media-player
    - pop-up
    - select
    - separator
  is_global: false                   # true = apply to all cards of supported types automatically
  description: |
    Free-text description shown in the module editor UI.
    HTML tags like <code-block><pre>…</pre></code-block> render formatted code samples.
  code: |-
    /* CSS goes here directly */
    .bubble-icon-container {
      min-width: ${this.config.<module_id>?.panel_width ?? 110}px !important;
    }
  editor:                            # optional — generates UI sliders/inputs for config
    - name: panel_width
      label: Panel width (px)
      default: 110
      selector:
        number:
          min: 60
          max: 200
          step: 2
          mode: slider
          unit_of_measurement: px
```

---

## The `code` field

The `code` value is a CSS+JS template string. Bubble Card evaluates `${…}` expressions at render time inside a context where `this` is the card element.

### Config access

```js
this.config.<module_id>?.<field>          // read a user-configured value
this.config.<module_id>?.<field> ?? 110   // with fallback default
```

Always use optional chaining (`?.`) — the module config object may be absent if the user hasn't configured it.

### Inline expression

```css
min-width: ${this.config.my_module?.size ?? 80}px !important;
```

### Block expression (for conditional logic)

```css
color: ${(() => {
  const val = this.config.my_module?.color ?? 'blue';
  return `var(--${val}-color)`;
})()};
```

### What `this` exposes

| Property | Type | Notes |
|----------|------|-------|
| `this.config` | object | Full card YAML config including all module configs |
| `this.hass` | object | Home Assistant connection (`this.hass.states['light.x']`) |
| `this.config.<module_id>` | object or undefined | This module's user config |

---

## CSS DOM structure by card type

All card types are built on a shared **base structure** plus type-specific additions. Classes shown are what exist in the rendered shadow DOM.

### Shared base structure

Every card type (except pop-up and horizontal-buttons-stack) renders:

```
.bubble-<type>-container  .bubble-container              ← mainContainer
└── .bubble-<type>  .bubble-wrapper                      ← cardWrapper
    ├── .bubble-background                               ← background
    ├── .bubble-content-container                        ← contentContainer
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container      ← iconContainer
    │   │   ├── ha-icon.bubble-main-icon
    │   │   │         .bubble-icon  .icon                ← icon element
    │   │   ├── .bubble-icon-feedback-container
    │   │   │   .bubble-feedback-container               ← icon feedback ripple
    │   │   │   └── .bubble-icon-feedback
    │   │   │       .bubble-feedback-element
    │   │   │       .feedback-element
    │   │   └── img.bubble-entity-picture                ← entity picture (optional)
    │   │          .entity-picture
    │   └── .bubble-name-container  .name-container      ← nameContainer
    │       ├── .bubble-name  .name                      ← name element
    │       └── .bubble-state  .state                    ← state text (optional)
    ├── .bubble-feedback-container  .feedback-container  ← card-level feedback
    │   └── .bubble-feedback-element  .feedback-element
    └── .bubble-buttons-container                        ← buttonsContainer (optional)
        └── [card-type-specific button elements]
```

The sub-button section (if configured) is appended inside `.bubble-buttons-container`:

```
.bubble-sub-button-container
└── .bubble-sub-button-group
    .position-<top|bottom>  .display-<inline|rows>
    .group-layout-<inline|rows>
    └── .bubble-sub-button  .bubble-sub-button-<n>  .<name_class>
        ├── .bubble-feedback-container
        │   └── .bubble-feedback-element  .feedback-element
        └── .bubble-sub-button-name-container
```

### button

Extra classes added on top of the base structure:

| Element | Additional classes |
|---------|--------------------|
| mainContainer | `bubble-button-card-container` (also `bubble-button-slider-container` when type=slider) |
| cardWrapper | `bubble-button-card` |
| background | `bubble-button-background` |

State classes on cardWrapper: `active`, `inactive`

### climate

The base `.bubble-buttons-container` is replaced by a temperature control structure:

```
.bubble-temperature-container
├── .bubble-climate-minus-button
│   ├── ha-icon.bubble-climate-minus-button-icon
│   └── ha-ripple
├── .bubble-temperature-display  .bubble-climate-temp-display
└── .bubble-climate-plus-button
    ├── ha-icon.bubble-climate-plus-button-icon
    └── ha-ripple

.bubble-target-temperature-container         ← when entity has low/high range
├── .bubble-low-temp-container
│   └── [same minus/display/plus structure]
│       └── .bubble-low-temperature-display  .bubble-climate-temp-display
└── .bubble-high-temp-container
    └── [same minus/display/plus structure]
        └── .bubble-high-temperature-display  .bubble-climate-temp-display
```

The background also gets `.bubble-color-background`.

`.tap-warning` animation is applied to the temperature display when the user taps at a limit.

### cover

The `.bubble-buttons-container` contains three buttons:

```
.bubble-buttons-container  .bubble-buttons  .buttons-container
├── .bubble-cover-button  .bubble-button  .bubble-open  .button  .open
│   ├── .bubble-feedback-container
│   │   └── .bubble-feedback-element  .feedback-element
│   ├── ha-icon.bubble-cover-button-icon  .bubble-icon-open
│   └── ha-ripple
├── .bubble-cover-button  .bubble-button  .bubble-stop  .button  .stop
│   └── [same structure]
└── .bubble-cover-button  .bubble-button  .bubble-close  .button  .close
    └── [same structure]
```

Disabled state: `.bubble-button.disabled` (opacity 0.3, pointer-events none).

### media-player

Extra elements beyond the base structure:

```
.bubble-cover-background                             ← background (backward-compat alias)
.bubble-icon-container
└── ha-icon.bubble-mute-button  .is-hidden           ← mute icon (hidden by default)

.bubble-content-container
└── .bubble-media-info-container
    ├── .bubble-title
    └── .bubble-artist

.bubble-button-container                             ← buttonsContainer (backward-compat alias)
├── .bubble-power-button       .bubble-media-button
├── .bubble-previous-button    .bubble-media-button
├── .bubble-next-button        .bubble-media-button
├── .bubble-volume-button      .bubble-media-button
└── .bubble-play-pause-button  .bubble-media-button
    └── ha-icon.bubble-media-button-icon (inside each)

.bubble-volume-slider-wrapper  .is-hidden            ← shown when volume active
├── .bubble-volume-slider-mute-button  .bubble-media-button
├── .bubble-volume-slider
└── .bubble-volume-slider-close-button  .bubble-media-button
```

Layout modifier classes: `large`, `full-width`, `bottom-fixed`, `fixed-top`.

### pop-up

Pop-up has a completely different structure — no base structure is used:

```
<bubble-card> (host, shadow DOM)
└── .bubble-backdrop-host  (shadow host for backdrop)
    └── .bubble-backdrop  .backdrop  [.is-hidden | .is-visible]

.bubble-pop-up  .pop-up
[.is-popup-closed | .is-popup-opened | .is-opening | .is-closing]
[.no-header]  [.large]
├── .bubble-pop-up-background
├── .bubble-header-container
│   ├── .bubble-header
│   │   └── .bubble-button-container           ← header button (entity/icon/name)
│   └── .bubble-close-button  .close-pop-up
│       ├── .bubble-feedback-container
│       │   └── .bubble-feedback-element  .feedback-element
│       └── ha-icon.bubble-close-icon
└── .bubble-pop-up-container                   ← scrollable card content
    └── [child cards]
```

### select

Same as base structure with one extra class:

| Element | Additional class |
|---------|-----------------|
| mainContainer | `bubble-select-card-container` |

`.bubble-background` gets `cursor: pointer`.

### horizontal-buttons-stack

Completely different structure — no base structure used:

```
.bubble-horizontal-buttons-stack-card-container
.horizontal-buttons-stack-container              ← mainContainer
└── .horizontal-buttons-stack-card
    [.has-gradient]
    └── .card-content                            ← horizontally scrollable, mask-image gradient edges
        ├── .bubble-button  .bubble-button-0  .button  .<link_hash>
        │   [.highlight when active view matches link]
        │   ├── ha-icon.bubble-icon  .icon
        │   ├── .bubble-name  .name
        │   ├── .bubble-background-color  .background-color
        │   ├── .bubble-background  .background
        │   └── ha-ripple
        └── .bubble-button  .bubble-button-1  ...
```

Scroll state classes on `.card-content`: `.is-scrolled`, `.is-maxed-scroll`.

---

## Editor schema reference

The `editor` key is an array of field objects. Fields appear in the Bubble Card module editor UI.

### Common field properties

```yaml
- name: field_key          # key used in this.config.<module_id>.field_key
  label: Display label     # shown above the input
  default: 80              # default value (cosmetic only — not injected into config)
  required: false
  disabled: false
```

### Selector types

```yaml
selector:
  number:
    min: 0
    max: 200
    step: 1
    mode: slider            # or "box"
    unit_of_measurement: px

selector:
  text:
    multiline: false

selector:
  boolean: {}

selector:
  select:
    options:
      - value: left
        label: Left
      - value: right
        label: Right

selector:
  color: {}                 # colour picker

selector:
  icon: {}                  # HA icon picker

selector:
  entity:
    domain: light           # optional filter

selector:
  device: {}

selector:
  area: {}
```

Other selectors exist (`time`, `date`, `action`, `condition`, `theme`, etc.) but have not all been tested with Bubble Card modules.

### Grid layout (advanced)

```yaml
- type: grid
  schema:
    - name: field_a
      label: Field A
      selector:
        number: { min: 0, max: 100 }
    - name: field_b
      label: Field B
      selector:
        number: { min: 0, max: 100 }
  column_min_width: 150px
```

### Expandable section (advanced)

```yaml
- type: expandable
  title: Advanced options
  icon: mdi:cog
  schema:
    - name: advanced_field
      label: Advanced field
      selector:
        text: {}
```

---

## Coding conventions

- Module IDs are `snake_case`. The YAML top-level key, the config access path (`this.config.<id>`), and the filename (`<id>.yaml`) must all match.
- Always use `!important` on CSS overrides — Bubble Card's own styles use it and specificity battles are unpredictable.
- Always use optional chaining and a fallback: `this.config.my_module?.field ?? defaultValue`. The config object is undefined until the user saves settings.
- Scope CSS rules by card-type-specific classes when a rule should not apply to all supported types. Example: `.bubble-button-card .bubble-name-container` targets only button/state cards, not media player.
- When both left sides of the card are clipped by a negative margin/overflow trick, set `border-top-left-radius: 0` and `border-bottom-left-radius: 0` explicitly — do not rely on the card's default radius.
- Comment only non-obvious constraints (e.g. "scoped via .bubble-button-card which only exists on button-type cards"). Do not comment what the CSS visually does.
- Use `min-width` + `max-width` set to the same value to lock an element's width against reflow.
- `align-self: stretch` + `height: 100%` gives a child element full card height.

---

## Testing a module

1. Copy the YAML file to `/config/bubble_card/modules/` on the HA host.
2. In the HA dashboard, edit a card, open the **Modules** tab, and enable the module.
3. Use browser DevTools on the HA frontend to inspect shadow DOM and confirm class names.
4. The `supported` list controls which card types the module appears on in the UI — keep it accurate.