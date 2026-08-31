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
mr = sys.modules[mar.MutationRecovery.__module__]
#: The file `mr` must resolve to. Named as a literal because the hop above is invisible to
#: the mutation-pool mapper: it walks imports and text, and this module is reached through
#: a `sys.modules` lookup keyed on a class's `__module__`, so `scripts/mutation_recovery.py`
#: mapped to NO standing test and its changed lines went unjudged (PARTIAL, exit 4).
#: Re-importing the file to fix that would bind a SECOND module object, and the
#: monkeypatching below would then patch a module nothing under test uses.
RECOVERY_SOURCE = ROOT / "scripts" / "mutation_recovery.py"


def test_the_module_under_test_is_the_file_on_disk() -> None:
    # Asserts what THIS module bound, not a global interpreter property: the `sys.modules`
    # hop above could silently resolve elsewhere if `mutate_and_restore` were refactored to
    # import MutationRecovery from a shim, and every monkeypatch below would then patch a
    # module nothing under test uses -- passing tests over unexercised code.
    assert Path(mr.__file__).resolve() == RECOVERY_SOURCE.resolve()


def _seed_recovery(tmp_path: Path, name: str = "recovery-repo"):
    repo = tmp_path / name
    repo.mkdir()
    target = repo / "subject.py"
    original = b"ORIGINAL\n"
    mutated = b"MUTATED\n"
    target.write_bytes(original)
    recovery = mar.MutationRecovery(repo)
    journal_id = recovery.begin(target, original, mutated)
    return repo, target, recovery, journal_id, original, mutated


def _rewrite_journal(recovery, update) -> None:
    payload = json.loads(recovery.journal_path.read_text(encoding="utf-8"))
    update(payload)
    recovery.journal_path.write_text(json.dumps(payload), encoding="utf-8")


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


