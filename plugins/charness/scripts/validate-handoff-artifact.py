#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifact_validator import (
    ValidationError,
    find_index,
    read_lines,
    validate_exact_h2_sections,
    validate_max_lines,
    validate_nonempty_sections,
    validate_title,
)
from skills.public.handoff.scripts.resolve_adapter import load_adapter

MAX_ARTIFACT_LINES = 120
REQUIRED_SECTIONS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")


def validate_references(lines: list[str]) -> None:
    start = find_index(lines, "## References") + 1
    section_lines = [line.strip() for line in lines[start:] if line.strip()]
    if not any(MARKDOWN_LINK_RE.search(line) for line in section_lines):
        raise ValidationError("`## References` must contain at least one markdown link")


def validate_handoff_artifact(path: Path) -> None:
    lines = read_lines(path)
    validate_title(
        lines,
        title_predicate=lambda line: line.startswith("# ") and "handoff" in line.lower(),
        error_message="handoff artifact must start with a `# ... Handoff` heading",
    )
    validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="handoff artifact")
    validate_exact_h2_sections(lines, REQUIRED_SECTIONS)
    validate_nonempty_sections(lines, REQUIRED_SECTIONS)
    validate_references(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    artifact_path = repo_root / adapter["artifact_path"]
    validate_handoff_artifact(artifact_path)
    print(f"Validated handoff artifact {artifact_path.relative_to(repo_root)}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

