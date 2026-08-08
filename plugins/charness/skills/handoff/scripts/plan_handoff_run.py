#!/usr/bin/env python3
"""Plan the first phase of a handoff run before reading broadly or writing."""

from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

INTENT_REFERENCE_READS = {
    "chunked_routing": (
        ("references/chunked-routing.md", "deterministic trigger says route backlog before pickup"),
    ),
    # workflow-trigger.md retired from the forced pickup reads (census INLINE):
    # its trigger-first gist is inlined in SKILL.md (step 2 authoritative-trigger
    # rule, step 5 keep-the-trigger-explicit, the session-open guardrail), and
    # the live trigger TEXT lives in the artifact's `## Workflow Trigger`
    # section, which the planner already forces as the first required read.
    # Forcing the reference re-read was the redundant doc-open proxy this
    # compaction retires; the honest pickup floor is the substance judge
    # (evals/cautilus/handoff-claim-fidelity/outcome-assertions.json). It STAYS
    # forced for judge_from_user_request (deciding pickup-vs-refresh is a
    # different, still-load-bearing purpose).
    "pickup": (
        ("references/continuation-sequence.md", "order the next move as continuation, not history"),
    ),
    "refresh": (
        # state-selection.md retired from the forced refresh reads (census
        # INLINE): the Compression Rule gist is inlined in SKILL.md (step 2,
        # step 4 keep-enumeration, guardrails), so the run keeps only
        # next-action state from core and the eval floors on the emitted
        # `Refresh kept:`/`Refresh non-claims:` closeout tokens instead of the
        # redundant re-read. spill-targets.md stays a forced read: its exact
        # owning-path routing table is genuine depth absent from SKILL.md.
        ("references/spill-targets.md", "spill durable detail instead of growing a diary"),
    ),
    "judge_from_user_request": (
        ("references/workflow-trigger.md", "decide whether this is pickup or refresh"),
        ("references/state-selection.md", "avoid carrying stale or non-actionable state"),
    ),
}


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
chunked_routing_lib = SKILL_RUNTIME.load_local_skill_module(
    __file__, "chunked_routing_lib"
)
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)

# The canonical sections and the content-line counting rule are single-sourced
# from the skill-local budget module, so planner diagnosis cannot disagree with
# the gate about WHICH lines count. The enforced ceiling still comes from the
# validator when it is loadable (that is the number the gate actually applies);
# a portable install without scripts/ degrades to the module default — floor-
# addition-restraint: this is diagnosis only, never a new blocking floor.
_budget = SKILL_RUNTIME.load_local_skill_module(__file__, "handoff_content_budget")
content_lines = _budget.content_lines
REQUIRED_SECTIONS, OPTIONAL_SECTIONS = _budget.REQUIRED_SECTIONS, _budget.OPTIONAL_SECTIONS
try:
    _handoff_validator = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.validate_handoff_artifact")
    MAX_CONTENT_LINES = int(_handoff_validator.MAX_CONTENT_LINES)
except Exception:
    MAX_CONTENT_LINES = _budget.DEFAULT_MAX_CONTENT_LINES
# "near" = within 8 content lines of the ceiling: enough room to add a fact, not
# enough to add a section, which is the point at which a refresh should prune.
NEAR_LIMIT_LINES = MAX_CONTENT_LINES - 8


def _relative_script_command(repo_root: Path, rel_path: str, *args: str) -> dict[str, Any]:
    path = repo_root / rel_path
    command = " ".join(["python3", rel_path, *args])
    return {
        "command": command,
        "available": path.is_file(),
        "path": rel_path,
    }


def _read(path: str, kind: str, why: str, *, base: str) -> dict[str, str]:
    return ENVELOPE.read(path, why, kind=kind, base=base)


def _packet(
    packet_id: str,
    trust_model: str,
    gate: dict[str, Any],
    *,
    cost_tier: str = "cheap",
) -> dict[str, Any]:
    return ENVELOPE.gate_packet(packet_id, trust_model, cost_tier=cost_tier, **gate)


