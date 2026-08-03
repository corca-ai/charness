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

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from tests.repo_copy import clone_seeded_charness_repo

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


def _run_gate(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["./scripts/run-quality.sh"],
        cwd=repo, capture_output=True, text=True,
        env={**os.environ, "CHARNESS_QUALITY_LABELS": "validate-retro-artifact"},
    )


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

    tail = result.stdout.strip().splitlines()[-3:]
    joined = "\n".join(tail)

    assert re.search(r"Quality summary: \d+ passed, [1-9]\d* failed", joined), joined
    assert "(FAILED: validate-retro-artifact)" in joined, (
        "the summary must NAME the failing check, not just count it: the count alone "
        f"is what forced a re-run. Got tail:\n{joined}"
    )
    assert ".charness/quality-failure-logs/" in joined, (
        f"a truncated read must still be told where the full output is. Got:\n{joined}"
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
    so truncation kept a usage-episode footer and lost the verdict. It is repeated
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
