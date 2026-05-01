# CLAUDE.md — Bubble Card Modules Development Reference

Authoritative development reference for this repository. All modules are YAML files targeting [Bubble Card](https://github.com/Clooos/Bubble-Card) **v3.1.6** (stable as of Apr 2026; v3.2.0 in beta).

---

## ⚠ Rule: Always use the reference files — never guess class names

Before writing any CSS selector, DOM-targeting code, or module suggestion, **read the relevant `bubble-card-reference/` file first**. Do not rely on memory for Bubble Card class names, state classes, or DOM structure — they are verified against source code and must be treated as the single source of truth.

This applies to AI suggestions too: if proposing CSS for a card type, open and cite the reference file. Do not guess or infer selectors.

When a Bubble Card update changes the DOM, the reference files are updated first — and everything else (diagrams, modules) follows from them.

---

## Reference documents in this repo

**[bubble-card-reference/](bubble-card-reference/)** — source-verified per-card-type reference directory. One file per card type, plus SVG layout diagrams in `layouts/`. **This is the primary reference for all DOM work.**

| File | What's inside |
|------|--------------|
| [00-index.md](bubble-card-reference/00-index.md) | Directory index, which cards share base structure, universal dev rules |
| [01-base-structure.md](bubble-card-reference/01-base-structure.md) | Shared base DOM, CSS variables, state classes, sub-button v3.1+ full DOM |
| [02-button.md](bubble-card-reference/02-button.md) | button — all types (switch/state/name/slider), grid layout, icon stability |
| [03-media-player.md](bubble-card-reference/03-media-player.md) | media-player — controls, volume slider, cover art crossfade system |
| [04-climate.md](bubble-card-reference/04-climate.md) | climate — temperature controls, HVAC colors, dual-target mode |
| [05-cover.md](bubble-card-reference/05-cover.md) | cover — open/stop/close, disabled state, device_class variants |
| [06-select.md](bubble-card-reference/06-select.md) | select — dropdown selector, overflow differences |
| [07-separator.md](bubble-card-reference/07-separator.md) | separator — direct icon/name/line DOM (no base elements) |
| [08-calendar.md](bubble-card-reference/08-calendar.md) | calendar — event list, day chips, scroll masking |
| [09-pop-up.md](bubble-card-reference/09-pop-up.md) | pop-up — panel structure, backdrop shadow DOM, transitions |
| [10-horizontal-buttons-stack.md](bubble-card-reference/10-horizontal-buttons-stack.md) | HBS — fixed nav bar, absolute button positioning, scroll masking |
| [layouts/](bubble-card-reference/layouts/) | SVG layout diagrams for each card type + sub-button system |

**[bubble-card-reference.md](bubble-card-reference.md)** — an older single-file reference focused on the `button` card type only. Still useful for:
- Quick CSS cheat sheet (section 9)
- Grid layout explanation for normal/large/large-2-rows
- Icon stability / reflow analysis (section 5)

Do not use it for DOM class names of other card types, sub-button structure, or module YAML format — all superseded by the `bubble-card-reference/` directory above.

---

## Sub-button schema — always use v3.1+ sectioned format

**Never write the old flat sub-button array.** Always use the sectioned schema:

```yaml
# ✅ Correct — v3.1+ sectioned schema
sub_button:
  main_layout: inline        # inline | rows
  bottom_layout: inline      # inline | rows
  main:
    - entity: light.desk
      name: Desk
    - group:
        - entity: light.a
        - entity: light.b
      buttons_layout: inline
  bottom:
    - entity: sensor.temp
      justify_content: center

# ❌ Wrong — legacy flat array (do not use)
sub_button:
  - entity: light.desk
    name: Desk
```

The sectioned schema is cleaner, supports top/bottom positioning, alignment lanes, and explicit groups. It is the only format that supports all v3.1+ layout features. See [bubble-card-reference/01-base-structure.md](bubble-card-reference/01-base-structure.md) for the full DOM structure this produces.

---

## Scripts

Two Python scripts in `scripts/` maintain generated files. Both require only the Python standard library — no `pip install` needed.

### `scripts/generate_layout_diagrams.py` — SVG layout diagrams

Generates the SVG card layout diagrams in `bubble-card-reference/layouts/`. The diagrams are derived from the reference docs in `bubble-card-reference/` and show the spatial 2D layout of each card type with color-coded element regions and DOM trees.

**When to run:**
- After updating any `bubble-card-reference/*.md` file to reflect Bubble Card DOM changes
- After editing the diagram script itself (color palette, layout tweaks, new annotations)

```bash
# Regenerate all 10 diagrams
python3 scripts/generate_layout_diagrams.py

# Regenerate one card only (faster for iterating on a single diagram)
python3 scripts/generate_layout_diagrams.py --card button
python3 scripts/generate_layout_diagrams.py --card media-player

# List all valid card keys
python3 scripts/generate_layout_diagrams.py --list
```

**Valid card keys:** `button`, `media-player`, `climate`, `cover`, `select`, `separator`, `calendar`, `pop-up`, `horizontal-buttons-stack`, `sub-buttons`

**Updating for Bubble Card changes:**

1. Update the relevant `bubble-card-reference/<NN>-<card>.md` file to match the new Bubble Card DOM (verify against Bubble Card source code).
2. Find the corresponding `diagram_<card>()` function in the script and apply the same changes.
3. Regenerate: `python3 scripts/generate_layout_diagrams.py --card <name>`
4. Verify the output SVG renders correctly in a browser or VSCode preview.

Reference doc → diagram function mapping is in the script docstring at the top of the file.

---

### `scripts/build_media_assets.py` — media_app_background assets

Generates combined preview SVGs and regenerates the base64 data URI strings embedded in `media_app_background.yaml`. Full CLI reference and workflow checklists are in the **SVG assets and base64 encoding** section below.

```bash
# Quick reference
python3 scripts/build_media_assets.py              # rebuild all + print YAML blocks to paste
python3 scripts/build_media_assets.py --verify     # check YAML is in sync with files on disk
python3 scripts/build_media_assets.py --service netflix  # process one service only
```

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

## CSS DOM — quick reference

> **Read the reference file for the card type you are targeting before writing any selectors.**
> The tables below are a navigation aid only — not a substitute for the reference files.

### Which cards use the shared base structure?

| Card type | Base structure | Key scoping selector | Reference |
|-----------|---------------|---------------------|-----------|
| button | ✅ full | `.bubble-button-card` | [02-button.md](bubble-card-reference/02-button.md) |
| media-player | ✅ full | `.bubble-media-player` | [03-media-player.md](bubble-card-reference/03-media-player.md) |
| climate | ✅ full | `.bubble-climate` | [04-climate.md](bubble-card-reference/04-climate.md) |
| cover | ✅ full | `.bubble-cover` | [05-cover.md](bubble-card-reference/05-cover.md) |
| select | ✅ full | `.bubble-select` | [06-select.md](bubble-card-reference/06-select.md) |
| separator | ⚠ partial (no base elements) | `.bubble-separator` | [07-separator.md](bubble-card-reference/07-separator.md) |
| calendar | ⚠ partial (no base elements) | `.bubble-calendar-container` | [08-calendar.md](bubble-card-reference/08-calendar.md) |
| pop-up | ❌ none | `.bubble-pop-up` | [09-pop-up.md](bubble-card-reference/09-pop-up.md) |
| horizontal-buttons-stack | ❌ none | `.horizontal-buttons-stack-card` | [10-horizontal-buttons-stack.md](bubble-card-reference/10-horizontal-buttons-stack.md) |

The shared base structure (icon container, name container, background, buttons container) is documented in [01-base-structure.md](bubble-card-reference/01-base-structure.md).

### Critical facts to keep in mind

- **State classes** (`.is-on`, `.is-off`, `.is-unavailable`, `.with-bottom-buttons`) live on the **mainContainer** (`.bubble-<type>-container`), not the wrapper.
- **Background class** varies by card: `.bubble-button-background` (button), `.bubble-color-background` (climate, added alongside `.bubble-background`), `.bubble-cover-background` (media-player alias).
- **Sub-button icon bleed**: any unscoped `.bubble-icon` rule hits sub-button icons too. Always follow with `.bubble-sub-button .bubble-icon { <cancel rule> !important; }`.
- **pop-up backdrop** is in shadow DOM — style it via CSS variables (`--bubble-backdrop-background-color`, `--bubble-backdrop-filter`), not direct selectors.
- **HBS buttons** are absolutely positioned, not flexbox — do not apply flex/grid layout rules to the container.

---

## Sub-buttons — quick reference

Always use the **v3.1+ sectioned schema** (see the rule above). Key points for CSS targeting:

- Individual buttons get a class from their `name` field: lowercased, spaces → `-`, accents stripped. E.g. `name: "Desk Light"` → `.desk-light`. Use this to target specific sub-buttons.
- Auto-grouping: individual `main` items are wrapped in `g_main_auto` when `main_layout: rows`, explicit groups exist, or any `bottom` items exist. Individual `bottom` items share `g_bottom_auto` unless mixed with explicit groups.
- Bottom alignment lanes: `.lane-start` (order 1), `.lane-center` (order 2), `.lane-fill` (order 3), `.lane-end` (order 4) — driven by `justify_content` on the group.

**For the complete sub-button DOM tree, group classes, alignment lane structure, and auto-grouping rules, read [bubble-card-reference/01-base-structure.md](bubble-card-reference/01-base-structure.md).**

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
- **Scope by card-type class** when a rule must not leak across card types. Key discriminators (verify exact names in the reference files):
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

## SVG assets and base64 encoding for `media_app_background`

The `media_app_background` module embeds two kinds of SVG as base64 data URIs directly in the YAML. The source SVG files live in `device_state_media_images/`. **The base64 strings in the YAML must always be kept in sync with those files.**

### Two SVG roles

| Role | Files | Used in | Visual treatment |
|------|-------|---------|-----------------|
| **Gradient background** | `<service>.svg` | `BUILTIN` object → `background-image` on `.bubble-background` | 400×225, solid colour + radialGradient overlay |
| **Logo overlay** | `<service>_logo.svg` | `LOGOS` object → `.bubble-media-player::after` pseudo-element | Any viewBox, transparent bg, rendered outside the blur scope at 25% opacity |
| **Combined preview** | `<service>_combined.svg` | Local reference only — not embedded in YAML | Generated by build script; gradient + logo composited |

---

### Gradient background SVG format

`viewBox="0 0 400 225"`. Structure: solid-fill rect + one or two `radialGradient` overlays. No logo paths.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 225">
  <rect width="400" height="225" fill="#141414"/>
  <radialGradient id="g" cx="50%" cy="50%" r="70%">
    <stop offset="0%" stop-color="#E50914" stop-opacity=".9"/>
    <stop offset="100%" stop-color="#141414" stop-opacity="0"/>
  </radialGradient>
  <rect width="400" height="225" fill="url(#g)"/>
</svg>
```

Rules:
- **No trailing blank lines** inside the SVG — even a single extra `\n` before `</svg>` changes the base64 hash.
- Single trailing newline at end of file (standard Unix).
- Use `id="g"` for single-gradient files. Use distinct IDs (e.g. `id="b"` and `id="r"`) for multi-gradient files. IDs must be unique within the file.

---

### Logo overlay SVG format

Any viewBox is fine — the build script scales to fit. The logo must be **transparent background, white or brand-coloured fill**. No background rect.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path d="M..." fill="white"/>
</svg>
```

Rules:
- Single trailing newline at end of file.
- Multi-colour logos (Peacock, Fandango F-mark) keep their original colours — they render attractively at 25% opacity on a dark background.

**Where to get logo paths:**
- **MDI**: https://pictogrammers.com/library/mdi/ — search by service name. Click → "View SVG" or copy the path. The MDI identifier used in HA (e.g. `mdi:netflix`) usually matches.
- **Simple Icons**: https://simpleicons.org/ — good for brand wordmarks MDI lacks. Note: not all brands are on the latest tag. Known working tags:
  - Amazon/Prime logo: tag **8.6.0** → `https://github.com/simple-icons/simple-icons/blob/8.6.0/icons/amazon.svg`
  - HBO logo: tag **8.6.0** → `https://github.com/simple-icons/simple-icons/blob/8.6.0/icons/hbo.svg`
- **Wikimedia Commons**: good for official wordmarks as SVG. Fetch with `curl -sL <upload URL>`. Examples used:
  - ESPN: `https://upload.wikimedia.org/wikipedia/commons/2/2f/ESPN_wordmark.svg`
  - NBC Peacock (2022): `https://upload.wikimedia.org/wikipedia/commons/2/24/NBC_Peacock_%282022%29.svg`
  - Fandango at Home: `https://commons.wikimedia.org/wiki/File:Fandango_at_Home_logo_%28horizontal%29.svg` (crop to icon only via viewBox)

---

### Logo sizing and viewBox padding

The build script scales each logo SVG by **height**: `scale = logo_height_px / viewBox_height`. This means a wide wordmark logo scaled to 90px tall will be rendered proportionally wide — potentially overflowing or dominating the 400×225 background canvas.

**When to add padding:**
A logo needs viewBox padding if, at the default `--logo-height 90`, the rendered content would be wider than roughly 50–55% of the 400px canvas (i.e., wider than ~200px). Rule of thumb: if the logo's width-to-height aspect ratio exceeds about 2.5:1, you need padding.

**How the scaling works (so you can reason about it):**

```
scale            = logo_height_px / viewBox_height
rendered_width   = viewBox_width  * scale
rendered_height  = viewBox_height * scale   (= logo_height_px, by definition)
content_on_canvas = actual path content * scale
```

Adding padding *expands the viewBox without moving the paths*, which lowers the scale factor, making the rendered content smaller.

**Step-by-step: how to add padding to a downloaded SVG logo**

1. **Download the raw SVG** and open it in a text editor.

2. **Find the viewBox** — note the current values `min_x min_y width height`.

3. **Estimate the path content bounds** — open in a browser or Inkscape. Look for the approximate bounding box of the visible content. For a simple wordmark, this is usually close to the full viewBox, but verify.

4. **Decide the target rendered width** on the 400×225 canvas. A good target is 40–50% of 400px = 160–200px.

5. **Calculate the required padding:**

   ```
   # Target: rendered content width = target_px (e.g. 175px)
   # content_width = measured path width in SVG units
   # content_height = measured path height in SVG units

   scale = target_content_width / content_width
   padded_canvas_height = logo_height_px / scale          # e.g. 90 / scale
   padded_canvas_width  = padded_canvas_height * (content_width / content_height)
   # or just make it wide enough: padded_canvas_width = padded_canvas_height * canvas_aspect_ratio

   pad_x = (padded_canvas_width  - content_width)  / 2   # equal left/right padding
   pad_y = (padded_canvas_height - content_height) / 2   # equal top/bottom padding
   ```

6. **Edit the SVG file:**
   - Change the `viewBox` to `"0 0 {padded_canvas_width} {padded_canvas_height}"`
   - Wrap all existing content in `<g transform="translate({pad_x},{pad_y})"> ... </g>`
   - Keep a `fill` on the paths (usually `fill="white"`)

7. **Verify** with the build script: `python3 scripts/build_media_assets.py --service <name>` and open the resulting `_combined.svg` in a browser.

**Worked example — ESPN:**

The original ESPN wordmark SVG (from Wikimedia Commons) had content approximately 554×137 SVG units.

Without padding — at `--logo-height 90`:
```
scale = 90 / 137 = 0.657
rendered width = 554 * 0.657 = 364px   → 91% of the 400px canvas — way too wide
```

Target: ~175px rendered width (44% of canvas). Working backwards:
```
scale_target = 175 / 554 = 0.316
padded_canvas_height = 90 / 0.316 = 285px  → rounded to 285.4 to preserve aspect ratio
pad_y = (285.4 - 137) / 2 = 74.2
padded_canvas_width = 1154   (chosen to give equal horizontal padding: 300px each side)
pad_x = (1154 - 554) / 2 = 300
```

Result — `espn_logo.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1154 285.4">
<g transform="translate(300,74.2)">
  <path d="M181.064..." fill="white"/>
</g>
</svg>
```

With the padded viewBox, at `--logo-height 90`:
```
scale = 90 / 285.4 = 0.315
rendered wordmark = 554 * 0.315 = 174.5px wide  → 44% of canvas ✓
```

This same technique applies to any wide wordmark. The numbers change; the method is the same.

---

### Adding a new service — complete checklist

1. **Create gradient SVG** → `device_state_media_images/<service>.svg` (400×225 format above)
2. **Create logo SVG** → `device_state_media_images/<service>_logo.svg`
   - Transparent background, white or brand-coloured fill, no background rect.
   - **If the logo is a wide wordmark** (aspect ratio > ~2.5:1), add viewBox padding before saving — see **Logo sizing and viewBox padding** above for the step-by-step and the ESPN worked example.
3. **Run the build script** to generate the combined preview and print updated YAML blocks:
   ```bash
   python3 scripts/build_media_assets.py --service <service>
   ```
4. **Paste the printed base64 lines** into `media_app_background.yaml` — one line into `BUILTIN`, one into `LOGOS`
5. **Add to `APPS` array** in the module code:
   ```js
   { keys: ['keyword1', 'keyword2'], id: '<service>', field: '<service>_image', toggle: '<service>_enabled' },
   ```
   - `keys` — substrings matched (case-insensitive) against the source attribute value. Use `app_id` package name fragments as primary keys.
   - `field` — allows YAML-level override of the background image (`cfg[field]` is checked before `BUILTIN`). No editor UI exposed for this; it's a power-user escape hatch.
   - `toggle` — maps to a boolean editor field; `=== false` skips the service (unset = enabled by default).
6. **Add one boolean toggle** to the "Enabled services" expandable grid in the editor:
   ```yaml
   - name: <service>_enabled
     label: Service Name
     default: true
     selector:
       boolean: {}
   ```
7. **Update the description** string at the top of the module to mention the new service
8. **Bump the version** string (e.g. `'1.6'` → `'1.7'`)
9. **Run verify** to confirm everything is in sync:
   ```bash
   python3 scripts/build_media_assets.py --verify
   ```
10. **Update the inventory table** below

---

### Updating an existing logo — complete checklist

1. **Replace** `device_state_media_images/<service>_logo.svg` with the new file. Apply viewBox padding if it is a wide wordmark — see **Logo sizing and viewBox padding** above.
2. **Regenerate** combined and get the updated base64:
   ```bash
   python3 scripts/build_media_assets.py --service <service>
   ```
3. **Paste the updated `LOGOS/<service>` line** into the YAML (only that one line changes)
4. **Verify**:
   ```bash
   python3 scripts/build_media_assets.py --verify
   ```

---

### The build script — full CLI reference

**Always use `scripts/build_media_assets.py`** — never hand-edit base64 strings in the YAML.

```bash
# Regenerate all combined SVGs + print full BUILTIN and LOGOS blocks for pasting
python3 scripts/build_media_assets.py

# Check YAML base64 matches files on disk — no writes, reports any mismatches
python3 scripts/build_media_assets.py --verify

# Process only one service (fast preview / targeted update)
python3 scripts/build_media_assets.py --service netflix

# Adjust logo rendering in combined SVGs
python3 scripts/build_media_assets.py --blur 0.3          # Gaussian blur stdDev (default 0.3; 0 = off)
python3 scripts/build_media_assets.py --logo-height 90    # logo height in px on 400x225 canvas (default 90)
python3 scripts/build_media_assets.py --logo-opacity 0.5  # logo opacity 0.0–1.0 (default 0.5)

# Preview a single service with custom settings before committing
python3 scripts/build_media_assets.py --service espn --blur 0.3 --logo-height 80
```

The full-run output prints ready-to-paste `BUILTIN` and `LOGOS` blocks. When using `--service`, only the combined SVG is regenerated — no YAML blocks are printed (look up that one service's base64 manually with `base64 -i ... | tr -d '\n'`).

**Note:** blur, logo-height, and logo-opacity only affect the `_combined.svg` preview files. They have no effect on the base64 data URIs embedded in the YAML — those come directly from the source `*.svg` and `*_logo.svg` files.

### Manual base64 for a single file

```bash
# macOS — no line wraps, ready to paste
base64 -i device_state_media_images/netflix.svg | tr -d '\n'
```

Prefix with `data:image/svg+xml;base64,` to get the full data URI.

---

### Current file inventory

| Service | id | Gradient | Logo | Combined | Logo source | Notes |
|---------|-----|----------|------|----------|-------------|-------|
| netflix  | `netflix`  | ✅ | ✅ | ✅ | MDI `mdi:netflix` | viewBox `6.5 2 11 20` (tight crop on N) |
| prime    | `prime`    | ✅ | ✅ | ✅ | Simple Icons 8.6.0 `amazon.svg` | keys: amazon, avod, primevideo, prime |
| disney   | `disney`   | ✅ | ✅ | ✅ | Geometric (3-circle Mickey silhouette) | |
| max      | `max`      | ✅ | ✅ | ✅ | Simple Icons 8.6.0 `hbo.svg` | keys: hbo, wbd.max; gradient indigo/black |
| appletv  | `appletv`  | ✅ | ✅ | ✅ | MDI `mdi:apple` | keys: apple, atve |
| hulu     | `hulu`     | ✅ | ✅ | ✅ | MDI `mdi:hulu` | |
| peacock  | `peacock`  | ✅ | ✅ | ✅ | Wikimedia Commons NBC Peacock (2022) | Multi-colour feather; keys: peacock, nbcuni |
| espn     | `espn`     | ✅ | ✅ | ✅ | Wikimedia Commons ESPN_wordmark.svg | Wide wordmark; padded viewBox `0 0 1154 285.4` |
| nba      | `nba`      | ✅ | ✅ | ✅ | Geometric (basketball circle + seam curves) | Split blue/red gradient |
| nfl      | `nfl`      | ✅ | ✅ | ✅ | Geometric (football ellipse + stitch lines) | keys: nfl, nflnetwork; gradient blue/red |
| plex     | `plex`     | ✅ | ✅ | ✅ | MDI `mdi:plex` | |
| fandango | `fandango` | ✅ | ✅ | ✅ | Wikimedia Commons Fandango at Home logo (F-mark only, cropped viewBox) | keys: fandango, vudu; multi-colour F icon |
| youtubetv | `youtubetv` | ✅ | ✅ | ✅ | Simple Icons YouTube icon (24×24 viewBox, white fill) | keys: youtube.tv, youtubetv — listed before tv to prevent collision |
| tv       | `tv`       | ✅ | ✅ | ✅ | MDI `mdi:television` (24×24 viewBox, white fill) | keys: livetv, live_tv, tv — white-glow gradient; youtubetv entry above catches YouTube TV first |

---

## Testing a module

1. Copy the YAML file to `/config/bubble_card/modules/` on the HA host (requires Bubble Card Tools integration).
2. Edit a card in the HA dashboard, open the **Modules** tab, enable the module.
3. Use browser DevTools on the HA frontend to inspect shadow DOM and verify class names.
4. Keep the `supported` list accurate — it controls which card types show the module in the UI.
