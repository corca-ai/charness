"""Tests for the changed-line mutation-coverage closeout producer (Slice 2).

The producer instruments the closeout broad pytest with plain coverage (lever
A+B: drop dynamic_context, piggyback the run), exports a small coverage JSON, and
stamps the freshness fingerprint marker the pre-push consumer trusts.
"""
from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from .mutation_coverage_producer_fixtures import git as _git
from .mutation_coverage_producer_fixtures import seed_mutation_coverage_repo as _seed_repo


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

    runner = "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only"
    out3 = instrument_broad_command(runner, data_file)
    assert "coverage run" in out3
    assert out3.endswith("scripts/run_standing_pytest.py --repo-root . --mode read-only")

    focused_runner = runner + " --pytest-target tests/focused.py::test_one"
    focused_out = instrument_broad_command(focused_runner, data_file)
    assert focused_out.endswith(
        "scripts/run_standing_pytest.py --repo-root . --mode read-only "
        "--pytest-target tests/focused.py::test_one"
    )

    out4 = instrument_broad_command(
        runner,
        data_file,
        extra_pytest_targets=["tests/focused.py::test_one"],
    )
    assert "--extra-pytest-target tests/focused.py::test_one" in out4

    out5 = instrument_broad_command(
        "python3 -m pytest -q tests/quality_gates",
        data_file,
        extra_pytest_targets=["tests/focused.py::test_one"],
    )
    assert out5.endswith("-m pytest -q tests/quality_gates tests/focused.py::test_one")


def test_instrument_broad_command_rejects_non_pytest(tmp_path: Path) -> None:
    from scripts.mutation_coverage_producer import (
        instrument_broad_command,
        is_instrumentable_pytest_command,
        is_standing_pytest_runner_command,
    )

    with pytest.raises(ValueError):
        instrument_broad_command("ruff check .", tmp_path / ".data")
    helper = "python3 scripts/run_standing_pytest.py --repo-root . --print-targets"
    assert not is_instrumentable_pytest_command(helper)
    with pytest.raises(ValueError):
        instrument_broad_command(helper, tmp_path / ".data")
    assert is_standing_pytest_runner_command("python3 scripts/run_standing_pytest.py 'unterminated")


