from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_script_loading import load_release_script

OBSERVER = load_release_script("release_observer")


def _result(returncode: int, stdout: str = "", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def _payload() -> dict:
    return {
        "target_version": "2.1.5",
        "tag_name": "v2.1.5",
        "commit_sha": "abc123",
        "release_url": "https://example.test/releases/tag/v2.1.5",
        "distinct_channel_verification": {
            "channel": "https-fetch",
            "status": "confirmed",
            "url": "https://example.test/releases/tag/v2.1.5",
        },
    }


def test_release_observer_persists_canonical_channel_and_installed_readback(tmp_path: Path) -> None:
    commands: list[str] = []

    def run_shell(command: str, **_kwargs):
        commands.append(command)
        if command == "charness version":
            return _result(0, "version: 2.1.5\n")
        return _result(0, "status: healthy\n")

    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={"status": "refreshed", "command": "charness update"},
        version_command="charness version",
        doctor_command="charness doctor",
        run_shell=run_shell,
    )
    payload = _payload()
    out = OBSERVER.write_release_observer(
        tmp_path,
        payload=payload,
        installed_readback=installed,
        now=lambda: datetime(2026, 7, 19, 1, 2, tzinfo=timezone.utc),
    )

    assert out["path"] == "charness-artifacts/probe/2026-07-19-v2.1.5-release-observer.json"
    record = json.loads((tmp_path / out["path"]).read_text(encoding="utf-8"))
    assert record["distinct_channel_verification"] == payload["distinct_channel_verification"]
    assert record["installed_readback"]["status"] == "observed"
    assert record["installed_readback"]["version"]["value"] == "version: 2.1.5"
    assert commands == ["charness version", "charness doctor"]
    assert not any("verdict" in key for key in record if key != "distinct_channel_verification")


def test_release_observer_records_unavailable_readbacks_without_false_success(tmp_path: Path) -> None:
    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={"status": "failed", "command": "charness update"},
        version_command="",
        doctor_command="charness doctor",
        run_shell=lambda *_a, **_k: _result(2, stderr="doctor unavailable"),
    )
    out = OBSERVER.write_release_observer(
        tmp_path,
        payload=_payload(),
        installed_readback=installed,
        now=lambda: datetime(2026, 7, 19, tzinfo=timezone.utc),
    )

    assert out["status"] == "unavailable"
    record = out["record"]
    assert record["installed_readback"]["version"]["status"] == "unavailable"
    assert record["installed_readback"]["version"]["reason"] == "adapter readback command is not configured"
    assert record["installed_readback"]["doctor"]["status"] == "unavailable"
    assert record["non_claims"]


def test_release_observer_converts_runner_exception_to_unavailable(tmp_path: Path) -> None:
    def fail(*_args, **_kwargs):
        raise OSError("binary disappeared")

    installed = OBSERVER.collect_installed_readback(
        tmp_path,
        install_refresh={"status": "refreshed"},
        version_command="charness version",
        doctor_command="charness doctor",
        run_shell=fail,
    )
    assert installed["status"] == "unavailable"
    assert installed["version"]["reason"] == "OSError: binary disappeared"
    assert installed["doctor"]["reason"] == "OSError: binary disappeared"


def test_release_observer_persistence_error_is_typed_and_nonblocking(tmp_path: Path) -> None:
    payload = _payload()
    payload["commit_sha"] = ""  # forces schema validation failure before any write
    out = OBSERVER.safe_write_release_observer(
        tmp_path,
        payload=payload,
        installed_readback={"status": "unavailable"},
    )
    assert out["status"] == "capture_error"
    assert out["path"] is None
    assert "target.commit" in out["reason"]
    assert out["non_claims"]


@pytest.mark.parametrize(
    "mutate, match",
    [
        (lambda record: record["target"].__setitem__("commit", ""), "target.commit"),
        (lambda record: record.__setitem__("distinct_channel_verification", {}), "channel"),
        (lambda record: record.__setitem__("installed_readback", {}), "installed_readback.status"),
        (lambda record: record.__setitem__("non_claims", []), "non_claims"),
    ],
)
def test_release_observer_validator_rejects_incomplete_evidence(mutate, match: str) -> None:
    record = {
        "schema_version": "charness.release_observer.v1",
        "target": {
            "version": "2.1.5",
            "tag": "v2.1.5",
            "commit": "abc123",
            "release_url": "https://example.test/v2.1.5",
        },
        "distinct_channel_verification": {"channel": "https-fetch", "status": "confirmed"},
        "installed_readback": {"status": "observed"},
        "non_claims": ["not terminal proof"],
    }
    mutate(record)
    with pytest.raises(ValueError, match=match):
        OBSERVER.validate_release_observer_record(record)
