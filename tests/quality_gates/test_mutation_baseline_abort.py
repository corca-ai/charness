"""Coverage-baseline abort marker tests (issue #422).

When `sample_mutation_files.py`'s coverage-baseline pytest run fails, no
mutation manifest is written and the failing nodeids only ever reached the CI
step log; `check_mutation_score.py` reported nothing but "stats missing" and
`check_js_mutation_score.py` appended an unrelated "StrykerJS JSON report
missing" slice on top of it. The abort marker records the real blocking
signal so both summaries can name it instead.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

import scripts.mutation.sample_mutation_files as sample_mutation_files
from scripts.mutation import (
    check_js_mutation_score,
    check_mutation_score,
    check_mutation_score_summary_lib,
)
from scripts.mutation.mutation_baseline_abort_lib import (
    STAGE_COSMIC_RAY_BASELINE,
    STAGE_SAMPLER_COVERAGE,
    baseline_abort_cause,
    delete_stale_baseline_abort_marker,
    parse_failed_nodeids,
    read_baseline_abort_marker,
    write_baseline_abort_marker,
)
from scripts.mutation.mutation_sampling_lib import CoverageCommandError
from scripts.mutation.sample_mutation_files import select_eligible_for_mutation
from tests.script_main import run_loaded_script_main

_ADAPTER_HEADER = dedent(
    """\
    version: 1
    repo: t
    output_dir: reports/quality
    mutation_testing:
      score_break: 60
      report_paths:
        summary_md: reports/mutation/summary.md
    """
)


def _write_adapter(repo: Path) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(_ADAPTER_HEADER, encoding="utf-8")


# ---------------------------------------------------------------------------
# parse_failed_nodeids


def test_parse_failed_nodeids_short_summary_form_with_reason() -> None:
    text = "FAILED tests/x.py::test_y - AssertionError: boom\n"
    assert parse_failed_nodeids(text) == ["tests/x.py::test_y"]


def test_parse_failed_nodeids_short_summary_form_without_reason() -> None:
    text = "FAILED tests/x.py::test_y\n"
    assert parse_failed_nodeids(text) == ["tests/x.py::test_y"]


def test_parse_failed_nodeids_verbose_form() -> None:
    text = "tests/x.py::test_y FAILED                                    [ 50%]\n"
    assert parse_failed_nodeids(text) == ["tests/x.py::test_y"]


def test_parse_failed_nodeids_dedupes_preserving_order() -> None:
    text = (
        "tests/a.py::test_first FAILED\n"
        "FAILED tests/b.py::test_second - Error\n"
        "FAILED tests/a.py::test_first - Error\n"
    )
    assert parse_failed_nodeids(text) == [
        "tests/a.py::test_first",
        "tests/b.py::test_second",
    ]


def test_parse_failed_nodeids_no_match_returns_empty() -> None:
    assert parse_failed_nodeids("2 passed in 0.01s\n") == []


def test_parse_failed_nodeids_collection_error_with_reason() -> None:
    text = "ERROR tests/x.py::test_y - ImportError: boom\n"
    assert parse_failed_nodeids(text) == ["tests/x.py::test_y"]


def test_parse_failed_nodeids_collection_error_bare_path() -> None:
    text = "ERROR tests/x.py\n"
    assert parse_failed_nodeids(text) == ["tests/x.py"]


# ---------------------------------------------------------------------------
# mutation_baseline_abort_lib marker round trip


def test_marker_round_trip(tmp_path: Path) -> None:
    marker_path = tmp_path / "baseline-abort.json"
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="python3 -m pytest -q tests",
        failing_nodeids=["tests/x.py::test_y"],
        log_tail=[],
        stage=STAGE_SAMPLER_COVERAGE,
    )

    marker = read_baseline_abort_marker(marker_path)

    assert marker is not None
    assert marker["failing_nodeids"] == ["tests/x.py::test_y"]
    assert marker["exit_code"] == 1
    assert marker["test_command"] == "python3 -m pytest -q tests"


def test_marker_missing_file_returns_none(tmp_path: Path) -> None:
    assert read_baseline_abort_marker(tmp_path / "missing.json") is None


def test_marker_malformed_json_returns_none(tmp_path: Path) -> None:
    marker_path = tmp_path / "baseline-abort.json"
    marker_path.write_text("{not json", encoding="utf-8")
    assert read_baseline_abort_marker(marker_path) is None


def test_marker_wrong_kind_returns_none(tmp_path: Path) -> None:
    marker_path = tmp_path / "baseline-abort.json"
    marker_path.write_text('{"kind": "something-else"}\n', encoding="utf-8")
    assert read_baseline_abort_marker(marker_path) is None


def test_delete_stale_marker_removes_existing_file(tmp_path: Path) -> None:
    marker_path = tmp_path / "baseline-abort.json"
    marker_path.write_text("{}", encoding="utf-8")

    delete_stale_baseline_abort_marker(marker_path)

    assert not marker_path.exists()


def test_delete_stale_marker_noop_when_absent(tmp_path: Path) -> None:
    delete_stale_baseline_abort_marker(tmp_path / "missing.json")  # must not raise


# ---------------------------------------------------------------------------
# sample_mutation_files.select_eligible_for_mutation baseline abort


def test_select_eligible_writes_marker_and_names_nodeid_on_baseline_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run_test_coverage(repo_root, test_command, coverage_json, **_kwargs):
        raise CoverageCommandError(
            1,
            test_command,
            "...\nFAILED tests/x.py::test_y - AssertionError: boom\n2 failed\n",
            "",
        )

    monkeypatch.setattr(sample_mutation_files, "run_test_coverage", fake_run_test_coverage)
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"

    with pytest.raises(SystemExit) as exc_info:
        select_eligible_for_mutation(
            repo_root=tmp_path,
            config_path=tmp_path / "cosmic-ray.toml",
            all_eligible=["scripts/a.py"],
            coverage_enabled=True,
            coverage_json=tmp_path / "reports" / "mutation" / "test-coverage.json",
            test_command="python3 -m pytest -q tests",
            min_file_coverage=0.85,
            baseline_abort_marker_path=marker_path,
        )

    assert "tests/x.py::test_y" in str(exc_info.value)
    marker = read_baseline_abort_marker(marker_path)
    assert marker is not None
    assert marker["failing_nodeids"] == ["tests/x.py::test_y"]
    assert marker["exit_code"] == 1
    assert marker["test_command"] == "python3 -m pytest -q tests"


def test_select_eligible_writes_log_tail_when_no_nodeids_parsed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run_test_coverage(repo_root, test_command, coverage_json, **_kwargs):
        raise CoverageCommandError(2, test_command, "collection error: ModuleNotFoundError\n", "")

    monkeypatch.setattr(sample_mutation_files, "run_test_coverage", fake_run_test_coverage)
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"

    with pytest.raises(SystemExit):
        select_eligible_for_mutation(
            repo_root=tmp_path,
            config_path=tmp_path / "cosmic-ray.toml",
            all_eligible=["scripts/a.py"],
            coverage_enabled=True,
            coverage_json=tmp_path / "reports" / "mutation" / "test-coverage.json",
            test_command="python3 -m pytest -q tests",
            min_file_coverage=0.85,
            baseline_abort_marker_path=marker_path,
        )

    marker = read_baseline_abort_marker(marker_path)
    assert marker is not None
    assert marker["failing_nodeids"] == []
    assert "ModuleNotFoundError" in "\n".join(marker["log_tail"])


@pytest.mark.boundary_contract(
    reason="prove the baseline workflow launches a nested pytest child with its own mutation-range environment"
)
def test_the_baseline_pytest_run_does_not_inherit_the_workflow_mutation_range() -> None:
    """The coverage-baseline pytest must not see the sampler's own range (#466).

    The mutation workflow sets `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA` for the
    whole "Select mutation sample" step, and the baseline pytest it launches
    inherits the step environment. Any test that seeds a throwaway git repo and
    runs a gate defaulting its head to `$MUTATION_HEAD_SHA` then analyzed THIS
    repo's HEAD inside that repo -- an invalid revision range, an UNESTABLISHED
    refusal, and a red baseline that aborted the whole mutation run before a
    single mutant was sampled.

    Run as a NESTED pytest with the range exported, because that is the only shape
    that can fail. Asserting `"MUTATION_HEAD_SHA" not in os.environ` in this
    process is a tautology in every lane that gates a merge: nothing outside the
    scheduled mutation workflow sets these, so the assertion holds with the
    fixture deleted. The child below reproduces the workflow's environment and
    re-runs the actual victim, so deleting `_scrub_ambient_runner_state` turns
    it red here rather than three hours later in the cron.

    `CHARNESS_NESTED_PYTEST` marks the child so its `pytest_sessionfinish` skips
    the agent-browser orphan reaper: a nested session must not kill process trees
    belonging to the outer run.
    """
    repo_root = Path(__file__).resolve().parents[2]
    outer_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True
    ).stdout.strip()

    # A hardcoded nodeid, because the child has to run the REAL victim -- and therefore a
    # standing maintenance obligation: this name has already died once to a test merge that
    # folded the old `test_a_git_failure_is_unestablished_not_an_empty_change_set` into the
    # one-checkout node below. Renaming or re-merging that node must repoint this line. Pick
    # a victim that both seeds a throwaway repo AND reads `MUTATION_HEAD_SHA`; the one named
    # here does the latter through `_assert_stale_head_and_invalid_adapter`.
    victim = (
        "tests/quality_gates/test_changed_line_coverage_gate.py"
        "::test_coverage_gate_shapes_on_one_checkout"
    )
    nested = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "-p",
            "no:randomly",
            victim,
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "CHARNESS_NESTED_PYTEST": "1",
            "MUTATION_BASE_SHA": outer_head,
            "MUTATION_HEAD_SHA": outer_head,
        },
    )
    # A renamed victim exits 4 with "not found", which is a DIFFERENT failure from the one
    # this test exists to catch. Say which one happened, or the next merge spends its time
    # debugging inherited-environment scrubbing that never broke.
    # pytest's own collection error, not any substring a victim's output might contain.
    assert f"ERROR: not found: {victim}" not in nested.stdout, (
        f"the victim nodeid no longer exists; repoint `victim` above.\n{nested.stdout}"
    )
    assert nested.returncode == 0, nested.stdout + nested.stderr


@pytest.mark.boundary_contract(
    reason="prove the nested baseline pytest child does not inherit the parent workflow step-output destination"
)
def test_the_baseline_pytest_run_does_not_write_to_the_runner_step_output(tmp_path: Path) -> None:
    """`$GITHUB_OUTPUT` is the same inherited-runner-state class as the range.

    `append_github_output` writes `sample_files=<...>` whenever `GITHUB_OUTPUT` is
    set, and the in-process `main()` calls in this file reach it. Under the
    mutation workflow that variable is the "Select mutation sample" step's own
    output file, which the "Run mutation" step consumes -- so a tmp-repo sample
    list from a test could stand in for the real one. Observed writing
    `sample_files=scripts/a.py` before the scrub.
    """
    step_output = tmp_path / "github-output.txt"
    step_output.write_text("", encoding="utf-8")

    victim = "tests/quality_gates/test_mutation_baseline_abort.py::test_sample_script_removes_stale_marker_on_successful_start"
    nested = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "-p",
            "no:randomly",
            victim,
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "CHARNESS_NESTED_PYTEST": "1", "GITHUB_OUTPUT": str(step_output)},
    )
    assert nested.returncode == 0, nested.stdout + nested.stderr
    assert step_output.read_text(encoding="utf-8") == "", step_output.read_text(encoding="utf-8")


def test_sample_script_removes_stale_marker_on_successful_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "cosmic-ray.toml").write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["scripts/adapters/control_plane_lib.py"]
            timeout = 30.0
            test-command = "python3 -m pytest -q tests"
            """
        ),
        encoding="utf-8",
    )
    marker_path = repo / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    marker_path.write_text('{"kind": "coverage-baseline-pytest-failed"}\n', encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv", ["sample_mutation_files.py", "--repo-root", str(repo), "--skip-coverage"]
    )
    monkeypatch.setenv("MUTATION_SAMPLE_MAX_FILES", "1")
    monkeypatch.setenv("MUTATION_SAMPLE_CHANGED_QUOTA", "0")
    monkeypatch.setenv("MUTATION_SAMPLE_SEED", "fixed-seed")
    monkeypatch.delenv("MUTATION_BASE_SHA", raising=False)
    monkeypatch.delenv("MUTATION_HEAD_SHA", raising=False)

    try:
        returncode = sample_mutation_files.main()
    except SystemExit as exc:
        returncode = exc.code

    assert returncode == 0
    assert not marker_path.exists()