def test_standing_runner_child_process_reaches_coverage_json(tmp_path: Path) -> None:
    """The focused runner adds a subprocess boundary; prove coverage crosses it."""
    from scripts import mutation_coverage_producer as prod

    pytest.importorskip("xdist", reason="worker coverage probe requires pytest-xdist")
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "scripts" / "demo.py").write_text(
        "def answer():\n    return 42\n", encoding="utf-8"
    )
    test_source = (
        "import os\n"
        "from pathlib import Path\n\n"
        "from scripts.demo import answer\n\n"
        "def test_answer():\n"
        "    worker = os.environ.get('PYTEST_XDIST_WORKER', '')\n"
        "    assert worker.startswith('gw')\n"
        "    Path(__file__).parents[1].joinpath(f'worker-{worker}').write_text(worker)\n"
        "    assert answer() == 42\n"
    )
    (repo / "tests" / "test_demo_one.py").write_text(test_source, encoding="utf-8")
    (repo / "tests" / "test_demo_two.py").write_text(test_source, encoding="utf-8")
    coverage_json = repo / "coverage.json"
    data_file, rcfile, env = prod._sampling.prepare_plain_coverage(repo, coverage_json)
    runner = Path(__file__).resolve().parents[2] / "scripts" / "run_standing_pytest.py"
    command = prod.instrument_broad_command(
        f"python3 {runner} --repo-root {repo} --mode read-only "
            "--pytest-target tests/test_demo_one.py "
            "--pytest-target tests/test_demo_two.py",
        data_file,
    )

    env["CHARNESS_PYTEST_WORKERS"] = "2"
    result = subprocess.run(
        shlex.split(command), cwd=repo, env=env, check=False, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert len(list(repo.glob("worker-gw*"))) == 2
    prod._sampling.combine_and_export_coverage(
        repo, rcfile, data_file, coverage_json, env, show_contexts=False
    )

    covered = prod._sampling.load_covered_lines(repo, coverage_json)
    assert covered["scripts/demo.py"] >= {1, 2}


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
    assert result["mutation_coverage_base_sha"] == base
    assert result["mutation_coverage_json"] == str(cov)
    consumer_tokens = shlex.split(result["mutation_coverage_consumer_command"])
    assert consumer_tokens[:2] == [
        "python3",
        str(Path(prod.__file__).resolve().with_name("check_changed_line_mutation_coverage.py")),
    ]
    assert consumer_tokens[consumer_tokens.index("--base-sha") + 1] == base
    assert consumer_tokens[consumer_tokens.index("--coverage-json") + 1] == str(cov)
    assert consumer_tokens[consumer_tokens.index("--head-sha") + 1] == "HEAD"
    assert "--reuse-coverage" in consumer_tokens
    assert "--require-fresh-coverage" in consumer_tokens
    marker = cov.with_name(cov.name + ".fingerprint")
    assert marker.is_file()
    assert marker.read_text(encoding="utf-8").strip() == changed_pool_fingerprint(repo, base)


def test_produce_broad_coverage_appends_extra_pytest_targets(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = _seed_repo(tmp_path)
    cov = repo / "reports" / "mutation" / "test-coverage.json"
    captured: dict = {}

    def fake_run(repo_root, command, phase):
        captured["command"] = command
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_combine(repo_root, rcfile, data_file, coverage_json, env, *, show_contexts):
        Path(coverage_json).write_text('{"files": {}}', encoding="utf-8")

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)

    result = prod.produce_broad_coverage(
        repo,
        "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only",
        base_sha=base,
        coverage_json=cov,
        run_command=fake_run,
        extra_pytest_targets=["tests/focused.py::test_one"],
    )

    assert "--extra-pytest-target tests/focused.py::test_one" in captured["command"]
    assert result["mutation_coverage_extra_pytest_targets"] == ["tests/focused.py::test_one"]
    assert "--extra-pytest-target tests/focused.py::test_one" in result["instrumented_command"]


def test_produce_command_coverage_emits_json_and_marker(tmp_path: Path, monkeypatch) -> None:
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

    result = prod.produce_command_coverage(
        repo,
        "python3 -m pytest -q tests/quality_gates/test_mutation_coverage_producer.py",
        base_sha=base,
        coverage_json=cov,
        run_command=fake_run,
    )

    assert "python3 -m coverage run" in captured["command"]
    assert "tests/quality_gates/test_mutation_coverage_producer.py" in captured["command"]
    assert captured["show_contexts"] is False
    assert result["produced_mutation_coverage"] is True
    marker = cov.with_name(cov.name + ".fingerprint")
    assert marker.read_text(encoding="utf-8").strip() == changed_pool_fingerprint(repo, base)


def test_produce_command_coverage_can_export_only_requested_paths(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = _seed_repo(tmp_path)
    cov = repo / "reports" / "mutation" / "test-coverage.json"
    captured: dict = {}

    def fake_run(repo_root, command, phase):
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_combine(
        repo_root, rcfile, data_file, coverage_json, env, *, show_contexts, include_paths=None
    ):
        captured["show_contexts"] = show_contexts
        captured["include_paths"] = include_paths
        Path(coverage_json).write_text('{"files": {}}', encoding="utf-8")

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)

    prod.produce_command_coverage(
        repo,
        "python3 -m pytest -q tests/quality_gates/test_mutation_coverage_producer.py",
        base_sha=base,
        coverage_json=cov,
        run_command=fake_run,
        include_paths=["scripts/foo.py", "scripts/bar.py"],
    )

    assert captured == {
        "show_contexts": False,
        "include_paths": ["scripts/foo.py", "scripts/bar.py"],
    }


def test_combine_export_preserves_all_include_paths_in_coverage_argv(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_sampling_lib as sampling

    commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        commands.append(command)

    monkeypatch.setattr(sampling.subprocess, "run", fake_run)
    sampling.combine_and_export_coverage(
        tmp_path,
        tmp_path / "coverage.rc",
        tmp_path / ".coverage",
        tmp_path / "coverage.json",
        {},
        show_contexts=False,
        include_paths=["scripts/foo.py", "scripts/bar.py"],
    )

    json_command = commands[1]
    include_index = json_command.index("--include")
    assert json_command[include_index + 1] == "scripts/foo.py,scripts/bar.py"
    assert json_command.count("--include") == 1


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

    broad = "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only"
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


def test_make_closeout_producer_uses_explicit_campaign_base_once(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod
    from scripts.mutation_changed_files_lib import changed_pool_fingerprint

    repo, base = _seed_repo(tmp_path)
    explicit = _git(repo, "rev-parse", "HEAD~1")
    resolver_called = False

    def unexpected_default(_repo: Path) -> str:
        nonlocal resolver_called
        resolver_called = True
        raise AssertionError("explicit campaign base must not use origin/main default resolver")

    def fake_run(repo_root, command, phase):
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_combine(repo_root, rcfile, data_file, coverage_json, env, *, show_contexts):
        Path(coverage_json).write_text('{"files": {}}', encoding="utf-8")

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)
    producer = prod.make_closeout_producer(
        repo,
        fake_run,
        base_sha=explicit,
        base_sha_resolver=unexpected_default,
    )
    result = producer(repo, "pytest -q tests", "verify")

    assert result["produced_mutation_coverage"] is True
    marker = repo / "reports" / "mutation" / "test-coverage.json.fingerprint"
    assert marker.read_text(encoding="utf-8").strip() == changed_pool_fingerprint(repo, explicit)
    assert resolver_called is False


def test_closeout_producer_or_error_binds_explicit_campaign_base(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    captured: dict[str, object] = {}

    def fake_make(repo_root, run_command, **kwargs):
        captured.update(kwargs)
        return lambda *args: {"returncode": 0}

    monkeypatch.setattr(prod, "make_closeout_producer", fake_make)
    args = SimpleNamespace(
        produce_mutation_coverage=True,
        verification_lock=True,
        skip_broad_pytest=False,
        mutation_coverage_command=None,
    )

    producer, error = prod.closeout_producer_or_error(
        args, tmp_path, lambda *args: {"returncode": 0}, base_sha="campaign-sha"
    )

    assert callable(producer)
    assert error is None
    assert captured["base_sha"] == "campaign-sha"


def test_closeout_producer_or_error_branches(tmp_path: Path) -> None:
    from scripts.mutation_coverage_producer import (
        FOCUSED_REQUIRES_PRODUCE_ERROR,
        FOCUSED_REQUIRES_PYTEST_ERROR,
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

    # focused command without producer mode -> error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(
            produce_mutation_coverage=False,
            mutation_coverage_command="pytest -q tests/test_demo.py",
        ),
        tmp_path,
        run_command,
    )
    assert producer is None and error == FOCUSED_REQUIRES_PRODUCE_ERROR

    # focused command must be an instrumentable pytest command
    producer, error = closeout_producer_or_error(
        SimpleNamespace(
            produce_mutation_coverage=True,
            verification_lock=True,
            skip_broad_pytest=False,
            mutation_coverage_command="python3 scripts/not_pytest.py",
        ),
        tmp_path,
        run_command,
    )
    assert producer is None and error == FOCUSED_REQUIRES_PYTEST_ERROR

    # requested without the verification lock -> error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(
            produce_mutation_coverage=True,
            verification_lock=False,
            skip_broad_pytest=False,
            mutation_coverage_command=None,
        ),
        tmp_path, run_command,
    )
    assert producer is None and error == PRODUCE_REQUIRES_LOCK_ERROR

    # requested with --skip-broad-pytest (no broad run to instrument) -> error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(
            produce_mutation_coverage=True,
            verification_lock=True,
            skip_broad_pytest=True,
            mutation_coverage_command=None,
        ),
        tmp_path, run_command,
    )
    assert producer is None and error == PRODUCE_REQUIRES_LOCK_ERROR

    # requested and valid -> a callable producer, no error
    producer, error = closeout_producer_or_error(
        SimpleNamespace(
            produce_mutation_coverage=True,
            verification_lock=True,
            skip_broad_pytest=False,
            mutation_coverage_command=None,
        ),
        tmp_path, run_command,
    )
    assert callable(producer) and error is None

    # focused producer keeps broad pytest on the ordinary closeout/cache path
    producer, error = closeout_producer_or_error(
        SimpleNamespace(
            produce_mutation_coverage=True,
            verification_lock=True,
            skip_broad_pytest=False,
            mutation_coverage_command="pytest -q tests/test_demo.py",
        ),
        tmp_path,
        run_command,
    )
    assert producer is None and error is None


