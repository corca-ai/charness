from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from scripts.init_repo_artifact_policy_lib import detect_charness_artifact_policy

RETRO_ADAPTER_RELATIVE_PATH = Path(".agents/retro-adapter.yaml")
RETRO_SUMMARY_RELATIVE_PATH = Path("charness-artifacts/retro/recent-lessons.md")
FRESH_EYE_MARKERS = ("fresh-eye", "fresh eye", "premortem", "subagent review", "subagent reviews")
FRESH_EYE_STALE_MARKERS = ("explicit consent", "local fallback")
FRESH_EYE_REQUIRED_SNIPPETS = (
    "already delegated",
    "second user message",
    "host blocks",
    "same-agent pass",
)
TASK_REVIEW_SCOPE_SNIPPETS = ("init-repo", "quality")
RECOMMENDATION_PRIORITY_ORDER = {
    "review_required": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "advisory": 4,
}
FINDING_RECOMMENDATION_PRIORITIES = {
    "fresh_eye_delegation_rule_drift": "review_required",
    "fresh_eye_task_review_scope_drift": "review_required",
    "fresh_eye_review_still_requires_consent_or_fallback": "review_required",
    "skill_routing_block_custom_or_drifted": "review_required",
    "charness_artifacts_commit_policy_drift": "review_required",
}
RECOMMENDATION_FINDING_TYPES = set(FINDING_RECOMMENDATION_PRIORITIES)


def _file_state(path: Path) -> dict[str, object]:
    if not path.exists() and not path.is_symlink():
        return {"exists": False, "kind": "missing"}
    if path.is_symlink():
        return {"exists": True, "kind": "symlink", "target": str(path.readlink())}
    if path.is_file():
        return {"exists": True, "kind": "file", "size": path.stat().st_size}
    return {"exists": True, "kind": "other"}


def _text_present(path: Path) -> bool:
    return path.is_file() and path.read_text(encoding="utf-8", errors="replace").strip() != ""


