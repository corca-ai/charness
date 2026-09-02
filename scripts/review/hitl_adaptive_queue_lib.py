from __future__ import annotations

from typing import Any

DECISION_VALUES = ("unreviewed", "approve", "request_changes", "comment_only", "defer")
QUEUE_EFFECT_TYPES = {
    "boost_tag",
    "deprioritize_tag",
    "supersede_tag",
    "supersede_item",
    "recommend_restart",
}
LEVEL_SCORES = {"high": 3, "medium": 2, "low": 1}
CONTEXT_COST_SCORES = {"low": 3, "medium": 2, "high": 1}


def first_string(*values: object, default: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def string_list(raw: object) -> list[str]:
    if isinstance(raw, str):
        return [raw.strip()] if raw.strip() else []
    if not isinstance(raw, list):
        return []
    values: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            values.append(item.strip())
    return values


def first_int(*values: object, default: int) -> int:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                continue
    return default


def normalize_priority(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    return {
        "leverage": first_string(raw.get("leverage"), raw.get("decision_leverage")).lower(),
        "risk": first_string(raw.get("risk")).lower(),
        "uncertainty": first_string(raw.get("uncertainty")).lower(),
        "context_cost": first_string(raw.get("context_cost")).lower(),
        "rule_seed": bool(raw.get("rule_seed", False)),
        "score": first_int(raw.get("score"), default=0),
        "reason": first_string(raw.get("reason"), raw.get("why_next"), raw.get("score_explanation")),
    }


def item_uses_adaptive_metadata(raw_item: dict[str, Any], packet: dict[str, Any]) -> bool:
    adaptive_keys = {
        "priority",
        "depends_on",
        "blocks",
        "tags",
        "source_order",
        "why_next",
        "score_explanation",
    }
    return bool(packet.get("adaptive_queue")) or any(key in raw_item for key in adaptive_keys)


def normalize_queue_effects(raw: object) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    effects: list[dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            continue
        effect_type = first_string(item.get("type"), item.get("action"))
        if effect_type not in QUEUE_EFFECT_TYPES:
            raise ValueError(f"queue effect {index} has unsupported type `{effect_type}`")
        effects.append(
            {
                "type": effect_type,
                "tag": first_string(item.get("tag")),
                "tags": string_list(item.get("tags")),
                "item_ids": string_list(
                    item.get("item_ids") or item.get("items") or item.get("superseded_item_ids")
                ),
                "reason": first_string(item.get("reason"), item.get("why")),
                "recommended_next_step": first_string(
                    item.get("recommended_next_step"),
                    item.get("agent_next_step"),
                    default="Apply accepted feedback, then restart HITL with a fresh queue.",
                ),
            }
        )
    return effects


def normalize_review_input(review_input: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if review_input is None:
        return {}
    raw_items = review_input.get("items")
    if isinstance(raw_items, dict):
        iterable = [dict(value, id=item_id) for item_id, value in raw_items.items() if isinstance(value, dict)]
    elif isinstance(raw_items, list):
        iterable = raw_items
    elif isinstance(review_input.get("decisions"), dict):
        iterable = [
            dict(value, id=item_id)
            for item_id, value in review_input["decisions"].items()
            if isinstance(value, dict)
        ]
    else:
        iterable = []
    normalized: dict[str, dict[str, Any]] = {}
    for item in iterable:
        if not isinstance(item, dict):
            continue
        item_id = first_string(item.get("id"))
        decision = first_string(item.get("decision"), default="unreviewed")
        if item_id and decision not in DECISION_VALUES:
            raise ValueError(f"review input item `{item_id}` has unsupported decision `{decision}`")
        if item_id:
            queue_effects = normalize_queue_effects(item.get("queue_effects") or item.get("effects"))
            comment = first_string(item.get("comment"), item.get("notes"))
            if queue_effects and decision == "unreviewed" and not comment:
                raise ValueError(
                    f"review input item `{item_id}` with queue effects must include an explicit decision or comment"
                )
            normalized[item_id] = {"decision": decision, "comment": comment, "queue_effects": queue_effects}
    return normalized


def validate_review_input_ids(items: list[dict[str, Any]], review_input: dict[str, dict[str, Any]]) -> None:
    item_ids = {item["id"] for item in items}
    unknown_ids = sorted(item_id for item_id in review_input if item_id not in item_ids)
    if unknown_ids:
        raise ValueError(f"review input references unknown item id(s): {', '.join(unknown_ids)}")


def reviewed_item_ids(review_input: dict[str, dict[str, Any]]) -> set[str]:
    reviewed: set[str] = set()
    for item_id, submitted in review_input.items():
        if submitted.get("decision") != "unreviewed" or submitted.get("comment") or submitted.get("queue_effects"):
            reviewed.add(item_id)
    return reviewed


def collect_queue_effects(review_input: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    effects: list[dict[str, Any]] = []
    for item_id, submitted in review_input.items():
        for effect in submitted.get("queue_effects", []):
            effects.append({**effect, "source_item_id": item_id})
    return effects


def tags_for_effect(effect: dict[str, Any]) -> set[str]:
    tags = set(effect.get("tags", []))
    tag = effect.get("tag")
    if tag:
        tags.add(str(tag))
    return tags


def queue_effect_summary(items: list[dict[str, Any]], review_input: dict[str, dict[str, Any]]) -> dict[str, Any]:
    effects = collect_queue_effects(review_input)
    item_by_id = {item["id"]: item for item in items}
    superseded_ids: set[str] = set()
    boost_tags: set[str] = set()
    deprioritize_tags: set[str] = set()
    restart_recommendation: dict[str, Any] | None = None
    for effect in effects:
        effect_type = effect["type"]
        if effect_type == "boost_tag":
            boost_tags.update(tags_for_effect(effect))
        elif effect_type == "deprioritize_tag":
            deprioritize_tags.update(tags_for_effect(effect))
        elif effect_type == "supersede_item":
            superseded_ids.update(effect["item_ids"])
        elif effect_type == "supersede_tag":
            target_tags = tags_for_effect(effect)
            superseded_ids.update(item["id"] for item in items if target_tags.intersection(set(item["tags"])))
        elif effect_type == "recommend_restart":
            superseded_ids.update(effect["item_ids"])
            restart_recommendation = {
                "status": "invalidation_recommended",
                "triggering_decision_id": effect["source_item_id"],
                "reason": effect["reason"],
                "recommended_next_step": effect["recommended_next_step"],
            }
    reviewed_ids = reviewed_item_ids(review_input)
    superseded_ids.difference_update(reviewed_ids)
    unknown_superseded = sorted(item_id for item_id in superseded_ids if item_id not in item_by_id)
    if unknown_superseded:
        raise ValueError(f"queue effect references unknown item id(s): {', '.join(unknown_superseded)}")
    return {
        "boost_tags": boost_tags,
        "deprioritize_tags": deprioritize_tags,
        "superseded_ids": superseded_ids,
        "restart_recommendation": restart_recommendation,
    }


def level_score(value: str, scores: dict[str, int] = LEVEL_SCORES) -> int:
    return scores.get(value, 0)


def priority_score(item: dict[str, Any], reviewed_ids: set[str], effect_summary: dict[str, Any]) -> int:
    priority = item["priority"]
    score = int(priority.get("score", 0))
    score += len(item["blocks"]) * 100
    score += 30 if priority.get("rule_seed") else 0
    score += level_score(priority["leverage"]) * 30
    score += level_score(priority["risk"]) * 20
    score += level_score(priority["uncertainty"]) * 10
    score += level_score(priority["context_cost"], CONTEXT_COST_SCORES) * 5
    tags = set(item["tags"])
    if tags.intersection(effect_summary["boost_tags"]):
        score += 1000
    if tags.intersection(effect_summary["deprioritize_tags"]):
        score -= 1000
    if [item_id for item_id in item["depends_on"] if item_id not in reviewed_ids]:
        score -= 10000
    return score


def order_items(
    items: list[dict[str, Any]],
    review_input: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reviewed_ids = reviewed_item_ids(review_input)
    effect_summary = queue_effect_summary(items, review_input)
    superseded_ids = effect_summary["superseded_ids"]
    remaining = [item for item in items if item["id"] not in reviewed_ids and item["id"] not in superseded_ids]
    ordered = sorted(
        remaining,
        key=lambda item: (-priority_score(item, reviewed_ids, effect_summary), item["source_order"], item["id"]),
    )
    recommendation = effect_summary["restart_recommendation"]
    if recommendation:
        recommendation = {
            **recommendation,
            "superseded_item_ids": sorted(superseded_ids),
            "requires_human_queue_decision": True,
            "suggestion_display_only": True,
        }
    return ordered, {
        "queue_epoch": 1 + len(reviewed_ids),
        "status": "invalidation_recommended" if recommendation else "ready",
        "reviewed_item_ids": sorted(reviewed_ids),
        "current_queue_order": [item["id"] for item in ordered],
        "superseded_unreviewed_item_ids": sorted(superseded_ids),
        "queue_recommendation": recommendation,
        "priority_policy_version": 1,
    }


def source_order_queue_state(items: list[dict[str, Any]], review_input: dict[str, dict[str, Any]]) -> dict[str, Any]:
    reviewed_ids = reviewed_item_ids(review_input)
    ordered = sorted(items, key=lambda item: (item["source_order"], item["id"]))
    return {
        "queue_epoch": 1 + len(reviewed_ids),
        "status": "ready",
        "reviewed_item_ids": sorted(reviewed_ids),
        "current_queue_order": [item["id"] for item in ordered],
        "superseded_unreviewed_item_ids": [],
        "queue_recommendation": None,
        "priority_policy_version": 1,
    }


def uses_adaptive_rendering(
    packet: dict[str, Any],
    items: list[dict[str, Any]],
    review_input: dict[str, dict[str, Any]],
) -> bool:
    if packet.get("adaptive_queue") or any(item["adaptive"] for item in items):
        return True
    return bool(collect_queue_effects(review_input))
