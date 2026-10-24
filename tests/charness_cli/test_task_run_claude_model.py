"""Claude model selection survives planning, execution and receipt projection."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.task_run import task_run_claude_review as review
from scripts.task_run import task_run_claude_sandbox as sandbox
from scripts.task_run import task_run_contract as contract
from scripts.task_run import task_run_lane_runner as runner
from scripts.task_run import task_run_detach as detach


@pytest.mark.parametrize("requested,expected", [(None, "sonnet"), ("haiku", "claude-haiku-5-5"), ("sonnet", "sonnet")])
def test_claude_model_parameter_reaches_command_and_result(tmp_path: Path, monkeypatch, requested, expected) -> None:
    monkeypatch.setattr(sandbox, "configure_claude_environment", lambda *_a: {})
    monkeypatch.setattr(sandbox, "_prepare_git", lambda *_a: None)
    monkeypatch.setattr(sandbox, "_settings", lambda *_a: tmp_path / "settings.json")
    monkeypatch.setattr(sandbox, "sandbox_prefix", lambda *_a: ["bwrap"])
    selected = contract.resolve_claude_model(requested)
    command = sandbox.build_claude_command("claude", tmp_path / "lane", tmp_path / "runtime", model=selected)
    payload = {}
    runner.record_lane_runner(payload, executor="claude", executable="claude", effort="medium", timeout_seconds=None, claude_model=selected)
    assert command[command.index("--model") + 1] == expected
    assert payload["executor"]["model"] == expected


def test_unsupported_claude_model_is_an_input_error() -> None:
    with pytest.raises(contract.TaskRunError, match="claude-model"):
        contract.resolve_claude_model("unselected")


@pytest.mark.parametrize("owner", ["claude", "reviewer"])
def test_auxiliary_session_writes_cannot_reach_operator_home(tmp_path: Path, monkeypatch, owner: str) -> None:
    """Poison ambient destinations; every session writer must use private state."""
    home, runtime, lane = tmp_path / "operator", tmp_path / "runtime", tmp_path / "lane"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    names = {"CODEX_HOME": ".codex", "CLAUDE_CONFIG_DIR": ".claude", "CEAL_HOME": ".ceal", "XDG_STATE_HOME": ".local/state"}
    inherited = {"HOME": str(home), "BASH_ENV": str(home / ".bashrc"), "ENV": str(home / ".profile"), "ZDOTDIR": str(home)}
    inherited.update({key: str(home / suffix) for key, suffix in names.items()})
    configured = (sandbox.configure_claude_environment(inherited, lane, runtime) if owner == "claude" else review.private_review_environment(inherited, runtime))
    for name in ("HOME", *names):
        destination = Path(configured[name])
        assert destination.is_relative_to(runtime), name
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "session-fixture").write_text("private")
    for filename in (".bashrc", ".zshrc", ".profile"):
        (Path(configured["HOME"]) / filename).write_text("private")
    assert not {"BASH_ENV", "ENV", "ZDOTDIR"} & configured.keys()
    assert not list(home.iterdir())


def test_model_survives_task_planning_and_detached_argv(tmp_path: Path, monkeypatch) -> None:
    import argparse
    from scripts.task_run import task_run, task_run_plan
    from .test_task_run_fixtures import _repo

    repo = _repo(tmp_path)
    monkeypatch.setattr(task_run_plan, "resolve_executor_executable", lambda *_a, **_k: "/fake/claude")
    payload = task_run.run_task(repo, lane="model", scopes=["module.py"], prompt="update module", executor="claude", claude_model="haiku", effort="medium", dry_run=True, skip_prepare=True)
    assert payload["executor"]["model"] == "claude-haiku-5-5", payload
    args = argparse.Namespace(scope=["module.py"], prompt="change module", prompt_file=None, executor="muse,claude", effort="medium", claude_model="haiku")
    argv = detach._prompt_argv(args)
    assert argv[argv.index("--claude-model") + 1] == "haiku"


def test_lane_command_uses_selected_model(tmp_path: Path, monkeypatch) -> None:
    seen = {}
    def build(_executable, **kwargs):
        seen.update(kwargs)
        return ["claude"]
    monkeypatch.setattr(sandbox, "build_claude_command", build)
    runner.lane_command(executor="claude", executable="claude", effort="medium", prompt="change", execution_runtime_path=tmp_path / "runtime", writable_dirs=[], worktree=tmp_path / "lane", claude_model="claude-haiku-5-5")
    assert seen["model"] == "claude-haiku-5-5"


def test_fallback_preserves_selected_claude_model(tmp_path: Path, monkeypatch) -> None:
    from scripts.task_run import task_run_attempts as attempts
    from scripts.task_run import task_run_support as support

    captured = {}
    monkeypatch.setattr(attempts._exec, "prepare_exec_environment", lambda *_a, **_k: {})
    monkeypatch.setattr(support, "scrubbed_lane_env", lambda _p, env, _e: env)
    def prepare(_payload, resolved, *_a, **_k):
        captured.update(resolved)
        return [], "prompt", ["claude", "--model", resolved["claude_model"]]
    monkeypatch.setattr(runner, "prepare_lane_execution", prepare)
    context = dict(claude_model="claude-haiku-5-5", effort="medium", timeout_seconds=None, target_path=tmp_path / "lane", execution_runtime_path=tmp_path / "runtime", git_worktree_dir=tmp_path / "git", prompt="change", require_change=True, scopes=["module.py"])
    payload = {}
    prepared = attempts._prepare_fallback_executor(payload, "claude", "claude", context)
    assert prepared["command"][-1] == "claude-haiku-5-5"
    assert captured["claude_model"] == payload["executor"]["model"] == "claude-haiku-5-5"
