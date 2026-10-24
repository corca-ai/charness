"""Claude's auxiliary Codex reviewer keeps home state private to the runtime."""

from __future__ import annotations

import json
import shutil
import stat
import sys
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


@pytest.mark.parametrize("executor", ["claude", "codex", "muse"])
def test_brief_critique_isolates_home_only_for_claude(
    tmp_path: Path, operator_home: Path, monkeypatch, executor: str
) -> None:
    execution_runtime = tmp_path / "execution"
    original_env = {"PATH": "/usr/bin", "HOME": str(operator_home)}
    exec_lib = import_repo_module(critique.__file__, "scripts.worktree.worktree_exec_lib")
    monkeypatch.setattr(task_run_runtime, "_resolve_codex", lambda _name: "/usr/bin/codex")
    monkeypatch.setattr(
        exec_lib, "prepare_exec_environment", lambda *_args, **_kwargs: dict(original_env)
    )
    monkeypatch.setattr(task_run_support, "scrubbed_lane_env", lambda _p, env, _e: env)
    observed = {}

    def execute(_command, **kwargs):
        observed.update(kwargs["configured_env"])
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
            "executor": executor,
        },
        prompt="Read the fixture contract.",
        premise_checks=[],
    )
    assert result["status"] == "completed"
    if executor == "claude":
        assert observed["HOME"] == str(review.reviewer_home(execution_runtime))
        assert Path(observed["CODEX_HOME"]).is_relative_to(execution_runtime)
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
