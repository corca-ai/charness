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
import sys
import time
from pathlib import Path

import pytest

from tests.repo_copy import clone_seeded_charness_repo

from .support import assert_quality_receipt

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def gate_repo(tmp_path: Path, seeded_charness_git_repo: Path) -> Path:
    """An isolated copy to drive the real gate in.

    The first cut wrote its probe artifact into the live checkout, and
    `check_test_repo_copy_invariants` refused it — rightly: an xdist worker or a
    snapshot-based test could observe the transient state. Same refusal this session
    already earned once, on a different test.
    """
    return clone_seeded_charness_repo(tmp_path, seeded_charness_git_repo)


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
    """A redirected run must not look like a command that never started.

    Phase commands deliberately write to private logs so parallel output cannot
    interleave. The progress channel has to cross that buffering boundary: observing
    it only after ``flush_phase`` returns would recreate the zero-byte transcript that
    prompted this regression test.
    """
    slow_validator = gate_repo / "scripts" / "validate_retro_artifact.py"
    slow_validator.write_text(
        "import time\ntime.sleep(30)\n",
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "CHARNESS_QUALITY_LABELS": "validate-retro-artifact",
        "CHARNESS_QUALITY_HEARTBEAT_SECONDS": "1",
    }
    transcript = gate_repo / "run-quality-progress.log"
    with transcript.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            ["./scripts/run-quality.sh"],
            cwd=gate_repo,
            stdout=stream,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            start_new_session=True,
        )
        try:
            observed = ""
            deadline = time.monotonic() + 5
            expected_batch = (
                "run-quality: BATCH_START checks=1 first=validate-retro-artifact "
                "last=validate-retro-artifact"
            )
            while time.monotonic() < deadline:
                observed = transcript.read_text(encoding="utf-8")
                if "run-quality: HEARTBEAT remaining=1 " in observed:
                    break
                if process.poll() is not None:
                    break
                time.sleep(0.05)
            assert "requested_scope=validate-retro-artifact" in observed, observed
            assert "run-quality: CHECK_START label=validate-retro-artifact" in observed, observed
            assert expected_batch in observed, observed
            assert "run-quality: HEARTBEAT remaining=1 " in observed, observed
            assert "running=validate-retro-artifact:" in observed, observed
            assert process.poll() is None, "progress arrived only after the slow gate exited"
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
    probe = gate_repo / "charness-artifacts" / "retro" / "2026-08-04-receipt-write-probe-retro.md"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("# Session Retro\nDate: 2026-08-04\n\n## Context\n\nProbe.\n", encoding="utf-8")
    blocked = gate_repo / "receipt-target"
    blocked.mkdir()
    result = _run_gate(gate_repo, receipt_path=blocked)

    assert result.returncode == 1
    assert "proof receipt: could not write" in result.stderr
    assert result.stdout.splitlines()[-1].startswith("Quality summary:"), result.stdout


def test_run_quality_summary_names_its_failing_checks(gate_repo: Path) -> None:
    """Drive a REAL failure and read only the tail, exactly as a truncating reader
    would. The retro validator is used because it fails on a well-formed but
    incomplete artifact, needing no repo damage to trigger."""
    probe = gate_repo / "charness-artifacts" / "retro" / "2026-08-04-summary-contract-probe-retro.md"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text(
        "# Session Retro\nDate: 2026-08-04\n\n## Context\n\nProbe artifact for the "
        "gate-summary contract test; deliberately missing required sections.\n",
        encoding="utf-8",
    )

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

    A VALID retro artifact is placed first. The seeded clone excludes
    `charness-artifacts/`, and this repo refuses an empty-scope green — so without one
    the validator fails for a reason that has nothing to do with the contract under
    test, and the control would pass for the wrong reason.
    """
    valid = ROOT / "charness-artifacts" / "retro" / "2026-08-07-finish-the-sweeps-this-run-left-retro.md"
    target = gate_repo / "charness-artifacts" / "retro" / valid.name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(valid.read_text(encoding="utf-8"), encoding="utf-8")
    # Committed, because the validator discovers artifacts through git.
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "seed a valid retro"], cwd=gate_repo,
                   check=True, capture_output=True)

    result = _run_gate(gate_repo)

    assert "0 failed" in result.stdout, result.stdout[-400:]

    summary = [line for line in result.stdout.splitlines() if line.startswith("Quality summary:")]
    assert summary, result.stdout[-500:]
    assert "FAILED:" not in summary[-1], summary[-1]
    assert "quality-failure-logs" not in result.stdout.split("Quality summary:")[-1]


def test_slice_closeout_repeats_its_verdict_last() -> None:
    """`Closeout status:` prints at the TOP of a report that runs to a hundred lines,
    so truncation kept a telemetry footer and lost the verdict. It is repeated
    last, with the failing command named."""
    import contextlib
    import io
    from importlib import util

    spec = util.spec_from_file_location(
        "slice_closeout_reporting", ROOT / "scripts" / "slice_closeout_reporting.py"
    )
    module = util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)

    payload = {
        "status": "failed",
        "changed_paths": [], "matched_surfaces": [], "unmatched_paths": [],
        "executed_commands": [
            {"phase": "verify", "returncode": 0, "command": "python3 fine.py"},
            {"phase": "verify", "returncode": 1, "command": "python3 broken.py"},
        ],
    }
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        module._print_final_verdict(payload)
    line = buffer.getvalue().strip()

    assert line.startswith("Closeout verdict: failed"), line
    assert "python3 broken.py" in line, line
    assert "python3 fine.py" not in line, "only the FAILING command belongs in the verdict"


def test_a_log_copy_that_fails_warns_instead_of_promising_a_stale_file(gate_repo: Path) -> None:
    """A path claim the file does not back is worse than no claim.

    The first cut ran the copy under `|| true` next to an UNCONDITIONAL "the log is
    here" line. When the copy failed, the reader was pointed at a path that either held
    nothing or — worse — held a PREVIOUS run's log for the same label, and would
    diagnose a failure that was already fixed. A stale log at a promised path is the
    same silent-loss shape this whole change exists to remove, reintroduced inside the
    repair.
    """
    probe = gate_repo / "charness-artifacts" / "retro" / "2026-08-04-copy-failure-probe-retro.md"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("# Session Retro\nDate: 2026-08-04\n\n## Context\n\nProbe.\n", encoding="utf-8")

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
