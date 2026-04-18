#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def resolve_tool_recommendations(
    args: Any,
    *,
    local_root: Any,
    manifests: list[dict[str, Any]],
    recommendations_for_public_skill: Any,
    recommendations_for_role: Any,
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
    return [], None


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
) -> dict[str, Any]:
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
        "trusted_skills": trusted_entries,
        "tool_recommendations": tool_recommendations,
        "tool_recommendation_query": recommendation_query,
    }
