"""Inner exec timeout must not outlive the outer job budget."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts.mutation.mutation_outer_budget import (
    InnerTimeoutExceedsOuterBudget,
    job_budget_from_env,
    resolve_exec_timeout_seconds,
    write_outer_budget_skip_marker,
)


def test_absent_job_budget_leaves_the_requested_timeout() -> None:
    timeout, reason = resolve_exec_timeout_seconds(9000)
    assert timeout == 9000
    assert reason is None


def test_ci_without_job_budget_refuses_an_uncapped_exec() -> None:
    with pytest.raises(InnerTimeoutExceedsOuterBudget, match="refusing to run an uncapped"):
        resolve_exec_timeout_seconds(9000, require_job_budget=True)


def test_inner_timeout_is_capped_to_remaining_outer_budget() -> None:
    timeout, reason = resolve_exec_timeout_seconds(
        9000,
        now_epoch=1_000_000,
        job_start_epoch=1_000_000 - 1800,
        job_timeout_seconds=10_800,
    )
    # 10800 - 1800 elapsed - 120 dump reserve = 8880
    assert timeout == 8880
    assert reason is not None
    assert "9000s -> 8880s" in reason


def test_inner_timeout_that_already_fits_is_unchanged() -> None:
    timeout, reason = resolve_exec_timeout_seconds(
        600,
        now_epoch=1_000_000,
        job_start_epoch=1_000_000,
        job_timeout_seconds=10_800,
    )
    assert timeout == 600
    assert reason is None


def test_no_remaining_outer_budget_refuses_exec() -> None:
    with pytest.raises(InnerTimeoutExceedsOuterBudget, match="below min exec"):
        resolve_exec_timeout_seconds(
            9000,
            now_epoch=1_000_000,
            job_start_epoch=1_000_000 - 10_700,
            job_timeout_seconds=10_800,
        )


def test_job_budget_from_env_parses_and_ignores_junk() -> None:
    start, timeout = job_budget_from_env(
        {"MUTATION_JOB_START_EPOCH": "10", "MUTATION_JOB_TIMEOUT_SECONDS": "10800"}
    )
    assert start == 10
    assert timeout == 10800
    start, timeout = job_budget_from_env(
        {"MUTATION_JOB_START_EPOCH": "nope", "MUTATION_JOB_TIMEOUT_SECONDS": ""}
    )
    assert start is None
    assert timeout is None


def test_job_budget_from_env_ignores_a_bad_timeout_but_keeps_start() -> None:
    start, timeout = job_budget_from_env(
        {"MUTATION_JOB_START_EPOCH": "10", "MUTATION_JOB_TIMEOUT_SECONDS": "nope"}
    )
    assert start == 10
    assert timeout is None


def test_both_mutation_workflows_export_the_outer_budget_env() -> None:
    from tests.quality_gates.test_quality_mutation_testing import _mutation_workflow_copies

    for path in _mutation_workflow_copies():
        text = path.read_text(encoding="utf-8")
        minutes = int(re.search(r"timeout-minutes:\s+(\d+)", text).group(1))
        seconds = int(re.search(r"MUTATION_JOB_TIMEOUT_SECONDS=(\d+)", text).group(1))
        assert seconds == minutes * 60, path
        assert "MUTATION_JOB_START_EPOCH=$(date +%s)" in text, path
        assert text.index("Record mutation job outer budget") < text.index("name: Checkout"), path


def test_skip_marker_names_the_outer_budget_not_an_exec_timeout(tmp_path: Path) -> None:
    marker = tmp_path / "exec-timeout.json"
    write_outer_budget_skip_marker(marker, requested=9000, reason="remaining outer budget 12s")
    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert payload["exec_timed_out"] is False
    assert payload["exec_skipped_outer_budget"] is True
    assert payload["exec_timeout_seconds"] == 9000
