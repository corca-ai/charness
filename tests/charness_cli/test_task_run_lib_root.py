"""`charness task run` inside a charness source checkout runs that checkout's runner."""

from __future__ import annotations

import argparse
from pathlib import Path

from tests.charness_cli.support import CLI, load_cli_module


def _cli(name: str):
    return load_cli_module(name, CLI)


def _source_checkout(root: Path) -> Path:
    (root / "packaging").mkdir(parents=True)
    (root / "packaging" / "charness.json").write_text("{}\n", encoding="utf-8")
    (root / "scripts" / "task_run").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "task_run" / "task_run.py").write_text("", encoding="utf-8")
    return root


def _patch_resolver_seams(monkeypatch, resolve_repo_root):
    """Patch the namespaces `_resolve_worktree_lib_root` reads after #873.

    The resolver lives in `scripts.cli.bootstrap_state`: entry-bound roots
    come lazily from `scripts.cli.bootstrap`, and `resolve_repo_root` from
    its own module global. Patching the loaded entry copy no longer reaches
    either, so both land here.
    """
    import scripts.cli.bootstrap as bootstrap
    import scripts.cli.bootstrap_state as bootstrap_state

    monkeypatch.setattr(bootstrap, "EMBEDDED_REPO_ROOT", None)
    monkeypatch.setattr(bootstrap_state, "resolve_repo_root", resolve_repo_root)


def test_parent_source_checkout_wins_over_the_managed_checkout(tmp_path: Path, monkeypatch) -> None:
    module = _cli("charness_task_run_lib_root_own")
    own = _source_checkout(tmp_path / "own")
    managed = _source_checkout(tmp_path / "managed")
    _patch_resolver_seams(monkeypatch, lambda *_args: (managed, True))
    args = argparse.Namespace(repo_root=own, home_root=tmp_path / "home", charness_checkout=None)

    assert module._resolve_worktree_lib_root(args) == own.resolve()


def test_explicit_checkout_still_wins_over_the_parent(tmp_path: Path, monkeypatch) -> None:
    module = _cli("charness_task_run_lib_root_explicit")
    own = _source_checkout(tmp_path / "own")
    explicit = _source_checkout(tmp_path / "explicit")
    _patch_resolver_seams(monkeypatch, lambda _home, given: (given.resolve(), False))
    args = argparse.Namespace(
        repo_root=own, home_root=tmp_path / "home", charness_checkout=explicit
    )

    assert module._resolve_worktree_lib_root(args) == explicit.resolve()


def test_a_consumer_parent_falls_through_to_the_managed_checkout(
    tmp_path: Path, monkeypatch
) -> None:
    module = _cli("charness_task_run_lib_root_consumer")
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    managed = _source_checkout(tmp_path / "managed")
    _patch_resolver_seams(monkeypatch, lambda *_args: (managed, True))
    args = argparse.Namespace(
        repo_root=consumer, home_root=tmp_path / "home", charness_checkout=None
    )

    assert module._resolve_worktree_lib_root(args) == managed
