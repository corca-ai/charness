"""Claude's auxiliary Codex reviewer keeps home state private to the runtime."""

from __future__ import annotations

import json
import shutil
import stat
import sys
import tempfile
from pathlib import Path

import pytest

from scripts.core.subprocess_guard import run_process
from scripts.runtime_bootstrap import import_repo_module
from scripts.task_run import task_run_brief_critique as critique
from scripts.task_run import task_run_claude_review as review
from scripts.task_run import task_run_claude_sandbox as sandbox
from scripts.task_run import task_run_execution, task_run_runtime, task_run_support


@pytest.fixture
def operator_home(tmp_path: Path, monkeypatch) -> Path:
    home = tmp_path / "operator"
    source = home / ".codex"
    source.mkdir(parents=True)
    (source / "auth.json").write_text('{"token":"fixture-only"}', encoding="utf-8")
    (source / "config.toml").write_text('model = "do-not-inherit"', encoding="utf-8")
    (source / "sessions").mkdir()
    (source / "sessions/existing.jsonl").write_text("fixture", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: home)
    return home


@pytest.mark.parametrize("env_auth", [False, True])
def test_private_review_home_inherits_only_needed_auth(
    tmp_path: Path, operator_home: Path, env_auth: bool
) -> None:
    runtime = tmp_path / "runtime"
    env = {
        "HOME": str(operator_home),
        "BASH_ENV": "unsafe",
        "ENV": "unsafe",
        "ZDOTDIR": str(operator_home),
    }
    if env_auth:
        env["OPENAI_API_KEY"] = "environment-fixture"
    isolated = review.private_review_environment(env, runtime)
    home = review.reviewer_home(runtime)
    for name in (
        "HOME",
        "CODEX_HOME",
        "XDG_CONFIG_HOME",
        "XDG_CACHE_HOME",
        "XDG_STATE_HOME",
        "TMPDIR",
        "TMP",
        "TEMP",
    ):
        assert Path(isolated[name]).is_relative_to(home)
    assert not {"BASH_ENV", "ENV", "ZDOTDIR"} & isolated.keys()
    assert stat.S_IMODE(home.stat().st_mode) == 0o700
    auth = Path(isolated["CODEX_HOME"]) / "auth.json"
    assert auth.exists() is not env_auth
    if not env_auth:
        assert auth.read_bytes() == (operator_home / ".codex/auth.json").read_bytes()
        assert stat.S_IMODE(auth.stat().st_mode) == 0o600
        repeated = review.private_review_environment(isolated, runtime)
        assert Path(repeated["CODEX_HOME"]) == auth.parent
        assert auth.read_bytes() == (operator_home / ".codex/auth.json").read_bytes()
    assert not (Path(isolated["CODEX_HOME"]) / "config.toml").exists()
    assert not (Path(isolated["CODEX_HOME"]) / "sessions").exists()
    assert (operator_home / ".codex/config.toml").read_text() == 'model = "do-not-inherit"'
    assert env["HOME"] == str(operator_home)


@pytest.mark.parametrize("executor", ["claude", "codex", "muse", "muse,claude"])
def test_brief_critique_isolates_home_only_for_claude(
    tmp_path: Path, operator_home: Path, monkeypatch, executor: str
) -> None:
    execution_runtime = tmp_path / "execution"
    original_env = {"PATH": "/usr/bin", "HOME": str(operator_home)}
    state_names = {"CODEX_HOME": ".codex", "CLAUDE_CONFIG_DIR": ".claude", "CEAL_HOME": ".ceal", "XDG_STATE_HOME": ".local/state"}
    original_env.update({key: str(operator_home / suffix) for key, suffix in state_names.items()})
    before = {path.relative_to(operator_home): path.read_bytes() for path in operator_home.rglob("*") if path.is_file()}
    exec_lib = import_repo_module(critique.__file__, "scripts.worktree.worktree_exec_lib")
    monkeypatch.setattr(task_run_runtime, "_resolve_codex", lambda _name: "/usr/bin/codex")
    monkeypatch.setattr(
        exec_lib, "prepare_exec_environment", lambda *_args, **_kwargs: dict(original_env)
    )
    monkeypatch.setattr(task_run_support, "scrubbed_lane_env", lambda _p, env, _e: env)
    observed = {}
    copies = []

    def execute(_command, **kwargs):
        observed.update(kwargs["configured_env"])
        copies.append((Path(kwargs["configured_env"]["CODEX_HOME"]) / "auth.json").is_file())
        if "claude" in executor.split(","):
            for name in state_names:
                destination = Path(observed[name])
                destination.mkdir(parents=True, exist_ok=True)
                (destination / "session-fixture").write_text("private")
        kwargs["stdout_log"].write_text(
            json.dumps({"premise_failure": False, "findings": [], "premise_checks": []})
        )
        return {"exit_code": 0, "timed_out": False}

    monkeypatch.setattr(task_run_execution, "_execute_codex", execute)
    result = critique._run_brief_critique(
        payload={"task_id": "lane", "execution_runtime_root": str(execution_runtime)},
        resolved={
            "runtime_path": tmp_path / "runtime",
            "target_path": tmp_path,
            "executor": executor.split(",")[0],
            "executor_order": executor.split(","),
        },
        prompt="Read the fixture contract.",
        premise_checks=[],
    )
    assert result["status"] == "completed"
    if "claude" in executor.split(","):
        assert observed["HOME"] == str(review.reviewer_home(execution_runtime))
        assert copies == [True]
        assert not (review.reviewer_home(execution_runtime) / ".codex/auth.json").exists()
        for name in state_names:
            assert Path(observed[name]).is_relative_to(execution_runtime)
        after = {path.relative_to(operator_home): path.read_bytes() for path in operator_home.rglob("*") if path.is_file()}
        assert after == before
    else:
        assert observed == original_env
        assert not review.reviewer_home(execution_runtime).exists()


