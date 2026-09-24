"""In-memory review and phase-time metrics for task-run lanes.

This store answers aggregate questions by lane label, carrier label, and their
pair. Each ``record_review`` call is one observed review sample; severity
counts add across samples, and rework rate is the fraction of review samples
that needed a follow-up fix lane. Phase observations add elapsed seconds and
also retain their sample counts and means.

Intended integration points are after review observations, when a follow-up
fix lane is known, and where the scheduler or integrator observes phase
durations. Callers should make these telemetry writes best-effort. This module
does not persist data, decide outcomes, gate lane completion, or assert
verdicts; synthetic store tests do not establish live task-run behavior.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

PHASES = ("wait", "run", "integrate", "verify", "rework")
SEVERITIES = ("P1", "P2", "P3")


@dataclass
class _Aggregate:
    review_count: int = 0
    rework_count: int = 0
    findings: dict[str, int] = field(
        default_factory=lambda: {severity: 0 for severity in SEVERITIES}
    )
    phase_totals: dict[str, float] = field(
        default_factory=lambda: {phase: 0.0 for phase in PHASES}
    )
    phase_samples: dict[str, int] = field(
        default_factory=lambda: {phase: 0 for phase in PHASES}
    )

    def record_review(
        self, *, p1: int, p2: int, p3: int, needs_follow_up_fix_lane: bool
    ) -> None:
        self.review_count += 1
        self.rework_count += int(needs_follow_up_fix_lane)
        self.findings["P1"] += p1
        self.findings["P2"] += p2
        self.findings["P3"] += p3

    def record_phase_time(self, phase: str, duration_seconds: float) -> None:
        self.phase_totals[phase] += duration_seconds
        self.phase_samples[phase] += 1

    def snapshot(self) -> dict[str, Any]:
        phase_times = {}
        for phase in PHASES:
            samples = self.phase_samples[phase]
            total = self.phase_totals[phase]
            phase_times[phase] = {
                "total_seconds": total,
                "sample_count": samples,
                "mean_seconds": total / samples if samples else None,
            }
        return {
            "review_count": self.review_count,
            "rework_count": self.rework_count,
            "rework_rate": (
                self.rework_count / self.review_count if self.review_count else None
            ),
            "findings": dict(self.findings),
            "phase_times": phase_times,
        }


def _validate_label(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _validate_count(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _validate_duration(value: int | float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("duration_seconds must be a finite non-negative number")
    try:
        seconds = float(value)
    except OverflowError as exc:
        raise ValueError("duration_seconds must be a finite non-negative number") from exc
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("duration_seconds must be a finite non-negative number")
    return seconds


class TaskRunMetricsStore:
    """Accumulate observations without coupling them to lane verdicts.

    Labels are opaque aggregation keys so the integration slice can choose its
    lane and carrier vocabulary without changing how metrics are accumulated.
    ``snapshot`` returns detached dictionaries; mutating one cannot alter the
    stored observations.
    """

    def __init__(self) -> None:
        self._by_lane: dict[str, _Aggregate] = {}
        self._by_carrier: dict[str, _Aggregate] = {}
        self._by_lane_and_carrier: dict[str, dict[str, _Aggregate]] = {}

    def record_review(
        self,
        lane: str,
        carrier: str,
        *,
        p1: int = 0,
        p2: int = 0,
        p3: int = 0,
        needs_follow_up_fix_lane: bool,
    ) -> None:
        """Add one review sample and its P1/P2/P3 finding counts."""
        lane = _validate_label(lane, "lane")
        carrier = _validate_label(carrier, "carrier")
        p1 = _validate_count(p1, "p1")
        p2 = _validate_count(p2, "p2")
        p3 = _validate_count(p3, "p3")
        if not isinstance(needs_follow_up_fix_lane, bool):
            raise ValueError("needs_follow_up_fix_lane must be a boolean")

        for aggregate in self._aggregates(lane, carrier):
            aggregate.record_review(
                p1=p1,
                p2=p2,
                p3=p3,
                needs_follow_up_fix_lane=needs_follow_up_fix_lane,
            )

    def record_phase_time(
        self, lane: str, carrier: str, phase: str, duration_seconds: int | float
    ) -> None:
        """Add one observed duration for a supported task-run phase."""
        lane = _validate_label(lane, "lane")
        carrier = _validate_label(carrier, "carrier")
        if phase not in PHASES:
            raise ValueError(f"phase must be one of: {', '.join(PHASES)}")
        seconds = _validate_duration(duration_seconds)
        for aggregate in self._aggregates(lane, carrier):
            aggregate.record_phase_time(phase, seconds)

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Return aggregates by lane, by carrier, and by lane/carrier pair."""
        return {
            "by_lane": {
                key: self._by_lane[key].snapshot() for key in sorted(self._by_lane)
            },
            "by_carrier": {
                key: self._by_carrier[key].snapshot()
                for key in sorted(self._by_carrier)
            },
            "by_lane_and_carrier": {
                lane: {
                    carrier: aggregates[carrier].snapshot()
                    for carrier in sorted(aggregates)
                }
                for lane, aggregates in sorted(self._by_lane_and_carrier.items())
            },
        }

    def _aggregates(self, lane: str, carrier: str) -> tuple[_Aggregate, ...]:
        lane_carriers = self._by_lane_and_carrier.setdefault(lane, {})
        return (
            self._by_lane.setdefault(lane, _Aggregate()),
            self._by_carrier.setdefault(carrier, _Aggregate()),
            lane_carriers.setdefault(carrier, _Aggregate()),
        )
