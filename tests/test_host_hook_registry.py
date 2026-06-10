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
