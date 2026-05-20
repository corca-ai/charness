"""Partial-run handling for `scripts/check_mutation_score.py` (#183 fix)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "check_mutation_score", ROOT / "scripts" / "check_mutation_score.py"
)
assert _spec is not None and _spec.loader is not None
CMS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CMS)


def _stats(
    *,
    total: int,
    killed: int,
    survived: int,
    pending: int = 0,
    no_tests: int = 0,
    skipped: int = 0,
    scope_gap: int = 0,
) -> dict[str, int]:
    return {
        "total": total,
        "killed": killed,
        "survived": survived,
        "incompetent": 0,
        "no_tests": no_tests,
        "scope_gap": scope_gap,
        "pending": pending,
        "abnormal": 0,
        "skipped": skipped,
    }


def test_full_run_pass() -> None:
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=85, survived=15), score_break=80, exec_timed_out=False
    )
    assert metrics["status"] == "PASS"
    assert metrics["passed"] is True
    assert metrics["executed"] == 100
    assert metrics["executed_ratio"] == 1.0


def test_full_run_fail_below_threshold() -> None:
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=60, survived=40), score_break=80, exec_timed_out=False
    )
    assert metrics["status"] == "FAIL"
    assert metrics["passed"] is False


def test_non_timeout_pending_mutants_fail_incomplete() -> None:
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=80, survived=0, pending=20),
        score_break=80,
        exec_timed_out=False,
    )
    assert metrics["status"] == "FAIL-incomplete"
    assert metrics["passed"] is False
    assert metrics["incomplete_exec"] is True


def test_partial_run_above_floor_with_passing_score() -> None:
    # 80/100 executed (80% >= 75% floor); 70 killed / (70+10) = 87.5% >= 80%.
    # A partial run may be diagnostically strong, but it must not auto-close a
    # mutation recovery issue.
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=70, survived=10, pending=20),
        score_break=80,
        exec_timed_out=True,
    )
    assert metrics["status"] == "PASS-partial"
    assert metrics["passed"] is False
    assert metrics["executed"] == 80
    assert metrics["executed_ratio"] == 0.8


def test_partial_run_below_floor_fails_incomplete() -> None:
    # Only 50/100 executed; even with a perfect reachable score it's incomplete.
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=45, survived=5, pending=50),
        score_break=80,
        exec_timed_out=True,
    )
    assert metrics["status"] == "FAIL-incomplete"
    assert metrics["passed"] is False
    assert metrics["executed_ratio"] == 0.5


def test_partial_run_above_floor_but_below_score_threshold() -> None:
    # 80/100 executed, but reachable score 60% < 80% → still FAIL (not -partial).
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=48, survived=32, pending=20),
        score_break=80,
        exec_timed_out=True,
    )
    assert metrics["status"] == "FAIL"
    assert metrics["passed"] is False


def test_partial_run_at_exact_completion_floor() -> None:
    """Boundary: executed_ratio == 0.75 must satisfy the floor (`>=`)."""
    # 75 executed of 100; reachable 60 killed + 15 survived = 75; score 80%.
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=60, survived=15, pending=25),
        score_break=80,
        exec_timed_out=True,
    )
    assert metrics["executed_ratio"] == 0.75
    assert metrics["status"] == "PASS-partial"
    assert metrics["passed"] is False


def test_completion_ratio_excludes_skipped_mutants() -> None:
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=60, survived=15, pending=25, skipped=20),
        score_break=80,
        exec_timed_out=True,
    )
    assert metrics["executable_total"] == 80
    assert metrics["executed"] == 55
    assert metrics["executed_ratio"] == 55 / 80
    assert metrics["status"] == "FAIL-incomplete"


def test_partial_run_requires_per_file_completion() -> None:
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=80, survived=0, pending=20),
        score_break=80,
        exec_timed_out=True,
        per_file_completion_ok=False,
    )
    assert metrics["executed_ratio"] == 0.8
    assert metrics["status"] == "FAIL-incomplete"
    assert metrics["passed"] is False


def test_partial_run_one_mutant_below_floor() -> None:
    """74/100 executed must FAIL-incomplete even with a perfect reachable score."""
    metrics = CMS.mutation_metrics(
        _stats(total=100, killed=74, survived=0, pending=26),
        score_break=80,
        exec_timed_out=True,
    )
    assert metrics["executed_ratio"] < CMS.PARTIAL_RUN_COMPLETION_FLOOR
    assert metrics["status"] == "FAIL-incomplete"
    assert metrics["passed"] is False


def test_timeout_marker_round_trip(tmp_path: Path) -> None:
    marker = tmp_path / "exec-timeout.json"
    marker.write_text('{"exec_timed_out": true, "exec_timeout_seconds": 9000}\n', encoding="utf-8")
    timed_out, seconds = CMS._read_timeout_marker(marker)
    assert timed_out is True
    assert seconds == 9000


def test_timeout_marker_absent_returns_false(tmp_path: Path) -> None:
    timed_out, seconds = CMS._read_timeout_marker(tmp_path / "missing.json")
    assert timed_out is False
    assert seconds is None
