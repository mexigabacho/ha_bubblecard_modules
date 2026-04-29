# Media Player Card

> `card_type: media-player`  
> Source: `src/cards/media-player/create.js` + `styles.css` + `changes.js`

Uses the full base structure with significant additions. See [01-base-structure.md](01-base-structure.md) for the shared DOM.

---

## Full DOM hierarchy

```
.bubble-media-player-container  .bubble-container    ← mainContainer
[.with-bottom-buttons]
[.large | .rows-2]
│
└── .bubble-media-player  .bubble-wrapper
    ├── .bubble-background  .bubble-cover-background  ← background; "cover-background" is a backward-compat alias
    │   [.bubble-cover-background-crossfade]          ← added by JS when cover_background: true and art arrives
    │   ├── .bubble-cover-crossfade-layer             ← layer A
    │   │   .bubble-cover-crossfade-layer--background
    │   │   [.is-visible | .is-empty]
    │   └── .bubble-cover-crossfade-layer             ← layer B
    │       .bubble-cover-crossfade-layer--background
    │       [.is-visible | .is-empty]
    │
    ├── .bubble-content-container
    │   ├── .bubble-main-icon-container
    │   │   .bubble-icon-container  .icon-container
    │   │   ├── ha-icon.bubble-main-icon  .bubble-icon  .icon
    │   │   ├── div.bubble-entity-picture  .entity-picture   ← icon-scope art host
    │   │   │   [.bubble-cover-icon-crossfade]               ← added by JS when art arrives
    │   │   │   ├── .bubble-cover-crossfade-layer
    │   │   │   │   .bubble-cover-crossfade-layer--icon
    │   │   │   │   [.is-visible | .is-empty]
    │   │   │   └── .bubble-cover-crossfade-layer
    │   │   │       .bubble-cover-crossfade-layer--icon
    │   │   │       [.is-visible | .is-empty]
    │   │   └── .bubble-media-button  .bubble-mute-button    ← mute button inside icon container
    │   │       [.is-hidden]                                 ← hidden while volume slider is closed
    │   │
    │   ├── .bubble-name-container  .name-container          ← shown when media info is absent/idle
    │   │   ├── .bubble-name  .name
    │   │   └── .bubble-state  .state
    │   │
    │   └── .bubble-media-info-container                     ← shown while playing (replaces name container)
    │       ├── .bubble-title
    │       └── .bubble-artist
    │
    ├── .bubble-feedback-container  .feedback-container
    │   └── .bubble-feedback-element  .feedback-element
    │
    ├── .bubble-buttons-container  .bubble-button-container  ← "bubble-button-container" is backward-compat alias
    │   ├── .bubble-media-button  .bubble-power-button
    │   │   ├── .bubble-feedback-container
    │   │   │   └── .bubble-feedback-element  .feedback-element
    │   │   ├── ha-icon.bubble-media-button-icon
    │   │   └── ha-ripple
    │   ├── .bubble-media-button  .bubble-previous-button    ← same internal structure
    │   ├── .bubble-media-button  .bubble-next-button
    │   ├── .bubble-media-button  .bubble-volume-button
    │   └── .bubble-media-button  .bubble-play-pause-button
    │
    ├── .bubble-volume-slider-wrapper                        ← volume overlay; appended to cardWrapper
    │   [.is-hidden]                                         ← hidden when volume slider is closed
    │   ├── .bubble-media-button  .bubble-volume-slider-mute-button
    │   ├── .bubble-volume-slider                            ← slider surface
    │   │   └── [slider range fill + value display]
    │   └── .bubble-media-button  .bubble-volume-slider-close-button
    │
    ├── .bubble-sub-button-container                         ← top sub-buttons (when configured)
    └── .bubble-sub-button-bottom-container                  ← bottom sub-buttons (when configured)
```

---

## Runtime modifier classes

On `cardWrapper` (`.bubble-media-player.bubble-wrapper`):

| Class | When |
|-------|------|
| `.large` | `card_layout: large` |
| `.full-width` | `card_layout: large` + bottom-fixed buttons |
| `.bottom-fixed` | Main buttons at bottom via `main_buttons_position: bottom` |
| `.fixed-top` | Bottom sub-button group or `main_buttons_position: bottom` |
| `.has-bottom-buttons` | Bottom buttons active (repositions volume slider wrapper) |
| `.fixed-top` | Content pinned to top when bottom groups exist |

---

## Cover art / album art crossfade system

The media player has a dedicated crossfade system driven by `changeMediaIcon()` and `changeBackground()`.

### Two scopes

| Scope | Container | Activated by | Visual treatment |
|-------|-----------|-------------|-----------------|
| `icon` | `.bubble-entity-picture` (inside `.bubble-icon-container`) | Always, when art available | Full opacity, `cover`/`center` |
| `background` | `.bubble-background.bubble-cover-background` | `cover_background: true` | `filter: blur(50px); opacity: 0.5` on the whole container |

### How the DOM mutates (one-time, per scope)

When art first appears, `ensureCoverLayers()` runs:
1. Clears all children of the container.
2. Adds class `bubble-cover-icon-crossfade` or `bubble-cover-background-crossfade` to the container.
3. Inserts two `div.bubble-cover-crossfade-layer` elements inside — layer A and layer B.