def _artifact_summary(repo_root: Path, adapter: dict[str, Any]) -> dict[str, Any]:
    rel_path = str(adapter["artifact_path"])
    path = repo_root / rel_path
    if not path.is_file():
        return {
            "path": rel_path,
            "exists": False,
            "line_count": 0,
            "content_line_count": 0,
            "status": "missing",
            "dated_session_sections": 0,
            "missing_sections": list(REQUIRED_SECTIONS),
            "extra_h2_sections": [],
        }

    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    try:
        # Actionable `## Next Session` entries = plausible pickups. Used only to
        # decide whether a pickup is ambiguous enough to need continuation-sequence.md;
        # open-issue union is intentionally omitted here to keep the planner
        # deterministic and tracker-independent.
        next_session_entry_count = len(chunked_routing_lib.parse_handoff_entries(raw))
    except Exception:
        next_session_entry_count = 0
    h2_sections = [line.strip() for line in lines if line.startswith("## ")]
    missing = [section for section in REQUIRED_SECTIONS if section not in h2_sections]
    extra = [section for section in h2_sections if section not in _budget.CANONICAL_SECTIONS]
    dated_sessions = sum(1 for line in h2_sections if line.startswith("## This Session ("))
    # Budget counts content, not file length (see handoff_content_budget).
    content_line_count = len(content_lines(lines))
    if content_line_count > MAX_CONTENT_LINES:
        status = "over_limit"
    elif dated_sessions:
        status = "diary_smell"
    elif missing or extra:
        status = "shape_issue"
    elif content_line_count >= NEAR_LIMIT_LINES:
        status = "near_limit"
    else:
        status = "ok"
    return {
        "path": rel_path,
        "exists": True,
        "line_count": len(lines),
        "content_line_count": content_line_count,
        "status": status,
        "dated_session_sections": dated_sessions,
        "missing_sections": missing,
        "extra_h2_sections": extra,
        "next_session_entry_count": next_session_entry_count,
    }


def _pickup_needs_continuation_sequence(artifact: dict[str, Any], pickup_target: str) -> bool:
    """continuation-sequence.md orders the next move among SEVERAL plausible pickups.
    A pickup needs it only when the pickup is ambiguous: the caller did not DECLARE
    which task is being picked up AND the live state offers more than one plausible
    pickup. This aligns the planner with the skill's own 'when several plausible
    pickups exist' scope."""
    if pickup_target.strip():
        return False
    return artifact.get("next_session_entry_count", 0) >= 2


def _resolve_intent(*, requested: str, invoked_directly: bool) -> dict[str, Any]:
    """Resolve routing from what the caller DECLARED, never from the invocation text.

    Python is not in the conversation, so a classifier here could only ever read
    the agent's retyping of the user's message — a judgment laundered through a
    regex and reported as machine-decided. The agent declares it instead, where
    the user can see and argue with it. `--invoked-directly` survives because it
    is a structural fact about the launch, not a reading of prose.
    `references/chunked-routing.md` owns the rule the agent applies.
    """
    if requested != "auto":
        return {"requested": requested, "resolved": requested, "reason": "explicit --intent"}
    if invoked_directly:
        return {
            "requested": requested,
            "resolved": "chunked_routing",
            "reason": "declared bare skill invocation with no task (--invoked-directly)",
        }
    return {
        "requested": requested,
        "resolved": "judge_from_user_request",
        "reason": "no declared intent; judge the user request, then re-run with --intent",
    }


# The next actions that AUTHOR the artifact by hand. `scaffold_missing_artifact`
# is deliberately absent: a generator writes that file, not an author.
WRITING_ACTIONS = frozenset({"refresh_handoff", "repair_or_prune_handoff", "run_chunked_routing"})


