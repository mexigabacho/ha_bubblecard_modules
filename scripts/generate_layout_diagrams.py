#!/usr/bin/env python3
"""Generate SVG layout diagrams for each Bubble Card card type.

Style mirrors bubble-card-layout-diagram.svg:
  - White background, pastel color regions, light borders
  - 2D card mockup showing spatial element positions
  - Color-coded monospace DOM tree below the mockup
  - Grid/layout annotations where relevant

Outputs to bubble-card-reference/layouts/ relative to the repo root.

Usage:
    python3 scripts/generate_layout_diagrams.py               # regenerate all
    python3 scripts/generate_layout_diagrams.py --card button  # one card
    python3 scripts/generate_layout_diagrams.py --list         # list card keys

── When Bubble Card updates ─────────────────────────────────────────────────────
DOM class names and structure are sourced from the per-card reference docs.
When Bubble Card changes, the update workflow is:

  1. Update the relevant bubble-card-reference/<NN>-<card>.md file with the
     new class names / structure (verify against the Bubble Card source code).
  2. Find the corresponding diagram_<card>() function in THIS file and apply
     the same changes to the DOM tree list and any spatial mockup elements.
  3. Run:  python3 scripts/generate_layout_diagrams.py
  4. Verify the SVG in a browser or VSCode preview.

Reference doc → diagram function mapping:
  01-base-structure.md    →  (base DOM used by all diagram functions)
  02-button.md            →  diagram_button()
  03-media-player.md      →  diagram_media_player()
  04-climate.md           →  diagram_climate()
  05-cover.md             →  diagram_cover()
  06-select.md            →  diagram_select()
  07-separator.md         →  diagram_separator()
  08-calendar.md          →  diagram_calendar()
  09-pop-up.md            →  diagram_popup()
  10-horizontal-buttons-stack.md  →  diagram_hbs()
  01-base-structure.md (sub-button section)  →  diagram_sub_buttons()
─────────────────────────────────────────────────────────────────────────────────
"""

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = REPO_ROOT / "bubble-card-reference" / "layouts"

FONT = "sans-serif"
MONO = "monospace"

# ── Pastel colour palette (matches original) ──────────────────────────────────
P = {
    "bg":          "#ffffff",
    "card_fill":   "#f1efe8",
    "card_stroke": "#b4b2a9",
    "card_text":   "#5f5e5a",

    # Per-element colours — fill / stroke / text
    "container":   ("#e6f1fb", "#85b7eb", "#185fa5"),  # blue
    "wrapper":     ("#f3f0fb", "#a89fd8", "#534ab7"),  # indigo (grid root)
    "background":  ("#e1f5ee", "#5dcaa5", "#0f6e56"),  # green
    "icon":        ("#faece7", "#d85a30", "#993c1d"),  # orange
    "name":        ("#e6f1fb", "#378add", "#185fa5"),  # blue-mid
    "state":       ("#e1f5ee", "#1d9e75", "#0f6e56"),  # teal
    "subbutton":   ("#faeeda", "#ba7517", "#854f0b"),  # amber
    "buttons":     ("#eaf3de", "#639922", "#3b6d11"),  # lime
    "media":       ("#f0e6fb", "#a855d8", "#7a1fad"),  # purple
    "temp":        ("#fde9d8", "#e07030", "#9a4510"),  # warm orange
    "cover_btn":   ("#e8f5fd", "#4ba8d8", "#1a6e9a"),  # sky
    "backdrop":    ("#f8f0e8", "#c89060", "#7a5020"),  # warm brown
    "event":       ("#f5f0fb", "#9070c0", "#5a3090"),  # violet
    "dyn":         ("#fffbe6", "#c8a020", "#7a6010"),  # yellow  (dynamic/conditional)
    "note":        ("#f5f5f0", "#aaaaaa", "#555555"),  # grey
}

# ── SVG helpers ───────────────────────────────────────────────────────────────

def svg_open(w, h, title=""):
    return (
        f'<svg width="{w}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:{P["bg"]};font-family:{FONT};">\n'
        f'<!-- {title} -->\n'
    )

def svg_close():
    return "</svg>\n"

def R(x, y, w, h, fill, stroke, rx=6, sw=0.5, opacity=1):
    op = f' opacity="{opacity}"' if opacity < 1 else ''
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{op}/>\n')

def T(x, y, text, size=11, fill="#333", anchor="start", weight="normal", font=None):
    font = font or FONT
    return (f'<text font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'x="{x}" y="{y}" text-anchor="{anchor}" font-family="{font}">'
            f'{text}</text>\n')