After this point, the container never holds `background-image` directly — it always lives in a layer.

### Crossfade transition (`crossfadeTo()`)

1. Preloads new image via `new Image()`.
2. On load: sets `background-image` on the *inactive* layer, adds `.is-visible` to it.
3. 50 ms later: removes `.is-visible` from the *current* layer.
4. CSS `transition: opacity 2s ease` blends them smoothly.
5. On error: marks layer `.is-empty` (opacity stays 0).
6. Fading *out*: sets `background-image: ''`, adds `.is-empty`, then swaps.

### State machine

| Entity state | Behaviour |
|---|---|
| `playing` | Show art immediately |
| `paused` | Show art (same as playing) |
| `idle` | 2 000 ms timeout → fade out |
| `off` / `unavailable` / `unknown` / `standby` | Clear art immediately |

### Module implications

- Do **not** set `background-image` directly on `.bubble-background.bubble-cover-background` or `.bubble-entity-picture` — once the crossfade system initialises, those elements no longer hold the image directly.
- The `filter: blur(50px)` on `.bubble-background` applies to the entire container including the crossfade layers — you cannot remove the blur from only the layers.
- To set a custom background without interfering with cover art, use a `::before` or `::after` pseudo-element on `.bubble-media-player` with a lower z-index.

---

## CSS variables (media-player-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-media-player-button-background-color` | transparent | Control button backgrounds |
| `--bubble-media-player-buttons-border-radius` | `var(--bubble-border-radius)` | Control button radius |
| `--bubble-media-player-border-radius` | `var(--bubble-border-radius)` | Volume slider radius |
| `--bubble-media-player-slider-background-color` | secondary bg | Volume slider track background |
| `--bubble-media-player-play-pause-icon-color` | white | Play/pause icon color |
| `--bubble-accent-color` | HA default | Play/pause button background |

---

## Key CSS targeting patterns

```css
/* Card background — careful: blur(50px) here affects everything inside */
.bubble-media-player .bubble-background { ... }

/* Background crossfade layers (don't set background-image here) */
.bubble-cover-background-crossfade .bubble-cover-crossfade-layer--background { ... }

/* Icon / art thumbnail area */
.bubble-media-player .bubble-entity-picture { ... }

/* Media info (title + artist — shown when playing) */
.bubble-media-info-container { ... }
.bubble-title { ... }
.bubble-artist { ... }

/* Control buttons (all share .bubble-media-button) */
.bubble-media-button { ... }
.bubble-play-pause-button { ... }
.bubble-power-button { ... }
.bubble-previous-button { ... }
.bubble-next-button { ... }
.bubble-volume-button { ... }

/* Volume slider overlay */
.bubble-volume-slider-wrapper { ... }
.bubble-volume-slider { ... }

/* Mute button (inside icon container) */
.bubble-mute-button { ... }

/* Apply background outside the blur scope — use ::after on wrapper */
.bubble-media-player::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url(...);
    background-size: cover;
    /* No blur — sits above .bubble-background but below card content */
    z-index: 0;
    pointer-events: none;
}

/* Cancel icon rules on sub-buttons */
.bubble-sub-button .bubble-icon { color: inherit !important; --mdc-icon-size: 16px !important; }
```

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Card background (no art) | `.bubble-media-player .bubble-background` | `background-color` |
| Background blur amount | `.bubble-media-player .bubble-background` | `filter: blur(Xpx)` |
| Background opacity | `.bubble-media-player .bubble-background` | `opacity` |
| Logo overlay outside blur | `.bubble-media-player::after` | `background-image`, `opacity` |
| Play/pause button color | `.bubble-play-pause-button` | `background-color` |
| Play/pause icon color | `--bubble-media-player-play-pause-icon-color` | CSS variable |
| All control buttons | `.bubble-media-button` | `background-color`, `border-radius` |
| Title text | `.bubble-title` | `font-size`, `font-weight` |
| Artist text | `.bubble-artist` | `font-size`, `opacity` |
| Volume slider bg | `.bubble-volume-slider` | `background-color` |
| Volume fill color | `.bubble-volume-slider .bubble-range-fill` | `background-color` |
| Hide power button | `.bubble-power-button` | `display: none` |
| Card height | `.bubble-media-player-container` | `height` or `grid_options: rows` |

---

## Debugging tips

- **Art not showing as blurred background**: check `cover_background: true` is set on the card. Without it, only the icon scope is active.
- **`background-image` on `.bubble-background` not working**: the crossfade system has mutated the DOM — the image lives in `.bubble-cover-crossfade-layer` children now. Target those instead, or use `::before`/`::after`.
- **Logo overlay appearing behind blur**: put it in `.bubble-media-player::after` at `z-index: 1` (or higher) — it will render above the blurred background layer.
- **`is-hidden` class on mute/volume wrapper**: the `.is-hidden` CSS sets `opacity: 0; pointer-events: none; transform: translateX(14px)`. Don't fight this — use state targeting instead.
- **Player shows name instead of title/artist**: `changeMediaInfo()` swaps visibility between `.bubble-name-container` and `.bubble-media-info-container` based on whether media info is available. Both elements always exist in the DOM.
