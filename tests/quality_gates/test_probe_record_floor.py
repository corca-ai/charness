"""The probe-record floor at its two boundaries: an issue close and a release publish.

The closeout floor matrix already proves the floor REACHES every carrier -- it breaks the
floor's input and observes each ingress's own verdict flip. These tests cover what the
matrix deliberately does not: the floor's decisions. Which claims owe a record, which
values satisfy it, and what happens when the record exists but did not establish anything.
"""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_ISSUE_SCRIPTS = ROOT / "skills" / "public" / "issue" / "scripts"
_RELEASE_SCRIPTS = ROOT / "skills" / "public" / "release" / "scripts"

_FLOOR = runpy.run_path(str(_ISSUE_SCRIPTS / "issue_probe_record_floor.py"))
evaluate_probe_record = _FLOOR["evaluate_probe_record"]
probe_record_problems = _FLOOR["probe_record_problems"]
_RELEASE_FLOORS = runpy.run_path(str(_RELEASE_SCRIPTS / "release_closeout_floors.py"))

_CLAIM = "Behavior #42: behavior test exercises the fixed path (distinct channel from CLOSED)"


def _body(*lines: str) -> str:
    return "\n".join(lines) + "\n"


# --- the obligation is triggered by the CLAIM, not the classification ---------


def test_a_verification_claim_with_no_probe_record_is_refused() -> None:
    result = evaluate_probe_record(_body(_CLAIM), "bug", [42], repo_root=ROOT)
    assert result["applies"] is True
    assert result["ok"] is False
    assert result["missing"] == [42]
    assert "no typed disposition" in probe_record_problems(result)[0]


def test_a_non_verifying_behavior_line_owes_nothing() -> None:
    # The whole thesis: a close that claims no measurement is owed no record. Gating on
    # classification instead would tax an honest non-verifying close for a claim it never
    # made.
    for disposition in (
        "blocked-needs-operator: the host cannot reach the provider",
        "local-only-by-contract",
        "deferred-by-operator: ruled out for this cycle",
        "out-of-scope: the reporter withdrew it",
    ):
        result = evaluate_probe_record(
            _body(f"Behavior #42: {disposition}"), "bug", [42], repo_root=ROOT
        )
        assert result["ok"] is True, disposition
        assert result["owing"] == [], disposition


def test_an_issue_with_no_behavior_line_at_all_owes_nothing_here() -> None:
    # The sibling behavioral-verdict floor already refuses that silence. Two floors
    # reporting one missing line is how a failure report starts double-counting.
    result = evaluate_probe_record(_body("Classification: bug"), "bug", [42], repo_root=ROOT)
    assert result["ok"] is True
    assert result["owing"] == []


def test_a_light_classification_never_applies() -> None:
    for classification in ("question", "decision-needed"):
        result = evaluate_probe_record(_body(_CLAIM), classification, [42], repo_root=ROOT)
        assert result["applies"] is False, classification
        assert result["ok"] is True, classification


# --- what satisfies it --------------------------------------------------------


def test_a_typed_disposition_satisfies_it() -> None:
    result = evaluate_probe_record(
        _body(_CLAIM, "Probe record #42: local-only-by-contract"), "bug", [42], repo_root=ROOT
    )
    assert result["ok"] is True
    assert result["records"][0]["disposition"] is True


def test_an_untyped_escape_fails_closed() -> None:
    result = evaluate_probe_record(
        _body(_CLAIM, "Probe record #42: we checked it and it seemed fine"),
        "bug", [42], repo_root=ROOT,
    )
    assert result["ok"] is False
    assert "resolves" in probe_record_problems(result)[0]


def test_the_shipped_exemplar_satisfies_it() -> None:
    # End to end against a REAL record rather than a fixture: the floor reads the file,
    # resolves it through `probe_record_lib`, and accepts only `evaluated`.
    result = evaluate_probe_record(
        _body(_CLAIM, "Probe record #42: charness-artifacts/probe/2026-08-18-standing-lane-flake-bar.md"),
        "bug", [42], repo_root=ROOT,
    )
    assert result["ok"] is True, probe_record_problems(result)
    assert result["records"][0]["state"] == "evaluated"