def line(x1, y1, x2, y2, stroke="#888", sw=0.5, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>\n'

def divider(y, w=640, x0=40):
    return line(x0, y, x0 + w, y, stroke="#ccc", dash="4 4")

def section_title(x, y, title, subtitle=""):
    out = T(x, y, title, size=15, weight="500", fill="#1a1a1a")
    if subtitle:
        offset = len(title) * 8 + x + 4
        out += T(offset, y, subtitle, size=12, fill="#666")
    return out

def color_block(x, y, w, h, key, label_lines, rx=6, sw=0.5):
    fill, stroke, text_color = P[key]
    out = R(x, y, w, h, fill, stroke, rx=rx, sw=sw)
    for i, line_text in enumerate(label_lines):
        out += T(x + w // 2, y + 16 + i * 14, line_text, size=10, fill=text_color, anchor="middle")
    return out

def legend_swatch(x, y, key, label):
    fill, stroke, _ = P[key]
    out = R(x, y, 12, 12, fill, stroke, rx=2, sw=0.5)
    out += T(x + 16, y + 10, label, size=11, fill="#333")
    return out

def dom_line(x, y, text, color="#222"):
    return T(x, y, text, size=12, fill=color, font=MONO)

def col_tick(x, y):
    return line(x, y, x, y + 16, stroke="#888", sw=0.5)

def col_label(x, y, top_label, bot_label=""):
    out = T(x, y + 28, top_label, size=11, fill="#333", anchor="middle")
    if bot_label:
        out += T(x, y + 42, bot_label, size=10, fill="#666", anchor="middle")
    return out


# ── Card mockup primitives ────────────────────────────────────────────────────

def card_shell(x, y, w, h, label=".bubble-*-container"):
    """Outer ha-card box."""
    out = R(x, y, w, h, P["card_fill"], P["card_stroke"], rx=12, sw=0.5)
    out += T(x + 12, y + 16, "ha-card", size=11, fill=P["card_text"])
    out += T(x + 12, y + 30, label, size=10, fill=P["container"][2])
    return out

def icon_box(x, y, w, h, lines=None):
    lines = lines or ["grid area i", ".bubble-icon-container", ".bubble-icon"]
    return color_block(x, y, w, h, "icon", lines)

def name_box(x, y, w, h, lines=None):
    lines = lines or ["grid area n", ".bubble-name-container"]
    return color_block(x, y, w, h, "name", lines)

def state_box(x, y, w, h, lines=None):
    lines = lines or [".bubble-state / .bubble-name"]
    return color_block(x, y, w, h, "state", lines)

def subbutton_box(x, y, w, h, lines=None):
    lines = lines or ["grid area a", ".bubble-sub-button-container"]
    return color_block(x, y, w, h, "subbutton", lines)

def bg_overlay(x, y, w, h, label=".bubble-background  (absolute fill)"):
    fill, stroke, text_color = P["background"]
    out = R(x, y, w, h, fill, stroke, rx=8, sw=0.5, opacity=0.25)
    out += T(x + 10, y + 14, label, size=10, fill=text_color)
    return out

def grid_outline(x, y, w, h):
    _, stroke, _ = P["wrapper"]
    return R(x, y, w, h, "none", stroke, rx=8, sw=1.5)

def dyn_box(x, y, w, h, lines, note="conditional"):
    fill, stroke, text_color = P["dyn"]
    out = R(x, y, w, h, fill, stroke, rx=4, sw=0.5)
    for i, l in enumerate(lines):
        out += T(x + 6, y + 14 + i * 13, l, size=10, fill=text_color)
    out += T(x + w - 4, y + 8, f"↑ {note}", size=9, fill=stroke, anchor="end")
    return out


# ── Diagram functions ─────────────────────────────────────────────────────────

def diagram_button():
    W, H = 680, 860
    out = svg_open(W, H, "Button Card Layout")

    # ── Normal layout ──────────────────────────────────────────────────
    out += section_title(40, 32, "Button card — Normal layout", "(card_layout: normal)")

    cx, cy, cw, ch = 40, 44, 380, 160
    out += card_shell(cx, cy, cw, ch, label=".bubble-button-card-container  [.is-on / .is-off / .is-unavailable]")
    out += bg_overlay(52, 66, 356, 128)
    out += grid_outline(52, 66, 356, 128)

    out += icon_box(64, 80, 72, 100, ["grid area i", ".bubble-icon-container", ".icon-with-state", ".bubble-icon"])
    out += name_box(144, 80, 154, 44, ["grid area n", ".bubble-name-container"])
    out += state_box(144, 132, 154, 48, [".bubble-state", ".bubble-name"])
    out += subbutton_box(306, 80, 90, 100, ["grid area a", ".bubble-sub-", "button-container", "(right side)"])

    # Column ticks
    for x in [64, 136, 144, 298, 306, 408]:
        out += col_tick(x, 192)
    out += col_label(100,  192, "auto",  "(icon col)")
    out += col_label(221,  192, "1fr",   "(name col)")
    out += col_label(357,  192, "auto",  "(sub-btn col)")
    out += T(40, 250, 'Grid template (normal):  grid-template-areas: "i n a"   ·   grid-template-columns: auto 1fr auto',
             size=11, fill="#444")

    # Legend
    lx = 452
    out += T(lx, 60, "Key classes", size=13, weight="500", fill="#1a1a1a")
    for i, (key, label) in enumerate([
        ("icon",       ".bubble-icon-container"),
        ("name",       ".bubble-name-container"),
        ("subbutton",  ".bubble-sub-button-container"),
        ("wrapper",    ".bubble-button-card (grid root)"),
        ("background", ".bubble-button-background"),
    ]):
        out += legend_swatch(lx, 68 + i * 18, key, label)
    out += T(lx, 162, ".bubble-icon  (icon element)", size=11, fill="#333")
    out += T(lx, 178, ".icon-with-state  (icon bg circle)", size=11, fill="#333")

    out += divider(270)

    # ── Large layout ───────────────────────────────────────────────────
    out += section_title(40, 296, "Large layout", "(card_layout: large  — default in section view)")

    cx, cy, cw, ch = 40, 308, 380, 200
    out += card_shell(cx, cy, cw, ch, label=".bubble-button-card-container.large")
    out += bg_overlay(52, 330, 356, 168)
    out += grid_outline(52, 330, 356, 168)

    out += icon_box(64, 356, 120, 130, ["grid area i", ".bubble-icon-container", "(larger, centered)", ".icon-with-state", ".bubble-icon"])
    out += name_box(192, 356, 150, 60, ["grid area n", ".bubble-name-container"])
    out += state_box(192, 424, 150, 62, [".bubble-state", ".bubble-name", "(or sub-buttons below)"])
    _, stroke, _ = P["buttons"]
    out += R(350, 356, 50, 130, P["buttons"][0], stroke, rx=6, sw=0.5)
    out += T(375, 424, "sub-btns", size=10, fill=P["buttons"][2], anchor="middle")

    for x in [64, 184, 192, 342, 350, 408]:
        out += col_tick(x, 498)
    out += col_label(124, 498, "auto",  "(icon — bigger)")
    out += col_label(267, 498, "1fr",   "(name + state)")
    out += col_label(379, 498, "auto",  "(sub-buttons)")

    out += divider(558)

    # ── DOM tree ───────────────────────────────────────────────────────
    out += T(40, 582, "DOM hierarchy (base structure — button, media-player, climate, cover, select)",
             size=13, weight="500", fill="#1a1a1a")

    dom = [
        ("#222", "ha-card"),
        ("#222", "  └─ .bubble-button-card-container  (outer size/overflow boundary)"),
        (P["background"][2], "      ├─ .bubble-button-background  (abs. positioned color/image fill)"),
        (P["wrapper"][2],    "      └─ .bubble-button-card  (grid root → areas: i  n  a)"),
        (P["icon"][2],       "          ├─ .bubble-icon-container  [grid-area: i]"),
        (P["icon"][2],       "          │   └─ .icon-with-state  →  .bubble-icon  (&lt;ha-icon&gt;)"),
        (P["name"][2],       "          ├─ .bubble-name-container  [grid-area: n]"),
        (P["name"][2],       "          │   ├─ .bubble-name  ·  .bubble-state"),
        (P["subbutton"][2],  "          └─ .bubble-sub-button-container  [grid-area: a]"),
        (P["subbutton"][2],  "              └─ .bubble-sub-button ×N  →  icon  ·  name-container"),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 602 + i * 18, text, color)

    out += T(40, 790, "v3.1+ sub-button groups: .bubble-sub-button-container (top) + .bubble-sub-button-bottom-container (bottom)",
             size=10, fill="#666")

    out += R(40, 800, 600, 20, P["note"][0], P["note"][1], rx=3, sw=0.5)
    out += T(46, 813, "State classes on .bubble-button-card-container:   .is-on   /   .is-off   /   .is-unavailable   /   .large   /   .with-bottom-buttons",
             size=11, fill="#555")

    out += T(40, 840, "button_type: slider → also adds .bubble-range-slider inside mainContainer (absolute, full-card overlay for drag-to-set)",
             size=10, fill="#888")

    out += svg_close()
    return out


def diagram_media_player():
    W, H = 680, 880
    out = svg_open(W, H, "Media Player Card Layout")
    out += section_title(40, 32, "Media Player card", "(card_type: media-player)")

    # Card shell
    out += card_shell(40, 44, 580, 200,
                      label=".bubble-media-player-container  [.with-bottom-buttons]  [.large]")
    out += bg_overlay(52, 70, 556, 164,
                      ".bubble-background  .bubble-cover-background  (filter: blur(50px) opacity:0.5 when cover_background:true)")
    out += grid_outline(52, 70, 556, 164)

    # Icon area (with entity picture and mute button)
    out += icon_box(64, 84, 100, 140, [".bubble-icon-container", ".bubble-entity-picture", "(art thumbnail)", ".bubble-mute-button"])

    # Name / media-info (alternate display)
    out += name_box(172, 84, 200, 60, [".bubble-name-container", "(shown when idle)"])
    _, stroke, text_c = P["media"]
    out += R(172, 152, 200, 60, P["media"][0], stroke, rx=6, sw=0.5)
    out += T(272, 172, ".bubble-media-info-container", size=10, fill=text_c, anchor="middle")
    out += T(272, 186, "(title + artist, shown playing)", size=10, fill=text_c, anchor="middle")
    out += T(272, 200, ".bubble-title  +  .bubble-artist", size=10, fill=text_c, anchor="middle")

    # Control buttons
    out += R(380, 84, 220, 60, P["buttons"][0], P["buttons"][1], rx=6, sw=0.5)
    out += T(490, 100, ".bubble-buttons-container", size=10, fill=P["buttons"][2], anchor="middle")
    btn_labels = ["power", "prev", "next", "vol", "play/pause"]
    for i, lbl in enumerate(btn_labels):
        bx = 386 + i * 42
        out += R(bx, 108, 36, 28, P["media"][0], P["media"][1], rx=4, sw=0.5)
        out += T(bx + 18, 124, lbl, size=8, fill=P["media"][2], anchor="middle")

    # Volume slider
    _, stroke, text_c = P["dyn"]
    out += R(380, 152, 220, 44, P["dyn"][0], stroke, rx=6, sw=0.5)
    out += T(490, 166, ".bubble-volume-slider-wrapper", size=10, fill=text_c, anchor="middle")
    out += T(490, 178, "[.is-hidden when closed]", size=9, fill=text_c, anchor="middle")
    out += T(490, 190, "mute-btn  ·  slider  ·  close-btn", size=9, fill=text_c, anchor="middle")

    out += divider(260, w=598)

    # Cover art crossfade section
    out += section_title(40, 286, "Cover art crossfade system", "(key for module CSS)")

    out += R(40, 298, 290, 200, P["icon"][0], P["icon"][1], rx=8, sw=0.5)
    out += T(185, 318, "Icon scope", size=12, weight="500", fill=P["icon"][2], anchor="middle")
    out += T(185, 334, ".bubble-entity-picture", size=11, fill=P["icon"][2], anchor="middle")
    out += T(185, 350, "[.bubble-cover-icon-crossfade]", size=10, fill="#888", anchor="middle")
    out += R(52, 360, 120, 48, P["note"][0], P["note"][1], rx=4)
    out += T(112, 376, "layer A", size=10, fill=P["note"][2], anchor="middle")
    out += T(112, 390, ".is-visible", size=9, fill="#639922", anchor="middle")
    out += R(180, 360, 120, 48, P["note"][0], P["note"][1], rx=4)
    out += T(240, 376, "layer B", size=10, fill=P["note"][2], anchor="middle")
    out += T(240, 390, "(inactive)", size=9, fill="#888", anchor="middle")
    out += T(52, 420, "2s CSS opacity crossfade between layers", size=10, fill="#555")
    out += T(52, 435, "Do NOT set background-image directly on", size=10, fill="#c0392b")
    out += T(52, 449, ".bubble-entity-picture after first art load", size=10, fill="#c0392b")
    out += T(52, 463, "(the element is mutated to a crossfade host)", size=9, fill="#888")

    out += R(340, 298, 290, 200, P["background"][0], P["background"][1], rx=8, sw=0.5)
    out += T(485, 318, "Background scope", size=12, weight="500", fill=P["background"][2], anchor="middle")
    out += T(485, 334, ".bubble-background.bubble-cover-background", size=10, fill=P["background"][2], anchor="middle")
    out += T(485, 350, "[.bubble-cover-background-crossfade]", size=10, fill="#888", anchor="middle")
    out += T(485, 366, "requires cover_background: true", size=10, fill="#888", anchor="middle")
    out += R(352, 378, 120, 48, P["note"][0], P["note"][1], rx=4)
    out += T(412, 394, "layer A", size=10, fill=P["note"][2], anchor="middle")
    out += R(480, 378, 120, 48, P["note"][0], P["note"][1], rx=4)
    out += T(540, 394, "layer B", size=10, fill=P["note"][2], anchor="middle")
    out += T(352, 440, "filter: blur(50px) on container →", size=10, fill="#555")
    out += T(352, 454, "blurs entire element incl. layers", size=10, fill="#555")
    out += T(352, 468, "Use ::after pseudo for unblurred overlay", size=10, fill="#0f6e56")
    out += T(352, 482, "e.g. logo at z-index:1 on .bubble-media-player", size=9, fill="#888")

    out += divider(510, w=598)

    # DOM tree
    out += T(40, 536, "DOM hierarchy", size=13, weight="500", fill="#1a1a1a")
    dom = [
        ("#222", "ha-card"),
        ("#222", "  └─ .bubble-media-player-container"),
        (P["background"][2], "      ├─ .bubble-background  .bubble-cover-background  (blurred bg)"),
        (P["wrapper"][2],    "      └─ .bubble-media-player  .bubble-wrapper"),
        (P["icon"][2],       "          ├─ .bubble-icon-container"),
        (P["icon"][2],       "          │   ├─ .bubble-entity-picture  (art thumbnail + crossfade host)"),
        (P["icon"][2],       "          │   └─ .bubble-mute-button  [.is-hidden]"),
        (P["name"][2],       "          ├─ .bubble-name-container  (shown when idle)"),
        (P["media"][2],      "          ├─ .bubble-media-info-container  (shown when playing)"),
        (P["media"][2],      "          │   ├─ .bubble-title  ·  .bubble-artist"),
        (P["buttons"][2],    "          ├─ .bubble-buttons-container  (.bubble-button-container alias)"),
        (P["buttons"][2],    "          │   ├─ .bubble-power-button  .bubble-previous-button  .bubble-next-button"),
        (P["buttons"][2],    "          │   └─ .bubble-volume-button  .bubble-play-pause-button"),
        (P["dyn"][1],        "          └─ .bubble-volume-slider-wrapper  [.is-hidden when closed]  ← dynamic"),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 556 + i * 18, text, color)

    out += R(40, 818, 600, 20, P["note"][0], P["note"][1], rx=3)
    out += T(46, 831, "State: playing→show art  |  idle→2s delay→fade  |  off/unavailable/standby→clear immediately",
             size=11, fill="#555")

    out += svg_close()
    return out


def diagram_climate():
    W, H = 680, 760
    out = svg_open(W, H, "Climate Card Layout")
    out += section_title(40, 32, "Climate card", "(card_type: climate)")

    out += card_shell(40, 44, 580, 180,
                      label=".bubble-climate-container  [.is-on / .is-off]  [.large]")
    _, bg_stroke, bg_text = P["background"]
    out += bg_overlay(52, 70, 556, 144,
                      ".bubble-background  .bubble-color-background  (bg-color driven by JS per HVAC mode)")
    out += grid_outline(52, 70, 556, 144)

    out += icon_box(64, 84, 100, 120, [".bubble-icon-container", ".bubble-icon", "(color = HVAC mode)"])
    out += name_box(172, 84, 160, 60, [".bubble-name-container", ".bubble-name  /  .bubble-state"])

    # Temperature container
    _, stroke, text_c = P["temp"]
    out += R(340, 84, 256, 120, P["temp"][0], stroke, rx=6, sw=0.5)
    out += T(468, 100, ".bubble-buttons-container", size=10, fill=text_c, anchor="middle")

    out += R(348, 108, 110, 44, P["icon"][0], P["icon"][1], rx=4, sw=0.5)
    out += T(403, 122, ".bubble-temperature-container", size=9, fill=P["icon"][2], anchor="middle")
    out += T(403, 134, "minus · display · plus", size=9, fill=P["icon"][2], anchor="middle")

    out += R(464, 108, 120, 44, P["dyn"][0], P["dyn"][1], rx=4, sw=0.5)
    out += T(524, 122, ".bubble-target-temp-container", size=9, fill=P["dyn"][1], anchor="middle")
    out += T(524, 134, "(heat_cool mode only)", size=9, fill=P["dyn"][1], anchor="middle")

    out += R(348, 160, 110, 32, P["note"][0], P["note"][1], rx=4)
    out += T(403, 174, "low-temp-container", size=9, fill="#c0392b", anchor="middle")
    out += T(403, 186, "(heat color)", size=9, fill="#c0392b", anchor="middle")

    out += R(464, 160, 120, 32, P["note"][0], P["note"][1], rx=4)
    out += T(524, 174, "high-temp-container", size=9, fill="#1a6e9a", anchor="middle")
    out += T(524, 186, "(cool color)", size=9, fill="#1a6e9a", anchor="middle")

    out += divider(242, w=598)

    # HVAC color table
    out += T(40, 268, "HVAC mode → background color", size=13, weight="500", fill="#1a1a1a")
    modes = [
        ("heat", "#e07030", "var(--state-climate-heat-color)"),
        ("cool", "#1a6e9a", "var(--state-climate-cool-color)"),
        ("heat_cool / auto", "#7a1fad", "var(--state-climate-auto-color)"),
        ("dry", "#ba7517", "var(--state-climate-dry-color)"),
        ("fan_only", "#3b6d11", "var(--state-climate-fan_only-color)"),
        ("off", "#888888", "transparent / none"),
    ]
    for i, (mode, color, var) in enumerate(modes):
        row = i // 2
        col = i % 2
        mx = 40 + col * 300
        my = 280 + row * 26
        out += R(mx, my, 12, 12, color, color, rx=2)
        out += T(mx + 16, my + 10, f"{mode}  →  {var}", size=11, fill="#333")

    out += divider(370, w=598)

    # DOM tree
    out += T(40, 396, "DOM hierarchy", size=13, weight="500", fill="#1a1a1a")
    dom = [
        ("#222", "ha-card"),
        ("#222", "  └─ .bubble-climate-container"),
        (P["background"][2], "      ├─ .bubble-background  .bubble-color-background  (HVAC-mode bg color)"),
        (P["wrapper"][2],    "      └─ .bubble-climate  .bubble-wrapper"),
        (P["icon"][2],       "          ├─ .bubble-icon-container → .bubble-icon  (color = HVAC mode)"),
        (P["name"][2],       "          ├─ .bubble-name-container → .bubble-name  ·  .bubble-state"),
        (P["temp"][2],       "          └─ .bubble-buttons-container"),
        (P["temp"][2],       "              ├─ .bubble-temperature-container  [.hidden when hide_temperature]"),
        (P["temp"][2],       "              │   └─ .bubble-climate-minus-button  ·  .bubble-temperature-display  ·  .bubble-climate-plus-button"),
        (P["dyn"][1],        "              └─ .bubble-target-temperature-container  [only in heat_cool mode]"),
        (P["dyn"][1],        "                  ├─ .bubble-low-temp-container  (heat color)"),
        (P["dyn"][1],        "                  └─ .bubble-high-temp-container  (cool color)"),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 416 + i * 18, text, color)

    out += R(40, 640, 600, 18, P["note"][0], P["note"][1], rx=3)
    out += T(46, 651, "tap-warning animation (shake) fires on mainContainer when user taps +/- at temperature limit",
             size=11, fill="#555")

    out += svg_close()
    return out


def diagram_cover():
    W, H = 680, 620
    out = svg_open(W, H, "Cover Card Layout")
    out += section_title(40, 32, "Cover card", "(card_type: cover)")

    out += card_shell(40, 44, 580, 160, label=".bubble-cover-container  [.is-on / .is-off]  [.large]")
    out += bg_overlay(52, 70, 556, 124)
    out += grid_outline(52, 70, 556, 124)

    out += icon_box(64, 84, 100, 100, [".bubble-icon-container", ".bubble-icon", "(open/close icon)"])
    out += name_box(172, 84, 180, 60, [".bubble-name-container", ".bubble-name  /  .bubble-state"])

    # Action buttons
    _, stroke, text_c = P["cover_btn"]
    out += R(360, 84, 236, 100, P["cover_btn"][0], stroke, rx=6, sw=0.5)
    out += T(478, 100, ".bubble-buttons-container", size=10, fill=text_c, anchor="middle")
    out += T(478, 112, ".bubble-buttons  .buttons-container", size=9, fill="#888", anchor="middle")

    for i, (lbl, cls, disabled_note) in enumerate([
        ("OPEN",  ".bubble-open",  "[.disabled at fully open]"),
        ("STOP",  ".bubble-stop",  "[hidden if no STOP feature]"),
        ("CLOSE", ".bubble-close", "[.disabled at fully closed]"),
    ]):
        bx = 366 + i * 74
        out += R(bx, 118, 64, 54, P["cover_btn"][0], stroke, rx=4, sw=0.5)
        out += T(bx + 32, 136, lbl, size=10, fill=text_c, anchor="middle", weight="500")
        out += T(bx + 32, 148, cls, size=8, fill=text_c, anchor="middle")
        out += T(bx + 32, 160, disabled_note, size=7, fill="#888", anchor="middle")

    out += divider(222, w=598)

    # Disabled state note
    out += R(40, 232, 580, 30, "#fff5f5", "#f87171", rx=6, sw=0.5)
    out += T(50, 250, ".disabled class: opacity:0.3 !important; pointer-events:none — added automatically when cover is fully open/closed",
             size=11, fill="#c0392b")

    out += divider(278, w=598)

    out += T(40, 304, "DOM hierarchy", size=13, weight="500", fill="#1a1a1a")
    dom = [
        ("#222", "ha-card"),
        ("#222", "  └─ .bubble-cover-container"),
        (P["background"][2], "      ├─ .bubble-background"),
        (P["wrapper"][2],    "      └─ .bubble-cover  .bubble-wrapper"),
        (P["icon"][2],       "          ├─ .bubble-icon-container → .bubble-icon  (switches open/close icon)"),
        (P["name"][2],       "          ├─ .bubble-name-container → .bubble-name  ·  .bubble-state"),
        (P["cover_btn"][2],  "          └─ .bubble-buttons-container  .bubble-buttons  .buttons-container"),
        (P["cover_btn"][2],  "              ├─ .bubble-cover-button  .bubble-open  [.disabled]"),
        (P["cover_btn"][2],  "              │   └─ ha-icon.bubble-cover-button-icon  .bubble-icon-open"),
        (P["cover_btn"][2],  "              ├─ .bubble-cover-button  .bubble-stop  [display:none if no STOP]"),
        (P["cover_btn"][2],  "              └─ .bubble-cover-button  .bubble-close  [.disabled]"),
        (P["cover_btn"][2],  "                  └─ ha-icon.bubble-cover-button-icon  .bubble-icon-close"),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 324 + i * 18, text, color)

    out += R(40, 560, 580, 18, P["note"][0], P["note"][1], rx=3)
    out += T(46, 571, "device_class: curtain → icons switch to arrow-expand-horizontal / arrow-collapse-horizontal",
             size=11, fill="#555")

    out += svg_close()
    return out


def diagram_select():
    W, H = 680, 540
    out = svg_open(W, H, "Select Card Layout")
    out += section_title(40, 32, "Select card", "(card_type: select — identical to button DOM plus dropdown)")

    out += card_shell(40, 44, 580, 160,
                      label=".bubble-select-container  .bubble-select-card-container  [overflow:inherit ← dropdown needs this]")
    out += bg_overlay(52, 70, 556, 124, ".bubble-background  (cursor:pointer; single tap forced to none — dropdown handles open)")
    out += grid_outline(52, 70, 556, 124)

    out += icon_box(64, 84, 100, 100, [".bubble-icon-container", ".bubble-icon"])
    out += name_box(172, 84, 300, 60, [".bubble-name-container", ".bubble-name  +  .bubble-state", "(current option shown in state)"])
    out += subbutton_box(480, 84, 120, 100, [".bubble-buttons-container", "(dropdown arrow", "appended here)"])

    _, stroke, text_c = P["dyn"]
    out += R(52, 152, 556, 42, P["dyn"][0], stroke, rx=4, sw=0.5)
    out += T(52 + 278, 166, ".bubble-dropdown  (rendered as absolute overlay by dropdown component when open)", size=10,
             fill=text_c, anchor="middle")
    out += T(52 + 278, 180, "NOT a child of the card DOM — escapes via overflow:inherit on .bubble-select-container", size=10,
             fill="#888", anchor="middle")

    out += divider(222, w=598)

    out += T(40, 248, "DOM hierarchy", size=13, weight="500", fill="#1a1a1a")
    dom = [
        ("#222", "ha-card"),
        ("#222", "  └─ .bubble-select-container  .bubble-select-card-container"),
        (P["background"][2], "      ├─ .bubble-background  (cursor:pointer; tap_action forced to none)"),
        (P["wrapper"][2],    "      └─ .bubble-select  .bubble-wrapper"),
        (P["icon"][2],       "          ├─ .bubble-icon-container → .bubble-icon"),
        (P["name"][2],       "          ├─ .bubble-name-container → .bubble-name  ·  .bubble-state  (selected option)"),
        (P["subbutton"][2],  "          └─ .bubble-buttons-container  (dropdown arrow appended here)"),
        (P["dyn"][1],        "   [dropdown overlay appended outside card via absolute positioning when open]"),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 268 + i * 18, text, color)

    out += R(40, 440, 580, 36, "#fff8e6", "#c8a020", rx=6, sw=0.5)
    out += T(50, 454, "Key difference from button: overflow:inherit on container (not overflow:hidden).", size=11, fill="#7a6010")
    out += T(50, 468, "This allows the dropdown option list to escape the card boundary and render above other cards.", size=11, fill="#7a6010")

    out += svg_close()
    return out


def diagram_separator():
    W, H = 680, 520
    out = svg_open(W, H, "Separator Card Layout")
    out += section_title(40, 32, "Separator card", "(card_type: separator — does NOT use base elements)")

    # Card mockup — minimal, no wrapper
    out += R(40, 44, 580, 70, P["card_fill"], P["card_stroke"], rx=12, sw=0.5)
    out += T(52, 62, ".bubble-separator-container  (background:none; overflow:visible; height:40px)", size=10, fill="#555")

    out += R(52, 70, 52, 36, P["icon"][0], P["icon"][1], rx=6, sw=0.5)
    out += T(78, 84, "ha-icon", size=10, fill=P["icon"][2], anchor="middle")
    out += T(78, 97, ".bubble-icon", size=9, fill=P["icon"][2], anchor="middle")

    out += R(112, 70, 100, 36, P["name"][0], P["name"][1], rx=6, sw=0.5)
    out += T(162, 84, "h4.bubble-name", size=10, fill=P["name"][2], anchor="middle")

    out += R(220, 78, 380, 18, P["state"][0], P["state"][1], rx=4, sw=0.5)
    out += T(410, 90, ".bubble-line  (flex-grow:1; height:6px; opacity:0.6)", size=10, fill=P["state"][2], anchor="middle")

    out += divider(134, w=598)

    out += R(40, 144, 580, 60, "#fff8e6", "#c8a020", rx=6, sw=0.5)
    out += T(50, 162, "Key differences from all other card types:", size=12, weight="500", fill="#7a6010")
    diffs = [
        "• ha-icon.bubble-icon is a direct child of mainContainer — NOT inside .bubble-icon-container",
        "• No .bubble-background  ·  No .bubble-content-container  ·  No .bubble-buttons-container",
        "• Name element is h4, not div  ·  Card background is none  ·  overflow: visible (not hidden)",
        "• Sub-button container has position:sticky; top:0  (unique — sticks to scroll container)",
    ]
    for i, d in enumerate(diffs):
        out += T(50, 178 + i * 14, d, size=10, fill="#7a6010")

    out += divider(224, w=598)

    out += T(40, 250, "DOM hierarchy", size=13, weight="500", fill="#1a1a1a")
    dom = [
        ("#222", "ha-card"),
        ("#222", "  └─ .bubble-separator-container  .bubble-separator  (background:none; overflow:visible)"),
        (P["icon"][2],      "      ├─ ha-icon.bubble-icon  ← direct child (no .bubble-icon-container wrapper)"),
        (P["name"][2],      "      ├─ h4.bubble-name  (.bubble-name:empty → display:none)"),
        (P["state"][2],     "      ├─ .bubble-line  (flex-grow:1; the horizontal rule)"),
        (P["subbutton"][2], "      └─ .bubble-sub-button-container  (position:sticky; top:0)"),
        (P["subbutton"][2], "          └─ [sub-button groups / .bubble-sub-button ×N]"),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 270 + i * 18, text, color)

    out += svg_close()
    return out


def diagram_calendar():
    W, H = 680, 680
    out = svg_open(W, H, "Calendar Card Layout")
    out += section_title(40, 32, "Calendar card", "(card_type: calendar — withBaseElements:false)")

    # Card mockup
    out += R(40, 44, 580, 220, P["card_fill"], P["card_stroke"], rx=12, sw=0.5)
    out += T(52, 62, ".bubble-calendar-container  (height = var(--bubble-calendar-height, rows×56px))", size=10, fill="#555")

    # Calendar content + scrollable area
    _, stroke, text_c = P["event"]
    out += R(52, 70, 490, 184, P["event"][0], stroke, rx=6, sw=0.5)
    out += T(297, 86, ".bubble-calendar-content  [.can-scroll-top]  [.can-scroll-bottom]  (overflow:scroll)", size=10, fill=text_c, anchor="middle")

    # Day wrapper + chip
    out += R(60, 96, 470, 146, P["note"][0], P["note"][1], rx=4)
    out += T(295, 112, ".bubble-day-wrapper  (+ ::before for separator line between days)", size=10, fill="#555", anchor="middle")

    out += R(68, 118, 46, 46, P["icon"][0], P["icon"][1], rx=23, sw=0.5)
    out += T(91, 134, ".bubble-day-chip", size=9, fill=P["icon"][2], anchor="middle")
    out += T(91, 146, "[.is-active]", size=9, fill="#639922", anchor="middle")
    out += T(91, 158, "(today)", size=9, fill="#888", anchor="middle")

    # Events
    out += R(122, 118, 398, 118, P["event"][0], stroke, rx=4, sw=0.5)
    out += T(321, 134, ".bubble-day-events", size=10, fill=text_c, anchor="middle")
    for i in range(3):
        out += R(130, 142 + i * 28, 382, 22, P["note"][0], P["note"][1], rx=3)
        if i < 2:
            out += R(136, 146 + i * 28, 50, 14, "#e1f5ee", "#1d9e75", rx=2)
            out += T(161, 156 + i * 28, ".event-time", size=8, fill="#0f6e56", anchor="middle")
            out += R(192, 146 + i * 28, 16, 14, P["event"][0], stroke, rx=7)
            out += R(214, 146 + i * 28, 290, 14, P["dyn"][0], P["dyn"][1], rx=2)
            out += T(359, 156 + i * 28, ".bubble-event-name  +  .bubble-event-place", size=8, fill=P["dyn"][1], anchor="middle")
        else:
            out += T(321, 156 + i * 28, "(.bubble-event rows continue...)", size=8, fill="#888", anchor="middle")

    # Sub-button sticky
    out += R(550, 70, 60, 184, P["subbutton"][0], P["subbutton"][1], rx=6, sw=0.5)
    out += T(580, 130, ".bubble-sub-", size=9, fill=P["subbutton"][2], anchor="middle")
    out += T(580, 143, "button-", size=9, fill=P["subbutton"][2], anchor="middle")
    out += T(580, 156, "container", size=9, fill=P["subbutton"][2], anchor="middle")
    out += T(580, 170, "(sticky)", size=9, fill="#639922", anchor="middle")
    out += T(580, 183, "top:0", size=9, fill="#639922", anchor="middle")

    out += divider(282, w=598)

    # Element classes
    out += T(40, 308, "Event element classes", size=13, weight="500", fill="#1a1a1a")
    classes = [
        (".bubble-day-wrapper",     "flex row containing day chip + day events"),
        (".bubble-day-chip",        "42×42px circle; .is-active added for today"),
        (".bubble-day-number",      "large date number  (e.g. 29)"),
        (".bubble-day-month",       "short month label  (e.g. Apr)"),
        (".bubble-day-events",      "column of .bubble-event rows"),
        (".bubble-event",           "single event row — time · color-dot · name · place"),
        (".bubble-event-time",      "formatted start time or 'All day'"),
        (".bubble-event-color",     "12×12px colored circle dot"),
        (".bubble-event-name",      "event title (truncated, font-weight:600)"),
        (".bubble-event-place",     "location text + icon (optional)"),
    ]
    for i, (cls, desc) in enumerate(classes):
        col = i % 2
        row = i // 2
        cx = 40 + col * 300
        cy = 326 + row * 18
        out += T(cx, cy, cls, size=11, fill=P["event"][2])
        out += T(cx + 170, cy, f"— {desc}", size=10, fill="#555")

    out += divider(432, w=598)

    # CSS variables
    out += T(40, 458, "Key CSS variables", size=13, weight="500", fill="#1a1a1a")
    vars_ = [
        ("--bubble-calendar-height",      "card height (set by JS: rows × 56px)"),
        ("--bubble-calendar-mask-size",   "scroll fade height (default 16px)"),
        ("--bubble-calendar-border-radius","event + chip corner radius"),
        ("--bubble-event-background-color", "event row background"),
        ("--bubble-button-icon-background-color", "day chip background"),
    ]
    for i, (var, desc) in enumerate(vars_):
        out += T(40, 476 + i * 16, var, size=10, fill=P["event"][2])
        out += T(290, 476 + i * 16, f"— {desc}", size=10, fill="#555")

    out += svg_close()
    return out


def diagram_popup():
    W, H = 680, 780
    out = svg_open(W, H, "Pop-up Card Layout")
    out += section_title(40, 32, "Pop-up card", "(card_type: pop-up — unique structure; modifies #root of vertical-stack)")

    # Backdrop
    _, stroke, text_c = P["backdrop"]
    out += R(40, 48, 580, 70, P["backdrop"][0], stroke, rx=8, sw=1)
    out += T(50, 64, "document.body  (global singleton)", size=11, weight="500", fill=text_c)
    out += R(50, 72, 560, 38, P["note"][0], P["note"][1], rx=4)
    out += T(60, 86, "div.bubble-backdrop-host  (shadow DOM host) → .bubble-backdrop  .backdrop", size=10, fill=text_c)
    out += T(60, 100, "[.is-hidden | .is-visible]  [.has-blur]  — style via CSS vars, NOT direct selectors", size=10, fill="#888")

    out += R(40, 126, 580, 16, "#fff8e6", "#c8a020", rx=3)
    out += T(50, 137, "Backdrop is shadow DOM — use --bubble-backdrop-background-color and --bubble-backdrop-filter CSS variables",
             size=10, fill="#7a6010")

    # Pop-up panel
    out += R(40, 152, 580, 300, P["card_fill"], P["card_stroke"], rx=12, sw=0.5)
    out += T(50, 170, "#root  →  .bubble-pop-up  .pop-up", size=12, weight="500", fill=P["wrapper"][2])
    out += T(50, 184, "[.is-popup-closed | .is-popup-opened | .is-opening | .is-closing]  [.no-header]  [.large]", size=10, fill="#888")

    out += R(52, 192, 556, 24, P["background"][0], P["background"][1], rx=4, sw=0.5)
    out += T(330, 208, ".bubble-pop-up-background  (the visible panel surface; rounded top corners)", size=10, fill=P["background"][2], anchor="middle")

    # Header
    out += R(52, 224, 556, 90, P["name"][0], P["name"][1], rx=6, sw=0.5)
    out += T(330, 240, ".bubble-header-container  [.is-unavailable]", size=10, fill=P["name"][2], anchor="middle")
    out += R(60, 252, 280, 52, P["icon"][0], P["icon"][1], rx=4, sw=0.5)
    out += T(200, 268, ".bubble-header", size=10, fill=P["icon"][2], anchor="middle")
    out += T(200, 282, "(entity button renders here as", size=9, fill="#888", anchor="middle")
    out += T(200, 294, "full bubble-button DOM)", size=9, fill="#888", anchor="middle")
    out += R(348, 252, 252, 52, P["subbutton"][0], P["subbutton"][1], rx=4, sw=0.5)
    out += T(474, 268, ".bubble-close-button  .close-pop-up", size=10, fill=P["subbutton"][2], anchor="middle")
    out += T(474, 282, "ha-icon.bubble-close-icon  +  ha-ripple", size=9, fill="#888", anchor="middle")

    # Content
    out += R(52, 322, 556, 120, P["state"][0], P["state"][1], rx=6, sw=0.5)
    out += T(330, 338, ".bubble-pop-up-container  (scrollable — child cards live here)", size=10, fill=P["state"][2], anchor="middle")
    out += T(330, 352, "gap: var(--bubble-pop-up-gap, 14px)", size=10, fill="#888", anchor="middle")
    for i in range(3):
        out += R(60 + i * 180, 360, 170, 70, P["note"][0], P["note"][1], rx=4)
        out += T(145 + i * 180, 400, f"[child card {i+1}]", size=10, fill="#888", anchor="middle")

    out += divider(470, w=598)

    # DOM tree
    out += T(40, 496, "DOM hierarchy", size=13, weight="500", fill="#1a1a1a")
    dom = [
        (P["backdrop"][2],  "document.body → div.bubble-backdrop-host (shadow DOM host)"),
        (P["backdrop"][2],  "   └─ (shadow root) → .bubble-backdrop .backdrop [.is-hidden/.is-visible] [.has-blur]"),
        ("#888", ""),
        (P["wrapper"][2],   "#root → .bubble-pop-up  .pop-up  [state classes]  [.no-header]  [.large]"),
        (P["background"][2],"    ├─ .bubble-pop-up-background  (panel surface)"),
        (P["name"][2],      "    ├─ .bubble-header-container  [.is-unavailable]"),
        (P["icon"][2],      "    │   ├─ .bubble-header  →  .bubble-button-container  (full button card DOM)"),
        (P["subbutton"][2], "    │   └─ .bubble-close-button  .close-pop-up  →  ha-icon.bubble-close-icon"),
        (P["state"][2],     "    └─ .bubble-pop-up-container  (scrollable; child cards rendered by HA)"),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 516 + i * 18, text, color)

    out += R(40, 690, 580, 40, "#fff5f5", "#f87171", rx=6, sw=0.5)
    out += T(50, 706, "Pop-up cards do NOT support module sub-buttons.", size=11, fill="#c0392b")
    out += T(50, 720, "The header entity button is a full bubble-button — its inner DOM can be targeted by button-scoped selectors.", size=11, fill="#c0392b")

    out += svg_close()
    return out


def diagram_hbs():
    W, H = 680, 680
    out = svg_open(W, H, "Horizontal Buttons Stack Layout")
    out += section_title(40, 32, "Horizontal Buttons Stack", "(card_type: horizontal-buttons-stack)")
    out += T(40, 50, "Fixed-position navigation bar. No sub-button support.", size=11, fill="#666")

    # ha-card
    out += R(40, 62, 580, 30, "#f1f5e8", "#9ab450", rx=8, sw=0.5)
    out += T(50, 80, "ha-card  .horizontal-buttons-stack-card  [.has-gradient]", size=10, fill="#3b6d11")
    out += T(460, 80, "position:fixed; bottom:16px; z-index:6", size=9, fill="#888")

    out += R(40, 96, 580, 12, "#e8fce8", "#639922", rx=3, sw=0.5, opacity=0.5)
    out += T(330, 105, "::before — gradient fade above bar (when .has-gradient)", size=9, fill="#3b6d11", anchor="middle")

    # card-content scroll wrapper
    out += R(40, 112, 580, 18, "#f1efe8", "#b4b2a9", rx=4, sw=0.5)
    out += T(330, 125, ".card-content  (HA scroll wrapper)  [.is-scrolled]  [.is-maxed-scroll]  — mask-image gradient fades edges",
             size=9, fill="#555", anchor="middle")

    # Container
    out += R(40, 134, 580, 130, "#e6f1fb", "#85b7eb", rx=6, sw=0.5)
    out += T(50, 150, ".bubble-horizontal-buttons-stack-card-container  .horizontal-buttons-stack-container", size=10, fill="#185fa5")

    # Buttons
    for i in range(4):
        bx = 48 + i * 142
        out += R(bx, 158, 130, 96, P["subbutton"][0], P["subbutton"][1], rx=6, sw=0.5)
        out += T(bx + 65, 172, f".bubble-button  .bubble-button-{i+1}", size=9, fill=P["subbutton"][2], anchor="middle")
        out += T(bx + 65, 184, f".button  .&lt;link-hash&gt;", size=9, fill="#888", anchor="middle")
        out += T(bx + 65, 196, "[.highlight when URL matches]", size=8, fill="#639922", anchor="middle")
        out += T(bx + 65, 208, "position:absolute", size=8, fill="#888", anchor="middle")
        out += T(bx + 65, 220, f"transform:translateX({i*142+10}px)", size=8, fill="#888", anchor="middle")
        out += R(bx + 4, 226, 56, 20, P["icon"][0], P["icon"][1], rx=3, sw=0.5)
        out += T(bx + 32, 239, "ha-icon.bubble-icon", size=7, fill=P["icon"][2], anchor="middle")
        out += R(bx + 66, 226, 56, 20, P["background"][0], P["background"][1], rx=3, sw=0.5)
        out += T(bx + 94, 239, ".bubble-background", size=7, fill=P["background"][2], anchor="middle")

    out += divider(284, w=598)

    # Positioning note
    out += R(40, 294, 580, 50, "#fff8e6", "#c8a020", rx=6, sw=0.5)
    out += T(50, 312, "Buttons use absolute positioning + transform:translateX, NOT flexbox/grid.", size=11, fill="#7a6010")
    out += T(50, 328, "placeButtons() measures offsetWidth, accumulates positions, caches widths in localStorage per link hash.", size=11, fill="#7a6010")

    out += divider(360, w=598)

    out += T(40, 386, "DOM hierarchy", size=13, weight="500", fill="#1a1a1a")
    dom = [
        ("#222", "ha-card  .horizontal-buttons-stack-card  [.has-gradient]"),
        ("#222", "  └─ .card-content  (HA scroll wrapper — .is-scrolled  .is-maxed-scroll)"),
        (P["buttons"][2], "      └─ .bubble-horizontal-buttons-stack-card-container"),
        (P["subbutton"][2], "          ├─ .bubble-button  .bubble-button-1  .button  .&lt;link-hash&gt;  [.highlight]"),
        (P["icon"][2],     "          │   ├─ ha-icon.bubble-icon  .icon"),
        (P["name"][2],     "          │   ├─ .bubble-name  .name"),
        (P["background"][2],"         │   ├─ .bubble-background-color  .background-color  (border + light tint)"),
        (P["background"][2],"         │   └─ .bubble-background  .background  (fill)"),
        (P["subbutton"][2], "          ├─ .bubble-button  .bubble-button-2  ..."),
        (P["subbutton"][2], "          └─ .bubble-button  .bubble-button-N  ..."),
    ]
    for i, (color, text) in enumerate(dom):
        out += dom_line(40, 406 + i * 18, text, color)

    out += R(40, 594, 580, 36, "#fff5f5", "#f87171", rx=6, sw=0.5)
    out += T(50, 610, "sub_button config is NOT supported on horizontal-buttons-stack cards.", size=11, fill="#c0392b")
    out += T(50, 624, "Target specific buttons by .bubble-button-1 (index) or .&lt;link-hash&gt; (e.g. .living-room from #living-room).",
             size=11, fill="#c0392b")

    out += svg_close()
    return out


def diagram_sub_buttons():
    W, H = 680, 820
    out = svg_open(W, H, "Sub-buttons System — v3.1+ Sectioned Schema")
    out += section_title(40, 32, "Sub-buttons — v3.1+ sectioned schema", "(button, media-player, climate, cover, select, separator, calendar)")

    # YAML example
    out += R(40, 48, 280, 200, "#f5f5f5", "#ccc", rx=6, sw=0.5)
    out += T(50, 64, "✅  Always use this schema:", size=11, weight="500", fill="#1a1a1a")
    yaml_lines = [
        ("sub_button:", "#1a1a1a"),
        ("  main_layout: inline", "#185fa5"),
        ("  bottom_layout: inline", "#185fa5"),
        ("  main:", "#1a1a1a"),
        ("    - entity: light.desk", "#0f6e56"),
        ("      name: Desk", "#0f6e56"),
        ("    - group:", "#854f0b"),
        ("        - entity: light.a", "#854f0b"),
        ("      buttons_layout: inline", "#854f0b"),
        ("  bottom:", "#1a1a1a"),
        ("    - entity: sensor.temp", "#7a1fad"),
        ("      justify_content: center", "#7a1fad"),
    ]
    for i, (txt, color) in enumerate(yaml_lines):
        out += T(50, 80 + i * 14, txt, size=10, fill=color, font=MONO)

    out += R(330, 48, 280, 200, "#fff5f5", "#f87171", rx=6, sw=0.5)
    out += T(340, 64, "❌  Legacy — do not use:", size=11, weight="500", fill="#c0392b")
    old_lines = [
        "sub_button:",
        "  - entity: light.desk",
        "    name: Desk",
        "  - entity: light.b",
        "    name: B",
    ]
    for i, txt in enumerate(old_lines):
        out += T(340, 80 + i * 14, txt, size=10, fill="#c0392b", font=MONO)
    out += T(340, 160, "Flat array lacks top/bottom", size=10, fill="#888")
    out += T(340, 174, "zones, groups, and alignment", size=10, fill="#888")
    out += T(340, 188, "lanes. Not supported in v3.1+.", size=10, fill="#888")

    out += divider(264, w=598)

    # DOM structure
    out += T(40, 290, "DOM structure produced by sectioned schema", size=13, weight="500", fill="#1a1a1a")

    # Wrapper box
    out += R(40, 304, 580, 350, P["card_fill"], P["card_stroke"], rx=8, sw=0.5)
    out += T(50, 320, ".bubble-wrapper  (card wrapper)", size=11, fill=P["wrapper"][2])

    # Base card area
    out += R(52, 328, 556, 30, P["note"][0], P["note"][1], rx=4)
    out += T(330, 346, "[base card content — icon, name, background, buttons]", size=10, fill="#555", anchor="middle")

    # Top container
    out += R(52, 368, 556, 100, P["subbutton"][0], P["subbutton"][1], rx=6, sw=0.5)
    out += T(60, 384, ".bubble-sub-button-container  [.groups-layout-inline | .groups-layout-rows]  [.fixed-top]", size=10, fill=P["subbutton"][2])

    # Explicit group
    out += R(60, 392, 260, 66, P["name"][0], P["name"][1], rx=4, sw=0.5)
    out += T(190, 408, ".bubble-sub-button-group  .position-top  .display-inline", size=9, fill=P["name"][2], anchor="middle")
    out += T(190, 422, "[data-group-id=g_main_0]  ← explicit group", size=9, fill="#888", anchor="middle")
    for i in range(3):
        out += R(66 + i * 82, 430, 72, 22, P["icon"][0], P["icon"][1], rx=3)
        out += T(102 + i * 82, 444, f".bubble-sub-button-{i+1}", size=8, fill=P["icon"][2], anchor="middle")

    # Auto group
    out += R(330, 392, 268, 66, P["state"][0], P["state"][1], rx=4, sw=0.5)
    out += T(464, 408, ".bubble-sub-button-group  .position-top", size=9, fill=P["state"][2], anchor="middle")
    out += T(464, 422, "[data-group-id=g_main_auto]  ← auto group", size=9, fill="#888", anchor="middle")
    out += R(338, 430, 120, 22, P["icon"][0], P["icon"][1], rx=3)
    out += T(398, 444, ".bubble-sub-button-4", size=8, fill=P["icon"][2], anchor="middle")

    # Bottom container
    out += R(52, 478, 556, 166, P["media"][0], P["media"][1], rx=6, sw=0.5)
    out += T(60, 494, ".bubble-sub-button-bottom-container  [.groups-layout-inline]  [.alignment-lanes-active]", size=10, fill=P["media"][2])

    lane_colors = [("#3b6d11", "#639922", "start  order:1"),
                   ("#185fa5", "#378add", "center  order:2"),
                   ("#854f0b", "#ba7517", "fill  order:3"),
                   ("#7a1fad", "#a855d8", "end  order:4")]
    for i, (text_c, stroke_c, label_txt) in enumerate(lane_colors):
        lx = 60 + i * 136
        out += R(lx, 502, 126, 128, "#fafafa", stroke_c, rx=4, sw=0.5)
        out += T(lx + 63, 518, f".lane-{label_txt.split()[0]}", size=9, fill=text_c, anchor="middle")
        out += T(lx + 63, 530, f"({label_txt.split()[1]})", size=9, fill="#888", anchor="middle")
        out += R(lx + 4, 538, 118, 36, P["note"][0], P["note"][1], rx=3)
        out += T(lx + 63, 552, ".bubble-sub-button-group", size=8, fill=text_c, anchor="middle")
        out += T(lx + 63, 564, f".alignment-{label_txt.split()[0]}", size=8, fill=text_c, anchor="middle")
        out += R(lx + 4, 580, 118, 40, P["dyn"][0], P["dyn"][1], rx=3)
        out += T(lx + 63, 600, ".bubble-sub-button ×N", size=8, fill=P["dyn"][1], anchor="middle")
        out += T(lx + 63, 614, ".&lt;name-class&gt;", size=8, fill="#888", anchor="middle")

    out += divider(668, w=598)

    out += T(40, 690, "Auto-grouping rules:", size=12, weight="500", fill="#1a1a1a")
    rules = [
        "main non-group items → g_main_auto when main_layout:rows, or when explicit groups exist, or when any bottom items exist",
        "bottom non-group items → g_bottom_auto (all together) unless mixed with explicit bottom groups",
        "mixed bottom case → each non-group item gets its own g_bottom_individual_N group to preserve YAML order",
    ]
    for i, r in enumerate(rules):
        out += T(50, 708 + i * 16, f"• {r}", size=10, fill="#333")

    out += R(40, 760, 580, 32, "#e1f5ee", "#1d9e75", rx=6, sw=0.5)
    out += T(50, 775, "justify_content values:  fill (default) → .alignment-fill  |  start → .alignment-start  |  center → .alignment-center  |  end → .alignment-end",
             size=10, fill="#0f6e56")
    out += T(50, 789, "space-between / space-around / space-evenly / stretch → .alignment-fill   (all map to fill)",
             size=10, fill="#888")

    out += svg_close()
    return out


# ── Registry and runner ───────────────────────────────────────────────────────

DIAGRAMS = {
    "button":                   ("button-card-layout.svg",          diagram_button),
    "media-player":             ("media-player-layout.svg",         diagram_media_player),
    "climate":                  ("climate-card-layout.svg",         diagram_climate),
    "cover":                    ("cover-card-layout.svg",           diagram_cover),
    "select":                   ("select-card-layout.svg",          diagram_select),
    "separator":                ("separator-card-layout.svg",       diagram_separator),
    "calendar":                 ("calendar-card-layout.svg",        diagram_calendar),
    "pop-up":                   ("pop-up-layout.svg",               diagram_popup),
    "horizontal-buttons-stack": ("hbs-layout.svg",                  diagram_hbs),
    "sub-buttons":              ("sub-buttons-layout.svg",          diagram_sub_buttons),
}


def build(card_key):
    filename, fn = DIAGRAMS[card_key]
    svg = fn()
    out_path = OUTPUT_DIR / filename
    out_path.write_text(svg, encoding="utf-8")
    print(f"  ✓  {filename}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate Bubble Card layout SVG diagrams.")
    parser.add_argument("--card", help="Only build one card type (use name from --list)")
    parser.add_argument("--list", action="store_true", help="List available card keys")
    args = parser.parse_args()

    if args.list:
        for k in DIAGRAMS:
            print(f"  {k}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.card:
        if args.card not in DIAGRAMS:
            print(f"Unknown card: {args.card}.  Use --list to see valid names.", file=sys.stderr)
            sys.exit(1)
        build(args.card)
    else:
        print(f"Generating {len(DIAGRAMS)} diagrams → {OUTPUT_DIR}")
        for key in DIAGRAMS:
            build(key)
        print("Done.")


if __name__ == "__main__":
    main()
