#!/usr/bin/env python3

"""Check command strings in shipped JSON/YAML assets against the plugin layout."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_repo_file_listing = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_generated_mirror_files = _repo_file_listing.iter_generated_mirror_files
GeneratedMirrorAbsentError = _repo_file_listing.GeneratedMirrorAbsentError

ASSET_GLOBS = ("plugins/**/*.json", "plugins/**/*.yaml", "plugins/**/*.yml")
COMMAND_RE = re.compile(
    r"(?:python3?|bash|sh)"
    r"(?:\s+--?[A-Za-z0-9][A-Za-z0-9_-]*(?:=[A-Za-z0-9_.-]+)?)*"
    r"\s+[\"']?(?P<target>(?:\./)?skills/"
    r"(?:public|support)/[A-Za-z0-9._<>/-]+\.(?:py|sh))"
)


class AssetError(Exception):
    pass


def _walk_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in _walk_strings(child, f"{path}.{key}")]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in _walk_strings(child, f"{path}[{index}]")]
    return []


def _parse(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        if path.suffix == ".json":
            return json.loads(text)
        return yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise AssetError(f"{path}: cannot parse structured asset: {exc}") from exc


def _source_and_shipped(target: str) -> tuple[str, str]:
    source = target.removeprefix("./")
    for source_prefix, shipped_prefix in (
        ("skills/public/", "skills/"),
        ("skills/support/", "support/"),
    ):
        if source.startswith(source_prefix):
            return source, shipped_prefix + source.removeprefix(source_prefix)
    raise AssertionError(f"unsupported authoring target: {target}")


def scan_asset(root: Path, asset: Path) -> list[str]:
    payload = _parse(asset)
    relative = asset.relative_to(root)
    if len(relative.parts) < 3:
        return [
            f"{relative}: unsupported plugin asset layout; expected "
            "plugins/<package>/<asset>"
        ]
    package_root = root / relative.parts[0] / relative.parts[1]
    findings: list[str] = []
    for value_path, text in _walk_strings(payload):
        for match in COMMAND_RE.finditer(text):
            target = match.group("target")
            source, shipped = _source_and_shipped(target)
            if not (root / source).is_file():
                findings.append(
                    f"{relative}:{value_path}: `{target}` uses the authoring-only "
                    "kind-bearing layout; expected "
                    f"`<plugin-dir>/{shipped}` (authoring source missing)"
                )
                continue
            status = "exported" if (package_root / shipped).is_file() else "export missing"
            findings.append(
                f"{relative}:{value_path}: `{target}` uses the authoring-only kind-bearing "
                f"layout; expected `<plugin-dir>/{shipped}` ({status})"
            )
    return findings


def scan_assets(root: Path) -> tuple[int, list[str]]:
    findings: list[str] = []
    # NOT `iter_matching_repo_files`: `/plugins/` is gitignored, so that scope was
    # 0 of 58 shipped assets on a complete mirror. Raises rather than returning an
    # empty list when the mirror is absent -- see `iter_generated_mirror_files`.
    assets = iter_generated_mirror_files(root, ASSET_GLOBS)
    for asset in assets:
        try:
            findings.extend(scan_asset(root, asset))
        except AssetError as exc:
            findings.append(str(exc))
    return len(assets), findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    try:
        asset_count, findings = scan_assets(args.repo_root.resolve())
    except GeneratedMirrorAbsentError as exc:
        print(f"status: unestablished\n{exc}", file=sys.stderr)
        return 1
    if findings:
        print("Unreachable command carriers in shipped structured assets:", file=sys.stderr)
        print("\n".join(f"- {finding}" for finding in sorted(set(findings))), file=sys.stderr)
        return 1
    print(f"Validated {asset_count} shipped JSON/YAML asset(s); no authoring-layout command carriers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
