# Pop-up Card

> `card_type: pop-up`  
> Source: `src/cards/pop-up/create.js` + `styles.css` + `backdrop.css` + `changes.js`  
> **Last verified: v3.2.3**

Completely different structure from all other card types. Does **not** use the base structure at all. The card modifies an existing `#root` element inside a vertical-stack (or creates its own root for standalone pop-ups), and manages a global backdrop in `document.body`.

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

### Pop-up panel (modifies `#root` of the vertical-stack, or standalone)

```
#root  (the vertical-stack's root element — transformed by Bubble Card)
  becomes: .bubble-pop-up  .pop-up
  ─── state classes (on .bubble-pop-up) ───
    .is-popup-closed        ← default; card is not visible
    .is-popup-opened        ← card is open/visible
    .is-opening             ← opening animation in progress
    .is-closing             ← closing animation in progress
  ─── layout/mode modifier classes ───
    .no-header              ← entity/name/icon all absent, or header hidden
    .no-header-actions      ← both close and previous buttons hidden
    .hide-close-button      ← close button hidden
    .show-previous-button   ← back/previous button visible
    .close-button-left      ← close button placed on the left
    .has-popup-shadow       ← shadow_opacity > 0
    .is-standalone-pop-up   ← card is a standalone pop-up (not in vertical-stack)
  ─── popup-mode classes (one of the three is active) ───
    .popup-mode-fit-content     ← fit-content mode
    .popup-mode-centered        ← centered dialog mode
    .popup-mode-adaptive-dialog ← adaptive dialog mode
    .popup-mode-with-bottom-offset ← has a bottom offset configured
    .popup-mode-full-width-on-mobile ← full-width on mobile (centered mode only)
  ─── popup-style class ───
    .popup-style-classic    ← classic style variant
  ─── performance mode (one of the two is active) ───
    .popup-performance-default
    .popup-performance-performance
  │
  ├── .bubble-pop-up-background                      ← visible panel background surface
  │
  ├── .bubble-header-container  #header-container
  │   ├── .bubble-header                             ← left side: entity button
  │   │   └── .bubble-button-container               ← full button card renders inside here
  │   │       [the header entity — full bubble-button structure]
  │   └── .bubble-header-actions                     ← right side: action buttons container
  │       ├── .bubble-header-action-button  .bubble-previous-button  .previous-pop-up
  │       │   ├── .bubble-feedback-container
  │       │   │   └── .bubble-feedback-element  .feedback-element
  │       │   ├── span.bubble-header-action-icon  .bubble-previous-icon  (contains SVG)
  │       │   └── ha-ripple
  │       └── .bubble-header-action-button  .bubble-close-button  .close-pop-up
  │           ├── .bubble-feedback-container
  │           │   └── .bubble-feedback-element  .feedback-element
  │           ├── span.bubble-header-action-icon  .bubble-close-icon  (contains SVG)
  │           └── ha-ripple
  │
  └── .bubble-pop-up-container                       ← scrollable content area
      [.is-scrollable added once the user scrolls]
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
| `.no-header` | Header hidden (no entity/name/icon, or disabled) |
| `.no-header-actions` | Both close and previous buttons are hidden |
| `.hide-close-button` | Close button specifically hidden |
| `.show-previous-button` | Back/previous button is visible |
| `.close-button-left` | Close button positioned on the left |
| `.has-popup-shadow` | `shadow_opacity` > 0 |
| `.is-standalone-pop-up` | Pop-up placed outside a vertical-stack |
| `.popup-mode-fit-content` | Fit-content popup mode |
| `.popup-mode-centered` | Centered dialog popup mode |
| `.popup-mode-adaptive-dialog` | Adaptive dialog popup mode |
| `.popup-mode-with-bottom-offset` | Has bottom offset configured |
| `.popup-mode-full-width-on-mobile` | Full-width on mobile (centered mode) |
| `.popup-style-classic` | Classic header style |
| `.popup-performance-default` | Default performance mode |
| `.popup-performance-performance` | Performance (low-cost) mode |

| Class on `.bubble-pop-up-container` | Meaning |
|------------------------------------|---------|
| `.is-scrollable` | Added once the user has scrolled the content area |

| Class on `.bubble-backdrop` | Meaning |
|----------------------------|---------|
| `.is-hidden` | Backdrop not visible |
| `.is-visible` | Backdrop visible (during open pop-up) |
| `.has-blur` | `backdrop-filter: blur(X)` applied |

---

## CSS variables (pop-up-specific)

### Layout / spacing

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-pop-up-border-radius` | `var(--bubble-border-radius, 42px)` | Panel corner radius |
| `--bubble-pop-up-content-border-radius` | falls back to `--bubble-pop-up-border-radius` | Content area corner radius (independent of header) |
| `--bubble-pop-up-gap` | `14px` | Gap between child cards in the content area |
| `--bubble-pop-up-header-overlap` | `50px` | How far the content container overlaps the header |
| `--bubble-pop-up-header-gap` | (set by JS) | Gap between header bottom and content area |
| `--bubble-pop-up-header-gap-reserve` | (set by JS) | Space reserved for header gap calculations |
| `--bubble-pop-up-visible-bottom-padding` | `18px` | Padding at the bottom of the visible content |
| `--bubble-pop-up-extra-bottom-space` | `max(0px, bottom-padding - 18px)` | Extra space added for bottom offset |
| `--bubble-pop-up-bottom-padding` | `18px` or `84px` | Total bottom padding (84px when HBS is present) |
| `--bubble-pop-up-available-height` | (set by JS) | Available viewport height for the popup |

