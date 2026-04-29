# Pop-up Card

> `card_type: pop-up`  
> Source: `src/cards/pop-up/create.js` + `styles.css` + `backdrop.css` + `changes.js`

Completely different structure from all other card types. Does **not** use the base structure at all. The card modifies an existing `#root` element inside a vertical-stack, and manages a global backdrop in `document.body`.

---

## DOM hierarchy

### Backdrop (global singleton in `document.body`)

```
document.body
└── div.bubble-backdrop-host                         ← shadow DOM host; one instance globally
    └── (shadow root)
        ├── .bubble-backdrop  .backdrop              ← full-screen overlay
        │   [.is-hidden | .is-visible]               ← toggled on open/close
        │   [.has-blur]                              ← added when backdrop_blur: > 0
        ├── <style>                                  ← backdrop base styles
        └── <style data-bubble-target="backdrop">    ← custom backdrop styles from card config
```

### Pop-up panel (modifies `#root` of the vertical-stack)

```
#root  (the vertical-stack's root element — transformed by Bubble Card)
  becomes: .bubble-pop-up  .pop-up
  state classes:
    .is-popup-closed    ← default; card is not visible
    .is-popup-opened    ← card is open/visible
    .is-opening         ← transition: opening animation in progress
    .is-closing         ← transition: closing animation in progress
  modifier classes:
    .no-header          ← when header_offset: 0 or no entity/name configured
    .large              ← when large: true
  │
  ├── .bubble-pop-up-background                      ← the visible panel background surface
  │   [background-color and border-radius from CSS vars]
  │
  ├── .bubble-header-container
  │   [.is-unavailable]  ← when entity is unavailable
  │   ├── .bubble-header                             ← left side: entity button
  │   │   └── .bubble-button-container               ← a full button card renders inside here
  │   │       [the header entity — full bubble-button structure]
  │   └── .bubble-close-button  .close-pop-up        ← right side: close button
  │       ├── .bubble-feedback-container
  │       │   └── .bubble-feedback-element  .feedback-element
  │       ├── ha-icon.bubble-close-icon
  │       └── ha-ripple
  │
  └── .bubble-pop-up-container                       ← scrollable content area
      [child cards rendered here by HA]
```

---

## State classes and transitions

| Class on `.bubble-pop-up` | Meaning |
|--------------------------|---------|
| `.is-popup-closed` | Panel hidden (default) |
| `.is-popup-opened` | Panel visible |
| `.is-opening` | Opening animation in progress |
| `.is-closing` | Closing animation in progress |

| Class on `.bubble-backdrop` | Meaning |
|----------------------------|---------|
| `.is-hidden` | Backdrop not visible |
| `.is-visible` | Backdrop visible (during open pop-up) |
| `.has-blur` | `backdrop-filter: blur(X)` applied |

---

## CSS variables (pop-up-specific)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-pop-up-border-radius` | `var(--bubble-border-radius, 42px)` | Panel corner radius (top corners) |
| `--bubble-pop-up-background-color` | `var(--bubble-secondary-background-color)` | Panel background |
| `--bubble-pop-up-main-background-color` | (fallback chain) | Header + button background |
| `--bubble-pop-up-fade-color` | (set by JS) | Gradient fade at panel top |
| `--bubble-pop-up-gap` | `14px` | Gap between child cards in `pop-up-container` |
| `--bubble-pop-up-close-button-border` | `var(--bubble-border)` | Close button border |
| `--bubble-pop-up-border` | `var(--bubble-border)` | Panel border |
| `--bubble-backdrop-background-color` | `var(--bubble-default-backdrop-background-color)` | Backdrop overlay color |
| `--bubble-backdrop-filter` | (none by default) | Backdrop blur/filter |

---

## Key CSS targeting patterns

```css
/* The pop-up panel itself */
.bubble-pop-up { ... }
.bubble-pop-up-background { background-color: rgba(30, 30, 30, 0.95) !important; }

/* Header */
.bubble-header-container { ... }
.bubble-header { ... }

/* Close button */
.bubble-close-button { ... }
.bubble-close-icon { --mdc-icon-size: 20px; }

/* Content area */
.bubble-pop-up-container { ... }

/* State-based */
.bubble-pop-up.is-popup-opened { ... }
.bubble-pop-up.is-popup-closed { ... }

/* Large variant */
.bubble-pop-up.large .bubble-header-container { ... }
.bubble-pop-up.large .bubble-close-button { ... }

/* No-header variant */
.bubble-pop-up.no-header .bubble-header-container { display: none !important; }

/* Backdrop — lives in shadow DOM; use CSS variables to style, not direct selectors */
/* Set --bubble-backdrop-background-color from outside the shadow DOM */
```

> **Note on backdrop styling**: The backdrop element lives inside a shadow DOM. You cannot target `.bubble-backdrop` directly from your module CSS. Use the `--bubble-backdrop-background-color` and `--bubble-backdrop-filter` CSS variables instead, setting them on `:root` or `ha-card`.

---

## Opening/closing mechanics

- Pop-ups open when the URL hash matches the pop-up's configured hash value
- CSS `transition` on `.bubble-pop-up` handles the slide-up animation
- `.is-opening` and `.is-closing` classes are applied during the transition for styling hooks
- The backdrop opacity transitions separately via `.is-visible`/`.is-hidden` classes

---

## Quick CSS cheat sheet

| Goal | Target | Property |
|------|--------|----------|
| Panel background | `.bubble-pop-up-background` | `background-color` |
| Panel corner radius | `--bubble-pop-up-border-radius` | CSS variable |
| Gap between cards | `--bubble-pop-up-gap` | CSS variable (default 14px) |
| Header background | `.bubble-header-container` | `background-color` |
| Close button style | `.bubble-close-button` | `background-color`, `border-radius` |
| Close icon size | `.bubble-close-icon` | `--mdc-icon-size` |
| Backdrop color | `--bubble-backdrop-background-color` | CSS variable (on `:root`) |
| Backdrop blur | `--bubble-backdrop-filter` | CSS variable (e.g. `blur(8px)`) |
| Panel open animation | `.is-opening .bubble-pop-up-background` | `transition`, `transform` |
| Panel closed state | `.is-popup-closed` | `visibility`, `opacity` |

---

## Editor mode

In the dashboard editor, the pop-up gets class `.editor` on `.bubble-pop-up`:
- `position: relative` instead of fixed
- Background gradient removed from pseudo-element
- Content area max-height is unrestricted

Editor also renders `.bubble-editor-placeholder` elements inside `.bubble-pop-up-container` to show where child cards will appear.
