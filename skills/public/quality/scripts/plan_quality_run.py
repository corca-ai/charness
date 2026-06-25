#!/usr/bin/env python3
"""Plan the first phase of a quality run before broad gates or fixes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[1] / "references" / "catalog.yaml"


def _load_yaml_file(path: Path) -> dict[str, Any]:
    for ancestor in Path(__file__).resolve().parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            root_text = str(ancestor)
            if root_text not in sys.path:
                sys.path.insert(0, root_text)
            from scripts.adapter_lib import load_yaml_file

            return load_yaml_file(path)
    raise RuntimeError("scripts/adapter_lib.py not found")


def _catalog() -> dict[str, Any]:
    return _load_yaml_file(CATALOG_PATH)


def _skill_paths_under(repo_root: Path, parents: list[Path]) -> list[str]:
    found: set[str] = set()
    for parent in parents:
        if not parent.is_dir():
            continue
        found.update(
            str(path.relative_to(repo_root))
            for path in sorted(parent.glob("*/SKILL.md"))
            if "generated" not in path.parts
        )
    return sorted(found)


def _skill_paths(repo_root: Path) -> list[str]:
    root_skills = _skill_paths_under(
        repo_root,
        [repo_root / "skills" / "public", repo_root / "skills" / "support"],
    )
    if root_skills:
        return root_skills
    plugin_skill_parents = []
    plugins_root = repo_root / "plugins"
    if plugins_root.is_dir():
        plugin_skill_parents = sorted(path / "skills" for path in plugins_root.iterdir() if (path / "skills").is_dir())
    return _skill_paths_under(repo_root, plugin_skill_parents)


STRUCTURAL_REVIEW_QUESTIONS = (
    {
        "id": "target_vs_ambient",
        "question": "Which findings are target-skill quality findings, which are ambient repo gate failures, and which opportunistic repairs are non-claims for the target?",
        "artifact_signal": "Record target boundary and ambient repo findings before recommendations.",
    },
    {
        "id": "helper_owned_packet",
        "question": "Does the target skill ask the model to rediscover an order or packet that a helper/planner should emit?",
        "artifact_signal": "Record whether a planner/report packet is needed, already sufficient, or deliberately unnecessary.",
    },
    {
        "id": "core_vs_reference",
        "question": "Does SKILL.md own selection and sequencing while references deepen the path, or has a reference become a second workflow?",
        "artifact_signal": "Record the progressive-disclosure judgment even when heuristics are quiet.",
    },
    {
        "id": "dogfood_pressure",
        "question": "Does the public-skill dogfood case pressure the real consumer behavior, not only syntax, packaging, or producer-side validators?",
        "artifact_signal": "Record dogfood sufficiency or the next consumer-side proof.",
    },
    {
        "id": "heuristic_blind_spot",
        "question": "If skill ergonomics heuristics are quiet, is that evidence of health or a blind spot against the target's main behavior risk?",
        "artifact_signal": "Record the prose judgment; do not equate zero heuristics with health.",
    },
    {
        "id": "next_structural_move",
        "question": "What is the next delete/merge/split/helper/interface-narrowing move, or why is there no structural move now?",
        "artifact_signal": "Record an active next gate or an evidence-backed no-change/defer disposition.",
    },
)


def _resolve_target_skill(repo_root: Path, skills: list[str], target: str | None) -> dict[str, Any]:
    if not target:
        return {
            "requested": None,
            "status": "unspecified",
            "path": None,
            "note": "No target skill was provided; answer the structural packet for the selected quality scope before recommending fixes.",
        }
    normalized = target.strip().removeprefix("charness:").removesuffix(" skill")
    candidates = [
        path for path in skills
        if path == target
        or path.endswith(f"/{normalized}/SKILL.md")
        or Path(path).parent.name == normalized
    ]
    if len(candidates) == 1:
        return {
            "requested": target,
            "status": "resolved",
            "path": candidates[0],
            "note": "Use this target for target-vs-ambient classification and structural review.",
        }
    if len(candidates) > 1:
        return {
            "requested": target,
            "status": "ambiguous",
            "path": None,
            "matches": candidates,
            "note": "Multiple skill paths matched; choose one before target-specific recommendations.",
        }
    return {
        "requested": target,
        "status": "not_found",
        "path": None,
        "note": "Target skill was not found in the checked-in skill surface; classify this before proceeding.",
    }


def _structural_review_packet(repo_root: Path, skills: list[str], target_skill: str | None) -> dict[str, Any] | None:
    if not skills:
        return None
    return {
        "required": True,
        "target_skill": _resolve_target_skill(repo_root, skills, target_skill),
        "write_artifact_signals": [
            "Target boundary:",
            "Ambient repo findings:",
            "prose review result:",
            "structural review result:",
        ],
        "questions": list(STRUCTURAL_REVIEW_QUESTIONS),
        "interpretation": {
            "measures": "a required judgment packet over the target skill, not another heuristic score",
            "proxy_for": "whether the quality run reached the north-star judgment phase before recommending fixes",
            "blind_spots": "the packet enforces that questions are answered, not that the answers are correct",
            "interpretation_question": "did the answers identify the next structural move or justify no structural move with evidence?",
        },
    }


def build_plan(repo_root: Path, *, target_skill: str | None = None) -> dict[str, Any]:
    skills = _skill_paths(repo_root)
    skills_in_scope = bool(skills)
    catalog = _catalog()
    references = catalog.get("references", [])
    gates = catalog.get("gates", [])
    required_reads = [
        ref
        for ref in references
        if ref.get("role") == "required-primer"
        or (ref.get("role") == "scope-primer" and ref.get("scope") == "skill-authoring" and skills_in_scope)
    ]
    on_demand_reads = [ref for ref in references if ref.get("role") == "on-demand"]
    required_refs = [str(ref["path"]) for ref in required_reads]
    on_demand_trigger_map = {
        str(ref["path"]): str(ref["trigger"])
        for ref in on_demand_reads
        if isinstance(ref, dict) and ref.get("path") and ref.get("trigger")
    }
    structural_packet = _structural_review_packet(repo_root, skills, target_skill)
    phase_barriers = [
        "Read required_reads (also exposed as required_primer_refs for compatibility) before broad gates.",
        "Run deterministic gates as evidence packets, then analyze the report against the primer refs before fixing.",
        "Use gate trust_model/cost_tier/parallel_group to decide whether to trust, parallelize, or manually inspect a packet.",
        "Open on-demand refs only when a concrete gate, inventory, source, or operator finding matches their trigger.",
    ]
    if structural_packet is not None:
        phase_barriers.insert(
            2,
            "Answer structural_review_packet before broad recommendations; separate target findings from ambient repo gate failures.",
        )
    return {
        "schema_version": "quality.run_plan.v2",
        "repo_root": str(repo_root),
        "skills_in_scope": skills_in_scope,
        "skill_scope_reason": (
            f"found {len(skills)} checked-in skill package(s)" if skills else "no skills/public or skills/support SKILL.md files found"
        ),
        "sample_skill_paths": skills[:8],
        "required_reads": required_reads,
        "required_primer_refs": required_refs,
        "structural_review_packet": structural_packet,
        "gate_plan": "report_first",
        "gate_packets": gates,
        "next_action": "read_primer_refs",
        "phase_barriers": phase_barriers,
        "on_demand_reads": on_demand_reads,
        "on_demand_trigger_map": on_demand_trigger_map,
    }


def format_human(plan: dict[str, Any]) -> str:
    lines = [
        "Quality run plan:",
        f"- next_action: {plan['next_action']}",
        f"- skills_in_scope: {str(plan['skills_in_scope']).lower()} ({plan['skill_scope_reason']})",
        f"- gate_plan: {plan['gate_plan']}",
        "- required_reads:",
    ]
    lines.extend(f"  - {ref['path']}: {ref.get('why', 'required')}" for ref in plan["required_reads"])
    lines.append("- phase_barriers:")
    lines.extend(f"  - {barrier}" for barrier in plan["phase_barriers"])
    packet = plan.get("structural_review_packet")
    if packet:
        target = packet["target_skill"]
        lines.append("- structural_review_packet:")
        lines.append(f"  - target: {target['status']} {target.get('path') or target.get('requested') or '(unspecified)'}")
        lines.extend(f"  - {question['id']}: {question['question']}" for question in packet["questions"])
    lines.append("- gate_packets:")
    lines.extend(
        f"  - {gate['id']}: {gate['cost_tier']} / {gate['trust_model']}"
        for gate in plan["gate_packets"]
    )
    lines.append("- on_demand_reads: open only from concrete findings")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--target-skill", help="Optional skill id or SKILL.md path for target-vs-ambient structural review")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plan = build_plan(args.repo_root.resolve(), target_skill=args.target_skill)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_human(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
