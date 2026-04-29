#!/usr/bin/env python3
"""
build_media_assets.py
=====================
Generates combined SVGs and regenerates base64 data URI strings for
media_app_background.yaml.

Reads from:
  device_state_media_images/<service>.svg          — gradient background
  device_state_media_images/<service>_logo.svg     — logo overlay (optional)

Writes:
  device_state_media_images/<service>_combined.svg — gradient + logo composite

Then prints updated BUILTIN and LOGOS blocks ready to paste into the YAML.

Usage:
  python3 scripts/build_media_assets.py
  python3 scripts/build_media_assets.py --verify            # check YAML sync only
  python3 scripts/build_media_assets.py --blur 2.0          # set logo blur (default 0)
  python3 scripts/build_media_assets.py --logo-height 80    # override logo height (px, default 90)
  python3 scripts/build_media_assets.py --logo-opacity 0.4  # override logo opacity (default 0.5)
  python3 scripts/build_media_assets.py --service prime     # only process one service
  python3 scripts/build_media_assets.py --service prime --blur 2.0  # preview one service with blur
"""

import argparse
import base64
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(REPO_ROOT, 'device_state_media_images')
YAML_PATH = os.path.join(REPO_ROOT, 'media_app_background.yaml')

# Defaults — can be overridden via CLI
DEFAULT_LOGO_HEIGHT_PX = 90
DEFAULT_LOGO_OPACITY = 0.5
DEFAULT_BLUR_STDDEV = 0.3   # subtle soft-glow; 0 = off; typical values: 0.3–1.0


def read_svg_path_data(svg_path):
    """Return the raw content of an SVG file as a string."""
    with open(svg_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def b64_encode_file(file_path):
    """Base64-encode a file with no line breaks."""
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def parse_viewbox(svg_text):
    """Return (min_x, min_y, width, height) from the viewBox attribute."""
    m = re.search(r'viewBox=["\']([^"\']+)["\']', svg_text)
    if not m:
        return (0, 0, 24, 24)
    parts = m.group(1).replace(',', ' ').split()
    return tuple(float(p) for p in parts)


def extract_inner_elements(svg_text):
    """Return everything between the outer <svg> tags as a string."""
    inner = re.sub(r'<\?xml[^>]*\?>', '', svg_text)
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.DOTALL)
    inner = re.sub(r'<svg[^>]*>', '', inner, count=1)
    inner = re.sub(r'</svg\s*>', '', inner)
    return inner.strip()


def make_combined_svg(gradient_path, logo_path, logo_height_px=DEFAULT_LOGO_HEIGHT_PX,
                      logo_opacity=DEFAULT_LOGO_OPACITY, blur_stddev=DEFAULT_BLUR_STDDEV):
    """
    Compose a 400x225 SVG: gradient background + logo overlay centered.

    logo_height_px  — logo display height on the 400x225 canvas
    logo_opacity    — opacity of the logo group (0.0–1.0)
    blur_stddev     — SVG feGaussianBlur stdDeviation; 0 disables the filter.
                      Good values: 1.0 (subtle), 2.0 (soft glow), 3.0+ (heavy blur).
    """
    grad_text = read_svg_path_data(gradient_path)
    logo_text = read_svg_path_data(logo_path)

    vb_min_x, vb_min_y, logo_w, logo_h = parse_viewbox(logo_text)

    scale = logo_height_px / logo_h
    scaled_w = logo_w * scale

    # Centre the scaled logo on the 400x225 canvas
    tx = (400 - scaled_w) / 2 - vb_min_x * scale
    ty = (225 - logo_height_px) / 2 - vb_min_y * scale

    grad_inner = extract_inner_elements(grad_text)
    logo_inner = extract_inner_elements(logo_text)

    lines = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 225">']
    lines.append(f'  {grad_inner}')

    if blur_stddev > 0:
        # feGaussianBlur in user-space units (post-scale); 'expand' region so the
        # blur doesn't clip at the logo bounding box edges.
        filter_id = 'logo_blur'
        lines.append(
            f'  <filter id="{filter_id}" x="-20%" y="-20%" width="140%" height="140%">'
        )
        lines.append(f'    <feGaussianBlur stdDeviation="{blur_stddev:.2f}"/>')
        lines.append('  </filter>')
        filter_attr = f' filter="url(#{filter_id})"'
    else:
        filter_attr = ''

    lines.append(
        f'  <g transform="translate({tx:.2f},{ty:.2f}) scale({scale:.4f})"'
        f' opacity="{logo_opacity:.2f}"{filter_attr}>'
    )
    lines.append(f'    {logo_inner}')
    lines.append('  </g>')
    lines.append('</svg>')
    lines.append('')  # trailing newline

    return '\n'.join(lines)


def list_services():
    """Return sorted list of service names (gradient files without suffix)."""
    return sorted(
        name[:-4]
        for name in os.listdir(IMG_DIR)
        if name.endswith('.svg') and '_logo' not in name and '_combined' not in name
    )


