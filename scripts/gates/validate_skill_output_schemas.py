#!/usr/bin/env python3
"""Refuse a classifier-bearing `Output Shape` that names no validator.

The Closeout Schema Rule
(`skills/public/create-skill/references/portable-authoring.md`): when a skill's
`Output Shape` declares classifier fields the caller must act on, ship a
validator that fails when those fields are missing or free-form. A pipe-delimited
schema bullet with a classifier key is that form; prose-only output is not.
Exit 1 when any public skill has the form and no named validator.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

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
    parser.add_argument(
        "--report",
        action="store_true",
        help="Accepted and inert: the survey is always emitted, as YAML, on every run.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    rows = survey(repo_root)
    gaps = [row for row in rows if row["gap"]]
    payload = {
        "rule_reference": (
            "skills/public/create-skill/references/portable-authoring.md 'Closeout Schema Rule'"
        ),
        "skills": rows,
        "gap_count": len(gaps),
        "gap_skills": [str(row["skill"]) for row in gaps],
        "gap_summary": (
            f"{len(gaps)} skill(s) with a classifier-bearing Output Shape and no named validator."
            if gaps
            else "No classifier-bearing Output Shape without a validator. Closeout Schema Rule satisfied."
        ),
    }
    emit_yaml(payload)
    return 1 if gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
