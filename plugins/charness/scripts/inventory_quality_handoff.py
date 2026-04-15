#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_RESOLVER_DIR = REPO_ROOT / "skills" / "public" / "quality" / "scripts"
if not _RESOLVER_DIR.is_dir():
    _RESOLVER_DIR = REPO_ROOT / "skills" / "quality" / "scripts"
sys.path[:0] = [str(_RESOLVER_DIR), str(REPO_ROOT)]

from resolve_adapter import load_adapter

HITL_FIELDS = (
    "target",
    "review_question",
    "decision_needed",
    "must_not_auto_decide",
    "observation_point",
    "revisit_cadence",
    "automation_candidate",
)
SECTION_RE = re.compile(r"^##\s+")


def section_text(lines: list[str], heading: str, next_heading: str | None = None) -> list[str]:
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    if next_heading is not None:
        try:
            end = lines.index(next_heading)
        except ValueError:
            end = len(lines)
    else:
        end = len(lines)
        for idx in range(start, len(lines)):
            if SECTION_RE.match(lines[idx]):
                end = idx
                break
    return lines[start:end]


def collect_bullets(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("- "):
            if current:
                bullets.append(" ".join(current).strip())
            current = [line[2:].strip()]
            continue
        if current and (line.startswith("  ") or not line.strip()):
            current.append(line.strip())
            continue
        if current:
            bullets.append(" ".join(current).strip())
            current = []
    if current:
        bullets.append(" ".join(current).strip())
    return bullets


def inventory_quality_handoff(artifact_text: str, artifact_path: str) -> dict[str, object]:
    lines = artifact_text.splitlines()
    recommended = section_text(lines, "## Recommended Next Gates", "## History")
    findings: list[dict[str, object]] = []
    for bullet in collect_bullets(recommended):
        if "NON_AUTOMATABLE" not in bullet:
            continue
        missing = [field for field in HITL_FIELDS if f"{field}=" not in bullet and f"`{field}`" not in bullet]
        if missing:
            findings.append(
                {
                    "type": "missing_hitl_handoff",
                    "item": bullet,
                    "missing_fields": missing,
                }
            )
    return {
        "schema_version": 1,
        "status": "advisory",
        "artifact": artifact_path,
        "findings": findings,
    }


def format_human(report: dict[str, object]) -> str:
    findings = report["findings"]
    assert isinstance(findings, list)
    if not findings:
        return "Quality HITL handoff inventory: no advisory findings."
    lines = [f"Quality HITL handoff inventory: {len(findings)} advisory finding(s)."]
    for finding in findings:
        assert isinstance(finding, dict)
        missing = finding["missing_fields"]
        assert isinstance(missing, list)
        lines.append(
            "- NON_AUTOMATABLE recommendation is missing HITL handoff fields: "
            + ", ".join(str(field) for field in missing)
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.artifact is None:
        adapter = load_adapter(repo_root)
        artifact_path = repo_root / adapter["artifact_path"]
    else:
        artifact_path = args.artifact if args.artifact.is_absolute() else repo_root / args.artifact
    try:
        artifact_label = str(artifact_path.relative_to(repo_root))
    except ValueError:
        artifact_label = str(artifact_path)
    report = inventory_quality_handoff(
        artifact_path.read_text(encoding="utf-8"),
        artifact_label,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_human(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
