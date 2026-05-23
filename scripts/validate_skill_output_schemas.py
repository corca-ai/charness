#!/usr/bin/env python3
"""Advisory survey of caller-action `Output Shape` fields and their validators.

The Closeout Schema Rule
(`skills/public/create-skill/references/portable-authoring.md`) asks: when a
skill's `Output Shape` declares classifier fields the caller must act on, ship a
validator that fails when those fields are missing or free-form. Whether a given
field needs a validator is a semantic judgment, not a lexical one, so this
survey is ADVISORY: it reports skills whose output carries a recognized
classifier schema but names no matching validator, and always exits 0. Authors
use the report to decide; CI does not hard-fail on the heuristic.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

# Classifier fields the caller is expected to act on. A pipe-delimited schema
# bullet carrying one of these keys is the signal the rule targets; generic
# backtick lists and prose bullets are intentionally NOT flagged.
CLASSIFIER_KEYS = ("bin", "severity", "urgency", "decision", "evidence", "action")
_SCHEMA_BULLET_RE = re.compile(r"^\s*-\s+.*\|.*\b(" + "|".join(CLASSIFIER_KEYS) + r")\s*:", re.IGNORECASE)
_VALIDATOR_MENTION_RE = re.compile(r"validate_[a-z0-9_]+_(artifacts?|outputs?)\.py", re.IGNORECASE)
_VALIDATOR_SUFFIXES = ("_artifact", "_artifacts", "_output", "_outputs")


def public_skill_dirs(repo_root: Path) -> list[Path]:
    public = repo_root / "skills" / "public"
    if not public.is_dir():
        return []
    return sorted(p for p in public.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def _skill_text(skill_dir: Path) -> str:
    parts = [(skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="ignore")]
    references = skill_dir / "references"
    if references.is_dir():
        for path in sorted(references.rglob("*.md")):
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def has_classifier_schema(text: str) -> bool:
    return any(_SCHEMA_BULLET_RE.match(line) for line in text.splitlines())


def named_validator(text: str) -> str | None:
    match = _VALIDATOR_MENTION_RE.search(text)
    return match.group(0) if match else None


def validator_file_for(repo_root: Path, skill_id: str) -> str | None:
    for suffix in _VALIDATOR_SUFFIXES:
        candidate = repo_root / "scripts" / f"validate_{skill_id}{suffix}.py"
        if candidate.is_file():
            return candidate.name
    return None


def survey(repo_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for skill_dir in public_skill_dirs(repo_root):
        skill_id = skill_dir.name
        text = _skill_text(skill_dir)
        classifier = has_classifier_schema(text)
        validator = named_validator(text) or validator_file_for(repo_root, skill_id)
        rows.append(
            {
                "skill": skill_id,
                "classifier_schema": classifier,
                "validator": validator,
                "gap": bool(classifier and not validator),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root to survey.")
    parser.add_argument("--report", action="store_true", help="Print the human-readable survey (default).")
    parser.add_argument("--json", action="store_true", help="Emit the survey as JSON instead of text.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    rows = survey(repo_root)
    gaps = [row for row in rows if row["gap"]]

    if args.json:
        print(json.dumps({"skills": rows, "gap_count": len(gaps)}, indent=2))
        return 0

    print("Closeout Schema Survey (advisory; always exits 0)")
    for row in rows:
        if not row["classifier_schema"]:
            continue
        status = "GAP — no validator" if row["gap"] else f"ok — {row['validator']}"
        print(f"  {row['skill']}: classifier-bearing Output Shape -> {status}")
    if gaps:
        names = ", ".join(str(row["skill"]) for row in gaps)
        print(f"\n{len(gaps)} skill(s) with a classifier-bearing Output Shape and no named validator: {names}")
        print("See skills/public/create-skill/references/portable-authoring.md 'Closeout Schema Rule'.")
    else:
        print("\nNo classifier-bearing Output Shape without a validator. Closeout Schema Rule satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
