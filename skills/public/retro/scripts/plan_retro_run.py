#!/usr/bin/env python3
"""Plan a retro run before gathering evidence and writing the artifact.

Owns the classify/brief decisions that used to live only in SKILL.md prose plus
the generic scaffold stub: classify the work
under review, and emit the fitting counterfactual lens brief as a deterministic
`required_read` so the run reaches `references/expert-lens.md` at the point of
need instead of relying on prose discipline. The scaffold stays the pure
template emitter; this planner is the briefing surface, matching the debug /
handoff / quality / issue / gather / release planner family.
"""

from __future__ import annotations

import argparse
import runpy
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
    "docs/",
    ".agents/",
    ".githooks/",
    "plugins/",
    ".claude-plugin/",
    "AGENTS.md",
    "CLAUDE.md",
)
MAX_RECENT_COMMITS = 5

ON_DEMAND_REFERENCE_READS = (
    (
        "references/section-guide.md",
        "for claim-strength tags, the gate-baseline-runtime rule, and per-decision fields",
    ),
    (
        "references/phase-aware-efficiency.md",
        "before token, tool-call, broad-exploration, or efficiency waste claims",
    ),
    (
        "references/waste-sibling-scan.md",
        "when a lesson names a transferable waste pattern (opt-in Sibling Search)",
    ),
    (
        "references/trigger-and-persistence.md",
        "for the full auto-trigger/skip taxonomy beyond the inlined Persisted rule",
    ),
    (
        "references/prepare-packet.md",
        "when the adapter declares packet_sections and a prepare packet is produced",
    ),
)


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_RUNTIME = _load_skill_runtime_bootstrap()
subprocess = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.core.subprocess_guard"
).subprocess
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.core.subprocess_guard"
).run_process
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
scaffold_retro_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "scaffold_retro_artifact")
surfaces_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.surfaces_lib")
_state = SKILL_RUNTIME.load_local_skill_module(__file__, "retro_artifact_state")
_artifact_summary = _state._artifact_summary
_gate_builder = SKILL_RUNTIME.load_local_skill_module(__file__, "retro_plan_gates")
_trigger = SKILL_RUNTIME.load_local_skill_module(__file__, "retro_plan_trigger")
_READS = SKILL_RUNTIME.load_local_skill_module(__file__, "retro_plan_reads")
ENVELOPE = SimpleNamespace(
    **runpy.run_path(
        str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py")
    )
)


def _read(path: str, kind: str, why: str, *, base: str) -> dict[str, str]:
    return ENVELOPE.read(path, why, kind=kind, base=base)


def _repo_evidence_read(repo_root: Path, path: str) -> dict[str, Any]:
    return _READS.repo_evidence_read(repo_root, path, read=_read)


_packet = ENVELOPE.gate_packet


def _relative_script_command(repo_root: Path, rel_path: str, *args: str) -> dict[str, Any]:
    return {
        "command": " ".join(["python3", rel_path, *args]),
        "available": (repo_root / rel_path).is_file(),
        "path": rel_path,
    }


def _skill_script_command(rel_path: str, *args: str) -> dict[str, Any]:
    """Emit a command for a script shipped beside this planner.

    A planner runs both from ``skills/public/<skill>`` in the authoring tree and
    from ``skills/<skill>`` in the exported plugin.  A repository-relative path
    is therefore a source-only carrier; ``$SKILL_DIR`` is the portable owner.
    Availability is checked against the resolved skill package, not the consumer
    repository, so an installed plan cannot advertise its own probe as missing.
    """
    return {
        "command": " ".join(["python3", f'"$SKILL_DIR/{rel_path}"', *args]),
        "available": (SKILL_ROOT / rel_path).is_file(),
        "required": True,
        "path": rel_path,
        "path_base": "skill-dir",
    }


def _recent_commit_paths(repo_root: Path, limit: int) -> list[str]:
    try:
        result = run_process(
            ["git", "log", f"-n{limit}", "--name-only", "--pretty=format:"],
            cwd=repo_root,
            timeout_seconds=None,
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
    if all(path.startswith("docs/") for path in paths):
        return "docs"
    if any(path.startswith(SYSTEM_IMPROVING_PREFIXES) for path in paths):
        return "system-improving"
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


def _required_reads(
    *,
    repo_root: Path,
    adapter: dict[str, Any],
    artifact: dict[str, Any],
    lens_brief: dict[str, str],
) -> list[dict[str, str]]:
    return _READS.required_reads(
        repo_root=repo_root,
        adapter=adapter,
        artifact=artifact,
        lens_brief=lens_brief,
        read=_read,
    )


def _repo_module_payload(module_name: str, build, *, fallback: dict[str, Any]) -> dict[str, Any]:
    """Announce a repo-module-owned fact, or state plainly that it could not be produced.

    Loaded defensively, and the fallback is a REQUIRED argument rather than an
    empty dict: the planner runs in consuming repos and hosts whose layout need not
    expose the repo-root modules, and an announcement that cannot be produced must
    degrade to a stated unavailability carrying the same keys — never take the
    whole plan down with it, and never drop the key so a reader mistakes an absent
    announcement for a negative answer.
    """
    try:
        module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, module_name)
        return {**build(module), "available": True}
    except Exception as exc:  # host layout / import surface, never a verdict
        return {
            **fallback,
            "available": False,
            "unavailable_reason": f"{type(exc).__name__}: {exc}",
        }