# ---------------------------------------------------------------------------
# check_mutation_score._marker_is_stale


def test_marker_is_stale_true_when_stats_file_is_newer(tmp_path: Path) -> None:
    marker_path = tmp_path / "baseline-abort.json"
    stats_path = tmp_path / "dump.jsonl"
    marker_path.write_text("{}", encoding="utf-8")
    stats_path.write_text("{}", encoding="utf-8")
    os.utime(marker_path, (1_000, 1_000))
    os.utime(stats_path, (1_000, 2_000))

    assert check_mutation_score._marker_is_stale(marker_path, stats_path) is True


def test_marker_is_stale_false_when_marker_is_newer(tmp_path: Path) -> None:
    marker_path = tmp_path / "baseline-abort.json"
    stats_path = tmp_path / "dump.jsonl"
    marker_path.write_text("{}", encoding="utf-8")
    stats_path.write_text("{}", encoding="utf-8")
    os.utime(stats_path, (1_000, 1_000))
    os.utime(marker_path, (1_000, 2_000))

    assert check_mutation_score._marker_is_stale(marker_path, stats_path) is False


def test_marker_is_stale_false_on_mtime_tie_keeps_marker_authoritative(tmp_path: Path) -> None:
    # On a coarse-granularity filesystem a persisted previous-run stats file can
    # tie the marker's mtime to the second; the tie must keep the marker
    # authoritative so a genuine current abort is not masked.
    marker_path = tmp_path / "baseline-abort.json"
    stats_path = tmp_path / "dump.jsonl"
    marker_path.write_text("{}", encoding="utf-8")
    stats_path.write_text("{}", encoding="utf-8")
    os.utime(marker_path, (1_000, 2_000))
    os.utime(stats_path, (1_000, 2_000))

    assert check_mutation_score._marker_is_stale(marker_path, stats_path) is False


