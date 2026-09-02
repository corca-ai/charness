"""In-process pins for `scripts/gates/check_issue_closeout_commit_msg.py`'s pure
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

import re
from pathlib import Path

import scripts.gates.check_issue_closeout_commit_msg as checker

_REPO_ROOT = Path(__file__).resolve().parents[1]


def test_bare_classification_honors_explicit_classification_line() -> None:
    # Neither classification helper falls through to a loose
    # `answer:`/`decision:` substring heuristic any more (B3): only an explicit
    # `Classification:` line overrides the strict `bug` default, on the bare
    # (no staged artifact) close-keyword path and the staged-artifact path alike.
    body = "Fixes #77\n\nJTBD: ship the fix.\n\nClassification: question\n"
    assert checker._bare_classification(body) == "question"


def test_report_payload_carries_staged_artifact_source_identity() -> None:
    # Restated for the YAML migration: `_format_failure` rendered a
    # `- <artifact>: #42` line, and the payload now carries that same identity
    # structurally. The intent is unchanged -- the author must be able to see
    # WHICH staged artifact carried WHICH issue numbers -- so pin it on the
    # emitted payload instead of on the deleted renderer's line format.
    report = {
        "ok": False,
        "reports": [
            {
                "ok": False,
                "source_artifact": "charness-artifacts/issue/2026-06-12-demo.md",
                "numbers": [42],
            },
        ],
    }
    payload = checker.report_payload(report)
    assert payload["reports"][0]["source_artifact"] == "charness-artifacts/issue/2026-06-12-demo.md"
    assert payload["reports"][0]["numbers"] == [42]
    assert payload["summary"] == checker._FAILURE_SUMMARY


def test_report_payload_marks_a_bare_close_keyword_with_no_artifact() -> None:
    # The bare close-keyword case used to be a distinct rendered sentence; the
    # payload distinguishes it by a null `source_artifact` beside the numbers.
    report = {"ok": False, "reports": [{"ok": False, "source_artifact": None, "numbers": [10, 11]}]}
    payload = checker.report_payload(report)
    assert payload["reports"][0]["source_artifact"] is None
    assert payload["reports"][0]["numbers"] == [10, 11]


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


def test_report_payload_pause_only_names_the_provenance_remedy() -> None:
    # #444 F5: when every FAILING report is pause-triggered, the summary and
    # remediation name the one-line `AI-provenance:` remedy instead of directing
    # the author toward close keywords and the closeout ledger. The prose moved
    # from the deleted renderer into `summary`/`remediation`; the swap contract
    # is unchanged.
    report = {
        "ok": False,
        "reports": [
            {
                "ok": False,
                "trigger": "pause-brief",
                "source_artifact": "charness-artifacts/issue/2026-01-01-issue-7-brief.md",
                "numbers": [7],
                "ai_provenance": {"applies": True, "ok": False},
            }
        ],
    }
    payload = checker.report_payload(report)
    assert "pausing resolution brief is missing its `AI-provenance:` line" in payload["summary"]
    assert any(
        "Append one `AI-provenance:` line to the staged brief" in line
        for line in payload["remediation"]
    )
    assert not any("Put the close keywords and closeout ledger" in line for line in payload["remediation"])
    assert "without a valid closeout carrier" not in payload["summary"]


def test_report_payload_keeps_generic_text_when_mixed_with_non_pause_failure() -> None:
    # A passing non-pause report beside a failing pause report keeps the pause
    # remedy (only FAILING reports key the swap); a failing non-pause report
    # restores the generic summary/remediation.
    passing_artifact = {
        "ok": True,
        "source_artifact": "charness-artifacts/issue/2026-01-01-issue-9.md",
        "numbers": [9],
    }
    failing_pause = {
        "ok": False,
        "trigger": "pause-brief",
        "source_artifact": "charness-artifacts/issue/2026-01-01-issue-7-brief.md",
        "numbers": [7],
    }
    failing_bare = {"ok": False, "source_artifact": None, "numbers": [10]}
    pause_beside_passing = checker.report_payload(
        {"ok": False, "reports": [passing_artifact, failing_pause]}
    )
    assert (
        "pausing resolution brief is missing its `AI-provenance:` line"
        in pause_beside_passing["summary"]
    )
    mixed_failures = checker.report_payload({"ok": False, "reports": [failing_pause, failing_bare]})
    assert "without a valid closeout carrier" in mixed_failures["summary"]
    assert any(
        "Put the close keywords and closeout ledger" in line
        for line in mixed_failures["remediation"]
    )


def test_pause_vocabulary_tracks_resolution_brief_template() -> None:
    # #444 F6 drift guard: `_PAUSE_BRIEF_RE` duplicates the resolution-brief
    # template's pause vocabulary. Read the checked-in template (producer
    # surface) and assert the regex (consumer surface) still recognizes the
    # template's own pause alternative and still rejects the continuing one.
    # Every extraction step asserts loudly: a template reword must fail here,
    # not silently stop matching.
    template = (
        _REPO_ROOT / "skills" / "public" / "issue" / "references" / "resolution-brief.md"
    ).read_text(encoding="utf-8")
    fenced = re.search(r"```markdown\n(.*?)```", template, re.DOTALL)
    assert fenced is not None, "resolution-brief fenced template block not found"
    placeholder = re.search(
        r"\*\*Autonomous vs pause\*\*: <(.*?)>", fenced.group(1), re.DOTALL
    )
    assert placeholder is not None, "Autonomous vs pause placeholder not found in template"
    alternatives = [
        " ".join(alt.split()) for alt in placeholder.group(1).split("|")
    ]
    assert len(alternatives) == 2, alternatives
    continuing, pausing = alternatives
    assert continuing.startswith("continuing"), alternatives
    assert checker._PAUSE_BRIEF_RE.search(f"**Autonomous vs pause**: {pausing}")
    assert not checker._PAUSE_BRIEF_RE.search(f"**Autonomous vs pause**: {continuing}")


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


def test_report_payload_names_every_critique_evidence_failure_shape() -> None:
    # This is the ONLY carrier that can block `git commit`, so each shape the
    # critique check can reject must reach the author by name: an invalid host
    # skip, an evidence file that is missing or empty, and a critique that does
    # not bind to the issue it was cited for. Nine generic words on this surface
    # left the author with no diagnosis. The renderer that spelled these out is
    # gone; the payload must still carry every shape, per finding, with its own
    # detail -- so pin the emitted structure rather than the rendered lines.
    report = {
        "ok": False,
        "reports": [
            {
                "ok": False,
                "numbers": [42],
                "resolution_critique_check": {
                    "ok": False,
                    "invalid_skips": [{"name": "resolution_critique", "detail": "host signal too short"}],
                    "missing_evidence_files": [
                        {"name": "resolution_critique", "path": "charness-artifacts/critique/gone.md"}
                    ],
                    "binding_failures": [{"number": 42, "reason": "critique cites no #42"}],
                },
            }
        ]
    }

    payload = checker.report_payload(report)

    critique = payload["reports"][0]["resolution_critique_check"]
    assert critique["ok"] is False
    assert critique["invalid_skips"] == [
        {"name": "resolution_critique", "detail": "host signal too short"}
    ]
    assert critique["missing_evidence_files"] == [
        {"name": "resolution_critique", "path": "charness-artifacts/critique/gone.md"}
    ]
    assert critique["binding_failures"] == [{"number": 42, "reason": "critique cites no #42"}]
