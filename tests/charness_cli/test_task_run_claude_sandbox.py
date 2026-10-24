"""Whole-process Claude boundary, private Git commits and home isolation."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import sys
from pathlib import Path

import pytest

from scripts.core.subprocess_guard import run_process
from scripts.task_run import task_run_claude_sandbox as sandbox


def _git(root: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = run_process(["git", *args], cwd=root, env=env)
    assert result.returncode == 0, args[0]
    return result.stdout.strip()


@pytest.mark.boundary_contract(reason="The actual OS sandbox must reject arbitrary-process outside writes")
def test_arbitrary_process_write_outside_lane_is_refused(tmp_path: Path) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    lane = tmp_path / "lane"
    runtime = tmp_path / "runtime"
    lane.mkdir()
    runtime.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("unchanged", encoding="utf-8")
    script = (
        "from pathlib import Path; import errno\n"
        "Path('inside.txt').write_text('allowed')\n"
        f"outside = Path({str(outside)!r})\n"
        "try:\n outside.write_text('forbidden')\n"
        "except OSError as exc:\n assert exc.errno in (errno.EROFS, errno.EACCES, errno.EPERM)\n"
        "else:\n raise AssertionError('outside write escaped confinement')\n"
        "print('inside-write=allowed outside-write=refused')\n"
    )
    result = run_process([*sandbox.sandbox_prefix(lane, runtime), "--", sys.executable, "-c", script], cwd=lane)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "inside-write=allowed outside-write=refused"
    assert outside.read_text(encoding="utf-8") == "unchanged"
    assert (lane / "inside.txt").read_text(encoding="utf-8") == "allowed"


@pytest.mark.boundary_contract(reason="Private Git must retain hooks and import the task-branch commit back through the real reader")
def test_private_git_commit_roundtrip_keeps_hooks_and_shared_git_readonly(tmp_path: Path) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    repo = tmp_path / "repo"
    lane = tmp_path / "lane"
    runtime = tmp_path / "runtime"
    repo.mkdir()
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.com")
    (repo / "doc.md").write_text("typoo\n", encoding="utf-8")
    _git(repo, "add", "doc.md")
    _git(repo, "commit", "-m", "seed")
    _git(repo, "worktree", "add", "-b", "pilot", str(lane))
    _git(repo, "config", "core.hooksPath", ".hooks")
    (lane / ".hooks").mkdir()
    hook = lane / ".hooks/pre-commit"
    hook.write_text("#!/bin/sh\nprintf '%s\\n' hook-ran > hook-proof\n", encoding="utf-8")
    hook.chmod(0o755)
    base = _git(lane, "rev-parse", "HEAD")
    sandbox.build_claude_command("claude", lane, runtime)
    env = sandbox.configure_claude_environment(dict(os.environ), lane, runtime)
    outside = tmp_path / "outside-hook-proof"
    malicious_hook = "#!/bin/sh\n" + "printf escaped > " + shlex.quote(str(outside)) + "\n"
    script = "printf '%s\\n' typo > doc.md && git add doc.md && git commit -m typo"
    script += " && printf %s " + shlex.quote(malicious_hook) + " > .hooks/reference-transaction && chmod +x .hooks/reference-transaction"
    result = run_process([*sandbox.sandbox_prefix(lane, runtime), "--", "/bin/sh", "-c", script], cwd=lane, env=env)
    assert result.returncode == 0, result.stderr
    assert (lane / "hook-proof").read_text(encoding="utf-8") == "hook-ran\n"
    assert _git(lane, "rev-parse", "HEAD") == base
    sandbox.finalize_claude_git(lane, runtime)
    assert not outside.exists(), "trusted metadata import ran a task-controlled hook"
    assert _git(lane, "rev-parse", "HEAD") != base
    assert _git(lane, "diff", "--name-only", "HEAD") == ""
    assert _git(lane, "log", "-1", "--format=%an <%ae>") == "Test <test@example.com>"
    assert _git(repo, "rev-parse", "main") == base
    sandbox.finalize_claude_git(lane, runtime)


def test_claude_settings_and_environment_are_invocation_local(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sandbox.Path, "home", lambda: tmp_path / "operator")
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "claude").mkdir()
    settings = json.loads(sandbox._settings(lane, runtime).read_text(encoding="utf-8"))
    env = sandbox.configure_claude_environment({"BASH_ENV": "do-not-source", "GIT_DIR": "old"}, lane, runtime)
    assert "BASH_ENV" not in env
    assert Path(env["HOME"]).is_relative_to(runtime)
    assert Path(env["CLAUDE_CONFIG_DIR"]).is_relative_to(runtime)
    assert Path(env["GIT_DIR"]).is_relative_to(runtime)
    assert env["CLAUDE_CODE_SUBPROCESS_ENV_SCRUB"] == "1"
    assert settings["permissions"]["disableBypassPermissionsMode"] == "disable"
    assert "Read(//proc/**)" in settings["permissions"]["deny"]
    assert settings["permissions"]["blockReadsOutsideWorkingDirectories"] is True


@pytest.mark.parametrize("which", ["home", "ancestor", "overlap"])
def test_unbounded_sandbox_roots_are_refused(tmp_path: Path, monkeypatch, which: str) -> None:
    operator_home = tmp_path / "operator"
    monkeypatch.setattr(sandbox.Path, "home", lambda: operator_home)
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    if which == "home":
        runtime = operator_home
    elif which == "ancestor":
        runtime = tmp_path
    else:
        runtime = lane / "runtime"
    with pytest.raises(sandbox.TaskRunError):
        sandbox.configure_claude_environment({}, lane, runtime)


@pytest.mark.boundary_contract(reason="Real loopback requests prove placeholder auth and fixed-upstream credential substitution")
def test_auth_proxy_hides_credentials_and_authenticates_invocation(monkeypatch) -> None:
    import http.client

    from scripts.task_run import task_run_claude_auth as auth

    captured = []

    class Response:
        status = 200

        def getheaders(self):
            return [("Content-Length", "2"), ("Authorization", "must-not-leave-proxy")]

        def read1(self, _size):
            if captured[-1].get("read"):
                return b""
            captured[-1]["read"] = True
            return b"ok"

    class Upstream:
        def __init__(self, host, timeout):
            assert host == "api.anthropic.com"

        def request(self, method, path, body, headers):
            captured.append({"method": method, "path": path, "body": body, "headers": headers})

        def getresponse(self):
            return Response()

        def close(self):
            pass

    monkeypatch.setattr(auth.http.client, "HTTPSConnection", Upstream)
    env = {"CLAUDE_CODE_OAUTH_TOKEN": "test-upstream-credential", "ANTHROPIC_API_KEY": "unused-test-key"}
    with auth.claude_auth_proxy(env) as child:
        assert child["CLAUDE_CODE_OAUTH_TOKEN"] != env["CLAUDE_CODE_OAUTH_TOKEN"]
        assert "ANTHROPIC_API_KEY" not in child
        assert all("test-upstream-credential" not in value for value in child.values())
        address = child["ANTHROPIC_BASE_URL"].removeprefix("http://")
        connection = http.client.HTTPConnection(address)
        connection.request("POST", "/v1/messages", body=b"{}")
        denied = connection.getresponse()
        assert denied.status == 403
        denied.read()
        connection.close()
        assert captured == []
        connection = http.client.HTTPConnection(address)
        connection.request("POST", "/v1/messages", body=b"{}", headers={"Authorization": "Bearer " + child["CLAUDE_CODE_OAUTH_TOKEN"]})
        response = connection.getresponse()
        assert response.status == 200
        assert response.getheader("Authorization") is None
        assert response.read() == b"ok"
        connection.close()
    assert captured[0]["headers"]["Authorization"] == "Bearer test-upstream-credential"


@pytest.mark.boundary_contract(reason="The real OS mount tree must prevent ancestor-rename policy replacement")
def test_sandbox_policy_ancestors_cannot_be_replaced(tmp_path: Path) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    lane.mkdir()
    private = runtime / "claude/git"
    private.mkdir(parents=True)
    policy = private / "config"
    policy.write_text("protected", encoding="utf-8")
    code = (
        "from pathlib import Path; import errno\n"
        f"paths = [Path({str(runtime / 'claude')!r}), Path({str(private)!r})]\n"
        "for path in paths:\n"
        " try:\n  path.rename(path.with_name(path.name + '.old'))\n"
        " except OSError as exc:\n  assert exc.errno in (errno.EBUSY, errno.EROFS, errno.EPERM)\n"
        " else:\n  raise AssertionError('policy ancestor replacement escaped')\n"
    )
    result = run_process([*sandbox.sandbox_prefix(lane, runtime), "--", sys.executable, "-c", code], cwd=lane)
    assert result.returncode == 0, result.stderr
    assert policy.read_text(encoding="utf-8") == "protected"


@pytest.mark.boundary_contract(reason="Arbitrary Bash reads must not bypass credential-file permission rules")
def test_preexisting_worktree_credentials_are_masked_for_subprocesses(tmp_path: Path) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    lane.mkdir()
    runtime.mkdir()
    secret = lane / ".env"
    secret.write_text("synthetic-credential-sentinel", encoding="utf-8")
    code = ("from pathlib import Path\n"
            "try:\n value = Path('.env').read_text()\n"
            "except PermissionError:\n pass\n"
            "else:\n assert value == ''\n")
    result = run_process([*sandbox.sandbox_prefix(lane, runtime), "--", sys.executable, "-c", code], cwd=lane)
    assert result.returncode == 0, result.stderr
    assert secret.read_text(encoding="utf-8") == "synthetic-credential-sentinel"
