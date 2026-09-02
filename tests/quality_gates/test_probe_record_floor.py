"""The reusable probe-record decision surface and its release boundary.

These tests pin which claims owe a record, which values satisfy it, and what
happens when the record exists but did not establish anything.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_ISSUE_SCRIPTS = ROOT / "skills" / "public" / "issue" / "scripts"
_RELEASE_SCRIPTS = ROOT / "skills" / "public" / "release" / "scripts"

def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_FLOOR_MOD = _load(_ISSUE_SCRIPTS / "issue_probe_record_floor.py")
evaluate_probe_record = _FLOOR_MOD.evaluate_probe_record
probe_record_problems = _FLOOR_MOD.probe_record_problems
_FLOORS_MOD = _load(_RELEASE_SCRIPTS / "release_closeout_floors.py")
_CLOSEOUT_MOD = _load(_RELEASE_SCRIPTS / "release_issue_closeout.py")
_RELEASE_FLOORS = {
    "evaluate_release_probe_record": _FLOORS_MOD.evaluate_release_probe_record,
}

# Modules this file is the standing coverage for, declared as quoted repo-relative paths
# so `suggest_mutation_coverage_command` can MAP them. The mapper reads textual references
# and these tests build their paths from variables (`_ISSUE_SCRIPTS / "x.py"`), which match
# none of its patterns -- so the changed-line gate reported these files unmapped and then
# blocked on lines this suite actually covers. Same declaration, same reason, as
# `test_issue_consolidated_closeout.py`.
_COVERS = (
    "skills/public/issue/scripts/issue_probe_record_floor.py",
    "skills/public/release/scripts/release_closeout_floors.py",
    "skills/public/release/scripts/release_issue_closeout.py",
)

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


# --- degraded installs, and the refusal text an operator actually reads --------


def test_the_release_floors_report_absence_rather_than_passing(monkeypatch) -> None:
    # A vendored tree with `release` but not `issue`: the probe floor must REFUSE with a
    # reason naming what to install. Patched on the REAL module, not a tmp_path copy --
    # a copy's coverage attributes to the copy, so the branch reads untested.
    monkeypatch.setattr(_FLOORS_MOD, "_load_probe_floor", lambda: None)
    verdict = _FLOORS_MOD.evaluate_release_probe_record(["Behavior #44: confirmed"], [], [44], ROOT)
    assert verdict["ok"] is False
    assert "issue_probe_record_floor.py was not found" in verdict["library_unavailable"]


def test_the_release_behavioral_floor_is_inert_with_no_issues() -> None:
    assert _FLOORS_MOD.evaluate_release_behavioral_verdict([], []) == {
        "applies": False, "ok": True, "missing": [],
    }


def test_the_closeout_delegator_refuses_when_the_floors_module_is_absent(monkeypatch) -> None:
    # `release_issue_closeout` reaches the floors through one delegator. When the sibling
    # is absent the probe evaluator returns a refusal payload and the rest raise -- never a
    # pass, which is the whole point of defaulting `absent` to a refusal.
    import pytest

    monkeypatch.setattr(_CLOSEOUT_MOD, "_FLOORS_CACHE", None)
    verdict = _CLOSEOUT_MOD.evaluate_release_probe_record([], ["Probe record #44: x"], [44], ROOT)
    assert verdict["ok"] is False
    assert "release_closeout_floors.py" in verdict["library_unavailable"]
    with pytest.raises(SystemExit, match="release_closeout_floors.py"):
        _CLOSEOUT_MOD.evaluate_release_behavioral_verdict(["Behavior #44: confirmed"], [44])
    with pytest.raises(SystemExit, match="release_closeout_floors.py"):
        _CLOSEOUT_MOD.fail_release_probe_record_floor(verdict)


def test_an_undispositioned_probe_line_is_reported_with_its_state() -> None:
    # Reaches `probe_record_problems`' failed-entry branch and the `library_unavailable`
    # branch, which report different things and must not be collapsed.
    result = evaluate_probe_record(
        _body(_CLAIM, "Probe record #42: absent.md"), "bug", [42], repo_root=ROOT
    )
    problems = probe_record_problems(result)
    assert any("not-established" in p or "could not be read" in p for p in problems)
    assert probe_record_problems(
        {"applies": True, "ok": False, "library_unavailable": "no lib here"}
    ) == ["probe_record:no lib here"]


def test_a_placeholder_line_is_skipped_by_both_readers() -> None:
    # A line that MATCHES the grammar but says nothing (`-`, `TBD`, `n/a`) binds on
    # neither reader. It must not be mistaken for an answer on either side: a placeholder
    # behavior line owes nothing, and a placeholder probe line satisfies nothing.
    owes_nothing = evaluate_probe_record(
        _body("Behavior #42: -"), "bug", [42], repo_root=ROOT
    )
    assert owes_nothing["ok"] is True
    assert owes_nothing["owing"] == []

    unsatisfied = evaluate_probe_record(
        _body(_CLAIM, "Probe record #42: -"), "bug", [42], repo_root=ROOT
    )
    assert unsatisfied["ok"] is False
    assert unsatisfied["missing"] == [42]


def test_the_issue_floor_refuses_when_the_probe_library_is_unresolvable(monkeypatch) -> None:
    # A tree whose `scripts/evidence/probe_record_lib.py` cannot be resolved: the floor REFUSES and
    # names why. A check that could not run has not run, and reporting it as satisfied is
    # the class of silence this floor exists to close.
    monkeypatch.setattr(_FLOOR_MOD, "_load_probe_record_lib", lambda: None)
    result = evaluate_probe_record(_body(_CLAIM), "bug", [42], repo_root=ROOT)
    assert result["ok"] is False
    assert "could not be resolved" in result["library_unavailable"]
    assert probe_record_problems(result) == [f"probe_record:{result['library_unavailable']}"]


def test_the_second_release_entrypoint_records_an_unbacked_claim(tmp_path: Path) -> None:
    """`ensure_release_issues_closed` reaches `gh issue close` DIRECTLY.

    At REVIEW severity it records the finding into the payload rather than refusing; the
    wiring at BOTH entrypoints is what matters, because resume/recovery can reach this one
    with no preflight and a floor wired at one call site is guarded at one call site.
    """
    payload: dict = {}

    def run(*_args, **_kwargs):
        raise SystemExit("backend reached; this test only needs the floors' payload")

    try:
        _CLOSEOUT_MOD.ensure_release_issues_closed(
            tmp_path, repo="example/demo", issue_numbers=[44], payload=payload,
            run=run,
            behavior_lines=["Behavior #44: confirmed via fresh checkout install"],
            probe_record_lines=[], carrier_source="probe-floor-test",
        )
    except SystemExit:
        pass  # the synthetic backend stops the run AFTER both floors have recorded
    assert payload["issue_closeout_probe_record"]["ok"] is False
    assert payload["issue_closeout_probe_record"]["missing"] == [44]
    assert payload["issue_closeout_behavioral_verdict"]["ok"] is True


def test_an_ordinary_english_issue_lead_is_not_a_defer() -> None:
    # `issue`/`issues` is the one status token that is also a common English word, and the
    # sibling floor splits it out with a tracker-ref conjunct FOR THAT REASON. Mirroring it
    # as a flat alternant dropped the conjunct and made the commonest way to start a bug
    # sentence a universal escape.
    for claim in (
        "issues with the stale cache are gone; confirmed via a fresh checkout install",
        "Issue reproduced at base, verified via the CLI at HEAD",
    ):
        result = evaluate_probe_record(_body(f"Behavior #42: {claim}"), "bug", [42], repo_root=ROOT)
        assert result["ok"] is False, claim
        assert result["owing"] == [42], claim


def test_a_defer_that_carries_its_tracker_ref_still_owes_nothing() -> None:
    result = evaluate_probe_record(_body("Behavior #42: #99 tracks the residual"), "bug", [42], repo_root=ROOT)
    assert result["ok"] is True
    assert result["owing"] == []


def test_a_typed_status_may_not_be_a_sentence_opener() -> None:
    # `out-of-scope drift aside, verified via CLI` leads with a typed token and then makes
    # a claim. The separator requirement is what splits a status from a sentence.
    result = evaluate_probe_record(
        _body("Behavior #42: out-of-scope drift aside, verified via CLI"), "bug", [42], repo_root=ROOT
    )
    assert result["ok"] is False
    assert result["owing"] == [42]


def test_an_impossibility_disposition_beside_a_claim_is_refused() -> None:
    # "I measured this" and "measuring was impossible" cannot both be true; the floor
    # refuses rather than picking one.
    result = evaluate_probe_record(
        _body("Behavior #42: confirmed via a fresh checkout install",
              "Probe record #42: blocked-needs-operator"),
        "bug", [42], repo_root=ROOT,
    )
    assert result["ok"] is False
    assert "CLAIMS a verification" in " ".join(result["failed"][0]["reasons"])


def test_a_claim_backed_only_by_a_disposition_is_reported_to_the_reviewer() -> None:
    # `local-only-by-contract` is coherent with a claim, so it is accepted -- and it is the
    # one-line escape from producing a record, so it is REPORTED. A reviewer who has to go
    # looking for these is a reviewer who will not.
    result = evaluate_probe_record(
        _body("Behavior #42: confirmed via a fresh checkout install",
              "Probe record #42: local-only-by-contract"),
        "bug", [42], repo_root=ROOT,
    )
    assert result["ok"] is True
    assert result["claim_rests_on_disposition"] == [42]


def test_a_claim_backed_by_a_real_record_rests_on_no_disposition() -> None:
    result = evaluate_probe_record(
        _body(_CLAIM, "Probe record #42: charness-artifacts/probe/2026-08-18-standing-lane-flake-bar.md"),
        "bug", [42], repo_root=ROOT,
    )
    assert result["ok"] is True
    assert result["claim_rests_on_disposition"] == []


def test_the_second_release_entrypoint_refuses_silence_too(tmp_path: Path) -> None:
    """The guard that only fires when the caller volunteers something to check.

    `--close-issue-behavior` defaults to `[]`, and the probe floor is deliberately inert on
    silence because the behavioral-verdict floor owns that refusal. Re-running only the
    probe floor at this entrypoint therefore let the CHEAPEST possible input reach
    `gh issue close`. Both floors run here now.
    """
    import pytest

    def run_must_not_be_called(*_args, **_kwargs):
        raise AssertionError("refused before any backend call, or the guard is too late")

    with pytest.raises(SystemExit, match="behavioral-verdict"):
        _CLOSEOUT_MOD.ensure_release_issues_closed(
            tmp_path, repo="example/demo", issue_numbers=[44], payload={},
            run=run_must_not_be_called, behavior_lines=[], probe_record_lines=[],
            carrier_source="probe-floor-test",
        )


# --- the blocking paths, exercised at `block` severity --------------------------
# Held at REVIEW by operator ruling, so none of this runs in normal operation. It is
# tested BECAUSE it does not run: the flip after slice 5 must not be the first time this
# code executes. A severity switch whose armed half is unproven is not a switch, it is a
# deferred surprise.


def _arm_blocking(monkeypatch, *modules) -> None:
    for module in modules:
        monkeypatch.setattr(module, "PROBE_RECORD_SEVERITY", "block")


def test_the_release_refusal_names_the_flag_and_the_finding(monkeypatch) -> None:
    import pytest

    verdict = _FLOORS_MOD.evaluate_release_probe_record(
        ["Behavior #44: confirmed via fresh checkout install"], [], [44], ROOT
    )
    with pytest.raises(SystemExit) as excinfo:
        _FLOORS_MOD.fail_release_probe_record_floor(verdict)
    message = str(excinfo.value)
    assert "--close-issue-probe-record" in message
    assert "irreversible boundary" in message
    assert "probe_record:#44" in message


def test_both_release_entrypoints_refuse_at_block_severity(tmp_path: Path, monkeypatch) -> None:
    # The pair this floor exists to guard: one runs before quality and mutation, the other
    # reaches `gh issue close` directly and can be entered by resume with no preflight.
    import pytest

    floor = _CLOSEOUT_MOD._release_closeout_floors()._load_probe_floor()
    _arm_blocking(monkeypatch, floor)

    def run_must_not_be_called(*_args, **_kwargs):
        raise AssertionError("refused before any backend call, or the guard is too late")

    carrier = tmp_path / "carrier.md"
    carrier.write_text("Closes #44.\nClassification: feature\n", encoding="utf-8")
    claim = ["Behavior #44: confirmed via fresh checkout install"]

    with pytest.raises(SystemExit, match="no probe record establishes"):
        _CLOSEOUT_MOD.preflight_release_issues(
            tmp_path, repo="example/demo", issue_numbers=[44],
            payload={"commit_message": "chore(release): probe floor test",
                     "tag_name": "v0.0.0-probe-floor-test",
                     "quality_command": "bash scripts/run-quality.sh"},
            run=run_must_not_be_called, behavior_lines=claim, probe_record_lines=[],
            classification="feature", carrier_file=carrier,
            carrier_source="probe-floor-test",
        )
    with pytest.raises(SystemExit, match="no probe record establishes"):
        _CLOSEOUT_MOD.ensure_release_issues_closed(
            tmp_path, repo="example/demo", issue_numbers=[44], payload={},
            run=run_must_not_be_called, behavior_lines=claim, probe_record_lines=[],
            carrier_source="probe-floor-test",
        )


def test_problem_fields_are_empty_while_advisory_and_populated_when_armed(monkeypatch) -> None:
    # The one place the severity decision lives, so no carrier can disagree with another
    # about it. Both arms exercised here rather than through each carrier's setup.
    result = evaluate_probe_record(_body(_CLAIM), "bug", [42], repo_root=ROOT)
    assert result["ok"] is False
    assert _FLOOR_MOD.probe_record_problem_fields(result) == []
    monkeypatch.setattr(_FLOOR_MOD, "PROBE_RECORD_SEVERITY", "block")
    fields = _FLOOR_MOD.probe_record_problem_fields(result)
    assert fields and fields[0].startswith("probe_record:#42")
