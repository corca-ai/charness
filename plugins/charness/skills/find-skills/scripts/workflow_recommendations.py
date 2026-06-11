from __future__ import annotations

import re
from typing import Any

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
