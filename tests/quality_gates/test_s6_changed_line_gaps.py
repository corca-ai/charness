"""Cover the changed lines S6's unobtained changed-line proof left unproven.

S6 shipped with its changed-line mutation proof UNOBTAINED — the run was killed
at 25 minutes as dominated, not completed. S6b-1 made that proof affordable, and
running it over `e12b41b5..68d63907` returned BLOCKING: twelve changed lines
across five files were executed by no test. Every one of them is an error,
refusal, or CLI-plumbing branch — the kind that is written to handle the bad day
and never exercised until the bad day.

These are the tests that verdict bought. Each targets a specific reported line;
where a branch cannot be reached without faking the failure, the fake is the
narrowest one that reaches it.
"""

from __future__ import annotations

import signal
import sys
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

from .support import ROOT

_ANCHOR = str(ROOT / "scripts/x.py")


def test_a_ratchet_row_with_a_non_integer_bar_refuses_the_whole_record(tmp_path: Path) -> None:
    """`check_docs_graph.ratchet_rows` — the `except ValueError` arm.

    The comment beside it says the WHOLE record is refused rather than the row
    skipped, because a skipped row is a missing history entry and monotonicity
    cannot be checked against a subset. Nothing asserted it."""
    gate = import_repo_module(_ANCHOR, "scripts.gates.check_docs_graph")
    record = tmp_path / gate.RATCHET_RECORD_PATH
    record.parent.mkdir(parents=True, exist_ok=True)
    header = f"{gate.RATCHET_SECTION_HEADING}\n\n| Date | Bar |\n| --- | --- |\n"
    # The undated row exercises the SHAPE filter beside it: rows are selected by
    # looking like a dated bar row, so surrounding prose in the same table is
    # skipped rather than making the record unreadable.
    record.write_text(
        header + "| note | see below |\n| 2026-08-01 | 200 |\n| 2026-08-02 | 167 |\n",
        encoding="utf-8",
    )

    assert gate.ratchet_rows(tmp_path) == [("2026-08-01", 200), ("2026-08-02", 167)]

    record.write_text(header + "| 2026-08-01 | 200 |\n| 2026-08-02 | many |\n", encoding="utf-8")

    assert gate.ratchet_rows(tmp_path) == [], (
        "one unreadable bar must refuse the record, not silently drop that row"
    )


def test_a_signal_handler_that_cannot_be_installed_is_reported_not_swallowed(capsys) -> None:
    """`standing_pytest_run_record._terminate_reaps_the_child` — the install-failure arm.

    Its own docstring says a swallowed install is REPORTED, "not silent", because
    off the main thread the tolerated outcome IS the orphaned-tree behaviour the
    handler exists to remove. That sentence had no test."""
    record = import_repo_module(_ANCHOR, "scripts.gates_support.standing_pytest_run_record")
    real_signal = signal.signal

    def refuse(_number, _handler):
        raise ValueError("signal only works in main thread")

    signal.signal = refuse
    try:
        with record._terminate_reaps_the_child():
            pass
    finally:
        signal.signal = real_signal

    stderr = capsys.readouterr().err
    assert "could not install" in stderr
    assert "orphan" in stderr, "the operator must be told which outcome they got"


def test_restoring_a_non_python_previous_handler_is_skipped_rather_than_passed_back() -> None:
    """Same module — the `handler is None: continue` arm.

    `signal.signal` returns None when the previous handler was not installed from
    Python; passing None back raises TypeError, which on the interrupt path would
    unwind INSTEAD of the KeyboardInterrupt and replace the real cause."""
    record = import_repo_module(_ANCHOR, "scripts.gates_support.standing_pytest_run_record")
    real_signal = signal.signal
    restored: list[object] = []

    def fake(_number, handler):
        restored.append(handler)
        return None  # previous handler was not installed from Python

    signal.signal = fake
    try:
        with record._terminate_reaps_the_child():
            pass
    finally:
        signal.signal = real_signal

    assert None not in restored, "a None previous handler must never be passed back"


