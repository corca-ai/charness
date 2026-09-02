#!/usr/bin/env python3
"""Plan the first phase of a quality run before broad gates or fixes."""

from __future__ import annotations

import argparse
import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[1] / "references" / "catalog.yaml"
SKILL_ROOT = Path(__file__).resolve().parents[1]
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)
DECLARED_GATE_SOURCE = runpy.run_path(str(Path(__file__).resolve().parent / "quality_declared_gate_source.py"))


def _load_declaration_lifecycle():
    path = Path(__file__).resolve().parent / "quality_declaration_lifecycle.py"
    spec = importlib.util.spec_from_file_location("quality_declaration_lifecycle", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"quality_declaration_lifecycle.py not loadable beside {Path(__file__).name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_plan_renderer():
    path = Path(__file__).resolve().parent / "quality_run_plan_render.py"
    spec = importlib.util.spec_from_file_location("quality_run_plan_render", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"quality_run_plan_render.py not loadable beside {Path(__file__).name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_yaml_file(path: Path) -> dict[str, Any]:
    for ancestor in Path(__file__).resolve().parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            root_text = str(ancestor)
            if root_text not in sys.path:
                sys.path.insert(0, root_text)
            from scripts.adapter_lib import load_yaml_file

            return load_yaml_file(path)
    raise RuntimeError("scripts/adapter_lib.py not found")


def _emit_yaml(payload: dict[str, Any]) -> None:
    for ancestor in Path(__file__).resolve().parents:
        if (ancestor / "scripts" / "yaml_output.py").is_file():
            root_text = str(ancestor)
            if root_text not in sys.path:
                sys.path.insert(0, root_text)
            from scripts.yaml_output import emit_yaml

            emit_yaml(payload)
            return
    raise RuntimeError("scripts/yaml_output.py not found")


def _measure_required_read(ref: dict[str, Any]) -> dict[str, Any]:
    """Disclose a catalog read from the quality skill's explicit path base.

    Quality's catalog refs carry no `base` token -- every one is skill-relative --
    so the shared resolver is handed that single anchor. See the sibling note in
    `plan_handoff_run._measure_required_read` for why this is a delegation now.
    """
    # A LITERAL map, not `{ref.get("base"): ...}`: deriving the key from the value
    # being looked up makes `unknown-base` structurally unreachable, so a future
    # catalog ref carrying `base: repo` would be priced against the SKILL root and
    # disclosed as `missing` -- or worse, as a confident size for the wrong file.
    return ENVELOPE.measure_read(dict(ref), {None: SKILL_ROOT})


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

# Canonical final stop-before-finish gate signals, cheap file/manifest probes.
# Presence sharpens the maintainer-local-enforcement prompt from a standing
# question into a named-gate one; absence leaves the standing question intact.
FINAL_GATE_FILE_SIGNALS = (
    ("scripts/run-quality.sh", "scripts/run-quality.sh"),
    ("scripts/run-verify.sh", "scripts/run-verify.sh"),
    ("scripts/run-verify.mjs", "scripts/run-verify.mjs"),
)
FINAL_GATE_MANIFEST_SIGNALS = (
    ("package.json", '"verify"', "package.json verify script"),
    ("Makefile", "verify:", "Makefile verify target"),
)


def _detect_final_gate(repo_root: Path) -> list[str]:
    """Cheap probe for a canonical final stop-before-finish gate.

    Only file existence + a single substring scan per manifest — no parsing — so
    the planner stays fast and dependency-free. Used to sharpen, never to gate.
    The manifest substring scan is deliberately permissive toward detection: a
    false positive only sharpens the already-standing maintainer-local prompt,
    while the ``else`` branch below still emits the standing question, so a miss
    never silences the discipline.
    """
    found: list[str] = []
    for rel, label in FINAL_GATE_FILE_SIGNALS:
        if (repo_root / rel).is_file():
            found.append(label)
    for rel, needle, label in FINAL_GATE_MANIFEST_SIGNALS:
        path = repo_root / rel
        if not path.is_file():
            continue
        try:
            if needle in path.read_text(encoding="utf-8", errors="ignore"):
                found.append(label)
        except OSError:
            continue
    return found


def _quality_brief(repo_root: Path, catalog: dict[str, Any]) -> dict[str, Any]:
    """Substantive brief that lets load-bearing primers stay trigger-gated depth.

    North star (reference-compaction intent.md): a gate/reference should BRIEF a
    capable agent, not force a mandatory prose read it already carries. The static
    residue of the demoted required-primers is declarative catalog data (`brief:`);
    this only injects the dynamic final-gate probe result into the maintainer-local
    prompt. detail_ref pointers preserve discoverability when a trigger fires.
    """
    brief = dict(catalog.get("brief") or {})
    final_gates = _detect_final_gate(repo_root)
    mle = dict(brief.get("maintainer_local_enforcement", {}))
    detected = str(mle.pop("detected_prompt_template", ""))
    standing = str(mle.pop("standing_prompt", ""))
    mle["final_gates_detected"] = final_gates
    mle["prompt"] = detected.replace("{gates}", ", ".join(final_gates)) if final_gates else standing
    brief["maintainer_local_enforcement"] = mle
    return brief


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
    discovered_skills = _skill_paths(repo_root)
    catalog = _load_yaml_file(CATALOG_PATH)
    references = catalog.get("references", [])
    catalog_gates = catalog.get("gates", [])
    declared_gates = DECLARED_GATE_SOURCE["read_consumer_gate_packets"](repo_root, _load_yaml_file)
    declaration_lifecycle, adapter_packets = _load_declaration_lifecycle().build_declaration_lifecycle(
        repo_root, skills=discovered_skills, catalog_gates=catalog_gates
    )
    skills = [
        row["path"]
        for row in declaration_lifecycle.get("skills", [])
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    ]
    skills_in_scope = bool(skills)
    adapter = declaration_lifecycle.get("adapter") or {}
    applicable_gate_ids = declaration_lifecycle.get("applicable_catalog_gate_ids")
    gates = list(catalog_gates)
    if adapter.get("found") and adapter.get("valid") and isinstance(applicable_gate_ids, list):
        gates = [gate for gate in gates if gate.get("id") in applicable_gate_ids]
    if declared_gates is not None:
        referenced_packet_ids = {
            packet_id
            for row in declaration_lifecycle.get("surfaces", [])
            if isinstance(row, dict)
            for packet_id in row.get("packet_ids", [])
            if isinstance(packet_id, str)
        }
        gates = [gate for gate in gates if gate.get("id") in referenced_packet_ids]
        gates = [*gates, *declared_gates]
    gates = [*gates, *adapter_packets]
    required_reads = [
        _measure_required_read(ref)
        for ref in references
        if ref.get("role") == "required-primer"
        or (ref.get("role") == "scope-primer" and ref.get("scope") == "skill-authoring" and skills_in_scope)
    ]
    on_demand_reads = [ref for ref in references if ref.get("role") == "on-demand"]
    on_demand_trigger_map = {
        str(ref["path"]): str(ref["trigger"])
        for ref in on_demand_reads
        if isinstance(ref, dict) and ref.get("path") and ref.get("trigger")
    }
    structural_packet = _structural_review_packet(repo_root, skills, target_skill)
    brief = _quality_brief(repo_root, catalog)
    phase_barriers = [
        "Read declaration_lifecycle before gates; declared-only, unreachable, missing, and not-run are not covered verdicts.",
        "Read required_reads before broad gates.",
        "The brief carries the load-bearing classification/automation/maintainer-enforcement discipline and the inventory-dispatch routing index (concern area -> inventories + detail_refs) inline; apply it and open a brief detail_ref only when its trigger fires.",
        "Run deterministic gates as evidence packets, then analyze the report against the primer refs before fixing.",
        "Use gate trust_model/cost_tier/parallel_group to decide whether to trust, parallelize, or manually inspect a packet.",
        "Open on-demand refs only when a concrete gate, inventory, source, or operator finding matches their trigger.",
    ]
    if structural_packet is not None:
        phase_barriers.insert(
            3,
            "Answer structural_review_packet before broad recommendations; separate target findings from ambient repo gate failures.",
        )
    return ENVELOPE.build_envelope(
        schema_version="quality.run_plan.v2",
        required_reads=required_reads,
        next_action=ENVELOPE.next_action("read_primer_refs"),
        gate_packets=gates,
        repo_root=str(repo_root),
        brief=brief,
        declaration_lifecycle=declaration_lifecycle,
        skills_in_scope=skills_in_scope,
        skill_scope_reason=(
            f"found {len(skills)} skill package(s) from {declaration_lifecycle.get('skill_scope_source', 'discovery')} scope"
            if skills
            else (
                "adapter-declared skill paths resolved to no SKILL.md files"
                if declaration_lifecycle.get("skill_scope_source") == "adapter-declared"
                else "no skills/public or skills/support SKILL.md files found"
            )
        ),
        sample_skill_paths=skills[:8],
        structural_review_packet=structural_packet,
        gate_plan="report_first",
        phase_barriers=phase_barriers,
        on_demand_reads=on_demand_reads,
        on_demand_trigger_map=on_demand_trigger_map,
    )


def format_human(plan: dict[str, Any]) -> str:
    return _load_plan_renderer().format_human(plan)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect for skills and quality inputs.",
    )
    parser.add_argument("--target-skill", help="Optional skill id or SKILL.md path for target-vs-ambient structural review")
    parser.add_argument("--detail", action="store_true", help="Emit the full quality run plan as YAML.")
    args = parser.parse_args()

    plan = build_plan(args.repo_root.resolve(), target_skill=args.target_skill)
    if args.detail:
        _emit_yaml(plan)
    else:
        print(format_human(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
