#!/usr/bin/env python3
"""Cheap pre-edit preflight for public/support skill-surface edits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
_issue_anchor_scan = import_repo_module(__file__, "scripts.gates_support.skill_issue_anchor_scan")
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
run_processes_in_order = _subprocess_guard.run_processes_in_order
_density = import_repo_module(__file__, "scripts.gates_support.skill_core_density")
# Core-density accounting lives in its own module (cohesive split at the length
# cap): the preflight owns the verdict, `skill_core_density` owns the count and
# the exemption audit. Re-exported so the preflight stays the single import for
# callers and tests.
CLOSEOUT_VOCAB_SECTION = _density.CLOSEOUT_VOCAB_SECTION
PRESSURE_EXEMPT_H2_SECTIONS = _density.PRESSURE_EXEMPT_H2_SECTIONS
CLOSEOUT_VOCAB_MAX_LINES = _density.CLOSEOUT_VOCAB_MAX_LINES
PRESSURE_EXEMPT_BUDGET = _density.PRESSURE_EXEMPT_BUDGET
pressure_exempt_findings = _density.pressure_exempt_findings
_core_nonempty_lines = _density.core_nonempty_lines
# The one action that clears an exempt-section block. The gate's other blocking
# cause (core headroom) has the opposite remedy, so naming only that one left an
# author restructuring a healthy skill and still blocked.
EXEMPT_SECTION_REMEDIATION = (
    "A line under an exempt `## References` / `## Load-Bearing Anchors` / "
    "`## Closeout Vocabulary` heading must stay token-shaped. Rewrite the flagged "
    "line as a single clause, or move the explanation into `references/` — see "
    "docs/authoring-preflight.md `## SKILL.md core headroom`."
)
# The anchor scan's own remediation, which reached the operator only through
# `skill_issue_anchor_scan.format_human`. This gate no longer renders human text,
# so the paragraph rides on the payload instead of being dropped on the way out.
_ISSUE_ANCHOR_REMEDY = (
    "Disallowed issue anchors (`#NNN`, `owner/repo#N`, `issues/N`) in a portable skill "
    "package. Keep issue provenance in the commit message and the goal/critique "
    "artifact, not the package, before the commit-time validate_skill_ergonomics "
    "sweep blocks it."
)
MAX_SKILL_MD_LINES = 200
# Non-blocking near-cap warning floor (#350): at or above this total, an added
# line (e.g. a reciprocal propagation line from an adjacent skill's author) may
# not land unless a concept is split out or deleted, so surface the trap before
# prose is written instead of at validator rejection.
NEAR_CAP_WARN_LINES = 195
MAX_CORE_NONEMPTY_LINES = 160
# A changed SKILL.md must keep at least this many core_nonempty lines of headroom
# below MAX_CORE_NONEMPTY_LINES. This buffer is the single source of truth shared
# by the broad-gate core-headroom test and the commit-boundary ratchet below, so
# the two surfaces can never disagree on the buffer width.
CORE_NONEMPTY_HEADROOM_BUFFER = 4


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
        raise PreflightError(
            "target must live under skills/public/<skill>/ or skills/support/<skill>/"
        )

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
    result = run_process(
        ["git", "show", ref],
        cwd=repo_root,
        timeout_seconds=None,
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
        row["exempt_findings"] = pressure_exempt_findings(new_text)
        row["blocked"] = row["blocked"] or bool(row["exempt_findings"])
        row["path"] = rel
        checked.append(row)
    blocked = [row["path"] for row in checked if row["blocked"]]
    # `unscoped`: a NAMED scope that ratcheted nothing is not `ok`.
    # `_is_skill_core_path` requires exactly four REPO-RELATIVE parts, so the
    # ABSOLUTE path of a real SKILL.md was dropped and the run still reported a
    # pass. An EMPTY `paths` keeps its meaning — the hook computed "no SKILL.md
    # changed", a real answer — per the empty-scope family's discovered-vs-named
    # asymmetry (charness-artifacts/critique/2026-07-27-empty-scope-family.md).
    # No per-path `unscoped` list and no extra human line: this file sits at its
    # 480-line cap, and `checked: []` beside the status already names the scope.
    return {
        "status": "blocked" if blocked else ("unscoped" if paths and not checked else "ok"),
        "blocked": blocked,
        "checked": checked,
    }


def changed_payload(report: dict[str, Any]) -> dict[str, Any]:
    """Fold the remediation prose into the payload the gate emits.

    Two different causes set `blocked`, and each needs its own remediation. The
    headroom paragraph told an author with 158 lines of headroom to split a
    concept out -- a prescribed action that does not clear an exempt-section
    block. Output is unconditionally YAML, so the remedy has to be a field.
    """
    payload = dict(report)
    payload["label"] = "skill-core-headroom"
    if report["status"] == "blocked":
        payload["remedy"] = _changed_blocked_message(report)
    return payload


def _changed_blocked_message(report: dict[str, Any]) -> str:
    checked = report["checked"]
    under_buffer = [row for row in checked if row["blocked"] and not row.get("exempt_findings")]
    messages: list[str] = []
    if any(row.get("exempt_findings") for row in checked):
        messages.append(EXEMPT_SECTION_REMEDIATION)
    if under_buffer or not messages:
        messages.append(
            "Changed SKILL.md core dropped below the core_nonempty headroom "
            f"buffer ({CORE_NONEMPTY_HEADROOM_BUFFER} lines). Split a concept "
            "into its own surface or delete one — do not shave lines to fit; "
            "fix this before the broad gate core-headroom test fails late."
        )
    return "\n".join(messages)


def _couplings(target_kind: str, skill_kind: str) -> list[dict[str, str]]:
    rows = [
        {
            "id": "validate_skills",
            "message": "Skill package shape, SKILL.md total line ceiling, references listings, and portability checks.",
            "command": "python3 -m tools.validate_skills --repo-root .",  # export-guard: filtered by _authoring_checkout before use
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
        {
            "id": "skill_ergonomics",
            "message": "Portable-package edits must avoid bare issue anchors, dated incidents, and host-surface references (or declare them).",
            "command": "python3 scripts/validate_skill_ergonomics.py --repo-root .",
        },
        {
            "id": "ownership_overlap",
            "message": "Cross-namespace tokens (charness-artifacts/<other>/, .agents/<other>-adapter.yaml) need an allowlist entry with a reason.",
            "command": "python3 scripts/check_skill_ownership_overlap.py --repo-root .",
        },
        {
            "id": "attention_state",
            "message": "A new exit-zero attention term in a package script must be declared in attention-state-visibility.json.",
            "command": "python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root tools --scan-root skills --scan-root-map ../charness-support=skills/support",  # export-guard: filtered by _authoring_checkout before use
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


def _check_commands(repo_root: Path) -> list[tuple[str, list[str]]]:
    """The full portable-package gate set this preflight runs in one pass (#328).

    Reporting all of these at once is the point: authoring into a skill package
    otherwise pays for them as serial commit-boundary gate failures (ergonomics
    issue-anchor, cross-namespace ownership overlap, exit-zero attention term),
    one round-trip at a time. Keep this aligned with the skill-package surface
    verify_commands in .agents/surfaces.json.
    """
    root = str(repo_root)
    return [
        (
            "validate_skills",
            ["python3", "-m", "tools.validate_skills", "--repo-root", root],
        ),  # export-guard: filtered by _authoring_checkout before use
        (
            "validate_skill_ergonomics",
            ["python3", "scripts/validate_skill_ergonomics.py", "--repo-root", root],
        ),
        (
            "check_skill_ownership_overlap",
            ["python3", "scripts/check_skill_ownership_overlap.py", "--repo-root", root],
        ),
        (
            "validate_attention_state_visibility",
            [
                "python3",
                "-m",
                "tools.validate_attention_state_visibility",  # export-guard: filtered by _authoring_checkout before use
                "--repo-root",
                root,
                "--scan-root",
                "scripts",
                "--scan-root",
                "tools",  # export-guard: filtered by _authoring_checkout before use
                "--scan-root",
                "skills",
                "--scan-root-map",
                "../charness-support=skills/support",
            ],
        ),
        ("check_doc_links", ["python3", "scripts/check_doc_links.py", "--repo-root", root]),
        ("check_markdown", ["./scripts/check-markdown.sh"]),
    ]


def _check_result(check_id: str, command: list[str], completed) -> dict[str, Any]:
    return {
        "id": check_id,
        "command": " ".join(command),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def _authoring_checkout(repo_root: Path) -> bool:
    """The charness source checkout: a consumer's own `tools/` directory is not it."""
    return (repo_root / "tools" / "__init__.py").is_file() and (
        repo_root / "packaging" / "charness.json"
    ).is_file()


def _authoring_only(command: list[str] | str) -> bool:
    """`python3 -m tools.<name>` gates live only in the charness authoring repo.

    The export carries no `tools/` tree, so a consumer running this preflight
    must not be told to run, or fail on, a command it cannot have.
    """
    text = command if isinstance(command, str) else " ".join(command)
    return "-m tools." in text  # export-guard: the discriminator string itself


def _run_checks(repo_root: Path) -> list[dict[str, Any]]:
    commands = _check_commands(repo_root)
    if not _authoring_checkout(repo_root):
        commands = [item for item in commands if not _authoring_only(item[1])]
    completed = run_processes_in_order(
        [command for _check_id, command in commands], cwd=repo_root, timeout_seconds=None
    )
    return [
        _check_result(check_id, command, result)
        for (check_id, command), result in zip(commands, completed, strict=True)
    ]


def build_report(
    repo_root: Path, target_arg: str, preview_delta: int, run_checks: bool
) -> dict[str, Any]:
    target, rel_target = _resolve_target(repo_root, target_arg)
    context = _skill_context(repo_root, target)
    skill_md = context["skill_md"]
    text = skill_md.read_text(encoding="utf-8")
    target_exists = target.is_file()
    target_lines = len(target.read_text(encoding="utf-8").splitlines()) if target_exists else None
    skill_preview = preview_delta if context["target_kind"] == "skill_core" else 0
    headroom = {
        "skill_md_total": _headroom(len(text.splitlines()), MAX_SKILL_MD_LINES, skill_preview),
        "core_nonempty": _headroom(
            _core_nonempty_lines(text), MAX_CORE_NONEMPTY_LINES, skill_preview
        ),
    }
    blockers = [name for name, row in headroom.items() if row["blocked"]]
    warnings: list[dict[str, str]] = []
    current_total = headroom["skill_md_total"]["current"]
    if current_total >= NEAR_CAP_WARN_LINES:
        warnings.append(
            {
                "id": "near_cap",
                "message": (
                    f"SKILL.md total {current_total}/{MAX_SKILL_MD_LINES} is at/above the "
                    f"{NEAR_CAP_WARN_LINES}-line near-cap floor: an added line may not land. "
                    "Split a concept into its own surface or delete one — do not shave lines "
                    "to fit; file an issue if neither fits now, and never silently drop a "
                    "reciprocal/propagation line."
                ),
            }
        )
    exempt_findings = pressure_exempt_findings(text)
    checks = _run_checks(repo_root) if run_checks else []
    check_failures = [row["id"] for row in checks if row["returncode"] != 0]
    return {
        "status": "blocked" if blockers or check_failures or exempt_findings else "ok",
        "blockers": blockers,
        "warnings": warnings,
        "exempt_findings": exempt_findings,
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
        "couplings": [
            coupling
            for coupling in _couplings(context["target_kind"], context["skill_kind"])
            if _authoring_checkout(repo_root) or not _authoring_only(coupling["command"])
        ],
        "checks": checks,
    }


def preflight_payload(report: dict[str, Any]) -> dict[str, Any]:
    """Fold the verdict-explaining text into the payload the gate emits.

    The rows already carry every measured number. What lived ONLY in the deleted
    human renderer is the exempt-section remediation (an author sitting on 158
    lines of headroom cannot act on a bare `exempt_findings` list) and the
    PASS/FAIL reading of each targeted check's return code.
    """
    payload = dict(report)
    payload["label"] = "skill-surface-preflight"
    if report.get("exempt_findings"):
        payload["remedy"] = EXEMPT_SECTION_REMEDIATION
    if report["checks"]:
        payload["check_results"] = [
            {**row, "status": "PASS" if row["returncode"] == 0 else "FAIL"}
            for row in report["checks"]
        ]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--path", help="Skill SKILL.md or references/*.md path (single-surface preflight)"
    )
    parser.add_argument(
        "--changed-skill-md",
        nargs="*",
        help="Changed SKILL.md paths to gate with the commit-boundary core-headroom ratchet",
    )
    parser.add_argument(
        "--scan-issue-anchors",
        nargs="*",
        help="Skill-package file paths to scan for disallowed issue anchors at edit time",
    )
    parser.add_argument(
        "--preview-delta", type=int, default=0, help="Planned added lines for this target"
    )
    parser.add_argument(
        "--run-checks", action="store_true", help="Run targeted read-only validators now"
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    if args.changed_skill_md is not None:
        report = scan_changed_skill_md(repo_root, args.changed_skill_md)
        emit_yaml(changed_payload(report))
        return 1 if report["status"] in {"blocked", "unscoped"} else 0

    if args.scan_issue_anchors is not None:
        try:
            report = _issue_anchor_scan.scan_issue_anchors(repo_root, args.scan_issue_anchors)
        except _issue_anchor_scan.IssueAnchorScanError as exc:
            print(f"skill-issue-anchor-scan: {exc}", file=sys.stderr)
            return 2
        payload = {**report, "label": "skill-issue-anchor-scan"}
        if report["findings"]:
            payload["remedy"] = _ISSUE_ANCHOR_REMEDY
        emit_yaml(payload)
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

    emit_yaml(preflight_payload(report))
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
