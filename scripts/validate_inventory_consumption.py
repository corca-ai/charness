#!/usr/bin/env python3

"""Fail when a quality inventory is cited in `## Commands Run` but the artifact body
does not engage with any of its declared non-headline review-state fields.

Issue #145 enriched several quality helpers with review-state fields beyond the
`status` / `heuristics` headline so consumers could form judgment. The
consumer-side contract did not yet exist: an artifact could cite the inventory
and still summarize only the headline. This validator closes that loop.

The contract only applies to artifacts dated on or after ENFORCED_FROM_DATE.
Earlier artifacts are frozen retros — rewriting them to fit a later gate would
be Goodhart's law (and the original reviewer never had this contract).

Contract source: skills/public/quality/references/inventory-consumer-fields.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

DEFAULT_ARTIFACT_PATH = "charness-artifacts/quality/latest.md"
DEFAULT_CONSUMER_FIELDS_PATH = "skills/public/quality/references/inventory-consumer-fields.json"
INVENTORY_FILE_RE = re.compile(r"inventory_[A-Za-z0-9_]+\.py")
COMMANDS_RUN_HEADER = "## Commands Run"
ARTIFACT_DATE_RE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
ENFORCED_FROM_DATE = date(2026, 5, 13)
SKILL_ERGONOMICS_INVENTORY = "inventory_skill_ergonomics.py"
PROSE_REVIEW_RESULT_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:prose[\s-]+review\s+result)\s*:",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact-path", type=Path, default=None)
    parser.add_argument("--consumer-fields-path", type=Path, default=None)
    return parser.parse_args()


def _split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"_preamble": []}
    current = "_preamble"
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            current = line.rstrip()
            sections.setdefault(current, [])
            continue
        sections[current].append(line)
    return {header: "\n".join(lines) for header, lines in sections.items()}


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    artifact_path = (args.artifact_path or (repo_root / DEFAULT_ARTIFACT_PATH)).resolve()
    consumer_fields_path = (
        args.consumer_fields_path or (repo_root / DEFAULT_CONSUMER_FIELDS_PATH)
    ).resolve()

    if not artifact_path.is_file():
        print(f"{artifact_path}: not found", file=sys.stderr)
        return 1
    if not consumer_fields_path.is_file():
        print(f"{consumer_fields_path}: not found", file=sys.stderr)
        return 1

    artifact_text = artifact_path.read_text(encoding="utf-8")
    match = ARTIFACT_DATE_RE.search(artifact_text)
    if match is not None:
        artifact_date = date.fromisoformat(match.group(1))
        if artifact_date < ENFORCED_FROM_DATE:
            print(
                f"Artifact {artifact_path.relative_to(repo_root)} dated {artifact_date.isoformat()} "
                f"predates contract start ({ENFORCED_FROM_DATE.isoformat()}); skipped."
            )
            return 0
    sections = _split_sections(artifact_text)
    commands_run = sections.get(COMMANDS_RUN_HEADER, "")
    body_without_commands = "\n".join(
        block for header, block in sections.items() if header != COMMANDS_RUN_HEADER
    )

    raw = json.loads(consumer_fields_path.read_text(encoding="utf-8"))
    inventories: dict[str, dict] = raw.get("inventories", {})

    cited = sorted(set(INVENTORY_FILE_RE.findall(commands_run)))
    failures: list[str] = []
    declared_consumed: list[str] = []

    for inventory in cited:
        entry = inventories.get(inventory)
        if entry is None:
            continue
        fields: list[str] = entry.get("non_headline_fields") or []
        if not fields:
            continue
        engaged = [
            field
            for field in fields
            if re.search(rf"\b{re.escape(field)}\b", body_without_commands)
        ]
        required = 2 if len(fields) >= 2 else 1
        if len(engaged) < required:
            relative = consumer_fields_path.relative_to(repo_root)
            failures.append(
                f"inventory `{inventory}` is cited in `{COMMANDS_RUN_HEADER}` but the artifact "
                f"body engages with {len(engaged)} of its declared non-headline fields "
                f"({', '.join(fields)}); contract requires ≥{required} distinct field(s). Cite "
                f"observations that use at least {required} of those fields, or remove the "
                f"citation if the inventory was not actually consumed. Declaration source: "
                f"{relative}."
            )
        else:
            declared_consumed.append(inventory)
        if inventory == SKILL_ERGONOMICS_INVENTORY:
            if not re.search(r"\bprose_review_status\b", body_without_commands):
                failures.append(
                    f"inventory `{inventory}` is cited in `{COMMANDS_RUN_HEADER}` but the artifact "
                    "body does not engage with `prose_review_status`; skill ergonomics inventory "
                    "output is not a prose-review result."
                )
            if not PROSE_REVIEW_RESULT_RE.search(body_without_commands):
                failures.append(
                    f"inventory `{inventory}` is cited in `{COMMANDS_RUN_HEADER}` but the artifact "
                    "body lacks an explicit `prose review result:` line outside the command log."
                )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    if declared_consumed:
        print(
            f"Validated inventory consumption for {len(declared_consumed)} declared inventory "
            f"citation(s) in {artifact_path.relative_to(repo_root)}."
        )
    else:
        print(f"No declared inventory citations found in {artifact_path.relative_to(repo_root)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