def test_marker_is_stale_false_when_stats_file_absent(tmp_path: Path) -> None:
    marker_path = tmp_path / "baseline-abort.json"
    marker_path.write_text("{}", encoding="utf-8")

    assert check_mutation_score._marker_is_stale(marker_path, tmp_path / "missing.jsonl") is False


# ---------------------------------------------------------------------------
# check_mutation_score.py marker awareness


def test_check_mutation_score_marker_ignored_when_stats_file_is_newer(tmp_path: Path) -> None:
    """A newer stats file supersedes a stale abort marker (#422 follow-up).

    Locally `reports/mutation/` persists across runs, so an abort marker left
    over from an earlier aborted attempt must not mask a fresh mutation run
    that produced a newer stats file.
    """
    _write_adapter(tmp_path)
    (tmp_path / "demo.py").write_text("def demo():\n    return 1\n", encoding="utf-8")
    dump_path = tmp_path / "reports" / "mutation" / "cosmic-ray-dump.jsonl"
    dump_path.parent.mkdir(parents=True)
    dump_path.write_text(
        json.dumps(
            [
                {
                    "job_id": "a",
                    "mutations": [
                        {
                            "module_path": "demo.py",
                            "operator_name": "core/NumberReplacer",
                            "start_pos": [2, 11],
                            "definition_name": "demo",
                        }
                    ],
                },
                {"worker_outcome": "normal", "test_outcome": "killed"},
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    marker_path = dump_path.parent / "baseline-abort.json"
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="python3 -m pytest -q tests",
        failing_nodeids=["tests/x.py::test_y"],
        log_tail=[],
        stage=STAGE_SAMPLER_COVERAGE,
    )
    os.utime(marker_path, (1_000, 1_000))
    os.utime(dump_path, (1_000, 2_000))

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )

    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Blocking signal: the sampler's coverage-baseline pytest failed" not in summary
    assert "Score denominator:" in summary
    assert result.returncode != 2


def test_check_mutation_score_marker_used_when_marker_is_newer_than_stats(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    dump_path = tmp_path / "reports" / "mutation" / "cosmic-ray-dump.jsonl"
    dump_path.parent.mkdir(parents=True)
    dump_path.write_text("", encoding="utf-8")
    marker_path = dump_path.parent / "baseline-abort.json"
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="python3 -m pytest -q tests",
        failing_nodeids=["tests/x.py::test_y"],
        log_tail=[],
        stage=STAGE_SAMPLER_COVERAGE,
    )
    os.utime(dump_path, (1_000, 1_000))
    os.utime(marker_path, (1_000, 2_000))

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 2
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert (
        "Blocking signal: the sampler's coverage-baseline pytest failed before mutation ran"
        in summary
    )
    assert "tests/x.py::test_y" in summary


def test_an_unmeasured_run_is_not_reported_with_the_verdict_of_a_measured_one(
    tmp_path: Path,
) -> None:
    """The abort summary must not spend the token that means "we scored it and it lost".

    A reader (and the auto-filed issue that republishes this summary) has to be able
    to tell "no mutant ran" from "mutants ran and the score broke". Between
    2026-08-19 and 2026-08-22 both rendered `Status: **FAIL**`, so four days of
    scheduled aborts published as mutation-score regressions, and #612's body still
    describes a run whose steps succeeded.

    Scope, stated exactly, because a comment that overstates a control's reach is
    what a later reader trusts: the assertions below compare the two renderers'
    STATUS TOKENS. They do not prove that no other line could reintroduce a measured
    verdict, and `**FAIL-incomplete**` or an unbolded `FAIL` would not be caught.

    The negative control renders the MEASURED summary through the same function the
    production path uses (`build_summary_lines`), not through `mutation_metrics`
    alone. An earlier version asserted only that `mutation_metrics` still returned
    `"FAIL"`, which a fresh-eye round showed would stay green if
    `check_mutation_score_summary_lib.py` stopped emitting the token altogether --
    the exact regression this control claims to guard.
    """
    _write_adapter(tmp_path)
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="python3 -m pytest -q tests",
        failing_nodeids=["tests/x.py::test_y"],
        log_tail=[],
        stage=STAGE_SAMPLER_COVERAGE,
    )

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")

    assert "- Status: **UNMEASURED**" in summary
    assert "**FAIL**" not in summary, "an unmeasured run must not carry a measured run's verdict"
    # Unmeasured is not forgiven: the workflow still goes red. Distinguishing the
    # verdict from the score break must not quietly turn one of them green.
    assert result.returncode == 2

    # Negative control, through the SAME rendering channel the measured path uses.
    # A run that did measure and scored below the break must still render FAIL --
    # otherwise the assertion above would also pass against a build that had merely
    # stopped emitting the token, which is the failure mode this whole goal is about.
    measured = check_mutation_score.mutation_metrics(
        {
            "killed": 1,
            "survived": 9,
            "total": 10,
            "skipped": 0,
            "pending": 0,
            "no_tests": 0,
            "incompetent": 0,
            "abnormal": 0,
            "scope_gap": 0,
        },
        score_break=80.0,
    )
    assert measured["status"] == "FAIL"
    measured_summary = "\n".join(
        check_mutation_score_summary_lib.build_summary_lines([], tmp_path, measured)
    )
    assert "- Status: **FAIL**" in measured_summary
    # And the two renderers disagree, which is the whole point of the slice.
    assert "- Status: **UNMEASURED**" not in measured_summary


