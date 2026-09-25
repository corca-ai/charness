"""Direct unit tests for the #873 `tool_commands` feature module.

Selection and repair branches only run inside tool flows the suite exercises
through seed-checkout copies, so in-process coverage never reaches them
without direct calls.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

import scripts.cli.tool_commands as tool_commands


def _manifest(
    tools_dir: Path,
    name: str,
    tool_id: object,
    skills: list[str],
    role: str | None = None,
) -> None:
    payload: dict[str, object] = {"tool_id": tool_id, "supports_public_skills": skills}
    if role is not None:
        payload["recommendation_role"] = role
    (tools_dir / name).write_text(json.dumps(payload), encoding="utf-8")


def _repo_with_manifests(tmp_path: Path) -> Path:
    tools_dir = tmp_path / "integrations" / "tools"
    tools_dir.mkdir(parents=True)
    (tools_dir / "manifest.schema.json").write_text("{}", encoding="utf-8")
    _manifest(tools_dir, "a.json", "tool-a", ["skill-x"], role="editor")
    _manifest(tools_dir, "b.json", "tool-b", ["skill-y"], role="reviewer")
    _manifest(tools_dir, "c.json", "tool-c", ["skill-x", "skill-y"])
    return tmp_path


def _args(**kwargs) -> argparse.Namespace:
    base = {
        "tool_ids": [],
        "recommend_for_skill": None,
        "recommendation_role": None,
        "next_skill_id": None,
    }
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_selected_tool_ids_prefers_explicit_ids(tmp_path: Path) -> None:
    args = _args(tool_ids=["tool-a"])
    assert tool_commands.selected_tool_ids_from_args(args, tmp_path) == ["tool-a"]


def test_selected_tool_ids_rejects_mixed_filters(tmp_path: Path) -> None:
    _repo_with_manifests(tmp_path)
    args = _args(tool_ids=["tool-a"], recommend_for_skill="skill-x")
    with pytest.raises(
        tool_commands.CharnessError, match="either explicit tool ids or recommendation"
    ):
        tool_commands.selected_tool_ids_from_args(args, tmp_path)


def test_selected_tool_ids_filters_manifests(tmp_path: Path) -> None:
    repo = _repo_with_manifests(tmp_path)
    assert tool_commands.selected_tool_ids_from_args(
        _args(recommend_for_skill="skill-x"), repo
    ) == ["tool-a", "tool-c"]
    assert tool_commands.selected_tool_ids_from_args(
        _args(recommendation_role="reviewer"), repo
    ) == ["tool-b"]
    assert tool_commands.selected_tool_ids_from_args(
        _args(recommend_for_skill="skill-y", next_skill_id="skill-y"), repo
    ) == ["tool-b", "tool-c"]


def test_selected_tool_ids_reports_empty_match(tmp_path: Path) -> None:
    repo = _repo_with_manifests(tmp_path)
    with pytest.raises(
        tool_commands.CharnessError, match="No tools matched recommendation filters"
    ):
        tool_commands.selected_tool_ids_from_args(
            _args(
                recommend_for_skill="skill-missing",
                recommendation_role="nobody",
                next_skill_id="skill-missing",
            ),
            repo,
        )


def test_tool_selection_payload_shapes(tmp_path: Path) -> None:
    assert tool_commands.tool_selection_payload(_args(), ["a"]) is None
    payload = tool_commands.tool_selection_payload(
        _args(recommend_for_skill="s", recommendation_role="r", next_skill_id="n"),
        ["a"],
    )
    assert payload is not None and payload["selected_tool_ids"] == ["a"]


def _repair_fakes(monkeypatch, repair_payload, repair_rc, doctor_results) -> None:
    monkeypatch.setattr(tool_commands, "resolve_repo_python", lambda _repo: "/usr/bin/python3")
    monkeypatch.setattr(
        tool_commands,
        "_run_repo_json_command",
        lambda _repo, _cmd: (repair_payload, repair_rc, ""),
    )
    monkeypatch.setattr(tool_commands, "invoke_repo_json_script", lambda *_a, **_k: doctor_results)


def test_repair_agent_browser_reports_failed(tmp_path: Path, monkeypatch) -> None:
    _repair_fakes(monkeypatch, {"target_pids": [1]}, 1, [])
    result = tool_commands._repair_agent_browser(tmp_path, tmp_path, execute=True)
    assert result["repair"]["status"] == "failed"


def test_repair_agent_browser_reports_would_repair(tmp_path: Path, monkeypatch) -> None:
    _repair_fakes(monkeypatch, {"target_pids": [7]}, 0, [])
    result = tool_commands._repair_agent_browser(tmp_path, tmp_path, execute=False)
    assert result["repair"]["status"] == "would-repair"
    assert "remove owned" in result["next_step"]


def test_repair_agent_browser_reports_executed(tmp_path: Path, monkeypatch) -> None:
    doctor_results = [{"tool_id": "agent-browser", "doctor_disposition": "healthy", "doctor": {}}]
    _repair_fakes(monkeypatch, {}, 0, doctor_results)
    result = tool_commands._repair_agent_browser(tmp_path, tmp_path, execute=True)
    assert result["repair"]["status"] == "executed"
    assert "ready" in result["next_step"]


def _command_fakes(monkeypatch, invoke_results) -> list[dict]:
    emitted: list[dict] = []
    monkeypatch.setattr(
        tool_commands, "resolve_tool_repo_root", lambda _args: (Path("/repo"), False)
    )
    monkeypatch.setattr(tool_commands, "default_plugin_root", lambda _path: Path("/plugin"))
    monkeypatch.setattr(tool_commands, "invoke_repo_json_script", lambda *_a, **_k: invoke_results)
    monkeypatch.setattr(
        tool_commands,
        "emit_operational_response",
        lambda _args, payload, **_kwargs: emitted.append(payload),
    )
    return emitted


def _base_command_args() -> argparse.Namespace:
    return argparse.Namespace(
        home_root=Path("/home"),
        repo_root=Path("/repo"),
        plugin_root=None,
        tool_ids=["tool-a"],
        no_write_locks=False,
        execute=False,
        upstream_checkout=["/upstream"],
        dry_run=False,
        skip_sync_support=True,
        recommend_for_skill=None,
        recommendation_role=None,
        next_skill_id=None,
    )


def test_cmd_tool_doctor_flags_blocking_disposition(monkeypatch) -> None:
    emitted = _command_fakes(
        monkeypatch,
        [{"tool_id": "tool-a", "doctor_disposition": "blocking-failure"}],
    )
    assert tool_commands.cmd_tool_doctor(_base_command_args()) == 1
    assert emitted and emitted[0]["results"]["tool-a"]["doctor"]["doctor_disposition"] == (
        "blocking-failure"
    )


def test_cmd_tool_repair_flags_failed_repair(monkeypatch) -> None:
    _command_fakes(monkeypatch, [])
    monkeypatch.setattr(
        tool_commands,
        "_repair_agent_browser",
        lambda _repo, _plugin, execute: {"repair": {"status": "failed"}},
    )
    args = _base_command_args()
    args.tool_ids = ["agent-browser"]
    assert tool_commands.cmd_tool_repair(args) == 1


def test_cmd_tool_sync_support_flags_blocking_doctor(monkeypatch) -> None:
    emitted = _command_fakes(
        monkeypatch,
        [{"tool_id": "tool-a", "doctor_disposition": "blocking-install-needed"}],
    )
    assert tool_commands.cmd_tool_sync_support(_base_command_args()) == 1
    assert emitted and "tool-a" in emitted[0]["results"]


def test_cmd_tool_install_flags_failed_install(monkeypatch) -> None:
    emitted = _command_fakes(
        monkeypatch,
        [{"tool_id": "tool-a", "status": "failed"}],
    )
    args = _base_command_args()
    args.tool_ids = []
    args.skip_sync_support = False
    assert tool_commands.cmd_tool_install(args) == 1
    assert emitted and "tool-a" in emitted[0]["results"]
