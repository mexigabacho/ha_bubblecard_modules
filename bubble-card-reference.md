# Bubble Card — Developer Reference

> Personal reference for customizing Home Assistant Bubble Card (latest / v3+) via CSS modules.  
> Card type covered: **button / status** (`card_type: button`).

---

## 1. DOM Hierarchy

```
ha-card
└── .bubble-button-card-container        ← outer size/scroll boundary; height lives here
    ├── .bubble-button-background        ← absolutely positioned; provides color/image fill
    ├── .bubble-color-background         ← state-reactive color overlay (is-on tint, etc.)
    └── .bubble-button-card              ← CSS GRID ROOT (areas: i n a)
        ├── .bubble-icon-container       ← [grid-area: i]  icon cell
        │   └── .icon-with-state         ← circular background behind icon
        │       └── .bubble-icon         ← the actual <ha-icon> element
        ├── .bubble-name-container       ← [grid-area: n]  name/state cell
        │   ├── .bubble-name
        │   ├── .bubble-state
        │   └── .bubble-attribute
        └── .bubble-sub-button-container ← [grid-area: a]  sub-buttons (flex row)
            └── .bubble-sub-button ×N
                ├── .bubble-sub-button-icon
                └── .bubble-sub-button-name-container
```

**State classes** applied to `.bubble-button-card-container`:
- `.is-on` — entity state is on
- `.is-off` — entity state is off
- `.is-unavailable` — entity unavailable

**Layout classes** applied to `.bubble-button-card-container`:
- `.large` — large layout mode (default in section view)
- `.rows-2` — large-2-rows layout

---

## 2. CSS Grid Layout

### Normal layout (`card_layout: normal`)

```
grid-template-areas:  "i  n  a"
grid-template-columns: auto  1fr  auto
grid-template-rows:    50px         (single row)
```

| Area | Class | Column sizing | Notes |
|------|-------|--------------|-------|
| `i` | `.bubble-icon-container` | `auto` — shrinks to content | Icon cell; left side |
| `n` | `.bubble-name-container` | `1fr` — fills remaining space | Name, state, attribute |
| `a` | `.bubble-sub-button-container` | `auto` — shrinks to content | Sub-buttons; right side |

### Large layout (`card_layout: large`)

Same three-area grid, but:
- `.bubble-icon-container` is taller/wider (more padding, larger default size)
- Card height is typically driven by `--row-height` and `--row-size` CSS variables
- Sub-button container may wrap below in `large-2-rows` mode

### Large-2-rows layout

```
grid-template-areas:  "i  n  a"
                      "b  b  b"    ← sub-buttons moved to a full-width bottom row
```

---

## 3. Key CSS Variables (theme-level)

| Variable | What it controls |
|----------|-----------------|
| `--bubble-accent-color` | Icon/highlight color when entity is on |
| `--bubble-icon-background-color` | Background of `.icon-with-state` circle |
| `--bubble-border-radius` | Card corner radius |
| `--bubble-main-background-color` | Card background |
| `--bubble-secondary-background-color` | Secondary surfaces |
| `--mdc-icon-size` | Icon size (set on `.bubble-icon`) |
| `--row-height` | Height of one grid row (section view) |
| `--row-size` | Number of rows the card spans |
| `--row-gap` | Gap between rows (section view) |

---

## 4. My "Large Icon" Module

### What it does
Enlarges the icon section of a button/status card so the icon is prominent and visually dominant. The icon container is widened, the icon itself is set to 90 px, and the name container is nudged to align neatly.

### Module code

```css
.bubble-icon-container {
  border-radius: 25% !important;
  width: 100% !important;
  height: 100% !important;
  max-width: 120px !important;
  max-height: 120px !important;
  margin: 0px 0px 10px -20px !important;
  padding: 5px 0px 10px 5px !important;
  opacity: .6 !important;
}

.bubble-name-container {
  justify-self: start !important;
  align-self: start !important;
  padding: 10px 5px 5px 5px;
}

.bubble-icon {
  position: relative !important;
  margin: 0px 0px 0px 0px !important;
  --mdc-icon-size: 90px !important;
  opacity: 1 !important;
}
```

### Diagnosis: why the icon can shift

The grid gives the `i` column `auto` width — meaning it sizes to the content of `.bubble-icon-container`. Your module sets `width: 100%` and `height: 100%` on that container, which makes it want to fill its grid cell. The negative left `margin: ... -20px` pulls the container out of flow slightly, which can cause the grid to recalculate the `i` column width unexpectedly when the `n` or `a` columns change size (e.g. longer state text, more sub-buttons appearing/disappearing, attribute values changing).

Additional pressure points:
- `padding: 5px 0px 10px 5px` adds to the total rendered size of the container, so the effective height is `max-height (120px) + 10px bottom padding = 130px` — this can exceed the card's natural height and cause overflow/reflow.
- In large layout, `.large .bubble-icon-container` has its own default margin overrides from Bubble Card's internal styles; your `!important` rules win, but the interaction with the grid's row height calculation can still shift things.

