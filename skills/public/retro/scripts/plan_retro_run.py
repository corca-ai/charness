#!/usr/bin/env python3
"""Plan a retro run before gathering evidence and writing the artifact.

Owns the classify/brief decisions that used to live only in SKILL.md prose plus
the generic scaffold stub: select the mode (session/weekly), classify the work
under review, and emit the fitting counterfactual lens brief as a deterministic
`required_read` so the run reaches `references/expert-lens.md` at the point of
need instead of relying on prose discipline. The scaffold stays the pure
template emitter; this planner is the briefing surface, matching the debug /
handoff / quality / issue / gather / release planner family.
"""

from __future__ import annotations

import argparse
import json
import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# Path prefixes whose change means the work under review is the harness improving
# itself (skill/workflow/eval/contract code), where expert-lens.md's non-inlined
# Engelbart `system-improving-itself` lens is the on-the-nose fit. charness-artifacts/
# is deliberately excluded: it is memory/output, not system code.
SYSTEM_IMPROVING_PREFIXES = (
    "skills/",
    "evals/",
    "scripts/",
    "docs/conventions/",
    ".agents/",
    ".githooks/",
    "plugins/",
    ".claude-plugin/",
    "AGENTS.md",
    "CLAUDE.md",
)
MAX_RECENT_COMMITS = 5
WEEKLY_HINTS = ("weekly", "this week", "sprint", "recent pattern", "주간", "이번 주", "한 주")

ON_DEMAND_REFERENCE_READS = (
    ("references/mode-guide.md", "for the full session/weekly selection and per-mode evidence bias beyond the inlined rule"),
    ("references/section-guide.md", "for claim-strength tags, the gate-baseline-runtime rule, and per-decision fields"),
    ("references/phase-aware-efficiency.md", "before token, tool-call, broad-exploration, or efficiency waste claims"),
    ("references/waste-sibling-scan.md", "when a lesson names a transferable waste pattern (opt-in Sibling Search)"),
    ("references/trigger-and-persistence.md", "for the full auto-trigger/skip taxonomy beyond the inlined Persisted rule"),
    ("references/prepare-packet.md", "when the adapter declares packet_sections and a prepare packet is produced"),
)


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
scaffold_retro_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "scaffold_retro_artifact")
surfaces_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.surfaces_lib")
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)


def _read(path: str, kind: str, why: str, *, base: str) -> dict[str, str]:
    return ENVELOPE.read(path, why, kind=kind, base=base)


_packet = ENVELOPE.gate_packet


def _relative_script_command(repo_root: Path, rel_path: str, *args: str) -> dict[str, Any]:
    return {
        "command": " ".join(["python3", rel_path, *args]),
        "available": (repo_root / rel_path).is_file(),
        "path": rel_path,
    }


def _recent_commit_paths(repo_root: Path, limit: int) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "log", f"-n{limit}", "--name-only", "--pretty=format:"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except (OSError, ValueError):
        return []
    if result.returncode != 0:
        return []
    ordered: list[str] = []
    for line in result.stdout.splitlines():
        candidate = line.strip()
        if candidate and candidate not in ordered:
            ordered.append(candidate)
    return ordered


def _work_paths(repo_root: Path, override: list[str] | None) -> tuple[list[str], str]:
    """The slice under review: explicit override, else uncommitted work, else recent commits.

    A capture runs on a clean worktree at a ref (no uncommitted changes), so the
    recent-commit fallback is what carries the just-finished work into the plan.
    """
    if override is not None:
        return override, "explicit_paths"
    try:
        working = list(surfaces_lib.collect_changed_paths(repo_root))
    except Exception:
        working = []
    if working:
        return working, "working_tree_diff"
    return _recent_commit_paths(repo_root, MAX_RECENT_COMMITS), "recent_commits"


def _classify_work_class(paths: list[str]) -> str:
    if not paths:
        return "unknown"
    if any(path.startswith(SYSTEM_IMPROVING_PREFIXES) for path in paths):
        return "system-improving"
    if all(path.startswith("docs/") for path in paths):
        return "docs"
    return "ordinary"


