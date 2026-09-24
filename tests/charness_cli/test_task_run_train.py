from __future__ import annotations

import os
import shlex
import subprocess
from types import SimpleNamespace
from pathlib import Path

import pytest
from scripts.task_run import task_run_train as train
from tests.quality_gates.repo_shapes import install_committed_repo
from .support import ROOT, run_cli_path


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    return install_committed_repo(tmp_path / "repo", {"base.txt": "base\n"}, branch="main")


def _branch(repo: Path, name: str, filename: str, contents: str) -> None:
    _git(repo, "switch", "--quiet", "-c", name, "main")
    (repo / filename).write_text(contents, encoding="utf-8")
    _git(repo, "add", filename)
    _git(
        repo,
        "-c",
        "user.name=Train Test",
        "-c",
        "user.email=train-test@example.com",
        "commit",
        "-m",
        name,
    )
    _git(repo, "switch", "--quiet", "main")


def _runtime(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", os.fspath(tmp_path / "runtime"))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)


def _provision_as_pass(monkeypatch) -> list[tuple[Path, dict[str, object]]]:
    calls: list[tuple[Path, dict[str, object]]] = []

    def prepare(path: Path, **kwargs):
        calls.append((path, kwargs))
        return {"status": train.PASS, "doctor": {"status": train.PASS}}

    monkeypatch.setattr(train._doctor, "run_prepare", prepare)
    return calls


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD")


def test_default_verify_profile_uses_standing_pytest_and_empty_baseline(tmp_path: Path) -> None:
    profile = train.load_verify_profile(tmp_path)

    assert profile["commands"][0]["id"] == "standing-pytest"
    assert profile["commands"][0]["argv"] == [
        "python3",
        "scripts/gates_support/run_standing_pytest.py",
        "--repo-root",
        ".",
    ]
    assert profile["commands"][0]["report"] == "junit-xml"
    assert profile["known_failures"] == []


def test_repo_verify_profile_override_is_loaded_and_validated(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    config = repo / ".agents" / "train-verify.yaml"
    config.parent.mkdir(parents=True)
    config.write_text(
        "version: 1\n"
        "commands:\n"
        "  - id: custom\n"
        "    argv:\n"
        "      - python3\n"
        "      - -c\n"
        "      - pass\n"
        "known_failures: []\n",
        encoding="utf-8",
    )

    assert train.load_verify_profile(repo)["commands"][0]["id"] == "custom"
    assert train.validate_verify_profile({"version": 1, "commands": [], "known_failures": []})


def test_train_subcommand_is_registered_on_root_cli() -> None:
    result = run_cli_path(ROOT / "charness", "train", "--help", cwd=ROOT)

    assert result.returncode == 0
    assert "usage: charness train" in result.stdout
    assert "branches" in result.stdout
    assert "--profile" in result.stdout


def test_train_cli_loads_runner_from_charness_for_profile_only_repo(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    _branch(repo, "lane/one", "one.txt", "one\n")
    _runtime(tmp_path, monkeypatch)
    profile = repo / ".agents" / "train-verify.yaml"
    profile.parent.mkdir()
    profile.write_text(
        "version: 1\n"
        "commands:\n"
        "  - id: consumer-check\n"
        "    argv:\n"
        "      - python3\n"
        "      - -c\n"
        "      - pass\n"
        "known_failures: []\n",
        encoding="utf-8",
    )

    result = run_cli_path(
        ROOT / "charness",
        "train",
        "--repo-root",
        str(repo),
        "lane/one",
        cwd=repo,
    )

    assert result.returncode == 1
    assert "decision: refused" in result.stdout
    assert "worktree prepare/doctor failed" in result.stdout
    assert "No module named" not in result.stderr


def test_junit_known_failure_baseline_allows_only_listed_testcases(
    tmp_path: Path, monkeypatch
) -> None:
    testcase = "tests.test_legacy::test_known"
    observed = {"name": "test_known"}
    exit_code = {"value": 1}
    monkeypatch.setattr(
        train,
        "configure_runtime_environment",
        lambda _worktree, env: env,
    )

    def run_phase(_command, *, env, **_kwargs):
        options = shlex.split(env["PYTEST_ADDOPTS"])
        report = Path(options[options.index("--junitxml") + 1])
        report.write_text(
            "<testsuites><testsuite><testcase classname='tests.test_legacy' "
            f"name='{observed['name']}'><failure/></testcase></testsuite></testsuites>",
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=exit_code["value"], stdout="", stderr="")

    monkeypatch.setattr(train._guard, "run_monitored_phase", run_phase)
    profile = {
        "version": 1,
        "commands": [{"id": "pytest", "argv": ["pytest"], "report": "junit-xml"}],
        "known_failures": [{"command_id": "pytest", "testcase": testcase}],
    }
    good, results = train.run_verify_profile(profile, tmp_path, tmp_path / "reports")
    assert good is True
    assert results[0]["known_failures"] == [testcase]

    exit_code["value"] = 124
    good, results = train.run_verify_profile(profile, tmp_path, tmp_path / "reports")
    assert good is False
    assert results[0]["timed_out"] is False

    observed["name"] = "test_new"
    exit_code["value"] = 1
    good, results = train.run_verify_profile(profile, tmp_path, tmp_path / "reports")
    assert good is False
    assert results[0]["new_failures"] == ["tests.test_legacy::test_new"]


def test_green_train_verifies_once_and_lands_multiple_branches(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    _branch(repo, "lane/one", "one.txt", "one\n")
    _branch(repo, "lane/two", "two.txt", "two\n")
    _runtime(tmp_path, monkeypatch)
    provision_calls = _provision_as_pass(monkeypatch)
    verify_calls: list[Path] = []

    def verify(_profile, worktree: Path, _report_root: Path):
        verify_calls.append(worktree)
        return True, [{"command_id": "stub", "status": train.PASS}]

    monkeypatch.setattr(train, "run_verify_profile", verify)
    base = _head(repo)
    result = train.run_train(repo, ["lane/one", "lane/two"])

    assert result["status"] == train.PASS
    assert result["decision"] == "land"
    assert result["landed_branches"] == ["lane/one", "lane/two"]
    assert result["requeue_branches"] == []
    assert len(verify_calls) == 1
    assert len(provision_calls) == 1
    assert provision_calls[0][1]["force"] is True
    assert provision_calls[0][1]["require_isolation"] is True
    assert _head(repo) != base
    assert (repo / "one.txt").is_file() and (repo / "two.txt").is_file()


def test_red_train_names_first_bad_branch_and_lands_green_prefix(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    _branch(repo, "lane/one", "one.txt", "one\n")
    _branch(repo, "lane/two", "two.txt", "two\n")
    _branch(repo, "lane/bad", "bad.txt", "bad\n")
    _branch(repo, "lane/four", "four.txt", "four\n")
    _runtime(tmp_path, monkeypatch)
    _provision_as_pass(monkeypatch)
    verified_prefixes: list[int] = []

    def verify(_profile, worktree: Path, _report_root: Path):
        count = sum(
            (worktree / name).exists()
            for name in ("one.txt", "two.txt", "bad.txt", "four.txt")
        )
        verified_prefixes.append(count)
        return not (worktree / "bad.txt").exists(), []

    monkeypatch.setattr(train, "run_verify_profile", verify)
    result = train.run_train(repo, ["lane/one", "lane/two", "lane/bad", "lane/four"])

    assert result["status"] == train.FAIL
    assert result["decision"] == "land-prefix"
    assert result["first_bad_branch"] == "lane/bad"
    assert result["landed_branches"] == ["lane/one", "lane/two"]
    assert result["requeue_branches"] == ["lane/bad", "lane/four"]
    assert verified_prefixes == [4, 2, 3]
    assert (repo / "one.txt").is_file() and (repo / "two.txt").is_file()
    assert not (repo / "bad.txt").exists() and not (repo / "four.txt").exists()


def test_main_move_during_verification_refuses_land_and_returns_requeue(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    _branch(repo, "lane/one", "one.txt", "one\n")
    _runtime(tmp_path, monkeypatch)
    _provision_as_pass(monkeypatch)
    base = _head(repo)
    calls = 0

    def verify(_profile, _worktree: Path, _report_root: Path):
        nonlocal calls
        calls += 1
        (repo / "concurrent.txt").write_text("main moved\n", encoding="utf-8")
        _git(repo, "add", "concurrent.txt")
        _git(
            repo,
            "-c",
            "user.name=Train Test",
            "-c",
            "user.email=train-test@example.com",
            "commit",
            "-m",
            "move main during verification",
        )
        return True, []

    monkeypatch.setattr(train, "run_verify_profile", verify)
    result = train.run_train(repo, ["lane/one"])

    assert result["status"] == train.FAIL
    assert result["decision"] == "requeue"
    assert result["reason"] == "main-moved"
    assert result["requeue_branches"] == ["lane/one"]
    assert calls == 1
    assert _head(repo) != base
    assert not (repo / "one.txt").exists()


def test_failed_provisioning_refuses_verification_on_stale_tree(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    _branch(repo, "lane/one", "one.txt", "one\n")
    _runtime(tmp_path, monkeypatch)
    provision_calls: list[tuple[Path, dict[str, object]]] = []
    verify_calls: list[Path] = []

    def prepare(path: Path, **kwargs):
        provision_calls.append((path, kwargs))
        return {"status": train.FAIL, "next_step": "repair install"}

    monkeypatch.setattr(train._doctor, "run_prepare", prepare)
    monkeypatch.setattr(
        train,
        "run_verify_profile",
        lambda _profile, worktree, _report: (verify_calls.append(worktree) or True, []),
    )
    base = _head(repo)
    result = train.run_train(repo, ["lane/one"])

    assert result["status"] == train.FAIL
    assert result["decision"] == "refused"
    assert "prepare/doctor failed" in result["error"]
    assert len(provision_calls) == 1
    assert provision_calls[0][1]["force"] is True
    assert provision_calls[0][1]["require_isolation"] is True
    assert verify_calls == []
    assert _head(repo) == base


def test_decision_core_selects_midpoint_then_prefix_land_without_io() -> None:
    queue = ["lane/a", "lane/b", "lane/c", "lane/d"]

    first = train.decide_next_action(
        queue, {0: True, 4: False}, main_at_start="base", main_now="base"
    )
    last = train.decide_next_action(
        queue, {0: True, 4: False, 2: True, 3: False},
        main_at_start="base", main_now="base",
    )

    assert first == {
        "action": "verify-prefix",
        "reason": None,
        "prefix_count": 2,
        "land_count": 0,
        "first_bad_branch": None,
        "landed_branches": [],
        "requeue_branches": queue,
    }
    assert last["action"] == "land-prefix"
    assert last["first_bad_branch"] == "lane/c"
    assert last["landed_branches"] == queue[:2]
    assert last["requeue_branches"] == queue[2:]


def test_decision_core_refuses_non_monotonic_prefix_outcomes() -> None:
    with pytest.raises(train.TrainError, match="non-monotonic"):
        train.decide_next_action(
            ["lane/a", "lane/b", "lane/c"],
            {0: True, 1: False, 2: True, 3: True},
            main_at_start="base",
            main_now="base",
        )
