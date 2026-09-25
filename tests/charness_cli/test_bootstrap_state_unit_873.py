"""Direct unit tests for `bootstrap_state` uncovered branches (#873)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import scripts.cli.bootstrap_state as bs


def test_configure_runtime_missing_owner_raises(monkeypatch) -> None:
    import pytest

    monkeypatch.setattr(bs, "_runtime_bootstrap_module", lambda repo_root: None)
    with pytest.raises(bs.CharnessError):
        bs._configure_runtime_for_repo(Path("/nonexistent"), required=True)


def test_git_head_returns_none_on_git_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(bs, "is_git_checkout", lambda path: True)
    monkeypatch.setattr(
        bs, "run", lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="")
    )
    assert bs.git_head(tmp_path) is None


def test_read_version_state_handles_bad_and_non_dict_payloads(tmp_path: Path) -> None:
    path = bs.default_version_state_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    assert bs.read_version_state(tmp_path) == {"state_version": 1}
    path.write_text(json.dumps([1, 2]), encoding="utf-8")
    assert bs.read_version_state(tmp_path) == {"state_version": 1}


def test_write_version_state_records_latest_release(tmp_path: Path) -> None:
    state = bs.write_version_state(tmp_path, latest_release={"latest_version": "9.0.0"})
    assert state["latest_release"] == {"latest_version": "9.0.0"}
    assert bs.read_version_state(tmp_path)["latest_release"] == {"latest_version": "9.0.0"}


def test_refresh_self_release_state_marks_update(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(bs, "probe_self_release", lambda: {"latest_version": "9.0.0"})
    monkeypatch.setattr(bs, "compute_update_available", lambda current, latest: True)
    state = bs.refresh_self_release_state(home_root=tmp_path, current_version="8.0.0")
    release = state["latest_release"]
    assert isinstance(release, dict)
    assert release["current_version"] == "8.0.0"
    assert release["update_available"] is True
    assert release["checked_at"]


def test_should_auto_refresh_ci_and_version_check_and_force(monkeypatch) -> None:
    eligible = {"eligible_for_auto_update_check": True}
    monkeypatch.delenv("CHARNESS_NO_UPDATE_CHECK", raising=False)
    monkeypatch.delenv("CHARNESS_FORCE_UPDATE_CHECK", raising=False)
    monkeypatch.setenv("CI", "1")
    args = argparse.Namespace(command="doctor", check=False)
    assert bs.should_auto_refresh_self_release(args, eligible) is False
    monkeypatch.delenv("CI", raising=False)
    version_args = argparse.Namespace(command="version", check=True)
    assert bs.should_auto_refresh_self_release(version_args, eligible) is False
    monkeypatch.setenv("CHARNESS_FORCE_UPDATE_CHECK", "1")
    assert bs.should_auto_refresh_self_release(args, eligible) is True


def test_maybe_record_self_version_state_refreshes_and_prints(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(bs, "resolve_repo_root", lambda home, explicit: (tmp_path, True))
    monkeypatch.setattr(
        bs,
        "build_version_provenance",
        lambda **kwargs: {"eligible_for_auto_update_check": True, "current_version": "8.0.0"},
    )
    monkeypatch.setattr(bs, "write_version_state", lambda home, **kwargs: {"latest_release": None})
    monkeypatch.setattr(bs, "should_auto_refresh_self_release", lambda args, prov: True)
    monkeypatch.setattr(bs, "latest_release_cache_is_fresh", lambda release, current: False)
    monkeypatch.setattr(
        bs,
        "refresh_self_release_state",
        lambda **kwargs: {"latest_release": {"status": "ok"}},
    )
    monkeypatch.setattr(bs, "build_self_update_notice", lambda release: "UPDATE!")
    args = argparse.Namespace(command="doctor", home_root=tmp_path, cli_path=None)
    bs.maybe_record_self_version_state(args)
    assert "UPDATE!" in capsys.readouterr().err


def test_build_version_payload_with_check_refreshes_release(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        bs,
        "build_version_provenance",
        lambda **kwargs: {"current_version": "8.0.0"},
    )
    monkeypatch.setattr(
        bs, "write_version_state", lambda home, **kwargs: {"latest_release": {"stale": True}}
    )
    monkeypatch.setattr(
        bs,
        "refresh_self_release_state",
        lambda **kwargs: {"latest_release": {"fresh": True}},
    )
    monkeypatch.setattr(bs, "build_self_update_notice", lambda release: None)
    payload = bs.build_version_payload(
        home_root=tmp_path,
        repo_root=tmp_path,
        managed_checkout=True,
        cli_path=tmp_path / "charness",
        check=True,
    )
    assert payload["latest_release_check"] == {"fresh": True}
