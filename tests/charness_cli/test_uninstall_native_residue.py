"""The native-core residue cleanup in `charness uninstall`, and its containment guard.

`charness:4526-4534` runs `shutil.rmtree` on a directory derived from the state
home, and `resolve_state_home` lets an operator relocate that state home anywhere
via `CHARNESS_STATE_HOME`/`XDG_STATE_HOME`. The `relative_to` guard is the only
thing standing between that `rmtree` and a path outside the home root, so both
branches are exercised here rather than left to fire first on someone's machine.

The residue itself is self-terminating -- once the directory is gone the cleanup
is a no-op -- which is exactly why it would otherwise never be observed running.
"""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest
import yaml

from .test_managed_install import load_charness_module


def _uninstall_module(monkeypatch: pytest.MonkeyPatch, repo_root: Path, home_root: Path):
    module = load_charness_module("charness_uninstall_native_residue_under_test")
    monkeypatch.setattr(module, "resolve_repo_root", lambda *_args: (repo_root, False))
    monkeypatch.setattr(
        module,
        "resolve_runtime_paths",
        lambda _args: (
            home_root / "plugin",
            home_root / "marketplace.json",
            home_root / "claude",
            home_root / "cli",
        ),
    )
    monkeypatch.setattr(module, "has_source_manifest", lambda _path: False)
    monkeypatch.setattr(module, "remove_codex_marketplace_entry", lambda _path: False)
    monkeypatch.setattr(module, "remove_codex_config_entries", lambda _path: [])
    return module


def _uninstall_args(repo_root: Path, home_root: Path) -> Namespace:
    return Namespace(
        home_root=home_root,
        repo_root=repo_root,
        plugin_root=None,
        codex_marketplace_path=None,
        claude_wrapper_path=None,
        cli_path=None,
        delete_checkout=False,
        delete_cli=False,
    )


def test_uninstall_removes_native_core_residue_inside_the_home_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    home_root = tmp_path / "home"
    monkeypatch.setenv("CHARNESS_STATE_HOME", str(home_root / ".local" / "state"))
    module = _uninstall_module(monkeypatch, repo_root, home_root)
    native_root = module.default_state_root(home_root) / "native"
    native_root.mkdir(parents=True)
    (native_root / "repograph").write_text("stale acquisition artifact", encoding="utf-8")

    assert module.cmd_uninstall(_uninstall_args(repo_root, home_root)) == 0

    assert yaml.safe_load(capsys.readouterr().out)["removed_native_core"] is True
    assert not native_root.exists()


def test_uninstall_refuses_a_native_root_outside_the_home_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    home_root = tmp_path / "home"
    home_root.mkdir()
    # A relocated state home is a supported configuration, not a malformed one:
    # `resolve_state_home` honours CHARNESS_STATE_HOME ahead of the home root.
    monkeypatch.setenv("CHARNESS_STATE_HOME", str(tmp_path / "elsewhere"))
    module = _uninstall_module(monkeypatch, repo_root, home_root)
    native_root = module.default_state_root(home_root) / "native"
    native_root.mkdir(parents=True)
    (native_root / "repograph").write_text("not ours to delete", encoding="utf-8")

    assert module.cmd_uninstall(_uninstall_args(repo_root, home_root)) == 0

    assert yaml.safe_load(capsys.readouterr().out)["removed_native_core"] is False
    assert (native_root / "repograph").read_text(encoding="utf-8") == "not ours to delete"
