# CLAUDE.md — Bubble Card Modules Development Reference

Authoritative development reference for this repository. All modules are YAML files targeting [Bubble Card](https://github.com/Clooos/Bubble-Card) **v3.1.6** (stable as of Apr 2026; v3.2.0 in beta).

---

## Project layout

```
ha_bubblecard_modules/
└── <module_id>.yaml      # one file per module
```

Each file is a standalone module, top-level key = module ID (snake_case). Deploy to `/config/bubble_card/modules/` on the HA host.

---

## Module YAML schema

```yaml
<module_id>:
  name: Human-readable name          # required
  version: '1.0'                     # string
  creator: Your Name
  link: https://…                    # optional URL
  supported:                         # omit = all card types
    - button
    - calendar
    - climate
    - cover
    - horizontal-buttons-stack
    - media-player
    - pop-up
    - select
    - separator
  is_global: false                   # true = auto-apply to all supported cards
  description: |
    Free-text shown in the module editor.
    <code-block><pre>yaml example here</pre></code-block> renders as formatted code.
  code: |-
    /* CSS + JS template — see "code field" section below */
  editor:                            # optional UI config panel
    - name: my_field
      label: My field
      default: 80
      selector:
        number: { min: 0, max: 200, step: 1, mode: slider, unit_of_measurement: px }
```

---

## The `code` field

The `code` value is a CSS+JS template string. `${…}` expressions are evaluated at render time.

### Available template variables

| Variable | Type | Notes |
|----------|------|-------|
| `this.config` | object | Full card YAML config |
| `this.config.<module_id>` | object \| undefined | This module's user settings |
| `this.hass` | object | HA connection object |
| `hass` | object | Alias for `this.hass` |
| `entity` | string | Card's entity_id |
| `state` | string | Current state string of the card's entity |

### Config access pattern

Always use optional chaining with a default — the module config object is `undefined` until the user saves settings:

```js
this.config.my_module?.my_field ?? defaultValue
```

### Inline expression

```css
min-width: ${this.config.my_module?.size ?? 80}px !important;
```

### Block expression (for conditional logic)

```css
background: ${(() => {
  if (state === 'on') return 'rgba(59,130,246,0.3)';
  return 'none';
})()};
```

### Accessing HA state attributes

```js
hass.states[entity]?.attributes?.brightness
hass.states[entity]?.attributes?.rgb_color?.join(',')
```

---

## CSS DOM structure by card type

All card types are built on a shared **base structure** plus type-specific additions. These are the actual class names assigned by the source code.

### Shared base structure

Used by: button, climate, cover, media-player, select (calendar and separator use it partially; pop-up and HBS do not use it at all).

```
.bubble-<type>-container  .bubble-container          ← mainContainer
[.with-bottom-buttons]                               ← added when bottom sub-buttons or main_buttons_position: bottom
└── .bubble-<type>  .bubble-wrapper                  ← cardWrapper
    ├── .bubble-background                           ← background (prepended)
    ├── .bubble-content-container                    ← contentContainer
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container  ← iconContainer
    │   │   ├── ha-icon.bubble-main-icon
    │   │   │         .bubble-icon  .icon            ← icon element
    │   │   ├── div.bubble-entity-picture            ← entity picture (optional)
    │   │   │      .entity-picture
    │   │   └── .bubble-icon-feedback-container      ← only when icon has a tap action
    │   │       .bubble-feedback-container
    │   │       └── .bubble-icon-feedback
    │   │           .bubble-feedback-element
    │   │           .feedback-element
    │   └── .bubble-name-container  .name-container  ← nameContainer
    │       ├── .bubble-name  .name
    │       └── .bubble-state  .state                ← state text (optional)
    ├── .bubble-feedback-container                   ← only when card background has a tap action
    │   .feedback-container
    │   └── .bubble-feedback-element  .feedback-element
    └── .bubble-buttons-container                    ← buttonsContainer
        └── [card-type-specific content]
```

Sub-buttons are appended inside `.bubble-<type>.bubble-wrapper` (after the buttons container). See the **sub-buttons** section for full detail.

---

### button

Extra classes on top of the base structure:

| Element | Additional classes |
|---------|--------------------|
| mainContainer | `bubble-button-card-container` (also `bubble-button-slider-container` when type=slider) |
| cardWrapper | `bubble-button-card` |
| background | `bubble-button-background` |

State classes added to cardWrapper at runtime: `active`, `inactive`.

Full hierarchy example:

```
.bubble-button-container  .bubble-container  .bubble-button-card-container
└── .bubble-button  .bubble-wrapper  .bubble-button-card
    ├── .bubble-background  .bubble-button-background
    ├── .bubble-content-container
    │   ├── .bubble-main-icon-container  .bubble-icon-container  .icon-container
    │   │   └── ha-icon.bubble-main-icon  .bubble-icon  .icon
    │   └── .bubble-name-container  .name-container
    │       ├── .bubble-name  .name
    │       └── .bubble-state  .state
    └── .bubble-buttons-container
```

---

### media-player

Built on the base structure with these additions:

| Element | Classes |
|---------|---------|
| background | also gets `bubble-cover-background` (backward-compat alias) |
| buttonsContainer | also gets `bubble-button-container` (backward-compat alias) |

Extra elements created inside the card:

```
.bubble-icon-container
└── .bubble-media-button  .bubble-mute-button  [.is-hidden]   ← inside icon container

.bubble-content-container
└── .bubble-media-info-container                              ← appended after nameContainer
    ├── .bubble-title
    └── .bubble-artist

.bubble-buttons-container  .bubble-button-container           ← media control buttons
├── .bubble-media-button  .bubble-power-button
│   ├── .bubble-feedback-container
│   │   └── .bubble-feedback-element  .feedback-element
│   ├── ha-icon.bubble-media-button-icon
│   └── ha-ripple
├── .bubble-media-button  .bubble-previous-button             ← same structure
├── .bubble-media-button  .bubble-next-button
├── .bubble-media-button  .bubble-volume-button
└── .bubble-media-button  .bubble-play-pause-button

.bubble-volume-slider-wrapper  [.is-hidden]                   ← appended to cardWrapper
├── .bubble-media-button  .bubble-volume-slider-mute-button
├── .bubble-volume-slider                                      ← slider container
└── .bubble-media-button  .bubble-volume-slider-close-button
```

Layout modifier classes (added at runtime to cardWrapper): `large`, `full-width`, `bottom-fixed`, `fixed-top`.

#### Cover art / album art background system

The media player has a dedicated crossfade system for showing album art in two places simultaneously. This is driven by `changeMediaIcon()` and `changeBackground()` in `changes.js`.

**Image source.** `getImage()` reads `entity_picture_local` then `entity_picture` from the HA entity state and calls `hass.hassUrl()` to get a full URL. Returns `''` when `force_icon: true` or an explicit `icon:` is configured. A cache-busting query param (`?v=<hash>`) is appended based on `media_content_id + media_title + media_artist` to handle proxy URLs that serve different art at the same URL (e.g. Apple TV).

**Two scopes.** Album art can appear in two places, each managed independently:

| Scope | Container element | Config required | Visual treatment |
|-------|------------------|-----------------|-----------------|
| `icon` | `.bubble-entity-picture` (inside `.bubble-icon-container`) | always active when art is available | full opacity, `cover`/`center` |
| `background` | `.bubble-background.bubble-cover-background` | `cover_background: true` | `filter: blur(50px); opacity: 0.5` (whole element) |

**Crossfade DOM mutation.** The first time art appears for a given scope, `ensureCoverLayers()` permanently transforms the container element:

1. Clears all children of the container.
2. Adds class `bubble-cover-icon-crossfade` (icon scope) or `bubble-cover-background-crossfade` (background scope) to the container.
3. Inserts two absolutely-positioned layer divs inside it:

```
.bubble-entity-picture  (or .bubble-background.bubble-cover-background)
  [.bubble-cover-icon-crossfade | .bubble-cover-background-crossfade]   ← added to container
  ├── .bubble-cover-crossfade-layer
  │   .bubble-cover-crossfade-layer--icon  (or --background)
  │   .is-visible                          ← active layer, opacity: 1
  └── .bubble-cover-crossfade-layer
      .bubble-cover-crossfade-layer--icon  (or --background)
                                           ← inactive layer, opacity: 0
```

**Crossfade transition.** `crossfadeTo()` swaps which layer is visible:
- Preloads the new image via `new Image()` to avoid a blank flash.
- On load: sets `background-image: url(...)` on the *inactive* layer, adds `.is-visible` to it.
- 50 ms later (via `requestAnimationFrame`): removes `.is-visible` from the *current* layer.
- CSS `transition: opacity 2s ease` does the 2-second blend.
- On image load error: marks the layer `.is-empty` (stays at opacity 0).
- Fading *out* (imageUrl = `''`): sets `background-image: ''`, adds `.is-empty`, then swaps.

**State machine.** `evaluateCoverState()` on every render update:
- `MEDIA_COVER_RESET_STATES` = `off`, `unavailable`, `unknown`, `standby` — clear art immediately.
- `idle` — start a 2000 ms timeout, then fade out (art is preserved briefly to avoid flicker on track change).
- The last known URL is cached in `_mediaCoverState.cachedUrl` and survives idle transitions until the timeout fires.

**CSS for the crossfade layers** (from `media-player/styles.css`):

```css
.bubble-cover-icon-crossfade,
.bubble-cover-background-crossfade {
    position: absolute; inset: 0; overflow: hidden;
}
.bubble-cover-crossfade-layer {
    position: absolute; inset: 0;
    background-size: cover; background-position: center;
    opacity: 0; transition: opacity 2s ease; pointer-events: none;
}
.bubble-cover-crossfade-layer.is-visible { opacity: 1; }
.bubble-cover-crossfade-layer.is-empty   { opacity: 0; }
.bubble-cover-crossfade-layer--icon      { z-index: 0; }

/* Background scope: blur applied to the whole container, layers inside inherit it */
.bubble-background {
    background-size: cover; background-position: center;
    filter: blur(50px); opacity: 0.5;
}
```

**Important for module CSS targeting the media player background:**
- Once cover art has appeared, `.bubble-background.bubble-cover-background` no longer has a `background-image` set directly on it — the image lives in the child crossfade layers.
- The `filter: blur(50px)` is on the container, so it blurs everything inside including the layers.
- The `.bubble-entity-picture` element switches from a simple `background-image` div to a crossfade host — do not set `background-image` directly on it once the system has initialized.

---

### cover

Extra on buttonsContainer: `bubble-buttons  buttons-container`

```
.bubble-buttons-container  .bubble-buttons  .buttons-container
├── .bubble-cover-button  .bubble-button  .bubble-open  .button  .open
│   ├── .bubble-feedback-container
│   │   └── .bubble-feedback-element  .feedback-element
│   ├── ha-icon.bubble-cover-button-icon  .bubble-icon-open
│   └── ha-ripple
├── .bubble-cover-button  .bubble-button  .bubble-stop  .button  .stop
│   └── [same — icon class: .bubble-icon-stop]
└── .bubble-cover-button  .bubble-button  .bubble-close  .button  .close
    └── [same — icon class: .bubble-icon-close]
```

Disabled state: `.bubble-button.disabled` (opacity 0.3, pointer-events none).

---

### climate

Extra on background: `bubble-color-background`

The `.bubble-buttons-container` holds temperature controls:

```
.bubble-buttons-container
├── .bubble-temperature-container                    ← single target temperature
│   ├── .bubble-climate-minus-button
│   │   ├── ha-icon.bubble-climate-minus-button-icon
│   │   └── ha-ripple
│   ├── .bubble-temperature-display  .bubble-climate-temp-display
│   └── .bubble-climate-plus-button
│       ├── ha-icon.bubble-climate-plus-button-icon
│       └── ha-ripple
└── .bubble-target-temperature-container             ← only when entity has low/high range
    ├── .bubble-low-temp-container
    │   └── [minus / .bubble-low-temperature-display.bubble-climate-temp-display / plus]
    └── .bubble-high-temp-container
        └── [minus / .bubble-high-temperature-display.bubble-climate-temp-display / plus]
```

Animation class applied at runtime to mainContainer: `tap-warning` (when user taps at temp limit).

---

### select

Base structure only, plus one extra class on mainContainer: `bubble-select-card-container`.

`.bubble-background` gets `cursor: pointer`.

---

### separator

Does **not** use the standard base content elements (`withBaseElements: false`). Custom structure:

```
.bubble-container  .bubble-separator  .separator-container   ← mainContainer (custom)
├── ha-icon.bubble-icon
├── h4.bubble-name
└── .bubble-line
```

Sub-buttons are still supported and are appended via `createSubButtonStructure`.

---

### calendar

Uses `withBaseElements: false` — no icon, name, or state elements. Only:

```
.bubble-calendar-container  .bubble-container               ← mainContainer
└── .bubble-calendar-content                                ← prepended
```

Sub-buttons supported.

---

### pop-up

Completely different structure — does **not** use the base structure. The card modifies an existing `#root` element inside a vertical-stack:

```
document.body
└── .bubble-backdrop-host                                    ← shadow DOM host, one global instance
    └── (shadow root)
        ├── .bubble-backdrop  .backdrop  [.is-hidden | .is-visible]
        │   [.has-blur]                                      ← when backdrop_blur > 0
        ├── <style>                                          ← backdrop styles
        └── <style data-bubble-target="backdrop">            ← custom backdrop styles

#root (vertical-stack's root element)
  becomes: .bubble-pop-up  .pop-up
  state classes: .is-popup-closed | .is-popup-opened | .is-opening | .is-closing
  modifier classes: .no-header, .large (when applicable)
  ├── .bubble-pop-up-background
  ├── .bubble-header-container
  │   ├── .bubble-header
  │   │   └── .bubble-button-container                      ← header entity button renders here
  │   └── .bubble-close-button  .close-pop-up
  │       ├── .bubble-feedback-container
  │       │   └── .bubble-feedback-element  .feedback-element
  │       ├── ha-icon.bubble-close-icon
  │       └── ha-ripple
  └── .bubble-pop-up-container                              ← scrollable, holds child cards
      └── [child cards]
```

---

### horizontal-buttons-stack

Does **not** use the base structure at all:

```
context.card (the HA card element)
  gets: .horizontal-buttons-stack-card
  [.has-gradient]                                           ← unless hide_gradient: true

.card-content (HA's built-in scroll wrapper)
  scroll state classes: .is-scrolled, .is-maxed-scroll

.bubble-horizontal-buttons-stack-card-container
.horizontal-buttons-stack-container                         ← cardContainer, inside card-content
├── .bubble-button  .bubble-button-1  .button  .<link-hash> ← per button (1-indexed)
│   [.highlight]                                            ← when current view matches link
│   ├── ha-icon.bubble-icon  .icon
│   ├── .bubble-name  .name
│   ├── .bubble-background-color  .background-color
│   ├── .bubble-background  .background
│   └── ha-ripple
└── .bubble-button  .bubble-button-2  ...
```

---

## Sub-buttons

Sub-buttons have a rich layout system added in v3.1+. The sectioned YAML schema separates top (`main`) and bottom (`bottom`) button areas, each supporting explicit groups.

### YAML schema (sectioned, current)

```yaml
sub_button:
  main_layout: inline          # or rows — how groups stack vertically in the top area
  bottom_layout: inline        # or rows — same for the bottom area
  main:
    - entity: light.desk       # individual button (auto-grouped internally)
      name: Desk
    - group:                   # explicit group
        - entity: light.a
          name: A
        - entity: light.b
          name: B
      buttons_layout: inline   # or column — how buttons stack within this group
      name: Group label
  bottom:
    - entity: sensor.temp      # individual button
    - group:
        - entity: light.c
      buttons_layout: inline
      justify_content: center  # only valid on bottom groups:
                               #   fill (default), start, center, end
                               #   space-between / space-around / space-evenly → mapped to fill
```

**Auto-grouping rules:**
- Individual `main` buttons are wrapped in a single auto group (`g_main_auto`) whenever `main_layout: rows`, when explicit groups also exist, or when there are any `bottom` items.
- Individual `bottom` buttons: if mixed with explicit bottom groups, each gets its own individual auto group to preserve YAML order; otherwise they share one auto group (`g_bottom_auto`).

### Sub-button DOM structure

```
.bubble-<type>  .bubble-wrapper
│
├── [base card content — contentContainer, buttonsContainer, etc.]
│
├── .bubble-sub-button-container                    ← top area
│   [.groups-layout-inline | .groups-layout-rows]
│   └── .bubble-sub-button-group
│       .position-top
│       .display-<inline|column>
│       .group-layout-<inline|rows>
│       [data-group-id="g_main_0 | g_main_auto | ..."]
│       └── .bubble-sub-button  .bubble-sub-button-<n>  [.<name-class>]
│           [.is-select]  [.fill-width]  [.content-<layout>]  [.hidden]
│           ├── .bubble-feedback-container
│           │   └── .bubble-feedback-element  .feedback-element
│           └── .bubble-sub-button-name-container
│
└── .bubble-sub-button-bottom-container             ← bottom area (only when bottom items exist)
    [.groups-layout-inline | .groups-layout-rows]
    [.alignment-lanes-active]                       ← present when inline layout with alignment lanes
    │
    ├── .bubble-sub-button-alignment-lane            ← one per alignment zone (inline layout only)
    │   .lane-<start|center|fill|end>
    │   [.lane-expand]                              ← when lane needs to flex-grow
    │   └── .bubble-sub-button-group
    │       .position-bottom
    │       .display-<inline|column>
    │       .group-layout-<inline|rows>
    │       .alignment-<start|center|fill|end>       ← from justify_content
    │       [.alignment-fill-auto]                  ← added when fill-width child forces lane fill
    │       └── .bubble-sub-button  ...             ← same as top area
    │
    └── [more alignment lanes]
```

**Alignment lane order** (CSS `order` property): start=1, center=2, fill=3, end=4.

**`justify_content` → alignment class mapping:**

| YAML value | Class |
|------------|-------|
| `fill` (default) | `alignment-fill` |
| `start` / `flex-start` / `left` | `alignment-start` |
| `center` | `alignment-center` |
| `end` / `flex-end` / `right` | `alignment-end` |
| `space-between` / `space-around` / `space-evenly` / `stretch` | `alignment-fill` |

### Name-based CSS class

Each sub-button gets a class derived from its `name` field: lowercased, accent-stripped, non-alphanumeric runs replaced with `-`, leading/trailing `-` stripped. E.g. `name: "My Button"` → class `my-button`. Use this to target specific sub-buttons in CSS.

---

## Editor schema reference

The `editor` key is an array of field objects. Fields render as UI controls in the Bubble Card module editor.

### Common field properties

```yaml
- name: field_key       # key — accessed as this.config.<module_id>.field_key
  label: Display label
  default: 80           # cosmetic only, not injected into config automatically
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
    mode: slider          # or "box"
    unit_of_measurement: px

selector:
  text:
    multiline: false

selector:
  boolean: {}

selector:
  select:
    mode: dropdown        # or "list"
    custom_value: false
    options:
      - label: Option A
        value: option_a
      - label: Option B
        value: option_b

selector:
  color: {}               # colour picker

selector:
  icon: {}                # HA icon picker

selector:
  entity:
    domain: light         # optional filter

selector:
  device: {}

selector:
  area: {}
```

Other selectors (`time`, `date`, `action`, `condition`, `theme`, etc.) exist but have not all been verified with Bubble Card modules.

### Grid layout

```yaml
- type: grid
  schema:
    - name: field_a
      label: Field A
      selector:
        number: { min: 0, max: 100, step: 1 }
    - name: field_b
      label: Field B
      selector:
        number: { min: 0, max: 100, step: 1 }
  column_min_width: 150px
```

### Expandable section

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

- **Module IDs** are `snake_case`. The YAML top-level key, config access path (`this.config.<id>`), and filename (`<id>.yaml`) must all match.
- **Always use `!important`** on CSS overrides — Bubble Card's own styles use it throughout.
- **Always use optional chaining and a default**: `this.config.my_module?.field ?? defaultValue`. The config object is `undefined` until the user saves settings.
- **Scope by card-type class** when a rule must not leak across card types. Key discriminators:
  - `.bubble-button-card` — only on button/state cards (not on slider, not on media player)
  - `.bubble-button-card > .bubble-icon-container` — main icon container on button cards only
  - `.bubble-sub-button .bubble-icon` — sub-button icons specifically (use to cancel rules that bleed)
  - `.bubble-media-player` — media player card wrapper
  - `.bubble-cover` — cover card wrapper
  - `.bubble-climate` — climate card wrapper
- **Lock element width** against reflow with equal `min-width` + `max-width`.
- **Full card height** on a flex child: `align-self: stretch !important; height: 100% !important`.
- **Left-bleed panel effect**: negative left margin + `overflow: hidden` on the container. Set `border-top-left-radius: 0; border-bottom-left-radius: 0` explicitly.
- **Keyframe name collisions**: prefix all `@keyframes` with the module ID (e.g., `@keyframes my_module-pulse`).
- **Comment only non-obvious constraints** — e.g. why a selector is scoped the way it is, or a workaround for a specific card type quirk. No comments explaining what the CSS visually does.
- **Block JS expressions** with side effects should return a CSS string. Don't return `undefined` — always have a fallback `return ''`.
- **Sub-button icon bleed**: unscoped `.bubble-icon` rules will hit sub-button icons. Always follow with `.bubble-sub-button .bubble-icon { <cancel rule> !important; }`.

---

## Testing a module

1. Copy the YAML file to `/config/bubble_card/modules/` on the HA host (requires Bubble Card Tools integration).
2. Edit a card in the HA dashboard, open the **Modules** tab, enable the module.
3. Use browser DevTools on the HA frontend to inspect shadow DOM and verify class names.
4. Keep the `supported` list accurate — it controls which card types show the module in the UI.