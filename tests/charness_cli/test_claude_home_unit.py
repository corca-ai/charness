from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
from pathlib import Path

from .support import CLI, build_test_path, make_fake_claude


def load_charness_module():
    name = "charness_claude_home_unit_under_test"
    loader = importlib.machinery.SourceFileLoader(name, str(CLI))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_claude_subprocess_env_preserves_default_and_binds_custom_home(tmp_path: Path, monkeypatch) -> None:
    module = load_charness_module()
    inherited = tmp_path / "inherited"
    custom = tmp_path / "custom"
    monkeypatch.setenv("HOME", str(inherited))
    monkeypatch.setattr(module, "default_home_root", lambda: inherited.resolve())

    assert module.claude_subprocess_env(inherited) is None

    env = module.claude_subprocess_env(custom)
    assert env is not None
    assert env["HOME"] == str(custom.resolve())
    assert env["PATH"] == os.environ.get("PATH", "")


def test_run_claude_forwards_effective_home_to_subprocess(tmp_path: Path, monkeypatch) -> None:
    module = load_charness_module()
    custom = tmp_path / "custom"
    process_home = tmp_path / "process"
    monkeypatch.setenv("HOME", str(process_home))
    seen: list[dict[str, str] | None] = []

    def fake_run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None):
        seen.append(env)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(module, "run", fake_run)

    result = module.run_claude(["claude", "--version"], cwd=tmp_path, home_root=custom)

    assert result.returncode == 0
    assert seen[0] is not None
    assert seen[0]["HOME"] == str(custom.resolve())


def test_all_claude_call_sites_bind_custom_home_and_doctor_reads_it(tmp_path: Path, monkeypatch) -> None:
    module = load_charness_module()
    repo = CLI.parent
    custom = tmp_path / "custom-home"
    process_home = tmp_path / "unrelated-process-home"
    fake_claude = make_fake_claude(tmp_path)
    monkeypatch.setenv("HOME", str(process_home))
    monkeypatch.setenv("PATH", build_test_path(fake_claude.parent))

    calls: list[tuple[list[str], str]] = []

    def run_claude(command: list[str], *, cwd: Path, home_root: Path):
        env = module.claude_subprocess_env(home_root)
        effective_home = (env or os.environ)["HOME"]
        calls.append((command, effective_home))
        return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True, env=env)

    monkeypatch.setattr(module, "run_claude", run_claude)

    # New marketplace: add + update. A stale source then exercises remove + add + update.
    module.ensure_claude_marketplace(repo, home_root=custom)
    known = custom / ".claude/plugins/known_marketplaces.json"
    known.write_text('{"corca-charness": {"source": {"source": "path", "path": "/stale"}}}\n')
    module.ensure_claude_marketplace(repo, home_root=custom)

    # Install and update paths both end in enable; update also refreshes the marketplace.
    module.ensure_claude_plugin(repo, home_root=custom, update=False)
    module.ensure_claude_plugin(repo, home_root=custom, update=True)

    # Doctor's consumer and both removal families must use the same effective HOME.
    status = module.claude_enabled_status(repo, home_root=custom)
    assert status is not None and status["present"] is True
    assert module.remove_claude_plugin(repo, home_root=custom) is True
    assert module.remove_claude_marketplace(repo, home_root=custom) is True

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
    assert all(any(tuple(command[: len(prefix)]) == prefix for command, _home in calls) for prefix in expected)
    assert {home for _command, home in calls} == {str(custom.resolve())}
    assert not (process_home / ".claude").exists()


def test_doctor_consumer_uses_custom_home_for_claude_listing(tmp_path: Path, monkeypatch) -> None:
    module = load_charness_module()
    repo = CLI.parent
    custom = tmp_path / "custom-home"
    process_home = tmp_path / "unrelated-process-home"
    fake_claude = make_fake_claude(tmp_path)
    monkeypatch.setenv("HOME", str(process_home))
    monkeypatch.setenv("PATH", build_test_path(fake_claude.parent))
    plugin_root = repo / "plugins" / "charness"

    # Seed the selected home through the fake CLI, while the inherited HOME stays empty.
    module.ensure_claude_marketplace(repo, home_root=custom)
    module.ensure_claude_plugin(repo, home_root=custom, update=False)
    payload = module.build_doctor_payload(
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