def test_run_focused_closeout_coverage_appends_result(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    payload = {"executed_commands": []}
    args = SimpleNamespace(
        produce_mutation_coverage=True,
        mutation_coverage_command="pytest -q tests/test_demo.py",
    )
    captured: dict = {}

    def fake_produce(repo_root, command, *, base_sha, coverage_json, run_command, phase):
        captured.update(
            {
                "repo_root": repo_root,
                "command": command,
                "base_sha": base_sha,
                "coverage_json": coverage_json,
                "phase": phase,
            }
        )
        return {
            "phase": phase,
            "command": command,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "produced_mutation_coverage": True,
        }

    monkeypatch.setattr(prod, "default_mutation_base_sha", lambda repo_root: "base")
    monkeypatch.setattr(prod, "produce_command_coverage", fake_produce)

    should_stop = prod.run_focused_closeout_coverage(
        args,
        tmp_path,
        payload,
        run_command=lambda *args, **kwargs: None,
    )

    assert should_stop is False
    assert captured["command"] == "pytest -q tests/test_demo.py"
    assert captured["base_sha"] == "base"
    assert captured["coverage_json"] == tmp_path / "reports" / "mutation" / "test-coverage.json"
    assert payload["executed_commands"][-1]["produced_mutation_coverage"] is True


def test_run_focused_closeout_coverage_uses_explicit_campaign_base(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    payload = {"executed_commands": []}
    args = SimpleNamespace(
        produce_mutation_coverage=True,
        mutation_coverage_command="pytest -q tests/test_demo.py",
    )
    captured: dict = {}

    def fake_produce(repo_root, command, *, base_sha, coverage_json, run_command, phase):
        captured["base_sha"] = base_sha
        return {
            "phase": phase,
            "command": command,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "produced_mutation_coverage": True,
        }

    monkeypatch.setattr(prod, "produce_command_coverage", fake_produce)
    monkeypatch.setattr(
        prod,
        "default_mutation_base_sha",
        lambda repo_root: (_ for _ in ()).throw(AssertionError("default resolver must not run")),
    )

    assert (
        prod.run_focused_closeout_coverage(
            args,
            tmp_path,
            payload,
            run_command=lambda *args, **kwargs: None,
            base_sha="campaign-sha",
        )
        is False
    )
    assert captured["base_sha"] == "campaign-sha"


def test_run_focused_closeout_coverage_skips_without_command(tmp_path: Path) -> None:
    from scripts import mutation_coverage_producer as prod

    payload = {"executed_commands": []}
    assert (
        prod.run_focused_closeout_coverage(
            SimpleNamespace(produce_mutation_coverage=True, mutation_coverage_command=None),
            tmp_path,
            payload,
            run_command=lambda *args, **kwargs: None,
        )
        is False
    )
    assert payload["executed_commands"] == []


def test_run_focused_closeout_coverage_marks_failed_payload(tmp_path: Path, monkeypatch) -> None:
    from scripts import mutation_coverage_producer as prod

    payload = {"executed_commands": []}
    args = SimpleNamespace(
        produce_mutation_coverage=True,
        mutation_coverage_command="pytest -q tests/test_demo.py",
    )

    def fake_produce(repo_root, command, *, base_sha, coverage_json, run_command, phase):
        return {
            "phase": phase,
            "command": command,
            "returncode": 1,
            "stdout": "",
            "stderr": "failed",
            "produced_mutation_coverage": False,
        }

    monkeypatch.setattr(prod, "default_mutation_base_sha", lambda repo_root: "base")
    monkeypatch.setattr(prod, "produce_command_coverage", fake_produce)

    should_stop = prod.run_focused_closeout_coverage(
        args,
        tmp_path,
        payload,
        run_command=lambda *args, **kwargs: None,
    )

    assert should_stop is True
    assert payload["status"] == "failed"
    assert payload["executed_commands"][-1]["returncode"] == 1


def test_explicit_campaign_base_marker_mismatch_is_detectable(tmp_path: Path, monkeypatch) -> None:
    from scripts import check_changed_line_mutation_coverage as consumer
    from scripts import mutation_coverage_producer as prod

    repo, base = _seed_repo(tmp_path)
    cov = repo / "reports" / "mutation" / "test-coverage.json"

    def fake_run(repo_root, command, phase):
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_combine(repo_root, rcfile, data_file, coverage_json, env, *, show_contexts):
        Path(coverage_json).write_text('{"files": {}}', encoding="utf-8")

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)
    prod.produce_command_coverage(
        repo,
        "pytest -q tests",
        base_sha=base,
        coverage_json=cov,
        run_command=fake_run,
    )
    marker = cov.with_name(cov.name + ".fingerprint")
    assert marker.is_file()
    consumer_args = SimpleNamespace(
        require_fresh_coverage=True,
        skip_if_no_coverage=False,
        coverage_json=cov,
    )
    # Producer and consumer agree when both use the explicit campaign SHA.
    assert consumer._coverage_source_skip(consumer_args, repo, cov, base, "HEAD") is None

    # A changed pool file rotates the consumer's recomputed fingerprint, so the
    # old marker is correctly rejected rather than treated as fresh coverage.
    (repo / "scripts" / "foo.py").write_text(
        "def a():\n    return 1\n\n\ndef b():\n    return 3\n", encoding="utf-8"
    )
    stale = consumer._coverage_source_skip(consumer_args, repo, cov, base, "HEAD")
    assert stale is not None
    assert "coverage source is stale" in stale["reason"]


def test_produced_consumer_command_reuses_exact_base_and_coverage_without_recollecting(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = _seed_repo(tmp_path)
    cov = repo / "reports" / "mutation" / "test-coverage.json"

    def fake_run(repo_root, command, phase):
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    def fake_combine(repo_root, rcfile, data_file, coverage_json, env, *, show_contexts):
        Path(coverage_json).write_text(
            json.dumps(
                {
                    "files": {
                        "scripts/foo.py": {
                            "executed_lines": [1, 2, 5, 6],
                            "missing_lines": [],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr(prod._sampling, "combine_and_export_coverage", fake_combine)
    produced = prod.produce_command_coverage(
        repo,
        "pytest -q tests",
        base_sha=base,
        coverage_json=cov,
        run_command=fake_run,
    )

    command = produced["mutation_coverage_consumer_command"]
    tokens = shlex.split(command)
    assert tokens[tokens.index("--base-sha") + 1] == produced["mutation_coverage_base_sha"]
    assert tokens[tokens.index("--coverage-json") + 1] == produced["mutation_coverage_json"]
    assert "--reuse-coverage" in tokens
    assert "--require-fresh-coverage" in tokens

    before_content = cov.read_bytes()
    before_mtime = cov.stat().st_mtime_ns
    result = subprocess.run(
        tokens,
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["base_sha"] == base
    assert payload["head_sha"] == "HEAD"
    assert payload["blocking"] == []
    assert cov.read_bytes() == before_content
    assert cov.stat().st_mtime_ns == before_mtime
