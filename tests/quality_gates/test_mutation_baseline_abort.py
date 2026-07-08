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

import scripts.sample_mutation_files as sample_mutation_files
from scripts import check_js_mutation_score, check_mutation_score
from scripts.mutation_baseline_abort_lib import (
    delete_stale_baseline_abort_marker,
    parse_failed_nodeids,
    read_baseline_abort_marker,
    write_baseline_abort_marker,
)
from scripts.sample_mutation_files import select_eligible_for_mutation
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
        raise subprocess.CalledProcessError(
            1,
            test_command,
            output="...\nFAILED tests/x.py::test_y - AssertionError: boom\n2 failed\n",
            stderr="",
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
        raise subprocess.CalledProcessError(
            2, test_command, output="collection error: ModuleNotFoundError\n", stderr=""
        )

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
            module-path = ["scripts/control_plane_lib.py"]
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
    )
    os.utime(marker_path, (1_000, 1_000))
    os.utime(dump_path, (1_000, 2_000))

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )

    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Blocking signal: coverage baseline pytest failed" not in summary
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
    )
    os.utime(dump_path, (1_000, 1_000))
    os.utime(marker_path, (1_000, 2_000))

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 2
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Blocking signal: coverage baseline pytest failed" in summary
    assert "tests/x.py::test_y" in summary


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
    )

    result = run_loaded_script_main(
        "check_mutation_score.py", check_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 2
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "ModuleNotFoundError" in summary


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
    )

    result = run_loaded_script_main(
        "check_js_mutation_score.py", check_js_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Status: **FAIL** (StrykerJS JSON report missing)" in summary
    assert "collateral" in summary
    assert "sampler aborted on its coverage baseline" in summary


def test_check_js_mutation_score_missing_report_without_marker_unchanged(tmp_path: Path) -> None:
    _write_adapter(tmp_path)

    result = run_loaded_script_main(
        "check_js_mutation_score.py", check_js_mutation_score, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Blocking signal: JS mutation full mode did not produce a fresh JSON report." in summary
    assert "collateral" not in summary
