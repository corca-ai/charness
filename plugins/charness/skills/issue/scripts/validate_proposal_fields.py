#!/usr/bin/env python3
"""Presence-only validator for retro-derived issue-proposal fields.

Checks that a proposal block carries non-empty `Structural pattern:`,
`Triggering instance(s):`, and `Destination:` fields, and that `Destination:`
is one of the allowed values. This is presence/enum only by design: a
present-but-vague pattern passes; only a missing field or an out-of-enum
destination fails. It never judges whether the generalization is good — that is
the reviewer's job, mirroring the achieve disposition floor. See
../../shared/references/retro-issue-destination-split.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("Structural pattern", "Triggering instance(s)", "Destination")
DESTINATION_VALUES = ("upstream-harness", "repo-local", "both")


def _field_value(text: str, label: str) -> str | None:
    """Return the inline value for a `Label:` field, tolerant of markdown markers.

    Matches lines like `Structural pattern: <value>`, `- Destination: both`, or
    `**Structural pattern:** <value>`. Returns the stripped value, or None when
    the field is absent or has an empty value.
    """
    pattern = re.compile(
        r"^[\s\-\*#>]*\**\s*" + re.escape(label) + r"\**\s*:\s*(?P<value>.*)$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        return None
    value = match.group("value").strip().strip("*").strip()
    return value or None


def evaluate_proposal_fields(text: str) -> dict[str, Any]:
    present: dict[str, str] = {}
    missing: list[str] = []
    errors: list[str] = []
    for label in REQUIRED_FIELDS:
        value = _field_value(text, label)
        if value:
            present[label] = value
        else:
            missing.append(label)
    destination = present.get("Destination")
    if destination is not None and destination.lower() not in DESTINATION_VALUES:
        errors.append("Destination must be one of: " + ", ".join(DESTINATION_VALUES))
    ok = not missing and not errors
    return {
        "ok": ok,
        "present": present,
        "missing": missing,
        "destination": destination,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Path to the proposal block; reads stdin when omitted",
    )
    args = parser.parse_args()
    if args.file is not None:
        text = args.file.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    report = evaluate_proposal_fields(text)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
