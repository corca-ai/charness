#!/usr/bin/env python3
from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

REFERENCE_TOKEN_RE = re.compile(r"`([^`]+)`")

# Advisory interpretation contract (see shared/references/
# advisory-interpretation-contract.md): the recommendation RANKING is an
# inference-layer proxy, so it self-declares blind spots and the question the
# routing consumer must answer. NOTE: this rides only the recommendation output,
# never the capability *inventory* (the list of installed skills/paths/triggers
# is a verified fact and stays trusted). Field values are single-line by design to
# keep this capability module under its length warn band.
RECOMMENDATION_INTERPRETATION = {
    "measures": "trigger / intent-phrase and task-text overlap between the request and registered skill/support/tool metadata, ranked into a recommended route",
    "proxy_for": "which installed capability actually fits the task",
    "blind_spots": "matches declared trigger vocabulary, not task semantics — a strong phrase match can still be the wrong route, and a genuinely-fitting skill whose metadata lacks the phrase ranks low or is absent; an empty ranking is not proof that no capability exists",
    "interpretation_question": "does the top-ranked route actually fit THIS task and repo state, or is it a trigger-phrase coincidence (and is a better-fitting skill missing from the ranking)?",
}

# North-star "brief the judge with the next move": when a ranking exists the
# deterministic inventory does not just emit the self-declaration above and hope the
# consumer reads its reference doc — it hands the agent the active next step, so
# routing-on-a-proxy is a move it consciously takes rather than a default it slides
# into. This is a plain routing imperative, NOT a 4-field interpretation declaration:
# it rides only the recommendation surface and is stripped from the canonical
# inventory artifact (see inventory_artifact._canonical_inventory).
ROUTING_NEXT_STEP = (
    "Before routing on this ranking, answer its interpretation question in your own "
    "words against THIS repo (see recommendation_interpretation.interpretation_question; "
    "the tie-break rules and ranking-interpretation framing live in this skill's "
    "references/discovery-order.md): does the top route actually fit this task, or is it "
    "a trigger-phrase coincidence — and is a better-fitting capability missing? Then "
    "invoke the confirmed route, widen the search, or classify the gap. A thin or empty "
    "ranking is not proof a capability is absent."
)
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


def shipped_support_recommendations_for_task(
    task_text: str,
    *,
    integrations: list[dict[str, Any]],
    materialized_support_ids: set[str],
) -> list[dict[str, Any]]:
    """Surface a SHIPPED charness-support skill (``support_skill_source``) through support
    routing even when not materialized locally — ``support_recommendations_for_task`` misses
    it, so the agent treats the binary as opaque. Skips materialized + binary-only."""
    recommendations: list[dict[str, Any]] = []
    for integration in integrations:
        tool_id = integration.get("id")
        if not tool_id or tool_id in materialized_support_ids:
            continue
        if integration.get("support_state") in (None, "integration-only"):
            continue
        triggers = _dedupe(_strings(integration.get("intent_triggers", [])))
        matched = [trigger for trigger in triggers if _task_text_matches(task_text, trigger)]
        if not matched or not _enough_task_signal(str(tool_id), matched, integrations):
            continue
        path = integration.get("support_skill_path")
        next_step = (
            f"Read `{path}` — the shipped support skill for `{tool_id}`." if path
            else f"`{tool_id}` ships a charness-support skill that materializes under "
            f"`support/{tool_id}/` on `charness update`; read it through support routing "
            "instead of reverse-engineering the binary."
        )
        recommendations.append({
            "id": tool_id,
            "layer": "synced support skill",
            "path": path or integration.get("path"),
            "summary": integration.get("summary", ""),
            "matched_triggers": matched,
            "support_state": integration.get("support_state"),
            "next_step": next_step,
        })
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
    has_recommendations = any([tool_recommendations, support_skill_recommendations, workflow_recommendations, public_skill_recommendations])
    next_step = ROUTING_NEXT_STEP if has_recommendations else None
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
        # Active next move the script hands the judge; rides the ranking only and is
        # stripped from the canonical inventory artifact, so a no-ranking run stays clean.
        "next_step": next_step,
        # Inference-layer self-declaration rides the ranking only; absent when no
        # recommendation was produced so it never attaches to the verified inventory.
        **({"recommendation_interpretation": dict(RECOMMENDATION_INTERPRETATION)} if has_recommendations else {}),
    }
