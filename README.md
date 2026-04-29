# HA Bubble Card Modules

Custom modules for [Bubble Card](https://github.com/Clooos/Bubble-Card) — a minimalist card collection for Home Assistant.

Each module is a self-contained YAML file that extends Bubble Card cards with custom CSS styling or JavaScript behaviour, without forking the card itself.

---

## Installation

### Bubble Card Tools (recommended, requires v3.1.0+)

1. Install [Bubble Card Tools](https://github.com/Clooos/Bubble-Card-Tools) — available in HACS or manually.
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

Enlarges the icon section so the icon is visually dominant. Creates a flush-left panel effect where the icon container bleeds into the left card edge — left corners are clipped by the card's overflow. Only the right-side corners are independently radiused.

The icon cell width is locked so it cannot shift when state text, attributes, or sub-buttons change.

**Supported card types:** button, calendar, climate, cover, horizontal-buttons-stack, media-player, pop-up, select

**Options:**

| Option | Default | Range | Description |
|--------|---------|-------|-------------|
| `icon_size` | 82 px | 40–160 | Icon size |
| `icon_padding` | 10 px | 0–40 | Padding inside the icon panel |
| `panel_width` | 110 px | 60–200 | Width of the icon panel |
| `left_bleed` | 16 px | 0–40 | How far the panel extends past the left card edge |
| `opacity` | 60 % | 10–100 | Icon panel opacity |
| `radius_tr` | 5 % | 0–50 | Top-right corner radius |
| `radius_br` | 25 % | 0–50 | Bottom-right corner radius |

**Example card YAML:**

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
    radius_tr: 5
    radius_br: 30
```

---

## Contributing

Each module lives in its own YAML file. See [CLAUDE.md](CLAUDE.md) for the full module format, CSS DOM reference for every card type, editor schema options, and coding conventions.