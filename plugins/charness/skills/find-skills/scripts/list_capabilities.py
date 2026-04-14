#!/usr/bin/env python3
# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


REPO_ROOT = _runtime_root()
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import load_support_capabilities  # noqa: E402
from scripts.repo_layout import generated_support_dir, public_skills_dir, support_dir  # noqa: E402
from scripts.support_sync_lib import support_link_name, support_state_for_manifest  # noqa: E402
from scripts.tool_recommendation_lib import recommendations_for_public_skill  # noqa: E402
from resolve_adapter import load_adapter  # noqa: E402


def _local_surface_root(target_root: Path) -> Path:
    return target_root if (REPO_ROOT / "skills" / "public").is_dir() else REPO_ROOT


def extract_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for raw in lines[1:]:
        if raw.strip() == "---":
            break
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def _render_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _collect_skill_entries(
    skill_roots: list[tuple[str, Path]],
    *,
    repo_root: Path,
    layer: str,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    seen_paths: set[Path] = set()
    for source_id, skill_root in skill_roots:
        if not skill_root.is_dir():
            continue
        for skill_md in sorted(skill_root.glob("*/SKILL.md")):
            resolved = skill_md.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            frontmatter = extract_frontmatter(skill_md)
            items.append(
                {
                    "id": skill_md.parent.name,
                    "name": frontmatter.get("name", skill_md.parent.name),
                    "description": frontmatter.get("description", ""),
                    "path": _render_path(skill_md, repo_root),
                    "source": source_id,
                    "layer": layer,
                }
            )
    return items


def materialized_support_skill_path(root: Path, manifest: dict[str, object]) -> str | None:
    support = manifest.get("support_skill_source")
    generated_skill = generated_support_dir(root) / support_link_name(manifest) / "SKILL.md"
    if not isinstance(support, dict) or not generated_skill.is_file():
        return None
    return str(generated_skill.relative_to(root))


def integrations(root: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for manifest in sorted((root / "integrations" / "tools").glob("*.json")):
        if manifest.name == "manifest.schema.json":
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        items.append(
            {
                "id": data.get("tool_id", manifest.stem),
                "kind": data.get("kind", "unknown"),
                "access_modes": data.get("access_modes", []),
                "support_state": support_state_for_manifest(data),
                "support_skill_path": materialized_support_skill_path(root, data),
                "capability_requirements": data.get("capability_requirements", {}),
                "config_layers": [
                    {
                        "layer_id": layer["layer_id"],
                        "layer_type": layer["layer_type"],
                        "summary": layer["summary"],
                    }
                    for layer in data.get("config_layers", [])
                ],
                "readiness_checks": [
                    {
                        "check_id": check["check_id"],
                        "summary": check["summary"],
                    }
                    for check in data.get("readiness_checks", [])
                ],
                "supports_public_skills": data.get("supports_public_skills", []),
                "recommendation_role": data.get("recommendation_role"),
                "path": str(manifest.relative_to(root)),
                "source": "local-integration",
                "layer": "external integration",
            }
        )
    return items


def support_capabilities(root: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for capability in load_support_capabilities(root):
        items.append(
            {
                "id": capability["tool_id"],
                "kind": capability["kind"],
                "access_modes": capability.get("access_modes", []),
                "capability_requirements": capability.get("capability_requirements", {}),
                "config_layers": [
                    {
                        "layer_id": layer["layer_id"],
                        "layer_type": layer["layer_type"],
                        "summary": layer["summary"],
                    }
                    for layer in capability.get("config_layers", [])
                ],
                "readiness_checks": [
                    {
                        "check_id": check["check_id"],
                        "summary": check["summary"],
                    }
                    for check in capability.get("readiness_checks", [])
                ],
                "path": capability["_manifest_path"],
                "support_skill_path": capability["support_skill_path"],
                "supports_public_skills": capability.get("supports_public_skills", []),
                "source": "local-support-capability",
                "layer": "support capability",
            }
        )
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--recommend-for-skill")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    local_root = _local_surface_root(root)
    adapter = load_adapter(root)
    trusted_skill_roots = adapter["data"].get("trusted_skill_roots", [])
    trusted_entries = _collect_skill_entries([(f"trusted-root-{index + 1}", (root / skill_root).resolve()) for index, skill_root in enumerate(trusted_skill_roots)], repo_root=root, layer="trusted skill")
    support_entries = _collect_skill_entries([("local-support", support_dir(local_root))], repo_root=local_root, layer="support skill")
    support_entries += _collect_skill_entries([("synced-support", generated_support_dir(local_root))], repo_root=local_root, layer="synced support skill")
    manifests = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((local_root / "integrations" / "tools").glob("*.json"))
        if path.name != "manifest.schema.json"
    ]
    payload = {
        "adapter": {
            "found": adapter["found"],
            "valid": adapter["valid"],
            "path": adapter["path"],
            "warnings": adapter["warnings"],
            "trusted_skill_roots": trusted_skill_roots,
            "allow_external_registry": adapter["data"].get("allow_external_registry", False),
            "prefer_local_first": adapter["data"].get("prefer_local_first", True),
        },
        "public_skills": _collect_skill_entries(
            [("local-public", public_skills_dir(local_root))],
            repo_root=local_root,
            layer="public skill",
        ),
        "support_skills": support_entries,
        "support_capabilities": support_capabilities(local_root),
        "integrations": integrations(local_root),
        "trusted_skills": trusted_entries,
        "tool_recommendations": (
            recommendations_for_public_skill(local_root, manifests, skill_id=args.recommend_for_skill)
            if args.recommend_for_skill
            else []
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
