"""#343: optional host-hook registry + dangling-checkout liveness.

The registry makes another hook intent a table row (not another copied
lazy-import block in `host_hook_install_lib`); `hook_state_liveness` flags
state-tracked hooks whose embedded script path no longer exists.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.hooks import host_hook_install_lib as lib
from scripts.hooks import host_hook_registry as registry
from tests.module_eviction import evict_module

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


def test_registry_names_the_supported_intent() -> None:
    keys = [intent.key for intent in registry.SIBLING_HOOK_INTENTS]
    assert keys == ["skill_anchor_edit_guard"]


def test_reconcile_host_hooks_payload_keys_match_pre_registry_shape(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    home = _fake_home(tmp_path)
    actions = lib.reconcile_host_hooks(repo, adapter={}, home=home)
    assert list(actions) == ["skill_anchor_edit_guard"]


def test_fourth_intent_is_a_table_row(tmp_path: Path) -> None:
    # Adding a hypothetical fourth hook intent means passing one more registry
    # row — reconcile fan-out needs no new import block or code path.
    repo = _fake_repo(tmp_path)
    home = _fake_home(tmp_path)
    fourth = registry.SiblingHookIntent(
        key="hypothetical_fourth",
        module="scripts.hooks.host_hook_skill_anchor_guard",
        reconcile_function="reconcile_skill_anchor_guard_hooks",
        status_function="skill_anchor_guard_status",
        script_relative_attr="GUARD_SCRIPT_RELATIVE",
    )
    actions = registry.reconcile_sibling_hooks(
        repo, adapter={}, home=home, intents=(*registry.SIBLING_HOOK_INTENTS, fourth)
    )
    assert list(actions) == ["skill_anchor_edit_guard", "hypothetical_fourth"]


def test_import_module_loads_a_nested_package_module(monkeypatch) -> None:
    evict_module(monkeypatch, "scripts.hooks.host_hook_skill_anchor_guard")
    module = registry._import_module("scripts.hooks.host_hook_skill_anchor_guard")
    assert module.__name__ == "scripts.hooks.host_hook_skill_anchor_guard"


def test_liveness_flags_missing_script(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    missing = repo / "scripts" / "post_edit_skill_anchor_guard.py"
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
    script = repo / "scripts" / "post_edit_skill_anchor_guard.py"
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
    _seed_state(
        repo, {"claude": {"settings_path": "x", "kind": "claude-json", "command": "echo hi"}}
    )
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
    _seed_state(
        repo,
        {"claude": {"settings_path": "x", "kind": "claude-json", "command": "python3 'unclosed"}},
    )
    liveness = registry.hook_state_liveness(repo)
    assert len(liveness["dangling"]) == 1


def _claude_settings_payload(commands: list[str], event: str = "PostToolUse") -> dict[str, object]:
    return {
        "hooks": {
            event: [
                {"matcher": "", "hooks": [{"type": "command", "command": cmd} for cmd in commands]}
            ]
        }
    }


def test_known_basenames_derive_from_owning_module_constants() -> None:
    # Pin the derived set against the live constants; a forked literal list
    # or a renamed script constant fails here, not in a consumer.
    from scripts.hooks import host_hook_skill_anchor_guard as guard

    assert registry.known_hook_script_basenames() == {
        guard.GUARD_SCRIPT_RELATIVE.name,
    }


def test_settings_scan_flags_deleted_checkout_leftover_in_claude_json(tmp_path: Path) -> None:
    # The deleted-checkout case: NO state file knows this entry; only the
    # settings file does. A foreign hook command is never flagged.
    home = _fake_home(tmp_path)
    leftover = tmp_path / "deleted-checkout" / "scripts" / "post_edit_skill_anchor_guard.py"
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
    leftover = tmp_path / "gone" / "scripts" / "post_edit_skill_anchor_guard.py"
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
                    "PostToolUse": [
                        {
                            "hooks": [
                                {"type": "command"},
                                {"type": "command", "command": f"python3 {leftover}"},
                            ]
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert len(scan["dangling"]) == 1


def test_settings_scan_flags_known_basename_without_parseable_path(tmp_path: Path) -> None:
    # shlex fails on the unclosed quote, the basename fallback still matches a
    # known charness script, but no path token is extractable — flagged loudly
    # rather than silently passed.
    home = _fake_home(tmp_path)
    claude = home / ".claude" / "settings.json"
    claude.parent.mkdir(parents=True)
    claude.write_text(
        json.dumps(_claude_settings_payload(["python3 'unclosed post_edit_skill_anchor_guard.py"])),
        encoding="utf-8",
    )
    scan = registry.settings_file_scan(home)
    assert len(scan["dangling"]) == 1
    assert "no script path found" in scan["dangling"][0]