def _case_insensitive_path(repo_root: Path, relative_path: Path) -> Path:
    current = repo_root
    for part in relative_path.parts:
        exact = current / part
        if exact.exists() or exact.is_symlink():
            current = exact
            continue
        if not current.is_dir():
            return exact
        matches = sorted(child for child in current.iterdir() if child.name.lower() == part.lower())
        current = matches[0] if matches else exact
    return current


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _missing_snippets(text: str, snippets: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [snippet for snippet in snippets if snippet.lower() not in lowered]


def _detect_retro_memory_normalization(repo_root: Path, agents_text: str) -> tuple[dict[str, object], list[dict[str, str]]]:
    adapter = repo_root / RETRO_ADAPTER_RELATIVE_PATH
    summary = repo_root / RETRO_SUMMARY_RELATIVE_PATH
    adapter_exists = adapter.is_file()
    summary_exists = summary.is_file()
    enabled = adapter_exists or summary_exists
    agents_mentions_summary = RETRO_SUMMARY_RELATIVE_PATH.as_posix() in agents_text
    findings: list[dict[str, str]] = []
    if enabled and not agents_mentions_summary:
        findings.append(
            {
                "type": "agents_missing_retro_recent_lessons_memory",
                "message": "Retro memory is enabled but AGENTS.md does not list the recent lessons digest.",
                "recommended_action": "add_recent_lessons_to_agents_memory",
            }
        )
    if summary_exists and not adapter_exists:
        findings.append(
            {
                "type": "retro_summary_without_adapter",
                "message": "Retro recent-lessons digest exists but .agents/retro-adapter.yaml is missing.",
                "recommended_action": "seed_or_restore_retro_adapter",
            }
        )
    if adapter_exists and not summary_exists:
        findings.append(
            {
                "type": "retro_adapter_without_summary",
                "message": "Retro adapter exists but the configured recent-lessons digest is missing.",
                "recommended_action": "seed_or_restore_recent_lessons_digest",
            }
        )
    return (
        {
            "enabled": enabled,
            "adapter_exists": adapter_exists,
            "summary_exists": summary_exists,
            "agents_mentions_summary": agents_mentions_summary,
        },
        findings,
    )


def _recommendation(
    *,
    rec_id: str,
    target: str,
    kind: str,
    priority: str,
    confidence: str,
    enforcement_tier: str,
    evidence: list[str],
    suggested_action: str,
) -> dict[str, object]:
    return {
        "id": rec_id,
        "target": target,
        "kind": kind,
        "priority": priority,
        "confidence": confidence,
        "enforcement_tier": enforcement_tier,
        "evidence": evidence,
        "suggested_action": suggested_action,
        "acknowledgement": {"status": "unacknowledged"},
    }


def finding_recommendation(finding: dict[str, str], *, priority: str = "advisory") -> dict[str, object]:
    return _recommendation(
        rec_id=finding["type"],
        target="AGENTS.md",
        kind="policy_sync",
        priority=priority,
        confidence="medium",
        enforcement_tier="NON_AUTOMATABLE",
        evidence=[finding["message"]],
        suggested_action=finding["recommended_action"],
    )


def is_acknowledged(item_id: str, acknowledged: set[str]) -> bool:
    return item_id in acknowledged


def sort_recommendations(recommendations: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        recommendations,
        key=lambda item: (RECOMMENDATION_PRIORITY_ORDER.get(str(item.get("priority")), 99), str(item.get("id"))),
    )


def _detect_fresh_eye_normalization(agents_text: str) -> tuple[dict[str, object], list[dict[str, str]]]:
    lowered = agents_text.lower()
    stop_gate_detected = any(marker in lowered for marker in FRESH_EYE_MARKERS)
    missing_required = _missing_snippets(agents_text, FRESH_EYE_REQUIRED_SNIPPETS) if stop_gate_detected else []
    missing_task_review_scopes = (
        [snippet for snippet in TASK_REVIEW_SCOPE_SNIPPETS if snippet not in lowered] if stop_gate_detected else []
    )
    stale_markers = [marker for marker in FRESH_EYE_STALE_MARKERS if marker in lowered]
    findings: list[dict[str, str]] = []
    if stop_gate_detected and missing_required:
        findings.append(
            {
                "type": "fresh_eye_delegation_rule_drift",
                "message": "Fresh-eye or premortem review is present but AGENTS.md is missing the delegated-review stop-gate rule.",
                "recommended_action": "normalize_fresh_eye_delegation_rule",
            }
        )
    if stop_gate_detected and missing_task_review_scopes:
        findings.append(
            {
                "type": "fresh_eye_task_review_scope_drift",
                "message": "Fresh-eye or premortem review is present but AGENTS.md does not name task-completing init-repo and quality review runs as spawn-authorized scopes.",
                "recommended_action": "add_init_repo_quality_delegated_review_scope",
            }
        )
    if stop_gate_detected and stale_markers:
        findings.append(
            {
                "type": "fresh_eye_review_still_requires_consent_or_fallback",
                "message": "Fresh-eye review wording still asks for explicit consent or permits local fallback.",
                "recommended_action": "replace_with_already_delegated_host_restriction_rule",
            }
        )
    return (
        {
            "stop_gate_detected": stop_gate_detected,
            "missing_required_snippets": missing_required,
            "missing_task_review_scopes": missing_task_review_scopes,
            "stale_markers": stale_markers,
        },
        findings,
    )


def detect_policy_source_recommendations(
    repo_root: Path,
    agents_text: str,
    policy: dict[str, Any],
) -> list[dict[str, object]]:
    lowered_agents = agents_text.lower()
    missing_required = _missing_snippets(agents_text, FRESH_EYE_REQUIRED_SNIPPETS)
    missing_scopes = [scope for scope in ("init-repo", "quality") if scope not in lowered_agents]
    if not missing_required and not missing_scopes:
        return []

    recommendations_by_id: dict[str, dict[str, object]] = {}
    enabled = set(policy.get("enabled", []))
    for source in policy.get("policy_sources", []):
        raw_path = source.get("path")
        if not isinstance(raw_path, str):
            continue
        source_text = _read_text(repo_root / raw_path)
        terms = source.get("evidence_terms") or FRESH_EYE_MARKERS
        source_mentions_review = any(str(term).lower() in source_text.lower() for term in terms)
        source_requests_recommendation = "agents.delegated_review_policy" in source.get("recommendations", [])
        enabled_requests_recommendation = "agents.delegated_review_policy" in enabled
        if not (source_mentions_review or source_requests_recommendation or enabled_requests_recommendation):
            continue
        evidence = [f"{raw_path} implies bounded fresh-eye, premortem, or subagent review policy"]
        if missing_required:
            evidence.append("AGENTS.md lacks delegated-review host restriction wording")
        if missing_scopes:
            evidence.append("AGENTS.md does not name init-repo and quality as task-completing review scopes")
        existing = recommendations_by_id.get("agents.delegated_review_policy")
        if existing is not None:
            existing_evidence = existing.setdefault("evidence", [])
            if isinstance(existing_evidence, list):
                for item in evidence:
                    if item not in existing_evidence:
                        existing_evidence.append(item)
            continue
        recommendations_by_id["agents.delegated_review_policy"] = _recommendation(
            rec_id="agents.delegated_review_policy",
            target="AGENTS.md",
            kind="policy_sync",
            priority="review_required",
            confidence="medium",
            enforcement_tier="NON_AUTOMATABLE",
            evidence=evidence,
            suggested_action="Review whether AGENTS.md should carry the delegated review rule.",
        )
    return list(recommendations_by_id.values())


def _detect_skill_routing_normalization(
    repo_root: Path,
    agents_text: str,
    skill_routing_payload: Callable[[Path], dict[str, Any]] | None,
) -> tuple[dict[str, object], list[dict[str, str]]]:
    has_skill_routing = "## Skill Routing" in agents_text
    payload = skill_routing_payload(repo_root) if skill_routing_payload is not None else {}
    expected_markdown = str(payload.get("markdown", ""))
    missing_expected_snippets: list[str] = []
    matches_compact_block = bool(expected_markdown and expected_markdown in agents_text)
    recommended_action = str(payload.get("recommended_action", "inspect_manually"))
    decision_needed: str | None = None
    findings: list[dict[str, str]] = []

    if has_skill_routing and expected_markdown and not matches_compact_block:
        expected_lines = tuple(line for line in expected_markdown.splitlines() if line.strip() and line != "## Skill Routing")
        missing_expected_snippets = [line for line in expected_lines if line not in agents_text]
        recommended_action = "review_existing_skill_routing"
        decision_needed = "leave_as_is_or_replace_with_compact_block"
        findings.append(
            {
                "type": "skill_routing_block_custom_or_drifted",
                "message": "AGENTS.md has a Skill Routing block that differs from the generated compact discovery-first block.",
                "recommended_action": "decide_leave_as_is_or_compact_skill_routing",
            }
        )

    return (
        {
            "has_skill_routing": has_skill_routing,
            "matches_compact_block": matches_compact_block,
            "recommended_action": recommended_action,
            "decision_needed": decision_needed,
            "missing_expected_snippets": missing_expected_snippets,
        },
        findings,
    )


def detect_agent_docs(
    repo_root: Path,
    *,
    skill_routing_payload: Callable[[Path], dict[str, Any]] | None = None,
) -> dict[str, object]:
    agents = _case_insensitive_path(repo_root, Path("AGENTS.md"))
    claude = _case_insensitive_path(repo_root, Path("CLAUDE.md"))
    agents_text = _read_text(agents)
    if not agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_agents_and_symlink"
    elif agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_symlink_only"
    elif claude.is_symlink() and claude.resolve() == agents.resolve():
        action = "leave_as_is"
    elif claude.is_file() and not agents.exists():
        action = "ask_to_promote_claude_into_agents"
    elif claude.is_file() and agents.exists():
        action = "ask_to_merge_and_replace_with_symlink"
    else:
        action = "inspect_manually"
    retro_memory, retro_findings = _detect_retro_memory_normalization(repo_root, agents_text)
    fresh_eye_review, fresh_eye_findings = _detect_fresh_eye_normalization(agents_text)
    charness_artifacts, charness_artifact_findings = detect_charness_artifact_policy(repo_root, agents_text)
    skill_routing, skill_routing_findings = _detect_skill_routing_normalization(
        repo_root,
        agents_text,
        skill_routing_payload,
    )
    normalization_findings = [*retro_findings, *fresh_eye_findings, *charness_artifact_findings, *skill_routing_findings]
    return {
        "agents": _file_state(agents),
        "claude": _file_state(claude),
        "recommended_action": action,
        "agents_has_text": _text_present(agents),
        "claude_has_text": _text_present(claude),
        "normalization": {
            "status": "needs_normalization" if normalization_findings else "ok",
            "findings": normalization_findings,
            "retro_memory": retro_memory,
            "fresh_eye_review": fresh_eye_review,
            "charness_artifacts": charness_artifacts,
            "skill_routing": skill_routing,
        },
    }