def test_a_zero_denominator_is_unmeasured_on_both_mutation_slices(tmp_path: Path) -> None:
    """`reachable == 0` means no mutant produced a verdict, so no score exists.

    The baseline-abort path is not the only way to reach "nothing was measured". A
    run can complete and still score nothing: every cosmic-ray work item filtered by
    the uncovered-mutation skip, an empty dump, or a StrykerJS config that ignores
    the whole operator set. Those rendered `Status: **FAIL**` -- a verdict about a
    measurement that never happened, which is this slice's defect reached by a
    different route. A fresh-eye round found them while reviewing the abort fix.

    Stated over the DENOMINATOR rather than as two more special cases, because
    `killed + survived == 0` is the one condition that covers every route into it.

    Both slices are asserted here: they are two renderers of one property, and the
    JS one was found only because the cosmic-ray one was.
    """
    zero_denominator = {
        "killed": 0,
        "survived": 0,
        "total": 4,
        "skipped": 4,
        "pending": 0,
        "no_tests": 0,
        "incompetent": 0,
        "abnormal": 0,
        "scope_gap": 4,
    }
    metrics = check_mutation_score.mutation_metrics(zero_denominator, score_break=80.0)
    assert metrics["reachable"] == 0
    assert metrics["status"] == "UNMEASURED"
    assert metrics["passed"] is False, "unmeasured must not be forgiven into a pass"

    rendered = "\n".join(
        check_mutation_score_summary_lib.build_summary_lines([], tmp_path, metrics)
    )
    assert "- Status: **UNMEASURED**" in rendered
    # EVERY VERDICT ROW, not just the status row. The first cut asserted only
    # `- Status: **FAIL**`, and that narrowing is what hid the blocker: the summary
    # rendered `- Status: **UNMEASURED**` immediately followed by
    # `- Mutation score: **FAIL** (0.0% ...)`, and an assertion anchored on the status
    # row steps straight around the contradicting line.
    #
    # But the blunt `"**FAIL**" not in rendered` that found it is ALSO wrong, and
    # deliberately not used here: `- Blocking signals: **FAIL** (no reachable
    # mutants, ...)` is a different predicate -- it says blocking signals EXIST, which
    # is true and is the row a triager needs. Forbidding the token everywhere would
    # have suppressed a correct line to satisfy a test. So the property is stated over
    # the rows that render a VERDICT ABOUT THE CODE, and the blocking-signal row is
    # asserted present rather than absent.
    for verdict_row in ("- Status: **FAIL**", "- Mutation score: **FAIL**"):
        assert verdict_row not in rendered, rendered
    assert "no score was computed" in rendered
    assert "- Blocking signals: **FAIL**" in rendered, "the real blocker must still be reported"

    # The JS slice, same property, its own renderer.
    js_summary = tmp_path / "js-summary.md"
    check_js_mutation_score.append_summary(
        js_summary,
        {"counts": {"Ignored": 3}, "reachable": 0, "score": 0.0, "survived_locations": []},
        80.0,
    )
    js_text = js_summary.read_text(encoding="utf-8")
    assert "- Status: **UNMEASURED**" in js_text
    assert "**FAIL**" not in js_text

    # Negative control for BOTH: a real denominator still renders a real verdict, so
    # the assertions above are about the zero case and not about the tokens vanishing.
    measured = check_mutation_score.mutation_metrics(
        # `total` moves with the members, or the fixture claims 10 scored mutants out
        # of 4 executable -- incoherent input that would break on any future
        # `reachable <= total` invariant, and break as the FIXTURE rather than as the
        # code it is meant to be guarding.
        {**zero_denominator, "total": 10, "killed": 1, "survived": 9, "skipped": 0, "scope_gap": 0},
        score_break=80.0,
    )
    assert measured["status"] == "FAIL"
    assert "- Status: **FAIL**" in "\n".join(
        check_mutation_score_summary_lib.build_summary_lines([], tmp_path, measured)
    )
    js_measured = tmp_path / "js-measured.md"
    check_js_mutation_score.append_summary(
        js_measured,
        {
            "counts": {"Killed": 1, "Survived": 9},
            "reachable": 10,
            "score": 10.0,
            "survived_locations": [],
        },
        80.0,
    )
    assert "- Status: **FAIL**" in js_measured.read_text(encoding="utf-8")


