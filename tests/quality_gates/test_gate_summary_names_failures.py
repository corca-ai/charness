"""The last line of a gate must be self-sufficient.

`tail` preserves the END of a stream, so the last line is the one every truncation
survives — a human scrolling, a CI log tail, an agent bounding its context. When the
summary reported only a COUNT (`85 passed, 1 failed`), a truncated read kept the
number and lost the one fact it could act on, and recovering it cost a full re-run of
a ~95s gate. Measured: ~10 minutes in one session.

The fix is not to forbid truncating. It is to make truncation harmless, by putting
what the reader needs where truncation cannot reach it.
"""
from __future__ import annotations

import contextlib
import os
import re
import signal
import subprocess
from pathlib import Path

import pytest

from .support import assert_quality_receipt, clone_quality_runner_repo

ROOT = Path(__file__).resolve().parents[2]

#: The label these tests drive. Nothing here is about the retro validator; it is the
#: label whose queue line already exists in the real runner, so driving it exercises the
#: runner's own reporting path rather than a synthetic one.
_LABEL = "validate-retro-artifact"


@pytest.fixture
def gate_repo(tmp_path: Path, seeded_quality_runner_repo: Path) -> Path:
    """A minimal runner repo, not a copy of this one.

    This file used to clone the whole checkout (`clone_seeded_charness_repo`) and
    git-commit inside it, costing ~7.3s of SETUP per test. Nothing here needs a
    repository: the contract under test is what `run-quality.sh` PRINTS, and the only
    other moving part is one gate that must pass or fail on demand. `make_quality_runner_repo`
    already builds exactly that fixture -- the real runner, the real exported-copy guard,
    the real label-universe reader, and stub gates -- and the sibling
    `test_quality_runner_release_order.py` has been using it all along.

    The full clone was never load-bearing: the very first test already overwrote the
    real validator with a two-line sleep stub.
    """

    repo, _env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    return repo


def _seed_gate(repo: Path, body: str) -> None:
    """Install the one gate this run queues. Stubbed BECAUSE it is not what is proven.

    The runner, its export-copy guard, and its label-universe reader are all real in
    this fixture; only the gate's verdict is under the test's control, which is the
    whole point -- a reporting contract needs a pass and a fail on demand, not a
    validator with opinions of its own about artifacts.
    """

    validator = repo / "scripts" / "gates" / "validate_retro_artifact.py"
    validator.parent.mkdir(parents=True, exist_ok=True)
    validator.write_text(body, encoding="utf-8")


def _run_gate(
    repo: Path,
    *,
    receipt_path: Path | None = None,
    labels: str = "validate-retro-artifact",
    fail_label: str | None = None,
) -> subprocess.CompletedProcess:
    runtime_root = repo.parent / "quality-runtime"
    env = {
        **os.environ,
        "CHARNESS_QUALITY_LABELS": labels,
        "CHARNESS_RUNTIME_ROOT": str(runtime_root),
        "CHARNESS_RUNTIME_ROOT_AUTO": "0",
    }
    if receipt_path is not None:
        env["CHARNESS_QUALITY_RECEIPT_JSON"] = str(receipt_path)
    if fail_label is not None:
        env["QUALITY_FAIL_LABEL"] = fail_label
    return subprocess.run(
        ["./scripts/run-quality.sh"],
        cwd=repo, capture_output=True, text=True,
        env=env,
    )


def test_run_quality_emits_progress_before_a_slow_phase_finishes(gate_repo: Path) -> None:
    """A non-tty run must emit progress before a slow phase finishes.

    Phase commands deliberately write to private logs so parallel output cannot
    interleave. The progress channel has to cross that buffering boundary: observing
    it only after ``flush_phase`` returns would recreate the zero-byte transcript that
    prompted this regression test. The child is read through a pipe rather than a tty,
    so the block-buffering property this test cares about is preserved.
    """
    _seed_gate(gate_repo, "import time\ntime.sleep(30)\n")
    env = {
        **os.environ,
        "CHARNESS_QUALITY_LABELS": _LABEL,
        "CHARNESS_QUALITY_HEARTBEAT_SECONDS": "1",
    }
    process = subprocess.Popen(
        ["./scripts/run-quality.sh"],
        cwd=gate_repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        start_new_session=True,
    )
    try:
        observed = ""
        expected_batch = (
            "run-quality: BATCH_START checks=1 first=validate-retro-artifact "
            "last=validate-retro-artifact"
        )
        assert process.stdout is not None
        while "run-quality: HEARTBEAT remaining=1 " not in observed:
            line = process.stdout.readline()
            if line == "":
                break
            observed += line
        assert "requested_scope=validate-retro-artifact" in observed, observed
        assert "run-quality: CHECK_START label=validate-retro-artifact" in observed, observed
        assert expected_batch in observed, observed
        assert "run-quality: HEARTBEAT remaining=1 " in observed, observed
        assert "running=validate-retro-artifact:" in observed, observed
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)


