from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_preflight_module():
    path = ROOT / "skills/public/release/scripts/publish_release_preflight.py"
    spec = importlib.util.spec_from_file_location("publish_release_preflight", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_preflight = _load_preflight_module()


def _raise_message(excinfo: pytest.ExceptionInfo[SystemExit]) -> str:
    return str(excinfo.value)


def test_publish_release_rejects_untracked_critique_artifact(tmp_path: Path) -> None:
    critique_artifact = tmp_path / "charness-artifacts" / "critique" / "demo.md"
    critique_artifact.parent.mkdir(parents=True)
    critique_artifact.write_text("# Demo critique\n", encoding="utf-8")

    def fake_run_command(*_args, **_kwargs):
        return SimpleNamespace(returncode=1)

    with pytest.raises(SystemExit) as excinfo:
        _preflight.validate_critique_artifact_arg(
            tmp_path,
            "charness-artifacts/critique/demo.md",
            run_command=fake_run_command,
        )

    assert "--critique-artifact must be tracked before release" in _raise_message(excinfo)


def test_publish_release_refuses_without_any_critique_flag(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as excinfo:
        _preflight.enforce_release_critique_gate(
            tmp_path,
            critique_artifact=None,
            critique_blocked=None,
        )

    message = _raise_message(excinfo)
    assert "release publish gate refused: standalone critique not satisfied" in message
    assert "standalone_critique" in message


def test_publish_release_refuses_when_blocked_signal_too_terse(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as excinfo:
        _preflight.enforce_release_critique_gate(
            tmp_path,
            critique_artifact=None,
            critique_blocked="host-down",
        )

    assert "release publish gate refused" in _raise_message(excinfo)


def test_publish_release_refuses_both_critique_flags_at_once(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as excinfo:
        _preflight.enforce_release_critique_gate(
            tmp_path,
            critique_artifact="charness-artifacts/critique/demo.md",
            critique_blocked="synthetic-host-signal that is long enough",
        )

    assert "pass exactly one of" in _raise_message(excinfo)
