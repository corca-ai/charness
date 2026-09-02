"""Reconcile quality-adapter declarations with planner routing, without running them."""

from __future__ import annotations

import importlib
import importlib.util
import shlex
import sys
from pathlib import Path
from typing import Any

COMMAND_FIELDS = (
    "preflight_commands",
    "gate_commands",
    "review_commands",
    "security_commands",
)


def _repo_module(name: str):
    parts = name.split(".")
    module_path = Path(*parts[:-1]) / f"{parts[-1]}.py"
    for ancestor in Path(__file__).resolve().parents:
        if (ancestor / module_path).is_file():
            root = str(ancestor)
            if root not in sys.path:
                sys.path.insert(0, root)
            return importlib.import_module(name)
    raise ImportError(f"{name} not found from quality skill runtime")


def _load_preset_reconciliation():
    path = Path(__file__).resolve().parent / "quality_preset_reconciliation.py"
    spec = importlib.util.spec_from_file_location("quality_preset_reconciliation", path)
    if spec is None or spec.loader is None:
        raise ImportError("quality_preset_reconciliation.py not loadable beside lifecycle")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_PRESET_RECONCILIATION = _load_preset_reconciliation()


def _preset_contract(repo_root: Path, preset: object) -> dict[str, Any]:
    return _PRESET_RECONCILIATION.preset_contract(repo_root, preset, _repo_module)


