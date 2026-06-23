#!/usr/bin/env python3
"""Plan the first phase of a handoff run before reading broadly or writing."""

from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

MAX_ARTIFACT_LINES = 70
NEAR_LIMIT_LINES = 60
# floor-addition-restraint: this mirrors scripts/validate_handoff_artifact.py for
# planner diagnosis only; it does not add a new blocking floor.
REQUIRED_SECTIONS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
)
INTENT_REFERENCE_READS = {
    "chunked_routing": (
        ("references/chunked-routing.md", "deterministic trigger says route backlog before pickup"),
    ),
    "pickup": (
        ("references/workflow-trigger.md", "pickup starts from the named workflow trigger"),
        ("references/continuation-sequence.md", "order the next move as continuation, not history"),
    ),
    "refresh": (
        ("references/state-selection.md", "refresh keeps only state that changes the next action"),
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


def _relative_script_command(repo_root: Path, rel_path: str, *args: str) -> dict[str, Any]:
    path = repo_root / rel_path
    command = " ".join(["python3", rel_path, *args])
    return {
        "command": command,
        "available": path.is_file(),
        "path": rel_path,
    }


def _read(path: str, kind: str, why: str, *, base: str) -> dict[str, str]:
    return {"path": path, "kind": kind, "base": base, "why": why}


def _packet(
    packet_id: str,
    trust_model: str,
    gate: dict[str, Any],
    *,
    cost_tier: str = "cheap",
) -> dict[str, Any]:
    return {
        "id": packet_id,
        "trust_model": trust_model,
        "cost_tier": cost_tier,
        **gate,
    }


def _artifact_summary(repo_root: Path, adapter: dict[str, Any]) -> dict[str, Any]:
    rel_path = str(adapter["artifact_path"])
    path = repo_root / rel_path
    if not path.is_file():
        return {
            "path": rel_path,
            "exists": False,
            "line_count": 0,
            "status": "missing",
            "dated_session_sections": 0,
            "missing_sections": list(REQUIRED_SECTIONS),
            "extra_h2_sections": [],
        }

    lines = path.read_text(encoding="utf-8").splitlines()
    h2_sections = [line.strip() for line in lines if line.startswith("## ")]
    missing = [section for section in REQUIRED_SECTIONS if section not in h2_sections]
    extra = [section for section in h2_sections if section not in REQUIRED_SECTIONS]
    dated_sessions = sum(1 for line in h2_sections if line.startswith("## This Session ("))
    line_count = len(lines)
    if line_count > MAX_ARTIFACT_LINES:
        status = "over_limit"
    elif dated_sessions:
        status = "diary_smell"
    elif missing or extra:
        status = "shape_issue"
    elif line_count >= NEAR_LIMIT_LINES:
        status = "near_limit"
    else:
        status = "ok"
    return {
        "path": rel_path,
        "exists": True,
        "line_count": line_count,
        "status": status,
        "dated_session_sections": dated_sessions,
        "missing_sections": missing,
        "extra_h2_sections": extra,
    }


def _resolve_intent(
    *,
    requested: str,
    invocation_text: str,
    chunked_routing: bool,
) -> dict[str, Any]:
    lowered = invocation_text.lower()
    if requested != "auto":
        resolved = requested
        reason = "explicit --intent"
    elif chunked_routing:
        resolved = "chunked_routing"
        reason = "handoff mention/direct invocation with no task directive"
    elif any(token in lowered for token in ("refresh", "update", "prepare", "write")):
        resolved = "refresh"
        reason = "refresh/update wording in invocation"
    elif any(token in lowered for token in ("pickup", "pick up", "resume", "continue")):
        resolved = "pickup"
        reason = "pickup/resume wording in invocation"
    else:
        resolved = "judge_from_user_request"
        reason = "no deterministic intent signal"
    return {
        "requested": requested,
        "resolved": resolved,
        "reason": reason,
    }


def _required_reads(
    *,
    artifact: dict[str, Any],
    intent: dict[str, Any],
    adapter: dict[str, Any],
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

    for path, why in INTENT_REFERENCE_READS.get(
        intent["resolved"],
        INTENT_REFERENCE_READS["judge_from_user_request"],
    ):
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
    if not artifact["exists"]:
        return {
            "kind": "scaffold_missing_artifact",
            "command": 'python3 "$SKILL_DIR/scripts/scaffold_handoff_artifact.py" --repo-root . --json',
            "why": "the adapter-resolved handoff artifact is missing",
        }
    if intent["resolved"] == "chunked_routing":
        return {
            "kind": "run_chunked_routing",
            "command": (
                'python3 "$SKILL_DIR/scripts/parse_handoff_entries.py" '
                "--repo-root . --with-issues"
            ),
            "why": "start the chunked-routing pipeline, then follow the reference",
        }
    if artifact["status"] in {"over_limit", "shape_issue", "diary_smell", "near_limit"}:
        return {
            "kind": "repair_or_prune_handoff",
            "command": f"sed -n '1,220p' {artifact_path}",
            "why": f"artifact status is {artifact['status']}",
        }
    if intent["resolved"] == "pickup":
        return {
            "kind": "follow_workflow_trigger",
            "command": f"sed -n '1,80p' {artifact_path}",
            "why": "pickup should invoke the named workflow trigger first",
        }
    return {
        "kind": "refresh_handoff",
        "command": f"sed -n '1,220p' {artifact_path}",
        "why": "inspect current handoff and live repo state before rewriting",
    }


def build_plan(
    repo_root: Path,
    *,
    intent: str,
    invocation_text: str,
    invoked_directly: bool,
) -> dict[str, Any]:
    adapter = resolve_adapter.load_adapter(repo_root)
    artifact = _artifact_summary(repo_root, adapter)
    should_chunk = chunked_routing_lib.should_fire_chunker(
        invocation_text,
        invoked_directly=invoked_directly,
    )
    resolved_intent = _resolve_intent(
        requested=intent,
        invocation_text=invocation_text,
        chunked_routing=should_chunk,
    )
    artifact_path = str(artifact["path"])
    return {
        "schema_version": "handoff.run_plan.v1",
        "repo_root": str(repo_root),
        "adapter": {
            "artifact_path": artifact_path,
            "found": bool(adapter.get("found")),
            "valid": bool(adapter.get("valid")),
            "warnings": adapter.get("warnings", []),
            "errors": adapter.get("errors", []),
        },
        "artifact": artifact,
        "intent": {
            **resolved_intent,
            "chunked_routing": {
                "should_run": should_chunk,
                "invoked_directly": invoked_directly,
            },
        },
        "required_reads": _required_reads(
            artifact=artifact,
            intent=resolved_intent,
            adapter=adapter,
        ),
        "gate_packets": _gate_packets(repo_root, artifact_path),
        "next_action": _next_action(
            artifact=artifact,
            intent=resolved_intent,
            artifact_path=artifact_path,
        ),
        "phase_barriers": [
            "Read required_reads before opening broader docs or editing the artifact.",
            "Treat gate_packets as evidence packets: cheap deterministic gates can be trusted for shape, not for judgment.",
            "For chunked routing, write only at the end; for refresh, keep only facts that change the next action.",
        ],
    }


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff plan_handoff_run")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--intent",
        choices=("auto", "pickup", "refresh"),
        default="auto",
        help="Operator intent when known; auto derives only deterministic cases.",
    )
    parser.add_argument("--invocation-text", default="")
    parser.add_argument("--invoked-directly", action="store_true")
    parser.add_argument("--json", action="store_true")
    try:
        args = parser.parse_args()
        plan = build_plan(
            args.repo_root.resolve(),
            intent=args.intent,
            invocation_text=args.invocation_text,
            invoked_directly=args.invoked_directly,
        )
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
