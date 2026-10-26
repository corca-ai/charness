"""Final lane cache environment follows sandbox selection and explicit grants."""
from pathlib import Path
import sys
import pytest
from scripts.core.subprocess_guard import run_process
from scripts.task_run import task_run_runtime as runtime
from scripts.task_run import task_run_claude_sandbox as sandbox

@pytest.mark.parametrize("executor", ["codex", "claude", "muse"])
@pytest.mark.parametrize("granted", [False, True])
def test_go_paths_follow_final_xdg_cache(tmp_path, monkeypatch, executor, granted):
    worktree = tmp_path / "worktree"; worktree.mkdir()
    private = tmp_path / "runtime"; private.mkdir()
    shared = tmp_path / "shared"; shared.mkdir()
    monkeypatch.setattr(sandbox, "_shared_git_dir", lambda *_: None)
    env = dict(CHARNESS_RUNTIME_ROOT=str(private), XDG_CACHE_HOME=str(private / "cache"),
               CHARNESS_TASK_RUN_CACHE_HOME=str(shared), ANTHROPIC_API_KEY="fixture",
               GOCACHE=str(tmp_path / "config/go-build"), GOPATH=str(tmp_path / "config/go"),
               GOMODCACHE=str(tmp_path / "config/mod"))
    payload = dict(worktree_path=str(worktree), granted_writable_dirs=[str(shared)] if granted else [])
    child = runtime.scrubbed_lane_env(payload, env, executor)
    cache = Path(child["XDG_CACHE_HOME"])
    assert (cache == shared) == (granted and executor != "muse")
    assert child["GOCACHE"] == str(cache / "go-build")
    assert child["GOPATH"] == str(cache / "go")
    assert child["GOMODCACHE"] == str(cache / "go/pkg/mod")
    assert "CHARNESS_TASK_RUN_CACHE_HOME" not in child
    for key in ("GOCACHE", "GOPATH", "GOMODCACHE"):
        assert Path(child[key]).is_dir()
    code = "from pathlib import Path; import os; p=Path(os.environ['GOCACHE'])/'probe'; p.write_text('ok'); print(p.read_text())"
    command = [sys.executable, "-c", code]
    if executor == "claude":
        command = [*sandbox.sandbox_prefix(worktree, private,
                     writable_dirs=[shared] if granted else []), "--", *command]
    result = run_process(command, env=child, cwd=worktree)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
