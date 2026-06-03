#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_capability_sources = SKILL_RUNTIME.load_local_skill_module(__file__, "capability_sources")
integrations, support_capabilities = _capability_sources.integrations, _capability_sources.support_capabilities
load_manifests = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.control_plane_lib").load_manifests_for_discovery
_layout = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.repo_layout")
generated_support_dir, public_skills_dir, support_dir = _layout.generated_support_dir, _layout.public_skills_dir, _layout.support_dir
_tool_rec = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.tool_recommendation_lib")
recommendations_for_public_skill = _tool_rec.recommendations_for_public_skill
recommendations_for_role = _tool_rec.recommendations_for_role
recommendations_for_task = _tool_rec.recommendations_for_task
_list_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "list_capabilities_lib")
build_inventory_payload, referenced_skill_paths = _list_lib.build_inventory_payload, _list_lib.referenced_skill_paths
resolve_tool_recommendations, support_recommendations_for_task = _list_lib.resolve_tool_recommendations, _list_lib.support_recommendations_for_task
workflow_integrations = _list_lib.workflow_integrations
workflow_recommendations_for_task = _list_lib.workflow_recommendations_for_task
_public_rec = SKILL_RUNTIME.load_local_skill_module(__file__, "public_skill_recommendations")
public_skill_recommendations_for_task = _public_rec.public_skill_recommendations_for_task
_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "inventory_artifact")
persist_inventory, read_only_inventory_artifacts = _artifact.persist_inventory, _artifact.read_only_inventory_artifacts
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter

def _target_has_repo_owned_skill_surface(target_root: Path) -> bool:
    return (target_root / "skills" / "public").is_dir() or (target_root / "skills" / "support").is_dir()

def _local_surface_root(target_root: Path) -> Path:
    if (REPO_ROOT / "skills" / "public").is_dir():
        return target_root
    return target_root if _target_has_repo_owned_skill_surface(target_root) else REPO_ROOT


@dataclass(frozen=True)
class SkillRoot:
    source_id: str
    path: Path
    display_prefix: Path | None = None

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
def _render_path(path: Path, repo_root: Path, skill_root: SkillRoot | None = None) -> str:
    if skill_root is not None and skill_root.display_prefix is not None:
        try:
            relative = path.relative_to(skill_root.path)
        except ValueError:
            pass
        else:
            return (skill_root.display_prefix / relative).as_posix()
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
    if name == "quality":
        phrases.extend(["test quality", "testability", "quality gate"])
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
def _collect_skill_entries(
    skill_roots: list[SkillRoot],
    *,
    repo_root: Path,
    layer: str,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    seen_paths: set[Path] = set()
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for skill_root in skill_roots:
        if not skill_root.path.is_dir():
            continue
        for skill_md in sorted(skill_root.path.glob("*/SKILL.md")):
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
                    "path": _render_path(skill_md, repo_root, skill_root),
                    "skill_dir": _render_path(skill_md.parent, repo_root, skill_root),
                    "canonical_path": _render_path(skill_md, repo_root, skill_root),
                    "trigger_phrases": _skill_trigger_phrases(name, layer),
                    "referenced_paths": referenced_skill_paths(skill_md, repo_root),
                    "source": skill_root.source_id,
                    "layer": layer,
                }
            )
    return items

def _filter_shadowed(entries: list[dict[str, str]], preferred: list[dict[str, str]]) -> list[dict[str, str]]:
    preferred_ids = {entry["id"] for entry in preferred}
    preferred_names = {entry["name"] for entry in preferred}
    return [entry for entry in entries if entry["id"] not in preferred_ids and entry["name"] not in preferred_names]


def _sibling_support_root(root: Path) -> Path:
    return root.parent / "charness-support"


def _support_skill_roots(local_root: Path) -> list[SkillRoot]:
    roots = [SkillRoot("local-support", support_dir(local_root))]
    sibling_support = _sibling_support_root(local_root)
    if sibling_support.is_dir():
        roots.append(SkillRoot("sibling-support", sibling_support, Path("skills/support")))
    return roots


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to scan for installed skills, support capabilities, and integrations")
    recommendation_group = parser.add_mutually_exclusive_group()
    recommendation_group.add_argument("--recommend-for-skill", help="Public skill id to score tool/support routes against (e.g. impl, quality)")
    recommendation_group.add_argument("--recommendation-role", choices=("runtime", "validation"), help="Limit recommendation route to runtime tooling or validation tooling for the named skill")
    recommendation_group.add_argument("--recommend-for-task", help="Free-text task summary to score against the capability inventory and return best-fit skills/support/integrations")
    parser.add_argument("--next-skill-id", help="Skill id the caller plans to invoke next; pairs with --recommendation-role to focus the route")
    parser.add_argument("--only-blocking", action="store_true", help="Filter recommendations to entries that are blocking for the requested skill/role")
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Skip durable inventory artifact write; emit inventory payload to stdout only.",
    )
    parser.add_argument(
        "--write-artifact",
        action="store_true",
        help="Force a durable inventory artifact write even for recommendation-shaped queries.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Emit a compact JSON summary with counts and recommendation results instead of the full inventory arrays.",
    )
    return parser.parse_args()


