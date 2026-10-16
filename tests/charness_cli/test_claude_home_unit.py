from __future__ import annotations

import os
import subprocess
from pathlib import Path

import scripts.cli.bootstrap as bootstrap
import scripts.cli.cmd_meta as cmd_meta
import scripts.cli.doctor_payload as doctor_payload
import scripts.cli.host_claude as host_claude

from .support import CLI, build_test_path, make_fake_claude


def test_claude_subprocess_env_preserves_default_and_binds_custom_home(
    tmp_path: Path, monkeypatch
) -> None:
    inherited = tmp_path / "inherited"
    custom = tmp_path / "custom"
    monkeypatch.setenv("HOME", str(inherited))
    monkeypatch.setattr(host_claude, "default_home_root", lambda: inherited.resolve())

    assert host_claude.claude_subprocess_env(inherited) is None

    env = host_claude.claude_subprocess_env(custom)
    assert env is not None
    assert env["HOME"] == str(custom.resolve())
    assert env["PATH"] == os.environ.get("PATH", "")


def test_run_claude_forwards_effective_home_to_subprocess(tmp_path: Path, monkeypatch) -> None:
    custom = tmp_path / "custom"
    process_home = tmp_path / "process"
    monkeypatch.setenv("HOME", str(process_home))
    seen: list[dict[str, str] | None] = []

    def fake_run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None):
        seen.append(env)
        return subprocess.CompletedProcess(command, 0, "", "")

    # `run_claude` lives in scripts/cli/host_claude.py after #873: patch the
    # namespace the payload calls, not the loaded entry copy.
    import scripts.cli.host_claude as host_claude

    monkeypatch.setattr(host_claude, "run", fake_run)

    result = host_claude.run_claude(["claude", "--version"], cwd=tmp_path, home_root=custom)

    assert result.returncode == 0
    assert seen[0] is not None
    assert seen[0]["HOME"] == str(custom.resolve())


def test_all_claude_call_sites_bind_custom_home_and_doctor_reads_it(
    tmp_path: Path, monkeypatch
) -> None:
    repo = CLI.parent
    custom = tmp_path / "custom-home"
    process_home = tmp_path / "unrelated-process-home"
    fake_claude = make_fake_claude(tmp_path)
    monkeypatch.setenv("HOME", str(process_home))
    monkeypatch.setenv("PATH", build_test_path(fake_claude.parent))

    calls: list[tuple[list[str], str]] = []

    def run_claude(command: list[str], *, cwd: Path, home_root: Path):
        env = host_claude.claude_subprocess_env(home_root)
        effective_home = (env or os.environ)["HOME"]
        calls.append((command, effective_home))
        return subprocess.run(
            command, cwd=cwd, check=False, capture_output=True, text=True, env=env
        )

    # Call sites live in scripts/cli/host_claude.py after #873.
    monkeypatch.setattr(host_claude, "run_claude", run_claude)

    # New marketplace: add + update. A stale source then exercises remove + add + update.
    host_claude.ensure_claude_marketplace(repo, home_root=custom)
    known = custom / ".claude/plugins/known_marketplaces.json"
    known.write_text('{"corca-charness": {"source": {"source": "path", "path": "/stale"}}}\n')
    host_claude.ensure_claude_marketplace(repo, home_root=custom)

    # Install and update paths both end in enable; update also refreshes the marketplace.
    host_claude.ensure_claude_plugin(repo, home_root=custom, update=False)
    host_claude.ensure_claude_plugin(repo, home_root=custom, update=True)

    # Doctor's consumer and both removal families must use the same effective HOME.
    status = host_claude.claude_enabled_status(repo, home_root=custom)
    assert status is not None and status["present"] is True
    assert cmd_meta.remove_claude_plugin(repo, home_root=custom) is True
    assert cmd_meta.remove_claude_marketplace(repo, home_root=custom) is True

    expected = (
        ("claude", "plugins", "marketplace", "add"),
        ("claude", "plugins", "marketplace", "update"),
        ("claude", "plugins", "marketplace", "remove"),
        ("claude", "plugins", "install"),
        ("claude", "plugins", "update"),
        ("claude", "plugins", "enable"),
        ("claude", "plugins", "list"),
        ("claude", "plugins", "uninstall"),
    )
    assert all(
        any(tuple(command[: len(prefix)]) == prefix for command, _home in calls)
        for prefix in expected
    )
    assert {home for _command, home in calls} == {str(custom.resolve())}
    assert not (process_home / ".claude").exists()


def test_remove_paths_intercept_late_patch_after_early_cmd_meta_import(
    tmp_path: Path, monkeypatch
) -> None:
    """The remove paths honor a late `run_claude` patch after an early import.

    `cmd_meta` used to from-bind `run_claude`, so when it was imported before
    the patch (the full-suite order), the remove calls bypassed the patched
    namespace while every return-value assertion still passed. Importing it
    first here pins that order.
    """
    import scripts.cli.cmd_meta  # noqa: F401 - pin the full-suite import order

    repo = CLI.parent
    custom = tmp_path / "custom-home"
    process_home = tmp_path / "unrelated-process-home"
    fake_claude = make_fake_claude(tmp_path)
    monkeypatch.setenv("HOME", str(process_home))
    monkeypatch.setenv("PATH", build_test_path(fake_claude.parent))

    calls: list[list[str]] = []

    def run_claude(command: list[str], *, cwd: Path, home_root: Path):
        calls.append(command)
        return subprocess.run(
            command, cwd=cwd, check=False, capture_output=True, text=True, env=None
        )

    monkeypatch.setattr(host_claude, "run_claude", run_claude)

    assert cmd_meta.remove_claude_plugin(repo, home_root=custom) is True
    assert cmd_meta.remove_claude_marketplace(repo, home_root=custom) is True
    assert any(tuple(command[:3]) == ("claude", "plugins", "uninstall") for command in calls)
    assert any(
        tuple(command[:4]) == ("claude", "plugins", "marketplace", "remove") for command in calls
    )


def test_doctor_consumer_uses_custom_home_for_claude_listing(tmp_path: Path, monkeypatch) -> None:
    repo = CLI.parent
    monkeypatch.setattr(bootstrap, "SCRIPT_PATH", CLI)
    monkeypatch.setattr(bootstrap, "EMBEDDED_REPO_ROOT", repo)
    custom = tmp_path / "custom-home"
    process_home = tmp_path / "unrelated-process-home"
    fake_claude = make_fake_claude(tmp_path)
    monkeypatch.setenv("HOME", str(process_home))
    monkeypatch.setenv("PATH", build_test_path(fake_claude.parent))
    plugin_root = repo / "plugins" / "charness"

    # Seed the selected home through the fake CLI, while the inherited HOME stays empty.
    host_claude.ensure_claude_marketplace(repo, home_root=custom)
    host_claude.ensure_claude_plugin(repo, home_root=custom, update=False)
    payload = doctor_payload.build_doctor_payload(
        home_root=custom,
        repo_root=repo,
        managed_checkout=False,
        target_repo_root=repo,
        plugin_root=plugin_root,
        codex_marketplace_path=tmp_path / "marketplace.json",
        cli_path=tmp_path / "charness",
        claude_wrapper_path=tmp_path / "claude-charness",
    )

    assert payload["claude_enabled_status"]["present"] is True
    assert payload["claude_installed_entry"]["version"] == "local"
    assert not (process_home / ".claude").exists()