def _lens_brief(work_class: str) -> dict[str, str]:
    if work_class == "system-improving":
        fitting = (
            "Engelbart (system-improving-itself): treat (H + LAM + T) as one unit — "
            "design the tool/automation (T) alongside the method/language (LAM)."
        )
        why = (
            "the slice changes harness/skill/workflow/eval/contract surfaces, so the "
            "on-the-nose counterfactual is the Engelbart system-improving lens — which "
            "lives ONLY in expert-lens.md (not inlined in SKILL.md). Open it and apply it."
        )
    elif work_class == "docs":
        fitting = "a narrative/clarity lens (reader-first framing) plus one decision-quality lens."
        why = "the slice is documentation; match it to a fitting clarity + decision lens from the catalog."
    else:
        fitting = (
            "Default Pattern: one domain lens + one decision-quality / operating-discipline lens "
            "(catalog: Ousterhout/Majors, Fournier/Grove, Klein/Kahneman)."
        )
        why = (
            "match the work domain to a fitting lens from the expert-lens.md catalog; prefer the "
            "direct lens when a name adds nothing."
        )
    return {"work_class": work_class, "fitting_lens": fitting, "why": why}


def _select_mode(adapter: dict[str, Any], invocation_text: str) -> tuple[str, str]:
    default_mode = str(adapter["data"].get("default_mode", "session"))
    text = invocation_text.lower()
    if any(hint in text for hint in WEEKLY_HINTS):
        return "weekly", "weekly wording in invocation"
    if any(token in text for token in ("this session", "this task", "what just happened", "방금", "이번 세션")):
        return "session", "session wording in invocation"
    return default_mode, "adapter default_mode"


def _artifact_summary(repo_root: Path, scaffold: dict[str, Any]) -> dict[str, Any]:
    write_rel = str(scaffold["write_artifact_path"])
    write_path = repo_root / write_rel
    exists = write_path.is_file()
    line_count = len(write_path.read_text(encoding="utf-8").splitlines()) if exists else 0
    return {
        "path": write_rel,
        "exists": exists,
        "line_count": line_count,
        "status": "today_artifact_exists" if exists else "missing",
        "role": scaffold["artifact_role"],
    }


def _required_reads(
    *,
    repo_root: Path,
    adapter: dict[str, Any],
    artifact: dict[str, Any],
    mode: str,
    lens_brief: dict[str, str],
) -> list[dict[str, str]]:
    reads: list[dict[str, str]] = []
    reads.append(_read("docs/handoff.md", "artifact", "current workflow trigger and pickup state", base="repo"))

    # The counterfactual is mandatory in every retro and the lens catalog + domain
    # triggers are not inlined in SKILL.md, so expert-lens.md is an unconditional
    # floor. The why carries the work-class-specific lens brief.
    reads.append(_read("references/expert-lens.md", "reference", lens_brief["why"], base="skill"))

    if artifact["exists"]:
        reads.append(_read(artifact["path"], "artifact", "today's retro already started; continue it", base="repo"))
    else:
        reads.append(_read("scripts/scaffold_retro_artifact.py", "script", "no retro artifact yet; scaffold before writing", base="skill"))

    if not adapter.get("found") or not adapter.get("valid") or adapter.get("errors"):
        reads.append(_read("references/adapter-contract.md", "reference", "adapter is missing or invalid; repair before relying on adapter paths", base="skill"))

    if mode == "weekly":
        reads.append(_read("references/weekly-trends.md", "reference", "weekly Trends vs Last Retro and closeout-telemetry mining", base="skill"))
        summary_path = str(adapter["data"].get("summary_path") or "")
        if summary_path and (repo_root / summary_path).is_file():
            reads.append(_read(summary_path, "artifact", "recent-lessons digest to compare the weekly window against", base="repo"))
    return reads


def _on_demand_reads() -> list[dict[str, str]]:
    return [_read(path, "reference", why, base="skill") for path, why in ON_DEMAND_REFERENCE_READS]


