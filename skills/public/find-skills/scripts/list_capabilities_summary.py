from __future__ import annotations


def summary_payload(payload: dict[str, object]) -> dict[str, object]:
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
            "next_step": payload.get("next_step"),
            "workflow_recommendations": payload.get("workflow_recommendations", []),
            "public_skill_recommendations": payload.get("public_skill_recommendations", []),
            "public_recommendation_query": payload.get("public_recommendation_query"),
            # Inference-layer self-declaration; present only when a ranking was produced.
            **(
                {"recommendation_interpretation": payload["recommendation_interpretation"]}
                if payload.get("recommendation_interpretation")
                else {}
            ),
        },
    }
