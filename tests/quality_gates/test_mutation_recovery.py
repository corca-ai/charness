"""Process-death and later-consumer proof for mutation recovery."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "mutate_and_restore.py"
mar = import_repo_module(SCRIPT, "scripts.mutate_and_restore")


def _interruptible_plan(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "interrupted-repo"
    repo.mkdir()
    target = repo / "subject.py"
    target.write_text("STATE = 'ORIGINAL'\n", encoding="utf-8")
    (repo / "runner.py").write_text(
        "import os\n"
        "import time\n"
        "from pathlib import Path\n"
        "text = Path('subject.py').read_text(encoding='utf-8')\n"
        "if 'MUTATED' in text:\n"
        "    Path('runner.pid').write_text(str(os.getpid()), encoding='utf-8')\n"
        "    time.sleep(30)\n"
        "print('1 passed in 0.01s')\n",
        encoding="utf-8",
    )
    plan_path = repo / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "test_command": [sys.executable, "runner.py"],
                "mutants": [
                    {
                        "id": "interrupt-me",
                        "path": "subject.py",
                        "find": "ORIGINAL",
                        "replace": "MUTATED",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return repo, plan_path


def _wait_for_mutation(repo: Path) -> None:
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if "MUTATED" in (repo / "subject.py").read_text(encoding="utf-8") and (repo / "runner.pid").exists():
            return
        time.sleep(0.02)
    raise AssertionError("the subprocess never reached the active mutation")


def test_sigterm_routes_through_restore_and_clears_the_journal(tmp_path: Path) -> None:
    repo, plan_path = _interruptible_plan(tmp_path)
    process = subprocess.Popen(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    _wait_for_mutation(repo)

    process.send_signal(signal.SIGTERM)
    _stdout, stderr = process.communicate(timeout=8)

    assert process.returncode == 128 + signal.SIGTERM, stderr
    assert "any active mutation was restored" in stderr
    assert (repo / "subject.py").read_text(encoding="utf-8") == "STATE = 'ORIGINAL'\n"
    assert not mar.MutationRecovery(repo).pending


def test_sigkill_leaves_a_detectable_journal_that_recovers_exact_bytes(tmp_path: Path) -> None:
    repo, plan_path = _interruptible_plan(tmp_path)
    process = subprocess.Popen(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    _wait_for_mutation(repo)
    child_pid = int((repo / "runner.pid").read_text(encoding="utf-8"))
    try:
        process.kill()
        process.communicate(timeout=8)

        assert process.returncode == -signal.SIGKILL
        assert "MUTATED" in (repo / "subject.py").read_text(encoding="utf-8")
        assert mar.MutationRecovery(repo).pending

        check = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--check-recovery"],
            capture_output=True,
            text=True,
        )
        assert check.returncode == 2
        assert "recovery is REQUIRED" in check.stderr

        recovered = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--recover"],
            capture_output=True,
            text=True,
        )
        assert recovered.returncode == 0, recovered.stderr
        assert "restored subject.py" in recovered.stdout
        assert (repo / "subject.py").read_text(encoding="utf-8") == "STATE = 'ORIGINAL'\n"
        assert list(repo.glob(".subject.py.charness-write-*")) == []
        assert not mar.MutationRecovery(repo).pending
        child_stat = Path(f"/proc/{child_pid}/stat")
        assert not child_stat.exists() or child_stat.read_text(encoding="utf-8").rsplit(")", 1)[1].split()[0] == "Z", (
            "recovery returned while the mutated test child was still active"
        )
    finally:
        try:
            os.kill(child_pid, signal.SIGTERM)
        except ProcessLookupError:
            pass


def test_recovery_refuses_to_overwrite_bytes_changed_after_the_mutation(tmp_path: Path) -> None:
    repo = tmp_path / "conflicted-repo"
    repo.mkdir()
    target = repo / "subject.py"
    original = b"ORIGINAL\n"
    mutated = b"MUTATED\n"
    target.write_bytes(original)
    recovery = mar.MutationRecovery(repo)
    recovery.begin(target, original, mutated)
    target.write_bytes(b"HUMAN EDIT\n")

    with pytest.raises(mar.SweepError, match="refusing to overwrite"):
        recovery.recover(mar.restore)

    assert target.read_bytes() == b"HUMAN EDIT\n"
    assert recovery.pending, "the unresolved ownership record must stay visible"


def test_commit_and_quality_consumers_refuse_pending_recovery_then_unblock(tmp_path: Path) -> None:
    quality_repo = tmp_path / "quality-consumer"
    (quality_repo / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "run-quality.sh", quality_repo / "scripts" / "run-quality.sh")
    quality_state = quality_repo / ".charness" / "mutation-recovery"
    quality_state.mkdir(parents=True)

    blocked_quality = subprocess.run(
        ["bash", "scripts/run-quality.sh", "--read-only"],
        cwd=quality_repo,
        capture_output=True,
        text=True,
    )
    assert blocked_quality.returncode == 2
    assert "interrupted mutation recovery is REQUIRED" in blocked_quality.stderr
    quality_state.rmdir()
    unblocked_quality = subprocess.run(
        ["bash", "scripts/run-quality.sh", "--read-only"],
        cwd=quality_repo,
        capture_output=True,
        text=True,
    )
    assert "interrupted mutation recovery is REQUIRED" not in unblocked_quality.stderr

    commit_repo = tmp_path / "commit-consumer"
    (commit_repo / ".githooks").mkdir(parents=True)
    (commit_repo / "scripts").mkdir()
    subprocess.run(["git", "init", "-q"], cwd=commit_repo, check=True)
    shutil.copy2(ROOT / ".githooks" / "pre-commit", commit_repo / ".githooks" / "pre-commit")
    (commit_repo / "scripts" / "run_slice_closeout.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    commit_state = commit_repo / ".git" / "charness-mutation-recovery"
    commit_state.mkdir()

    blocked_commit = subprocess.run(
        ["bash", ".githooks/pre-commit"], cwd=commit_repo, capture_output=True, text=True
    )
    assert blocked_commit.returncode == 2
    assert "interrupted mutation recovery is REQUIRED" in blocked_commit.stderr
    commit_state.rmdir()
    unblocked_commit = subprocess.run(
        ["bash", ".githooks/pre-commit"], cwd=commit_repo, capture_output=True, text=True
    )
    assert unblocked_commit.returncode == 0, unblocked_commit.stderr
