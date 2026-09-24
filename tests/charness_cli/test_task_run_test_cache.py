from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.task_run import task_run_test_cache as cache
from scripts.task_run import task_run_train as train


def _profile(test_file: str) -> dict[str, object]:
    return {
        "version": 1,
        "commands": [
            {
                "id": "pytest",
                "argv": ["python3", "-m", "pytest", test_file],
                "report": "exit-code",
            }
        ],
        "known_failures": [],
    }


def _run_pair(
    tmp_path: Path, monkeypatch, *, source: str, dependency: str | None = None
) -> tuple[int, list[dict[str, object]]]:
    repo = tmp_path / "repo"
    test_file = repo / "tests" / "test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(source, encoding="utf-8")
    if dependency is not None:
        support = repo / "scripts" / "support.py"
        support.parent.mkdir(parents=True)
        support.write_text(dependency, encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(
        train,
        "configure_runtime_environment",
        lambda _worktree, env: env,
    )

    def run_phase(command, **_kwargs):
        calls.append(list(command))
        return SimpleNamespace(returncode=0, stdout="", stderr="", timed_out=False)

    monkeypatch.setattr(train._guard, "run_monitored_phase", run_phase)
    profile = _profile("tests/test_sample.py")
    runtime = tmp_path / "runtime"
    first_good, first = train.run_verify_profile(
        profile,
        repo,
        runtime / "train-runs" / "first" / "reports" / "verify",
    )
    assert cache.cached_green_outcome(
        runtime / "test-result-cache", repo, Path("tests/test_sample.py")
    ) is not None
    second_good, second = train.run_verify_profile(
        profile,
        repo,
        runtime / "train-runs" / "second" / "reports" / "verify",
    )
    assert first_good and second_good
    assert first[0]["status"] == second[0]["status"] == train.PASS
    return len(calls), [first[0], second[0]]


def test_matching_test_and_import_hashes_skip_verify_command(
    tmp_path: Path, monkeypatch
) -> None:
    calls, outcomes = _run_pair(tmp_path, monkeypatch, source="def test_sample(): pass\n")

    assert calls == 1
    assert outcomes[0]["command_id"] == outcomes[1]["command_id"] == "pytest"
    assert outcomes[1]["exit_code"] == 0


def test_test_content_change_runs_verify_command_again(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    test_file = repo / "tests" / "test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_sample(): pass\n", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(train, "configure_runtime_environment", lambda _root, env: env)
    monkeypatch.setattr(
        train._guard,
        "run_monitored_phase",
        lambda command, **_kwargs: (
            calls.append(list(command))
            or SimpleNamespace(returncode=0, stdout="", stderr="", timed_out=False)
        ),
    )
    profile = _profile("tests/test_sample.py")
    cache_root = tmp_path / "cache"
    train.run_verify_profile(profile, repo, tmp_path / "reports" / "first", cache_root=cache_root)
    test_file.write_text("def test_sample(): assert True\n", encoding="utf-8")

    good, results = train.run_verify_profile(
        profile, repo, tmp_path / "reports" / "second", cache_root=cache_root
    )

    assert good is True
    assert results[0]["status"] == train.PASS
    assert len(calls) == 2


def test_import_closure_change_invalidates_cached_test(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    test_file = repo / "tests" / "test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "from .support import VALUE\n"
        "from scripts.package import support as package_support\n"
        "import tests.helper\n"
        "import_repo_module(__file__, 'scripts.bad-name')\n",
        encoding="utf-8",
    )
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "conftest.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "support.py").write_text("VALUE = 1\n", encoding="utf-8")
    helper = repo / "tests" / "helper.py"
    helper.write_text("from scripts.support import VALUE\n", encoding="utf-8")
    support = repo / "scripts" / "support.py"
    support.parent.mkdir(parents=True)
    (support.parent / "__init__.py").write_text("", encoding="utf-8")
    support.write_text("from tests.helper import VALUE\nVALUE = 1\n", encoding="utf-8")
    package = repo / "scripts" / "package"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "support.py").write_text("VALUE = 1\n", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(train, "configure_runtime_environment", lambda _root, env: env)
    monkeypatch.setattr(
        train._guard,
        "run_monitored_phase",
        lambda command, **_kwargs: (
            calls.append(list(command))
            or SimpleNamespace(returncode=0, stdout="", stderr="", timed_out=False)
        ),
    )
    profile = _profile("tests/test_sample.py")
    cache_root = tmp_path / "cache"
    train.run_verify_profile(profile, repo, tmp_path / "reports" / "first", cache_root=cache_root)
    support.write_text("VALUE = 2\n", encoding="utf-8")

    good, results = train.run_verify_profile(
        profile, repo, tmp_path / "reports" / "second", cache_root=cache_root
    )

    assert good is True
    assert results[0]["status"] == train.PASS
    assert len(calls) == 2
    assert cache.file_hashes(repo, Path("tests/test_sample.py")) is not None


def test_standing_runner_filters_only_the_changed_file(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    tests = repo / "tests"
    tests.mkdir(parents=True)
    first = tests / "test_first.py"
    second = tests / "test_second.py"
    first.write_text("def test_first(): pass\n", encoding="utf-8")
    second.write_text("def test_second(): pass\n", encoding="utf-8")
    runner = repo / "scripts" / "gates_support" / "run_standing_pytest.py"
    runner.parent.mkdir(parents=True)
    runner.write_text(
        "import sys\n"
        "if '--print-expanded-targets' in sys.argv:\n"
        "    print('tests')\n"
        "    print('../outside/test_escape.py')\n",
        encoding="utf-8",
    )
    outside = tmp_path / "outside" / "test_escape.py"
    outside.parent.mkdir()
    outside.write_text("def test_escape(): pass\n", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(train, "configure_runtime_environment", lambda _root, env: env)
    monkeypatch.setattr(
        train._guard,
        "run_monitored_phase",
        lambda command, **_kwargs: (
            calls.append(list(command))
            or SimpleNamespace(returncode=0, stdout="", stderr="", timed_out=False)
        ),
    )
    profile = {
        "commands": [
            {
                "id": "standing-pytest",
                "argv": [sys.executable, "scripts/gates_support/run_standing_pytest.py", "--repo-root", "."],
                "report": "exit-code",
            }
        ],
        "known_failures": [],
    }
    cache_root = tmp_path / "cache"
    train.run_verify_profile(profile, repo, tmp_path / "reports" / "first", cache_root=cache_root)
    first.write_text("def test_first(): assert True\n", encoding="utf-8")

    good, results = train.run_verify_profile(
        profile, repo, tmp_path / "reports" / "second", cache_root=cache_root
    )
    train.run_verify_profile(profile, repo, tmp_path / "reports" / "third", cache_root=cache_root)

    assert good is True
    assert results[0]["status"] == train.PASS
    assert len(calls) == 2
    assert "--pytest-target" in calls[1]
    assert calls[1][calls[1].index("--pytest-target") + 1] == str(first)
    assert str(second) not in calls[1]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("result_kind", "failed"),
        ("exit_code", 1),
        ("verify_status", "fail"),
        ("verify_timed_out", True),
        ("verify_exit_code", 1),
        ("verify_known_failures", ["test::known"]),
        ("verify_new_failures", ["test::new"]),
        ("verify_outcome", "invalid"),
        ("path", "tests/other.py"),
        ("hashes", {}),
        ("raw_record", []),
    ],
)
def test_skip_requires_frozen_success_envelope(
    tmp_path: Path, monkeypatch, field: str, value: object
) -> None:
    repo = tmp_path / "repo"
    test_file = repo / "tests" / "test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_sample(): pass\n", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(train, "configure_runtime_environment", lambda _root, env: env)
    monkeypatch.setattr(
        train._guard,
        "run_monitored_phase",
        lambda command, **_kwargs: (
            calls.append(list(command))
            or SimpleNamespace(returncode=0, stdout="", stderr="", timed_out=False)
        ),
    )
    profile = _profile("tests/test_sample.py")
    cache_root = tmp_path / "cache"
    train.run_verify_profile(profile, repo, tmp_path / "reports" / "first", cache_root=cache_root)
    cache_file = next(cache_root.glob("*.json"))
    record = json.loads(cache_file.read_text(encoding="utf-8"))
    if field == "raw_record":
        cache_file.write_text(json.dumps(value), encoding="utf-8")
    elif field == "verify_outcome":
        record[field] = value
        cache_file.write_text(json.dumps(record), encoding="utf-8")
    elif field.startswith("verify_"):
        outcome_field = field.removeprefix("verify_")
        record["verify_outcome"][outcome_field] = value
        cache_file.write_text(json.dumps(record), encoding="utf-8")
    else:
        record[field] = value
        cache_file.write_text(json.dumps(record), encoding="utf-8")

    good, results = train.run_verify_profile(
        profile, repo, tmp_path / "reports" / "second", cache_root=cache_root
    )

    assert good is True
    assert results[0]["status"] == train.PASS
    assert len(calls) == 2


def test_failed_verify_outcome_is_never_cached(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    test_file = repo / "tests" / "test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_sample(): pass\n", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(train, "configure_runtime_environment", lambda _root, env: env)
    monkeypatch.setattr(
        train._guard,
        "run_monitored_phase",
        lambda command, **_kwargs: (
            calls.append(list(command))
            or SimpleNamespace(returncode=1, stdout="", stderr="failed", timed_out=False)
        ),
    )
    profile = _profile("tests/test_sample.py")
    cache_root = tmp_path / "cache"

    for index in range(2):
        good, results = train.run_verify_profile(
            profile, repo, tmp_path / "reports" / str(index), cache_root=cache_root
        )
        assert good is False
        assert results[0]["status"] == train.FAIL

    assert len(calls) == 2
    assert not list(cache_root.glob("*.json"))


def test_standing_target_query_and_unknown_commands_fall_back_to_execution(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    runner = repo / "scripts" / "gates_support" / "run_standing_pytest.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("pass\n", encoding="utf-8")
    monkeypatch.setattr(
        cache,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stdout="", stderr="failed"),
    )
    argv = [sys.executable, "scripts/gates_support/run_standing_pytest.py"]

    assert cache.cacheable_command(argv, repo) is None
    assert cache.prepare_verify(tmp_path / "cache", repo, "standing", argv) is None
    assert cache.prepare_verify(
        tmp_path / "cache", repo, "custom", ["python3", "-c", "pass"]
    ) is None


def test_direct_command_reruns_only_a_changed_test_file(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    tests = repo / "tests"
    tests.mkdir(parents=True)
    first = tests / "test_first.py"
    second = tests / "test_second.py"
    first.write_text("def test_first(): pass\n", encoding="utf-8")
    second.write_text("def test_second(): pass\n", encoding="utf-8")
    commands: list[list[str]] = []
    monkeypatch.setattr(train, "configure_runtime_environment", lambda _root, env: env)
    monkeypatch.setattr(
        train._guard,
        "run_monitored_phase",
        lambda command, **_kwargs: (
            commands.append(list(command))
            or SimpleNamespace(returncode=0, stdout="", stderr="", timed_out=False)
        ),
    )
    profile = {
        "commands": [
            {
                "id": "pytest",
                "argv": ["python3", "-m", "pytest", str(first), str(second)],
                "report": "exit-code",
            }
        ],
        "known_failures": [],
    }
    cache_root = tmp_path / "cache"
    train.run_verify_profile(profile, repo, tmp_path / "reports" / "first", cache_root=cache_root)
    first.write_text("def test_first(): assert True\n", encoding="utf-8")

    good, results = train.run_verify_profile(
        profile, repo, tmp_path / "reports" / "second", cache_root=cache_root
    )

    assert good is True
    assert results[0]["status"] == train.PASS
    assert len(commands) == 2
    assert str(first) in commands[1]
    assert str(second) not in commands[1]


def test_cache_writer_handles_syntax_and_atomic_write_failures(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    test_file = repo / "tests" / "test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_sample(): pass\n", encoding="utf-8")
    green = {
        "command_id": "pytest",
        "status": train.PASS,
        "exit_code": 0,
        "timed_out": False,
        "known_failures": [],
        "new_failures": [],
    }
    cache_root = tmp_path / "cache"
    test_file.write_text("def broken(\n", encoding="utf-8")

    assert cache.remember_green_outcome(cache_root, repo, test_file, green) is False
    test_file.write_text("def test_sample(): pass\n", encoding="utf-8")
    monkeypatch.setattr(
        cache.os,
        "replace",
        lambda *_args: (_ for _ in ()).throw(OSError("disk")),
    )
    original_unlink = Path.unlink

    def fail_cache_cleanup(path: Path, *args, **kwargs) -> None:
        if path.name.startswith(".test-cache-"):
            raise OSError("cleanup")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_cache_cleanup)

    assert cache.remember_green_outcome(cache_root, repo, test_file, green) is False
    assert not list(cache_root.glob("*.json"))
