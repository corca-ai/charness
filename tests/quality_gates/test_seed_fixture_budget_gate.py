from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

SCRIPT = ROOT / "scripts" / "gates" / "check_seed_fixture_budget.py"
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


def _payload(result: SimpleNamespace) -> dict:
    """The gate's one output shape: a YAML document on stdout, on every path."""
    return yaml.safe_load(result.stdout)


def test_scan_failure_blocks_instead_of_passing_silently(monkeypatch) -> None:
    """The fail-open bug: a scan that measured nothing must not report success.

    A permanently broken `du` returns `unavailable` on every run. While that
    classified as advisory the gate passed forever without ever checking a byte.

    This half pins the BLOCK and the explanation an operator can act on. The
    `scope_classification` token alone says a state without saying what it means or
    what to do about it, so the folded-in prose is part of the verdict, not decoration.
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
    payload = _payload(result)
    assert payload["scope_classification"] == "blocking_pytest_temp_scan_failed"
    assert "du_exit_nonzero" in payload["detail"]
    assert "proves nothing" in payload["detail"]
    assert "--advisory-on-scan-failure" in payload["remediation"]


def test_scan_failure_payload_names_what_the_scan_did_and_did_not_measure(monkeypatch) -> None:
    """The machine-readable half, on a different failure reason.

    Distinct from the block above: this pins the fields a consumer reads rather than
    the prose an operator reads, and `total_disk_bytes is None` is the load-bearing
    one -- a failed scan that reported `0` would be indistinguishable from an empty
    tree comfortably inside budget.
    """
    result = _run(
        monkeypatch,
        {
            "status": "unavailable",
            "root": "/tmp/pytest-of-someone",
            "reason": "du_timeout",
            "attempts": 3,
            "capability_gap": False,
        },
    )
    assert result.returncode == 1
    payload = _payload(result)
    assert payload["scope_classification"] == "blocking_pytest_temp_scan_failed"
    assert payload["pytest_temp_scan_reason"] == "du_timeout"
    assert payload["pytest_temp_scan_attempts"] == 3
    assert payload["total_disk_bytes"] is None


@pytest.mark.parametrize("reason", ["du_timeout", "du_exit_nonzero"])
def test_scan_failure_on_an_unowned_temp_root_stays_advisory(monkeypatch, reason: str) -> None:
    """Without PYTEST_DEBUG_TEMPROOT the scan walks the shared system temp dir, where
    every other project's pytest tree also lands. Someone else's huge tree blowing the
    timeout is not this repo's verdict to block a push on."""
    result = _run(
        monkeypatch,
        {
            "status": "unavailable",
            "root": "/tmp/pytest-of-someone",
            "root_source": "shared_fallback",
            "reason": reason,
            "attempts": 3,
            "capability_gap": False,
        },
    )
    assert result.returncode == 0
    payload = _payload(result)
    assert payload["scope_classification"] == "advisory_only_unowned_temp_root"
    # The way back to a blocking measurement. Without it the carve-out reads as a
    # permanent exemption rather than as a consequence of an unowned root.
    assert "PYTEST_DEBUG_TEMPROOT" in payload["remediation"]


def test_scan_failure_on_a_repo_scoped_root_still_blocks(monkeypatch) -> None:
    """The unowned-root carve-out must not swallow the fail-open fix: once the repo
    points at its own root, the same failure is the repo's to answer for."""
    result = _run(
        monkeypatch,
        {
            "status": "unavailable",
            "root": "/repo/.charness/pytest-tmp/pytest-of-someone",
            "root_source": "configured",
            "reason": "du_timeout",
            "attempts": 3,
            "capability_gap": False,
        },
    )
    assert result.returncode == 1
    assert _payload(result)["scope_classification"] == "blocking_pytest_temp_scan_failed"


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
    payload = _payload(result)
    assert payload["scope_classification"] == "advisory_only_scan_failure_waived"
    # A waiver that read as a PASS would be worse than the block it replaces, so the
    # payload has to keep saying the run measured nothing.
    assert "proves nothing" in payload["detail"]


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
    payload = _payload(result)
    assert payload["scope_classification"] == "advisory_only_du_unavailable"
    assert payload["pytest_temp_scan_reason"] == reason
    assert reason in payload["detail"]


