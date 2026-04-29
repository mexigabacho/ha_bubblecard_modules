# HA Bubble Card Modules

Custom modules for [Bubble Card](https://github.com/Clooos/Bubble-Card) (v3.1.6+) — a minimalist card collection for Home Assistant.

Each module is a self-contained YAML file that extends Bubble Card cards with custom CSS styling or JavaScript behaviour, without forking the card itself.

---

## Installation

### Bubble Card Tools (recommended, requires v3.1.0+)

1. Install [Bubble Card Tools](https://github.com/Clooos/Bubble-Card-Tools) — available via HACS or manually.
2. Add the integration: **Settings → Devices & Services → Add Integration → Bubble Card Tools**.
3. Copy the YAML file(s) from this repo to `/config/bubble_card/modules/` on your HA host.
4. The module is immediately available in the **Modules** tab of any compatible Bubble Card.

### Legacy / manual import

1. Open any Bubble Card in the dashboard editor.
2. Go to the **Modules** tab.
3. Click **Import from YAML**, paste the module YAML, and click **Import Module**.

---

## Modules

### `device_large_icon`

**File:** [device_large_icon.yaml](device_large_icon.yaml)

Enlarges the icon section so the icon is visually dominant. Creates a flush-left panel effect where the icon container bleeds into the left card edge — left corners are clipped by the card's `overflow: hidden`. Only the right-side corners are independently radiused.

The icon cell width is locked (`min-width` = `max-width`) so it cannot shift when state text, attributes, or sub-buttons change.

**Supported:** button, calendar, climate, cover, horizontal-buttons-stack, media-player, pop-up, select

| Option | Default | Range | Description |
|--------|---------|-------|-------------|
| `icon_size` | 82 px | 40–160 | Icon size |
| `icon_padding` | 10 px | 0–40 | Padding inside the icon panel |
| `panel_width` | 110 px | 60–200 | Width of the icon panel |
| `left_bleed` | 16 px | 0–40 | How far the panel extends past the left card edge |
| `opacity` | 60 % | 10–100 | Icon panel opacity |
| `radius_tr` | 5 % | 0–50 | Top-right corner radius |
| `radius_br` | 25 % | 0–50 | Bottom-right corner radius |

```yaml
type: custom:bubble-card
card_type: button
entity: light.living_room
modules:
  device_large_icon:
    icon_size: 90
    panel_width: 120
    left_bleed: 12
    opacity: 70
    radius_br: 30
```

---

### `device_state_theme`

**File:** [device_state_theme.yaml](device_state_theme.yaml)

Applies state-driven background gradients, icon colours, and looping animations to cards based on device type presets. Each preset maps entity states to visual effects driven by the card's entity state. Media player cards are excluded to preserve Bubble Card's native album-art background.

**Supported:** button, climate, cover, select, calendar

| Option | Default | Description |
|--------|---------|-------------|
| `device_type` | `none` | Preset to apply (see table below) |
| `enable_gradient` | `false` | Fade gradient on the background instead of solid fill |
| `animations_enabled` | `true` | Enable looping icon animations |
| `animation_speed` | `1.0x` | Speed multiplier (0.25–3.0) |

**Device type presets:**

| Preset | States handled | Effects |
|--------|---------------|---------|
| `vacuum` | cleaning, returning, paused, error | rotation, float, shake |
| `mop` | cleaning, returning, paused, error | pulse, float, shake |
| `washer_dryer` | Running, Starting, Finished, Off, Unknown | shake, pulse, icon colour |
| `ceiling_fan` | on, off | spin-360 |
| `coffee_maker` | Cleaning, Brewing, Ready, Off | glow |
| `light` | on, off | subtle warm background |
| `light_warm` | on, off | warm gradient wash |
| `network_connection` | on, primary, backup, off, unavailable | pulse on backup |

```yaml
type: custom:bubble-card
card_type: button
entity: vacuum.roomba
modules:
  device_state_theme:
    device_type: vacuum
    enable_gradient: true
    animations_enabled: true
    animation_speed: 1.0
```

---

### `room_card_plus_customstyle`

**File:** [room_card_plus_customstyle.yaml](room_card_plus_customstyle.yaml)

Adds bold text-shadow styling to the card name and a dynamic background fill on the `.bubble-button-background` that reflects the light entity's RGB colour and brightness. The fill height tracks brightness as a percentage; the colour tracks the entity's `rgb_color` attribute.

**Supported:** button

No configurable options — edit the YAML directly to adjust colours or thresholds.

---

### `media_app_background`

**File:** [media_app_background.yaml](media_app_background.yaml)

Shows a branded ambient background on a media player card when the integration cannot provide cover art — typically DRM-protected content on an Android TV / Nvidia Shield where the ADB integration can't capture a screenshot. When the entity has a live `entity_picture` (e.g. YouTube), the module steps aside automatically and Bubble Card's native cover-art system takes over.

All backgrounds and logos are embedded as SVG data URIs — zero file deployment required. Built-in support for 12 services:

| Service | Match keywords |
|---------|---------------|
| Netflix | `netflix` |
| Prime Video | `amazon`, `avod`, `primevideo`, `prime` |
| Disney+ | `disney` |
| HBO / Max | `hbo`, `wbd.max` |
| Apple TV+ | `apple`, `atve` |
| Hulu | `hulu` |
| Peacock | `peacock`, `nbcuni` |
| ESPN | `espn` |
| NBA | `nba`, `nbaimd` |
| NFL Network | `nfl`, `nflnetwork` |
| Plex | `plex` |
| Fandango at Home (Vudu) | `fandango`, `vudu` |

**Supported:** media-player

| Option | Default | Description |
|--------|---------|-------------|
| `source_entity` | _(card entity)_ | Entity to read the app attribute from |
| `source_attribute` | `app_id` | Attribute to match — `app_id` (package name, most reliable), `app_name`, or `source` |
| `show_when_paused` | `true` | Also show the background when the player is paused |
| `<service>_enabled` | `true` | Per-service toggle — set to `false` to disable a specific service's background |
| `default_image` | — | Background path shown for any unrecognized app (e.g. `/local/bg/fallback.jpg`) |

> **Tip:** Enable `cover_background: true` on the card for best results. When real cover art arrives it overlays the module background automatically, then fades back when art disappears.

```yaml
type: custom:bubble-card
card_type: media-player
entity: media_player.office_shieldtv
cover_background: true
modules:
  media_app_background:
    source_attribute: app_id
    show_when_paused: true
    peacock_enabled: false   # disable Peacock if you don't use it
```

**SVG source files** are in [device_state_media_images/](device_state_media_images/) — gradient backgrounds (`<service>.svg`), logo overlays (`<service>_logo.svg`), and combined previews (`<service>_combined.svg`). See [CLAUDE.md](CLAUDE.md) for the full workflow to add new services or update logos.

---

## Contributing

Each module lives in its own YAML file. See [CLAUDE.md](CLAUDE.md) for the full module format, CSS DOM reference for every card type (including complete sub-button group structure), editor schema options, and coding conventions.