def test_recovery_state_dir_handles_git_exec_failure_and_relative_git_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unavailable(*_args, **_kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(mr.subprocess, "run", unavailable)
    assert mr.recovery_state_dir(tmp_path) == tmp_path / ".charness" / "mutation-recovery"

    monkeypatch.setenv("GIT_DIR", str(tmp_path / ".git"))
    completed = subprocess.CompletedProcess(["git"], 0, ".git\n", "")
    monkeypatch.setattr(mr.subprocess, "run", lambda *_args, **_kwargs: completed)
    assert mr.recovery_state_dir(tmp_path) == (tmp_path / ".git" / "charness-mutation-recovery").resolve()


def test_begin_refuses_existing_owner_and_removes_partial_record_on_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, target, recovery, journal_id, original, mutated = _seed_recovery(tmp_path, "owned")
    with pytest.raises(mar.SweepError, match="refuse to overwrite"):
        recovery.begin(target, original, mutated)
    with pytest.raises(mar.SweepError, match="already exists"):
        recovery.assert_clear()
    recovery.clear(journal_id)

    repo = tmp_path / "partial"
    repo.mkdir()
    target = repo / "subject.py"
    target.write_bytes(original)
    failed = mar.MutationRecovery(repo)

    def fail_after_partial(_payload) -> None:
        (failed.state_dir / "partial").write_text("partial", encoding="utf-8")
        raise RuntimeError("journal write failed")

    monkeypatch.setattr(failed, "_write_payload", fail_after_partial)
    with pytest.raises(RuntimeError, match="journal write failed"):
        failed.begin(target, original, mutated)
    assert not failed.state_dir.exists()


def test_journal_read_and_clear_refuse_corruption_and_changed_ownership(tmp_path: Path) -> None:
    _repo, _target, invalid, _journal_id, _original, _mutated = _seed_recovery(tmp_path, "invalid-json")
    invalid.journal_path.write_text("{", encoding="utf-8")
    with pytest.raises(mar.SweepError, match="unreadable"):
        invalid._read()

    _repo, _target, unsupported, _journal_id, _original, _mutated = _seed_recovery(tmp_path, "unsupported")
    _rewrite_journal(unsupported, lambda payload: payload.update(version=9))
    with pytest.raises(mar.SweepError, match="unsupported version"):
        unsupported._read()

    _repo, _target, recovery, journal_id, _original, _mutated = _seed_recovery(tmp_path, "ownership")
    with pytest.raises(mar.SweepError, match="ownership changed"):
        recovery.clear("another-owner")
    staged = recovery.state_dir / "journal.leftover.tmp"
    staged.write_text("stale", encoding="utf-8")
    recovery.clear(journal_id)
    assert not staged.exists()
    assert not recovery.pending


def test_attach_child_refuses_early_exit_timeout_invalid_marker_and_changed_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Process:
        def __init__(self, returncode):
            self.returncode = returncode

        def poll(self):
            return self.returncode

    _repo, _target, exited, journal_id, _original, _mutated = _seed_recovery(tmp_path, "exited")
    with pytest.raises(mar.SweepError, match="exited before recording"):
        exited.attach_child(journal_id, Process(1))

    _repo, _target, timed_out, journal_id, _original, _mutated = _seed_recovery(tmp_path, "timeout")
    clock = iter((0.0, 6.0))
    with monkeypatch.context() as timeout_patch:
        timeout_patch.setattr(mr.time, "monotonic", lambda: next(clock))
        with pytest.raises(mar.SweepError, match="did not record"):
            timed_out.attach_child(journal_id, Process(None))

    # A marker that is still unreadable when the deadline expires. The clock is driven
    # because the wait is now a retry loop: an unreadable marker is re-read until the
    # deadline rather than refused on the first look, so a real clock would spend the
    # whole 5s window here proving nothing.
    _repo, _target, invalid, journal_id, _original, _mutated = _seed_recovery(tmp_path, "invalid-marker")
    invalid.child_marker.write_text("not-a-pgid", encoding="utf-8")
    invalid_clock = iter((0.0, 1.0, 6.0))
    with monkeypatch.context() as invalid_patch:
        invalid_patch.setattr(mr.time, "monotonic", lambda: next(invalid_clock))
        with pytest.raises(mar.SweepError, match="invalid process group"):
            invalid.attach_child(journal_id, Process(None))

    _repo, _target, changed, _journal_id, _original, _mutated = _seed_recovery(tmp_path, "changed-owner")
    changed.child_marker.write_text("43210", encoding="utf-8")
    with pytest.raises(mar.SweepError, match="ownership changed before child launch"):
        changed.attach_child("another-owner", Process(None))


def test_a_marker_caught_mid_write_is_waited_out_not_called_invalid(tmp_path: Path) -> None:
    """The race that read as a flaky test, from the parent's side.

    The wrapper used to publish its pgid with `write_text` -- create, write, close --
    while the parent waited only for the path to EXIST. On a loaded runner the parent
    could read between create and write, get `""`, and raise "recorded an invalid
    process group". Quality Core hit it once on `1240348b7` and it was indistinguishable
    from a genuinely corrupt marker. The empty file below is exactly that window held
    open; a parent that refuses on first look fails here.
    """

    class Process:
        def poll(self):
            return None

    _repo, _target, recovery, journal_id, _original, _mutated = _seed_recovery(tmp_path, "mid-write")
    recovery.child_marker.write_text("", encoding="utf-8")
    filled: list[int] = []

    original_sleep = mr.time.sleep

    def fill_on_first_sleep(seconds: float) -> None:
        if not filled:
            filled.append(1)
            recovery.child_marker.write_text("43210\n", encoding="utf-8")
        original_sleep(seconds)

    mr.time.sleep = fill_on_first_sleep
    try:
        assert recovery.attach_child(journal_id, Process()) == 43210
    finally:
        mr.time.sleep = original_sleep
    assert filled, "the marker was read before the parent ever waited; the window was not exercised"


def test_the_wrapper_publishes_its_pgid_by_rename(tmp_path: Path) -> None:
    # The writer's side of the same race, run for real: the wrapper is executed with a
    # marker path, and the file it leaves must be complete. Asserting the source text
    # would only prove a spelling, so the wrapper is actually run.
    marker = tmp_path / "child-pgid"
    start = tmp_path / "child-start"
    start.write_text("start\n", encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            mr._CHILD_WRAPPER,
            str(marker),
            str(start),
            str(os.getpid()),
            sys.executable,
            "-c",
            "",
        ],
        check=False, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert int(marker.read_text(encoding="utf-8").strip()) > 1
    # No staging file survives a normal run -- `clear()` rmdir's this directory.
    assert not (tmp_path / "child-pgid.partial").exists()


@pytest.mark.boundary_contract(reason="prove a pre-exec child exits when its parent dies before attachment")
def test_the_wrapper_does_not_outlive_a_parent_that_dies_before_start(tmp_path: Path) -> None:
    marker = tmp_path / "child-pgid"
    start = tmp_path / "child-start"
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            mr._CHILD_WRAPPER,
            str(marker),
            str(start),
            "0",
            sys.executable,
            "-c",
            "raise SystemExit(99)",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=2,
    )
    assert proc.returncode == 0, proc.stderr
    assert marker.is_file()
    assert not start.exists()


