"""Human rendering for the structured quality run plan."""
from __future__ import annotations

from typing import Any


def _append_lifecycle(lines: list[str], lifecycle: dict[str, Any]) -> None:
    adapter = lifecycle.get("adapter") or {}
    lines.append(
        "  - adapter: "
        f"{'found' if adapter.get('found') else 'not-found'} / "
        f"{'valid' if adapter.get('valid') else 'not-valid'}"
    )
    for row in lifecycle.get("presets", []):
        lines.append(
            f"  - preset {row.get('preset')}: {row.get('reconciliation_state')}"
        )
    for row in lifecycle.get("commands", []):
        lines.append(
            f"  - command {row.get('field')}: {row.get('routing_state')} / "
            f"{row.get('execution_state')} / {row.get('command')}"
        )
    for row in lifecycle.get("surfaces", []):
        target = f" / {row['target_state']}" if row.get("target_state") else ""
        packets = ", ".join(row.get("packet_ids", [])) or "no-packet"
        lines.append(
            f"  - surface {row.get('surface')}: {row.get('routing_state')}"
            f"{target} / {packets}"
        )
    for row in lifecycle.get("declared_skill_paths", []):
        lines.append(
            f"  - skill path {row.get('declaration')}: {row.get('target_state')} / "
            f"{row.get('packet_id')}"
        )
    for gap in lifecycle.get("gaps", []):
        lines.append(f"  - GAP {gap.get('kind')}: {gap.get('detail')}")


def format_human(plan: dict[str, Any]) -> str:
    lifecycle = plan.get("declaration_lifecycle") or {}
    lines = [
        "Quality run plan:",
        f"- next_action: {plan['next_action']['kind']}",
        f"- skills_in_scope: {str(plan['skills_in_scope']).lower()} ({plan['skill_scope_reason']})",
        f"- gate_plan: {plan['gate_plan']}",
        f"- declaration_lifecycle: {lifecycle.get('status', 'unknown')} "
        f"({len(lifecycle.get('gaps', []))} gap(s))",
    ]
    _append_lifecycle(lines, lifecycle)
    lines.append("- required_reads:")
    lines.extend(f"  - {ref['path']}: {ref.get('why', 'required')}" for ref in plan["required_reads"])
    lines.append("- phase_barriers:")
    lines.extend(f"  - {barrier}" for barrier in plan["phase_barriers"])
    packet = plan.get("structural_review_packet")
    if packet:
        target = packet["target_skill"]
        lines.append("- structural_review_packet:")
        lines.append(
            f"  - target: {target['status']} "
            f"{target.get('path') or target.get('requested') or '(unspecified)'}"
        )
        lines.extend(f"  - {question['id']}: {question['question']}" for question in packet["questions"])
    brief = plan.get("brief")
    if brief:
        lines.append("- brief (load-bearing residue of demoted primers; open detail_ref on trigger):")
        gate_classification = brief.get("gate_classification", {})
        if gate_classification.get("closeout_states"):
            states = gate_classification["closeout_states"]
            lines.append(
                f"  - gate states: {', '.join(states)} "
                f"(see {gate_classification.get('detail_ref', '')})"
            )
            lines.append(f"  - weak also = {states.get('weak', '')}")
        automation = brief.get("automation_promotion", {})
        if automation.get("cases"):
            lines.append(
                f"  - automation: {', '.join(automation['cases'])} "
                f"(see {automation.get('detail_ref', '')})"
            )
        enforcement = brief.get("maintainer_local_enforcement", {})
        if enforcement.get("prompt"):
            lines.append(f"  - maintainer-local: {enforcement['prompt']}")
        if enforcement.get("field_discipline"):
            lines.append(f"    field: {enforcement['field_discipline']}")
        dispatch = brief.get("inventory_dispatch", {})
        if dispatch.get("areas"):
            lines.append(
                f"  - inventory dispatch ({len(dispatch['areas'])} concern areas; "
                f"open {dispatch.get('detail_ref', '')} on trigger):"
            )
            for area in dispatch["areas"]:
                inventories = ", ".join(area.get("inventories", [])) or "(detail_refs only)"
                lines.append(f"    - {area['area']}: {inventories}")
    lines.append("- gate_packets:")
    for gate in plan["gate_packets"]:
        lines.append(f"  - {gate['id']}: {gate['cost_tier']} / {gate['trust_model']}")
        if gate.get("command"):
            lines.append(f"    command: {gate['command']}")
    lines.append("- on_demand_reads: open only from concrete findings")
    return "\n".join(lines)
