from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

import scripts.cli.cmd_capability as cmd_capability


def _roots(tmp_path: Path) -> tuple[Path, Path]:
    return (tmp_path / "charness", tmp_path / "target")


def test_resolve_capability_missing_binding_existing_config(tmp_path: Path, monkeypatch) -> None:
    charness_root, target_root = _roots(tmp_path)
    monkeypatch.setattr(
        cmd_capability,
        "load_repo_capability_config",
        lambda root: {
            "path": str(target_root / "capability.json"),
            "exists": True,
            "bindings": {},
            "profiles": {},
        },
    )
    with pytest.raises(cmd_capability.CharnessError, match="does not bind"):
        cmd_capability.resolve_capability(
            charness_repo_root=charness_root,
            target_repo_root=target_root,
            logical_id="github.default",
        )


def test_resolve_capability_unknown_profile(tmp_path: Path, monkeypatch) -> None:
    charness_root, target_root = _roots(tmp_path)
    monkeypatch.setattr(
        cmd_capability,
        "load_repo_capability_config",
        lambda root: {
            "path": str(target_root / "capability.json"),
            "exists": True,
            "bindings": {"github.default": "github.missing"},
            "profiles": {"github.missing": "not-a-dict"},
        },
    )
    with pytest.raises(cmd_capability.CharnessError, match="unknown profile"):
        cmd_capability.resolve_capability(
            charness_repo_root=charness_root,
            target_repo_root=target_root,
            logical_id="github.default",
        )


def test_resolve_capability_unknown_provider(tmp_path: Path, monkeypatch) -> None:
    charness_root, target_root = _roots(tmp_path)
    monkeypatch.setattr(
        cmd_capability,
        "load_repo_capability_config",
        lambda root: {
            "path": str(target_root / "capability.json"),
            "exists": True,
            "bindings": {"github.default": "github.dev"},
            "profiles": {"github.dev": {"provider": "nope", "env_bindings": {}}},
        },
    )
    monkeypatch.setattr(cmd_capability, "provider_index", lambda root: {})
    with pytest.raises(cmd_capability.CharnessError, match="unknown provider"):
        cmd_capability.resolve_capability(
            charness_repo_root=charness_root,
            target_repo_root=target_root,
            logical_id="github.default",
        )


def test_load_skill_capability_needs_missing_file(tmp_path: Path) -> None:
    assert cmd_capability.load_skill_capability_needs(tmp_path, "nosuch") is None


def test_load_skill_capability_needs_rejects_non_dict(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "capability-needs.json").write_text("[1, 2]\n", encoding="utf-8")
    with pytest.raises(cmd_capability.CharnessError, match="JSON object"):
        cmd_capability.load_skill_capability_needs(tmp_path, "demo")


def test_explain_skill_capabilities_no_needs_file(tmp_path: Path) -> None:
    charness_root, target_root = _roots(tmp_path)
    payload = cmd_capability.explain_skill_capabilities(
        charness_repo_root=charness_root,
        target_repo_root=target_root,
        skill_id="nosuch",
    )
    assert payload["capability_needs"] == []
    assert payload["notes"]


def test_explain_skill_capabilities_rejects_bad_needs(tmp_path: Path) -> None:
    charness_root, target_root = _roots(tmp_path)
    skill_dir = charness_root / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "capability-needs.json").write_text(
        json.dumps({"capability_needs": "nope", "notes": []}) + "\n", encoding="utf-8"
    )
    with pytest.raises(cmd_capability.CharnessError, match="as a list"):
        cmd_capability.explain_skill_capabilities(
            charness_repo_root=charness_root,
            target_repo_root=target_root,
            skill_id="demo",
        )


def test_explain_skill_capabilities_rejects_bad_notes(tmp_path: Path) -> None:
    charness_root, target_root = _roots(tmp_path)
    skill_dir = charness_root / "skills" / "public" / "demo2"
    skill_dir.mkdir(parents=True)
    (skill_dir / "capability-needs.json").write_text(
        json.dumps({"capability_needs": [], "notes": "nope"}) + "\n", encoding="utf-8"
    )
    with pytest.raises(cmd_capability.CharnessError, match="as a list"):
        cmd_capability.explain_skill_capabilities(
            charness_repo_root=charness_root,
            target_repo_root=target_root,
            skill_id="demo2",
        )


def test_capability_doctor_payload_missing_provider(tmp_path: Path, monkeypatch) -> None:
    charness_root, _ = _roots(tmp_path)
    monkeypatch.setattr(cmd_capability, "invoke_repo_json_script", lambda *a, **k: [])
    resolved: dict[str, object] = {
        "provider_id": "github-gh",
        "env_binding_status": {},
    }
    with pytest.raises(cmd_capability.CharnessError, match="did not resolve"):
        cmd_capability.capability_doctor_payload(
            charness_repo_root=charness_root, resolved=resolved
        )