def _authoring_rules_read(repo_root: Path, artifact_path: str) -> dict[str, str] | None:
    """The deterministic constraints on the artifact, as a READ before authoring.

    The forecast rode only as a `gate_packets` entry — evidence to run against
    something already written — so an author met the rules by breaking one. This
    is the rules mode, which answers with no target. The content check stays a
    gate packet: different question, same surface.
    """
    rel = "scripts/check_doc_authoring_preflight.py"
    # Probe BOTH files the emitted command needs. The rules mode (no `--path`)
    # imports `scripts/doc_authoring_rules.py` at runtime, so probing only the
    # entrypoint emits a command that dies on import in a partially vendored
    # repo -- and the read would still be reported as available.
    for required in (rel, "scripts/doc_authoring_rules.py"):
        if not (repo_root / required).is_file():
            return None
    surface = "handoff" if artifact_path.endswith("handoff.md") else None
    command = f"python3 {rel} --repo-root ." + (f" --as-surface {surface}" if surface else "")
    return {
        **_read(rel, "preflight", "deterministic rules for this surface BEFORE writing into it", base="repo"),
        "command": command,
    }


def _required_reads(
    *,
    repo_root: Path,
    artifact: dict[str, Any],
    intent: dict[str, Any],
    adapter: dict[str, Any],
    pickup_target: str,
    action_kind: str,
) -> list[dict[str, str]]:
    reads: list[dict[str, str]] = []
    if artifact["exists"]:
        reads.append(
            _read(
                str(artifact["path"]),
                "artifact",
                "current handoff state and workflow trigger",
                base="repo",
            )
        )
    else:
        reads.append(
            _read(
                "scripts/scaffold_handoff_artifact.py",
                "script",
                "artifact is missing; scaffold before refresh",
                base="skill",
            )
        )

    if not adapter.get("found") or adapter.get("warnings") or adapter.get("errors"):
        reads.append(
            _read(
                "references/adapter-contract.md",
                "reference",
                "adapter was missing, warned, or invalid",
                base="skill",
            )
        )

    # A run that WRITES the artifact owes the rules first, and the next action is
    # what says whether it writes — not the intent. A PICKUP against a bloated or
    # mis-shaped artifact is sent to prune it, which is authoring; keying this on
    # the intent left that one case briefed by nothing.
    if action_kind in WRITING_ACTIONS:
        rules_read = _authoring_rules_read(repo_root, str(artifact["path"]))
        if rules_read is not None:
            reads.append(rules_read)

    pickup_skip_continuation = (
        intent["resolved"] == "pickup"
        and not _pickup_needs_continuation_sequence(artifact, pickup_target)
    )
    for path, why in INTENT_REFERENCE_READS.get(
        intent["resolved"],
        INTENT_REFERENCE_READS["judge_from_user_request"],
    ):
        if pickup_skip_continuation and path == "references/continuation-sequence.md":
            # Unambiguous pickup: one clearly-pinned task or a single plausible
            # pickup — no sequencing among alternatives is needed, so the planner
            # does not force continuation-sequence.md (which scopes itself to
            # "when several plausible pickups exist").
            continue
        reads.append(_read(path, "reference", why, base="skill"))
    return reads


def _gate_packets(repo_root: Path, artifact_path: str) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    gate_defs = (
        (
            "handoff-artifact-shape",
            "deterministic shape, size, section, and reference-link gate",
            _relative_script_command(repo_root, "scripts/validate_handoff_artifact.py", "--repo-root", "."),
            True,
        ),
        (
            "current-pointer-freshness",
            "deterministic stale rolling-pointer claim gate",
            _relative_script_command(repo_root, "scripts/validate_current_pointer_freshness.py", "--repo-root", "."),
            False,
        ),
        (
            "doc-authoring-preflight",
            "deterministic markdown authoring preflight",
            _relative_script_command(repo_root, "scripts/check_doc_authoring_preflight.py", "--path", artifact_path),
            False,
        ),
    )
    for packet_id, trust_model, gate, always_include in gate_defs:
        if always_include or gate["available"]:
            packets.append(_packet(packet_id, trust_model, gate))
    return packets


