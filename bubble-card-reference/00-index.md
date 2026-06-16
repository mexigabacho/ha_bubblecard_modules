# Bubble Card — Developer Reference Index

> Source-verified against Bubble Card v3.2.3 (`src/` directory).  
> All class names come directly from `create.js` and `styles.css` for each card type.  
> Pop-up reference updated for v3.2.x DOM changes (new mode/style classes, header-actions structure, standalone pop-up support). All other card types verified unchanged from v3.1.6.

---

## Files in this directory

| File | Covers |
|------|--------|
| [01-base-structure.md](01-base-structure.md) | Shared base DOM, CSS variables, state classes, sub-button system |
| [02-button.md](02-button.md) | `card_type: button` — all button types (switch, state, name, slider) |
| [03-media-player.md](03-media-player.md) | `card_type: media-player` — controls, volume slider, cover art crossfade |
| [04-climate.md](04-climate.md) | `card_type: climate` — temperature controls, HVAC mode dropdown |
| [05-cover.md](05-cover.md) | `card_type: cover` — open/stop/close buttons, position feedback |
| [06-select.md](06-select.md) | `card_type: select` — dropdown selector card |
| [07-separator.md](07-separator.md) | `card_type: separator` — section divider with icon, name, line |
| [08-calendar.md](08-calendar.md) | `card_type: calendar` — event list with day chips |
| [09-pop-up.md](09-pop-up.md) | `card_type: pop-up` — overlay panel, backdrop, header |
| [10-horizontal-buttons-stack.md](10-horizontal-buttons-stack.md) | `card_type: horizontal-buttons-stack` — fixed nav bar |
| [layouts/](layouts/) | SVG layout diagrams for each card type |

---

## Which card types share the base structure?

The **base structure** (`createBaseStructure()` in `base-card/create.js`) produces the icon container, name container, background element, and buttons container. Card types that use it:

| Card type | Uses base structure | Notes |
|-----------|-------------------|-------|
| `button` | ✅ full | Adds `bubble-button-card`, `bubble-button-background` backwards-compat classes |
| `media-player` | ✅ full | Adds media controls, media info container, cover art system |
| `climate` | ✅ full | Adds temperature containers, `bubble-color-background` alias |
| `cover` | ✅ full | Adds open/stop/close buttons, `bubble-buttons` alias |
| `select` | ✅ full | Minimal additions — background cursor change, dropdown handled separately |
| `separator` | ⚠️ partial | Does NOT use `withBaseElements`; creates its own icon/name/line DOM |
| `calendar` | ⚠️ partial | Does NOT use `withBaseElements`; creates only `bubble-calendar-content` |
| `pop-up` | ❌ none | Completely different DOM — modifies `#root` of a vertical-stack |
| `horizontal-buttons-stack` | ❌ none | Completely different DOM — fixed bottom nav bar |

---

## Key development rules (apply everywhere)

1. **Always `!important`** — Bubble Card's own styles use it; your rules must too.
2. **Always optional-chain config**: `this.config.my_module?.field ?? default` — config object is `undefined` until user saves.
3. **Sub-button icon bleed**: any unscoped `.bubble-icon` rule will hit sub-button icons. Always cancel with `.bubble-sub-button .bubble-icon { ... !important; }`.
4. **Use the new sub-button schema** — `sub_button: { main: [...], bottom: [...] }` — not the old flat array. See [01-base-structure.md](01-base-structure.md#sub-buttons-v31-sectioned-schema).
5. **Lock element width**: equal `min-width` + `max-width` prevents grid reflow. See [02-button.md](02-button.md#icon-stability).
