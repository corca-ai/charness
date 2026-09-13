"""Keep the inner mutation exec timeout inside the outer job budget.

Two clocks used to run independently: GitHub ``timeout-minutes`` on the job,
and ``--exec-timeout-seconds`` inside ``cosmic-ray exec``. When the inner
clock was wider, the job cancelled first and the summary read UNEXPLAINED
instead of the exec's own timeout marker (recurrence-class:
inner-timeout-outlives-outer-budget).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

DUMP_RESERVE_SECONDS = 120
MIN_EXEC_SECONDS = 60
JOB_START_ENV = "MUTATION_JOB_START_EPOCH"
JOB_TIMEOUT_ENV = "MUTATION_JOB_TIMEOUT_SECONDS"


class InnerTimeoutExceedsOuterBudget(RuntimeError):
    """The inner exec timeout would outlive the remaining job budget."""


def job_budget_from_env(env: dict[str, str] | None = None) -> tuple[int | None, int | None]:
    source = os.environ if env is None else env
    start_raw = source.get(JOB_START_ENV, "").strip()
    timeout_raw = source.get(JOB_TIMEOUT_ENV, "").strip()
    try:
        start = int(start_raw) if start_raw else None
    except ValueError:
        start = None
    try:
        timeout = int(timeout_raw) if timeout_raw else None
    except ValueError:
        timeout = None
    return start, timeout


def resolve_exec_timeout_seconds(
    requested: int,
    *,
    now_epoch: float | None = None,
    job_start_epoch: int | None = None,
    job_timeout_seconds: int | None = None,
    dump_reserve_seconds: int = DUMP_RESERVE_SECONDS,
    min_exec_seconds: int = MIN_EXEC_SECONDS,
    require_job_budget: bool = False,
) -> tuple[int, str | None]:
    """Cap inner exec timeout so dump can still run before the outer job dies.

    When job-budget facts are absent (a local run), return ``requested``
    unchanged unless ``require_job_budget`` is true (CI). When remaining outer
    time minus dump reserve is below ``min_exec_seconds``, raise
    ``InnerTimeoutExceedsOuterBudget`` instead of starting an exec the job
    will cancel first.
    """
    if job_start_epoch is None or job_timeout_seconds is None:
        if require_job_budget:
            raise InnerTimeoutExceedsOuterBudget(
                "CI mutation exec requires MUTATION_JOB_START_EPOCH and "
                "MUTATION_JOB_TIMEOUT_SECONDS; refusing to run an uncapped inner timeout"
            )
        return requested, None
    now = int(now_epoch if now_epoch is not None else time.time())
    remaining = job_timeout_seconds - (now - job_start_epoch) - dump_reserve_seconds
    if remaining < min_exec_seconds:
        raise InnerTimeoutExceedsOuterBudget(
            f"remaining outer budget {remaining}s is below min exec {min_exec_seconds}s "
            f"(job_timeout={job_timeout_seconds}s, elapsed={now - job_start_epoch}s, "
            f"dump_reserve={dump_reserve_seconds}s)"
        )
    if remaining < requested:
        return remaining, (
            f"capped exec timeout {requested}s -> {remaining}s so dump fits in the "
            f"remaining outer budget"
        )
    return requested, None


def write_outer_budget_skip_marker(
    marker_path: Path, *, requested: int, reason: str
) -> None:
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(
        json.dumps(
            {
                "exec_timed_out": False,
                "exec_skipped_outer_budget": True,
                "exec_timeout_seconds": requested,
                "reason": reason,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