def test_unmeasured_outranks_incomplete_when_there_is_no_denominator(tmp_path: Path) -> None:
    """The precedence decision the `reachable == 0` branch makes, pinned.

    That branch sits BEFORE the `exec_timed_out` and `incomplete_exec` arms, so a run
    that timed out with nothing scored reports UNMEASURED rather than FAIL-incomplete.
    That is deliberate -- "we measured nothing" is the stronger and more actionable
    statement than "we measured part of it" -- but it was shipped unpinned, and a
    later reorder putting the zero check after the timeout arm is a defensible reading
    that would silently restore FAIL-incomplete. A round-2 review named it.

    The detail a reader needs is NOT lost to the rename: the pending count, its
    blocking signal, and the timeout note all still render.
    """
    stats = {
        "killed": 0,
        "survived": 0,
        "total": 20,
        "skipped": 0,
        "pending": 20,
        "no_tests": 0,
        "incompetent": 0,
        "abnormal": 0,
        "scope_gap": 0,
    }
    timed_out = check_mutation_score.mutation_metrics(stats, score_break=80.0, exec_timed_out=True)
    assert timed_out["status"] == "UNMEASURED"
    assert timed_out["passed"] is False

    pending_only = check_mutation_score.mutation_metrics(stats, score_break=80.0)
    assert pending_only["status"] == "UNMEASURED"
    assert pending_only["passed"] is False

    rendered = "\n".join(
        check_mutation_score_summary_lib.build_summary_lines([], tmp_path, timed_out)
    )
    assert "- Pending (not executed): 20" in rendered
    assert "- Blocking signal: mutation execution left pending mutants." in rendered
    # And the timeout note must not tell the reader the status encodes a completion
    # ratio, because on this path it encodes a zero denominator.
    assert "Exec timeout fired" in rendered
    assert "status reflects partial completion" not in rendered

    # Negative control: with a denominator, the incomplete arms still own the verdict.
    still_incomplete = check_mutation_score.mutation_metrics(
        {**stats, "killed": 5, "survived": 5, "pending": 10}, score_break=80.0
    )
    assert still_incomplete["status"] == "FAIL-incomplete"


