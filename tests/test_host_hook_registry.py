"""#343: sibling host-hook intent registry + dangling-checkout liveness.

The registry makes a fourth hook intent a table row (not another copied
lazy-import block in `host_hook_install_lib`); `hook_state_liveness` flags
state-tracked hooks whose embedded script path no longer exists.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import host_hook_install_lib as lib
import host_hook_registry as registry

REPO_ROOT = Path(__file__).resolve().parent.parent


def _fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir()
    return repo


def _fake_home(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    return home


def _seed_state(repo: Path, entries: dict[str, dict[str, str]]) -> None:
    state: dict[str, object] = {"schema_version": 1}
    state.update(entries)
    lib.write_state(repo, state)


def test_registry_names_the_two_sibling_intents_in_payload_order() -> None:
    keys = [intent.key for intent in registry.SIBLING_HOOK_INTENTS]
    assert keys == ["find_skills_routing", "skill_anchor_edit_guard"]


def test_reconcile_host_hooks_payload_keys_match_pre_registry_shape(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    home = _fake_home(tmp_path)
    actions = lib.reconcile_host_hooks(repo, adapter={}, home=home)
    assert list(actions) == ["claude", "codex", "find_skills_routing", "skill_anchor_edit_guard"]


def test_fourth_intent_is_a_table_row(tmp_path: Path) -> None:
    # Adding a hypothetical fourth hook intent means passing one more registry
    # row — reconcile fan-out needs no new import block or code path.
    repo = _fake_repo(tmp_path)
    home = _fake_home(tmp_path)
    fourth = registry.SiblingHookIntent(
        key="hypothetical_fourth",
        module="host_hook_find_skills",
        reconcile_function="reconcile_find_skills_hooks",
        status_function="find_skills_routing_status",
        script_relative_attr="FIND_SKILLS_SCRIPT_RELATIVE",
    )
    actions = registry.reconcile_sibling_hooks(
        repo, adapter={}, home=home, intents=(*registry.SIBLING_HOOK_INTENTS, fourth)
    )
    assert list(actions) == ["find_skills_routing", "skill_anchor_edit_guard", "hypothetical_fourth"]


def test_sibling_reconcile_isolates_per_host_errors(tmp_path: Path, monkeypatch) -> None:
    # An enabled host's failure reports per-host and never aborts the chain:
    # claude's installer raising HostHookError still yields a codex result and
    # the second sibling intent still reconciles.
    import host_hook_find_skills as fs

    repo = _fake_repo(tmp_path)
    home = _fake_home(tmp_path)

    def _boom(repo_root: Path, *, home: Path) -> dict[str, object]:
        raise lib.HostHookError("boom")

    monkeypatch.setattr(fs, "install_find_skills_claude_hook", _boom)
    adapter = {"find_skills_routing": {"claude": "enabled"}}
    actions = registry.reconcile_sibling_hooks(repo, adapter=adapter, home=home)
    assert actions["find_skills_routing"]["claude"]["error"] == "boom"
    assert "result" in actions["find_skills_routing"]["codex"]
    assert "claude" in actions["skill_anchor_edit_guard"]


def test_import_module_fallback_inserts_scripts_dir(monkeypatch) -> None:
    # The lazy-import fallback fires when scripts/ is absent from sys.path
    # (module invoked from elsewhere): the first import raises ImportError,
    # then the registry inserts its own parent dir and retries.
    scripts_dir = (REPO_ROOT / "scripts").resolve()
    cleaned = [p for p in sys.path if Path(p or ".").resolve() != scripts_dir]
    monkeypatch.setattr(sys, "path", cleaned)
    monkeypatch.delitem(sys.modules, "host_hook_find_skills", raising=False)
    module = registry._import_module("host_hook_find_skills")
    assert module.__name__ == "host_hook_find_skills"


def test_liveness_flags_missing_script(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    missing = repo / "scripts" / "usage_episode_session_start.py"
    _seed_state(
        repo,
        {
            "claude": {
                "settings_path": str(tmp_path / "home" / ".claude" / "settings.json"),
                "kind": "claude-json",
                "command": f"python3 {missing} --host claude",
            }
        },
    )
    liveness = registry.hook_state_liveness(repo)
    assert [entry["state_key"] for entry in liveness["entries"]] == ["claude"]
    assert liveness["entries"][0]["script_exists"] is False
    assert len(liveness["dangling"]) == 1
    assert str(missing) in liveness["dangling"][0]


def test_liveness_passes_existing_script_and_skips_non_hook_keys(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    script = repo / "scripts" / "usage_episode_session_start.py"
    script.touch()
    _seed_state(
        repo,
        {
            "claude": {
                "settings_path": "x",
                "kind": "claude-json",
                "command": f"python3 {script} --host claude",
            }
        },
    )
    liveness = registry.hook_state_liveness(repo)
    # schema_version (non-dict) is skipped; the live entry is not dangling.
    assert liveness["dangling"] == []
    assert liveness["entries"][0]["script_exists"] is True


def test_liveness_flags_command_without_script_path(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    _seed_state(repo, {"claude": {"settings_path": "x", "kind": "claude-json", "command": "echo hi"}})
    liveness = registry.hook_state_liveness(repo)
    assert len(liveness["dangling"]) == 1
    assert "no script path found" in liveness["dangling"][0]


def test_liveness_skips_entry_without_command(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    _seed_state(repo, {"claude": {"settings_path": "x", "kind": "claude-json"}})
    liveness = registry.hook_state_liveness(repo)
    assert liveness["entries"] == []
    assert liveness["dangling"] == []


def test_liveness_flags_unparseable_command(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    _seed_state(repo, {"claude": {"settings_path": "x", "kind": "claude-json", "command": "python3 'unclosed"}})
    liveness = registry.hook_state_liveness(repo)
    assert len(liveness["dangling"]) == 1


def _claude_settings_payload(commands: list[str], event: str = "SessionStart") -> dict[str, object]:
    return {"hooks": {event: [{"matcher": "", "hooks": [{"type": "command", "command": cmd} for cmd in commands]}]}}


def test_known_basenames_derive_from_owning_module_constants() -> None:
    # Pin the derived set against the live constants; a forked literal list
    # or a renamed script constant fails here, not in a consumer.
    import host_hook_find_skills as fs
    import host_hook_skill_anchor_guard as guard

    assert registry.known_hook_script_basenames() == {
        lib.HOOK_SCRIPT_RELATIVE.name,
        fs.FIND_SKILLS_SCRIPT_RELATIVE.name,
        guard.GUARD_SCRIPT_RELATIVE.name,
    }
    assert registry.known_hook_script_basenames() == {
        "usage_episode_session_start.py",
        "session_start_find_skills.py",
        "post_edit_skill_anchor_guard.py",
    }


def test_settings_scan_flags_deleted_checkout_leftover_in_claude_json(tmp_path: Path) -> None:
    # The deleted-checkout case: NO state file knows this entry; only the
    # settings file does. A foreign hook command is never flagged.
    home = _fake_home(tmp_path)
    leftover = tmp_path / "deleted-checkout" / "scripts" / "usage_episode_session_start.py"
    settings = home / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        json.dumps(_claude_settings_payload([f"python3 {leftover} --host claude", "eslint --fix"])),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert len(scan["entries"]) == 1  # the foreign command is not even listed
    assert scan["entries"][0]["kind"] == "claude-json"
    assert scan["entries"][0]["script_exists"] is False
    assert len(scan["dangling"]) == 1
    assert str(leftover) in scan["dangling"][0]


def test_settings_scan_passes_live_entry_and_scans_all_events(tmp_path: Path) -> None:
    home = _fake_home(tmp_path)
    live = tmp_path / "live-checkout" / "scripts" / "post_edit_skill_anchor_guard.py"
    live.parent.mkdir(parents=True)
    live.touch()
    settings = home / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        json.dumps(_claude_settings_payload([f"python3 {live}"], event="PostToolUse")),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert scan["dangling"] == []
    assert scan["entries"][0]["script_exists"] is True


def test_settings_scan_flags_leftover_in_codex_hooks_json(tmp_path: Path) -> None:
    home = _fake_home(tmp_path)
    leftover = tmp_path / "gone" / "scripts" / "session_start_find_skills.py"
    hooks_json = home / ".codex" / "hooks.json"
    hooks_json.parent.mkdir(parents=True)
    hooks_json.write_text(
        json.dumps(_claude_settings_payload([f"python3 {leftover} --host codex"])),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert [entry["kind"] for entry in scan["entries"]] == ["codex-json"]
    assert len(scan["dangling"]) == 1


def test_settings_scan_flags_leftover_in_codex_config_toml(tmp_path: Path) -> None:
    import host_hook_codex_toml_lib as toml_lib

    home = _fake_home(tmp_path)
    leftover = tmp_path / "gone" / "scripts" / "usage_episode_session_start.py"
    config = home / ".codex" / "config.toml"
    config.parent.mkdir(parents=True)
    config.write_text(
        toml_lib.codex_toml_block(f"python3 {leftover} --host codex"),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert [entry["kind"] for entry in scan["entries"]] == ["codex-toml"]
    assert len(scan["dangling"]) == 1
    assert str(leftover) in scan["dangling"][0]


def test_settings_scan_degrades_to_silence(tmp_path: Path) -> None:
    # No settings files at all, then an unreadable/invalid JSON file: both are
    # silence, never an error — repos and machines without charness hooks
    # inherit nothing from the scan.
    home = _fake_home(tmp_path)
    assert registry.settings_file_scan(home) == {"entries": [], "dangling": []}
    settings = home / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text("{not json", encoding="utf-8")
    assert registry.settings_file_scan(home) == {"entries": [], "dangling": []}


def test_settings_scan_walks_malformed_json_shapes_tolerantly(tmp_path: Path) -> None:
    # Every malformed shape is skipped in place, the one valid leftover still
    # flags: hooks-not-dict file, non-list event, non-dict entry, non-list
    # inner hooks, command-less item.
    home = _fake_home(tmp_path)
    leftover = tmp_path / "gone" / "scripts" / "usage_episode_session_start.py"
    claude = home / ".claude" / "settings.json"
    claude.parent.mkdir(parents=True)
    claude.write_text(json.dumps({"hooks": "not-a-dict"}), encoding="utf-8")
    assert registry.settings_file_scan(home) == {"entries": [], "dangling": []}
    claude.write_text(
        json.dumps(
            {
                "hooks": {
                    "Stop": "not-a-list",
                    "PreToolUse": ["not-a-dict", {"hooks": "not-a-list"}],
                    "SessionStart": [
                        {"hooks": [{"type": "command"}, {"type": "command", "command": f"python3 {leftover}"}]}
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert len(scan["dangling"]) == 1


def test_settings_scan_toml_oserror_degrades_to_silence(tmp_path: Path, monkeypatch) -> None:
    # An existing-but-unreadable config.toml (permission error) degrades to
    # silence; a directory at that path is silence too (not-a-file short-circuit).
    import host_hook_codex_toml_lib as toml_lib

    home = _fake_home(tmp_path)
    (home / ".codex" / "config.toml").mkdir(parents=True)
    assert registry.settings_file_scan(home) == {"entries": [], "dangling": []}

    def _denied(path: Path) -> str:
        raise PermissionError(f"denied: {path}")

    monkeypatch.setattr(toml_lib, "read_text_or_empty", _denied)
    assert registry.settings_file_scan(home) == {"entries": [], "dangling": []}


def test_settings_scan_flags_known_basename_without_parseable_path(tmp_path: Path) -> None:
    # shlex fails on the unclosed quote, the basename fallback still matches a
    # known charness script, but no path token is extractable — flagged loudly
    # rather than silently passed.
    home = _fake_home(tmp_path)
    claude = home / ".claude" / "settings.json"
    claude.parent.mkdir(parents=True)
    claude.write_text(
        json.dumps(_claude_settings_payload(["python3 'unclosed usage_episode_session_start.py"])),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert len(scan["dangling"]) == 1
    assert "no script path found" in scan["dangling"][0]


def test_status_mode_reports_settings_leftover_without_state(tmp_path: Path) -> None:
    # End-to-end deleted-checkout acceptance: the repo's state file is empty
    # (the deleted checkout's state died with it), only the scratch home's
    # settings carry the leftover — status still flags it and exits 1.
    repo = _fake_repo(tmp_path)
    home = _fake_home(tmp_path)
    (repo / ".agents" / "usage-episodes-adapter.yaml").write_text(
        "version: 1\nenabled: false\n", encoding="utf-8"
    )
    leftover = tmp_path / "deleted-checkout" / "scripts" / "usage_episode_session_start.py"
    settings = home / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        json.dumps(_claude_settings_payload([f"python3 {leftover} --host claude"])),
        encoding="utf-8",
    )
    runner = REPO_ROOT / "scripts" / "reconcile_usage_episodes_host_hooks.py"
    result = subprocess.run(
        [sys.executable, str(runner), "--repo-root", str(repo), "--home", str(home), "--mode", "status"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["in_sync"] is False
    assert payload["settings_scan"]["dangling"]
    assert payload["hook_liveness"]["dangling"] == []  # state knows nothing
    assert any(str(leftover) in line for line in payload["drift"])


def test_status_mode_reports_dangling_hook_and_exits_one(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    home = _fake_home(tmp_path)
    (repo / ".agents" / "usage-episodes-adapter.yaml").write_text(
        "version: 1\nenabled: false\n", encoding="utf-8"
    )
    deleted_checkout_script = tmp_path / "deleted-checkout" / "scripts" / "usage_episode_session_start.py"
    _seed_state(
        repo,
        {
            "claude": {
                "settings_path": str(home / ".claude" / "settings.json"),
                "kind": "claude-json",
                "command": f"python3 {deleted_checkout_script} --host claude",
            }
        },
    )
    runner = REPO_ROOT / "scripts" / "reconcile_usage_episodes_host_hooks.py"
    result = subprocess.run(
        [sys.executable, str(runner), "--repo-root", str(repo), "--home", str(home), "--mode", "status"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["in_sync"] is False
    assert payload["hook_liveness"]["dangling"]
    assert any(str(deleted_checkout_script) in line for line in payload["drift"])
