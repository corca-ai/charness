from __future__ import annotations

from pathlib import Path
from typing import Any

REFERENCE_SUMMARY = {
    "references/resolve-flow.md": "resolve sequencing, GitHub source-of-truth selection, and read-before-design",
    "references/issue-shaping.md": "problem-first issue creation and external-source preservation",
    "references/resolution-brief.md": "feature/deferred-work pre-mutation brief and pause rules",
    "references/causal-review.md": "bug causal review and recurrence critique handoff",
    "references/issue-backend.md": "adapter-selected backend, body-file safety, read/create/close operations",
    "references/closeout-discipline.md": "verified ledger, auto-close carrier, behavior verdict, and final state proof",
    "../../shared/references/fresh-eye-subagent-review.md": "bounded reviewer contract for bug causal review and resolution critique",
}


def _backend_summary(preflight: dict[str, Any]) -> dict[str, Any] | None:
    selected = preflight.get("selected_backend")
    if not isinstance(selected, dict):
        return None
    return {
        "id": selected.get("id"),
        "binary": selected.get("binary"),
        "binary_path": selected.get("binary_path"),
        "found": selected.get("found"),
        "commands": selected.get("commands"),
    }


def _ref(path: str, trigger: str, role: str) -> dict[str, str]:
    return {
        "path": path,
        "role": role,
        "trigger": trigger,
        "why": REFERENCE_SUMMARY[path],
    }


def build_new_plan(repo_root: Path, target: dict[str, Any], adapter: dict[str, Any], preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "issue.run_plan.v1",
        "intent": "new",
        "repo_root": str(repo_root),
        "target": target,
        "adapter": {
            "valid": adapter["valid"],
            "path": adapter.get("path"),
            "feature_brief_pause": adapter.get("data", {}).get("feature_brief_pause"),
        },
        "selected_backend": _backend_summary(preflight),
        "backend_ready": bool(preflight.get("ok")),
        "required_reads": [
            _ref("references/issue-shaping.md", "before drafting the issue body", "engage-always"),
            _ref("references/issue-backend.md", "before create, labels, milestones, or backend mutation", "engage-always"),
            _ref("references/closeout-discipline.md", "before reporting the created issue", "engage-always"),
        ],
        "on_demand_reads": [
            _ref("references/issue-shaping.md", "when the issue originated in an external source or gathered artifact", "source-preservation")
        ],
        "gate_packets": [
            {
                "id": "preflight",
                "status": "pass" if preflight.get("ok") else "fail",
                "trust_model": "deterministic backend/auth readiness; trust failures, inspect warnings",
                "cost_tier": "cheap",
                "parallel_group": "adapter-readiness",
            },
            {
                "id": "source-preservation",
                "command": "issue_tool.py check-source-preservation --body-file <body>",
                "trust_model": "presence/form gate only; model still judges whether preservation is adequate",
                "cost_tier": "cheap",
                "parallel_group": "draft-checks",
            },
        ],
        "next_action": "draft_problem_first_body_file_then_create",
        "phase_barriers": [
            "Do not create from inline shell-quoted body text.",
            "Fetch labels/milestones through the selected backend before assigning them.",
            "Render closeout only from the verified create ledger.",
        ],
    }


def build_resolve_plan(
    repo_root: Path,
    invocation: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, Any]:
    numbers = invocation.get("numbers")
    selector_source = invocation.get("selector_source")
    if numbers is None:
        next_action = "select_newest_open_issue_from_github_then_read"
    else:
        next_action = "read_selected_issues_with_comments_then_classify"
    return {
        "schema_version": "issue.run_plan.v1",
        "intent": "resolve",
        "repo_root": str(repo_root),
        "target": invocation.get("target"),
        "selector": invocation.get("selector"),
        "numbers": numbers,
        "selector_source": selector_source,
        "brief_pause": invocation.get("brief_pause"),
        "selected_backend": _backend_summary(preflight),
        "backend_ready": bool(preflight.get("ok")),
        "required_reads": [
            _ref("references/resolve-flow.md", "before selecting or ordering issues", "engage-always"),
            _ref("references/issue-backend.md", "before backend read, carrier validation, or close", "engage-always"),
            _ref("references/closeout-discipline.md", "before publishing or verifying a closeout carrier", "engage-always"),
        ],
        "on_demand_reads": [
            _ref("references/causal-review.md", "classification is bug or likely bug", "classification:bug"),
            _ref(
                "../../shared/references/fresh-eye-subagent-review.md",
                "classification is bug or critique is required",
                "classification:bug-review-policy",
            ),
            _ref(
                "references/resolution-brief.md",
                "classification is feature or deferred-work",
                "classification:feature,deferred-work",
            ),
            _ref("references/issue-shaping.md", "resolution discovers a sibling that should become a new issue", "sibling-filing"),
        ],
        "gate_packets": [
            {
                "id": "preflight",
                "status": "pass" if preflight.get("ok") else "fail",
                "trust_model": "deterministic backend/auth readiness; trust failures, inspect warnings",
                "cost_tier": "cheap",
                "parallel_group": "adapter-readiness",
            },
            {
                "id": "issue-read",
                "command": "issue_tool.py read --repo <org/repo> --number <n>",
                "trust_model": "deterministic backend read; require comments_read=true before design",
                "cost_tier": "network",
                "parallel_group": "issue-read",
            },
            {
                "id": "closeout-draft",
                "command": "issue_tool.py validate-closeout-draft ...",
                "trust_model": "presence/form gate; does not prove behavior or final GitHub state",
                "cost_tier": "cheap",
                "parallel_group": "carrier-checks",
            },
            {
                "id": "closeout-verify",
                "command": "issue_tool.py verify-closeout ... --expect-state CLOSED",
                "trust_model": "tracker/carrier verification only; pair with distinct behavior verdict",
                "cost_tier": "network",
                "parallel_group": "final-readback",
            },
        ],
        "classification_actions": {
            "bug": {
                "action_id": "causal_review_before_design",
                "fresh_eye_required": True,
                "required_reads": [
                    "references/causal-review.md",
                    "../../shared/references/fresh-eye-subagent-review.md",
                ],
                "blocked_behavior": "stop_and_report_host_signal",
            },
            "feature": {
                "action_id": "resolution_brief_before_mutation",
                "pause_when": "open_decisions_non_empty",
                "required_reads": ["references/resolution-brief.md"],
            },
            "deferred-work": {
                "action_id": "resolution_brief_before_mutation",
                "pause_when": "open_decisions_non_empty",
                "required_reads": ["references/resolution-brief.md"],
            },
            "question": {
                "action_id": "answer_or_discuss",
                "review_pass": "not_required_by_default",
            },
            "decision-needed": {
                "action_id": "discuss_before_design",
                "classification_may_change": True,
            },
        },
        "next_action": next_action,
        "phase_barriers": [
            "GitHub issue state is the source of truth for selection and freshness.",
            "Do not design before each selected issue has comments_read=true.",
            "Do not close before the fix carrier is published and verified through GitHub readback.",
            "Do not report CLOSED as behavior proof; render the distinct behavior verdict or typed disposition.",
        ],
    }