def test_run_quality_preserves_gate_exit_when_receipt_write_fails(gate_repo: Path) -> None:
    _seed_gate(gate_repo, "raise SystemExit(1)\n")
    blocked = gate_repo / "receipt-target"
    blocked.mkdir()
    result = _run_gate(gate_repo, receipt_path=blocked)

    assert result.returncode == 1
    assert "proof receipt: could not write" in result.stderr
    assert result.stdout.splitlines()[-1].startswith("Quality summary:"), result.stdout


def test_run_quality_summary_names_its_failing_checks(gate_repo: Path) -> None:
    """Drive a failing gate and read only the tail, exactly as a truncating reader would."""
    _seed_gate(gate_repo, "raise SystemExit(1)\n")

    result = _run_gate(gate_repo)

    summary_line = [line for line in result.stdout.splitlines() if line.startswith("Quality summary:")][-1]

    assert re.search(r"Quality summary: \d+ passed, [1-9]\d* failed", summary_line), summary_line
    expected_log = gate_repo.parent / "quality-runtime" / "quality-failure-logs" / "validate-retro-artifact.log"
    assert f"(FAILED: validate-retro-artifact [log: {expected_log}])" in summary_line, (
        "the summary must NAME the failing check, not just count it: the count alone "
        f"is what forced a re-run, and its final line must carry the recovery path. Got:\n{summary_line}"
    )
    assert str(expected_log.parent) in summary_line, (
        f"a truncated read must still be told where the full output is. Got:\n{summary_line}"
    )


def test_a_clean_run_summary_is_unchanged(gate_repo: Path) -> None:
    """The false-positive control: naming failures must not add noise to a green run.
    A summary that grows a `(FAILED: )` on success would be a new thing to read past.

    The passing arm used to need a VALID retro artifact copied out of this checkout and
    then git-committed, because the real validator discovers artifacts through git. With
    the verdict under the test's control, the control proves the same thing without a
    repository, an artifact, or a commit.
    """
    _seed_gate(gate_repo, "raise SystemExit(0)\n")

    result = _run_gate(gate_repo)

    assert "0 failed" in result.stdout, result.stdout[-400:]

    summary = [line for line in result.stdout.splitlines() if line.startswith("Quality summary:")]
    assert summary, result.stdout[-500:]
    assert "FAILED:" not in summary[-1], summary[-1]
    assert "quality-failure-logs" not in result.stdout.split("Quality summary:")[-1]


def test_a_log_copy_that_fails_warns_instead_of_promising_a_stale_file(gate_repo: Path) -> None:
    """A path claim the file does not back is worse than no claim.

    The first cut ran the copy under `|| true` next to an UNCONDITIONAL "the log is
    here" line. When the copy failed, the reader was pointed at a path that either held
    nothing or — worse — held a PREVIOUS run's log for the same label, and would
    diagnose a failure that was already fixed. A stale log at a promised path is the
    same silent-loss shape this whole change exists to remove, reintroduced inside the
    repair.
    """
    _seed_gate(gate_repo, "raise SystemExit(1)\n")

    # Occupy the copy target with a read-only file, so the copy cannot land.
    log_dir = gate_repo.parent / "quality-runtime" / "quality-failure-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stale = log_dir / "validate-retro-artifact.log"
    stale.write_text("STALE OUTPUT FROM AN EARLIER RUN\n", encoding="utf-8")
    stale.chmod(0o400)

    receipt_path = gate_repo / "receipt.json"
    try:
        result = _run_gate(gate_repo, receipt_path=receipt_path)
    finally:
        stale.chmod(0o600)

    assert "could not save full output for validate-retro-artifact" in result.stderr, result.stderr[-400:]
    assert "Full output for each failing check:" not in result.stdout, (
        "the path must be WITHHELD when the copy did not land, or the reader is sent "
        f"to a stale file:\n{result.stdout[-400:]}"
    )
    # the verdict itself still names the failure
    assert "(FAILED: validate-retro-artifact [log unavailable])" in result.stdout
    assert "quality-failure-logs/validate-retro-artifact.log" not in result.stdout
    assert stale.read_text(encoding="utf-8").startswith("STALE"), "the stale file was not overwritten"
    assert_quality_receipt(
        gate_repo,
        result,
        status="fail",
        passed=0,
        failed=1,
        adverse_subjects=["validate-retro-artifact"],
        adverse_recoveries=[{"status": "unavailable", "reason": "full output could not be copied"}],
    )
