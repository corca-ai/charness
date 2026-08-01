#!/usr/bin/env python3
"""Measure what the inventory-consumption floors cost this repo's real artifact corpus.

Two sweep rows meet in `validate_inventory_consumption.py`:

- **S9** — the artifact's own `Date:` line decided whether the floor ran at all, so
  backdating it turned six violations into exit 0. The repair corroborates that claim
  against git, a channel the artifact does not author.
- **S10** — "engagement" was `\\b<field>\\b` presence anywhere in the body, so an explicit
  negation plus five `n/a` stubs satisfied the contract. The repair requires a mention to
  carry a value beyond the field's own name.

Both are arming decisions, and this repo's rule is that a threshold is defended by a
number that can be re-run, not by a sentence. This script produces that number.

**What it does NOT license.** It measures THIS repo's checked-in quality artifacts. It
says nothing about a consumer repo's corpus, and it cannot: the artifacts a consumer
writes are not visible from here. It is evidence that arming costs this repo N, not
evidence that arming is free everywhere.

Exit codes: 0 clean, 1 the ≥N-declared-field floor drops a citation below its
requirement OR an artifact's pre-contract exemption is refused, 2 the corpus resolved to
no files (a clean result over an empty corpus is not a measurement).

**Scope, stated because the first version of this docstring overclaimed.** `scan()`
measures the declared-field count floor and the label-value floors. It does NOT run the
gate end to end, so exit 0 is not "no artifact is newly refused" — the recorded
`_provenance.baseline_check` covers that by comparing the whole corpus against HEAD's
validator, and that comparison is not reproducible from this script alone. The corpus
glob is non-recursive `*.md`, and any artifact reached via `--artifact-path` rather than
the default rolling pointer is outside it. Label residuals are collected corpus-wide,
while the gate applies the four label floors only when `inventory_skill_ergonomics.py` is
cited — so `label_value_residuals.below_floor` is an upper bound on cost, not a
gate-scoped count.

Two numbers cited in `docs/deferred-decisions.md` D47 are NOT produced here and were
measured by hand: 51 of 169 field mentions carry no value marker, and arming a
value-marker rule would refuse 5 checked-in reviews. They are one-off measurements; the
reopen trigger in D47 is where to re-derive them.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_inventory_consumption as gate  # noqa: E402

DEFAULT_CORPUS = "charness-artifacts/quality"


LABEL_FLOORS = {
    "Target boundary": "TARGET_BOUNDARY_RE",
    "Ambient repo findings": "AMBIENT_REPO_FINDINGS_RE",
    "prose review result": "PROSE_REVIEW_RESULT_RE",
    "structural review result": "STRUCTURAL_REVIEW_RESULT_RE",
}


def _label_residuals(body: str) -> list[dict[str, object]]:
    """Residuals of the four `Label:` VALUES — the half of S10 that changed from
    presence-only to value-bearing, and the half the first version of this script never
    measured while a comment cited its corpus minimum of 7."""
    rows: list[dict[str, object]] = []
    for label, attr in LABEL_FLOORS.items():
        pattern = getattr(gate, attr)
        for match in pattern.finditer(body):
            end = body.find("\n", match.end())
            value = body[match.end():] if end == -1 else body[match.end():end]
            rows.append({"label": label, "residual": gate.residual_chars(value, ""), "value": value.strip()[:60]})
    return rows


def _bodies(text: str) -> tuple[str, str]:
    sections = gate._split_sections(text)
    commands = sections.get(gate.COMMANDS_RUN_HEADER, "")
    body = "\n".join(
        block for header, block in sections.items() if header != gate.COMMANDS_RUN_HEADER
    )
    return commands, body


def scan(repo_root: Path, corpus: Path, fields_path: Path, floor: int | None = None) -> dict[str, object]:
    inventories = json.loads(fields_path.read_text(encoding="utf-8")).get("inventories", {})
    effective_floor = gate.MIN_ENGAGEMENT_RESIDUAL_CHARS if floor is None else floor
    rows: list[dict[str, object]] = []
    residuals: list[int] = []
    label_residuals: list[dict[str, object]] = []
    for path in sorted(corpus.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        commands, body = _bodies(text)
        declared = gate.ARTIFACT_DATE_RE.search(text)
        declared_date = declared.group(1) if declared else None
        state, committed = gate.commit_state(repo_root, path)
        claims_exemption = bool(declared_date) and declared_date < gate.ENFORCED_FROM_DATE.isoformat()
        label_residuals.extend(_label_residuals(body))
        row: dict[str, object] = {
            "path": gate._display_path(path, repo_root),
            "declared_date": declared_date,
            "last_commit_date": committed.isoformat() if committed else None,
            "claims_pre_contract_exemption": claims_exemption,
            "commit_state": state,
            "exemption": (
                "not-claimed" if not claims_exemption
                else "not-corroborated" if committed is None or state == "unavailable"
                else "corroborated" if committed < gate.ENFORCED_FROM_DATE
                else "REFUSED-uncorroborated"
            ),
            "citations": {},
        }
        for inventory in sorted(set(gate.INVENTORY_FILE_RE.findall(commands))):
            fields = (inventories.get(inventory) or {}).get("non_headline_fields") or []
            if not fields:
                continue
            others = tuple(fields)
            loose = [f for f in fields if re.search(rf"\b{re.escape(f)}\b", body)]
            strict = [
                f for f in fields
                if any(
                    re.search(rf"\b{re.escape(f)}\b", line)
                    and gate.residual_chars(line, f, tuple(x for x in others if x != f)) >= effective_floor
                    for line in body.splitlines()
                )
            ]
            for field in loose:
                for line in body.splitlines():
                    if re.search(rf"\b{re.escape(field)}\b", line):
                        residuals.append(
                            gate.residual_chars(line, field, tuple(x for x in others if x != field))
                        )
            row["citations"][inventory] = {
                "required": 2 if len(fields) >= 2 else 1,
                "engaged_presence_only": len(loose),
                "engaged_with_a_value": len(strict),
                "lost_to_the_floor": sorted(set(loose) - set(strict)),
            }
        rows.append(row)

    residuals.sort()
    label_values = sorted(int(r["residual"]) for r in label_residuals)
    return {
        "corpus": gate._display_path(corpus, repo_root),
        "artifacts": len(rows),
        "floor": effective_floor,
        "label_value_residuals": {
            "count": len(label_values),
            "min": label_values[0] if label_values else None,
            "median": label_values[len(label_values) // 2] if label_values else None,
            "below_floor": sum(1 for v in label_values if v < effective_floor),
        },
        "exemption_counts": {
            state: sum(1 for r in rows if r["exemption"] == state)
            for state in ("not-claimed", "corroborated", "not-corroborated", "REFUSED-uncorroborated")
        },
        "citations_lowered_below_requirement": [
            {"path": r["path"], "inventory": name, **stats}
            for r in rows for name, stats in r["citations"].items()
            if stats["engaged_presence_only"] >= stats["required"]
            and stats["engaged_with_a_value"] < stats["required"]
        ],
        "field_mention_residuals": {
            "count": len(residuals),
            "min": residuals[0] if residuals else None,
            "p5": residuals[len(residuals) // 20] if residuals else None,
            "median": residuals[len(residuals) // 2] if residuals else None,
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--corpus", type=Path, default=None, help=f"Default: {DEFAULT_CORPUS}")
    parser.add_argument("--consumer-fields-path", type=Path, default=None)
    parser.add_argument(
        "--floor", type=int, default=None,
        help="Override the gate's MIN_ENGAGEMENT_RESIDUAL_CHARS so a counterfactual floor "
             "can be re-run without editing the gate constant.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    corpus = (args.corpus or (repo_root / DEFAULT_CORPUS)).resolve()
    fields_path = (
        args.consumer_fields_path or (repo_root / gate.DEFAULT_CONSUMER_FIELDS_PATH)
    ).resolve()
    if not corpus.is_dir() or not any(corpus.glob("*.md")):
        print(
            f"no artifacts found under {corpus}; a clean result over an empty corpus is "
            "not a measurement.",
            file=sys.stderr,
        )
        return 2

    report = scan(repo_root, corpus, fields_path, args.floor)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f"{report['artifacts']} artifact(s) under {report['corpus']}; "
            f"engagement floor {report['floor']} chars."
        )
        print(f"  exemption states: {report['exemption_counts']}")
        print(f"  label-value residuals: {report['label_value_residuals']}")
        print(f"  field-mention residuals: {report['field_mention_residuals']}")
        lowered = report["citations_lowered_below_requirement"]
        print(f"  citations the floor drops below their requirement: {len(lowered)}")
        for entry in lowered:
            print(
                f"    {entry['path']} :: {entry['inventory']} "
                f"{entry['engaged_presence_only']}->{entry['engaged_with_a_value']} "
                f"(needs {entry['required']}); lost {entry['lost_to_the_floor']}"
            )
    return 1 if (
        report["citations_lowered_below_requirement"]
        or report["exemption_counts"]["REFUSED-uncorroborated"]
        or report["label_value_residuals"]["below_floor"]
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())
