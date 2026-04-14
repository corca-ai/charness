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
    validate_date_line,
    validate_max_lines,
    validate_section_order,
)
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
RUNTIME_SIGNAL_PREFIXES = (
    "- runtime hot spots:",
    "- coverage gate:",
    "- evaluator depth:",
)
RECOMMENDED_GATE_PREFIXES = ("- active ", "- passive ")


def validate_history_section(lines: list[str]) -> None:
    start = find_index(lines, "## History") + 1
    section_lines = [line.strip() for line in lines[start:] if line.strip()]
    if not section_lines:
        raise ValidationError("`## History` must link to at least one archived review")
    if not any(HISTORY_LINK_RE.search(line) for line in section_lines):
        raise ValidationError("`## History` must contain at least one `history/*.md` markdown link")


def validate_runtime_signals_section(lines: list[str]) -> None:
    start = find_index(lines, "## Runtime Signals") + 1
    end = find_index(lines, "## Healthy")
    section_lines = [line.strip() for line in lines[start:end] if line.strip()]
    missing = [prefix for prefix in RUNTIME_SIGNAL_PREFIXES if not any(line.startswith(prefix) for line in section_lines)]
    if missing:
        raise ValidationError(
            "`## Runtime Signals` must explicitly state runtime hot spots, coverage-gate status, "
            "and evaluator depth"
        )


def validate_recommended_next_gates_section(lines: list[str]) -> None:
    start = find_index(lines, "## Recommended Next Gates") + 1
    end = find_index(lines, "## History")
    section_lines = [line.strip() for line in lines[start:end] if line.strip()]
    bullets = [line for line in section_lines if line.startswith("- ")]
    if not bullets:
        raise ValidationError("`## Recommended Next Gates` must contain at least one bullet")
    if any(not line.startswith(RECOMMENDED_GATE_PREFIXES) for line in bullets):
        raise ValidationError("recommended next gates must start with `- active ` or `- passive `")
    for line in bullets:
        if line.startswith("- passive ") and " because" not in line and " until" not in line:
            raise ValidationError("passive recommended next gates must explain why they are passive")


def validate_quality_artifact(path: Path) -> None:
    lines = read_lines(path)
    if not lines or lines[0].strip() != "# Quality Review":
        raise ValidationError("quality artifact must start with `# Quality Review`")
    validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="quality artifact")
    validate_date_line(lines)

    validate_section_order(lines, REQUIRED_SECTIONS)
    validate_runtime_signals_section(lines)
    validate_recommended_next_gates_section(lines)
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
