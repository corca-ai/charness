#!/usr/bin/env python3

"""Hold declared consumption entries; do not require every inventory script.

`validate_inventory_consumption.py` refuses a Commands Run citation of an
undeclared inventory. That is the opt-in hole. This checker only validates
entries that are already in the declaration: they must exist on disk, carry
`non_headline_fields` (≥2 distinct) or an empty list plus `opt_out_reason`,
and must not name a missing script.

An undeclared `inventory_*.py` on disk is not a consumption-contract concern
until an artifact cites it.

Scope: skills/public/quality/scripts/inventory_*.py only. Inventory scripts
elsewhere in the repo are out of scope by design. See the `_scope` field of
the declaration JSON for the canonical contract.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_CONSUMER_FIELDS_PATH = "skills/public/quality/references/inventory-consumer-fields.json"
INVENTORY_DIR = "skills/public/quality/scripts"
INVENTORY_FILE_RE = re.compile(r"^inventory_[A-Za-z0-9_]+\.py$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--consumer-fields-path", type=Path, default=None)
    parser.add_argument("--inventory-dir", type=Path, default=None)
    return parser.parse_args()


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
    if not inventory_dir.is_dir():
        print(f"{inventory_dir}: not a directory", file=sys.stderr)
        return 1

    raw = json.loads(consumer_fields_path.read_text(encoding="utf-8"))
    declared: dict[str, dict] = raw.get("inventories", {})

    on_disk = sorted(
        path.name
        for path in inventory_dir.iterdir()
        if path.is_file() and INVENTORY_FILE_RE.match(path.name)
    )
    failures: list[str] = []

    extra = [name for name in declared if name not in set(on_disk)]
    if extra:
        relative = consumer_fields_path.relative_to(repo_root)
        failures.append(
            f"{relative} declares inventory script(s) that no longer exist on disk: "
            f"{', '.join(extra)}. Remove the entry or restore the script."
        )

    for name, entry in sorted(declared.items()):
        if name not in set(on_disk):
            continue
        fields = entry.get("non_headline_fields")
        if not isinstance(fields, list):
            failures.append(f"`{name}`: non_headline_fields must be a list.")
            continue
        opt_out_reason = entry.get("opt_out_reason", "")
        if len(fields) == 0:
            if not isinstance(opt_out_reason, str) or not opt_out_reason.strip():
                failures.append(
                    f"`{name}`: empty non_headline_fields requires a non-empty "
                    "`opt_out_reason` string."
                )
            continue
        if len(set(fields)) < 2:
            failures.append(
                f"`{name}`: declared non_headline_fields must have ≥2 distinct entries "
                "(or opt out with non_headline_fields: [] + opt_out_reason)."
            )
        if opt_out_reason:
            failures.append(
                f"`{name}`: opt_out_reason is set but non_headline_fields is non-empty; "
                "remove one of them."
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    with_fields = sum(1 for entry in declared.values() if entry.get("non_headline_fields"))
    opted_out = sum(1 for entry in declared.values() if not entry.get("non_headline_fields"))
    undeclared = len(on_disk) - len(declared)
    print(
        f"Validated {len(declared)} consumption declaration(s) "
        f"({with_fields} with fields, {opted_out} opted out); "
        f"{undeclared} undeclared inventory script(s) are not in the consumption contract."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
