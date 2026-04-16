from __future__ import annotations

import json
from pathlib import Path

from scripts.control_plane_lib import load_support_capabilities
from scripts.repo_layout import discovery_stub_dir, generated_support_dir
from scripts.support_sync_lib import support_link_name, support_state_for_manifest


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _materialized_support_skill_path(root: Path, manifest: dict[str, object]) -> str | None:
    support = manifest.get("support_skill_source")
    generated_skill = generated_support_dir(root) / support_link_name(manifest) / "SKILL.md"
    if not isinstance(support, dict) or not generated_skill.is_file():
        return None
    return str(generated_skill.relative_to(root))


def _materialized_discovery_stub_path(root: Path, tool_id: str) -> str | None:
    stub = discovery_stub_dir(root) / f"{tool_id}.md"
    if not stub.is_file():
        return None
    return str(stub.relative_to(root))


def _layers(data: dict[str, object]) -> list[dict[str, object]]:
    return [
        {"layer_id": layer["layer_id"], "layer_type": layer["layer_type"], "summary": layer["summary"]}
        for layer in data.get("config_layers", [])
    ]


def _checks(data: dict[str, object]) -> list[dict[str, object]]:
    return [
        {"check_id": check["check_id"], "summary": check["summary"]}
        for check in data.get("readiness_checks", [])
    ]


def integrations(root: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for manifest in sorted((root / "integrations" / "tools").glob("*.json")):
        if manifest.name == "manifest.schema.json":
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        tool_id = data.get("tool_id", manifest.stem)
        items.append(
            {
                "id": tool_id,
                "kind": data.get("kind", "unknown"),
                "access_modes": data.get("access_modes", []),
                "support_state": support_state_for_manifest(data),
                "support_skill_path": _materialized_support_skill_path(root, data),
                "discovery_stub_path": _materialized_discovery_stub_path(root, tool_id),
                "capability_requirements": data.get("capability_requirements", {}),
                "intent_triggers": data.get("intent_triggers", []),
                "config_layers": _layers(data),
                "readiness_checks": _checks(data),
                "supports_public_skills": data.get("supports_public_skills", []),
                "recommendation_role": data.get("recommendation_role"),
                "path": str(manifest.relative_to(root)),
                "source": "local-integration",
                "layer": "external integration",
            }
        )
    return items


def _support_trigger_phrases(capability: dict[str, object]) -> list[str]:
    tool_id = capability["tool_id"]
    return _dedupe(
        [
            str(tool_id),
            str(capability.get("display_name", "")),
            f"{tool_id} support",
            f"{tool_id} support skill",
            f"support/{tool_id}",
            *capability.get("intent_triggers", []),
        ]
    )


def support_capabilities(root: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for capability in load_support_capabilities(root):
        items.append(
            {
                "id": capability["tool_id"],
                "kind": capability["kind"],
                "display_name": capability.get("display_name", capability["tool_id"]),
                "summary": capability.get("summary", ""),
                "access_modes": capability.get("access_modes", []),
                "capability_requirements": capability.get("capability_requirements", {}),
                "intent_triggers": capability.get("intent_triggers", []),
                "trigger_phrases": _support_trigger_phrases(capability),
                "config_layers": _layers(capability),
                "readiness_checks": _checks(capability),
                "path": capability["_manifest_path"],
                "support_skill_path": capability["support_skill_path"],
                "supports_public_skills": capability.get("supports_public_skills", []),
                "source": "local-support-capability",
                "layer": "support capability",
            }
        )
    return items
