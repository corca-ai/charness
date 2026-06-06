"""Tests for the changed-line mutation-coverage closeout producer (Slice 2).

The producer instruments the closeout broad pytest with plain coverage (lever
A+B: drop dynamic_context, piggyback the run), exports a small coverage JSON, and
stamps the freshness fingerprint marker the pre-push consumer trusts.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from .support import ROOT


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _seed_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    foo = repo / "scripts" / "foo.py"
    foo.write_text("def a():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    foo.write_text("def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")
    return repo, base


def test_instrument_broad_command_rewrites_and_preserves_glob(tmp_path: Path) -> None:
    from scripts.mutation_coverage_producer import instrument_broad_command

    data_file = tmp_path / ".mutation-coverage"
    broad = "pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py"
    out = instrument_broad_command(broad, data_file)
    assert out.startswith("python3 -m coverage run --data-file ")
    # the glob and the rest of the args survive verbatim so bash still expands them
    assert out.endswith(
        "-m pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py"
    )

    out2 = instrument_broad_command("python3 -m pytest tests", data_file)
    assert "coverage run" in out2 and out2.endswith("-m pytest tests")


def test_instrument_broad_command_rejects_non_pytest(tmp_path: Path) -> None:
    from scripts.mutation_coverage_producer import instrument_broad_command

    with pytest.raises(ValueError):
        instrument_broad_command("ruff check .", tmp_path / ".data")


def test_produce_broad_coverage_emits_json_and_marker(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod
    from scripts.mutation_changed_files_lib import changed_pool_fingerprint

    repo, base = _seed_repo(tmp_path)
    cov = repo / "reports" / "mutation" / "test-coverage.json"
    captured: dict = {}

    def fake_run(repo_root, command, phase):
        captured["command"] = command
        captured["phase"] = phase
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_combine(repo_root, rcfile, data_file, coverage_json, env, *, show_contexts):
        captured["show_contexts"] = show_contexts
        Path(coverage_json).write_text('{"files": {}}', encoding="utf-8")

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)

    result = prod.produce_broad_coverage(
        repo, "pytest -q tests", base_sha=base, coverage_json=cov, run_command=fake_run
    )

    assert "python3 -m coverage run" in captured["command"]  # instrumented, not plain
    assert captured["show_contexts"] is False  # lever A: no per-test contexts
    assert result["returncode"] == 0
    assert result["produced_mutation_coverage"] is True
    assert result["command"] == "pytest -q tests"  # original preserved for the proof cache
    marker = cov.with_name(cov.name + ".fingerprint")
    assert marker.is_file()
    assert marker.read_text(encoding="utf-8").strip() == changed_pool_fingerprint(repo, base)


def test_produce_broad_coverage_skips_emit_on_failure(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = _seed_repo(tmp_path)
    cov = repo / "reports" / "mutation" / "test-coverage.json"
    called = {"combine": False}

    def fake_run(repo_root, command, phase):
        return {"phase": phase, "command": command, "returncode": 1, "stdout": "", "stderr": "boom"}

    def fake_combine(*args, **kwargs):
        called["combine"] = True

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)

    result = prod.produce_broad_coverage(
        repo, "pytest -q tests", base_sha=base, coverage_json=cov, run_command=fake_run
    )

    assert result["returncode"] == 1
    assert result["produced_mutation_coverage"] is False
    assert called["combine"] is False  # no export when the broad pytest failed
    assert not cov.with_name(cov.name + ".fingerprint").is_file()


def test_execute_command_plan_routes_broad_to_producer(tmp_path: Path, monkeypatch) -> None:
    from scripts import slice_closeout_command_executor as ex

    broad = "pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py"
    plan = [("verify", "ruff check ."), ("verify", broad)]
    payload: dict = {"executed_commands": []}
    ran: list[str] = []
    produced: list[str] = []
    recorded: list[str] = []

    def fake_run(repo_root, command, phase):
        ran.append(command)
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_producer(repo_root, command, phase):
        produced.append(command)
        return {
            "phase": phase, "command": command, "returncode": 0,
            "stdout": "", "stderr": "", "produced_mutation_coverage": True,
        }

    def reuse_must_not_run(*args, **kwargs):
        raise AssertionError("reuse/block path must be bypassed in producer mode")

    monkeypatch.setattr(ex, "_maybe_reuse_or_block_broad", reuse_must_not_run)
    monkeypatch.setattr(ex, "_record_broad", lambda *args, **kwargs: recorded.append(args[2]))

    stop = ex.execute_command_plan(
        tmp_path, plan, payload,
        run_command=fake_run,
        collect_changed_paths=lambda repo_root: [],
        refresh_broad_pytest_proof=False,
        broad_pytest_producer=fake_producer,
    )

    assert stop is False
    assert ran == ["ruff check ."]   # ordinary command -> run_command
    assert produced == [broad]       # broad pytest -> producer
    assert recorded == [broad]       # proof still recorded for the broad command
    assert payload["executed_commands"][-1]["produced_mutation_coverage"] is True


def test_changed_pool_files_vs_base_empty_base_is_empty(tmp_path: Path) -> None:
    # No base SHA -> no changed-pool set (the workflow_dispatch / first-push case).
    from scripts.mutation_changed_files_lib import changed_pool_files_vs_base

    assert changed_pool_files_vs_base(tmp_path, "") == []


def test_clear_stale_coverage_data_removes_data_file_and_shards(tmp_path: Path) -> None:
    # The exists->unlink branch + the parallel-shard glob cleanup before a fresh
    # plain-coverage run (otherwise a prior run's data leaks into the verdict).
    from scripts.mutation_sampling_lib import clear_stale_coverage_data

    data_file = tmp_path / ".mutation-coverage"
    data_file.write_text("stale", encoding="utf-8")
    shard = tmp_path / ".mutation-coverage.host.1234"
    shard.write_text("stale-shard", encoding="utf-8")

    clear_stale_coverage_data(data_file)

    assert not data_file.exists()
    assert not shard.exists()


def test_safe_read_bytes_falls_back_for_unreadable_path(tmp_path: Path) -> None:
    # Covers the defensive `<absent>` branch the changed-line gate would otherwise
    # flag as an uncovered changed line in this pool file (fresh-eye REVISE fold).
    from scripts.mutation_changed_files_lib import _safe_read_bytes

    real = tmp_path / "real.py"
    real.write_text("x = 1\n", encoding="utf-8")
    assert _safe_read_bytes(real) == b"x = 1\n"
    assert _safe_read_bytes(tmp_path / "missing.py") == b"<absent>"


def test_default_mutation_base_sha_matches_merge_base(tmp_path: Path) -> None:
    from scripts.mutation_coverage_producer import default_mutation_base_sha

    repo, _base = _seed_repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", head)

    assert default_mutation_base_sha(repo) == head
    # graceful empty string when there is no origin/main to merge-base against
    plain = tmp_path / "plain"
    plain.mkdir()
    _git(plain, "init", "-q")
    assert default_mutation_base_sha(plain) == ""


def test_make_closeout_producer_binds_base_and_produces(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = _seed_repo(tmp_path)

    def fake_run(repo_root, command, phase):
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_combine(repo_root, rcfile, data_file, coverage_json, env, *, show_contexts):
        Path(coverage_json).write_text('{"files": {}}', encoding="utf-8")

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)

    producer = prod.make_closeout_producer(repo, fake_run, base_sha_resolver=lambda r: base)
    result = producer(repo, "pytest -q tests", "verify")

    assert result["produced_mutation_coverage"] is True
    marker = repo / "reports" / "mutation" / "test-coverage.json.fingerprint"
    assert marker.is_file()


def test_closeout_producer_or_error_branches(tmp_path: Path) -> None:
    from scripts.mutation_coverage_producer import (
        PRODUCE_REQUIRES_LOCK_ERROR,
        closeout_producer_or_error,
    )

    def run_command(repo_root, command, phase):  # never called in these branches
        raise AssertionError

    # not requested -> no producer, no error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(produce_mutation_coverage=False), tmp_path, run_command
    )
    assert producer is None and error is None

    # requested without the verification lock -> error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(produce_mutation_coverage=True, verification_lock=False, skip_broad_pytest=False),
        tmp_path, run_command,
    )
    assert producer is None and error == PRODUCE_REQUIRES_LOCK_ERROR

    # requested with --skip-broad-pytest (no broad run to instrument) -> error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(produce_mutation_coverage=True, verification_lock=True, skip_broad_pytest=True),
        tmp_path, run_command,
    )
    assert producer is None and error == PRODUCE_REQUIRES_LOCK_ERROR

    # requested and valid -> a callable producer, no error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(produce_mutation_coverage=True, verification_lock=True, skip_broad_pytest=False),
        tmp_path, run_command,
    )
    assert callable(producer) and error is None


def test_resolve_broad_producer_raises_on_misuse() -> None:
    # In-process (no subprocess boundary): the closeout misuse guard raises
    # SurfaceError, which the entrypoint reports + exits non-zero on.
    import scripts.run_slice_closeout as rsc

    args = SimpleNamespace(
        produce_mutation_coverage=True, verification_lock=False, skip_broad_pytest=False
    )
    with pytest.raises(rsc.SurfaceError, match="requires --verification-lock"):
        rsc._resolve_broad_producer(args, ROOT, run_command=lambda *a, **k: None)


def test_resolve_broad_producer_none_when_not_producing() -> None:
    import scripts.run_slice_closeout as rsc

    args = SimpleNamespace(produce_mutation_coverage=False)
    assert rsc._resolve_broad_producer(args, ROOT, run_command=lambda *a, **k: None) is None


def test_resolve_broad_producer_returns_callable_when_valid() -> None:
    import scripts.run_slice_closeout as rsc

    args = SimpleNamespace(
        produce_mutation_coverage=True, verification_lock=True, skip_broad_pytest=False
    )
    producer = rsc._resolve_broad_producer(args, ROOT, run_command=lambda *a, **k: None)
    assert callable(producer)