def _is_recommendation_query(args: argparse.Namespace) -> bool:
    return bool(args.recommend_for_task or args.recommend_for_skill or args.recommendation_role)


def _summary_payload(payload: dict[str, object]) -> dict[str, object]:
    counts: dict[str, int] = {}
    for key in (
        "public_skills",
        "support_skills",
        "support_capabilities",
        "integrations",
        "workflow_integrations",
        "trusted_skills",
    ):
        value = payload.get(key)
        counts[key] = len(value) if isinstance(value, list) else 0
    return {
        "mode": "summary",
        "adapter": payload.get("adapter"),
        "counts": counts,
        "artifacts": payload.get("artifacts"),
        "recommendations": {
            "tool_recommendations": payload.get("tool_recommendations", []),
            "tool_recommendation_query": payload.get("tool_recommendation_query"),
            "support_skill_recommendations": payload.get("support_skill_recommendations", []),
            "support_recommendation_query": payload.get("support_recommendation_query"),
            "support_recommendation_note": payload.get("support_recommendation_note"),
            "workflow_recommendations": payload.get("workflow_recommendations", []),
            "public_skill_recommendations": payload.get("public_skill_recommendations", []),
            "public_recommendation_query": payload.get("public_recommendation_query"),
        },
    }


def main() -> None:
    args = _parse_args()
    root = args.repo_root.resolve()
    local_root = _local_surface_root(root)
    adapter = load_adapter(root)
    trusted_skill_roots = adapter["data"].get("trusted_skill_roots", [])
    support_roots = _support_skill_roots(local_root)
    if REPO_ROOT != local_root and (REPO_ROOT / ".codex-plugin" / "plugin.json").is_file() and support_dir(REPO_ROOT).is_dir():
        support_roots.append(SkillRoot("installed-plugin-support", support_dir(REPO_ROOT)))
    support_entries = _collect_skill_entries(support_roots, repo_root=local_root, layer="support skill")
    support_entries += _collect_skill_entries([SkillRoot("synced-support", generated_support_dir(local_root))], repo_root=local_root, layer="synced support skill")
    public_entries = _collect_skill_entries(
        [SkillRoot("local-public", public_skills_dir(local_root))],
        repo_root=local_root,
        layer="public skill",
    )
    trusted_entries = _collect_skill_entries(
        [
            SkillRoot(f"trusted-root-{index + 1}", (root / skill_root).resolve())
            for index, skill_root in enumerate(trusted_skill_roots)
        ],
        repo_root=root,
        layer="trusted skill",
    )
    trusted_entries = _filter_shadowed(trusted_entries, [*public_entries, *support_entries])
    manifests = load_manifests(local_root)
    support_capability_entries = support_capabilities(local_root)
    integration_entries = integrations(local_root)
    tool_recommendations, recommendation_query = resolve_tool_recommendations(
        args,
        local_root=local_root,
        manifests=manifests,
        recommendations_for_public_skill=recommendations_for_public_skill,
        recommendations_for_role=recommendations_for_role,
        recommendations_for_task=recommendations_for_task,
    )
    support_skill_recommendations = []
    support_recommendation_query = None
    workflow_recommendations = []
    public_skill_recommendations = []
    public_recommendation_query = None
    if args.recommend_for_task:
        support_skill_recommendations = support_recommendations_for_task(
            args.recommend_for_task,
            support_entries=support_entries,
            support_capabilities=support_capability_entries,
            integrations=integration_entries,
        )
        workflow_recommendations = workflow_recommendations_for_task(args.recommend_for_task)
        public_skill_recommendations = public_skill_recommendations_for_task(
            args.recommend_for_task,
            public_entries=public_entries,
        )
        support_recommendation_query = {
            "mode": "task_text",
            "task_text": args.recommend_for_task,
        }
        public_recommendation_query = {
            "mode": "task_text",
            "task_text": args.recommend_for_task,
        }
    payload = build_inventory_payload(
        adapter=adapter,
        trusted_skill_roots=trusted_skill_roots,
        public_entries=public_entries,
        support_entries=support_entries,
        support_capabilities=support_capability_entries,
        integrations=integration_entries,
        trusted_entries=trusted_entries,
        tool_recommendations=tool_recommendations,
        recommendation_query=recommendation_query,
        support_skill_recommendations=support_skill_recommendations,
        support_recommendation_query=support_recommendation_query,
        workflow_recommendations=workflow_recommendations,
        workflow_integrations=workflow_integrations(),
        public_skill_recommendations=public_skill_recommendations,
        public_recommendation_query=public_recommendation_query,
    )
    if args.read_only or (_is_recommendation_query(args) and not args.write_artifact):
        payload["artifacts"] = read_only_inventory_artifacts()
    else:
        try:
            payload["artifacts"] = persist_inventory(
                repo_root=root,
                output_dir=root / adapter["data"]["output_dir"],
                inventory=payload,
            )
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
    output_payload = _summary_payload(payload) if args.summary else payload
    print(json.dumps(output_payload, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
