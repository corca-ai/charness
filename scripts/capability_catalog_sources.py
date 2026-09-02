"""Deterministic capability inventory sources.

This module deliberately contains facts only: installed public/support skills,
synced support surfaces, trusted roots, and integration manifests.  It has no
free-text routing or recommendation logic.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scripts.adapter_lib import (
    load_yaml_file,
    optional_bool,
    optional_string,
    optional_string_list,
    validate_adapter_version,
)
from scripts.control_plane_lib import load_manifests_for_discovery, load_support_capabilities
from scripts.core.repo_layout import generated_support_dir, public_skills_dir, support_dir
from scripts.support_sync_lib import support_link_name, support_state_for_manifest

PROVIDER_ID_ALIASES = {"github-gh": "github-worker"}
TEXT_REPLACEMENTS = {
    "github-gh": "github-worker",
    "SLACK" + "_BOT_TOKEN": "Slack credential grant",
    "https://www.googleapis" + ".com/auth/": "google-workspace-scope:",
    "authenticated or installed binaries such as `gh`, `yt-dlp`, `defuddle`, or `agent-browser`": "host-mediated fetch helpers",
    "authenticated `gh`": "host-mediated GitHub credential",
    "`gh`": "GitHub worker",
}
ADAPTER_CANDIDATES = (
    Path(".agents/capability-catalog-adapter.yaml"),
)


def _sanitize(value: Any) -> Any:
    if isinstance(value, str):
        for source, replacement in TEXT_REPLACEMENTS.items():
            value = value.replace(source, replacement)
        return value
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize(item) for key, item in value.items()}
    return value


def _alias_path(path: str) -> str:
    for source, public in PROVIDER_ID_ALIASES.items():
        path = path.replace(f"{source}.json", f"{public}.json").replace(source, public)
    return path


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def _referenced_paths(path: Path, repo_root: Path) -> list[str]:
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
    paths: list[str] = []
    for token in re.findall(r"`([^`]+)`", text):
        if not (token == "adapter.example.yaml" or token.startswith(("references/", "scripts/", "../")) or token.endswith((".md", ".json", ".yaml", ".yml"))):
            continue
        candidate = (path.parent / token).resolve()
        try:
            relative = candidate.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            paths.append(relative.as_posix())
    return _dedupe(paths)


def _skill_entries(roots: list[tuple[str, Path]], *, repo_root: Path, layer: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for source, root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*/SKILL.md")):
            resolved = path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            front = _frontmatter(path)
            skill_id = path.parent.name
            name = front.get("name", skill_id)
            if skill_id in seen_ids or name in seen_names:
                continue
            seen_ids.add(skill_id)
            seen_names.add(name)
            try:
                rendered = path.relative_to(repo_root).as_posix()
                skill_dir = path.parent.relative_to(repo_root).as_posix()
            except ValueError:
                rendered, skill_dir = str(path), str(path.parent)
            entries.append({
                "id": skill_id,
                "name": name,
                "description": front.get("description", ""),
                "summary": front.get("description", ""),
                "path": rendered,
                "skill_dir": skill_dir,
                "canonical_path": rendered,
                "referenced_paths": _referenced_paths(path, repo_root),
                "source": source,
                "layer": layer,
            })
    return entries


def _sibling_support_root(root: Path) -> Path:
    return root.parent / "charness-support"


def _layers(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"layer_id": item["layer_id"], "layer_type": item["layer_type"], "summary": item["summary"]} for item in data.get("config_layers", [])]


def _checks(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"check_id": item["check_id"], "summary": item["summary"]} for item in data.get("readiness_checks", [])]


def integrations(root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for data in load_manifests_for_discovery(root):
        source_id = data["tool_id"]
        tool_id = PROVIDER_ID_ALIASES.get(source_id, source_id)
        support = data.get("support_skill_source")
        generated = generated_support_dir(root) / support_link_name(data) / "SKILL.md"
        support_path = generated.relative_to(root).as_posix() if support and generated.is_file() else None
        stub = root / ".agents" / "charness-discovery" / f"{tool_id}.md"
        entry = {
            "id": tool_id,
            "kind": "external capability" if source_id in PROVIDER_ID_ALIASES else data.get("kind", "unknown"),
            "summary": data.get("summary", ""),
            "access_modes": data.get("access_modes", []),
            "support_state": support_state_for_manifest(data),
            "support_skill_path": support_path,
            "discovery_stub_path": stub.relative_to(root).as_posix() if stub.is_file() else None,
            "capability_requirements": data.get("capability_requirements", {}),
            "config_layers": _layers(data),
            "readiness_checks": _checks(data),
            "supports_public_skills": data.get("supports_public_skills", []),
            "intent_triggers": data.get("intent_triggers", []),
            "strong_intent_triggers": data.get("strong_intent_triggers", []),
            "recommendation_role": data.get("recommendation_role"),
            "path": _alias_path(str(data["_manifest_path"])),
            "source": "local-integration" if data.get("_manifest_origin", "user-repo") == "user-repo" else "plugin-fallback-integration",
            "layer": "external integration",
        }
        result.append(_sanitize(entry))
    return result


def _support_caps(root: Path) -> list[dict[str, Any]]:
    values = list(load_support_capabilities(root))
    sibling = _sibling_support_root(root)
    for path in sorted(sibling.glob("*/capability.json")) if sibling.is_dir() else []:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["tool_id"] = data["capability_id"]
        data["_manifest_path"] = f"skills/support/{path.parent.name}/capability.json"
        data["support_skill_path"] = f"skills/support/{path.parent.name}/SKILL.md"
        values.append(data)
    result: list[dict[str, Any]] = []
    for data in values:
        tool_id = data["tool_id"]
        triggers = _dedupe([str(tool_id), str(data.get("display_name", "")), f"{tool_id} support", f"support/{tool_id}", *[str(item) for item in data.get("intent_triggers", [])]])
        result.append(_sanitize({
            "id": tool_id, "kind": data["kind"], "display_name": data.get("display_name", tool_id),
            "summary": data.get("summary", ""), "access_modes": data.get("access_modes", []),
            "capability_requirements": data.get("capability_requirements", {}), "config_layers": _layers(data),
            "readiness_checks": _checks(data), "path": data["_manifest_path"],
            "support_skill_path": data["support_skill_path"], "supports_public_skills": data.get("supports_public_skills", []),
            "source": "local-support-capability", "layer": "support capability", "trigger_phrases": triggers,
            "intent_triggers": data.get("intent_triggers", []),
            "strong_intent_triggers": data.get("strong_intent_triggers", []),
            "recommendation_role": data.get("recommendation_role"),
        }))
    return result


def load_adapter(repo_root: Path) -> dict[str, Any]:
    defaults: dict[str, Any] = {"version": 1, "repo": repo_root.name, "language": "en", "output_dir": "charness-artifacts/capability-catalog", "trusted_skill_roots": [], "prefer_local_first": True, "allow_external_registry": False}
    path = next((repo_root / item for item in ADAPTER_CANDIDATES if (repo_root / item).is_file()), None)
    warnings: list[str] = []
    errors: list[str] = []
    if path is None:
        warnings.append("No capability catalog adapter found; using local-first discovery defaults.")
    else:
        raw = load_yaml_file(path)
        if not isinstance(raw, dict):
            raw = {}
            warnings.append("Adapter file did not contain a mapping; using inferred defaults.")
        validate_adapter_version(raw, {}, errors)
        if not errors:
            for field in ("repo", "language", "preset_id", "preset_version", "customized_from"):
                value = optional_string(raw.get(field), field, errors)
                if value is not None:
                    defaults[field] = value
            roots = optional_string_list(raw.get("trusted_skill_roots", raw.get("official_skill_roots")), "trusted_skill_roots", errors)
            if roots is not None:
                defaults["trusted_skill_roots"] = roots
            for field in ("prefer_local_first", "allow_external_registry"):
                value = optional_bool(raw.get(field), field, errors)
                if value is not None:
                    defaults[field] = value
    return {"found": path is not None, "valid": not errors, "path": path.relative_to(repo_root).as_posix() if path else None, "data": defaults, "errors": errors, "warnings": warnings}


def build_inventory(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    adapter = load_adapter(root)
    support_roots = [("local-support", support_dir(root))]
    sibling = _sibling_support_root(root)
    if sibling.is_dir():
        support_roots.append(("sibling-support", sibling))
    # When the catalog is running from an installed plugin checkout, preserve
    # the old consumer-repo behavior: local surfaces win, while plugin-owned
    # public/support surfaces remain visible as fallback facts.
    source_root = Path(__file__).resolve().parent.parent
    plugin_roots = [source_root / "skills"]
    exported_root = source_root / "plugins" / "charness"
    if (source_root / ".codex-plugin" / "plugin.json").is_file():
        exported_root = source_root
    if (exported_root / ".codex-plugin" / "plugin.json").is_file():
        plugin_roots.insert(0, exported_root / "skills")
    if source_root != root:
        plugin_support = source_root / "skills" / "support"
        if (exported_root / "skills").is_dir():
            plugin_support = exported_root / "support"
        if plugin_support.is_dir():
            support_roots.append(("installed-plugin-support", plugin_support))
    support = _skill_entries(support_roots, repo_root=root, layer="support skill")
    support += _skill_entries([("synced-support", generated_support_dir(root))], repo_root=root, layer="synced support skill")
    public_roots = [("local-public", public_skills_dir(root))]
    if source_root != root:
        for plugin_root in plugin_roots:
            if plugin_root.is_dir():
                public_roots.append(("installed-plugin-public", plugin_root))
    public = _skill_entries(public_roots, repo_root=root, layer="public skill")
    trusted: list[dict[str, Any]] = []
    for index, relative in enumerate(adapter["data"].get("trusted_skill_roots", []), 1):
        trusted += _skill_entries([(f"trusted-root-{index}", (root / relative).resolve())], repo_root=root, layer="trusted skill")
    shadowed = {item["id"] for item in [*public, *support]} | {item["name"] for item in [*public, *support]}
    trusted = [item for item in trusted if item["id"] not in shadowed and item["name"] not in shadowed]
    return {"adapter": {"found": adapter["found"], "valid": adapter["valid"], "path": adapter["path"], "errors": adapter["errors"], "warnings": adapter["warnings"], "trusted_skill_roots": adapter["data"].get("trusted_skill_roots", []), "allow_external_registry": adapter["data"].get("allow_external_registry", False), "prefer_local_first": adapter["data"].get("prefer_local_first", True)}, "public_skills": public, "support_skills": support, "support_capabilities": _support_caps(root), "integrations": integrations(root), "trusted_skills": trusted}
