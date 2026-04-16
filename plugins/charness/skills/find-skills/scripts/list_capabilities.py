#!/usr/bin/env python3
# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import json
import re
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

from capability_sources import integrations, support_capabilities  # noqa: E402
from scripts.repo_layout import generated_support_dir, public_skills_dir, support_dir  # noqa: E402
from scripts.tool_recommendation_lib import recommendations_for_public_skill  # noqa: E402
from resolve_adapter import load_adapter  # noqa: E402

REFERENCE_TOKEN_RE = re.compile(r"`([^`]+)`")

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

def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result

def _skill_trigger_phrases(name: str, layer: str) -> list[str]:
    phrases = [
        name,
        f"{name} skill",
        f"{name} 스킬",
        f"charness:{name}",
    ]
    if "support" in layer:
        phrases.extend(
            [
                f"support/{name}",
                f"{name} support",
                f"{name} support skill",
                f"{name} helper",
            ]
        )
    return _dedupe(phrases)

def _referenced_skill_paths(skill_md: Path, repo_root: Path) -> list[str]:
    text = skill_md.read_text(encoding="utf-8")
    paths: list[str] = []
    for match in REFERENCE_TOKEN_RE.findall(text):
        token = match.strip()
        if not (
            token == "adapter.example.yaml"
            or token.startswith("references/")
            or token.startswith("scripts/")
        ):
            continue
        candidate = skill_md.parent / token
        if candidate.is_file():
            paths.append(_render_path(candidate, repo_root))
    return _dedupe(paths)

def _collect_skill_entries(
    skill_roots: list[tuple[str, Path]],
    *,
    repo_root: Path,
    layer: str,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    seen_paths: set[Path] = set()
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for source_id, skill_root in skill_roots:
        if not skill_root.is_dir():
            continue
        for skill_md in sorted(skill_root.glob("*/SKILL.md")):
            resolved = skill_md.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            frontmatter = extract_frontmatter(skill_md)
            name = frontmatter.get("name", skill_md.parent.name)
            if skill_md.parent.name in seen_ids or name in seen_names:
                continue
            seen_ids.add(skill_md.parent.name)
            seen_names.add(name)
            description = frontmatter.get("description", "")
            items.append(
                {
                    "id": skill_md.parent.name,
                    "name": name,
                    "description": description,
                    "summary": description,
                    "path": _render_path(skill_md, repo_root),
                    "skill_dir": _render_path(skill_md.parent, repo_root),
                    "canonical_path": _render_path(skill_md, repo_root),
                    "trigger_phrases": _skill_trigger_phrases(name, layer),
                    "referenced_paths": _referenced_skill_paths(skill_md, repo_root),
                    "source": source_id,
                    "layer": layer,
                }
            )
    return items


def _filter_shadowed(entries: list[dict[str, str]], preferred: list[dict[str, str]]) -> list[dict[str, str]]:
    preferred_ids = {entry["id"] for entry in preferred}
    preferred_names = {entry["name"] for entry in preferred}
    return [entry for entry in entries if entry["id"] not in preferred_ids and entry["name"] not in preferred_names]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--recommend-for-skill")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    local_root = _local_surface_root(root)
    adapter = load_adapter(root)
    trusted_skill_roots = adapter["data"].get("trusted_skill_roots", [])
    support_entries = _collect_skill_entries([("local-support", support_dir(local_root))], repo_root=local_root, layer="support skill")
    support_entries += _collect_skill_entries([("synced-support", generated_support_dir(local_root))], repo_root=local_root, layer="synced support skill")
    public_entries = _collect_skill_entries(
        [("local-public", public_skills_dir(local_root))],
        repo_root=local_root,
        layer="public skill",
    )
    trusted_entries = _collect_skill_entries(
        [(f"trusted-root-{index + 1}", (root / skill_root).resolve()) for index, skill_root in enumerate(trusted_skill_roots)],
        repo_root=root,
        layer="trusted skill",
    )
    trusted_entries = _filter_shadowed(trusted_entries, [*public_entries, *support_entries])
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
        "public_skills": public_entries,
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
