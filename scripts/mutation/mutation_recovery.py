"""Durable file and process ownership for mutation sweeps.

This module owns the lifecycle boundary that survives the sweep process:
write-ahead pristine bytes, atomic source replacement, a stopped child session
bound into the journal before execution, and explicit recovery after SIGKILL.
It deliberately knows nothing about mutation verdicts or pytest summaries.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import signal
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import run_monitored_phase, run_process  # noqa: E402


class RecoveryError(Exception):
    """A lifecycle refusal the caller must surface rather than guess through."""


class SweepTerminated(BaseException):
    """A trappable termination request that must cross the restoring finally."""

    def __init__(self, signum: int):
        super().__init__(signum)
        self.signum = signum


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def recovery_state_dir(repo_root: Path) -> Path:
    """Keep recovery bytes in git metadata when possible, never in a commit."""
    from scripts.core.git_checkout import discoverable, discovery_redirected, layout_from_files

    layout = layout_from_files(repo_root)
    if layout is not None:
        return layout.git_dir / "charness-mutation-recovery"
    if not discovery_redirected() and not discoverable(repo_root):
        return repo_root / ".charness" / "mutation-recovery"
    try:
        completed = run_process(
            ["git", "rev-parse", "--git-dir"], cwd=repo_root, timeout_seconds=None
        )
    except OSError:
        completed = SimpleNamespace(returncode=1, stdout="", stderr="")
    if completed.returncode == 0 and completed.stdout.strip():
        git_dir = Path(completed.stdout.strip())
        if not git_dir.is_absolute():
            git_dir = repo_root / git_dir
        return git_dir.resolve() / "charness-mutation-recovery"
    return repo_root / ".charness" / "mutation-recovery"


def _fsync_directory(path: Path) -> None:
    directory_fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def atomic_write_bytes(path: Path, content: bytes) -> None:
    """Replace a source file atomically so process death cannot leave half a write."""
    staged = path.with_name(f".{path.name}.charness-write-{os.getpid()}-{uuid.uuid4().hex}")
    mode = path.stat().st_mode & 0o777
    try:
        descriptor = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staged, path)
        _fsync_directory(path.parent)
    finally:
        staged.unlink(missing_ok=True)


class MutationRecovery:
    """Durable ownership record for the one file currently under mutation."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.state_dir = recovery_state_dir(self.repo_root)
        self.journal_path = self.state_dir / "journal.json"
        self.child_marker = self.state_dir / "child-pgid"
        self.child_start = self.state_dir / "child-start"

    @property
    def pending(self) -> bool:
        return self.state_dir.exists()

    def assert_clear(self) -> None:
        if self.pending:
            raise RecoveryError(
                "an interrupted mutation recovery record already exists at "
                f"{self.state_dir}; run this command with --check-recovery, then --recover"
            )

    def begin(self, path: Path, original: bytes, mutated: bytes) -> str:
        """Persist pristine bytes before the first mutation byte reaches disk."""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise RecoveryError(
                "another or interrupted mutation owns the recovery record at "
                f"{self.state_dir}; refuse to overwrite it"
            ) from exc
        journal_id = uuid.uuid4().hex
        payload = {
            "version": 1,
            "id": journal_id,
            "pid": os.getpid(),
            "path": path.relative_to(self.repo_root).as_posix(),
            "original_sha256": _sha256(original),
            "mutated_sha256": _sha256(mutated),
            "original_base64": base64.b64encode(original).decode("ascii"),
        }
        try:
            self._write_payload(payload)
        except BaseException:
            # No mutation can have started until begin() returns.
            for state_file in self.state_dir.iterdir():
                state_file.unlink(missing_ok=True)
            self.state_dir.rmdir()
            raise
        return journal_id

    def _write_payload(self, payload: dict) -> None:
        staged = self.state_dir / f"journal.{os.getpid()}.{uuid.uuid4().hex}.tmp"
        try:
            staged.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
            with staged.open("rb") as handle:
                os.fsync(handle.fileno())
            os.replace(staged, self.journal_path)
            _fsync_directory(self.state_dir)
        finally:
            staged.unlink(missing_ok=True)

    def _read(self) -> dict:
        try:
            payload = json.loads(self.journal_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RecoveryError(
                f"mutation recovery record at {self.journal_path} is unreadable; "
                "refusing to guess whether source bytes are pristine"
            ) from exc
        if payload.get("version") != 1:
            raise RecoveryError(
                f"mutation recovery record at {self.journal_path} has unsupported version "
                f"{payload.get('version')!r}"
            )
        return payload

    def clear(self, journal_id: str) -> None:
        payload = self._read()
        if payload.get("id") != journal_id:
            raise RecoveryError(
                "mutation recovery ownership changed; refusing to clear another sweep's journal"
            )
        self._clear_child_markers()
        self.journal_path.unlink()
        for staged in self.state_dir.glob("journal.*.tmp"):
            staged.unlink(missing_ok=True)
        self.state_dir.rmdir()

    def attach_child(self, journal_id: str, process) -> int:  # noqa: ANN001
        """Bind a stopped child session to the journal before allowing exec."""
        # The wait condition is a READABLE pgid, not a path that exists. Existence alone
        # was the race: the wrapper published the marker with write_text, so the parent
        # could read it empty and turn a timing window into "recorded an invalid process
        # group" -- observed once in CI (Quality Core, 1240348b7) and indistinguishable
        # from a genuinely corrupt marker. The wrapper now renames the marker into place,
        # so an unreadable one here is a real defect; this loop keeps waiting anyway
        # rather than trusting one writer's atomicity, and the deadline still bounds it.
        deadline = time.monotonic() + 5
        process_group: int | None = None
        while time.monotonic() < deadline:
            try:
                process_group = int(self.child_marker.read_text(encoding="utf-8").strip())
                break
            except (OSError, ValueError):
                pass
            if process.poll() is not None:
                raise RecoveryError(
                    "mutated test wrapper exited before recording its process group"
                )
            time.sleep(0.01)
        if process_group is None:
            if self.child_marker.exists():
                raise RecoveryError("mutated test wrapper recorded an invalid process group")
            raise RecoveryError("mutated test wrapper did not record its process group")
        payload = self._read()
        if payload.get("id") != journal_id:
            raise RecoveryError("mutation recovery ownership changed before child launch")
        payload["child_process_group"] = process_group
        self._write_payload(payload)
        self.child_start.write_text("start\n", encoding="utf-8")
        return process_group

    def _clear_child_markers(self) -> None:
        self.child_start.unlink(missing_ok=True)
        self.child_marker.unlink(missing_ok=True)
        # The wrapper's rename staging path. A child killed between write and rename
        # leaves it behind, and `clear()` rmdir's this directory -- a stale sibling
        # turns the teardown into OSError: Directory not empty.
        self.child_marker.with_name(self.child_marker.name + ".partial").unlink(missing_ok=True)

    @staticmethod
    def _pid_active(pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        try:
            state = (
                (Path("/proc") / str(pid) / "stat")
                .read_text(encoding="utf-8")
                .rsplit(")", 1)[1]
                .split()[0]
            )
        except (OSError, IndexError):
            return True
        return state != "Z"

    @staticmethod
    def _group_active(process_group: int) -> bool:
        proc = Path("/proc")
        if proc.is_dir():
            for stat_path in proc.glob("[0-9]*/stat"):
                try:
                    fields = stat_path.read_text(encoding="utf-8").rsplit(")", 1)[1].split()
                    if int(fields[2]) == process_group and fields[0] != "Z":
                        return True
                except (OSError, ValueError, IndexError):
                    continue
            return False
        try:
            os.killpg(process_group, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def _stop_owned_processes(self, payload: dict) -> None:
        owner = payload.get("pid")
        if isinstance(owner, int) and owner != os.getpid() and self._pid_active(owner):
            raise RecoveryError(
                f"mutation sweep pid {owner} is still active; refusing concurrent recovery"
            )
        process_group = payload.get("child_process_group")
        if process_group is None and self.child_marker.exists():
            try:
                process_group = int(self.child_marker.read_text(encoding="utf-8").strip())
            except (OSError, ValueError) as exc:
                raise RecoveryError(
                    "interrupted mutation has an invalid child process-group marker"
                ) from exc
        if not isinstance(process_group, int) or not self._group_active(process_group):
            return
        if process_group <= 1 or process_group == os.getpgrp():
            raise RecoveryError(f"refusing unsafe recovery process group {process_group}")
        os.killpg(process_group, signal.SIGTERM)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and self._group_active(process_group):
            time.sleep(0.02)
        if self._group_active(process_group):
            os.killpg(process_group, signal.SIGKILL)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline and self._group_active(process_group):
                time.sleep(0.02)
        if self._group_active(process_group):
            raise RecoveryError(
                f"mutated test process group {process_group} is still active; recovery remains required"
            )

    def recover(self, restore_bytes: Callable[[Path, bytes], None]) -> str:
        """Restore only exact owned bytes after stopping every owned consumer."""
        if not self.pending:
            return "no interrupted mutation recovery record exists"
        if not self.journal_path.exists():
            self.state_dir.rmdir()
            return "cleared an incomplete recovery record; no source mutation could remain"
        payload = self._read()
        self._stop_owned_processes(payload)
        rel = payload.get("path")
        if not isinstance(rel, str):
            raise RecoveryError("mutation recovery record has no target path")
        path = (self.repo_root / rel).resolve()
        if not path.is_relative_to(self.repo_root) or not path.is_file():
            raise RecoveryError(f"mutation recovery target is absent or escapes the repo: {rel}")
        try:
            original = base64.b64decode(payload["original_base64"], validate=True)
        except (KeyError, ValueError) as exc:
            raise RecoveryError("mutation recovery record has invalid pristine bytes") from exc
        if _sha256(original) != payload.get("original_sha256"):
            raise RecoveryError(
                "mutation recovery record's pristine-byte digest does not match its payload"
            )
        current_sha = _sha256(path.read_bytes())
        if current_sha == payload.get("original_sha256"):
            disposition = f"{rel} was already restored; cleared the stale recovery record"
        elif current_sha == payload.get("mutated_sha256"):
            restore_bytes(path, original)
            disposition = f"restored {rel} from the interrupted mutation recovery record"
        else:
            raise RecoveryError(
                f"{rel} changed after the interrupted mutation; refusing to overwrite bytes "
                "the sweep does not own"
            )
        for staged in path.parent.glob(f".{path.name}.charness-write-{payload.get('pid')}-*"):
            staged.unlink(missing_ok=True)
        self.clear(str(payload.get("id")))
        return disposition


@contextmanager
def termination_handlers():
    """Route trappable termination through Python's restoring finally."""
    previous: dict[int, object] = {}

    def terminate(signum, _frame):
        signal.signal(signum, signal.SIG_DFL)
        raise SweepTerminated(signum)

    try:
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.getsignal(signum)
            signal.signal(signum, terminate)
        yield
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


_CHILD_WRAPPER = """
import os  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

marker, start, expected_parent, *command = sys.argv[1:]
# Published by rename, not by write_text. The parent polls the marker for EXISTENCE and
# then reads it, so a plain write_text -- create, write, close -- lets the parent win
# between create and write and read an empty file. That is `int("")`, which the parent
# reports as "recorded an invalid process group": a load-dependent race that reads as a
# flaky test. Same-directory rename is atomic, so the path never exists half-written.
staging = Path(marker + ".partial")
staging.write_text(str(os.getpid()) + "\\n", encoding="utf-8")
os.replace(staging, marker)
while not Path(start).exists():
    if os.getppid() != int(expected_parent) or not Path(marker).parent.exists():
        raise SystemExit(0)
    time.sleep(0.01)
os.execvp(command[0], command)
"""


def _stop_process_group(process_group: int) -> None:
    if process_group <= 1 or process_group == os.getpgrp():
        raise RecoveryError(f"refusing unsafe mutated test process group {process_group}")
    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline and MutationRecovery._group_active(process_group):
        time.sleep(0.02)
    if MutationRecovery._group_active(process_group):
        os.killpg(process_group, signal.SIGKILL)


def run_mutation_command(
    command: list[str], cwd: Path, recovery: MutationRecovery, journal_id: str
):
    """Run a mutant in an owned session that recovery can stop before clearing."""
    wrapped = [
        sys.executable,
        "-c",
        _CHILD_WRAPPER,
        str(recovery.child_marker),
        str(recovery.child_start),
        str(os.getpid()),
        *command,
    ]
    outcome: list[object] = []
    worker_error: list[BaseException] = []

    def execute() -> None:
        try:
            outcome.append(
                run_monitored_phase(
                    wrapped,
                    cwd=cwd,
                    phase="mutated-test",
                    timeout_seconds=None,
                    capture=True,
                )
            )
        except BaseException as exc:  # pragma: no cover - guard setup failure
            worker_error.append(exc)

    worker = threading.Thread(target=execute, name="charness-mutated-test")
    worker.start()

    class _WorkerProcess:
        def poll(self):  # noqa: ANN201
            return None if worker.is_alive() else 0

    process = _WorkerProcess()
    process_group: int | None = None
    try:
        process_group = recovery.attach_child(journal_id, process)
        worker.join()
        if worker_error:
            raise worker_error[0]
        if not outcome:
            raise RecoveryError("mutated test guard exited without a result")
        return outcome[0].completed_process()
    except BaseException:
        if process_group is None and recovery.child_marker.exists():
            try:
                process_group = int(recovery.child_marker.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                process_group = None
        if process_group is not None:
            _stop_process_group(process_group)
        worker.join()
        raise
    finally:
        recovery._clear_child_markers()