def _next_action(
    *,
    artifact: dict[str, Any],
    intent: dict[str, Any],
    artifact_path: str,
) -> dict[str, str]:
    resolved = intent["resolved"]
    if not artifact["exists"]:
        return ENVELOPE.next_action(
            "scaffold_missing_artifact",
            command='python3 "$SKILL_DIR/scripts/scaffold_handoff_artifact.py" --repo-root .',
            why="the adapter-resolved handoff artifact is missing")
    if resolved == "judge_from_user_request":
        # An undeclared run must not be steered anywhere. Falling through to the
        # refresh branch would make the planner guess again, unconditionally and
        # on the writing side, which is the defect this planner was repaired to
        # stop making.
        return ENVELOPE.next_action(
            "judge_the_user_request",
            command='python3 "$SKILL_DIR/scripts/plan_handoff_run.py" --repo-root . --intent <chunked_routing|pickup|refresh>',
            why="no route was declared; decide from the user request, then re-run declaring it")
    if resolved == "chunked_routing":
        return ENVELOPE.next_action(
            "run_chunked_routing",
            command='python3 "$SKILL_DIR/scripts/parse_handoff_entries.py" --repo-root . --with-issues',
            why="start the chunked-routing pipeline, then follow the reference")
    if artifact["status"] in {"over_limit", "shape_issue", "diary_smell", "near_limit"}:
        return ENVELOPE.next_action(
            "repair_or_prune_handoff",
            command=f"sed -n '1,220p' {artifact_path}",
            why=f"artifact status is {artifact['status']}")
    if resolved == "pickup":
        return ENVELOPE.next_action(
            "follow_workflow_trigger",
            command=f"sed -n '1,80p' {artifact_path}",
            why="pickup should invoke the named workflow trigger first")
    return ENVELOPE.next_action(
        "refresh_handoff",
        command=f"sed -n '1,220p' {artifact_path}",
        why="inspect current handoff and live repo state before rewriting")


def build_plan(
    repo_root: Path,
    *,
    intent: str,
    invoked_directly: bool,
    pickup_target: str = "",
) -> dict[str, Any]:
    adapter = resolve_adapter.load_adapter(repo_root)
    artifact = _artifact_summary(repo_root, adapter)
    resolved_intent = _resolve_intent(requested=intent, invoked_directly=invoked_directly)
    artifact_path = str(artifact["path"])
    action = _next_action(artifact=artifact, intent=resolved_intent, artifact_path=artifact_path)
    return ENVELOPE.build_envelope(
        schema_version="handoff.run_plan.v1",
        required_reads=_required_reads(
            repo_root=repo_root,
            artifact=artifact,
            intent=resolved_intent,
            adapter=adapter,
            pickup_target=pickup_target,
            action_kind=str(action["kind"]),
        ),
        next_action=action,
        gate_packets=_gate_packets(repo_root, artifact_path),
        repo_root=str(repo_root),
        adapter={
            "artifact_path": artifact_path,
            "found": bool(adapter.get("found")),
            "valid": bool(adapter.get("valid")),
            "warnings": adapter.get("warnings", []),
            "errors": adapter.get("errors", []),
        },
        artifact=artifact,
        intent={
            **resolved_intent,
            "chunked_routing": {
                "should_run": resolved_intent["resolved"] == "chunked_routing",
                "invoked_directly": invoked_directly,
            },
        },
        phase_barriers=[
            "Read required_reads before opening broader docs or editing the artifact.",
            "Treat gate_packets as evidence packets: cheap deterministic gates can be trusted for shape, not for judgment.",
            "For chunked routing, write only at the end; for refresh, keep only facts that change the next action.",
        ],
    )


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff plan_handoff_run")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(),
                        help="Repository root used to resolve handoff adapter and artifact state.")
    parser.add_argument(
        "--intent",
        choices=("auto", "chunked_routing", "pickup", "refresh"),
        default="auto",
        help="Declare the routing decision you judged from the user request; auto only reads structural signals.",
    )
    parser.add_argument("--invoked-directly", action="store_true",
                        help="Declare that the skill was launched bare with no task, which routes to chunked routing.")
    parser.add_argument("--pickup-target", default="",
                        help="Name the one task being picked up when it is already settled; leave empty when it is not.")
    parser.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    try:
        args = parser.parse_args()
        plan = build_plan(
            args.repo_root.resolve(),
            intent=args.intent,
            invoked_directly=args.invoked_directly,
            pickup_target=args.pickup_target,
        )
        if args.json:
            print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            yaml_output.emit_yaml(plan)
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
