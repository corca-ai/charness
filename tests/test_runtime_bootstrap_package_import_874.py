"""Import-time environment pollution guard (#874).

Importing a `scripts.*` package module (e.g. `scripts.task_run.task_run_git`
via the hooks chain, or `scripts.core.git_status_snapshot`) must not mutate
the process environment: no `CHARNESS_RUNTIME_ROOT_AUTO`/`CHARNESS_RUNTIME_REPO_KEY`
markers, no `TMPDIR`/cache rewrites for the real repo. While those markers
lingered, `runtime_root()` silently ignored a pointed `CHARNESS_RUNTIME_ROOT`
for any other repo, so friction-record assertions observed other tests'
history. A standalone entry script (`__main__`) still owns its process
environment and keeps the historic configure side effect.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

from scripts import runtime_bootstrap
from scripts.runtime_bootstrap import repo_root_from_script
from tests.module_eviction import evict_module

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_FILE = REPO_ROOT / "charness"


def test_package_caller_skips_configure(monkeypatch) -> None:
    """A caller inside `scripts.*` resolves the root without configuring."""
    calls: list[Path] = []
    monkeypatch.setattr(
        runtime_bootstrap,
        "configure_runtime_environment",
        lambda root: calls.append(Path(root)) or {},
    )
    namespace = {
        "__name__": "scripts.fake_874_caller",
        "repo_root_from_script": repo_root_from_script,
        "script_file": str(SCRIPT_FILE),
    }
    exec("RESULT = repo_root_from_script(script_file)", namespace)
    assert calls == []
    assert namespace["RESULT"] == REPO_ROOT


def test_standalone_caller_configures(monkeypatch) -> None:
    """A standalone caller (this test module) keeps the historic side effect."""
    calls: list[Path] = []
    monkeypatch.setattr(
        runtime_bootstrap,
        "configure_runtime_environment",
        lambda root: calls.append(Path(root)) or {},
    )
    root = repo_root_from_script(SCRIPT_FILE)
    assert root == REPO_ROOT
    assert calls == [REPO_ROOT]


def test_package_context_detection_edge_cases(monkeypatch) -> None:
    """Frame-machinery failures fail safe toward historic behavior."""
    assert runtime_bootstrap._package_import_context() is False
    monkeypatch.setattr(sys, "_getframe", lambda _depth: None)
    assert runtime_bootstrap._package_import_context() is False

    def _boom(_depth):
        raise ValueError("shallow stack")

    monkeypatch.setattr(sys, "_getframe", _boom)
    assert runtime_bootstrap._package_import_context() is False


def test_import_chain_leaves_environ_untouched(monkeypatch, tmp_path) -> None:
    """Re-importing an import_repo_module user does not touch os.environ.

    The pointed root plus STALE auto markers (another repo's key) is the
    exact state from the issue: the pre-#874 loader ran
    `configure_runtime_environment` for the real repo, took the auto branch
    on the key mismatch, and rewrote the pointed root, the markers, TMPDIR
    and the cache dirs. A plain `configure` is idempotent against an
    already-consistent environment, so only the inconsistent state makes
    this test sensitive. The `finally` restore keeps the worker safe if
    this ever fails.
    """
    import tempfile

    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(tmp_path / "runtime"))
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT_AUTO", "1")
    monkeypatch.setenv("CHARNESS_RUNTIME_REPO_KEY", "stale-key-from-another-repo")
    before = dict(os.environ)
    old_pycache_prefix = getattr(sys, "pycache_prefix", None)
    old_tempdir = tempfile.tempdir
    try:
        evict_module(monkeypatch, "scripts.core.git_status_snapshot")
        importlib.import_module("scripts.core.git_status_snapshot")
        assert dict(os.environ) == before
    finally:
        os.environ.clear()
        os.environ.update(before)
        if old_pycache_prefix is None:
            if hasattr(sys, "pycache_prefix"):
                del sys.pycache_prefix
        else:
            sys.pycache_prefix = old_pycache_prefix
        tempfile.tempdir = old_tempdir