def test_missing_temp_root_stays_advisory(monkeypatch) -> None:
    result = _run(monkeypatch, {"status": "missing", "root": "/tmp/pytest-of-someone"})
    assert result.returncode == 0
    assert _payload(result)["scope_classification"] == "advisory_only_no_pytest_temp_yet"


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
    payload = _payload(result)
    assert payload["scope_classification"] == "scanned"
    assert payload["breaches"] == []
    assert "Seed fixture budget within limits" in payload["detail"]


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
    payload = _payload(result)
    assert payload["breaches"] == []
    assert "within limits" in payload["detail"]


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
    payload = _payload(result)
    breaches = {breach["type"]: breach for breach in payload["breaches"]}
    assert sorted(breaches) == ["per_seed_budget_exceeded", "total_budget_exceeded"]
    assert breaches["total_budget_exceeded"]["observed_bytes"] == 4096
    assert breaches["total_budget_exceeded"]["budget_bytes"] == 1024
    # The per-seed breach has to name WHICH prefix and how many sessions built it;
    # a bare byte count leaves the operator nothing to delete.
    assert breaches["per_seed_budget_exceeded"]["seed_prefix"] == "charness-repo-seed"
    assert breaches["per_seed_budget_exceeded"]["session_count"] == 3
    assert "charness-repo-seed" in breaches["per_seed_budget_exceeded"]["remediation"]
    assert "2 breach(es)" in payload["detail"]


def test_breaches_exit_nonzero(monkeypatch) -> None:
    """The exit-code half, on a total-only breach.

    Kept distinct from the report above: that one proves the breach payload is
    complete, this one proves a breach still ends the run nonzero. A gate that
    described a breach and exited 0 would let every over-budget push through.
    """
    result = _run(
        monkeypatch,
        {
            "status": "available",
            "root": "/tmp/pytest-of-someone",
            "total_disk_bytes": 4096,
            "seed_totals": {},
        },
        "--total-budget-bytes",
        "1024",
    )
    assert result.returncode == 1
    assert _payload(result)["breaches"][0]["type"] == "total_budget_exceeded"


