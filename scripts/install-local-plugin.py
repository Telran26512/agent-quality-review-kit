#!/usr/bin/env python3
"""Install this repository as a local Codex plugin marketplace entry.

The expected local plugin location is:

  ~/plugins/agent-quality-review

Codex local marketplace metadata is written to:

  ~/.agents/plugins/marketplace.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


PLUGIN_NAME = "agent-quality-review"
MARKETPLACE_NAME = "local-codex-plugins"
MARKETPLACE_DISPLAY_NAME = "Local Codex Plugins"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_home() -> Path:
    return Path(os.environ.get("HOME", str(Path.home()))).expanduser()


def plugin_entry() -> dict:
    return {
        "name": PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": f"./plugins/{PLUGIN_NAME}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Productivity",
    }


def load_marketplace(path: Path) -> dict:
    if not path.exists():
        return {
            "name": MARKETPLACE_NAME,
            "interface": {"displayName": MARKETPLACE_DISPLAY_NAME},
            "plugins": [],
        }

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")

    data.setdefault("name", MARKETPLACE_NAME)
    data.setdefault("interface", {"displayName": MARKETPLACE_DISPLAY_NAME})
    data.setdefault("plugins", [])

    if not isinstance(data["plugins"], list):
        raise ValueError(f"{path}: plugins must be an array")

    return data


def upsert_plugin(data: dict, entry: dict) -> bool:
    for index, existing in enumerate(data["plugins"]):
        if isinstance(existing, dict) and existing.get("name") == PLUGIN_NAME:
            changed = existing != entry
            data["plugins"][index] = entry
            return changed

    data["plugins"].append(entry)
    return True


def copy_plugin(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)

    def ignore(_: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in {".git", "__pycache__", ".pytest_cache"}
            or name.endswith(".pyc")
        }

    shutil.copytree(source, target, ignore=ignore)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Agent Quality Review as a local Codex plugin.")
    parser.add_argument("--home", type=Path, default=default_home(), help="Home directory that owns ~/.agents and ~/plugins.")
    parser.add_argument("--no-copy", action="store_true", help="Only update the local marketplace entry; do not copy plugin files.")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned actions without writing files.")
    args = parser.parse_args()

    home = args.home.expanduser().resolve()
    source = repo_root()
    target = home / "plugins" / PLUGIN_NAME
    marketplace_path = home / ".agents" / "plugins" / "marketplace.json"

    if not (source / ".codex-plugin" / "plugin.json").exists():
        print(f"error: {source} is missing .codex-plugin/plugin.json", file=sys.stderr)
        return 1

    print(f"source: {source}")
    print(f"target: {target}")
    print(f"marketplace: {marketplace_path}")

    if args.dry_run:
        print("dry-run: no files changed")
        return 0

    if not args.no_copy:
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            copy_plugin(source, target)
        else:
            print("copy skipped: source is already the local plugin target")

    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    data = load_marketplace(marketplace_path)
    changed = upsert_plugin(data, plugin_entry())

    with marketplace_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")

    if changed:
        print("marketplace entry installed")
    else:
        print("marketplace entry already up to date")

    print("restart Codex, then open /plugins and look for Agent Quality Review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