def test_pid_activity_handles_permissions_proc_errors_and_zombies(monkeypatch: pytest.MonkeyPatch) -> None:
    def denied(_pid, _signal):
        raise PermissionError

    monkeypatch.setattr(mr.os, "kill", denied)
    assert mr.MutationRecovery._pid_active(123)

    monkeypatch.setattr(mr.os, "kill", lambda *_args: None)

    def unreadable(_self, **_kwargs):
        raise OSError("proc unavailable")

    monkeypatch.setattr(mr.Path, "read_text", unreadable)
    assert mr.MutationRecovery._pid_active(123)
    monkeypatch.setattr(mr.Path, "read_text", lambda _self, **_kwargs: "123 (child) Z 1 1 1")
    assert not mr.MutationRecovery._pid_active(123)
    monkeypatch.setattr(mr.Path, "read_text", lambda _self, **_kwargs: "123 (child) S 1 1 1")
    assert mr.MutationRecovery._pid_active(123)


def test_group_activity_ignores_bad_proc_rows_and_falls_back_to_killpg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BadStat:
        def read_text(self, **_kwargs):
            return "malformed"

    class Proc:
        def __init__(self, _path):
            pass

        def is_dir(self):
            return True

        def glob(self, _pattern):
            return [BadStat()]

    monkeypatch.setattr(mr, "Path", Proc)
    assert not mr.MutationRecovery._group_active(123)

    monkeypatch.setattr(Proc, "is_dir", lambda _self: False)

    def missing(_pgid, _signal):
        raise ProcessLookupError

    monkeypatch.setattr(mr.os, "killpg", missing)
    assert not mr.MutationRecovery._group_active(123)

    def denied(_pgid, _signal):
        raise PermissionError

    monkeypatch.setattr(mr.os, "killpg", denied)
    assert mr.MutationRecovery._group_active(123)
    monkeypatch.setattr(mr.os, "killpg", lambda *_args: None)
    assert mr.MutationRecovery._group_active(123)