def test_print_capability_summary_full(capsys) -> None:
    payload: dict[str, object] = {
        "logical_id": "github.default",
        "target_repo_root": "/repo",
        "capability_config_path": "/repo/cap.json",
        "profile_id": "github.dev",
        "provider_id": "github-gh",
        "provider_kind": "cli",
        "provider_manifest_path": "/m.json",
        "env_bindings": {"GH_TOKEN": "GH_TOKEN_DEV"},
        "env_binding_status": {"GH_TOKEN": {"present": True}},
        "provider_doctor": {"doctor_status": "ok", "support_state": "ready"},
    }
    cmd_capability.print_capability_summary(payload)
    out = capsys.readouterr().out
    assert "LOGICAL_ID: github.default" in out
    assert "TARGET_REPO_ROOT: /repo" in out
    assert "CONFIG: /repo/cap.json" in out
    assert "PROFILE: github.dev" in out
    assert "PROVIDER: github-gh (cli)" in out
    assert "PROVIDER_MANIFEST: /m.json" in out
    assert "ENV_BINDING: GH_TOKEN <- GH_TOKEN_DEV (present)" in out
    assert "PROVIDER_DOCTOR: ok (ready)" in out


def test_print_capability_summary_empty(capsys) -> None:
    payload: dict[str, object] = {
        "logical_id": "x.default",
        "target_repo_root": "/repo",
        "capability_config_path": "/repo/cap.json",
        "profile_id": "x.dev",
        "provider_id": "web-fetch",
        "provider_kind": "public",
        "provider_manifest_path": "/m.json",
        "env_bindings": {},
    }
    cmd_capability.print_capability_summary(payload)
    out = capsys.readouterr().out
    assert "ENV_BINDING: none" in out
    assert "PROVIDER_DOCTOR" not in out


def test_print_capability_explain_summary_full(capsys) -> None:
    payload: dict[str, object] = {
        "skill_id": "demo",
        "metadata_path": "/skills/demo/capability-needs.json",
        "capability_needs": [
            "not-a-dict",
            {"logical_id": "github.default", "summary": "s", "when": "always"},
            {"logical_id": "x.default", "summary": "t", "when": ""},
        ],
        "notes": ["hello", 42],
        "announcement_delivery": {
            "delivery_kind": "human-backend",
            "status": "executable",
            "delivery_capability": "x.default",
        },
    }
    cmd_capability.print_capability_explain_summary(payload)
    out = capsys.readouterr().out
    assert "SKILL: demo" in out
    assert "METADATA: /skills/demo/capability-needs.json" in out
    assert "NEEDS: github.default - s" in out
    assert "WHEN: always" in out
    assert "NEEDS: x.default - t" in out
    assert "NOTE: hello" in out
    assert "42" not in out
    assert "ANNOUNCEMENT_DELIVERY: human-backend executable x.default" in out


def test_print_capability_explain_summary_empty(capsys) -> None:
    payload: dict[str, object] = {
        "skill_id": "demo",
        "capability_needs": [],
        "notes": [],
    }
    cmd_capability.print_capability_explain_summary(payload)
    out = capsys.readouterr().out
    assert "SKILL: demo" in out
    assert "METADATA" not in out
    assert "NEEDS: none" in out


def test_cmd_capability_doctor_blocking_disposition(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cmd_capability, "_resolve_charness_repo_root", lambda args: tmp_path)
    monkeypatch.setattr(cmd_capability, "resolve_capability", lambda **k: {"logical_id": "x"})
    monkeypatch.setattr(
        cmd_capability,
        "capability_doctor_payload",
        lambda **k: {
            "provider_doctor": {"doctor_disposition": "blocking-failure"},
            "missing_env_sources": [],
        },
    )
    emitted: dict[str, object] = {}
    monkeypatch.setattr(cmd_capability, "emit_yaml", lambda payload: emitted.update(payload))
    args = argparse.Namespace(target_repo_root=None, logical_id="x.default")
    assert cmd_capability.cmd_capability_doctor(args) == 1


def test_cmd_capability_doctor_missing_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cmd_capability, "_resolve_charness_repo_root", lambda args: tmp_path)
    monkeypatch.setattr(cmd_capability, "resolve_capability", lambda **k: {"logical_id": "x"})
    monkeypatch.setattr(
        cmd_capability,
        "capability_doctor_payload",
        lambda **k: {
            "provider_doctor": {"doctor_disposition": "ok"},
            "missing_env_sources": ["GH_TOKEN_DEV"],
        },
    )
    monkeypatch.setattr(cmd_capability, "emit_yaml", lambda payload: None)
    args = argparse.Namespace(target_repo_root=None, logical_id="x.default")
    assert cmd_capability.cmd_capability_doctor(args) == 1


def test_cmd_capability_env_no_bindings(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cmd_capability, "_resolve_charness_repo_root", lambda args: tmp_path)
    monkeypatch.setattr(
        cmd_capability,
        "resolve_capability",
        lambda **k: {
            "profile_id": "github.dev",
            "env_bindings": {},
            "env_binding_status": {},
        },
    )
    args = argparse.Namespace(target_repo_root=None, logical_id="github.default")
    with pytest.raises(cmd_capability.CharnessError, match="does not declare"):
        cmd_capability.cmd_capability_env(args)
