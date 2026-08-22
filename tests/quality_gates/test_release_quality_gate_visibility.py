"""The pre-push quality gate is the longest child in a publish, so it must be observable.

`run_pre_push_quality_gates` used to run the repo's standing quality runner through
`run_shell` — `capture_output=True` bounded at 1800s. That runner streams its own
per-check lifecycle, and buffering it produced a silence an operator could not tell
apart from a hang, at the exact moment they are deciding whether to abort a publish.

These pin the two halves of the repair: the release lane picks the MONITORED shape
for that one call, and the monitored shape keeps `run_shell`'s refusal contract so
nothing downstream had to learn a new failure path.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_script_loading import load_release_script

_COMMON = load_release_script("publish_release_common")
_HELPERS = load_release_script("publish_release_helpers")


def _recording_cli(calls: list[tuple[str, str]]) -> SimpleNamespace:
    def run_shell(command, *, cwd, check=True):
        calls.append(("run_shell", command))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def run_phase(command, *, cwd, phase, check=True):
        calls.append((f"run_phase:{phase}", command))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    return SimpleNamespace(
        run_requested_review_gate=lambda _repo_root: {"status": "ok"},
        run_cli_skill_surface_gate=lambda _repo_root, _adapter: None,
        run_shell=run_shell,
        run_phase=run_phase,
    )


def test_pre_push_quality_gate_runs_as_a_monitored_phase(tmp_path: Path) -> None:
    calls: list[tuple[str, str]] = []
    payload: dict[str, object] = {}

    _COMMON.run_pre_push_quality_gates(
        tmp_path,
        {"quality_command": "./scripts/run-quality.sh"},
        payload,
        cli=_recording_cli(calls),
        # `stage` is REQUIRED, deliberately: it was a hardcoded
        # `post-bump, pre-commit` literal that is false on the resume/claims
        # lane, and a default would let a new lane inherit a wrong stage
        # silently. A caller must say what is true.
        stage="post-bump, pre-commit",
    )

    assert ("run_phase:quality_command", "./scripts/run-quality.sh") in calls
    assert not [call for call in calls if call[0] == "run_shell"], (
        "the quality runner must not go back through the buffered shape; "
        f"observed calls: {calls}"
    )
    assert payload["requested_review_gate"] == {"status": "ok"}


def test_run_phase_streams_lifecycle_and_still_returns_the_isolated_body(tmp_path: Path, capsys) -> None:
    result = _HELPERS.run_phase(
        "printf 'gate output\\n'",
        cwd=tmp_path,
        phase="quality_command",
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "gate output"
    events = capsys.readouterr().err
    assert "RUN [quality_command] " in events
    assert "PASS [quality_command] " in events


def test_run_phase_keeps_the_run_shell_refusal_contract(tmp_path: Path, capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        _HELPERS.run_phase(
            "printf 'partial\\n'; printf 'why\\n' >&2; exit 7",
            cwd=tmp_path,
            phase="quality_command",
        )

    message = str(excinfo.value)
    assert "command failed: printf 'partial\\n'" in message
    assert "exit_code: 7" in message
    # The isolated body is REPLAYED on failure — that is what makes buffering it
    # acceptable in the first place.
    assert "STDOUT:\npartial" in message
    assert "STDERR:\nwhy" in message
    assert "FAIL [quality_command] " in capsys.readouterr().err


def test_run_phase_actually_beats_while_the_gate_runs(monkeypatch, tmp_path: Path, capsys) -> None:
    """The REGRESSION itself, not just the shape selection.

    Every other test here uses an instantaneous child, so with the 30s default no
    heartbeat ever fires — deleting the `heartbeat_seconds` wiring on
    `publish_release_helpers.run_phase` would leave them all green while the
    operator got `RUN`, thirty minutes of nothing, `PASS`.
    """
    monkeypatch.setenv(_HELPERS.PROGRESS_INTERVAL_ENV, "0.1")

    result = _HELPERS.run_phase("sleep 0.5", cwd=tmp_path, phase="quality_command")

    assert result.returncode == 0
    events = capsys.readouterr().err
    assert events.count("HEARTBEAT [quality_command] elapsed=") >= 2, events


def test_run_phase_can_defer_the_refusal_to_its_caller(tmp_path: Path) -> None:
    result = _HELPERS.run_phase("exit 4", cwd=tmp_path, phase="advisory", check=False)

    assert result.returncode == 4


def test_run_shell_keeps_its_own_refusal_after_delegating_the_capture(tmp_path: Path) -> None:
    """The quiet shape's refusal is the same contract, rendered from the raw string.

    `run` renders `" ".join(command)`; `run_shell` renders the command verbatim. Both
    now route through one `_refuse`, so the rendering is the part that can silently
    drift.
    """
    with pytest.raises(SystemExit) as excinfo:
        _HELPERS.run_shell("printf 'quiet\\n' >&2; exit 9", cwd=tmp_path)

    message = str(excinfo.value)
    assert message.startswith("command failed: printf 'quiet\\n' >&2; exit 9")
    assert "exit_code: 9" in message
    assert "STDERR:\nquiet" in message