def _preset_rows(
    repo_root: Path, raw: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _PRESET_RECONCILIATION.preset_rows(repo_root, raw, _repo_module)


def _load_catalog_applicability():
    path = Path(__file__).resolve().parent / "quality_catalog_gate_applicability.py"
    spec = importlib.util.spec_from_file_location("quality_catalog_gate_applicability", path)
    if spec is None or spec.loader is None:
        raise ImportError(
            "quality_catalog_gate_applicability.py not loadable beside quality_declaration_lifecycle.py"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_skill_scope():
    path = Path(__file__).resolve().parent / "quality_skill_scope.py"
    spec = importlib.util.spec_from_file_location("quality_skill_scope", path)
    if spec is None or spec.loader is None:
        raise ImportError(
            "quality_skill_scope.py not loadable beside quality_declaration_lifecycle.py"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_REPO_FILE_LISTING = _repo_module("scripts.core.repo_file_listing")
_CATALOG_APPLICABILITY = _load_catalog_applicability()
_SKILL_SCOPE = _load_skill_scope()


def _packet(
    packet_id: str,
    command: str,
    *,
    purpose: str,
    cost_tier: str = "unknown",
) -> dict[str, Any]:
    return {
        "id": packet_id,
        "command": command,
        "purpose": purpose,
        "trust_model": (
            "repo-declared route; planner inclusion proves reachability only, "
            "and execution remains not-run until a later receipt says otherwise"
        ),
        "cost_tier": cost_tier,
        "parallel_group": "adapter-declared",
        "run_after": "required-primer",
        "run_when": "declared by the resolved quality adapter",
    }


def _declared_commands(
    raw: dict[str, Any], catalog_gates: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    packets: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    catalog_by_command = {
        str(gate.get("command")): str(gate.get("id"))
        for gate in catalog_gates
        if gate.get("command") and gate.get("id")
    }
    for field in COMMAND_FIELDS:
        commands = raw.get(field)
        if not isinstance(commands, list):
            continue
        for index, command in enumerate(commands, 1):
            if not isinstance(command, str) or not command.strip():
                continue
            packet_id = catalog_by_command.get(command)
            if packet_id is None:
                family = field.removesuffix("_commands").replace("_", "-")
                packet_id = f"adapter-{family}-{index}"
                packets.append(
                    _packet(
                        packet_id,
                        command,
                        purpose=f"execute the adapter's declared {field} entry",
                        cost_tier="review" if field == "review_commands" else "unknown",
                    )
                )
            rows.append(
                {
                    "field": field,
                    "command": command,
                    "declaration_state": "declared",
                    "routing_state": "routed",
                    "execution_state": "not-run",
                    "packet_id": packet_id,
                }
            )
    return rows, packets


def _declared_skill_paths(repo_root: Path, raw: dict[str, Any]) -> list[dict[str, Any]]:
    return _SKILL_SCOPE.declared_skill_paths(repo_root, raw, _REPO_FILE_LISTING)


def _surface_rows(
    repo_root: Path,
    raw: dict[str, Any],
    skills: list[str],
    command_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    packets: list[dict[str, Any]] = []
    probes = raw.get("cli_skill_surface_probe_commands")
    probe_commands = (
        [item for item in probes if isinstance(item, str) and item]
        if isinstance(probes, list)
        else []
    )
    for index, command in enumerate(probe_commands, 1):
        packets.append(
            _packet(
                f"adapter-cli-probe-{index}",
                command,
                purpose="exercise one adapter-declared installable CLI probe",
                cost_tier="cheap",
            )
        )

    surfaces = raw.get("product_surfaces")
    review_packet_ids = [
        str(row["packet_id"])
        for row in command_rows
        if row.get("field") == "review_commands" and row.get("packet_id")
    ]
    for surface in surfaces if isinstance(surfaces, list) else []:
        if surface in {"bundled_skill", "public_skill"}:
            reachable = bool(skills)
            packet_ids = ["skill-ergonomics"] if reachable else []
            routing_state = "routed" if reachable else "unreachable"
        elif surface == "support_skill":
            reachable = any(path.startswith("skills/support/") for path in skills)
            packet_ids = ["skill-ergonomics"] if reachable else []
            routing_state = "routed" if reachable else "unreachable"
        elif surface == "installable_cli":
            reachable = bool(probe_commands)
            packet_ids = [f"adapter-cli-probe-{i}" for i in range(1, len(probe_commands) + 1)]
            routing_state = "routed" if reachable else "unreachable"
        else:
            packet_ids = review_packet_ids
            routing_state = "partial" if packet_ids else "unreachable"
        rows.append(
            {
                "surface": surface,
                "declaration_state": "declared",
                "routing_state": routing_state,
                "packet_ids": packet_ids,
            }
        )

    docs = raw.get("canonical_markdown_surfaces")
    doc_paths = (
        [item for item in docs if isinstance(item, str) and item] if isinstance(docs, list) else []
    )
    if doc_paths:
        command = 'python3 "$SKILL_DIR/scripts/inventory_entrypoint_docs_ergonomics.py" --repo-root . --summary'
        command += "".join(f" --doc-path {shlex.quote(path)}" for path in doc_paths)
        packets.append(
            _packet(
                "adapter-canonical-docs",
                command,
                purpose="inspect each adapter-declared canonical Markdown surface",
                cost_tier="cheap",
            )
        )
        rows.extend(
            {
                "surface": path,
                "kind": "canonical_markdown_surface",
                "declaration_state": "declared",
                "target_state": "present" if (repo_root / path).is_file() else "missing",
                "routing_state": "routed",
                "packet_ids": ["adapter-canonical-docs"],
            }
            for path in doc_paths
        )
    return rows, packets


def _effective_skill_paths(
    discovered: list[str], declared_rows: list[dict[str, Any]], raw: dict[str, Any]
) -> tuple[list[str], str]:
    return _SKILL_SCOPE.effective_skill_paths(discovered, declared_rows, raw)


def build_declaration_lifecycle(
    repo_root: Path,
    *,
    skills: list[str],
    catalog_gates: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    adapter_lib = _repo_module("scripts.adapters.quality_adapter_lib")
    yaml_lib = _repo_module("scripts.adapter_lib")
    adapter = adapter_lib.load_quality_adapter_permissive(repo_root)
    report: dict[str, Any] = {
        "status": "not-configured" if not adapter.get("found") else "configured",
        "adapter": {
            "found": bool(adapter.get("found")),
            "valid": adapter.get("valid") is True,
            "path": adapter.get("path"),
            "errors": list(adapter.get("errors") or []),
            "warnings": list(adapter.get("warnings") or []),
        },
        "presets": [],
        "commands": [],
        "surfaces": [],
        "skills": [],
        "skill_scope_source": "discovered",
        "declared_skill_paths": [],
        "unavailable_catalog_gates": [],
        "gaps": [],
    }
    if adapter.get("valid") is not True:
        report["status"] = "invalid"
        report["gaps"].append(
            {
                "kind": "invalid_adapter",
                "detail": "repair adapter errors before trusting declared routes",
            }
        )
        return report, []
    path = adapter.get("path")
    raw = yaml_lib.load_yaml_file(Path(path)) if path else {}
    if not isinstance(raw, dict):
        raw = {}

    preset_rows, preset_gaps = _preset_rows(repo_root, raw)
    report["presets"] = preset_rows
    report["gaps"].extend(preset_gaps)

    if adapter.get("found"):
        applicable_catalog_gates, unavailable_catalog_gates = (
            _CATALOG_APPLICABILITY.applicable_catalog_gates(repo_root, raw, catalog_gates)
        )
    else:
        applicable_catalog_gates, unavailable_catalog_gates = catalog_gates, []
    report["unavailable_catalog_gates"] = unavailable_catalog_gates
    for unavailable in unavailable_catalog_gates:
        report["gaps"].append(
            {
                "kind": "catalog_gate_unavailable",
                "detail": f"{unavailable['id']}: {unavailable['reason']}",
            }
        )

    declared_skill_paths = _declared_skill_paths(repo_root, raw)
    skills, skill_scope_source = _effective_skill_paths(skills, declared_skill_paths, raw)
    report["skill_scope_source"] = skill_scope_source
    report["skills"] = [
        {
            "path": path,
            "kind": "checked-in-skill",
            "routing_state": "routed",
            "packet_id": "skill-ergonomics",
        }
        for path in skills
    ]
    command_rows, command_packets = _declared_commands(raw, applicable_catalog_gates)
    surface_rows, surface_packets = _surface_rows(repo_root, raw, skills, command_rows)
    report["commands"] = command_rows
    report["surfaces"] = surface_rows
    report["declared_skill_paths"] = declared_skill_paths
    for row in [*surface_rows, *report["declared_skill_paths"]]:
        routing_state = row.get("routing_state")
        if routing_state in {"partial", "unreachable"} or row.get("target_state") in {
            "unreachable",
            "missing",
        }:
            report["gaps"].append(
                {
                    "kind": (
                        "declared_surface_partial"
                        if routing_state == "partial"
                        else "declared_surface_unreachable"
                    ),
                    "detail": row.get("surface") or row.get("declaration"),
                }
            )
    if report["gaps"]:
        report["status"] = "action-required"
    report["applicable_catalog_gate_ids"] = [
        str(gate["id"]) for gate in applicable_catalog_gates if isinstance(gate.get("id"), str)
    ]
    return report, [*command_packets, *surface_packets]
