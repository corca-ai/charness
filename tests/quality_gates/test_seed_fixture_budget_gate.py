from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

SCRIPT = ROOT / "scripts" / "check_seed_fixture_budget.py"
SCAN_LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "pytest_temp_scan_lib.py"


def _gate() -> ModuleType:
    return load_script_module("check_seed_fixture_budget_for_test", SCRIPT)


def _lib() -> ModuleType:
    return load_script_module("pytest_temp_scan_lib_for_seed_gate_test", SCAN_LIB)


def _run(monkeypatch, footprint: dict[str, object], *args: str) -> SimpleNamespace:
    module = _gate()
    monkeypatch.setattr(
        module,
        "_load_inventory",
        lambda: SimpleNamespace(_pytest_temp_footprint_quick=lambda: footprint),
    )
    return run_loaded_script_main(
        "check_seed_fixture_budget.py",
        module,
        "--repo-root",
        str(ROOT),
        *args,
    )


def test_scan_failure_blocks_instead_of_passing_silently(monkeypatch) -> None:
    """The fail-open bug: a scan that measured nothing must not report success.

    A permanently broken `du` returns `unavailable` on every run. While that
    classified as advisory the gate passed forever without ever checking a byte.
    """
    result = _run(
        monkeypatch,
        {
            "status": "unavailable",
            "root": "/tmp/pytest-of-someone",
            "reason": "du_exit_nonzero",
            "attempts": 3,
            "capability_gap": False,
        },
    )
    assert result.returncode == 1
    assert "blocking_pytest_temp_scan_failed" in result.stderr
    assert "du_exit_nonzero" in result.stderr
    assert "remediation" in result.stderr


