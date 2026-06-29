#!/usr/bin/env python3
"""Plan the first phase of a quality run before broad gates or fixes."""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[1] / "references" / "catalog.yaml"
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)


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
        "id": "capability_needed",
        "question": "What user or downstream-agent capability is weak or missing for this target?",
        "artifact_signal": "Record the capability before naming the move; do not start from a gate or authoring form.",
    },
    {
        "id": "sequencing_applicability",
        "question": "Does order affect correctness, uncertainty reduction, or downstream unlocks here, or should the generative-sequence lens stay unused?",
        "artifact_signal": "Use ../../../shared/references/generative-sequence.md only when the failure is sequencing-shaped.",
    },
    {
        "id": "current_centers",
        "question": "Which current centers already help the capability, and which one should be strengthened next?",
        "artifact_signal": "Record current centers and the next center before choosing a transformation.",
    },
    {
        "id": "quality_move_card",
        "question": "For each recommended quality move, what is the bounded transformation, proof boundary, and enforcement posture?",
        "artifact_signal": "Apply the move card only to recommended moves, not every finding.",
    },
    {
        "id": "enforcement_posture",
        "question": "Is the posture advisory, describe-first, existing-gate-reuse, candidate-floor, or no-gate?",
        "artifact_signal": "Default missing or uncertain posture to advisory/no-gate; candidate-floor requires north-star plus floor-addition-restraint provenance.",
    },
    {
        "id": "authoring_form_relevance",
        "question": "Do helper ownership, core-vs-reference, dogfood, or ergonomics issues explain the weak capability, or are they ambient/non-claims?",
        "artifact_signal": "Use authoring/form questions only when they explain the consumer capability weakness.",
    },
)

QUALITY_MOVE_TYPES = (
    "cleanup-delete",
    "merge-or-split-ownership",
    "helper-extraction",
    "interface-narrowing",
    "dogfood-or-evidence-packet",
    "gate-reuse",
    "floor-candidate",
    "defer-watch",
    "no-op",
)

ENFORCEMENT_POSTURES = (
    "advisory",
    "describe-first",
    "existing-gate-reuse",
    "candidate-floor",
    "no-gate",
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
            "Recommended Next Quality Moves:",
        ],
        "quality_move_card": {
            "applies_to": "recommended moves only",
            "fields": [
                "capability_needed",
                "current_centers",
                "next_center",
                "transformation",
                "proof_boundary",
                "enforcement_posture",
            ],
            "move_types": list(QUALITY_MOVE_TYPES),
            "enforcement_postures": list(ENFORCEMENT_POSTURES),
            "default_enforcement_posture": "advisory-or-no-gate",
            "candidate_floor_requirement": "explicit north-star plus floor-addition-restraint record",
        },
        "questions": list(STRUCTURAL_REVIEW_QUESTIONS),
        "interpretation": {
            "measures": "a required judgment packet over the target skill, not another heuristic score",
            "proxy_for": "whether the quality run reached capability-first judgment before recommending moves",
            "blind_spots": "the packet enforces that questions are answered, not that the answers are correct; it must not become form-filling for every finding",
            "interpretation_question": "did the answers identify the next quality move or justify no quality move with evidence?",
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
    return ENVELOPE.build_envelope(
        schema_version="quality.run_plan.v2",
        required_reads=required_reads,
        next_action=ENVELOPE.next_action("read_primer_refs"),
        gate_packets=gates,
        repo_root=str(repo_root),
        skills_in_scope=skills_in_scope,
        skill_scope_reason=(
            f"found {len(skills)} checked-in skill package(s)" if skills else "no skills/public or skills/support SKILL.md files found"
        ),
        sample_skill_paths=skills[:8],
        required_primer_refs=required_refs,
        structural_review_packet=structural_packet,
        gate_plan="report_first",
        phase_barriers=phase_barriers,
        on_demand_reads=on_demand_reads,
        on_demand_trigger_map=on_demand_trigger_map,
    )


def format_human(plan: dict[str, Any]) -> str:
    lines = [
        "Quality run plan:",
        f"- next_action: {plan['next_action']['kind']}",
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
