#!/usr/bin/env python3
"""
Manage Android TV app IDs for the media_app_background module.

READ-ONLY commands (no network):
  --list                         List all services and packages from app_ids.yaml
  --check-module                 Cross-check app_ids.yaml packages against the module's APPS/SKIP keys

READ-ONLY commands (network):
  --verify-store [svc]           Verify package names exist on the Google Play Store

WRITE commands (edit app_ids.yaml in place):
  --add-service <id>             Scaffold a new service entry interactively
  --add-package <svc> <pkg>      Append a new package variant to an existing service
  --mark-delisted <svc> <pkg>    Comment-out a package that has been removed from the Play Store

Usage examples:
  python3 scripts/manage_appids.py --list
  python3 scripts/manage_appids.py --check-module
  python3 scripts/manage_appids.py --verify-store
  python3 scripts/manage_appids.py --verify-store max
  python3 scripts/manage_appids.py --add-service paramountplus
  python3 scripts/manage_appids.py --add-package max com.wbd.stream.tv
  python3 scripts/manage_appids.py --mark-delisted max com.hbo.hbonow

No third-party dependencies — uses only the Python standard library.
Non-zero exit code if any check or write operation fails.
"""

import sys
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT     = Path(__file__).resolve().parent.parent
APP_IDS_FILE  = REPO_ROOT / "device_state_media_appids" / "app_ids.yaml"
MODULE_FILE   = REPO_ROOT / "media_app_background.yaml"
PLAY_URL      = "https://play.google.com/store/apps/details?id={package}&hl=en_US"
REQUEST_DELAY = 1.0  # seconds between requests — be polite

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ── Parsers ───────────────────────────────────────────────────────────────────

def load_app_ids():
    """
    Parse app_ids.yaml (stdlib only).
    Returns dict: { service_id: { packages: [...], keys: [...], friendly_keys: [...], skip: bool } }
    """
    services = {}
    current = None
    section = None  # 'packages' | 'keys' | 'friendly_keys' | None

    with open(APP_IDS_FILE) as f:
        for line in f:
            s = line.rstrip()

            if re.match(r'^[a-z][a-z0-9_]+:\s*$', s):
                current = s.rstrip(':').strip()
                services[current] = {"packages": [], "keys": [], "friendly_keys": [], "skip": False}
                section = None
                continue

            if current is None:
                continue

            if re.match(r'^\s{2}packages:\s*$', s):
                section = 'packages'
                continue
            if re.match(r'^\s{2}keys:\s*$', s):
                section = 'keys'
                continue
            if re.match(r'^\s{2}friendly_keys:\s*$', s):
                section = 'friendly_keys'
                continue
            if re.match(r'^\s{2}skip:\s*true\s*$', s):
                services[current]['skip'] = True
                continue
            if re.match(r'^\s{2}[a-z]', s) and not s.strip().startswith('-'):
                section = None
                continue

            if section in ('packages', 'keys', 'friendly_keys'):
                m = re.match(r'^\s{4}-\s+([\w.\-]+)', s)
                if m:
                    services[current][section].append(m.group(1))

    return services


def load_module_keys():
    """
    Parse APPS and SKIP arrays out of media_app_background.yaml.
    Returns:
      apps:      dict { service_id: [key, ...] }
      skip_keys: list of raw key strings from the SKIP array
    """
    text = MODULE_FILE.read_text()

    skip_keys = []
    skip_m = re.search(r'const SKIP\s*=\s*\[(.*?)\];', text, re.DOTALL)
    if skip_m:
        skip_keys = re.findall(r"'([^']+)'", skip_m.group(1))

    apps = {}
    for entry in re.finditer(r"\{\s*keys:\s*\[([^\]]+)\][^}]*id:\s*'([^']+)'", text):
        keys = re.findall(r"'([^']+)'", entry.group(1))
        svc_id = entry.group(2)
        apps[svc_id] = keys

    return apps, skip_keys


# ── Read-only commands ────────────────────────────────────────────────────────

def cmd_list(services):
    for svc, data in services.items():
        skip_tag = "  [SKIP]" if data['skip'] else ""
        print(f"{svc}:{skip_tag}")
        for pkg in data["packages"]:
            print(f"  {pkg}")


