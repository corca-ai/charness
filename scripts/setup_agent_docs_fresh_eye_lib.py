from __future__ import annotations

FRESH_EYE_MARKERS = ("fresh-eye", "fresh eye", "critique", "subagent review", "subagent reviews")
FRESH_EYE_STALE_MARKERS = ("explicit consent", "local fallback")
FRESH_EYE_SECTION_HEADING = "## Subagent Delegation"
FRESH_EYE_REQUIRED_SNIPPETS = (
    "explicit user delegation request",
    "already delegated",
    "second user message",
    "host blocks",
    "same-agent pass",
)
FRESH_EYE_COMPACT_REQUIRED_SNIPPETS = (
    "standing delegation request",
    "canonical scopes",
    "host block",
)
FRESH_EYE_COMPACT_SAME_AGENT_FORBIDDEN_SNIPPETS = (
    "same-agent substitutes are forbidden",
    "no same-agent",
    "do not substitute a same-agent",
    "same-agent pass fails",
)
FRESH_EYE_DELEGATION_CAVEAT_PATTERNS = (
    "higher-priority host",
    "developer policy requires explicit user delegation",
    "once the user authorizes subagents",
    "follow that stricter rule",
)
TASK_REVIEW_SCOPE_SNIPPETS = ("setup", "quality", "critique", "release", "issue")
LEGACY_TASK_REVIEW_SCOPE_SNIPPET = "init-repo"


def _missing_snippets(text: str, snippets: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [snippet for snippet in snippets if snippet.lower() not in lowered]


def _extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    target = heading.strip().lower()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip().lower() == target:
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def fresh_eye_compact_contract_present(agents_text: str) -> bool:
    section_body = _extract_section(agents_text, FRESH_EYE_SECTION_HEADING)
    section_lower = section_body.lower()
    same_agent_forbidden = any(snippet in section_lower for snippet in FRESH_EYE_COMPACT_SAME_AGENT_FORBIDDEN_SNIPPETS)
    return bool(section_body) and same_agent_forbidden and not _missing_snippets(section_body, FRESH_EYE_COMPACT_REQUIRED_SNIPPETS)


def fresh_eye_policy_gaps(agents_text: str) -> tuple[list[str], list[str]]:
    lowered_agents = agents_text.lower()
    compact_contract_present = fresh_eye_compact_contract_present(agents_text)
    missing_required = [] if compact_contract_present else _missing_snippets(agents_text, FRESH_EYE_REQUIRED_SNIPPETS)
    missing_scopes = [scope for scope in TASK_REVIEW_SCOPE_SNIPPETS if scope not in lowered_agents]
    return missing_required, missing_scopes


def detect_fresh_eye_normalization(agents_text: str) -> tuple[dict[str, object], list[dict[str, str]]]:
    lowered = agents_text.lower()
    stop_gate_detected = any(marker in lowered for marker in FRESH_EYE_MARKERS)
    has_subagent_delegation_section = FRESH_EYE_SECTION_HEADING.lower() in lowered
    compact_contract_present = stop_gate_detected and fresh_eye_compact_contract_present(agents_text)
    missing_required = (
        _missing_snippets(agents_text, FRESH_EYE_REQUIRED_SNIPPETS)
        if stop_gate_detected and not compact_contract_present
        else []
    )
    if stop_gate_detected and not has_subagent_delegation_section and not compact_contract_present:
        missing_required.append(FRESH_EYE_SECTION_HEADING)
    missing_task_review_scopes = (
        [snippet for snippet in TASK_REVIEW_SCOPE_SNIPPETS if snippet not in lowered] if stop_gate_detected else []
    )
    legacy_init_repo_scope_present = (
        stop_gate_detected
        and "setup" in missing_task_review_scopes
        and LEGACY_TASK_REVIEW_SCOPE_SNIPPET in lowered
    )
    stale_markers = [marker for marker in FRESH_EYE_STALE_MARKERS if marker in lowered]
    section_body = _extract_section(agents_text, FRESH_EYE_SECTION_HEADING) if has_subagent_delegation_section else ""
    section_lower = section_body.lower()
    weakening_caveats_detected = (
        [pattern for pattern in FRESH_EYE_DELEGATION_CAVEAT_PATTERNS if pattern in section_lower]
        if section_body
        else []
    )
    findings: list[dict[str, str]] = []
    if stop_gate_detected and missing_required:
        findings.append(
            {
                "type": "fresh_eye_delegation_rule_drift",
                "message": "Fresh-eye or critique review is present but AGENTS.md is missing the delegated-review stop-gate rule.",
                "recommended_action": "normalize_fresh_eye_delegation_rule",
            }
        )
    if stop_gate_detected and missing_task_review_scopes and not legacy_init_repo_scope_present:
        findings.append(
            {
                "type": "fresh_eye_task_review_scope_drift",
                "message": "Fresh-eye or critique review is present but AGENTS.md does not name all repo-mandated review runs as spawn-authorized scopes.",
                "recommended_action": "add_repo_mandated_delegated_review_scopes",
            }
        )
    if legacy_init_repo_scope_present:
        findings.append(
            {
                "type": "fresh_eye_task_review_scope_uses_legacy_init_repo",
                "message": (
                    "AGENTS.md still names the legacy `init-repo` scope for the delegated-review stop gate. "
                    "The skill was renamed to `setup`; migrate the scope to the repo-mandated review set. "
                    "This is advisory during consumer migration and will tighten in a future release."
                ),
                "recommended_action": "rename_legacy_init_repo_scope_to_setup",
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
    if weakening_caveats_detected:
        findings.append(
            {
                "type": "fresh_eye_delegation_caveat_weakens_contract",
                "message": (
                    "Subagent Delegation section contains caveat wording that weakens the standing delegation "
                    f"contract: {', '.join(weakening_caveats_detected)}."
                ),
                "recommended_action": "remove_weakening_caveats_from_subagent_delegation_section",
            }
        )
    return (
        {
            "stop_gate_detected": stop_gate_detected,
            "has_subagent_delegation_section": has_subagent_delegation_section,
            "compact_contract_present": compact_contract_present,
            "missing_required_snippets": missing_required,
            "missing_task_review_scopes": missing_task_review_scopes,
            "legacy_init_repo_scope_present": legacy_init_repo_scope_present,
            "stale_markers": stale_markers,
            "weakening_caveats_detected": weakening_caveats_detected,
        },
        findings,
    )