def _write_lib_stub(root: Path, relative: str) -> Path:
    target = root.joinpath(*relative.split("/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("MARKER = 'loaded'\n", encoding="utf-8")
    return target


@pytest.mark.parametrize(
    "layout",
    [
        "skills/public/quality/scripts/standing_test_economics_lib.py",
        "skills/quality/scripts/standing_test_economics_lib.py",
    ],
    ids=["source-layout", "plugin-export-layout"],
)
def test_load_inventory_resolves_both_layouts(monkeypatch, tmp_path: Path, layout: str) -> None:
    """The plugin export flattens `skills/public/` to `skills/`. Hard-coding the
    source layout left the exported gate dead on arrival with a bare
    FileNotFoundError out of exec_module."""
    module = _gate()
    repo_root = tmp_path / "repo"
    _write_lib_stub(repo_root, layout)
    monkeypatch.setattr(module, "__file__", str(repo_root / "scripts" / "gates" / "check_seed_fixture_budget.py"))

    assert module._load_inventory().MARKER == "loaded"


def test_load_inventory_names_both_layouts_when_neither_exists(monkeypatch, tmp_path: Path) -> None:
    """A bare FileNotFoundError from exec_module does not say what was looked for."""
    module = _gate()
    repo_root = tmp_path / "repo"
    (repo_root / "scripts").mkdir(parents=True)
    monkeypatch.setattr(module, "__file__", str(repo_root / "scripts" / "gates" / "check_seed_fixture_budget.py"))

    with pytest.raises(ImportError) as excinfo:
        module._load_inventory()

    message = str(excinfo.value)
    assert "skills/public/quality/scripts/standing_test_economics_lib.py" in message
    assert "skills/quality/scripts/standing_test_economics_lib.py" in message


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
    # Pin the ownership label. `run-quality.sh` sets PYTEST_DEBUG_TEMPROOT and bare
    # pytest does not, so leaving this to the ambient environment would make these
    # assertions pass under one runner and fail under the other.
    monkeypatch.setattr(lib, "pytest_temp_root_source", lambda: "configured")
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
    """No root total means `du` died early and there is nothing to grade.

    One attempt now spends one spawn per `DU_SCAN_VARIANTS` entry, so an unusable
    walk must fail every variant before the attempt counter advances. Scripting a
    full round of misses keeps this a test of the across-attempts retry rather than
    of the within-attempt variant fallback (covered separately below).
    """
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    (root / "pytest-1" / "charness-repo-seed0").mkdir(parents=True)
    variants = len(lib.DU_SCAN_VARIANTS)
    scripted = _Scripted(
        [_completed(_du_output(root, include_root_total=False), returncode=1)] * variants
        + [_completed(_du_output(root, include_root_total=True))]
    )
    _stub_root(monkeypatch, lib, root, scripted)

    footprint = lib.pytest_temp_footprint_quick()

    assert scripted.calls == variants + 1
    assert footprint["status"] == "available"
    assert footprint["attempts"] == 2
    assert footprint["partial"] is False


def test_quick_scan_falls_back_to_the_portable_unit_within_one_attempt(
    monkeypatch, tmp_path: Path
) -> None:
    """A `du` that rejects `-B1` gets measured by `-k`, in KiB scaled back to bytes.

    Crucially the fallback is driven by "this walk produced no root total", NOT by
    matching stderr against `DU_USAGE_ERROR_TOKENS`: the scripted rejection below
    uses a wording that list does not contain, which is the BSD/macOS case no host
    here can probe.
    """
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    (root / "pytest-1" / "charness-repo-seed0").mkdir(parents=True)
    seen: list[tuple[str, ...]] = []
    kib_output = "\n".join([f"1\t{root / 'pytest-1' / 'charness-repo-seed0'}", f"4\t{root}"]) + "\n"

    def fake_run(command, **kwargs):
        seen.append(tuple(command[1:-1]))
        if "-B1" in command:
            return _completed("", returncode=1, stderr="du: du: option requires an argument -- B")
        return _completed(kib_output)

    _stub_root(monkeypatch, lib, root, fake_run)

    footprint = lib.pytest_temp_footprint_quick()

    assert seen == [("-d", "4", "-B1"), ("-d", "4", "-k")]
    assert footprint["status"] == "available"
    assert footprint["attempts"] == 1
    assert footprint["size_granularity_bytes"] == 1024
    assert footprint["total_disk_bytes"] == 4096
    assert footprint["seed_totals"]["charness-repo-seed"] == {"count": 1, "disk_bytes": 1024}


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

    assert scripted.calls == lib.PYTEST_TEMP_SCAN_ATTEMPTS * len(lib.DU_SCAN_VARIANTS)
    assert footprint == {
        "status": "unavailable",
        "root": str(root),
        "root_source": "configured",
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


# `spawns` is a callable of the lib so each row states its own spend in terms of the
# two constants that govern it -- attempts, and how many option variants exist -- and
# no row silently inherits the wrong one when either changes.
@pytest.mark.parametrize(
    ("outcome", "expected", "capability_gap", "spawns"),
    [
        (FileNotFoundError("du"), "du_missing", True, lambda lib: 1),
        (PermissionError("nope"), "du_not_executable", True, lambda lib: 1),
        (
            _completed("", returncode=1, stderr="du: unrecognized option '-B'"),
            "du_unsupported_options",
            True,
            lambda lib: len(lib.DU_SCAN_VARIANTS),
        ),
        (
            _completed("", returncode=1, stderr="BusyBox\nUsage: du [-aHLdclsxhmk]"),
            "du_unsupported_options",
            True,
            lambda lib: len(lib.DU_SCAN_VARIANTS),
        ),
        (subprocess.TimeoutExpired(["du"], 30), "du_timeout", False, lambda lib: lib.PYTEST_TEMP_SCAN_ATTEMPTS),
        (OSError("odd"), "du_oserror", False, lambda lib: lib.PYTEST_TEMP_SCAN_ATTEMPTS),
        (
            subprocess.SubprocessError("odd"),
            "du_subprocess_error",
            False,
            lambda lib: lib.PYTEST_TEMP_SCAN_ATTEMPTS,
        ),
    ],
    ids=["missing", "not-executable", "gnu-bad-option", "busybox-usage", "timeout", "oserror", "subprocess"],
)
def test_quick_scan_names_each_failure_mode(
    monkeypatch, tmp_path: Path, outcome: object, expected: str, capability_gap: bool, spawns
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
    # An option-rejection gap still costs one spawn per variant, because proving the
    # box cannot do it means having tried the portable form too. A `du` that never
    # ran gets no variant spend at all, and a transient failure keeps its attempts.
    assert scripted.calls == spawns(lib)


def test_quick_scan_degrades_to_one_attempt_rather_than_looping_forever(
    monkeypatch, tmp_path: Path
) -> None:
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    root.mkdir(parents=True)
    scripted = _Scripted([_completed("", returncode=1)])
    _stub_root(monkeypatch, lib, root, scripted)

    assert lib.pytest_temp_footprint_quick(attempts=0)["attempts"] == 1
    assert scripted.calls == len(lib.DU_SCAN_VARIANTS)


def test_quick_scan_reports_a_missing_root_without_running_du(monkeypatch, tmp_path: Path) -> None:
    lib = _lib()
    root = tmp_path / "absent"
    scripted = _Scripted([_completed("")])
    _stub_root(monkeypatch, lib, root, scripted)

    assert lib.pytest_temp_footprint_quick() == {
        "status": "missing",
        "root": str(root),
        "root_source": "configured",
    }
    assert scripted.calls == 0


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [(None, "shared_fallback"), ("/repo/.charness/pytest-tmp", "configured")],
    ids=["unset", "set"],
)
def test_temp_root_source_reports_who_owns_the_scanned_tree(
    monkeypatch, env_value: str | None, expected: str
) -> None:
    lib = _lib()
    if env_value is None:
        monkeypatch.delenv("PYTEST_DEBUG_TEMPROOT", raising=False)
    else:
        monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", env_value)

    assert lib.pytest_temp_root_source() == expected


def _du_accepts_block_size() -> bool:
    """Whether THIS host's `du` accepts `-B`, which is what the scan actually needs.

    `shutil.which("du")` is the wrong predicate: BusyBox ships a `du` that is present
    and rejects `-B`, which is precisely the host the sibling test below exists to
    prove. Probing the capability rather than the name keeps each test skipping on
    the condition it actually depends on.
    """
    if shutil.which("du") is None:
        return False
    try:
        return subprocess.run(
            ["du", "-B1", "-s", "."], capture_output=True, text=True, timeout=30
        ).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


@pytest.mark.skipif(shutil.which("busybox") is None, reason="busybox not installed on this host")
def test_real_busybox_du_is_measured_through_the_portable_fallback(monkeypatch, tmp_path: Path) -> None:
    """Probed, not inferred, and now a measurement rather than a gap.

    BusyBox `du` rejects `-B`, which used to make this whole host advisory-only. The
    `-k` variant is in BusyBox's own usage string (`[-aHLdclsxhmk]`), so the scan
    gets a real -- if KiB-granular -- footprint instead. This drives the production
    scan against the actual `busybox du` by putting it first on PATH, so the claim
    rests on the binary and not on its documentation."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    (root / "pytest-1" / "charness-repo-seed0").mkdir(parents=True)
    shim_dir = tmp_path / "bin"
    shim_dir.mkdir()
    # A symlink, not a shell wrapper: BusyBox dispatches on argv[0], so this needs no
    # interpreter. A `#!/usr/bin/env bash` shim would fail on a busybox-without-bash
    # host -- exactly the minimal image this test targets -- and would surface as a
    # misleading `du_missing` rather than as "no bash".
    os.symlink(shutil.which("busybox"), shim_dir / "du")
    monkeypatch.setenv("PATH", f"{shim_dir}:{os.environ['PATH']}")
    monkeypatch.setattr(lib, "pytest_temp_root", lambda: root)

    footprint = lib.pytest_temp_footprint_quick()

    assert footprint["status"] == "available"
    # The `-B1` rejection is real, so the usable walk came from the `-k` variant.
    assert footprint["size_granularity_bytes"] == 1024
    assert footprint["total_disk_bytes"] > 0
    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1
    # Resolved inside one attempt: the variant fallback is not a retry.
    assert footprint["attempts"] == 1


@pytest.mark.skipif(not _du_accepts_block_size(), reason="this host's du does not accept -B")
@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="chmod 000 does not deny root, so the unreadable-subdir setup cannot hold",
)
def test_real_du_still_totals_after_an_unreadable_subdir(monkeypatch, tmp_path: Path) -> None:
    """The load-bearing premise of this whole design, against the real binary: `du`
    exits nonzero when it cannot read an entry, yet keeps walking and still prints the
    scanned root's own total. If that were false, accepting a nonzero exit would be
    accepting a fabricated number."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    seed = root / "pytest-1" / "charness-repo-seed0"
    seed.mkdir(parents=True)
    (seed / "payload.bin").write_bytes(b"x" * 4096)
    denied = root / "pytest-1" / "denied"
    denied.mkdir()
    (denied / "inner.bin").write_bytes(b"y" * 4096)
    denied.chmod(0o000)
    monkeypatch.setattr(lib, "pytest_temp_root", lambda: root)

    try:
        footprint = lib.pytest_temp_footprint_quick()
    finally:
        denied.chmod(0o755)

    assert footprint["status"] == "available"
    assert footprint["partial"] is True, "a nonzero du exit that still totalled must be marked partial"
    assert footprint["total_disk_bytes"] > 0
    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1


def test_quick_scan_counts_a_nested_seed_dir_only_once(monkeypatch, tmp_path: Path) -> None:
    """`du -d 4` reports a seed dir AND anything seed-named inside it. Counting both
    would double-count the same bytes against the per-seed budget."""
    lib = _lib()
    root = tmp_path / "pytest-of-someone"
    outer = root / "pytest-1" / "charness-repo-seed0"
    outer.mkdir(parents=True)
    stdout = (
        f"4096\t{outer}\n"
        f"1024\t{outer / 'charness-repo-seed-nested'}\n"
        f"8192\t{root}\n"
    )
    scripted = _Scripted([_completed(stdout)])
    _stub_root(monkeypatch, lib, root, scripted)

    footprint = lib.pytest_temp_footprint_quick()

    assert footprint["seed_totals"]["charness-repo-seed"] == {"count": 1, "disk_bytes": 4096}


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