def _date_activated_rules(repo_root: Path) -> dict[str, Any]:
    """Announce the generic retro floors that switch on by artifact date."""
    return _repo_module_payload(
        "scripts.validate_retro_artifact",
        lambda validator: {"rules": validator.date_activated_rules(repo_root)},
        fallback={"rules": []},
    )


def _on_demand_reads() -> list[dict[str, str]]:
    return [_read(path, "reference", why, base="skill") for path, why in ON_DEMAND_REFERENCE_READS]


def _next_action(artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact["exists"]:
        return {
            "kind": "continue-existing-retro",
            "instruction": "read today's retro artifact, then continue from the planned lens brief",
            "artifact_path": artifact["path"],
        }
    return {
        "kind": "scaffold-retro-artifact",
        "command": "python3 $SKILL_DIR/scripts/scaffold_retro_artifact.py --repo-root .",
        "instruction": "open the required_reads (incl. expert-lens.md for the briefed lens), scaffold the artifact, then write the retro",
        "write_artifact_path": artifact["path"],
    }


def build_plan(
    repo_root: Path,
    *,
    changed_paths: list[str] | None = None,
) -> dict[str, Any]:
    adapter = resolve_adapter.load_adapter(repo_root)
    scaffold = scaffold_retro_artifact.payload_for(repo_root, title=None)
    artifact = _artifact_summary(repo_root, scaffold)
    work_paths, work_paths_source = _work_paths(repo_root, changed_paths)
    work_class = _classify_work_class(work_paths)
    lens_brief = _lens_brief(work_class)
    artifact.update(
        scaffold_retro_artifact._scaffold_lib.write_target_facts(repo_root, artifact["path"])
    )
    auto_trigger_args, auto_trigger_scope = _trigger.auto_trigger_scope(
        work_paths, work_paths_source
    )
    gate_packets = _gate_builder.build_gate_packets(
        repo_root,
        adapter,
        scaffold,
        packet=_packet,
        relative_script_command=_relative_script_command,
        skill_script_command=_skill_script_command,
        auto_trigger_args=auto_trigger_args,
        auto_trigger_scope=auto_trigger_scope,
    )
    unavailable_required_packets = [
        packet["id"]
        for packet in gate_packets
        if packet.get("required") is True and packet.get("available") is False
    ]
    ready = bool(adapter.get("valid")) and not unavailable_required_packets
    return ENVELOPE.build_envelope(
        schema_version="retro.run_plan.v1",
        required_reads=ENVELOPE.measure_reads(
            _required_reads(
                repo_root=repo_root, adapter=adapter, artifact=artifact, lens_brief=lens_brief
            ),
            {"repo": repo_root, "skill": SKILL_ROOT},
        ),
        next_action=_next_action(artifact),
        gate_packets=gate_packets,
        ok=ready,
        readiness={
            "status": "ready" if ready else "not-ready",
            "blocking_packets": unavailable_required_packets,
            "adapter_valid": bool(adapter.get("valid")),
        },
        repo_root=str(repo_root),
        work_class=work_class,
        changed_paths=work_paths,
        work_paths_source=work_paths_source,
        trigger_scope=auto_trigger_scope["trigger_scope"],
        trigger_scope_source=auto_trigger_scope["trigger_scope_source"],
        trigger_scope_status=auto_trigger_scope.get("trigger_scope_status", "established"),
        lens_brief=lens_brief,
        adapter=ENVELOPE.adapter_echo(adapter),
        artifact=artifact,
        on_demand_reads=_on_demand_reads(),
        date_activated_rules=_date_activated_rules(repo_root),
        phase_barriers=[
            "Open required_reads (esp. expert-lens.md for the briefed lens) before writing the retro.",
            "Read date_activated_rules before concluding a generic floor is broken: a floor "
            "your last retro did not need may have activated since.",
            "Treat gate_packets as cheap deterministic evidence: trust them for shape, not for judgment.",
            "Never close without a Persisted: yes/no line.",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan a retro run before gathering evidence and writing the artifact."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used to resolve adapter state, artifacts, and changed paths.",
    )
    parser.add_argument(
        "--changed-paths",
        nargs="*",
        help="Explicit paths for work-class classification (defaults to working tree, then recent commits)",
    )
    args = parser.parse_args()
    payload = build_plan(
        args.repo_root.resolve(),
        changed_paths=args.changed_paths,
    )
    yaml_output.emit_yaml(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
