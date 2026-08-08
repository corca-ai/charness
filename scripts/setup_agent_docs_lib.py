from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from scripts.setup_agent_docs_fresh_eye_lib import (
    FRESH_EYE_MARKERS,
    detect_fresh_eye_normalization,
    fresh_eye_policy_gaps,
)
from scripts.setup_artifact_policy_lib import detect_charness_artifact_policy
from scripts.setup_commit_discipline_lib import detect_commit_discipline_policy
from scripts.setup_critique_adapter_inspection import (
    _detect_critique_adapter_normalization,
)
from scripts.setup_markdown_section_lib import extract_section
from scripts.setup_skill_routing_lib import (
    COMPACT_SKILL_ROUTING_CALL_RE,
    COMPACT_SKILL_ROUTING_NEGATED_CALL_RE,
    skill_routing_declares_charness_management,
    skill_routing_semantically_complete,
)

RETRO_ADAPTER_RELATIVE_PATH = Path(".agents/retro-adapter.yaml")
RETRO_SUMMARY_RELATIVE_PATH = Path("charness-artifacts/retro/recent-lessons.md")
CRITIQUE_ADAPTER_RELATIVE_PATH = Path(".agents/critique-adapter.yaml")
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
    "fresh_eye_task_review_scope_uses_legacy_init_repo": "advisory",
    "fresh_eye_review_still_requires_consent_or_fallback": "review_required",
    "fresh_eye_delegation_caveat_weakens_contract": "advisory",
    "critique_adapter_missing_for_fresh_eye_review": "review_required",
    "critique_adapter_codex_profile_drift": "review_required",
    "agents_missing_charness_dynamic_workflow_policy": "review_required",
    "agents_missing_subagent_model_policy": "review_required",
    "skill_routing_block_custom_or_drifted": "review_required",
    "charness_artifacts_commit_policy_drift": "review_required",
    "commit_discipline_drift": "review_required",
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


