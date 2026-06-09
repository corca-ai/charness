from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.control_plane_lib import load_manifests_for_discovery, load_support_capabilities
from scripts.repo_layout import discovery_stub_dir, generated_support_dir
from scripts.support_sync_lib import support_link_name, support_state_for_manifest

PROVIDER_ID_ALIASES = {
    "github-gh": "github-worker",
    "gws-cli": "google-workspace-worker",
}

TEXT_REPLACEMENTS = {
    "github-gh": "github-worker",
    "gws-cli": "google-workspace-worker",
    "SLACK" + "_BOT_TOKEN": "Slack credential grant",
    "authenticated or installed binaries such as `gh`, `yt-dlp`, `defuddle`, or `agent-browser`": "host-mediated fetch helpers",
    "authenticated `gh`": "host-mediated GitHub credential",
    "`gh`": "GitHub worker",
    "gws" + " auth": "Google Workspace credential setup",
    "gws" + " gather": "workspace gather",
    "authenticated `gws`": "host-mediated Google Workspace credential",
    "`gws`": "Google Workspace worker",
    "https://www.googleapis" + ".com/auth/": "google-workspace-scope:",
}


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _public_tool_id(tool_id: str) -> str:
    return PROVIDER_ID_ALIASES.get(tool_id, tool_id)


def _sanitize_text(value: str) -> str:
    result = value
    for source, replacement in TEXT_REPLACEMENTS.items():
        result = result.replace(source, replacement)
    return result


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    return value


def _alias_path(path: str) -> str:
    for source_id, public_id in PROVIDER_ID_ALIASES.items():
        path = path.replace(f"{source_id}.json", f"{public_id}.json")
        path = path.replace(source_id, public_id)
    return path


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
    for data in load_manifests_for_discovery(root):
        tool_id = _public_tool_id(data["tool_id"])
        origin = data.get("_manifest_origin", "user-repo")
        entry = {
            "id": tool_id,
            "kind": "external capability" if data["tool_id"] in PROVIDER_ID_ALIASES else data.get("kind", "unknown"),
            "summary": data.get("summary", ""),
            "access_modes": data.get("access_modes", []),
            "support_state": support_state_for_manifest(data),
            "support_skill_path": _materialized_support_skill_path(root, data),
            "discovery_stub_path": _materialized_discovery_stub_path(root, tool_id),
            "capability_requirements": data.get("capability_requirements", {}),
            "intent_triggers": data.get("intent_triggers", []),
            "strong_intent_triggers": data.get("strong_intent_triggers", []),
            "config_layers": _layers(data),
            "readiness_checks": _checks(data),
            "supports_public_skills": data.get("supports_public_skills", []),
            "recommendation_role": data.get("recommendation_role"),
            "path": _alias_path(data["_manifest_path"]),
            "source": "local-integration" if origin == "user-repo" else "plugin-fallback-integration",
            "layer": "external integration",
        }
        items.append(_sanitize_value(entry))
    return items


def _sibling_support_root(root: Path) -> Path:
    return root.parent / "charness-support"


def _load_sibling_support_capabilities(root: Path) -> list[dict[str, object]]:
    support_root = _sibling_support_root(root)
    if not support_root.is_dir():
        return []
    items: list[dict[str, object]] = []
    for path in sorted(support_root.glob("*/capability.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        skill_id = path.parent.name
        data["_manifest_path"] = f"skills/support/{skill_id}/capability.json"
        data["support_skill_path"] = f"skills/support/{skill_id}/SKILL.md"
        data["tool_id"] = data["capability_id"]
        items.append(data)
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
    for capability in [*load_support_capabilities(root), *_load_sibling_support_capabilities(root)]:
        items.append(
            _sanitize_value({
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
            })
        )
    return items
