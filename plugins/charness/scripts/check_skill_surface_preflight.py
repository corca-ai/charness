#!/usr/bin/env python3
"""Cheap pre-edit preflight for public/support skill-surface edits."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
MAX_SKILL_MD_LINES = 200
MAX_CORE_NONEMPTY_LINES = 160
PRESSURE_EXEMPT_H2_SECTIONS = {"Load-Bearing Anchors", "References"}


class PreflightError(Exception):
    pass


def _repo_relative(repo_root: Path, path: Path) -> Path:
    try:
        return path.relative_to(repo_root)
    except ValueError as exc:
        raise PreflightError(f"{path} is outside repo root {repo_root}") from exc


def _resolve_target(repo_root: Path, raw_path: str) -> tuple[Path, Path]:
    target = Path(raw_path)
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    rel = _repo_relative(repo_root, target)
    return target, rel


def _skill_context(repo_root: Path, target: Path) -> dict[str, Any]:
    rel = _repo_relative(repo_root, target)
    parts = rel.parts
    if len(parts) < 4 or parts[0] != "skills" or parts[1] not in {"public", "support"}:
        raise PreflightError("target must live under skills/public/<skill>/ or skills/support/<skill>/")

    skill_kind = parts[1]
    skill_id = parts[2]
    skill_root = repo_root / "skills" / skill_kind / skill_id
    skill_md = skill_root / "SKILL.md"
    if not skill_md.is_file():
        raise PreflightError(f"{skill_md.relative_to(repo_root)} is missing")

    if parts[3:] == ("SKILL.md",):
        target_kind = "skill_core"
    elif len(parts) >= 5 and parts[3] == "references" and target.suffix == ".md":
        target_kind = "reference"
    else:
        raise PreflightError("target must be SKILL.md or references/*.md within a skill package")

    return {
        "skill_kind": skill_kind,
        "skill_id": skill_id,
        "skill_root": skill_root,
        "skill_md": skill_md,
        "target_kind": target_kind,
    }


def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def _remove_pressure_exempt_sections(lines: list[str]) -> list[str]:
    kept: list[str] = []
    skip = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip()
            skip = section in PRESSURE_EXEMPT_H2_SECTIONS
            if skip:
                continue
        if not skip:
            kept.append(line)
    return kept


def _core_nonempty_lines(text: str) -> int:
    body_lines = _remove_pressure_exempt_sections(_strip_frontmatter(text).splitlines())
    return sum(1 for line in body_lines if line.strip())


def _headroom(current: int, limit: int, preview_delta: int) -> dict[str, Any]:
    after = current + preview_delta
    remaining = limit - current
    remaining_after_preview = limit - after
    return {
        "current": current,
        "limit": limit,
        "preview_delta": preview_delta,
        "after_preview": after,
        "remaining": remaining,
        "remaining_after_preview": remaining_after_preview,
        "blocked": remaining_after_preview < 0,
    }


def _couplings(target_kind: str, skill_kind: str) -> list[dict[str, str]]:
    rows = [
        {
            "id": "validate_skills",
            "message": "Skill package shape, SKILL.md total line ceiling, references listings, and portability checks.",
            "command": "python3 scripts/validate_skills.py --repo-root .",
        },
        {
            "id": "markdown_inline_code",
            "message": "Wrapped inline code spans surface through check-markdown before broad quality.",
            "command": "./scripts/check-markdown.sh",
        },
        {
            "id": "doc_links",
            "message": "Relative markdown/file links must resolve from the edited markdown file.",
            "command": "python3 scripts/check_doc_links.py --repo-root .",
        },
    ]
    if skill_kind == "public":
        rows.append(
            {
                "id": "plugin_mirror_sync",
                "message": "Public skill edits require plugin mirror sync before validators and staging.",
                "command": "python3 scripts/sync_root_plugin_manifests.py --repo-root .",
            }
        )
    if target_kind == "reference":
        rows.append(
            {
                "id": "reference_link_depth",
                "message": "references/*.md links need one extra ../ compared with SKILL.md-local links.",
                "command": "python3 scripts/check_doc_links.py --repo-root .",
            }
        )
    rows.append(
        {
            "id": "staged_index_hazard",
            "message": "Do not run staged mirror-drift e2e checks against the shared parent repo during parallel hooks.",
            "command": "Use an isolated seeded repo for tests that exercise git write-tree.",
        }
    )
    return rows


def _run_checks(repo_root: Path) -> list[dict[str, Any]]:
    commands = [
        ("validate_skills", ["python3", "scripts/validate_skills.py", "--repo-root", str(repo_root)]),
        ("check_doc_links", ["python3", "scripts/check_doc_links.py", "--repo-root", str(repo_root)]),
        ("check_markdown", ["./scripts/check-markdown.sh"]),
    ]
    results: list[dict[str, Any]] = []
    for check_id, command in commands:
        completed = subprocess.run(command, cwd=repo_root, check=False, capture_output=True, text=True)
        results.append(
            {
                "id": check_id,
                "command": " ".join(command),
                "returncode": completed.returncode,
                "stdout_tail": completed.stdout[-1000:],
                "stderr_tail": completed.stderr[-1000:],
            }
        )
    return results


def build_report(repo_root: Path, target_arg: str, preview_delta: int, run_checks: bool) -> dict[str, Any]:
    target, rel_target = _resolve_target(repo_root, target_arg)
    context = _skill_context(repo_root, target)
    skill_md = context["skill_md"]
    text = skill_md.read_text(encoding="utf-8")
    target_exists = target.is_file()
    target_lines = len(target.read_text(encoding="utf-8").splitlines()) if target_exists else None
    skill_preview = preview_delta if context["target_kind"] == "skill_core" else 0
    headroom = {
        "skill_md_total": _headroom(len(text.splitlines()), MAX_SKILL_MD_LINES, skill_preview),
        "core_nonempty": _headroom(_core_nonempty_lines(text), MAX_CORE_NONEMPTY_LINES, skill_preview),
    }
    blockers = [
        name
        for name, row in headroom.items()
        if row["blocked"]
    ]
    checks = _run_checks(repo_root) if run_checks else []
    check_failures = [row["id"] for row in checks if row["returncode"] != 0]
    return {
        "status": "blocked" if blockers or check_failures else "ok",
        "blockers": blockers,
        "check_failures": check_failures,
        "skill": {
            "id": context["skill_id"],
            "kind": context["skill_kind"],
            "root": str(context["skill_root"].relative_to(repo_root)),
            "skill_md": str(skill_md.relative_to(repo_root)),
        },
        "target": {
            "path": rel_target.as_posix(),
            "kind": context["target_kind"],
            "exists": target_exists,
            "current_lines": target_lines,
        },
        "preview_delta": preview_delta,
        "headroom": headroom,
        "couplings": _couplings(context["target_kind"], context["skill_kind"]),
        "checks": checks,
    }


def _format_headroom(label: str, row: dict[str, Any]) -> str:
    suffix = " BLOCKER" if row["blocked"] else ""
    return (
        f"{label}: {row['current']}/{row['limit']} "
        f"({row['remaining']} left; after preview {row['remaining_after_preview']} left){suffix}"
    )


def format_human(report: dict[str, Any]) -> str:
    lines = [
        f"skill-surface-preflight: {report['target']['path']} ({report['target']['kind']})",
        f"skill: {report['skill']['kind']}/{report['skill']['id']}",
        _format_headroom("SKILL.md total", report["headroom"]["skill_md_total"]),
        _format_headroom("core nonempty", report["headroom"]["core_nonempty"]),
    ]
    if report["target"]["current_lines"] is not None:
        lines.append(f"target current lines: {report['target']['current_lines']}")
    lines.append("couplings:")
    for row in report["couplings"]:
        lines.append(f"- {row['id']}: {row['message']} [{row['command']}]")
    if report["checks"]:
        lines.append("targeted checks:")
        for row in report["checks"]:
            status = "PASS" if row["returncode"] == 0 else "FAIL"
            lines.append(f"- {row['id']}: {status} ({row['command']})")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--path", required=True, help="Skill SKILL.md or references/*.md path")
    parser.add_argument("--preview-delta", type=int, default=0, help="Planned added lines for this target")
    parser.add_argument("--run-checks", action="store_true", help="Run targeted read-only validators now")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.preview_delta < 0:
        parser.error("--preview-delta must be non-negative")
    try:
        report = build_report(repo_root, args.path, args.preview_delta, args.run_checks)
    except PreflightError as exc:
        print(f"skill-surface-preflight: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_human(report))
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