def test_owned_process_recovery_refuses_live_owner_bad_marker_and_unsafe_group(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _target, recovery, _journal_id, _original, _mutated = _seed_recovery(tmp_path, "owned-process")
    monkeypatch.setattr(recovery, "_pid_active", lambda _pid: True)
    with pytest.raises(mar.SweepError, match="still active"):
        recovery._stop_owned_processes({"pid": os.getpid() + 10_000})

    recovery.child_marker.write_text("invalid", encoding="utf-8")
    with pytest.raises(mar.SweepError, match="invalid child process-group marker"):
        recovery._stop_owned_processes({"pid": os.getpid()})

    recovery.child_marker.unlink()
    monkeypatch.setattr(recovery, "_group_active", lambda _pgid: True)
    with pytest.raises(mar.SweepError, match="unsafe recovery process group"):
        recovery._stop_owned_processes({"pid": os.getpid(), "child_process_group": os.getpgrp()})


def test_owned_process_recovery_escalates_after_term_and_refuses_a_surviving_group(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _target, recovery, _journal_id, _original, _mutated = _seed_recovery(tmp_path, "escalate")
    monkeypatch.setattr(mr.time, "monotonic", lambda: 0.0)
    monkeypatch.setattr(mr.time, "sleep", lambda _delay: None)
    signals: list[int] = []
    monkeypatch.setattr(mr.os, "killpg", lambda _pgid, signum: signals.append(signum))

    activity = iter((True, True, False, True, True, False, False))
    monkeypatch.setattr(recovery, "_group_active", lambda _pgid: next(activity))
    recovery._stop_owned_processes({"pid": os.getpid(), "child_process_group": 43210})
    assert signals == [signal.SIGTERM, signal.SIGKILL]

    activity = iter((True, False, True, False, True))
    monkeypatch.setattr(recovery, "_group_active", lambda _pgid: next(activity))
    with pytest.raises(mar.SweepError, match="still active"):
        recovery._stop_owned_processes({"pid": os.getpid(), "child_process_group": 43210})


@pytest.mark.parametrize(
    ("name", "update", "message"),
    [
        ("missing-path", lambda payload: payload.pop("path"), "no target path"),
        ("absent-target", lambda payload: payload.update(path="absent.py"), "absent or escapes"),
        ("invalid-bytes", lambda payload: payload.update(original_base64="%%%"), "invalid pristine bytes"),
        ("digest-mismatch", lambda payload: payload.update(original_sha256="0" * 64), "digest does not match"),
    ],
)
def test_recovery_refuses_malformed_or_unowned_records(
    tmp_path: Path, name: str, update, message: str
) -> None:
    _repo, _target, recovery, _journal_id, _original, _mutated = _seed_recovery(tmp_path, name)
    _rewrite_journal(recovery, update)
    with pytest.raises(mar.SweepError, match=message):
        recovery.recover(mar.restore)
    assert recovery.pending


def test_recovery_handles_absence_incomplete_record_and_already_restored_bytes(tmp_path: Path) -> None:
    empty_repo = tmp_path / "empty"
    empty_repo.mkdir()
    empty = mar.MutationRecovery(empty_repo)
    assert empty.recover(mar.restore) == "no interrupted mutation recovery record exists"

    incomplete_repo = tmp_path / "incomplete"
    incomplete_repo.mkdir()
    incomplete = mar.MutationRecovery(incomplete_repo)
    incomplete.state_dir.mkdir(parents=True)
    assert incomplete.recover(mar.restore) == "cleared an incomplete recovery record; no source mutation could remain"
    assert not incomplete.pending

    _repo, target, recovery, _journal_id, original, _mutated = _seed_recovery(tmp_path, "restored")
    payload = recovery._read()
    staged = target.parent / f".{target.name}.charness-write-{payload['pid']}-leftover"
    staged.write_text("stale", encoding="utf-8")
    disposition = recovery.recover(mar.restore)
    assert "already restored" in disposition
    assert target.read_bytes() == original
    assert not staged.exists()
    assert not recovery.pending


def test_stop_process_group_refuses_unsafe_handles_missing_and_escalates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(mar.SweepError, match="unsafe mutated test process group"):
        mr._stop_process_group(os.getpgrp())

    def missing(_pgid, _signal):
        raise ProcessLookupError

    monkeypatch.setattr(mr.os, "killpg", missing)
    mr._stop_process_group(43210)

    signals: list[int] = []
    monkeypatch.setattr(mr.os, "killpg", lambda _pgid, signum: signals.append(signum))
    monkeypatch.setattr(mr.time, "monotonic", lambda: 0.0)
    monkeypatch.setattr(mr.time, "sleep", lambda _delay: None)
    activity = iter((True, False, True))
    monkeypatch.setattr(mr.MutationRecovery, "_group_active", staticmethod(lambda _pgid: next(activity)))
    mr._stop_process_group(43210)
    assert signals == [signal.SIGTERM, signal.SIGKILL]


def test_run_mutation_command_kills_an_unattached_child_after_bad_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Process:
        returncode = None
        killed = False
        waited = False

        def poll(self):
            return None

        def kill(self):
            self.killed = True

        def wait(self):
            self.waited = True

    _repo, _target, recovery, journal_id, _original, _mutated = _seed_recovery(tmp_path, "bad-child")
    process = Process()
    monkeypatch.setattr(mr.subprocess, "Popen", lambda *_args, **_kwargs: process)
    recovery.child_marker.write_text("invalid", encoding="utf-8")
    monkeypatch.setattr(recovery, "attach_child", lambda *_args: (_ for _ in ()).throw(RuntimeError("attach failed")))

    with pytest.raises(RuntimeError, match="attach failed"):
        mr.run_mutation_command(["ignored"], tmp_path, recovery, journal_id)
    assert process.killed and process.waited
    assert not recovery.child_marker.exists()


def test_refused_apply_clears_journal_and_recovery_cli_covers_clean_and_error_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "mutant"
    repo.mkdir()
    target = repo / "subject.py"
    target.write_text("value = 1\n", encoding="utf-8")
    baseline = mar.Baseline(returncode=0, passed=1, output="1 passed")
    monkeypatch.setattr(mar, "apply_mutation", lambda *_args: (_ for _ in ()).throw(mar.SweepError("refused apply")))

    result = mar.run_mutant(
        {"id": "refused", "path": "subject.py", "find": "1", "replace": "2"},
        ["ignored"],
        repo,
        baseline,
    )
    assert result.verdict == mar.REFUSED
    assert not mar.MutationRecovery(repo).pending

    monkeypatch.setattr(sys, "argv", ["mutate_and_restore.py", "--repo-root", str(repo), "--check-recovery"])
    assert mar.main() == 0
    assert "no interrupted mutation recovery is pending" in capsys.readouterr().out

    class FailedRecovery:
        pending = False

        def __init__(self, _repo_root):
            pass

        def recover(self, _restore):
            raise mar.SweepError("cannot recover")

    monkeypatch.setattr(mar, "MutationRecovery", FailedRecovery)
    monkeypatch.setattr(sys, "argv", ["mutate_and_restore.py", "--repo-root", str(repo), "--recover"])
    assert mar.main() == 2
    assert "cannot recover" in capsys.readouterr().err


def test_commit_and_quality_consumers_refuse_pending_recovery_then_unblock(tmp_path: Path) -> None:
    quality_repo = tmp_path / "quality-consumer"
    (quality_repo / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "run-quality.sh", quality_repo / "scripts" / "run-quality.sh")
    shutil.copy2(
        ROOT / "scripts" / "exported-copy-guard.sh",
        quality_repo / "scripts" / "exported-copy-guard.sh",
    )
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
    # Both hook-invoked gates are stubbed clean: this test's subject is the
    # mutation-recovery arm, and neither gate's own behavior is under test here.
    # They stay UNGUARDED in the hook itself -- a `[[ -f ]]` around a refusal gate
    # is a disarm vector, so the absent-script case is a stub here rather than a
    # skip there.
    for gate in ("check_git_identity.py", "check_staged_router_change.py"):
        (commit_repo / "scripts" / gate).write_text("raise SystemExit(0)\n", encoding="utf-8")
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
