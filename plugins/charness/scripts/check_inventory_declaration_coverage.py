#!/usr/bin/env python3

"""Fail when an inventory_*.py under skills/public/quality/scripts/ is not declared
in skills/public/quality/references/inventory-consumer-fields.json.

Closes the opt-in gap in the issue #145 v2 consumer contract: previously,
`validate_inventory_consumption.py` only enforced consumer engagement for
inventories explicitly listed in the JSON. A new inventory could ship without
ever appearing in the declaration, and the headline-only summary trap would
re-open silently. This validator forces a conscious choice for every inventory:
either declare non_headline_fields (≥2 distinct) or opt out with a
non-empty `opt_out_reason`.
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

    missing = [name for name in on_disk if name not in declared]
    if missing:
        relative = consumer_fields_path.relative_to(repo_root)
        failures.append(
            "inventory script(s) missing from "
            f"{relative}: {', '.join(missing)}. "
            "Add either `non_headline_fields: [<field>, ...]` (≥2 distinct fields) or "
            "`non_headline_fields: []` with a non-empty `opt_out_reason`."
        )

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

    print(
        f"Validated declaration coverage for {len(on_disk)} inventory script(s) "
        f"({sum(1 for n, e in declared.items() if e.get('non_headline_fields'))} declared, "
        f"{sum(1 for n, e in declared.items() if not e.get('non_headline_fields'))} opted out)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
