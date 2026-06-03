"""Lazy, composable test DSL for the subprocess + tmp-repo idiom.

Most quality_gates and control_plane tests follow one shape: build a small repo
under ``tmp_path`` (dirs + a ``.agents/<name>-adapter.yaml`` + a few artifact
files), run a ``scripts/*.py`` entrypoint against it with ``--repo-root``, then
assert on exit code, JSON stdout, stderr substrings, and files the script wrote
back. This module captures that shape as two small immutable values layered over
plain ``subprocess`` — it does not replace the area ``support.py`` helpers (fake
tool builders, expensive whole-repo fixtures); it absorbs the per-test
``seed_repo`` copy-paste and the ``returncode == 0, stderr`` / ``json.loads``
boilerplate.

Design:

- ``Repo`` is a frozen, lazy filesystem spec. Every method returns a new value;
  nothing touches disk until ``build()``/``run()``. File bodies may be a ``str``
  or a zero-arg callable (a thunk), so expensive bodies stay deferred and a test
  materializes only the files it declares.
- ``Result`` wraps a finished process plus the repo path with chainable,
  intention-revealing assertions.

``Repo.run()`` injects ``--repo-root <repo>`` because that is the dominant
convention; ``run_raw()`` is the escape hatch for entrypoints that take the repo
path differently or not at all.

Scope: this targets the subprocess + tmp-repo idiom only. In-process tests that
call library functions directly (most flat ``tests/test_*.py``) do not need it
and should keep using plain pytest.

Environment: a run with ``env=None`` (the default) inherits the full parent
environment — including the ``CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS`` and
``GIT_CEILING_DIRECTORIES`` that the autouse ``conftest`` fixtures set. Passing
an explicit ``env=`` *fully replaces* the environment (it does not merge onto
``os.environ`` the way the area ``support.run_script`` helpers do), so merge it
yourself until a dedicated merge-semantics slice lands.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Union

import yaml

ROOT = Path(__file__).resolve().parents[1]

Content = Union[str, Callable[[], str]]


def _render(content: Content) -> str:
    return content() if callable(content) else content


@dataclass(frozen=True)
class Repo:
    """A lazy, composable description of a tmp repo. Disk I/O happens in build()."""

    _entries: tuple[tuple[str, Content], ...] = ()

    def file(self, path: str, content: Content) -> Repo:
        """Add one file at repo-relative ``path``; ``content`` may be a thunk."""
        return replace(self, _entries=self._entries + ((path, content),))

    def files(self, mapping: Mapping[str, Content]) -> Repo:
        """Add many files at once from a ``{path: content}`` mapping."""
        return replace(self, _entries=self._entries + tuple(mapping.items()))

    def adapter(self, name: str, body: Mapping[str, Any] | str) -> Repo:
        """Add ``.agents/<name>-adapter.yaml`` from a dict (rendered) or raw text."""
        text = body if isinstance(body, str) else yaml.safe_dump(dict(body), sort_keys=False)
        return self.file(f".agents/{name}-adapter.yaml", text)

    def merge(self, other: Repo) -> Repo:
        """Layer another spec's files on top of this one (later entries win on disk)."""
        return replace(self, _entries=self._entries + other._entries)

    def build(self, root: Path, *, name: str = "repo") -> Path:
        """Materialize the spec under ``root/<name>`` and return the repo path."""
        repo = root / name
        repo.mkdir(parents=True, exist_ok=True)
        for rel, content in self._entries:
            target = repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_render(content), encoding="utf-8")
        return repo

    def run(self, root: Path, script: str, *flags: str, env: Mapping[str, str] | None = None) -> Result:
        """Build the repo, then run ``script`` with ``--repo-root`` auto-injected.

        Each call re-materializes a fresh repo and re-evaluates content thunks. For
        a multi-step flow against one repo (run, mutate a file, run again), call
        ``build()`` once and reuse ``run_at``.
        """
        return run_at(self.build(root), script, *flags, env=env)


@dataclass(frozen=True)
class Result:
    """A finished subprocess plus its repo, with chainable assertions."""

    proc: subprocess.CompletedProcess[str]
    repo: Path

    def ok(self) -> Result:
        assert self.proc.returncode == 0, (
            f"exit {self.proc.returncode} at {self.repo}\n"
            f"stdout:\n{self.proc.stdout}\nstderr:\n{self.proc.stderr}"
        )
        return self

    def failed(self, code: int | None = None) -> Result:
        assert self.proc.returncode != 0, f"expected failure, got 0\n{self.proc.stdout}"
        if code is not None:
            assert self.proc.returncode == code, f"expected exit {code}, got {self.proc.returncode}"
        return self

    def stderr_has(self, *substrings: str) -> Result:
        for sub in substrings:
            assert sub in self.proc.stderr, f"{sub!r} not in stderr:\n{self.proc.stderr}"
        return self

    def stdout_has(self, *substrings: str) -> Result:
        for sub in substrings:
            assert sub in self.proc.stdout, f"{sub!r} not in stdout:\n{self.proc.stdout}"
        return self

    @property
    def json(self) -> Any:
        """Parse stdout as JSON."""
        return json.loads(self.proc.stdout)

    def file_text(self, rel: str) -> str:
        """Read a file the script wrote, relative to the repo root."""
        return (self.repo / rel).read_text(encoding="utf-8")

    def file_json(self, rel: str) -> Any:
        """Read and parse a JSON file the script wrote, relative to the repo root."""
        return json.loads(self.file_text(rel))


def _run(argv: Iterable[str], repo: Path, env: Mapping[str, str] | None) -> Result:
    proc = subprocess.run(
        ["python3", *argv],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=dict(env) if env is not None else None,
    )
    return Result(proc, repo)


def run_at(repo: Path, script: str, *flags: str, env: Mapping[str, str] | None = None) -> Result:
    """Run ``script`` against an already-built ``repo``, injecting ``--repo-root``."""
    return _run([script, "--repo-root", str(repo), *flags], repo, env)


def run_raw(repo: Path, *argv: str, env: Mapping[str, str] | None = None) -> Result:
    """Run a raw ``python3`` argv against ``repo`` with no flag injection."""
    return _run(argv, repo, env)