def test_scan_failure_blocks_in_json_mode_too(monkeypatch) -> None:
    result = _run(
        monkeypatch,
        {
            "status": "unavailable",
            "root": "/tmp/pytest-of-someone",
            "reason": "du_timeout",
            "attempts": 3,
            "capability_gap": False,
        },
        "--json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["scope_classification"] == "blocking_pytest_temp_scan_failed"
    assert payload["pytest_temp_scan_reason"] == "du_timeout"
    assert payload["pytest_temp_scan_attempts"] == 3
    assert payload["total_disk_bytes"] is None


def test_scan_failure_can_be_waived_without_disabling_every_gate(monkeypatch) -> None:
    """The only alternative escape hatch is `git push --no-verify`, which turns off
    all 82 gates to get past this one."""
    footprint = {
        "status": "unavailable",
        "root": "/tmp/pytest-of-someone",
        "reason": "du_exit_nonzero",
        "attempts": 3,
        "capability_gap": False,
    }
    result = _run(monkeypatch, footprint, "--advisory-on-scan-failure")
    assert result.returncode == 0
    assert "advisory_only_scan_failure_waived" in result.stdout
    assert "proves nothing" in result.stdout


@pytest.mark.parametrize(
    "reason",
    ["du_missing", "du_not_executable", "du_unsupported_options"],
)
def test_capability_gaps_stay_advisory(monkeypatch, reason: str) -> None:
    """A `du` that is absent, unrunnable, or too old to accept `-B` is something the
    box cannot do, not a measurement that broke. Blocking a push on it would wedge
    every BusyBox/BSD container the harness is supposed to be portable to."""
    result = _run(
        monkeypatch,
        {
            "status": "unavailable",
            "root": "/tmp/pytest-of-someone",
            "reason": reason,
            "attempts": 1,
            "capability_gap": True,
        },
    )
    assert result.returncode == 0
    assert "advisory_only_du_unavailable" in result.stdout
    assert reason in result.stdout


def test_missing_temp_root_stays_advisory(monkeypatch) -> None:
    result = _run(monkeypatch, {"status": "missing", "root": "/tmp/pytest-of-someone"})
    assert result.returncode == 0
    assert "advisory_only_no_pytest_temp_yet" in result.stdout


def test_within_budget_passes(monkeypatch) -> None:
    result = _run(
        monkeypatch,
        {
            "status": "available",
            "root": "/tmp/pytest-of-someone",
            "total_disk_bytes": 1024,
            "seed_totals": {"charness-repo-seed": {"count": 2, "disk_bytes": 512}},
        },
    )
    assert result.returncode == 0
    assert "Seed fixture budget within limits" in result.stdout


def test_exactly_at_budget_is_within_budget(monkeypatch) -> None:
    """The comparison is `>`, not `>=`. A repo parked exactly on its configured
    budget must not start blocking pushes."""
    result = _run(
        monkeypatch,
        {
            "status": "available",
            "root": "/tmp/pytest-of-someone",
            "total_disk_bytes": 1024,
            "seed_totals": {"charness-repo-seed": {"count": 1, "disk_bytes": 512}},
        },
        "--total-budget-bytes",
        "1024",
        "--per-seed-budget-bytes",
        "512",
    )
    assert result.returncode == 0
    assert "within limits" in result.stdout


def test_total_and_per_seed_breaches_are_reported(monkeypatch) -> None:
    result = _run(
        monkeypatch,
        {
            "status": "available",
            "root": "/tmp/pytest-of-someone",
            "total_disk_bytes": 4096,
            "seed_totals": {"charness-repo-seed": {"count": 3, "disk_bytes": 4096}},
        },
        "--total-budget-bytes",
        "1024",
        "--per-seed-budget-bytes",
        "512",
    )
    assert result.returncode == 1
    assert "total: 4.00 KiB > 1.00 KiB" in result.stderr
    assert "per-seed `charness-repo-seed`" in result.stderr
    assert "session_count=3" in result.stderr


def test_breaches_exit_nonzero_in_json_mode(monkeypatch) -> None:
    result = _run(
        monkeypatch,
        {
            "status": "available",
            "root": "/tmp/pytest-of-someone",
            "total_disk_bytes": 4096,
            "seed_totals": {},
        },
        "--json",
        "--total-budget-bytes",
        "1024",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["breaches"][0]["type"] == "total_budget_exceeded"


class _Scripted:
    """Stand-in for subprocess.run that replays a fixed list of outcomes."""

    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        outcome = self.outcomes[min(self.calls - 1, len(self.outcomes) - 1)]
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _completed(stdout: str, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["du"], returncode=returncode, stdout=stdout, stderr=stderr)


def _stub_root(monkeypatch, lib: ModuleType, root: Path, scripted: _Scripted) -> None:
    monkeypatch.setattr(lib, "pytest_temp_root", lambda: root)
    monkeypatch.setattr(lib, "PYTEST_TEMP_SCAN_RETRY_SECONDS", 0)
    # Scope the stub to the module under test rather than mutating the global
    # `subprocess` module: `lib.subprocess` IS the shared stdlib object, so
    # patching through it swaps `subprocess.run` for every thread in the process
    # for the duration of the test.
    monkeypatch.setattr(lib, "subprocess", SimpleNamespace(**{**_subprocess_namespace(), "run": scripted}))


def _subprocess_namespace() -> dict[str, object]:
    return {
        "CompletedProcess": subprocess.CompletedProcess,
        "CalledProcessError": subprocess.CalledProcessError,
        "TimeoutExpired": subprocess.TimeoutExpired,
        "SubprocessError": subprocess.SubprocessError,
    }


def _du_output(root: Path, *, include_root_total: bool) -> str:
    lines = [f"512\t{root / 'pytest-1' / 'charness-repo-seed0'}"]
    if include_root_total:
        lines.append(f"2048\t{root}")
    return "\n".join(lines) + "\n"


def test_quick_scan_accepts_a_walk_that_lost_a_file_but_still_totalled(
    monkeypatch, tmp_path: Path
) -> None:
    """`du` exits 1 merely because an entry vanished under it, yet it keeps walking
    and still prints the root total. Treating that nonzero status as a failed
    measurement is what would block every push made while a second pytest run is
    tearing its temp tree down."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    (root / "pytest-1" / "charness-repo-seed0").mkdir(parents=True)
    scripted = _Scripted(
        [_completed(_du_output(root, include_root_total=True), returncode=1, stderr="du: cannot access ...")]
    )
    _stub_root(monkeypatch, lib, root, scripted)

    footprint = lib.pytest_temp_footprint_quick()

    assert scripted.calls == 1
    assert footprint["status"] == "available"
    assert footprint["total_disk_bytes"] == 2048
    assert footprint["session_count"] == 1
    assert footprint["seed_totals"]["charness-repo-seed"] == {"count": 1, "disk_bytes": 512}
    assert footprint["partial"] is True


def test_quick_scan_retries_a_walk_that_died_before_totalling(monkeypatch, tmp_path: Path) -> None:
    """No root total means `du` died early and there is nothing to grade."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    (root / "pytest-1" / "charness-repo-seed0").mkdir(parents=True)
    scripted = _Scripted(
        [
            _completed(_du_output(root, include_root_total=False), returncode=1),
            _completed(_du_output(root, include_root_total=True)),
        ]
    )
    _stub_root(monkeypatch, lib, root, scripted)

    footprint = lib.pytest_temp_footprint_quick()

    assert scripted.calls == 2
    assert footprint["status"] == "available"
    assert footprint["attempts"] == 2
    assert footprint["partial"] is False


def test_quick_scan_records_attempts_on_a_first_try_success(monkeypatch, tmp_path: Path) -> None:
    """A retry that silently succeeded would otherwise leave no trace that the scan
    is flaky on this box."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    (root / "pytest-1" / "charness-repo-seed0").mkdir(parents=True)
    scripted = _Scripted([_completed(_du_output(root, include_root_total=True))])
    _stub_root(monkeypatch, lib, root, scripted)

    assert lib.pytest_temp_footprint_quick()["attempts"] == 1


def test_quick_scan_gives_up_after_the_attempt_budget(monkeypatch, tmp_path: Path) -> None:
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    root.mkdir(parents=True)
    scripted = _Scripted([_completed("", returncode=1)])
    _stub_root(monkeypatch, lib, root, scripted)

    footprint = lib.pytest_temp_footprint_quick()

    assert scripted.calls == lib.PYTEST_TEMP_SCAN_ATTEMPTS
    assert footprint == {
        "status": "unavailable",
        "root": str(root),
        "reason": "du_exit_nonzero",
        "attempts": lib.PYTEST_TEMP_SCAN_ATTEMPTS,
        "capability_gap": False,
    }


def test_quick_scan_sleeps_only_between_attempts(monkeypatch, tmp_path: Path) -> None:
    """One sleep per gap, not per attempt: a trailing sleep is pure dead wall time
    on the failure path of every pre-push run."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    root.mkdir(parents=True)
    scripted = _Scripted([_completed("", returncode=1)])
    _stub_root(monkeypatch, lib, root, scripted)
    sleeps: list[float] = []
    monkeypatch.setattr(lib, "time", SimpleNamespace(monotonic=time.monotonic, sleep=sleeps.append))

    lib.pytest_temp_footprint_quick()

    assert len(sleeps) == lib.PYTEST_TEMP_SCAN_ATTEMPTS - 1


def test_quick_scan_caps_total_time_across_attempts(monkeypatch, tmp_path: Path) -> None:
    """Retrying must not multiply the gate's worst case by the attempt count; the
    per-gate runtime budget measures the total, not one attempt."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    root.mkdir(parents=True)
    timeouts: list[float] = []

    def slow_du(*_args, **kwargs):
        timeouts.append(kwargs["timeout"])
        raise subprocess.TimeoutExpired(["du"], kwargs["timeout"])

    _stub_root(monkeypatch, lib, root, slow_du)
    clock = iter([0.0, 0.0, 25.0, 31.0])
    monkeypatch.setattr(lib, "time", SimpleNamespace(monotonic=lambda: next(clock), sleep=lambda _s: None))

    footprint = lib.pytest_temp_footprint_quick(total_timeout=30.0)

    assert timeouts == [30.0, 5.0]
    assert footprint["reason"] == "du_timeout"


@pytest.mark.parametrize(
    ("outcome", "expected", "capability_gap"),
    [
        (FileNotFoundError("du"), "du_missing", True),
        (PermissionError("nope"), "du_not_executable", True),
        (_completed("", returncode=1, stderr="du: unrecognized option '-B'"), "du_unsupported_options", True),
        (_completed("", returncode=1, stderr="BusyBox\nUsage: du [-aHLdclsxhmk]"), "du_unsupported_options", True),
        (subprocess.TimeoutExpired(["du"], 30), "du_timeout", False),
        (OSError("odd"), "du_oserror", False),
        (subprocess.SubprocessError("odd"), "du_subprocess_error", False),
    ],
    ids=["missing", "not-executable", "gnu-bad-option", "busybox-usage", "timeout", "oserror", "subprocess"],
)
def test_quick_scan_names_each_failure_mode(
    monkeypatch, tmp_path: Path, outcome: object, expected: str, capability_gap: bool
) -> None:
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    root.mkdir(parents=True)
    scripted = _Scripted([outcome])
    _stub_root(monkeypatch, lib, root, scripted)

    footprint = lib.pytest_temp_footprint_quick()

    assert footprint["reason"] == expected
    assert footprint["capability_gap"] is capability_gap
    # A capability gap is identical on every retry; spending attempts on it is waste.
    assert scripted.calls == (1 if capability_gap else lib.PYTEST_TEMP_SCAN_ATTEMPTS)


def test_quick_scan_degrades_to_one_attempt_rather_than_looping_forever(
    monkeypatch, tmp_path: Path
) -> None:
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    root.mkdir(parents=True)
    scripted = _Scripted([_completed("", returncode=1)])
    _stub_root(monkeypatch, lib, root, scripted)

    assert lib.pytest_temp_footprint_quick(attempts=0)["attempts"] == 1
    assert scripted.calls == 1


def test_quick_scan_reports_a_missing_root_without_running_du(monkeypatch, tmp_path: Path) -> None:
    lib = _lib()
    root = tmp_path / "absent"
    scripted = _Scripted([_completed("")])
    _stub_root(monkeypatch, lib, root, scripted)

    assert lib.pytest_temp_footprint_quick() == {"status": "missing", "root": str(root)}
    assert scripted.calls == 0


def test_quick_scan_ignores_unparsable_and_out_of_root_du_lines(monkeypatch, tmp_path: Path) -> None:
    """`du` writes warnings to stderr, but a symlinked or bind-mounted entry can put
    a path outside the scanned root on stdout; neither may corrupt the totals."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    (root / "pytest-1" / "charness-repo-seed0").mkdir(parents=True)
    stdout = (
        "not-a-size-line\n"
        f"nope\t{root / 'pytest-1'}\n"
        f"999\t{tmp_path / 'elsewhere'}\n"
        f"512\t{root / 'pytest-1' / 'charness-repo-seed0'}\n"
        f"2048\t{root}\n"
    )
    scripted = _Scripted([_completed(stdout)])
    _stub_root(monkeypatch, lib, root, scripted)

    footprint = lib.pytest_temp_footprint_quick()

    assert footprint["total_disk_bytes"] == 2048
    assert footprint["seed_totals"]["charness-repo-seed"] == {"count": 1, "disk_bytes": 512}
