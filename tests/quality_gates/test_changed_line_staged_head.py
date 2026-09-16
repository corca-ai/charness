"""Staged-tree analysis target for changed-line gates (`:staged:`).

The release lane must prove the tree it is about to commit, but trust only
attested committed ranges — so a first commit of pool changes could never
earn its own receipt (commit needs receipt, receipt needs commit). These
controls pin the fix: staged-only dirt analyzes the index tree with the same
anti-false-green invariant (worktree pool bytes == analyzed tree pool
bytes), while staged-invisible changes still refuse.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from scripts.core.git_status_snapshot import GitStatusRecord, GitStatusSnapshot
from scripts.gates_support import changed_line_run_trust as trust
from scripts.gates_support.changed_line_staged_head import (
    STAGED_HEAD,
    resolve_staged_tree,
    staged_dirty_refusal,
    staged_false_green_message,
    staged_invisible_from_snapshot,
    staged_invisible_pool_changes,
)

from .changed_line_mutation_fixtures import (
    git as _git,
)
from .changed_line_mutation_fixtures import (
    seed_repo_with_changed_pool_file as _seed,
)
from .support import run_script

_TEETH = "scripts/mutation/check_changed_line_mutation_coverage.py"
POOL = {"scripts/foo.py"}


def _snapshot(*records: GitStatusRecord) -> GitStatusSnapshot:
    return GitStatusSnapshot("a" * 40, "main", tuple(records))


def _ordinary(path: str, xy: str) -> GitStatusRecord:
    return GitStatusRecord("ordinary", xy, path)


def test_staged_only_dirt_is_visible_to_the_staged_tree() -> None:
    snapshot = _snapshot(_ordinary("scripts/foo.py", "M."))
    assert staged_invisible_from_snapshot(snapshot, POOL) == []


def test_unstaged_and_untracked_pool_changes_are_staged_invisible() -> None:
    snapshot = _snapshot(
        _ordinary("scripts/foo.py", ".M"),
        _ordinary("scripts/bar.py", "MM"),
        GitStatusRecord("untracked", "", "scripts/new.py"),
        _ordinary("docs/guide.md", ".M"),
    )
    assert staged_invisible_from_snapshot(snapshot, {"scripts/foo.py", "scripts/bar.py", "scripts/new.py"}) == [
        "scripts/bar.py",
        "scripts/foo.py",
        "scripts/new.py",
    ]


def test_unparseable_status_fails_closed() -> None:
    snapshot = _snapshot(GitStatusRecord("ordinary", "?!?", "scripts/foo.py"))
    assert staged_invisible_from_snapshot(snapshot, POOL) == ["scripts/foo.py"]


def test_resolve_staged_tree_matches_write_tree(tmp_path: Path) -> None:
    repo, _base, _head = _seed(tmp_path)
    assert resolve_staged_tree(repo) == _git(repo, "write-tree")


def test_probe_staged_pins_the_index_tree(tmp_path: Path) -> None:
    repo, _base, _head = _seed(tmp_path)
    probe = trust.probe_run_trust(repo, STAGED_HEAD, POOL)
    assert probe.contaminated == []
    assert probe.unestablished_kind is None
    assert probe.resolved_pair[0] == _git(repo, "write-tree")


def test_probe_staged_reports_unstaged_dirt(tmp_path: Path) -> None:
    repo, _base, _head = _seed(tmp_path)
    foo = repo / "scripts" / "foo.py"
    foo.write_text(foo.read_text(encoding="utf-8") + "\n# worktree note\n", encoding="utf-8")
    probe = trust.probe_run_trust(repo, STAGED_HEAD, POOL)
    assert probe.contaminated == ["scripts/foo.py"]
    assert probe.unestablished_kind is None


def test_staged_drift_ignores_a_mid_run_commit(tmp_path: Path, monkeypatch) -> None:
    pinned = {"head_commit": "a" * 40, "pool_fingerprint": "fp", "resolved_head_sha": "b" * 40}
    monkeypatch.setattr(
        trust, "_pin_run_state", lambda *_args, **_kwargs: dict(pinned, head_commit="c" * 40)
    )
    assert trust.run_state_drift(tmp_path, "base", STAGED_HEAD, pinned) is None


def test_staged_drift_catches_an_index_only_change(tmp_path: Path) -> None:
    from scripts.gates_support import changed_line_run_trust as trust_module

    repo, base, _head = _seed(tmp_path)
    foo = repo / "scripts" / "foo.py"
    foo.write_text(foo.read_text(encoding="utf-8") + "\n# staged note\n", encoding="utf-8")
    _git(repo, "add", "scripts/foo.py")
    probe = trust_module.probe_run_trust(repo, STAGED_HEAD, POOL)
    assert probe.unestablished_kind is None
    pinned = trust_module._pin_run_state(
        repo, base, STAGED_HEAD, resolved_pair=probe.resolved_pair
    )
    # Index-only movement: unstage while the worktree (and its fingerprint)
    # stays identical, so only the tree comparison can catch it.
    _git(repo, "reset", "-q", "HEAD", "--", "scripts/foo.py")
    drift = trust_module.run_state_drift(repo, base, STAGED_HEAD, pinned)
    assert drift is not None and "staged index tree changed" in drift


def test_staged_messages_name_staging_not_committing() -> None:
    assert "git add" in staged_dirty_refusal(["scripts/foo.py"], "b" * 64)
    assert "staged index" in staged_false_green_message(["scripts/foo.py"], "b" * 64)


def _run(repo: Path, base: str, cov: Path) -> subprocess.CompletedProcess[str]:
    return run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        STAGED_HEAD,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
    )


def _cover_all(repo: Path, path: str = "scripts/foo.py") -> Path:
    import json

    lines = (repo / path).read_text(encoding="utf-8").splitlines()
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps({"files": {path: {"executed_lines": list(range(1, len(lines) + 1)), "missing_lines": []}}}),
        encoding="utf-8",
    )
    return cov


def test_staged_only_change_gets_a_real_verdict(tmp_path: Path) -> None:
    repo, base, _head = _seed(tmp_path)
    foo = repo / "scripts" / "foo.py"
    foo.write_text(foo.read_text(encoding="utf-8") + "\n\ndef c():\n    return 3\n", encoding="utf-8")
    _git(repo, "add", "scripts/foo.py")
    result = _run(repo, base, _cover_all(repo))
    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["head_sha"] == STAGED_HEAD
    assert payload["resolved_head_sha"] == _git(repo, "write-tree")


def test_staged_change_with_uncovered_lines_blocks(tmp_path: Path) -> None:
    import json

    repo, base, _head = _seed(tmp_path)
    foo = repo / "scripts" / "foo.py"
    before = foo.read_text(encoding="utf-8").splitlines()
    foo.write_text(foo.read_text(encoding="utf-8") + "\n\ndef c():\n    return 3\n", encoding="utf-8")
    _git(repo, "add", "scripts/foo.py")
    after = foo.read_text(encoding="utf-8").splitlines()
    new_lines = list(range(len(before) + 1, len(after) + 1))
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps(
            {
                "files": {
                    "scripts/foo.py": {
                        "executed_lines": [n for n in range(1, len(before) + 1)],
                        "missing_lines": new_lines,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    result = _run(repo, base, cov)
    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["blocking"] == ["scripts/foo.py"]


def test_unstaged_change_refuses_with_staging_instructions(tmp_path: Path) -> None:
    repo, base, _head = _seed(tmp_path)
    foo = repo / "scripts" / "foo.py"
    foo.write_text(foo.read_text(encoding="utf-8") + "\n# worktree note\n", encoding="utf-8")
    result = _run(repo, base, _cover_all(repo))
    assert result.returncode == 2, result.stdout + result.stderr
    assert "git add" in result.stderr


def test_staged_invisible_helper_returns_none_when_git_fails(tmp_path: Path, monkeypatch) -> None:
    from scripts.gates_support import changed_line_staged_head as staged

    def boom(*_args, **_kwargs):
        raise OSError("git not found")

    monkeypatch.setattr(staged, "GitCheckout", boom)
    assert staged_invisible_pool_changes(tmp_path, POOL) is None


def test_probe_staged_resolve_failure_is_inspection_failed(tmp_path: Path, monkeypatch) -> None:
    from scripts.gates_support import changed_line_staged_head as staged

    repo, _base, _head = _seed(tmp_path)
    monkeypatch.setattr(staged, "resolve_staged_tree", lambda _root: None)
    probe = trust.probe_run_trust(repo, STAGED_HEAD, POOL)
    assert probe.unestablished_kind == "inspection-failed"
    assert "staged index tree" in probe.unestablished_reason


def test_probe_staged_snapshot_failure_is_inspection_failed(tmp_path: Path, monkeypatch) -> None:
    from scripts.gates_support import changed_line_staged_head as staged

    repo, _base, _head = _seed(tmp_path)
    monkeypatch.setattr(staged, "staged_invisible_pool_changes", lambda *_a, **_k: None)
    probe = trust.probe_run_trust(repo, STAGED_HEAD, POOL)
    assert probe.unestablished_kind == "inspection-failed"
    assert "staged-invisible" in probe.unestablished_reason


def test_staged_drift_reports_worktree_movement(tmp_path: Path, monkeypatch) -> None:
    pinned = {"head_commit": "a" * 40, "pool_fingerprint": "fp", "resolved_head_sha": "b" * 40}
    monkeypatch.setattr(
        trust, "_pin_run_state", lambda *_args, **_kwargs: dict(pinned, pool_fingerprint="moved")
    )
    drift = trust.run_state_drift(tmp_path, "base", STAGED_HEAD, pinned)
    assert drift is not None and "worktree content changed" in drift


def test_resolve_returns_none_when_git_is_missing(tmp_path: Path, monkeypatch) -> None:
    from scripts.gates_support import changed_line_staged_head as staged

    def boom(*_args, **_kwargs):
        raise OSError("git not found")

    monkeypatch.setattr(staged, "run_process", boom)
    assert resolve_staged_tree(tmp_path) is None


def test_resolve_returns_none_on_unusable_output(tmp_path: Path, monkeypatch) -> None:
    from types import SimpleNamespace

    from scripts.gates_support import changed_line_staged_head as staged

    monkeypatch.setattr(
        staged, "run_process", lambda *_a, **_k: SimpleNamespace(returncode=1, stdout="")
    )
    assert resolve_staged_tree(tmp_path) is None
    monkeypatch.setattr(
        staged, "run_process", lambda *_a, **_k: SimpleNamespace(returncode=0, stdout="not-a-sha\n")
    )
    assert resolve_staged_tree(tmp_path) is None


def test_ignored_records_are_skipped() -> None:
    snapshot = _snapshot(GitStatusRecord("ignored", "", "scripts/foo.py"))
    assert staged_invisible_from_snapshot(snapshot, POOL) == []


def test_dirty_rename_lists_both_names() -> None:
    snapshot = _snapshot(GitStatusRecord("rename", "RM", "scripts/new.py", "scripts/old.py"))
    assert staged_invisible_from_snapshot(
        snapshot, {"scripts/new.py", "scripts/old.py"}
    ) == ["scripts/new.py", "scripts/old.py"]


def test_bootstrap_inserts_an_absent_repo_root(monkeypatch) -> None:
    import sys

    from scripts.gates_support import changed_line_staged_head as staged

    from .support import ROOT

    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(ROOT)])
    staged._load_repo_runtime_bootstrap()
    assert sys.path[0] == str(ROOT)
