#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from skills.public.quality.scripts.resolve_adapter import load_adapter

MAX_ARTIFACT_LINES = 140
REQUIRED_SECTIONS = (
    "## Scope",
    "## Current Gates",
    "## Runtime Signals",
    "## Healthy",
    "## Weak",
    "## Missing",
    "## Deferred",
    "## Commands Run",
    "## Recommended Next Gates",
    "## History",
)
HISTORY_LINK_RE = re.compile(r"\[.+\]\(history/[^)]+\.md\)")


class ValidationError(Exception):
    pass


def find_index(lines: list[str], heading: str) -> int:
    for index, line in enumerate(lines):
        if line.strip() == heading:
            return index
    raise ValidationError(f"missing required section `{heading}`")


def validate_section_order(lines: list[str]) -> None:
    indices = [find_index(lines, heading) for heading in REQUIRED_SECTIONS]
    if indices != sorted(indices):
        raise ValidationError("required sections must stay in canonical order")


def validate_history_section(lines: list[str]) -> None:
    start = find_index(lines, "## History") + 1
    section_lines = [line.strip() for line in lines[start:] if line.strip()]
    if not section_lines:
        raise ValidationError("`## History` must link to at least one archived review")
    if not any(HISTORY_LINK_RE.search(line) for line in section_lines):
        raise ValidationError("`## History` must contain at least one `history/*.md` markdown link")


def validate_quality_artifact(path: Path) -> None:
    if not path.exists():
        raise ValidationError(f"missing quality artifact `{path}`")

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "# Quality Review":
        raise ValidationError("quality artifact must start with `# Quality Review`")
    if len(lines) > MAX_ARTIFACT_LINES:
        raise ValidationError(
            f"quality artifact should stay concise; archive older review detail before it grows past {MAX_ARTIFACT_LINES} lines"
        )
    if len(lines) < 2 or not lines[1].startswith("Date: "):
        raise ValidationError("quality artifact must record `Date: YYYY-MM-DD` on line 2")

    validate_section_order(lines)
    validate_history_section(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    artifact_path = repo_root / adapter["artifact_path"]
    validate_quality_artifact(artifact_path)
    print(f"Validated quality artifact {artifact_path.relative_to(repo_root)}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