def _gate_packets(repo_root: Path, adapter: dict[str, Any], scaffold: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _packet(
            "adapter-readiness",
            "deterministic adapter parser; trust failures and warnings",
            status="pass" if adapter.get("valid") else "fail",
            path=adapter.get("path"),
            warnings=adapter.get("warnings", []),
            errors=adapter.get("errors", []),
        ),
        _packet(
            "retro-artifact-scaffold",
            "deterministic scaffold payload; trust write target and validator command",
            command="python3 $SKILL_DIR/scripts/scaffold_retro_artifact.py --repo-root . --json",
            write_artifact_path=scaffold["write_artifact_path"],
            validator_command=scaffold["validator_command"],
        ),
        _packet(
            "retro-artifact-shape",
            "deterministic Sibling Search follow-up grammar gate; trust section/format failures",
            **_relative_script_command(repo_root, "scripts/validate_retro_artifact.py", "--repo-root", "."),
        ),
        _packet(
            "auto-session-trigger",
            "deterministic slice-surface trigger probe; agent judges whether to fire a bounded session retro",
            **_relative_script_command(repo_root, "skills/public/retro/scripts/check_auto_trigger.py", "--repo-root", "."),
        ),
    ]


def _next_action(artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact["exists"]:
        return {
            "kind": "continue-existing-retro",
            "instruction": "read today's retro artifact, then continue from the planned mode and lens brief",
            "artifact_path": artifact["path"],
        }
    return {
        "kind": "scaffold-retro-artifact",
        "command": "python3 $SKILL_DIR/scripts/scaffold_retro_artifact.py --repo-root . --json",
        "instruction": "open the required_reads (incl. expert-lens.md for the briefed lens), scaffold the artifact, then write the retro",
        "write_artifact_path": artifact["path"],
    }


def build_plan(
    repo_root: Path,
    *,
    invocation_text: str = "",
    changed_paths: list[str] | None = None,
) -> dict[str, Any]:
    adapter = resolve_adapter.load_adapter(repo_root)
    scaffold = scaffold_retro_artifact.payload_for(repo_root, title=None)
    artifact = _artifact_summary(repo_root, scaffold)
    mode, mode_reason = _select_mode(adapter, invocation_text)
    work_paths, work_paths_source = _work_paths(repo_root, changed_paths)
    work_class = _classify_work_class(work_paths)
    lens_brief = _lens_brief(work_class)
    return ENVELOPE.build_envelope(
        schema_version="retro.run_plan.v1",
        required_reads=_required_reads(
            repo_root=repo_root, adapter=adapter, artifact=artifact, mode=mode, lens_brief=lens_brief
        ),
        next_action=_next_action(artifact),
        gate_packets=_gate_packets(repo_root, adapter, scaffold),
        ok=bool(adapter.get("valid")),
        repo_root=str(repo_root),
        mode=mode,
        mode_reason=mode_reason,
        work_class=work_class,
        work_paths_source=work_paths_source,
        lens_brief=lens_brief,
        adapter=ENVELOPE.adapter_echo(adapter),
        artifact=artifact,
        on_demand_reads=_on_demand_reads(),
        phase_barriers=[
            "Open required_reads (esp. expert-lens.md for the briefed lens) before writing the retro.",
            "Treat gate_packets as cheap deterministic evidence: trust them for shape, not for judgment.",
            "Never close without a Persisted: yes/no line.",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a retro run before gathering evidence and writing the artifact.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--invocation-text", default="", help="The user's retro request, used to select session vs weekly mode")
    parser.add_argument("--changed-paths", nargs="*", help="Explicit paths for work-class classification (defaults to working tree, then recent commits)")
    parser.add_argument("--json", action="store_true", help="Emit JSON; accepted for parity with other planners")
    args = parser.parse_args()
    payload = build_plan(
        args.repo_root.resolve(),
        invocation_text=args.invocation_text,
        changed_paths=args.changed_paths,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