def build_combined_svgs(service_filter=None, logo_height_px=DEFAULT_LOGO_HEIGHT_PX,
                        logo_opacity=DEFAULT_LOGO_OPACITY, blur_stddev=DEFAULT_BLUR_STDDEV):
    """Generate <service>_combined.svg for every service that has both files."""
    services = list_services()
    if service_filter:
        services = [s for s in services if s == service_filter]
        if not services:
            raise ValueError(f'Service "{service_filter}" not found in {IMG_DIR}')

    generated = []
    skipped = []
    for svc in services:
        grad_path = os.path.join(IMG_DIR, f'{svc}.svg')
        logo_path = os.path.join(IMG_DIR, f'{svc}_logo.svg')
        out_path = os.path.join(IMG_DIR, f'{svc}_combined.svg')
        if not os.path.exists(logo_path):
            skipped.append(svc)
            continue
        combined = make_combined_svg(grad_path, logo_path, logo_height_px, logo_opacity, blur_stddev)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(combined)
        generated.append(svc)

    return generated, skipped


def print_yaml_blocks(service_filter=None):
    """Print BUILTIN and LOGOS base64 blocks ready to paste into the YAML."""
    services = list_services()
    if service_filter:
        services = [s for s in services if s == service_filter]

    print('  /* ── BUILTIN — paste into const BUILTIN = { ... } ── */')
    for svc in services:
        path = os.path.join(IMG_DIR, f'{svc}.svg')
        b64 = b64_encode_file(path)
        print(f"        {svc}: 'data:image/svg+xml;base64,{b64}',")

    print()
    print('  /* ── LOGOS — paste into const LOGOS = { ... } ── */')
    for svc in services:
        logo_path = os.path.join(IMG_DIR, f'{svc}_logo.svg')
        if not os.path.exists(logo_path):
            continue
        b64 = b64_encode_file(logo_path)
        print(f"        {svc}: 'data:image/svg+xml;base64,{b64}',")


def verify_yaml_sync():
    """Check that YAML base64 strings match the files on disk."""
    with open(YAML_PATH, encoding='utf-8') as f:
        yaml_content = f.read()

    all_ok = True
    for obj_name, suffix in [('BUILTIN', ''), ('LOGOS', '_logo')]:
        m = re.search(r'const ' + obj_name + r' = \{(.*?)\};', yaml_content, re.DOTALL)
        if not m:
            print(f'WARNING: {obj_name} block not found in YAML')
            continue
        entries = re.findall(r"(\w+):\s*'data:image/svg\+xml;base64,([^']+)'", m.group(1))
        for key, b64 in entries:
            path = os.path.join(IMG_DIR, key + suffix + '.svg')
            if not os.path.exists(path):
                print(f'MISSING FILE: {path}')
                all_ok = False
                continue
            file_b64 = b64_encode_file(path)
            if file_b64 == b64:
                print(f'OK:       {obj_name}/{key}')
            else:
                print(f'MISMATCH: {obj_name}/{key}')
                all_ok = False

    if all_ok:
        print('\nAll base64 strings are in sync.')
    else:
        print('\nSome mismatches found — run without --verify to regenerate combined SVGs and print updated YAML blocks.')
    return all_ok


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--verify', action='store_true',
        help='Check YAML sync only, do not write files',
    )
    parser.add_argument(
        '--service', metavar='NAME',
        help='Process only this service (e.g. prime, netflix). Useful for previews.',
    )
    parser.add_argument(
        '--blur', type=float, default=DEFAULT_BLUR_STDDEV, metavar='STDDEV',
        help=f'Gaussian blur stdDeviation applied to logos in combined SVGs '
             f'(default {DEFAULT_BLUR_STDDEV}; 0 = off; typical: 1–4)',
    )
    parser.add_argument(
        '--logo-height', type=float, default=DEFAULT_LOGO_HEIGHT_PX, metavar='PX',
        help=f'Logo height in px on the 400x225 canvas (default {DEFAULT_LOGO_HEIGHT_PX})',
    )
    parser.add_argument(
        '--logo-opacity', type=float, default=DEFAULT_LOGO_OPACITY, metavar='FLOAT',
        help=f'Logo group opacity 0.0–1.0 (default {DEFAULT_LOGO_OPACITY})',
    )
    args = parser.parse_args()

    if args.verify:
        verify_yaml_sync()
        return

    print('=== Building combined SVGs ===')
    if args.blur > 0:
        print(f'  Blur: feGaussianBlur stdDeviation={args.blur}')
    if args.logo_height != DEFAULT_LOGO_HEIGHT_PX:
        print(f'  Logo height: {args.logo_height}px')
    if args.logo_opacity != DEFAULT_LOGO_OPACITY:
        print(f'  Logo opacity: {args.logo_opacity}')

    generated, skipped = build_combined_svgs(
        service_filter=args.service,
        logo_height_px=args.logo_height,
        logo_opacity=args.logo_opacity,
        blur_stddev=args.blur,
    )
    for svc in generated:
        print(f'  Generated: {svc}_combined.svg')
    for svc in skipped:
        print(f'  Skipped (no logo): {svc}')

    if not args.service:
        print()
        print('=== Updated YAML base64 blocks ===')
        print_yaml_blocks()

        print()
        print('=== Verifying sync ===')
        verify_yaml_sync()


if __name__ == '__main__':
    main()
