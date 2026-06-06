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
# A changed SKILL.md must keep at least this many core_nonempty lines of headroom
# below MAX_CORE_NONEMPTY_LINES. This buffer is the single source of truth shared
# by the broad-gate core-headroom test and the commit-boundary ratchet below, so
# the two surfaces can never disagree on the buffer width.
CORE_NONEMPTY_HEADROOM_BUFFER = 4
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


def _is_skill_core_path(rel: str) -> bool:
    parts = Path(rel).parts
    return (
        len(parts) == 4
        and parts[0] == "skills"
        and parts[1] in {"public", "support"}
        and parts[3] == "SKILL.md"
    )


def _git_show(repo_root: Path, ref: str) -> str | None:
    result = subprocess.run(
        ["git", "show", ref],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def _base_core_nonempty(repo_root: Path, rel: str) -> int | None:
    """core_nonempty of the committed (HEAD) version, or None when untracked."""
    text = _git_show(repo_root, f"HEAD:{rel}")
    return None if text is None else _core_nonempty_lines(text)


def _changed_skill_text(repo_root: Path, rel: str, target: Path) -> str | None:
    """Content that will be committed: the staged index blob (``git show :<rel>``),
    so the commit-boundary gate judges what is actually being committed rather than
    a working tree that may diverge from the index. Falls back to the working tree
    when the path is not in the index (ad-hoc/unstaged invocation)."""
    staged = _git_show(repo_root, f":{rel}")
    if staged is not None:
        return staged
    return target.read_text(encoding="utf-8") if target.is_file() else None


def evaluate_core_headroom(
    new_core: int,
    base_core: int | None,
    *,
    limit: int = MAX_CORE_NONEMPTY_LINES,
    buffer: int = CORE_NONEMPTY_HEADROOM_BUFFER,
) -> dict[str, Any]:
    """Ratchet verdict for one changed SKILL.md core_nonempty count.

    Blocks only when the change leaves the core under the >=``buffer`` headroom
    AND the change made headroom worse (or the surface is brand new). An existing
    surface already under buffer is grandfathered: it may stay flat or improve,
    but it may not erode further while under buffer. A newly tracked surface has
    no base, so it must carry the buffer from the start.
    """
    new_remaining = limit - new_core
    base_remaining = None if base_core is None else limit - base_core
    under_buffer = new_remaining < buffer
    regressed = base_remaining is None or new_remaining < base_remaining
    return {
        "limit": limit,
        "buffer": buffer,
        "new_core": new_core,
        "new_remaining": new_remaining,
        "base_core": base_core,
        "base_remaining": base_remaining,
        "under_buffer": under_buffer,
        "regressed": regressed,
        "blocked": under_buffer and regressed,
    }


def scan_changed_skill_md(repo_root: Path, paths: list[str]) -> dict[str, Any]:
    """Commit-boundary core-headroom ratchet over changed SKILL.md paths."""
    checked: list[dict[str, Any]] = []
    for raw in paths:
        rel = Path(raw).as_posix()
        if not _is_skill_core_path(rel):
            continue
        new_text = _changed_skill_text(repo_root, rel, repo_root / rel)
        if new_text is None:
            continue
        row = evaluate_core_headroom(
            _core_nonempty_lines(new_text),
            _base_core_nonempty(repo_root, rel),
        )
        row["path"] = rel
        checked.append(row)
    blocked = [row["path"] for row in checked if row["blocked"]]
    return {
        "status": "blocked" if blocked else "ok",
        "blocked": blocked,
        "checked": checked,
    }


def format_changed_human(report: dict[str, Any]) -> str:
    lines = [f"skill-core-headroom: {report['status']}"]
    for row in report["checked"]:
        verdict = "BLOCK" if row["blocked"] else "ok"
        was = "new" if row["base_remaining"] is None else str(row["base_remaining"])
        lines.append(
            f"- {row['path']}: {row['new_remaining']} left "
            f"(buffer {row['buffer']}, was {was}) [{verdict}]"
        )
    if report["status"] == "blocked":
        lines.append(
            "Changed SKILL.md core dropped below the core_nonempty headroom "
            f"buffer ({CORE_NONEMPTY_HEADROOM_BUFFER} lines). Move prose into "
            "references/ or scripts/ to restore headroom before the broad gate "
            "core-headroom test fails late."
        )
    return "\n".join(lines)


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
    parser.add_argument("--path", help="Skill SKILL.md or references/*.md path (single-surface preflight)")
    parser.add_argument(
        "--changed-skill-md",
        nargs="*",
        help="Changed SKILL.md paths to gate with the commit-boundary core-headroom ratchet",
    )
    parser.add_argument("--preview-delta", type=int, default=0, help="Planned added lines for this target")
    parser.add_argument("--run-checks", action="store_true", help="Run targeted read-only validators now")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    if args.changed_skill_md is not None:
        report = scan_changed_skill_md(repo_root, args.changed_skill_md)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_changed_human(report))
        return 1 if report["status"] == "blocked" else 0

    if not args.path:
        parser.error("--path is required unless --changed-skill-md is given")
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
