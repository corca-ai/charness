"""Regression checks for mutation score validity semantics."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.check_mutation_score import (  # noqa: E402
    iter_dump_records,
    mutation_metrics,
    summarize_cosmic_ray,
)

_ADAPTER_HEADER = dedent(
    """\
    version: 1
    repo: testrepo
    language: en
    output_dir: charness-artifacts/quality
    """
)


def test_cosmic_ray_dump_summary_counts_reachable_denominator(tmp_path: Path) -> None:
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        "\n".join(
            [
                json.dumps([{"job_id": "a"}, {"worker_outcome": "normal", "test_outcome": "killed"}]),
                json.dumps([{"job_id": "b"}, {"worker_outcome": "normal", "test_outcome": "survived"}]),
                json.dumps([{"job_id": "c"}, {"worker_outcome": "exception", "test_outcome": "incompetent"}]),
                json.dumps([{"job_id": "d"}, None]),
                json.dumps([{"job_id": "e"}, {"worker_outcome": "skipped", "test_outcome": "killed"}]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    counts = summarize_cosmic_ray(iter_dump_records(dump))

    assert counts["total"] == 5
    assert counts["killed"] == 1
    assert counts["survived"] == 1
    assert counts["incompetent"] == 1
    assert counts["pending"] == 1
    assert counts["skipped"] == 1
    assert counts["scope_gap"] == 0


def test_mutation_metrics_fail_when_no_reachable_mutants() -> None:
    metrics = mutation_metrics(
        {
            "total": 10,
            "killed": 0,
            "survived": 0,
            "incompetent": 0,
            "no_tests": 0,
            "scope_gap": 0,
            "pending": 10,
            "abnormal": 0,
            "skipped": 0,
        },
        80,
    )

    assert metrics["reachable"] == 0
    assert metrics["score"] == 0.0
    assert metrics["passed"] is False


def test_mutation_metrics_fail_when_no_tests_mutants_exist() -> None:
    metrics = mutation_metrics(
        {
            "total": 11,
            "killed": 10,
            "survived": 0,
            "incompetent": 0,
            "no_tests": 1,
            "scope_gap": 0,
            "pending": 0,
            "abnormal": 0,
            "skipped": 0,
        },
        80,
    )

    assert metrics["reachable"] == 10
    assert metrics["score"] == 100.0
    assert metrics["passed"] is False


def test_check_mutation_score_fails_zero_reachable_dump(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "quality-adapter.yaml").write_text(
        _ADAPTER_HEADER
        + dedent(
            """\
            mutation_testing:
              score_break: 50
              report_paths:
                summary_md: reports/mutation/summary.md
            """
        ),
        encoding="utf-8",
    )
    dump = tmp_path / "dump.jsonl"
    dump.write_text(json.dumps([{"job_id": "a"}, None]) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            "python3",
            "scripts/check_mutation_score.py",
            "--repo-root",
            str(tmp_path),
            "--stats",
            str(dump),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Blocking signal: no reachable mutants were executed." in summary


def test_check_mutation_score_fails_no_tests_dump(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "quality-adapter.yaml").write_text(
        _ADAPTER_HEADER
        + dedent(
            """\
            mutation_testing:
              score_break: 50
              report_paths:
                summary_md: reports/mutation/summary.md
            """
        ),
        encoding="utf-8",
    )
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        "\n".join(
            [
                json.dumps([{"job_id": "a"}, {"worker_outcome": "normal", "test_outcome": "killed"}]),
                json.dumps([{"job_id": "b"}, {"worker_outcome": "no-test", "test_outcome": "survived"}]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "scripts/check_mutation_score.py",
            "--repo-root",
            str(tmp_path),
            "--stats",
            str(dump),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    counts = summarize_cosmic_ray(iter_dump_records(dump))
    metrics = mutation_metrics(counts, 50)
    assert counts["no_tests"] == 1
    assert counts["survived"] == 0
    assert metrics["reachable"] == 1
    assert "Blocking signal: Cosmic Ray reported mutants with no mutation possible." in summary
    assert "## Survived Mutants" not in summary


def test_check_mutation_score_fails_scope_gap_skips(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "quality-adapter.yaml").write_text(
        _ADAPTER_HEADER
        + dedent(
            """\
            mutation_testing:
              score_break: 50
              report_paths:
                summary_md: reports/mutation/summary.md
            """
        ),
        encoding="utf-8",
    )
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        "\n".join(
            [
                json.dumps([{"job_id": "a"}, {"worker_outcome": "normal", "test_outcome": "killed"}]),
                json.dumps(
                    [
                        {"job_id": "b"},
                        {
                            "worker_outcome": "skipped",
                            "test_outcome": "killed",
                            "output": "Filtered uncovered mutation line",
                        },
                    ]
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "scripts/check_mutation_score.py",
            "--repo-root",
            str(tmp_path),
            "--stats",
            str(dump),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "Scope gaps (uncovered sampled mutants): 1" in summary
    assert "Blocking signal: sampled mutants were not covered by the selected test command." in summary


def test_check_mutation_score_fails_changed_files_excluded_by_sampling(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "quality-adapter.yaml").write_text(
        _ADAPTER_HEADER
        + dedent(
            """\
            mutation_testing:
              score_break: 50
              report_paths:
                summary_md: reports/mutation/summary.md
            """
        ),
        encoding="utf-8",
    )
    reports = tmp_path / "reports" / "mutation"
    reports.mkdir(parents=True)
    (reports / "sample.json").write_text(
        json.dumps({"uncovered_changed_files": ["scripts/changed.py"]}) + "\n",
        encoding="utf-8",
    )
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        json.dumps([{"job_id": "a"}, {"worker_outcome": "normal", "test_outcome": "killed"}])
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "scripts/check_mutation_score.py",
            "--repo-root",
            str(tmp_path),
            "--stats",
            str(dump),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    summary = (reports / "summary.md").read_text(encoding="utf-8")
    assert (
        "Blocking signal: changed files were excluded before mutation by coverage, mutation-line, or selection-budget filters."
        in summary
    )
    assert "## Changed Files Excluded Before Mutation" in summary
    assert "`scripts/changed.py`" in summary


def test_check_mutation_score_fails_changed_files_excluded_by_selection_budget(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "quality-adapter.yaml").write_text(
        _ADAPTER_HEADER
        + dedent(
            """\
            mutation_testing:
              score_break: 50
              report_paths:
                summary_md: reports/mutation/summary.md
            """
        ),
        encoding="utf-8",
    )
    reports = tmp_path / "reports" / "mutation"
    reports.mkdir(parents=True)
    (reports / "sample.json").write_text(
        json.dumps({"selection_excluded_changed_files": ["scripts/expensive.py"]}) + "\n",
        encoding="utf-8",
    )
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        json.dumps([{"job_id": "a"}, {"worker_outcome": "normal", "test_outcome": "killed"}])
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "scripts/check_mutation_score.py",
            "--repo-root",
            str(tmp_path),
            "--stats",
            str(dump),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    summary = (reports / "summary.md").read_text(encoding="utf-8")
    assert "## Changed Files Excluded Before Mutation" in summary
    assert "`scripts/expensive.py`" in summary
