from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)

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


def _adapter_summary(adapter: dict[str, Any]) -> dict[str, Any]:
    return {
        "valid": adapter["valid"],
        "path": adapter.get("path"),
        "feature_brief_pause": adapter.get("data", {}).get("feature_brief_pause"),
    }


def _preflight_gate(preflight: dict[str, Any]) -> dict[str, str]:
    return _ENVELOPE.gate_packet(
        "preflight",
        "deterministic backend/auth readiness; trust failures, inspect warnings",
        status="pass" if preflight.get("ok") else "fail",
        parallel_group="adapter-readiness",
    )


def _brief_action() -> dict[str, Any]:
    return {
        "action_id": "resolution_brief_before_mutation",
        "pause_when": "open_decisions_non_empty",
        "required_reads": ["references/resolution-brief.md"],
    }


def _ref(path: str, trigger: str, role: str) -> dict[str, str]:
    return _ENVELOPE.read(path, REFERENCE_SUMMARY[path], role=role, trigger=trigger)


def build_new_plan(repo_root: Path, target: dict[str, Any], adapter: dict[str, Any], preflight: dict[str, Any]) -> dict[str, Any]:
    return _ENVELOPE.build_envelope(
        schema_version="issue.run_plan.v1",
        required_reads=[
            _ref("references/issue-shaping.md", "before drafting the issue body", "engage-always"),
            _ref("references/issue-backend.md", "before create, labels, milestones, or backend mutation", "engage-always"),
            _ref("references/closeout-discipline.md", "before reporting the created issue", "engage-always"),
        ],
        next_action=_ENVELOPE.next_action("draft_problem_first_body_file_then_create"),
        gate_packets=[
            _preflight_gate(preflight),
            _ENVELOPE.gate_packet(
                "source-preservation",
                "presence/form gate only; model still judges whether preservation is adequate",
                command="issue_tool.py check-source-preservation --body-file <body>",
                parallel_group="draft-checks",
            ),
        ],
        intent="new",
        repo_root=str(repo_root),
        target=target,
        adapter=_adapter_summary(adapter),
        selected_backend=_backend_summary(preflight),
        backend_ready=bool(preflight.get("ok")),
        on_demand_reads=[
            _ref("references/issue-shaping.md", "when the issue originated in an external source or gathered artifact", "source-preservation")
        ],
        phase_barriers=[
            "Do not create from inline shell-quoted body text.",
            "Fetch labels/milestones through the selected backend before assigning them.",
            "Render closeout only from the verified create ledger.",
        ],
    )