def cmd_check_module(services):
    """
    For every package in app_ids.yaml, confirm at least one key in the
    module's APPS or SKIP array matches it as a substring.
    Also flags keys in the module that match no known package (dead keys).
    """
    apps, skip_keys = load_module_keys()
    failures = []
    warnings = []

    print(f"\nChecking packages in app_ids.yaml against module APPS/SKIP keys...\n")
    print(f"  {'Service':<12} {'Package':<55} {'Matched by'}")
    print(f"  {'─'*12} {'─'*55} {'─'*30}")

    for svc, data in services.items():
        if data['skip']:
            active_keys = skip_keys
            array_label = 'SKIP'
        else:
            active_keys = apps.get(svc, [])
            array_label = 'APPS'

        if not active_keys:
            for pkg in data['packages']:
                print(f"  ❌ {svc:<12} {pkg:<55} (service not in module {array_label})")
                failures.append((svc, pkg, f"service '{svc}' missing from module {array_label}"))
            continue

        for pkg in data['packages']:
            matched = [k for k in active_keys if k in pkg]
            if matched:
                print(f"  ✅ {svc:<12} {pkg:<55} {matched}")
            else:
                print(f"  ❌ {svc:<12} {pkg:<55} no key matches — {array_label} keys: {active_keys}")
                failures.append((svc, pkg, f"no key in {array_label} matches"))

    print(f"\nChecking for dead keys (module keys matching no package in app_ids.yaml)...\n")
    all_packages = [pkg for data in services.values() for pkg in data['packages']]
    all_friendly = {k for data in services.values() for k in data['friendly_keys']}

    for svc_id, keys in apps.items():
        for key in keys:
            if any(key in pkg for pkg in all_packages):
                continue
            if key in all_friendly:
                print(f"  ℹ  APPS[{svc_id}] key '{key}' — friendly key (matches app_name/source, not package name)")
                continue
            msg = f"APPS[{svc_id}] key '{key}' matches no package in app_ids.yaml"
            print(f"  ⚠  {msg}")
            warnings.append(msg)

    for key in skip_keys:
        if any(key in pkg for pkg in all_packages):
            continue
        if key in all_friendly:
            print(f"  ℹ  SKIP key '{key}' — friendly key (matches app_name/source, not package name)")
            continue
        msg = f"SKIP key '{key}' matches no package in app_ids.yaml"
        print(f"  ⚠  {msg}")
        warnings.append(msg)

    if not warnings:
        print(f"  No unexpected dead keys ✅")

    print(f"\n{'─'*60}")
    if failures:
        print(f"\n⚠  {len(failures)} package(s) unmatched by module:")
        for svc, pkg, reason in failures:
            print(f"   {svc}: {pkg}  ({reason})")
        return 1
    else:
        print(f"\nAll packages matched by module keys ✅")
        return 0


def cmd_verify_store(services, filter_key=None):
    """Verify package names against the Google Play Store (network required)."""
    items = (
        [(filter_key, services[filter_key])] if filter_key
        else list(services.items())
    )
    failures = []

    for svc, data in items:
        print(f"\n{'─'*60}")
        print(f"Service: {svc}")
        for i, pkg in enumerate(data["packages"]):
            if i > 0:
                time.sleep(REQUEST_DELAY)
            ok, title, code = _fetch_play_store(pkg)
            if ok:
                print(f"  ✅ {pkg}")
                print(f"        → \"{title}\"")
            else:
                print(f"  ❌ {pkg}  (HTTP {code})")
                failures.append((svc, pkg, code))
            time.sleep(REQUEST_DELAY)

    print(f"\n{'─'*60}")
    if failures:
        print(f"\n⚠  {len(failures)} package(s) failed:")
        for svc, pkg, code in failures:
            print(f"   {svc}: {pkg}  (HTTP {code})")
        return 1
    else:
        print(f"\nAll packages verified ✅")
        return 0


def _fetch_play_store(package):
    """Returns (ok, title, status_code)."""
    url = PLAY_URL.format(package=package)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            m = re.search(r'<title>([^<]+)</title>', html)
            title = m.group(1).strip() if m else "(title not found)"
            title = re.sub(r'\s*-\s*Apps on Google Play$', '', title)
            return True, title, resp.status
    except urllib.error.HTTPError as e:
        return False, "", e.code
    except Exception as e:
        return False, str(e), 0