### Scrolling gradient mask

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-pop-up-mask-top-alpha` | (set by JS) | Opacity of the top scroll-fade gradient |
| `--bubble-pop-up-mask-bottom-alpha` | (set by JS) | Opacity of the bottom scroll-fade gradient |
| `--bubble-pop-up-mask-top-stop` | (set by JS) | Stop position of the top gradient |
| `--bubble-pop-up-mask-bottom-stop` | (set by JS) | Stop position of the bottom gradient |

### Colours

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-pop-up-background-color` | (set by JS from `bg_color`) | Panel background |
| `--bubble-pop-up-fade-color` | (set by JS) | Gradient fade at panel top |
| `--bubble-pop-up-main-background-color` | (fallback chain) | Header + button background |
| `--bubble-pop-up-close-button-border` | `var(--bubble-border)` | Close/action button border |
| `--bubble-pop-up-border` | `var(--bubble-border)` | Panel border |

### Backdrop (shadow DOM — set on `:root` or `ha-card`, not inside shadow)

| Variable | Default | Controls |
|----------|---------|----------|
| `--bubble-backdrop-background-color` | `var(--bubble-default-backdrop-background-color)` | Backdrop overlay colour |
| `--bubble-backdrop-filter` | (none) | Backdrop blur/filter |

---

## Key CSS targeting patterns

```css
/* The pop-up panel itself */
.bubble-pop-up { ... }
.bubble-pop-up-background { background-color: rgba(30, 30, 30, 0.95) !important; }

/* Header container */
.bubble-header-container { ... }
.bubble-header { ... }                   /* entity button side */
.bubble-header-actions { ... }           /* close/previous button side */

/* Close and previous buttons */
.bubble-close-button { ... }
.bubble-close-icon { }                   /* span containing inline SVG */
.bubble-previous-button { ... }
.bubble-previous-icon { }               /* span containing inline SVG */

/* Content area */
.bubble-pop-up-container { ... }

/* State-based */
.bubble-pop-up.is-popup-opened { ... }
.bubble-pop-up.is-popup-closed { ... }

/* No-header variant */
.bubble-pop-up.no-header > .bubble-header-container { ... }
.bubble-pop-up.no-header-actions > .bubble-header-container > .bubble-header { ... }

/* Popup mode variants */
.bubble-pop-up.popup-mode-centered { ... }
.bubble-pop-up.popup-mode-fit-content { ... }
.bubble-pop-up.popup-mode-adaptive-dialog { ... }
.bubble-pop-up.popup-style-classic { ... }

/* Close-button-on-left layout */
.bubble-pop-up.close-button-left > .bubble-header-container > .bubble-header-actions { ... }

/* Standalone pop-up (not inside vertical-stack) */
.bubble-pop-up.is-standalone-pop-up { ... }

/* Scrolled content (added once user scrolls) */
.bubble-pop-up-container.is-scrollable { ... }

/* Backdrop — lives in shadow DOM; use CSS variables to style, not direct selectors */
/* Set --bubble-backdrop-background-color from outside the shadow DOM */
```

> **Note on backdrop styling**: The backdrop element lives inside a shadow DOM. You cannot target `.bubble-backdrop` directly from your module CSS. Use the `--bubble-backdrop-background-color` and `--bubble-backdrop-filter` CSS variables instead, setting them on `:root` or `ha-card`.

> **Note on header button color (v3.2.x change)**: In v3.1.x, `--bubble-button-background-color` for the header entity was applied to `.bubble-pop-up` directly. From v3.2.x it is applied to `.bubble-pop-up > .bubble-header-container > .bubble-header`. Modules that read or override this variable should target `.bubble-header` rather than `.bubble-pop-up`.

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
| Content area corner radius | `--bubble-pop-up-content-border-radius` | CSS variable (independent of header) |
| Gap between cards | `--bubble-pop-up-gap` | CSS variable (default 14px) |
| Header background | `.bubble-header-container` | `background-color` |
| Header entity button color | `.bubble-header` | `--bubble-button-background-color` |
| Close button style | `.bubble-close-button` | `background-color`, `border-radius` |
| Close icon | `.bubble-close-icon` | targets the `<span>` containing the SVG |
| Previous button style | `.bubble-previous-button` | `background-color`, `border-radius` |
| Backdrop color | `--bubble-backdrop-background-color` | CSS variable (on `:root`) |
| Backdrop blur | `--bubble-backdrop-filter` | CSS variable (e.g. `blur(8px)`) |
| Panel open animation | `.is-opening .bubble-pop-up-background` | `transition`, `transform` |
| Panel closed state | `.is-popup-closed` | `visibility`, `opacity` |
| Scrolled content area | `.bubble-pop-up-container.is-scrollable` | style hook once user scrolls |

---

## Editor mode

In the dashboard editor, the pop-up gets class `.editor` on `.bubble-pop-up`:
- `position: relative` instead of fixed
- Background gradient removed from pseudo-element
- Content area max-height is unrestricted

Editor also renders `.bubble-editor-placeholder` elements inside `.bubble-pop-up-container` to show where child cards will appear.