def _detect_charness_subagent_policy(agents_text: str) -> tuple[dict[str, object], list[dict[str, str]]]:
    """Report missing Charness-specific standing policies without rewriting AGENTS.md."""

    charness_managed = skill_routing_declares_charness_management(
        extract_section(agents_text, "## Skill Routing")
    )
    dynamic_section = " ".join(
        extract_section(agents_text, "## Dynamic Workflows")
        .lower()
        .translate(str.maketrans("", "", "`*~"))
        .split()
    )
    dynamic_complete = all(
        token in dynamic_section
        for token in ("standing request", "earns its cost", "higher-priority", "host")
    )
    # This check used to require the literal tokens `gpt-5.6-terra`, `medium reasoning
    # effort`, and `fork_turns: "none"` in AGENTS.md. Commit 353fa4a5 deliberately
    # DELETED that block, because the contract now says a host-specific model id belongs
    # in that host's adapter or preset -- "naming one in this file bakes a model id into
    # the contract and it goes stale silently". The validator was not moved with it, so
    # it demanded the exact tokens the contract had just forbidden, and main went red.
    #
    # That is this repo's own recurring defect: a declaration no executable reader was
    # reconciled against. The tokens below track what the contract actually asserts now
    # -- that the default is PER-HOST, that a model id lives in an adapter or preset
    # rather than here, and that the session model is inherited by default -- and
    # deliberately name no model id, so a model bump cannot stale this gate again.
    # Scoped to `## Subagent Delegation`, not the whole document, matching
    # `dynamic_complete` above. Read document-wide, the three phrases could be scattered
    # across unrelated sections and still satisfy the check.
    #
    # KNOWN LIMIT, stated rather than implied: this is substring matching, so it has no
    # polarity. A section that says "the claim that subagent model/effort defaults are
    # per-host is wrong -- pin the model here rather than in that host's adapter or
    # preset, and never rely on inheriting the session model" contains all three tokens
    # and passes. The tokens are also near-verbatim from the contract they check, so a
    # rewording reddens this without any behavior changing. What the check DOES buy is
    # narrow and real: it can no longer be satisfied by the superseded model-id block,
    # and the negative fixture in the tests proves that direction. Making it semantic is
    # tracked, not claimed.
    subagent_section = " ".join(
        extract_section(agents_text, "## Subagent Delegation")
        .lower()
        .translate(str.maketrans("", "", "`*~"))
        .split()
    )
    profile_complete = all(
        token in subagent_section
        for token in (
            "subagent model/effort defaults are per-host",
            "adapter or preset",
            "inheriting the session model",
        )
    )
    findings: list[dict[str, str]] = []
    if charness_managed and not dynamic_complete:
        findings.append(
            {
                "type": "agents_missing_charness_dynamic_workflow_policy",
                "message": "Charness-managed AGENTS.md is missing the standing, judgment-gated Dynamic Workflows policy.",
                "recommended_action": "add_charness_dynamic_workflow_standing_policy",
            }
        )
    if charness_managed and not profile_complete:
        findings.append(
            {
                "type": "agents_missing_subagent_model_policy",
                "message": "Charness-managed AGENTS.md is missing the per-host subagent model/effort default policy.",
                "recommended_action": "add_subagent_model_default_policy",
            }
        )
    return (
        {
            "charness_managed": charness_managed,
            "dynamic_workflow_complete": dynamic_complete,
            "subagent_model_policy_complete": profile_complete,
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
    target = "AGENTS.md"
    kind = "policy_sync"
    if finding["type"].startswith("critique_adapter_"):
        target = CRITIQUE_ADAPTER_RELATIVE_PATH.as_posix()
        kind = "adapter_sync"
    return _recommendation(
        rec_id=finding["type"],
        target=target,
        kind=kind,
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


def detect_policy_source_recommendations(
    repo_root: Path,
    agents_text: str,
    policy: dict[str, Any],
) -> list[dict[str, object]]:
    missing_required, missing_scopes = fresh_eye_policy_gaps(agents_text)
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
        evidence = [f"{raw_path} implies bounded fresh-eye, critique, or subagent review policy"]
        if missing_required:
            evidence.append("AGENTS.md lacks delegated-review host restriction wording")
        if missing_scopes:
            evidence.append("AGENTS.md does not name all repo-mandated task-completing review scopes")
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
    section_body = extract_section(agents_text, "## Skill Routing") if has_skill_routing else ""
    section_lower = section_body.lower()
    catalog_available = True
    compact_discovery_first_present = any(
        COMPACT_SKILL_ROUTING_CALL_RE.search(line)
        and not COMPACT_SKILL_ROUTING_NEGATED_CALL_RE.search(line)
        and ("startup" in line or "sessionstart" in line or "session start" in line)
        and ("once" in line or "before broader exploration" in line)
        and ("catalog" in line or "capability" in line or "route" in line)
        for line in section_lower.splitlines()
    )
    semantically_complete = skill_routing_semantically_complete(section_body)
    accepts_compact_discovery_first = (
        has_skill_routing
        and not matches_compact_block
        and catalog_available
        and (compact_discovery_first_present or semantically_complete)
    )
    recommended_action = str(payload.get("recommended_action", "inspect_manually"))
    decision_needed: str | None = None
    findings: list[dict[str, str]] = []

    if matches_compact_block or accepts_compact_discovery_first:
        recommended_action = "leave_as_is"

    if has_skill_routing and expected_markdown and not matches_compact_block and not accepts_compact_discovery_first:
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
            "semantically_complete": semantically_complete,
            "accepts_compact_discovery_first": accepts_compact_discovery_first,
            "catalog_available": catalog_available,
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
    fresh_eye_review, fresh_eye_findings = detect_fresh_eye_normalization(agents_text)
    critique_adapter, critique_adapter_findings = _detect_critique_adapter_normalization(
        repo_root,
        agents_text=agents_text,
        fresh_eye_review=fresh_eye_review,
    )
    charness_subagent_policy, charness_subagent_policy_findings = _detect_charness_subagent_policy(agents_text)
    charness_artifacts, charness_artifact_findings = detect_charness_artifact_policy(repo_root, agents_text)
    commit_discipline, commit_discipline_findings = detect_commit_discipline_policy(agents_text)
    skill_routing, skill_routing_findings = _detect_skill_routing_normalization(
        repo_root,
        agents_text,
        skill_routing_payload,
    )
    from scripts.setup_adapter_inspect_lib import (
        detect_setup_adapter_normalization,
        detect_worktree_adapter_normalization,
    )

    worktree_adapter, worktree_adapter_findings, worktree_adapter_recommendations = (
        detect_worktree_adapter_normalization(repo_root)
    )
    setup_adapter, setup_adapter_recommendations = detect_setup_adapter_normalization(repo_root)
    normalization_findings = [
        *retro_findings,
        *fresh_eye_findings,
        *critique_adapter_findings,
        *charness_subagent_policy_findings,
        *charness_artifact_findings,
        *commit_discipline_findings,
        *skill_routing_findings,
        *worktree_adapter_findings,
    ]
    extra_recommendations = [*worktree_adapter_recommendations, *setup_adapter_recommendations]
    return {
        "agents": _file_state(agents),
        "claude": _file_state(claude),
        "recommended_action": action,
        "agents_has_text": _text_present(agents),
        "claude_has_text": _text_present(claude),
        "normalization": {
            "status": "needs_normalization" if normalization_findings or extra_recommendations else "ok",
            "findings": normalization_findings,
            "extra_recommendations": extra_recommendations,
            "retro_memory": retro_memory,
            "fresh_eye_review": fresh_eye_review,
            "critique_adapter": critique_adapter,
            "charness_subagent_policy": charness_subagent_policy,
            "charness_artifacts": charness_artifacts,
            "commit_discipline": commit_discipline,
            "skill_routing": skill_routing,
            "worktree_adapter": worktree_adapter,
            "setup_adapter": setup_adapter,
        },
    }