# ── Write commands ────────────────────────────────────────────────────────────

def cmd_add_service(service_id):
    """
    Scaffold a new service entry in app_ids.yaml interactively.
    Prompts for package name(s), matching keys, and whether it's a SKIP entry.
    Appends the new block before the final blank line at end of file.
    """
    services = load_app_ids()
    if service_id in services:
        print(f"Error: '{service_id}' already exists in app_ids.yaml.")
        sys.exit(1)

    if not re.match(r'^[a-z][a-z0-9_]+$', service_id):
        print(f"Error: service ID must be lowercase letters/digits/underscores, got '{service_id}'.")
        sys.exit(1)

    print(f"\nAdding new service: {service_id}")
    print("Enter values below. Press Enter to leave optional fields blank.\n")

    # Packages
    packages = []
    print("Package name(s) — one per line, blank line to finish:")
    while True:
        pkg = input("  package: ").strip()
        if not pkg:
            break
        comment = input(f"  comment for '{pkg}' (optional): ").strip()
        packages.append((pkg, comment))
    if not packages:
        print("Error: at least one package is required.")
        sys.exit(1)

    # Skip?
    is_skip = input("\nIs this a SKIP entry (module returns '' immediately)? [y/N]: ").strip().lower() == 'y'

    # Keys (only if not skip)
    keys = []
    friendly_keys = []
    if not is_skip:
        print("\nMatching keys (substrings matched against package names) — blank line to finish:")
        while True:
            k = input("  key: ").strip()
            if not k:
                break
            keys.append(k)

        print("\nFriendly keys (match app_name/source values, not package names) — blank line to finish:")
        while True:
            k = input("  friendly_key: ").strip()
            if not k:
                break
            friendly_keys.append(k)
    else:
        print("\nSKIP key (substring matched against app_id to trigger skip):")
        k = input("  skip key: ").strip()
        if k:
            keys.append(k)

    # Notes
    notes = input("\nNotes (one line, optional): ").strip()

    # Build the YAML block
    lines = [f"\n{service_id}:"]
    lines.append("  packages:")
    for pkg, comment in packages:
        if comment:
            lines.append(f"    - {pkg}  # {comment}")
        else:
            lines.append(f"    - {pkg}")

    if is_skip:
        lines.append("  skip: true")

    if keys:
        lines.append("  keys:")
        for k in keys:
            lines.append(f"    - {k}")

    if friendly_keys:
        lines.append("  friendly_keys:")
        for k in friendly_keys:
            lines.append(f"    - {k}")

    if notes:
        lines.append(f"  notes: >")
        lines.append(f"    {notes}")

    block = "\n".join(lines) + "\n"

    # Append to file (ensure single trailing newline)
    content = APP_IDS_FILE.read_text()
    content = content.rstrip("\n") + "\n" + block
    APP_IDS_FILE.write_text(content)

    print(f"\n✅ Added '{service_id}' to {APP_IDS_FILE.name}.")
    print(f"   Next: wire up APPS/SKIP in media_app_background.yaml, then run --check-module.")


def cmd_add_package(service_id, package):
    """
    Append a new package variant to an existing service's packages list.
    Inserts after the last existing package line for that service.
    """
    services = load_app_ids()
    if service_id not in services:
        print(f"Error: '{service_id}' not found in app_ids.yaml. Known: {', '.join(services)}")
        sys.exit(1)

    if package in services[service_id]['packages']:
        print(f"'{package}' is already listed under '{service_id}'.")
        sys.exit(0)

    comment = input(f"Comment for '{package}' (optional, e.g. 'Android TV leanback build'): ").strip()

    lines = APP_IDS_FILE.read_text().splitlines(keepends=True)
    new_line = f"    - {package}"
    if comment:
        new_line += f"  # {comment}"
    new_line += "\n"

    # Find the last package line for this service
    in_service = False
    in_packages = False
    last_pkg_idx = None

    for i, line in enumerate(lines):
        s = line.rstrip()
        if re.match(r'^[a-z][a-z0-9_]+:\s*$', s):
            svc = s.rstrip(':').strip()
            in_service = (svc == service_id)
            in_packages = False
            continue
        if not in_service:
            continue
        if re.match(r'^\s{2}packages:\s*$', s):
            in_packages = True
            continue
        if in_packages:
            if re.match(r'^\s{4}-\s+[\w.]+', s):
                last_pkg_idx = i
            elif re.match(r'^\s{2}[a-z]', s):
                in_packages = False

    if last_pkg_idx is None:
        print(f"Error: could not locate packages list for '{service_id}' in file.")
        sys.exit(1)

    lines.insert(last_pkg_idx + 1, new_line)
    APP_IDS_FILE.write_text("".join(lines))
    print(f"✅ Added '{package}' to '{service_id}' in {APP_IDS_FILE.name}.")
    print(f"   Next: update keys in media_app_background.yaml if needed, then run --check-module.")