def test_a_failing_restore_does_not_escape_the_context_manager() -> None:
    """Same module — the `except (ValueError, OSError, TypeError): pass` arm.

    The restore runs in a `finally`; an exception raised there would replace
    whatever the body was already unwinding with."""
    record = import_repo_module(_ANCHOR, "scripts.gates_support.standing_pytest_run_record")
    real_signal = signal.signal
    calls: list[int] = []

    def fake(number, handler):
        calls.append(number)
        if handler is not None and not callable(handler):
            raise OSError("cannot restore")
        if len(calls) > len(set(calls)):  # restore pass
            raise OSError("cannot restore")
        return real_signal  # a truthy, non-None "previous handler"

    signal.signal = fake
    try:
        with record._terminate_reaps_the_child():
            pass
    finally:
        signal.signal = real_signal

    assert len(calls) > len(set(calls)), "the restore pass must have been attempted"


def test_git_output_returns_none_when_git_cannot_be_run(tmp_path: Path, monkeypatch) -> None:
    """`worktree_doctor_checks._git_output` — the
    `(FileNotFoundError, TimeoutExpired, NotADirectoryError)` arm. A doctor that
    raises instead of reporting `None` turns a missing git into a crash."""
    checks = import_repo_module(_ANCHOR, "scripts.worktree.worktree_doctor_checks")

    def explode(*_args, **_kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(checks, "run_process", explode)

    assert checks._git_output(tmp_path, "rev-parse", "--git-dir") is None


def test_worktree_doctor_main_runs_and_its_require_isolation_flag_parses(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """`worktree_doctor.main` — the `--require-isolation` argument and the
    `run_doctor` call. The flag is the mechanism the release contract names for
    handing a write-capable agent a checkout; nothing executed `main` at all."""
    doctor = import_repo_module(_ANCHOR, "scripts.worktree.worktree_doctor")
    seen: dict[str, object] = {}

    def fake_run_doctor(repo_root, *, require_isolation):
        seen.update(repo_root=repo_root, require_isolation=require_isolation)
        return {"status": doctor.PASS}

    monkeypatch.setattr(doctor, "run_doctor", fake_run_doctor)
    monkeypatch.setattr(sys, "argv", ["worktree_doctor", "--repo-root", str(tmp_path)])

    assert doctor.main() == 0
    assert seen["require_isolation"] is False
    assert Path(seen["repo_root"]) == tmp_path
    assert capsys.readouterr().out.strip(), "the doctor must emit its payload"

    monkeypatch.setattr(
        sys, "argv", ["worktree_doctor", "--repo-root", str(tmp_path), "--require-isolation"]
    )
    monkeypatch.setattr(
        doctor,
        "run_doctor",
        lambda repo_root, *, require_isolation: (
            seen.update(require_isolation=require_isolation) or {"status": "fail"}
        ),
    )

    assert doctor.main() == 1, "a non-PASS payload must exit non-zero"
    assert seen["require_isolation"] is True


def test_the_gate_cli_module_puts_the_repo_root_on_the_path_when_absent(monkeypatch) -> None:
    """`changed_line_gate_cli` — the `sys.path.insert` bootstrap.

    Only reached on DIRECT invocation, where the repo root is not already on the
    path; every test import has it there already. Executed here by importing the
    module from a stripped path, which is the direct-invocation case."""
    import importlib.util

    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != str(ROOT)])
    assert str(ROOT) not in sys.path, "the direct-invocation case is a path WITHOUT the root"

    # `exec_module` runs the module body itself, which is the only way to reach a
    # top-level bootstrap line: an ordinary import from the test process finds the
    # root already on the path and skips it. The body's own `from scripts...`
    # import then only resolves BECAUSE line 19 ran.
    spec = importlib.util.spec_from_file_location(
        "changed_line_gate_cli_direct_invocation_probe",
        ROOT / "scripts/gates_support/changed_line_gate_cli.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert str(module.REPO_ROOT) in sys.path
    assert callable(module.parse_args)


@pytest.mark.parametrize("module_name", ["scripts.worktree.worktree_doctor_checks"])
def test_subprocess_is_reachable_for_the_arms_above(module_name: str) -> None:
    """Guards the fake seam: the module must bind the shared process primitive."""
    module = import_repo_module(_ANCHOR, module_name)
    assert callable(module.run_process)
