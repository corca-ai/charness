#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def _resolver_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "quality" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("quality resolve_adapter.py not found")


_quality_resolve_adapter = load_path_module("quality_resolve_adapter", _resolver_path(REPO_ROOT))
load_adapter = _quality_resolve_adapter.load_adapter
_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines
validate_date_line = _scripts_artifact_validator_module.validate_date_line
validate_max_lines = _scripts_artifact_validator_module.validate_max_lines
validate_section_order = _scripts_artifact_validator_module.validate_section_order

MAX_ARTIFACT_LINES = 140
REQUIRED_SECTIONS = (
    "## Scope",
    "## Current Gates",
    "## Runtime Signals",
    "## Healthy",
    "## Weak",
    "## Missing",
    "## Deferred",
    "## Advisory",
    "## Delegated Review",
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
FORBIDDEN_SUBAGENT_BLOCKER_PHRASES = (
    "did not explicitly allow subagents",
    "explicit subagent allowance",
    "same-agent fallback",
    "same agent fallback",
    "same-agent pass as equivalent",
)
DELEGATED_REVIEW_STATUSES = ("executed", "blocked", "not_applicable")
SLOW_GATE_DELEGATED_LENSES = (
    "fixture-economics",
    "parallel-critical-path",
    "duplicated-proof",
)
ADVISORY_EVIDENCE_MARKERS = (
    "`",
    "inventory",
    "command:",
    "artifact:",
    "evidence:",
    "because",
    "from ",
    "found by ",
)


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


def validate_advisory_section(lines: list[str]) -> None:
    start = find_index(lines, "## Advisory") + 1
    end = find_index(lines, "## Delegated Review")
    section_lines = [line.strip() for line in lines[start:end] if line.strip()]
    bullets = [line for line in section_lines if line.startswith("- ")]
    if not bullets:
        raise ValidationError("`## Advisory` must contain at least one bullet")
    lowered = "\n".join(section_lines).lower()
    if "none" in lowered and "none found by inventory" not in lowered:
        raise ValidationError("empty advisory claims must use `none found by inventory` evidence wording")
    if "none found by inventory" in lowered and not any(token in lowered for token in ("command:", "artifact:", "`")):
        raise ValidationError("empty advisory claims must cite inventory-backed command or artifact evidence")
    for bullet in bullets:
        bullet_lowered = bullet.lower()
        if "none found by inventory" in bullet_lowered:
            continue
        if not any(marker in bullet_lowered for marker in ADVISORY_EVIDENCE_MARKERS):
            raise ValidationError("advisory bullets must cite inventory, command, artifact, or other explicit evidence")


def validate_delegated_review_section(lines: list[str]) -> None:
    start = find_index(lines, "## Delegated Review") + 1
    end = find_index(lines, "## Commands Run")
    section_lines = [line.strip() for line in lines[start:end] if line.strip()]
    if not section_lines:
        raise ValidationError("`## Delegated Review` must record executed, blocked, or not_applicable status")
    lowered = "\n".join(section_lines).lower()
    if not any(status in lowered for status in DELEGATED_REVIEW_STATUSES):
        raise ValidationError("`## Delegated Review` must include executed, blocked, or not_applicable status")
    if "blocked" in lowered and "host signal:" not in lowered and "tool signal:" not in lowered:
        raise ValidationError("blocked delegated review must cite a concrete host signal or tool signal")
    artifact_text = "\n".join(lines).lower()
    slow_gate_scope = any(token in artifact_text for token in ("slow", "standing test", "fixture economics"))
    if slow_gate_scope and "executed" in lowered:
        missing = [lens for lens in SLOW_GATE_DELEGATED_LENSES if lens not in lowered]
        if missing:
            raise ValidationError(
                "runtime/test quality artifacts with executed delegated review must name slow-gate lenses: "
                + ", ".join(missing)
            )


def validate_subagent_blocker_reasoning(lines: list[str]) -> None:
    for raw in lines:
        lowered = raw.lower()
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in lowered:
                raise ValidationError(
                    "quality artifact must not treat missing explicit subagent allowance as the canonical blocker; "
                    "cite a concrete host signal or describe the pass as degraded/unprobed"
                )


def validate_quality_artifact(path: Path) -> None:
    lines = read_lines(path)
    if not lines or lines[0].strip() != "# Quality Review":
        raise ValidationError("quality artifact must start with `# Quality Review`")
    validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="quality artifact")
    validate_date_line(lines)

    validate_section_order(lines, REQUIRED_SECTIONS)
    validate_runtime_signals_section(lines)
    validate_advisory_section(lines)
    validate_delegated_review_section(lines)
    validate_recommended_next_gates_section(lines)
    validate_history_section(lines)
    validate_subagent_blocker_reasoning(lines)


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
