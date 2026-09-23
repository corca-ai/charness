"""Synthetic accumulation checks for the task-run metrics store.

These tests observe the in-memory API only; they do not exercise live lane
completion or prove that an integration caller records every event.
"""

from __future__ import annotations

import pytest

from scripts.task_run.task_run_metrics import TaskRunMetricsStore


def test_reviews_accumulate_by_lane_carrier_and_pair() -> None:
    metrics = TaskRunMetricsStore()

    assert metrics.record_review(
        "implementation",
        "carrier-a",
        p1=1,
        p2=2,
        needs_follow_up_fix_lane=True,
    ) is None
    metrics.record_review(
        "implementation", "carrier-a", p2=1, p3=3, needs_follow_up_fix_lane=False
    )
    metrics.record_review(
        "implementation", "carrier-b", p1=2, p3=1, needs_follow_up_fix_lane=True
    )
    metrics.record_review(
        "review", "carrier-a", p2=1, p3=1, needs_follow_up_fix_lane=False
    )

    snapshot = metrics.snapshot()
    implementation = snapshot["by_lane"]["implementation"]
    assert implementation["review_count"] == 3
    assert implementation["rework_count"] == 2
    assert implementation["rework_rate"] == pytest.approx(2 / 3)
    assert implementation["findings"] == {"P1": 3, "P2": 3, "P3": 4}

    carrier_a = snapshot["by_carrier"]["carrier-a"]
    assert carrier_a["review_count"] == 3
    assert carrier_a["rework_count"] == 1
    assert carrier_a["rework_rate"] == pytest.approx(1 / 3)
    assert carrier_a["findings"] == {"P1": 1, "P2": 4, "P3": 4}

    implementation_carrier_a = snapshot["by_lane_and_carrier"]["implementation"]["carrier-a"]
    assert implementation_carrier_a["review_count"] == 2
    assert implementation_carrier_a["rework_rate"] == 0.5
    assert implementation_carrier_a["findings"] == {"P1": 1, "P2": 3, "P3": 3}


def test_phase_times_accumulate_seconds_and_samples_by_lane_and_carrier() -> None:
    metrics = TaskRunMetricsStore()

    observations = (
        ("implementation", "carrier-a", "wait", 1.5),
        ("implementation", "carrier-a", "wait", 2.5),
        ("implementation", "carrier-a", "run", 4),
        ("implementation", "carrier-a", "integrate", 3),
        ("implementation", "carrier-a", "verify", 0.5),
        ("implementation", "carrier-a", "rework", 2),
        ("implementation", "carrier-b", "wait", 4),
        ("implementation", "carrier-b", "run", 6),
        ("review", "carrier-a", "wait", 3),
    )
    for lane, carrier, phase, seconds in observations:
        assert metrics.record_phase_time(lane, carrier, phase, seconds) is None

    snapshot = metrics.snapshot()
    lane_wait = snapshot["by_lane"]["implementation"]["phase_times"]["wait"]
    assert lane_wait == {
        "total_seconds": 8.0,
        "sample_count": 3,
        "mean_seconds": pytest.approx(8 / 3),
    }

    carrier_wait = snapshot["by_carrier"]["carrier-a"]["phase_times"]["wait"]
    assert carrier_wait == {
        "total_seconds": 7.0,
        "sample_count": 3,
        "mean_seconds": pytest.approx(7 / 3),
    }

    pair = snapshot["by_lane_and_carrier"]["implementation"]["carrier-a"]
    assert pair["phase_times"]["wait"] == {
        "total_seconds": 4.0,
        "sample_count": 2,
        "mean_seconds": 2.0,
    }
    assert pair["phase_times"]["integrate"]["total_seconds"] == 3.0
    assert pair["phase_times"]["verify"]["total_seconds"] == 0.5
    assert pair["phase_times"]["rework"]["total_seconds"] == 2.0
    assert pair["phase_times"]["run"]["total_seconds"] == 4.0


def test_empty_samples_have_no_rate_or_phase_mean() -> None:
    metrics = TaskRunMetricsStore()
    metrics.record_phase_time("implementation", "carrier-a", "wait", 0)

    summary = metrics.snapshot()["by_lane"]["implementation"]
    assert summary["review_count"] == 0
    assert summary["rework_count"] == 0
    assert summary["rework_rate"] is None
    assert summary["phase_times"]["wait"]["mean_seconds"] == 0
    assert summary["phase_times"]["run"] == {
        "total_seconds": 0.0,
        "sample_count": 0,
        "mean_seconds": None,
    }


def test_invalid_observation_does_not_change_the_snapshot() -> None:
    metrics = TaskRunMetricsStore()
    before = metrics.snapshot()

    with pytest.raises(ValueError, match="phase"):
        metrics.record_phase_time("implementation", "carrier-a", "deploy", 1)
    with pytest.raises(ValueError, match="non-negative"):
        metrics.record_review(
            "implementation", "carrier-a", p1=-1, needs_follow_up_fix_lane=False
        )
    with pytest.raises(ValueError, match="duration_seconds"):
        metrics.record_phase_time("implementation", "carrier-a", "wait", float("nan"))

    assert metrics.snapshot() == before