---

## 5. Icon Stability Fix

The goal: lock the icon cell to a fixed size so no other column can push it around.

### Strategy
Give `.bubble-icon-container` explicit fixed dimensions instead of `width/height: 100%`, and use `flex-shrink: 0` on it to prevent the grid from squeezing it. Also swap the negative margin (which removes the element from normal flow calculations) for a `translate` which is layout-neutral.

### Stable module CSS

```css
/* Lock the icon cell to a fixed footprint */
.bubble-icon-container {
  flex-shrink: 0 !important;
  width: 110px !important;
  height: 110px !important;
  min-width: 110px !important;   /* prevents grid squeezing */
  min-height: 110px !important;
  max-width: 110px !important;
  max-height: 110px !important;
  border-radius: 25% !important;
  /* Replace negative margin with layout-neutral translate */
  margin: 0 4px 0 0 !important;
  padding: 0 !important;
  transform: translateX(-8px);   /* tweak to taste; doesn't affect grid calc */
  opacity: 0.6 !important;
  align-self: center !important;
}

.bubble-name-container {
  justify-self: start !important;
  align-self: start !important;
  padding: 10px 5px 5px 5px;
}

.bubble-icon {
  position: relative !important;
  margin: 0 !important;
  --mdc-icon-size: 90px !important;
  opacity: 1 !important;
}
```

### Why this works
- `min-width` / `max-width` both set to the same value → the grid `auto` column has only one possible size; it cannot reflow.
- `flex-shrink: 0` → if the container is ever inside a flex parent (some Bubble Card wrappers are), it won't compress.
- `transform: translateX()` → visual offset without affecting layout; the grid never knows the icon moved.
- Removing `width/height: 100%` → no more "fill my parent" pressure that conflicts with `max-width/height`.

---

## 6. Targeting by State

```css
/* Icon container when entity is ON */
.is-on .bubble-icon-container { ... }

/* Icon when entity is OFF */
.is-off .bubble-icon-container { ... }

/* Large layout variant */
.large .bubble-icon-container { ... }

/* Specific sub-button by name (e.g. sub-button named "Volume") */
.volume .bubble-sub-button-icon { ... }
```

---

## 7. Module YAML Structure

```yaml
my_large_icon:
  name: Large device icon
  version: "v1.0"
  creator: "you"
  description: Enlarges the icon section for button/status cards
  supported:
    - button
  code: |
    .bubble-icon-container {
      /* ... your CSS here ... */
    }
```

Place in `/www/bubble/bubble-modules.yaml`. Apply in card YAML:

```yaml
type: custom:bubble-card
card_type: button
button_type: state
entity: light.example
modules:
  - my_large_icon
```

---

## 8. Debugging Tips

- **Inspect in browser DevTools**: right-click the card → Inspect → find `.bubble-button-card` → look at the Computed tab to see which `grid-template-columns` values are actually resolved.
- **Find conflicting styles**: in DevTools, look for crossed-out rules on `.bubble-icon-container` — any rule your module is overriding will be struck through.
- **Check for `!important` wars**: Bubble Card's own styles (in `styles.ts`) use `!important` sparingly in large layout; if your rule loses, add `!important`. If it already has `!important` and still loses, a later stylesheet is winning — check module load order.
- **Large layout height**: the card height in section view is `calc(var(--row-height) * var(--row-size) + var(--row-gap) * (var(--row-size) - 1))`. If your icon is taller than this, it clips.
- **Sub-button name classes**: a sub-button named `"My Sensor"` gets the class `.my-sensor` — use that to target it individually without affecting others.

---

## 9. Quick CSS Cheat Sheet

| Goal | Target | Property |
|------|--------|----------|
| Icon size | `.bubble-icon` | `--mdc-icon-size: Xpx` |
| Icon background circle size | `.icon-with-state` | `width`, `height`, `min-width`, `min-height` |
| Icon background circle shape | `.bubble-icon-container` | `border-radius` |
| Card background color | `.bubble-button-background` | `background-color` |
| State color overlay | `.bubble-color-background` | `background-color` |
| Card height (normal) | `.bubble-button-card-container` | `height` |
| Card height (section) | Card YAML | `grid_options: rows: N` |
| Name font size | `.bubble-name` | `font-size` |
| State font size | `.bubble-state` | `font-size` |
| Sub-button size | `.bubble-sub-button` | `width`, `height`, `min-width`, `min-height` |
| Sub-button icon size | `.bubble-sub-button-icon` | `--mdc-icon-size` |
| Hide sub-button text | `.bubble-sub-button-name-container` | `display: none` |

---

*Last updated: April 2026 — Bubble Card v3+*