def test_check_mutation_score_marker_present_falls_back_to_log_tail_when_no_nodeids(
    tmp_path: Path,
) -> None:
    _write_adapter(tmp_path)
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    write_baseline_abort_marker(
        marker_path,
        exit_code=2,
        test_command="python3 -m pytest -q tests",
        failing_nodeids=[],
        log_tail=["collection error: ModuleNotFoundError"],
        stage=STAGE_SAMPLER_COVERAGE,
    )

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 2
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "ModuleNotFoundError" in summary
    # The log-tail branch renders a DIFFERENT body from the failing-nodeids branch,
    # so the unmeasured-vs-measured property has to be pinned here too. A fresh-eye
    # round noted that the property test above only ever exercises the other branch,
    # which would leave a measured verdict reintroducible on this path alone.
    assert "- Status: **UNMEASURED**" in summary
    assert "**FAIL**" not in summary


def test_check_mutation_score_malformed_marker_falls_back_to_missing_stats(tmp_path: Path) -> None:
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    marker_path.write_text("{not json", encoding="utf-8")

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 2
    assert "mutation stats not found" in result.stderr


# ---------------------------------------------------------------------------
# check_js_mutation_score.py marker awareness


def test_check_js_mutation_score_missing_report_with_marker_shows_collateral_signal(
    tmp_path: Path,
) -> None:
    _write_adapter(tmp_path)
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="pytest",
        failing_nodeids=["tests/x.py::test_y"],
        log_tail=[],
        stage=STAGE_SAMPLER_COVERAGE,
    )

    result = run_loaded_script_main(
        "check_js_mutation_score.py", check_js_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "- Status: **UNMEASURED** (StrykerJS JSON report missing)" in summary
    # The cosmic-ray unmeasured path got this exclusion and the JS one did not, which
    # a fresh-eye round flagged: without it a second `Status:`-shaped line carrying a
    # measured verdict could be added to this section and nothing would catch it.
    assert "**FAIL**" not in summary
    assert "collateral" in summary
    assert "the sampler's coverage-baseline pytest failed" in summary
    assert "so the JS slice was never invoked" in summary


def test_check_js_mutation_score_names_the_cosmic_ray_baseline_stage_not_the_sampler(
    tmp_path: Path,
) -> None:
    """The stage that actually recurs, and the reason `stage` exists (#590).

    A single hardcoded sentence named the SAMPLER for every abort. When
    `cosmic-ray baseline` is what failed -- which is what the 2026-08-10 runs did --
    that sentence was false, and the alternative the reader saw instead was worse:
    "JS mutation full mode did not produce a fresh JSON report", for a run in which
    JS mutation was never invoked at all.
    """
    _write_adapter(tmp_path)
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="cosmic-ray baseline cosmic-ray.toml",
        failing_nodeids=["tests/quality_gates/test_mutate_and_restore.py::test_x"],
        log_tail=[],
        stage=STAGE_COSMIC_RAY_BASELINE,
    )

    result = run_loaded_script_main(
        "check_js_mutation_score.py", check_js_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "`cosmic-ray baseline` failed" in summary
    assert "sampler" not in summary
    assert "did not produce a fresh JSON report" not in summary


def test_an_unknown_baseline_abort_stage_is_refused_at_write_time(tmp_path: Path) -> None:
    # A stage the renderer has no sentence for must not reach a report at all; the
    # write refuses rather than letting a summary describe an abort it cannot name.
    with pytest.raises(ValueError, match="unknown baseline-abort stage"):
        write_baseline_abort_marker(
            tmp_path / "m.json",
            exit_code=1,
            test_command="x",
            failing_nodeids=[],
            log_tail=[],
            stage="not-a-stage",
        )


def test_check_js_mutation_score_missing_report_without_marker_unchanged(tmp_path: Path) -> None:
    _write_adapter(tmp_path)

    result = run_loaded_script_main(
        "check_js_mutation_score.py", check_js_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Blocking signal: JS mutation full mode did not produce a fresh JSON report." in summary
    assert "collateral" not in summary


# --- the MUST-2 repairs, each pinned so deleting it turns the suite red ---


def test_the_cosmic_ray_wrapper_clears_a_stale_marker_before_its_baseline(tmp_path: Path) -> None:
    """A marker WRITER that is not also a marker CLEARER poisons the next run.

    `reports/mutation/` persists locally, and the JS reader treats any marker as "the
    baseline aborted, so the JS slice never ran". A leftover one turns a real JS
    failure into a collateral note that tells the reader to stop looking — #590 in
    mirror image, and worse than the symptom it replaced.
    """
    import sys as _sys
    from unittest.mock import patch

    from runtime_bootstrap import import_repo_module

    rcrm = import_repo_module(
        Path(__file__).resolve().parents[2] / "scripts" / "mutation" / "run_cosmic_ray_mutation.py",
        "scripts.mutation.run_cosmic_ray_mutation",
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "cosmic-ray.toml").write_text(
        '[cosmic-ray]\nmodule-path = ["mod.py"]\n', encoding="utf-8"
    )
    marker_path = repo / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="an earlier attempt",
        failing_nodeids=["tests/stale.py::test_old"],
        log_tail=[],
        stage=STAGE_COSMIC_RAY_BASELINE,
    )

    argv = ["run_cosmic_ray_mutation.py", "--repo-root", str(repo), "--mode", "dry-run"]
    with (
        patch.object(_sys, "argv", argv),
        patch.object(rcrm, "run"),
        patch.object(rcrm, "_run_baseline"),
    ):
        assert rcrm.main() == 0

    assert not marker_path.exists(), "a previous run's abort marker survived into a clean run"


def test_the_js_reader_ignores_a_marker_older_than_this_run_s_own_artifacts(tmp_path: Path) -> None:
    # Without this, a real JS failure after a since-repaired baseline reads as
    # "collateral — the baseline failed, so the JS slice was never invoked".
    _write_adapter(tmp_path)
    marker_path = tmp_path / "reports" / "mutation" / "baseline-abort.json"
    marker_path.parent.mkdir(parents=True)
    write_baseline_abort_marker(
        marker_path,
        exit_code=1,
        test_command="an earlier attempt",
        failing_nodeids=["tests/stale.py::test_old"],
        log_tail=[],
        stage=STAGE_COSMIC_RAY_BASELINE,
    )
    dump_path = tmp_path / "reports" / "mutation" / "cosmic-ray-dump.jsonl"
    dump_path.write_text("{}\n", encoding="utf-8")
    os.utime(marker_path, (1_000, 1_000))
    os.utime(dump_path, (1_000, 2_000))

    result = run_loaded_script_main(
        "check_js_mutation_score.py", check_js_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "collateral" not in summary
    assert "Blocking signal: JS mutation full mode did not produce a fresh JSON report." in summary


def test_an_unrecognized_stage_renders_as_unrecognized_rather_than_guessing() -> None:
    """The write path refuses an unknown stage, so this renderer only ever sees one
    from a marker written by an older tool version or hand-edited. It must not fall
    back to either real stage: naming the wrong cause is how a summary sends the
    reader to the wrong file, which is the defect the marker exists to remove."""
    rendered = baseline_abort_cause({"stage": "some-future-stage"})
    assert "unrecognized stage" in rendered
    assert "some-future-stage" in rendered
    assert "sampler" not in rendered


def test_a_marker_deleted_mid_read_is_not_stale_and_not_a_traceback(tmp_path: Path) -> None:
    """A concurrent run can delete the marker between the read that proved it
    existed and the stat that ages it. Absent means nothing to age out; a report
    must not become a traceback over that race."""
    assert check_js_mutation_score._marker_is_stale(tmp_path / "gone.json", tmp_path) is False