def test_a_named_record_that_established_nothing_is_refused(tmp_path: Path) -> None:
    # The floor's reason for existing: the record EXISTS and is well-formed, and it still
    # does not back the claim. A presence check would pass this.
    record = tmp_path / "unmeasured.md"
    record.write_text(
        "Claim: the loader refuses\n"
        "Claim kind: change\n"
        "Observable: the exit status\n"
        "Source ref: #628\n"
        "Source degraded reason: the issue body is not readable from this repo\n"
        "Source conditions: a refused version\n"
        "Base ref: aaa\nHead ref: bbb\nBase arm: base-observed\n"
        "Call sites unproven: none\n"
        "\n## Source text\n\n```\nquoted from the issue body\n```\n"
        "\n## Stimulus\n\n```\nrun it\n```\n"
        "\n## Base observable\n\n```\nexit 1\n```\n"
        "\n## Head observable\n\n```\nexit 1\n```\n",
        encoding="utf-8",
    )
    result = evaluate_probe_record(
        _body(_CLAIM, f"Probe record #42: {record.name}"), "bug", [42], repo_root=tmp_path
    )
    assert result["ok"] is False
    assert result["failed"][0]["state"] == "not-established"
    assert "measured nothing" in " ".join(result["failed"][0]["reasons"])


def test_an_unreadable_named_record_is_refused_not_crashed(tmp_path: Path) -> None:
    result = evaluate_probe_record(
        _body(_CLAIM, "Probe record #42: absent.md"), "bug", [42], repo_root=tmp_path
    )
    assert result["ok"] is False
    assert "could not be read" in " ".join(result["failed"][0]["reasons"])


def test_a_multi_issue_close_binds_per_issue() -> None:
    body = _body(
        "Behavior #42: exercised through the shared fixture (distinct channel)",
        "Behavior #43: exercised through the shared fixture (distinct channel)",
        "Probe record #42: local-only-by-contract",
    )
    result = evaluate_probe_record(body, "bug", [42, 43], repo_root=ROOT)
    assert result["ok"] is False
    assert result["missing"] == [43]


def test_a_record_line_for_an_unclosed_issue_does_not_bind() -> None:
    # A quoted or copied entry for another issue is not this carrier's disposition.
    result = evaluate_probe_record(
        _body(_CLAIM, "Probe record #99: local-only-by-contract"), "bug", [42], repo_root=ROOT
    )
    assert result["ok"] is False
    assert result["missing"] == [42]


# --- the release boundary -----------------------------------------------------


def test_the_release_floor_refuses_a_claim_with_no_record() -> None:
    verdict = _RELEASE_FLOORS["evaluate_release_probe_record"](
        ["Behavior #44: confirmed via fresh checkout install"], [], [44], ROOT
    )
    assert verdict["ok"] is False
    assert verdict["missing"] == [44]


def test_the_release_floor_accepts_a_typed_disposition() -> None:
    verdict = _RELEASE_FLOORS["evaluate_release_probe_record"](
        ["Behavior #44: confirmed via fresh checkout install"],
        ["Probe record #44: local-only-by-contract"],
        [44],
        ROOT,
    )
    assert verdict["ok"] is True


def test_the_release_floor_owes_nothing_for_a_non_verifying_line() -> None:
    verdict = _RELEASE_FLOORS["evaluate_release_probe_record"](
        ["Behavior #44: blocked-needs-capability"], [], [44], ROOT
    )
    assert verdict["ok"] is True


def test_the_release_floor_is_not_applicable_with_no_issues() -> None:
    verdict = _RELEASE_FLOORS["evaluate_release_probe_record"]([], [], [], ROOT)
    assert verdict["applies"] is False
    assert verdict["ok"] is True
