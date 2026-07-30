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


def test_publish_release_refuses_a_critique_for_a_different_release(tmp_path: Path) -> None:
    """The closeout contract recorded release version-binding as an open
    follow-up: the publish gate called the same presence-only `check()`, so any
    tracked critique under the artifact prefix satisfied it — including one
    written for an entirely different release.
    """
    artifact = tmp_path / "charness-artifacts" / "critique" / "v1-4-0-release-packet.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Release critique\n\nRelease: 1.4.0\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        _preflight.enforce_release_critique_gate(
            tmp_path,
            critique_artifact="charness-artifacts/critique/v1-4-0-release-packet.md",
            critique_blocked=None,
            target_version="2.12.0",
        )
    message = _raise_message(excinfo)
    assert "release publish gate refused" in message
    assert "unbound_evidence" in message

    # Control: the critique for the release actually being published passes.
    result = _preflight.enforce_release_critique_gate(
        tmp_path,
        critique_artifact="charness-artifacts/critique/v1-4-0-release-packet.md",
        critique_blocked=None,
        target_version="1.4.0",
    )
    assert result["ok"] is True
    assert result["binding_checked"] is True


def test_release_binding_tokens_accept_both_spellings_the_repo_writes() -> None:
    """Dotted is what the manifest and release notes carry; hyphenated is what the
    checked-in critique BASENAMES use (`v2-1-6-release-candidate-packet.md`).
    Binding on one form only would refuse artifacts this repo already writes,
    which is how a correctness gate earns a bypass."""
    assert _preflight.release_binding_tokens("2.12.0") == ["2-12-0", "2.12.0"]
    assert _preflight.release_binding_tokens("v2.12.0") == ["2-12-0", "2.12.0"]
    # No version resolved means presence-only, not a refusal: a version lookup
    # that failed is not evidence that the critique is wrong.
    assert _preflight.release_binding_tokens(None) == []
    assert _preflight.release_binding_tokens("  ") == []
