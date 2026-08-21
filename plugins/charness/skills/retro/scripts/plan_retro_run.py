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

ON_DEMAND_REFERENCE_READS = (
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


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_RUNTIME = _load_skill_runtime_bootstrap()
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
scaffold_retro_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "scaffold_retro_artifact")
surfaces_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.surfaces_lib")
_state = SKILL_RUNTIME.load_local_skill_module(__file__, "retro_artifact_state")
_artifact_summary = _state._artifact_summary
_gate_builder = SKILL_RUNTIME.load_local_skill_module(__file__, "retro_plan_gates")
_trigger = SKILL_RUNTIME.load_local_skill_module(__file__, "retro_plan_trigger")
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)


def _read(path: str, kind: str, why: str, *, base: str) -> dict[str, str]:
    return ENVELOPE.read(path, why, kind=kind, base=base)


def _repo_evidence_read(repo_root: Path, path: str) -> dict[str, Any]:
    """Describe optional adapter evidence without pretending directories are files.

    Availability and path KIND only. This function used to stat and disclose a
    measurement itself; layering the shared `measure_reads` over that produced an
    item carrying BOTH `size_bytes` and an `unavailable_reason` whenever the two
    resolvers disagreed -- an adapter naming an evidence path outside the repo root
    made the whole planner raise instead of planning. One measurer, at the envelope.
    Found by a bounded round-1 reviewer of the read-measurement mandate.
    """
    item: dict[str, Any] = _read(
        path,
        "evidence",
        "adapter-declared local evidence; inspect when available, then apply its repo-owned contract",
        base="repo",
    )
    candidate = repo_root / path
    item["available"] = candidate.exists()
    item["path_kind"] = "directory" if candidate.is_dir() else "file" if candidate.is_file() else "missing"
    return item


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


def _required_reads(
    *,
    repo_root: Path,
    adapter: dict[str, Any],
    artifact: dict[str, Any],
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

    # Gate-runtime waste is invisible to a passing gate by construction, and its
    # signal is recurrence across runs — which no single session can observe. It was
    # previously reachable only from `weekly`, a mode invoked once in three months,
    # so the stream accumulated 985 records that nothing read. Routed for every retro.
    reads.append(_read("references/closeout-telemetry.md", "reference", "recurring gate-runtime and artifact-only-commit waste the closeout stream already recorded", base="skill"))
    already_named = {str(item["path"]) for item in reads}
    for evidence_path in adapter["data"].get("evidence_paths", []):
        path = str(evidence_path)
        if path and path not in already_named:
            reads.append(_repo_evidence_read(repo_root, path))
            already_named.add(path)
    summary_path = str(adapter["data"].get("summary_path") or "")
    if summary_path and (repo_root / summary_path).is_file():
        reads.append(_read(summary_path, "artifact", "recent-lessons digest to compare this retro's window against", base="repo"))
    return reads


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
        return {**fallback, "available": False, "unavailable_reason": f"{type(exc).__name__}: {exc}"}


def _date_activated_rules(repo_root: Path) -> dict[str, Any]:
    """Announce the retro floors that switch on by artifact date.

    These dates were reachable only by tripping them, so an author whose previous
    retro needed no `## Lesson Evaluation` section read the new refusal as
    breakage rather than as a dated floor that had just activated. The achieve
    planner family already emits `rule_date` in every report payload; this does
    the same, reading the validator's own constants so the announcement cannot
    drift from the rule it announces.
    """
    return _repo_module_payload(
        "scripts.validate_retro_artifact",
        lambda validator: {"rules": validator.date_activated_rules(repo_root)},
        fallback={"rules": []},
    )


def _lesson_session(repo_root: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    """Route this retro to the declared lesson session that still owes it a score.

    The evaluating half of the lesson lifecycle had zero production callers: a
    session could be declared and receipted and then nothing ever told the retro
    author it existed, so every disposition in this repo was `not-evaluated /
    missing-start` while the continuity gate reported `violations=0` over it.

    The three states are the shared `lesson_evaluation_records_lib` verdict, not a
    second implementation — `unclaimed_receipted_sessions` is the same helper the
    continuity gate turns into `unclaimed-emission`, so the router cannot route to
    a session the gate does not see, or skip one it does. When the planner cannot
    load the module at all the answer is `not-established`, never `not-configured`:
    an unreadable probe has not established that this repo opted out.
    """
    return _repo_module_payload(
        "scripts.lesson_evaluation_records_lib",
        lambda records: records.lesson_session_routing(repo_root, source_retro=artifact["path"]),
        fallback={"state": "not-established", "configuration_status": "planner-cannot-read", "sessions": []},
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
    auto_trigger_args, auto_trigger_scope = _trigger.auto_trigger_scope(work_paths, work_paths_source)
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
    # Hoisted so a barrier can be conditioned on it. A barrier that names
    # `lesson_session[].solicitation` in a repo with no evaluator points at keys
    # that payload does not carry -- the "names a path nothing creates" defect this
    # planner's own lesson-routing module cites as its motivation.
    lesson_session = _lesson_session(repo_root, artifact)
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
        lesson_session=lesson_session,
        phase_barriers=[
            "Open required_reads (esp. expert-lens.md for the briefed lens) before writing the retro.",
            "Read date_activated_rules before concluding a floor is broken: a section your last "
            "retro did not need may be a dated floor that activated since, and the lesson-evaluation "
            "floor is inert entirely in a repo that declares no lesson evaluator.",
            "If repo-owned evidence defines lesson evaluation, score only a list presented contemporaneously before the work; write the exact repo-owned disposition, then run its adapter metric after persistence. A stored snapshot or command receipt alone is not presentation.",
            "Read `lesson_session` and keep its order: append every score FIRST, then write the "
            "disposition line, then run the reconciler after persistence. The disposition declares "
            "the score count, so it is the assertion ABOUT the appends and can never drive them; "
            "`state: not-established` means the only honest disposition is the `honest_disposition` "
            "it names, and `state: not-configured` means the floor is inert.",
            *(
                [
                    "When `lesson_session.sessions[]` carries a `solicitation`, answer it against that "
                    "session's own `lessons` before deciding the disposition, and answer its "
                    "harmful/negative question first and out loud. The evaluator owns what the "
                    "answers mean; do not restate its scoring rules from memory."
                ]
                if lesson_session.get("sessions")
                else []
            ),
            "Treat gate_packets as cheap deterministic evidence: trust them for shape, not for judgment.",
            "Never close without a Persisted: yes/no line.",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a retro run before gathering evidence and writing the artifact.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used to resolve adapter state, artifacts, and changed paths.",
    )
    parser.add_argument("--changed-paths", nargs="*", help="Explicit paths for work-class classification (defaults to working tree, then recent commits)")
    args = parser.parse_args()
    payload = build_plan(
        args.repo_root.resolve(),
                changed_paths=args.changed_paths,
    )
    yaml_output.emit_yaml(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
