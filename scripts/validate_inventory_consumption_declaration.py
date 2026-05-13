#!/usr/bin/env python3

"""Fail when an inventory in skills/public/quality/references/inventory-consumer-fields.json
declares a non-headline field that is no longer present as a key in the
inventory script's actual `--json` output.

Closes the drift hole in the issue #145 v2 consumer contract: without this
check, a maintainer can rename or remove a field in the inventory script and
the consumer-side declaration silently goes stale, so
`validate_inventory_consumption.py` would either pass spuriously (declaration
still matches by accident) or fail with no clear root cause.

Only entries with `non_headline_fields` non-empty are executed; opted-out
entries (empty list + `opt_out_reason`) are skipped here — coverage is owned
by scripts/check_inventory_declaration_coverage.py.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DEFAULT_CONSUMER_FIELDS_PATH = "skills/public/quality/references/inventory-consumer-fields.json"
INVENTORY_DIR = "skills/public/quality/scripts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--consumer-fields-path", type=Path, default=None)
    parser.add_argument(
        "--inventory-dir",
        type=Path,
        default=None,
        help="Directory containing inventory_*.py scripts (defaults to skills/public/quality/scripts).",
    )
    return parser.parse_args()


def _collect_keys(node: object, sink: set[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str):
                sink.add(key)
            _collect_keys(value, sink)
    elif isinstance(node, list):
        for item in node:
            _collect_keys(item, sink)


def _run_inventory(script_path: Path, repo_root: Path) -> tuple[object | None, str | None]:
    try:
        completed = subprocess.run(
            [sys.executable, str(script_path), "--repo-root", str(repo_root), "--json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return None, "timed out after 120s"
    except Exception as exc:
        return None, f"unexpected {type(exc).__name__}: {exc}"
    if completed.returncode != 0:
        stderr = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else "(no stderr)"
        return None, f"exit {completed.returncode}: {stderr}"
    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"non-JSON stdout: {exc}"


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    consumer_fields_path = (
        args.consumer_fields_path or (repo_root / DEFAULT_CONSUMER_FIELDS_PATH)
    ).resolve()
    inventory_dir = (args.inventory_dir or (repo_root / INVENTORY_DIR)).resolve()

    if not consumer_fields_path.is_file():
        print(f"{consumer_fields_path}: not found", file=sys.stderr)
        return 1

    raw = json.loads(consumer_fields_path.read_text(encoding="utf-8"))
    inventories: dict[str, dict] = raw.get("inventories", {})

    targets: list[tuple[str, list[str], Path]] = []
    failures: list[str] = []
    for inventory_name, entry in sorted(inventories.items()):
        fields: list[str] = entry.get("non_headline_fields") or []
        if not fields:
            continue
        script_path = inventory_dir / inventory_name
        if not script_path.is_file():
            failures.append(
                f"declared inventory `{inventory_name}` has non-empty non_headline_fields "
                f"but the script file {script_path.relative_to(repo_root)} does not exist."
            )
            continue
        targets.append((inventory_name, fields, script_path))

    validated: list[str] = []
    if targets:
        with ThreadPoolExecutor(max_workers=min(8, len(targets))) as pool:
            results = list(
                pool.map(
                    lambda target: (target[0], target[1], _run_inventory(target[2], repo_root)),
                    targets,
                )
            )
        for inventory_name, fields, (data, error) in results:
            if error is not None:
                failures.append(
                    f"declared inventory `{inventory_name}` could not be executed for drift "
                    f"check ({error}); either fix the script's --json output or move the entry "
                    f"to `non_headline_fields: []` with an `opt_out_reason`."
                )
                continue
            keys: set[str] = set()
            _collect_keys(data, keys)
            missing = [field for field in fields if field not in keys]
            if missing:
                relative = consumer_fields_path.relative_to(repo_root)
                failures.append(
                    f"declared inventory `{inventory_name}` lists non_headline_field(s) "
                    f"{', '.join(repr(field) for field in missing)} that no longer appear as "
                    f"keys in the script's --json output; update {relative} or restore the "
                    f"field in the inventory script."
                )
            else:
                validated.append(inventory_name)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    if validated:
        print(
            f"Validated declared non_headline_fields drift-free across "
            f"{len(validated)} inventory script(s)."
        )
    else:
        print("No declared inventories with non-empty non_headline_fields; nothing to check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
