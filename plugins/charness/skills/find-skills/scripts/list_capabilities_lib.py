#!/usr/bin/env python3
from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

REFERENCE_TOKEN_RE = re.compile(r"`([^`]+)`")
# Temporary canonical source for workflow integrations until a manifest-backed
# workflow registry exists.
WORKFLOW_RECOMMENDATIONS = [
    {
        "id": "worktree-create",
        "intent": "create",
        "layer": "workflow integration",
        "path": "integrations/worktree/adapter.example.yaml",
        "summary": "Create and prepare git worktrees through the Charness worktree CLI.",
        "triggers": [
            "worktree",
            "git worktree",
            "create worktree",
            "add worktree",
            "worktree create",
            "worktree add",
            "fresh worktree",
            "new worktree",
            "prepare worktree",
        ],
        "next_step": "Use `charness worktree create --prepare --path <path> --branch <branch> --base <ref>` instead of raw `git worktree add` when the operator wants adapter-declared setup to run immediately.",
    },
    {
        "id": "worktree-cleanup",
        "intent": "cleanup",
        "layer": "workflow integration",
        "path": "integrations/worktree/adapter.example.yaml",
        "summary": "Safely remove finished git worktrees through the Charness worktree CLI.",
        "triggers": [
            "cleanup worktree",
            "clean up worktree",
            "remove worktree",
            "delete worktree",
            "worktree cleanup",
            "worktree remove",
            "worktree teardown",
        ],
        "next_step": "Use `charness worktree cleanup --path <worktree>` for a dry-run plan; add `--delete-merged-branch --yes` only after local branch containment is the intended cleanup policy.",
    },
]


def workflow_integrations() -> list[dict[str, Any]]:
    return [
        {
            "id": workflow["id"],
            "layer": workflow["layer"],
            "path": workflow["path"],
            "summary": workflow["summary"],
            "trigger_phrases": workflow["triggers"],
            "next_step": workflow["next_step"],
        }
        for workflow in WORKFLOW_RECOMMENDATIONS
    ]


