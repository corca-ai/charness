"""In-process coverage for `scripts/check_issue_closeout_commit_msg.py`'s pure
helpers. `tests/quality_gates/test_issue_closeout_commit_msg_hook.py` drives
this script ONLY via `subprocess.run(["python3", SCRIPT, ...])`
(`tests/quality_gates/support.run_script`), so coverage.py never attributes
lines inside its helper functions to the source file -- the #393
subprocess-only-attribution class. These tests call `_bare_classification`
and `_format_failure` directly (no subprocess) so the normal pytest+coverage
run records the lines, without re-testing the CLI contract the subprocess
suite already owns.
"""
from __future__ import annotations

import scripts.check_issue_closeout_commit_msg as checker


def test_bare_classification_honors_explicit_classification_line() -> None:
    # `_bare_classification` deliberately does NOT fall through to the loose
    # `answer:`/`decision:` substring heuristic `_infer_classification` uses --
    # only an explicit `Classification:` line overrides the strict `bug`
    # default for a bare (no staged artifact) close-keyword commit.
    body = "Fixes #77\n\nJTBD: ship the fix.\n\nClassification: question\n"
    assert checker._bare_classification(body) == "question"


def test_bare_classification_defaults_to_bug_without_explicit_line() -> None:
    body = "Fixes #77\n\nAnswer: yes, ship it.\n"
    assert checker._bare_classification(body) == "bug"


def test_format_failure_renders_staged_artifact_source_line() -> None:
    report = {
        "reports": [
            {"source_artifact": "charness-artifacts/issue/2026-06-12-demo.md", "numbers": [42]},
        ]
    }
    rendered = checker._format_failure(report)
    assert "- charness-artifacts/issue/2026-06-12-demo.md: #42" in rendered


def test_format_failure_renders_bare_close_keyword_line_when_no_artifact() -> None:
    report = {"reports": [{"source_artifact": None, "numbers": [10, 11]}]}
    rendered = checker._format_failure(report)
    assert "- commit message close keyword (no staged closeout artifact): #10, #11" in rendered


def _advisory_fn():
    # Exercise the real load + re-export chain (D36): the commit-msg carrier
    # resolves the shared advisory owner through `issue_verify_closeout`.
    return checker._load_issue_verify_closeout().review_advisory_for_classification


def test_exemption_advisories_surface_for_exempt_classification() -> None:
    reports = [
        {"classification": "question", "numbers": [42], "source_artifact": "charness-artifacts/issue/x.md"},
    ]
    lines = checker._exemption_advisories(reports, _advisory_fn())
    assert len(lines) == 1
    assert "#42" in lines[0]
    assert "charness-artifacts/issue/x.md" in lines[0]


def test_exemption_advisories_bare_keyword_names_default_scope() -> None:
    reports = [{"classification": "decision-needed", "numbers": [7], "source_artifact": None}]
    lines = checker._exemption_advisories(reports, _advisory_fn())
    assert len(lines) == 1
    assert "commit-message close keyword" in lines[0]


def test_exemption_advisories_empty_for_nonexempt_classification() -> None:
    reports = [{"classification": "bug", "numbers": [42], "source_artifact": None}]
    assert checker._exemption_advisories(reports, _advisory_fn()) == []
