"""Tests for the release-owned changed-line mutation-coverage producer.

The producer instruments a focused pytest command with plain coverage, exports a
small coverage JSON, and stamps the producer-qualified freshness marker the
changed-line consumer trusts.
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.mutation.mutation_changed_files_lib import (
    changed_line_coverage_marker_path,
    read_changed_line_coverage_marker,
)

from .mutation_coverage_producer_fixtures import git as _git
from .mutation_coverage_producer_fixtures import seed_mutation_coverage_repo as _seed_repo


def test_instrument_broad_command_rewrites_and_preserves_glob(tmp_path: Path) -> None:
    from scripts.mutation.mutation_coverage_producer import instrument_broad_command

    data_file = tmp_path / ".mutation-coverage"
    broad = (
        "pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py"
    )
    out = instrument_broad_command(broad, data_file)
    # The interpreter is the caller's when the command names one, else the SAME
    # default the argv builder uses -- it was a hardcoded `python3` here until a
    # round-2 reviewer measured the two builders driving one accepted command
    # under two different interpreters (SC18).
    assert out.startswith(f"{shlex.quote(sys.executable)} -m coverage run --data-file ")
    # the glob and the rest of the args survive verbatim so bash still expands them
    assert out.endswith(
        "-m pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py"
    )

    out2 = instrument_broad_command("python3 -m pytest tests", data_file)
    assert "coverage run" in out2 and out2.endswith("-m pytest tests")

    runner = "python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only"
    out3 = instrument_broad_command(runner, data_file)
    assert "coverage run" in out3
    assert out3.endswith("scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only")

    focused_runner = runner + " --pytest-target tests/focused.py::test_one"
    focused_out = instrument_broad_command(focused_runner, data_file)
    assert focused_out.endswith(
        "scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only "
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
    from scripts.mutation.mutation_coverage_producer import (
        instrument_broad_command,
        is_instrumentable_pytest_command,
        is_standing_pytest_runner_command,
    )

    with pytest.raises(ValueError):
        instrument_broad_command("ruff check .", tmp_path / ".data")
    helper = "python3 scripts/gates_support/run_standing_pytest.py --repo-root . --print-targets"
    assert not is_instrumentable_pytest_command(helper)
    with pytest.raises(ValueError):
        instrument_broad_command(helper, tmp_path / ".data")
    assert is_standing_pytest_runner_command("python3 scripts/gates_support/run_standing_pytest.py 'unterminated")


@pytest.mark.boundary_contract(
    reason="prove the standing pytest runner's real child and xdist workers produce the coverage JSON consumed by mutation sampling"
)
def test_standing_runner_child_process_reaches_coverage_json(tmp_path: Path) -> None:
    """The focused runner adds a subprocess boundary; prove coverage crosses it."""
    from scripts.mutation import mutation_coverage_producer as prod

    pytest.importorskip("xdist", reason="worker coverage probe requires pytest-xdist")
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "scripts" / "demo.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
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
    runner = Path(__file__).resolve().parents[2] / "scripts" / "gates_support" / "run_standing_pytest.py"
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


def test_produce_command_coverage_emits_json_and_marker(tmp_path: Path, monkeypatch) -> None:
    from scripts.mutation import mutation_coverage_producer as prod
    from scripts.mutation.mutation_changed_files_lib import changed_pool_fingerprint

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
    marker = changed_line_coverage_marker_path(cov)
    assert read_changed_line_coverage_marker(marker) == changed_pool_fingerprint(repo, base)


def test_produce_command_coverage_can_export_only_requested_paths(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts.mutation import mutation_coverage_producer as prod

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


def test_combine_export_preserves_all_include_paths_in_coverage_argv(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts.mutation import mutation_sampling_lib as sampling

    commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(sampling, "run_process", fake_run)
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


def test_changed_pool_files_vs_base_empty_base_is_empty(tmp_path: Path) -> None:
    # No base SHA -> no changed-pool set (the workflow_dispatch / first-push case).
    from scripts.mutation.mutation_changed_files_lib import changed_pool_files_vs_base

    assert changed_pool_files_vs_base(tmp_path, "") == []


def test_clear_stale_coverage_data_removes_data_file_and_shards(tmp_path: Path) -> None:
    # The exists->unlink branch + the parallel-shard glob cleanup before a fresh
    # plain-coverage run (otherwise a prior run's data leaks into the verdict).
    from scripts.mutation.mutation_sampling_lib import clear_stale_coverage_data

    data_file = tmp_path / ".mutation-coverage"
    data_file.write_text("stale", encoding="utf-8")
    shard = tmp_path / ".mutation-coverage.host.1234"
    shard.write_text("stale-shard", encoding="utf-8")

    clear_stale_coverage_data(data_file)

    assert not data_file.exists()
    assert not shard.exists()


def test_safe_read_bytes_falls_back_for_unreadable_path(tmp_path: Path) -> None:
    # Covers the defensive `<absent>` branch the changed-line gate would otherwise
    # flag as an uncovered changed line in this pool file.
    from scripts.mutation.mutation_changed_files_lib import _safe_read_bytes

    real = tmp_path / "real.py"
    real.write_text("x = 1\n", encoding="utf-8")
    assert _safe_read_bytes(real) == b"x = 1\n"
    assert _safe_read_bytes(tmp_path / "missing.py") == b"<absent>"


@pytest.mark.boundary_contract(
    reason="exercise default mutation-base discovery against real git refs created for the fixture"
)
def test_default_mutation_base_sha_matches_merge_base(tmp_path: Path) -> None:
    from scripts.mutation.mutation_coverage_producer import default_mutation_base_sha

    repo, _base = _seed_repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", head)

    assert default_mutation_base_sha(repo) == head
    # graceful empty string when there is no origin/main to merge-base against
    plain = tmp_path / "plain"
    plain.mkdir()
    _git(plain, "init", "-q")
    assert default_mutation_base_sha(plain) == ""


def test_explicit_campaign_base_marker_mismatch_is_detectable(tmp_path: Path, monkeypatch) -> None:
    from scripts.mutation import check_changed_line_mutation_coverage as consumer
    from scripts.mutation import mutation_coverage_producer as prod

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
    marker = changed_line_coverage_marker_path(cov)
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


def test_every_key_the_subprocess_env_sets_is_exported_to_the_child() -> None:
    """The producer re-exports `_COVERAGE_ENV_KEYS` and ONLY those.

    A key that `coverage_subprocess_env` assigns but the export list omits never
    reaches the pytest subprocess, so that subprocess writes its coverage
    somewhere `combine` does not look. `COVERAGE_FILE` was omitted exactly this
    way: every file in `release-changed-line-coverage`'s output read 0.0% except
    the one process `coverage run` wrapped directly, and a BLOCKING release gate
    was rendering verdicts on coverage data containing no test-suite execution.

    Asserted as containment over what the env owner actually assigns, not as the
    current tuple's literal contents -- pinning the literal would restate today's
    list and let the next added key fail the same silent way.
    """
    import os

    from scripts.mutation import mutation_coverage_producer as prod
    from scripts.mutation import mutation_sampling_lib as sampling

    baseline = dict(os.environ)
    produced = sampling.coverage_subprocess_env(
        Path("/tmp/rcfile"), Path("/tmp/sitecustomize"), data_file=Path("/tmp/data")
    )
    assigned = {key for key, value in produced.items() if baseline.get(key) != value}

    missing = sorted(assigned - set(prod._COVERAGE_ENV_KEYS))
    assert not missing, (
        f"coverage_subprocess_env assigns {missing} but _COVERAGE_ENV_KEYS does not "
        "export them, so the pytest subprocess never receives them."
    )
