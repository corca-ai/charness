"""In-process pins for `scripts/check_issue_closeout_commit_msg.py`'s pure
helpers, complementing the subprocess CLI suite in
`tests/quality_gates/test_issue_closeout_commit_msg_hook.py`. Note the
subprocess suite IS coverage-traced here (children inherit os.environ, so
sitecustomize + COVERAGE_PROCESS_START propagate — see the 2026-07-03
test-value audit's Coverage-Model Correction); these in-process tests exist
for the helper branches the CLI contract does not pin directly, not for
attribution. Redundant attribution-only twins were removed by the 2026-07-08
delta rotation.
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


def test_infer_classification_accepts_bold_template_form() -> None:
    # The resolution-brief template renders `**Classification**: deferred-work`;
    # the plain-only regex used to miss it and fall through to the strict `bug`
    # default, demanding the bug ledger for a deferred-work brief (#444).
    body = "# Resolution Brief\n\n**Classification**: deferred-work\n"
    assert checker._infer_classification(body) == "deferred-work"


def test_pause_brief_marker_matches_pause_states_only() -> None:
    assert checker._PAUSE_BRIEF_RE.search("**Autonomous vs pause**: pausing for user discussion")
    assert checker._PAUSE_BRIEF_RE.search("Autonomous vs pause: paused; awaiting operator decisions")
    assert not checker._PAUSE_BRIEF_RE.search(
        "**Autonomous vs pause**: continuing because empty open decisions"
    )


def test_bare_classification_honors_bold_explicit_line() -> None:
    # Deliberate bundle from the #444 critique (C2): the shared regex widening
    # also lets a BARE commit message assert classification in the template's
    # bold form. That stays consistent with `_bare_classification`'s contract
    # (an explicit line is a deliberate assertion, unlike the loose substring
    # heuristic it refuses), so the behavior is pinned here as intentional.
    body = "Fixes #9\n\n**Classification**: question\n"
    assert checker._bare_classification(body) == "question"


def test_pause_brief_provenance_floor_is_unconditional_on_classification() -> None:
    # #444 critique C5: `evaluate_ai_provenance` self-exempts question/
    # decision-needed carriers, but the pause light path keeps exactly one
    # requirement — the provenance line — so that exemption must not tunnel
    # through a loosely-inferred classification.
    module = checker._load_issue_verify_closeout()
    artifact = {
        "path": "charness-artifacts/issue/2026-01-01-issue-7-brief.md",
        "numbers": [7],
        "classification": "question",
        "body": "Autonomous vs pause: pausing for user discussion\n",
    }
    reports = checker._pause_brief_reports([artifact], module)
    assert reports[0]["ok"] is False
    assert reports[0]["ai_provenance"]["missing"] is True
    assert reports[0]["classification"] == "question"