def resolve_tool_recommendations(
    args: Any,
    *,
    local_root: Any,
    manifests: list[dict[str, Any]],
    recommendations_for_public_skill: Any,
    recommendations_for_role: Any,
    recommendations_for_task: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if args.recommend_for_skill:
        return recommendations_for_public_skill(local_root, manifests, skill_id=args.recommend_for_skill), {
            "mode": "public_skill",
            "skill_id": args.recommend_for_skill,
        }
    if args.recommendation_role:
        next_skill_id = args.next_skill_id or "quality"
        return recommendations_for_role(
            local_root,
            manifests,
            recommendation_role=args.recommendation_role,
            next_skill_id=next_skill_id,
            only_blocking=args.only_blocking,
        ), {
            "mode": "recommendation_role",
            "recommendation_role": args.recommendation_role,
            "next_skill_id": next_skill_id,
            "only_blocking": args.only_blocking,
        }
    if args.recommend_for_task:
        return recommendations_for_task(
            local_root,
            manifests,
            task_text=args.recommend_for_task,
            next_skill_id=args.next_skill_id,
            only_blocking=args.only_blocking,
        ), {
            "mode": "task_text",
            "task_text": args.recommend_for_task,
            "next_skill_id": args.next_skill_id,
            "only_blocking": args.only_blocking,
        }
    return [], None


def _strings(items: Iterable[Any]) -> list[str]:
    return [item for item in items if isinstance(item, str) and item]


def _dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _render_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _strip_fenced_code_blocks(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence:
            lines.append(line)
    return "\n".join(lines)


def referenced_skill_paths(skill_md: Path, repo_root: Path) -> list[str]:
    text = _strip_fenced_code_blocks(skill_md.read_text(encoding="utf-8"))
    paths: list[str] = []
    for match in REFERENCE_TOKEN_RE.findall(text):
        token = match.strip()
        if not (
            token == "adapter.example.yaml"
            or token.startswith("references/")
            or token.startswith("scripts/")
            or token.startswith("../")
            or token.endswith((".md", ".json", ".yaml", ".yml"))
        ):
            continue
        candidate = (skill_md.parent / token).resolve()
        try:
            candidate.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            paths.append(_render_path(candidate, repo_root))
    return _dedupe(paths)


def _task_text_matches(task_text: str, candidate: str) -> bool:
    normalized = candidate.casefold().strip()
    return bool(normalized) and normalized in task_text.casefold()


def _task_words(task_text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", task_text.casefold()))


def _cleanup_worktree_intent(task_text: str) -> bool:
    normalized = task_text.casefold()
    words = _task_words(task_text)
    return "worktree" in words and (
        bool(words & {"cleanup", "remove", "delete", "teardown"})
        or "clean up" in normalized
    )


def _strong_triggers_for(skill_id: str, integrations: list[dict[str, Any]]) -> set[str] | None:
    """Return the casefolded `strong_intent_triggers` declared for ``skill_id`` in an
    integration manifest, or ``None`` when no manifest pins the strong subset.

    A non-empty declared list means at least one matched trigger must come from
    that subset before the support skill is surfaced — narrower than `intent_triggers`,
    which is the broad task-text-match pool. Missing field = no gate (broad pool only).
    """

    for integration in integrations:
        if integration.get("id") != skill_id and integration.get("tool_id") != skill_id:
            continue
        declared = integration.get("strong_intent_triggers")
        if isinstance(declared, list) and declared:
            return {item.casefold() for item in declared if isinstance(item, str)}
        return None
    return None


def _enough_task_signal(
    skill_id: str, matched: list[str], integrations: list[dict[str, Any]]
) -> bool:
    strong = _strong_triggers_for(skill_id, integrations)
    if strong is None:
        return bool(matched)
    return any(item.casefold() in strong for item in matched)


def _support_skill_triggers(
    entry: dict[str, Any],
    *,
    support_capabilities: list[dict[str, Any]],
    integrations: list[dict[str, Any]],
) -> list[str]:
    skill_id = entry.get("id")
    skill_path = entry.get("canonical_path") or entry.get("path")
    triggers = [
        *_strings(entry.get("trigger_phrases", [])),
        *_strings([entry.get("id"), entry.get("name"), entry.get("description")]),
    ]
    for cap in support_capabilities:
        if cap.get("support_skill_path") == skill_path or cap.get("id") == skill_id:
            triggers.extend(_strings(cap.get("trigger_phrases", [])) + _strings(cap.get("intent_triggers", [])))
    for integration in integrations:
        if integration.get("id") == skill_id or integration.get("support_skill_path") == skill_path:
            triggers.extend(_strings(integration.get("intent_triggers", [])))
    return _dedupe(triggers)


def support_recommendations_for_task(
    task_text: str,
    *,
    support_entries: list[dict[str, Any]],
    support_capabilities: list[dict[str, Any]],
    integrations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for entry in support_entries:
        triggers = _support_skill_triggers(
            entry,
            support_capabilities=support_capabilities,
            integrations=integrations,
        )
        matched = [trigger for trigger in triggers if _task_text_matches(task_text, trigger)]
        if not matched or not _enough_task_signal(str(entry["id"]), matched, integrations):
            continue
        recommendations.append(
            {
                "id": entry["id"],
                "layer": entry["layer"],
                "path": entry["path"],
                "summary": entry["summary"],
                "matched_triggers": matched,
                "referenced_paths": entry.get("referenced_paths", []),
                "next_step": f"Read `{entry['path']}` before modifying or running this support-backed surface.",
            }
        )
    return recommendations


def workflow_recommendations_for_task(task_text: str) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    cleanup_intent = _cleanup_worktree_intent(task_text)
    for workflow in WORKFLOW_RECOMMENDATIONS:
        if cleanup_intent and workflow.get("intent") == "create":
            continue
        matched = [trigger for trigger in workflow["triggers"] if _task_text_matches(task_text, trigger)]
        if not matched and cleanup_intent and workflow.get("intent") == "cleanup":
            matched = ["cleanup+worktree"]
        if not matched:
            continue
        recommendations.append(
            {
                "id": workflow["id"],
                "layer": workflow["layer"],
                "path": workflow["path"],
                "summary": workflow["summary"],
                "matched_triggers": matched,
                "next_step": workflow["next_step"],
            }
        )
    return recommendations


def _validation_shaped_task(query: dict[str, Any] | None) -> bool:
    if not isinstance(query, dict):
        return False
    task_text = query.get("task_text")
    if not isinstance(task_text, str):
        return False
    normalized = task_text.casefold()
    return any(token in normalized for token in ("validate", "validation", "evaluate", "eval", "검증", "평가"))


def build_inventory_payload(
    *,
    adapter: dict[str, Any],
    trusted_skill_roots: list[str],
    public_entries: list[dict[str, Any]],
    support_entries: list[dict[str, Any]],
    support_capabilities: list[dict[str, Any]],
    integrations: list[dict[str, Any]],
    trusted_entries: list[dict[str, Any]],
    tool_recommendations: list[dict[str, Any]],
    recommendation_query: dict[str, Any] | None,
    support_skill_recommendations: list[dict[str, Any]] | None = None,
    support_recommendation_query: dict[str, Any] | None = None,
    workflow_recommendations: list[dict[str, Any]] | None = None,
    workflow_integrations: list[dict[str, Any]] | None = None,
    public_skill_recommendations: list[dict[str, Any]] | None = None,
    public_recommendation_query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    show_note = (
        support_recommendation_query is not None
        and not support_skill_recommendations
        and not tool_recommendations
        and not workflow_recommendations
        and not public_skill_recommendations
        and (support_entries or _validation_shaped_task(support_recommendation_query))
    )
    note = (
        f"No support skill matched the task text via registered intent_triggers, but "
        f"{len(support_entries)} support skill(s) are available locally. Inspect `support_skills` "
        "or rerun with --recommend-for-skill <id>; empty result is not proof that no capability exists. "
        "For validation-shaped requests, rerun with "
        "`--recommendation-role validation --next-skill-id <skill-id>`."
    ) if show_note else None
    return {
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
        "support_capabilities": support_capabilities,
        "integrations": integrations,
        "workflow_integrations": workflow_integrations or [],
        "trusted_skills": trusted_entries,
        "tool_recommendations": tool_recommendations,
        "tool_recommendation_query": recommendation_query,
        "support_skill_recommendations": support_skill_recommendations or [],
        "support_recommendation_query": support_recommendation_query,
        "workflow_recommendations": workflow_recommendations or [],
        "public_skill_recommendations": public_skill_recommendations or [],
        "public_recommendation_query": public_recommendation_query,
        "support_recommendation_note": note,
    }