def build_resolve_plan(
    repo_root: Path,
    invocation: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, Any]:
    numbers = invocation.get("numbers")
    selector_source = invocation.get("selector_source")
    if numbers is None:
        next_action = _ENVELOPE.next_action("select_newest_open_issue_from_github_then_read")
    else:
        next_action = _ENVELOPE.next_action("read_selected_issues_with_comments_then_classify")
    return _ENVELOPE.build_envelope(
        schema_version="issue.run_plan.v1",
        required_reads=[
            _ref("references/resolve-flow.md", "before selecting or ordering issues", "engage-always"),
            _ref("references/issue-backend.md", "before backend read, carrier validation, or close", "engage-always"),
            _ref("references/closeout-discipline.md", "before publishing or verifying a closeout carrier", "engage-always"),
        ],
        next_action=next_action,
        gate_packets=[
            _preflight_gate(preflight),
            _ENVELOPE.gate_packet(
                "issue-read",
                "deterministic backend read; require comments_read=true before design",
                cost_tier="network",
                command="issue_tool.py read --repo <org/repo> --number <n>",
                parallel_group="issue-read",
            ),
            _ENVELOPE.gate_packet(
                "closeout-draft",
                "presence/form gate; does not prove behavior or final GitHub state",
                command="issue_tool.py validate-closeout-draft ...",
                parallel_group="carrier-checks",
            ),
            _ENVELOPE.gate_packet(
                "closeout-verify",
                "tracker/carrier verification only; pair with distinct behavior verdict",
                cost_tier="network",
                command="issue_tool.py verify-closeout ... --expect-state CLOSED",
                parallel_group="final-readback",
            ),
        ],
        intent="resolve",
        repo_root=str(repo_root),
        target=invocation.get("target"),
        selector=invocation.get("selector"),
        numbers=numbers,
        selector_source=selector_source,
        brief_pause=invocation.get("brief_pause"),
        selected_backend=_backend_summary(preflight),
        backend_ready=bool(preflight.get("ok")),
        on_demand_reads=[
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
        classification_actions={
            "bug": {
                "action_id": "causal_review_before_design",
                "fresh_eye_required": True,
                "required_reads": [
                    "references/causal-review.md",
                    "../../shared/references/fresh-eye-subagent-review.md",
                ],
                "blocked_behavior": "stop_and_report_host_signal",
            },
            "feature": _brief_action(),
            "deferred-work": _brief_action(),
            "question": {
                "action_id": "answer_or_discuss",
                "review_pass": "not_required_by_default",
            },
            "decision-needed": {
                "action_id": "discuss_before_design",
                "classification_may_change": True,
            },
        },
        phase_barriers=[
            "GitHub issue state is the source of truth for selection and freshness.",
            "Do not design before each selected issue has comments_read=true.",
            "Do not close before the fix carrier is published and verified through GitHub readback.",
            "Do not report CLOSED as behavior proof; render the distinct behavior verdict or typed disposition.",
        ],
    )


def command_plan(
    args: Any,
    *,
    adapter_module: Any,
    runtime_module: Any,
    brief_module: Any,
    backend_module: Any,
    resolve_backend: Any,
    emit: Any,
) -> int:
    repo_root = args.repo_root.resolve()
    adapter = adapter_module.load_adapter(repo_root)
    resolved = resolve_backend(repo_root)
    preflight = backend_module.build_preflight_payload(resolved)
    if not adapter["valid"]:
        emit({"ok": False, "adapter": adapter, "next_action": _ENVELOPE.next_action("repair_issue_adapter")})
        return 1
    try:
        if args.intent == "new":
            target = runtime_module.resolve_target(repo_root, args.target, adapter["data"])
            payload = build_new_plan(repo_root, target, adapter, preflight)
        else:
            if args.target:
                emit({
                    "ok": False,
                    "error": "`--target` is only valid with `--intent new`; pass resolve repo/selector as positional values",
                    "adapter": adapter,
                })
                return 2
            invocation = brief_module.build_invocation_payload(
                repo_root,
                args.values,
                adapter,
                adapter_module.DEFAULT_FEATURE_BRIEF_PAUSE,
            )
            payload = build_resolve_plan(repo_root, invocation, preflight)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), "adapter": adapter})
        return 2
    payload["ok"] = bool(payload.get("backend_ready"))
    emit(payload)
    return 0 if payload["ok"] else 1


def register_plan_subparser(
    subparsers: Any,
    cwd_default: Path,
    *,
    adapter_module: Any,
    runtime_module: Any,
    brief_module: Any,
    backend_module: Any,
    resolve_backend: Any,
    emit: Any,
) -> None:
    parser = subparsers.add_parser("plan", help="Plan an issue new/resolve run before reading, mutating, or closing")
    parser.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    parser.add_argument("--intent", choices=("new", "resolve"), required=True, help="Issue operation to plan")
    parser.add_argument("--target", help="Target repo for issue new; defaults through adapter/git remote")
    parser.add_argument("values", nargs="*", help="Raw issue resolve invocation values when --intent resolve")
    parser.set_defaults(
        func=lambda args: command_plan(
            args,
            adapter_module=adapter_module,
            runtime_module=runtime_module,
            brief_module=brief_module,
            backend_module=backend_module,
            resolve_backend=resolve_backend,
            emit=emit,
        )
    )