def cmd_mark_delisted(service_id, package):
    """
    Comment-out an active package line for a service, noting it as delisted.
    Converts:  '    - com.foo.bar'
    To:        '    # com.foo.bar — delisted from Play Store'
    """
    services = load_app_ids()
    if service_id not in services:
        print(f"Error: '{service_id}' not found in app_ids.yaml. Known: {', '.join(services)}")
        sys.exit(1)

    if package not in services[service_id]['packages']:
        print(f"Error: '{package}' is not an active package under '{service_id}'.")
        print(f"  Active packages: {services[service_id]['packages']}")
        sys.exit(1)

    lines = APP_IDS_FILE.read_text().splitlines(keepends=True)
    target = re.compile(r'^(\s{4})-\s+' + re.escape(package) + r'(\s*.*)$')
    replaced = False

    for i, line in enumerate(lines):
        m = target.match(line.rstrip('\n'))
        if m:
            trailing = m.group(2).strip()
            # Preserve any existing inline comment
            if trailing.startswith('#'):
                note = trailing[1:].strip()
                new_line = f"    # {package} — delisted from Play Store; {note}\n"
            else:
                new_line = f"    # {package} — delisted from Play Store\n"
            lines[i] = new_line
            replaced = True
            break

    if not replaced:
        print(f"Error: could not find active package line for '{package}' in file.")
        sys.exit(1)

    APP_IDS_FILE.write_text("".join(lines))
    print(f"✅ Marked '{package}' as delisted under '{service_id}' in {APP_IDS_FILE.name}.")
    print(f"   Run --check-module to confirm no keys are now broken.")


# ── Entry point ───────────────────────────────────────────────────────────────

def usage():
    print(__doc__)
    sys.exit(1)


def _next_arg(args, idx, flag):
    """Return args[idx+1] if it exists and isn't a flag, else error."""
    if idx + 1 >= len(args) or args[idx + 1].startswith('--'):
        print(f"Error: {flag} requires an argument.")
        sys.exit(1)
    return args[idx + 1]


def main():
    args = sys.argv[1:]

    if not args or '--help' in args or '-h' in args:
        usage()

    if '--list' in args:
        cmd_list(load_app_ids())
        return

    if '--check-module' in args:
        sys.exit(cmd_check_module(load_app_ids()))

    if '--verify-store' in args:
        services = load_app_ids()
        idx = args.index('--verify-store')
        filter_key = None
        if idx + 1 < len(args) and not args[idx + 1].startswith('--'):
            filter_key = args[idx + 1]
            if filter_key not in services:
                print(f"Unknown service '{filter_key}'. Known: {', '.join(services)}")
                sys.exit(1)
        sys.exit(cmd_verify_store(services, filter_key))

    if '--add-service' in args:
        idx = args.index('--add-service')
        service_id = _next_arg(args, idx, '--add-service')
        cmd_add_service(service_id)
        return

    if '--add-package' in args:
        idx = args.index('--add-package')
        service_id = _next_arg(args, idx, '--add-package')
        if idx + 2 >= len(args) or args[idx + 2].startswith('--'):
            print("Error: --add-package requires two arguments: <service> <package>")
            sys.exit(1)
        package = args[idx + 2]
        cmd_add_package(service_id, package)
        return

    if '--mark-delisted' in args:
        idx = args.index('--mark-delisted')
        service_id = _next_arg(args, idx, '--mark-delisted')
        if idx + 2 >= len(args) or args[idx + 2].startswith('--'):
            print("Error: --mark-delisted requires two arguments: <service> <package>")
            sys.exit(1)
        package = args[idx + 2]
        cmd_mark_delisted(service_id, package)
        return

    usage()


if __name__ == "__main__":
    main()
