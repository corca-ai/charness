"""Direct unit tests for `capability_support` uncovered branches (#873)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.cli.capability_support as cap


def _write_capability(root: Path, payload: object) -> Path:
    path = root / ".charness" / "local" / "capability.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_read_json_mapping_returns_default_on_bad_json(tmp_path: Path) -> None:
    path = tmp_path / "capability.json"
    path.write_text("{not json", encoding="utf-8")
    assert cap.read_json_mapping(path, default={"a": 1}) == {"a": 1}


def test_load_repo_capability_config_rejects_non_dict_bindings(tmp_path: Path) -> None:
    _write_capability(tmp_path, {"bindings": [], "profiles": {}})
    with pytest.raises(cap.CharnessError):
        cap.load_repo_capability_config(tmp_path)


def test_load_repo_capability_config_rejects_bad_binding_entry(tmp_path: Path) -> None:
    _write_capability(tmp_path, {"bindings": {"": "profile"}, "profiles": {}})
    with pytest.raises(cap.CharnessError):
        cap.load_repo_capability_config(tmp_path)


def test_load_repo_capability_config_rejects_non_dict_profiles(tmp_path: Path) -> None:
    _write_capability(tmp_path, {"bindings": {}, "profiles": []})
    with pytest.raises(cap.CharnessError):
        cap.load_repo_capability_config(tmp_path)


def test_load_repo_capability_config_rejects_bad_profile_shapes(tmp_path: Path) -> None:
    _write_capability(tmp_path, {"bindings": {}, "profiles": {"": {"provider": "x"}}})
    with pytest.raises(cap.CharnessError):
        cap.load_repo_capability_config(tmp_path)
    _write_capability(tmp_path, {"bindings": {}, "profiles": {"p": "nope"}})
    with pytest.raises(cap.CharnessError):
        cap.load_repo_capability_config(tmp_path)
    _write_capability(tmp_path, {"bindings": {}, "profiles": {"p": {}}})
    with pytest.raises(cap.CharnessError):
        cap.load_repo_capability_config(tmp_path)


def test_load_repo_capability_config_rejects_bad_env_bindings(tmp_path: Path) -> None:
    _write_capability(
        tmp_path,
        {"bindings": {}, "profiles": {"p": {"provider": "g", "env_bindings": {"K": ""}}}},
    )
    with pytest.raises(cap.CharnessError):
        cap.load_repo_capability_config(tmp_path)


def test_build_repo_onboarding_source_missing(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "src"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    monkeypatch.setattr(cap, "looks_like_repo_root", lambda path: True)
    monkeypatch.setattr(cap, "has_source_manifest", lambda path: False)
    payload = cap.build_repo_onboarding_payload(source_repo_root=source, target_repo_root=target)
    assert payload["status"] == "source-missing"
    assert payload["manual_action_required"] is True
    assert "charness init" in str(payload["message"])


def test_build_repo_onboarding_required_without_skill_tree(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "src"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    monkeypatch.setattr(cap, "looks_like_repo_root", lambda path: True)
    monkeypatch.setattr(cap, "has_source_manifest", lambda path: True)
    monkeypatch.setattr(cap, "invoke_repo_script", lambda *args, **kwargs: "raw")
    monkeypatch.setattr(
        cap,
        "parse_repo_script_payload",
        lambda stdout, source: {
            "repo_mode": "GREENFIELD",
            "agent_docs": {"recommended_action": "edit"},
        },
    )
    payload = cap.build_repo_onboarding_payload(source_repo_root=source, target_repo_root=target)
    assert payload["status"] == "required"
    assert payload["manual_action_required"] is True
    assert payload["reasons"] == ["core_operating_surface", "agent_docs"]
    assert payload["skill_bearing_repo"] is False
    assert "setup" in str(payload["message"])


def test_build_repo_onboarding_ready_for_skill_bearing_repo(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "src"
    target = tmp_path / "target"
    (target / "skills" / "public").mkdir(parents=True)
    source.mkdir()
    monkeypatch.setattr(cap, "looks_like_repo_root", lambda path: True)
    monkeypatch.setattr(cap, "has_source_manifest", lambda path: True)
    monkeypatch.setattr(cap, "invoke_repo_script", lambda *args, **kwargs: "raw")
    monkeypatch.setattr(
        cap,
        "parse_repo_script_payload",
        lambda stdout, source: {
            "repo_mode": "ONBOARDED",
            "agent_docs": {"recommended_action": "leave_as_is"},
        },
    )
    payload = cap.build_repo_onboarding_payload(source_repo_root=source, target_repo_root=target)
    assert payload["status"] == "ready"
    assert payload["reasons"] == []
    assert payload["skill_bearing_repo"] is True


def test_update_gitignore_appends_missing_line(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("node_modules/", encoding="utf-8")
    assert cap.update_gitignore_for_capability_local(tmp_path) == "appended"
    assert gitignore.read_text(encoding="utf-8") == "node_modules/\n/.charness/local/\n"