@pytest.mark.boundary_contract(
    reason="The actual post-grant OS mask must hide the reviewer's copied auth from Claude commands"
)
def test_later_claude_cannot_read_private_review_auth(tmp_path: Path, operator_home: Path) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    worktree, runtime = tmp_path / "lane", tmp_path / "runtime"
    worktree.mkdir()
    env = review.private_review_environment({"PATH": "/usr/bin"}, runtime)
    auth = Path(env["CODEX_HOME"]) / "auth.json"
    assert auth.is_file()
    script = (
        "from pathlib import Path\n"
        f"auth = Path({str(auth)!r})\n"
        "try:\n auth.read_bytes()\n"
        "except (FileNotFoundError, PermissionError):\n pass\n"
        "else:\n raise AssertionError('review authentication escaped the OS mask')\n"
        "Path('inside.txt').write_text('allowed')\n"
        "print('review-auth=hidden inside-write=allowed')\n"
    )
    result = run_process(
        [*sandbox.sandbox_prefix(worktree, runtime), "--", sys.executable, "-c", script],
        cwd=worktree,
        env={"PATH": "/usr/bin"},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "review-auth=hidden inside-write=allowed"
    assert auth.read_bytes() == (operator_home / ".codex/auth.json").read_bytes()


def _run_claude_preflight(monkeypatch, operator_home: Path, execution_runtime: Path, target: Path, execute) -> dict:
    env = {"PATH": "/usr/bin", "HOME": str(operator_home), "CODEX_HOME": str(operator_home / ".codex")}
    exec_lib = import_repo_module(critique.__file__, "scripts.worktree.worktree_exec_lib")
    monkeypatch.setattr(task_run_runtime, "_resolve_codex", lambda _name: "/usr/bin/codex")
    monkeypatch.setattr(exec_lib, "prepare_exec_environment", lambda *_args, **_kwargs: dict(env))
    monkeypatch.setattr(task_run_support, "scrubbed_lane_env", lambda _p, child, _e: child)
    monkeypatch.setattr(task_run_execution, "_execute_codex", execute)
    return critique._run_brief_critique(
        payload={"task_id": "lane", "execution_runtime_root": str(execution_runtime)},
        resolved={"runtime_path": target / "runtime", "target_path": target,
                  "executor": "claude", "executor_order": ["claude"]},
        prompt="Read the fixture contract.",
        premise_checks=[],
    )


def test_preflight_deletes_the_auth_copy_when_the_review_fails(
    tmp_path: Path, operator_home: Path, monkeypatch
) -> None:
    execution_runtime = tmp_path / "execution"
    copy = review.reviewer_home(execution_runtime) / ".codex" / "auth.json"
    during = []

    def execute(_command, **_kwargs):
        during.append(copy.is_file())
        raise RuntimeError("review crashed")

    with pytest.raises(RuntimeError, match="review crashed"):
        _run_claude_preflight(monkeypatch, operator_home, execution_runtime, tmp_path, execute)
    assert during == [True]
    assert not copy.exists()


def test_preflight_deletes_a_partial_auth_copy_when_setup_fails(
    tmp_path: Path, operator_home: Path, monkeypatch
) -> None:
    execution_runtime = tmp_path / "execution"
    copy = review.reviewer_home(execution_runtime) / ".codex" / "auth.json"
    reviews = []

    def interrupted_copy(_source, destination) -> None:
        destination.write(b'{"token":')
        destination.flush()
        assert copy.is_file()
        raise OSError("disk full")

    monkeypatch.setattr(review.shutil, "copyfileobj", interrupted_copy)
    with pytest.raises(OSError, match="disk full"):
        _run_claude_preflight(
            monkeypatch, operator_home, execution_runtime, tmp_path,
            lambda *_args, **_kwargs: reviews.append("ran"),
        )
    assert reviews == []
    assert not copy.exists()


@pytest.mark.boundary_contract(
    reason="A finished preflight must leave no Codex credential another Claude lane can read"
)
@pytest.mark.parametrize("parent", ["/tmp", "/var/tmp"])
def test_other_claude_lanes_cannot_read_a_finished_preflights_auth(
    operator_home: Path, monkeypatch, parent: str
) -> None:
    """Runtimes under one /tmp tree, or anywhere outside /tmp, are visible to other lanes."""
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    try:
        base = Path(tempfile.mkdtemp(prefix="charness-preflight-", dir=parent))
    except OSError:
        pytest.skip(f"{parent} is not writable")
    try:
        runtime_b, runtime_a = base / "task-run/B/runtime", base / "task-run/A/runtime"
        lane_a = base / "lane-a"
        lane_a.mkdir()
        copy = review.reviewer_home(runtime_b) / ".codex" / "auth.json"
        during = []

        def execute(_command, **kwargs):
            during.append(copy.is_file())
            kwargs["stdout_log"].write_text(
                json.dumps({"premise_failure": False, "findings": [], "premise_checks": []})
            )
            return {"exit_code": 0, "timed_out": False}

        result = _run_claude_preflight(monkeypatch, operator_home, runtime_b, base, execute)
        assert result["status"] == "completed"
        assert during == [True]
        probe = run_process(
            [*sandbox.sandbox_prefix(lane_a, runtime_a), "--", "cat", str(copy)],
            cwd=lane_a,
            env={"PATH": "/usr/bin"},
        )
        assert probe.returncode != 0
        assert "fixture-only" not in probe.stdout
    finally:
        shutil.rmtree(base, ignore_errors=True)
