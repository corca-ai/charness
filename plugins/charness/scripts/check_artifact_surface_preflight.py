#!/usr/bin/env python3
"""Author-time shape preflight for the hand-authored artifact family.

Generalizes ``check_skill_surface_preflight.py`` from skill surfaces to the
``charness-artifacts/**`` artifact-shape validator family. Given an artifact
path or type it surfaces the owning validator's required shape — delegating to
the owning scaffold or the validator's declared shape source, never
re-declaring it — and at the commit boundary it relocates the owning validator's
verdict earlier (a blocking structural-sweep member), so an author learns the
required shape before the broad gate rather than by failing it
(the #284 -> #308 -> #325 -> #329 -> #332 -> #334 recurrence class).

The registry below is the generalization: one place that knows the artifact-
authoring family. Each surface declares a *shape source* — a ``scaffold`` script
(stub-by-construction) or a ``template`` section (the goal template already seeds
the closeout block) — plus its owning validator. The dispatcher reads shape from
that source; it adds no new shape requirement and changes no validator verdict.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

# Goal template that already seeds the `## Final Verification` closeout block;
# the goal-closeout surface has no scaffold script, so this template section IS
# the single-source shape an author should start from.
_GOAL_TEMPLATE = "skills/public/achieve/scripts/goal_artifact_template.md"


@dataclass(frozen=True)
class Surface:
    artifact_type: str
    prefix: str | None  # repo-relative path prefix (or exact file); None for non-path
    validator: str | None  # repo-relative owning validator
    scaffold: str | None  # repo-relative scaffold script (shape source)
    template_section: str | None  # (template_path, "## Heading") shape source
    commit_boundary: bool  # relocate the validator's verdict to the commit gate
    note: str
    paths_arg: bool = True  # validator accepts --paths; False => validate-all default

    def excludes(self, rel: str) -> bool:
        # retro validator skips its rolled-up memory + archived history.
        if self.artifact_type != "retro":
            return False
        tail = rel[len(self.prefix or ""):]
        return tail == "recent-lessons.md" or tail.startswith("history/")


# The artifact-authoring shape family. Two coverage tiers, by validator shape:
#  - Prefix-mapped surfaces (critique, ideation, retro) accept `--paths` and run
#    CHANGED-SCOPED, so they are wired into the blocking fail-fast structural
#    sweep (`commit_boundary=True`): cheap, changed-scoped, no reordering of the
#    deeper run_slice_closeout stages.
#  - Adapter-scoped siblings (debug, quality, handoff) validate-ALL (no --paths)
#    and the debug surface feeds run_slice_closeout's risk-interrupt machinery, so
#    they are NOT in the fail-fast sweep (`commit_boundary=False`); they get
#    author-time shape help via `--type`/`--emit-stub`/`--path` and the broad gate
#    remains their enforcement. (Putting a validate-all gate in the fail-fast sweep
#    would reorder shape-before-risk-interrupt and block on pre-existing siblings.)
#  - goal-closeout shape is owned at the achieve complete-flip (not a commit gate).
# See charness-artifacts/spec/authoring-preflight-generalization-and-disposition-delaunder.md
# and charness-artifacts/spec/artifact-shape-preflight-coverage.md.
REGISTRY: tuple[Surface, ...] = (
    Surface(
        "critique", "charness-artifacts/critique/",
        "scripts/validate_critique_artifacts.py",
        "skills/public/critique/scripts/scaffold_critique_artifact.py",
        None, True,
        "Hand-authored critique record; `## Reviewer Tier Evidence` + `## Structured Findings` enforced when present.",
    ),
    Surface(
        "ideation", "charness-artifacts/ideation/",
        "scripts/validate_ideation_artifact.py",
        "skills/public/ideation/scripts/scaffold_ideation_artifact.py",
        None, True,
        "Hand-authored ideation record; `## Structured Questions` enforced when present.",
    ),
    Surface(
        "retro", "charness-artifacts/retro/",
        "scripts/validate_retro_artifact.py",
        "skills/public/retro/scripts/scaffold_retro_artifact.py",
        None, True,
        "Hand-authored session retro; `## Next Improvements` disposition form enforced.",
    ),
    Surface(
        "goal-closeout", None, None, None,
        f"{_GOAL_TEMPLATE}|## Final Verification", False,
        "Goal `## Final Verification` closeout-evidence block; seeded by the goal template (no scaffold script).",
    ),
    Surface(
        "debug", "charness-artifacts/debug/",
        "scripts/validate_debug_artifact.py",
        "skills/public/debug/scripts/scaffold_debug_artifact.py",
        None, False,
        "Hand-authored debug artifact; required sections + seam-risk/interrupt prefixed values + cross-file sibling marker.",
        paths_arg=False,
    ),
    Surface(
        "quality", "charness-artifacts/quality/",
        "scripts/validate_quality_artifact.py",
        "skills/public/quality/scripts/scaffold_quality_artifact.py",
        None, False,
        "Hand-authored quality artifact; required sections + runtime-signal/delegated-review shape.",
        paths_arg=False,
    ),
    Surface(
        "handoff", "docs/handoff.md",
        "scripts/validate_handoff_artifact.py",
        "skills/public/handoff/scripts/scaffold_handoff_artifact.py",
        None, False,
        "Hand-authored handoff artifact (default docs/handoff.md); required H2 sections + a References link.",
        paths_arg=False,
    ),
)


def _resolve(repo_root: Path, raw: str) -> str:
    target = Path(raw)
    if not target.is_absolute():
        target = repo_root / target
    try:
        return target.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return Path(raw).as_posix()


def surface_for_path(rel: str) -> Surface | None:
    for surface in REGISTRY:
        if surface.prefix and rel.startswith(surface.prefix) and rel.endswith(".md"):
            if not surface.excludes(rel):
                return surface
    return None


def surface_for_type(artifact_type: str) -> Surface | None:
    return next((s for s in REGISTRY if s.artifact_type == artifact_type), None)


def _run(repo_root: Path, argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=repo_root, check=False, capture_output=True, text=True)


def _shape_text(repo_root: Path, surface: Surface) -> str:
    if surface.scaffold:
        proc = _run(repo_root, ["python3", surface.scaffold, "--repo-root", str(repo_root)])
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout
        return f"(could not render scaffold {surface.scaffold}: {proc.stderr.strip() or 'no output'})"
    if surface.template_section:
        tpl_rel, _, heading = surface.template_section.partition("|")
        tpl = repo_root / tpl_rel
        if tpl.is_file():
            return _extract_section(tpl.read_text(encoding="utf-8"), heading)
        return f"(template {tpl_rel} not found)"
    return "(no shape source registered)"


def _extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if line.strip() == heading:
            capturing = True
            out.append(line)
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            out.append(line)
    return "\n".join(out).rstrip() + "\n" if out else f"(section {heading} not found in template)"


def describe(repo_root: Path, surface: Surface, *, target_rel: str | None) -> str:
    out = [
        f"artifact-surface-preflight: {surface.artifact_type}",
        f"note: {surface.note}",
        "",
        "required shape (from the owning scaffold/template — the single source):",
        _shape_text(repo_root, surface).rstrip(),
        "",
    ]
    if surface.validator:
        # Adapter-scoped validators validate-all (no --paths); prefix validators
        # take --paths for a changed-scoped verdict.
        argv = ["python3", surface.validator, "--repo-root", str(repo_root)]
        cmd = f"python3 {surface.validator} --repo-root ."
        if surface.paths_arg and target_rel:
            argv += ["--paths", target_rel]
            cmd += f" --paths {target_rel}"
        out.append(f"owning validator: {cmd}")
        if target_rel and (repo_root / target_rel).is_file():
            proc = _run(repo_root, argv)
            verdict = "PASS" if proc.returncode == 0 else "FAIL"
            scope = target_rel if surface.paths_arg else f"{surface.artifact_type} surface (validate-all)"
            out.append(f"current verdict on {scope}: {verdict}")
            if proc.returncode != 0:
                out.append((proc.stderr or proc.stdout).strip())
    else:
        out.append("owning validator: achieve closeout (check_goal_artifact.py at the complete flip)")
    return "\n".join(out).rstrip() + "\n"


def emit_stub(repo_root: Path, surface: Surface) -> tuple[str, int]:
    if surface.scaffold:
        proc = _run(repo_root, ["python3", surface.scaffold, "--repo-root", str(repo_root)])
        if proc.returncode == 0:
            return proc.stdout, 0
        return (proc.stderr or proc.stdout), 1
    return (
        f"{surface.artifact_type} has no scaffold script; its shape is seeded by "
        f"{surface.template_section.split('|')[0]} — author into that block directly.\n"
    ), 0


def changed_artifacts(repo_root: Path, paths: list[str]) -> dict[str, Any]:
    """Commit-boundary arm: relocate each owning validator's verdict earlier.

    Groups changed artifacts by owning commit-boundary surface and runs each
    validator on its changed paths. Same validator, same verdict — only earlier.
    Only `commit_boundary` surfaces are processed, and those are all changed-scoped
    (`paths_arg=True`); validate-all surfaces are author-time-only (not here),
    because a validate-all gate in the fail-fast sweep would reorder the deeper
    closeout stages and block on pre-existing siblings.
    """
    groups: dict[str, tuple[Surface, list[str]]] = {}
    for raw in paths:
        rel = Path(raw).as_posix()
        surface = surface_for_path(rel)
        if surface is None or not surface.commit_boundary or surface.validator is None:
            continue
        groups.setdefault(surface.artifact_type, (surface, []))[1].append(rel)
    results: list[dict[str, Any]] = []
    for artifact_type in sorted(groups):
        surface, group = groups[artifact_type]
        proc = _run(repo_root, ["python3", surface.validator, "--repo-root", str(repo_root), "--paths", *sorted(group)])
        results.append({
            "artifact_type": artifact_type,
            "validator": surface.validator,
            "paths": sorted(group),
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        })
    blocked = [r["validator"] for r in results if r["returncode"] != 0]
    return {"status": "blocked" if blocked else "ok", "blocked": blocked, "checked": results}


def _format_changed(report: dict[str, Any]) -> str:
    lines = [f"artifact-shape-preflight: {report['status']}"]
    for row in report["checked"]:
        verdict = "BLOCK" if row["returncode"] != 0 else "ok"
        lines.append(f"- {row['validator']} on {len(row['paths'])} changed artifact(s) [{verdict}]")
        if row["returncode"] != 0:
            detail = (row["stderr"] or row["stdout"]).strip()
            if detail:
                lines.append(detail)
    if report["status"] == "blocked":
        lines.append(
            "An artifact's owning validator failed at the commit boundary (relocated "
            "from the broad gate). Fix the required shape — run "
            "`python3 scripts/check_artifact_surface_preflight.py --path <artifact>` to see it."
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--path", help="Artifact path to surface required shape for")
    parser.add_argument("--type", dest="artifact_type", help="Artifact type (see the registry)")
    parser.add_argument("--emit-stub", action="store_true", help="Emit a starter stub via the owning scaffold")
    parser.add_argument("--changed-artifacts", nargs="*", help="Commit-boundary: relocate owning validator verdicts for these paths")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    if args.changed_artifacts is not None:
        report = changed_artifacts(repo_root, args.changed_artifacts)
        print(json.dumps(report, indent=2, sort_keys=True) if args.json else _format_changed(report))
        return 1 if report["status"] == "blocked" else 0

    target_rel = _resolve(repo_root, args.path) if args.path else None
    if args.artifact_type:
        surface = surface_for_type(args.artifact_type)
    elif target_rel:
        surface = surface_for_path(target_rel)
    else:
        parser.error("one of --path, --type, or --changed-artifacts is required")
    if surface is None:
        known = ", ".join(s.artifact_type for s in REGISTRY)
        print(f"artifact-surface-preflight: no registered surface for {args.artifact_type or target_rel}; known: {known}", file=sys.stderr)
        return 2

    if args.emit_stub:
        text, code = emit_stub(repo_root, surface)
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
        return code
    print(describe(repo_root, surface, target_rel=target_rel), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
