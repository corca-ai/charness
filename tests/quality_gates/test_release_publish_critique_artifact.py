from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]


def _load_preflight_module():
    path = ROOT / "skills/public/release/scripts/publish_release_preflight.py"
    return load_module("publish_release_preflight", path)


def _load_plan_module():
    path = ROOT / "skills/public/release/scripts/publish_release_plan.py"
    return load_module("publish_release_plan", path)


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


def test_an_unresolvable_version_degrades_to_presence_only_and_says_so(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The fail-open at the publish boundary must be audible and auditable.

    When the target version cannot be read the gate accepts the critique on
    PRESENCE alone — the pre-binding behavior — rather than refusing, because a
    version lookup that failed is not evidence that the critique is wrong. But
    that is a silent downgrade at an irreversible boundary unless it is
    announced, so it warns on stderr and the report carries
    `binding_checked: false` for the payload to record.
    """
    artifact = tmp_path / "charness-artifacts" / "critique" / "v1-4-0-release-packet.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Release critique\n\nRelease: 1.4.0\n", encoding="utf-8")

    result = _preflight.enforce_release_critique_gate(
        tmp_path,
        critique_artifact="charness-artifacts/critique/v1-4-0-release-packet.md",
        critique_blocked=None,
        target_version=None,
    )

    assert result["ok"] is True
    assert result["binding_checked"] is False
    assert "accepted on PRESENCE alone" in capsys.readouterr().err


def test_a_non_string_manifest_version_resolves_to_no_binding_token(tmp_path: Path) -> None:
    """`gate_target_version` returns `None` rather than letting a malformed
    manifest version reach `target_version` and bind something arbitrary."""
    plan = _load_plan_module()
    args = SimpleNamespace(publish_current=True, set_version=None, part=None)

    plan.build_release_payload = lambda _root: {"surface_versions": {"packaging_manifest": 3}}
    try:
        assert plan.gate_target_version(tmp_path, args) is None
    finally:
        plan.build_release_payload = plan._current_release.build_payload
