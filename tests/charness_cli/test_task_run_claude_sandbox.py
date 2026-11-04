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



@pytest.mark.boundary_contract(reason="Claude Git discovery must honor foreign repositories while task commits roundtrip through private Git or explicit native grants")
@pytest.mark.parametrize("shared", [False, True], ids=["private", "native"])
def test_lane_git_discovery_respects_foreign_checkout(tmp_path: Path, shared: bool) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    repo, lane, foreign, runtime = [tmp_path / name for name in ("repo", "lane", "foreign", "runtime")]
    for root in (repo, foreign):
        root.mkdir()
        _git(root, "init", "--initial-branch=main")
        _git(root, "config", "user.name", "Test")
        _git(root, "config", "user.email", "test@example.com")
        _git(root, "commit", "--allow-empty", "-m", root.name)
    base = _git(repo, "rev-parse", "HEAD")
    foreign_head = _git(foreign, "rev-parse", "HEAD")
    assert foreign_head != base
    _git(repo, "worktree", "add", "-b", "pilot", str(lane))
    writable = [repo / ".git"] if shared else []
    command = sandbox.build_claude_command("claude", lane, runtime, writable_dirs=writable)
    env = sandbox.configure_claude_environment(dict(os.environ, CHARNESS_RUNTIME_ROOT=str(runtime)),
                                                lane, runtime, writable_dirs=writable)
    prefix = command[:command.index("--")]
    code = (
        "import subprocess; from pathlib import Path\n"
        "def git(*args, cwd=None):\n"
        " return subprocess.check_output(['git',*args],cwd=cwd,text=True).strip()\n"
        f"assert git('-C',{str(foreign)!r},'rev-parse','HEAD') == {foreign_head!r}, 'foreign -C discovery'\n"
        f"assert git('rev-parse','HEAD',cwd={str(foreign)!r}) == {foreign_head!r}, 'foreign cwd discovery'\n"
        "Path('nested').mkdir()\n"
        f"assert git('rev-parse','HEAD',cwd='nested') == {base!r}\n"
        "git('commit','--allow-empty','-m','lane discovery')\n"
        "print(git('rev-parse','HEAD'))\n"
    )
    result = run_process([*prefix, "--", sys.executable, "-c", code], cwd=lane, env=env)
    assert result.returncode == 0, result.stderr
    tip = result.stdout.splitlines()[-1]
    assert tip != base
    assert _git(lane, "rev-parse", "HEAD") == (tip if shared else base)
    finalized = {"exit_code": 0}
    sandbox.finalize_executor_candidate(finalized, "claude", lane, env)
    assert finalized == {"exit_code": 0}
    assert _git(lane, "rev-parse", "HEAD") == tip
    assert _git(repo, "rev-parse", "main") == base
    assert _git(foreign, "rev-parse", "HEAD") == foreign_head



def test_lane_loads_only_managed_charness_plugin(tmp_path: Path, monkeypatch) -> None:
    from scripts.cli.bootstrap import managed_checkout_root

    operator = tmp_path / "operator"
    monkeypatch.setattr(sandbox.Path, "home", lambda: operator)
    monkeypatch.setattr(sandbox, "_prepare_git", lambda *_args: None)
    monkeypatch.setattr(sandbox, "sandbox_prefix", lambda *_args, **_kwargs: ["bwrap"])
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    command = sandbox.build_claude_command("claude", lane, runtime)
    plugin = managed_checkout_root(operator) / "plugins" / "charness"
    assert command.count("--plugin-dir") == 1
    assert command[command.index("--plugin-dir") + 1] == str(plugin)
    assert command[command.index("--setting-sources") + 1] == "project"
    assert "--strict-mcp-config" in command
    assert command[command.index("--mcp-config") + 1] == '{"mcpServers":{}}'
    env = sandbox.configure_claude_environment({}, lane, runtime)
    assert Path(env["HOME"]).is_relative_to(runtime)
    assert Path(env["CLAUDE_CONFIG_DIR"]).is_relative_to(runtime)


def test_claude_settings_and_environment_are_invocation_local(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sandbox.Path, "home", lambda: tmp_path / "operator")
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "claude").mkdir()
    settings = json.loads(sandbox._settings(lane, runtime).read_text(encoding="utf-8"))
    env = sandbox.configure_claude_environment({"BASH_ENV": "do-not-source", "GIT_DIR": "old", "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB": "1"}, lane, runtime)
    assert "BASH_ENV" not in env
    assert Path(env["HOME"]).is_relative_to(runtime)
    assert Path(env["CLAUDE_CONFIG_DIR"]).is_relative_to(runtime)
    assert not any(key in env for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"))
    assert "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB" not in env
    assert settings["permissions"]["disableBypassPermissionsMode"] == "disable"
    assert "Read(//proc/**)" in settings["permissions"]["deny"]
    assert "blockReadsOutsideWorkingDirectories" not in settings["permissions"]
    assert "Bash(*)" in settings["permissions"]["allow"]


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


@pytest.mark.boundary_contract(reason="Explicit host grants must roundtrip native task-branch commits and gate receipts through the actual OS sandbox")
def test_explicit_grants_allow_shared_git_and_gate_cache(tmp_path: Path) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    from scripts.task_run import task_run_lane_options as options, task_run_lane_runner as runner
    from scripts.task_run.task_run_runtime import scrubbed_lane_env

    repo, lane, runtime, cache = [tmp_path / name for name in ("repo", "lane", "runtime", "cache")]
    repo.mkdir()
    cache.mkdir()
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "commit", "--allow-empty", "-m", "seed")
    _git(repo, "worktree", "add", "-b", "pilot", str(lane))
    # A retained private runtime must not import its stale branch after opt-in.
    sandbox.build_claude_command("claude", lane, runtime)
    common = repo / ".git"
    _git(repo, "config", "extensions.worktreeConfig", "true")
    _git(lane, "config", "--worktree", "user.name", "Test")
    linked = Path(_git(lane, "rev-parse", "--absolute-git-dir"))
    grants = options.resolve_granted_writable(repo, [common, cache], executor="claude")
    payload = {"worktree_path": str(lane)}
    resolved = {"git_common_dir": common, "granted_writable_dirs": grants}
    writable = runner.lane_writable_dirs(payload, resolved, common / "worktrees/lane", runtime,
                                         executor="claude", worktree=lane)
    command = runner.lane_command(executor="claude", executable="claude", effort="medium",
                                  prompt="probe", execution_runtime_path=runtime,
                                  writable_dirs=writable, worktree=lane)
    env = scrubbed_lane_env(payload, dict(os.environ, CHARNESS_RUNTIME_ROOT=str(runtime)), "claude")
    base = _git(repo, "rev-parse", "main")
    receipt = common / "ceal/pre-push-attestations/probe.jsonl"
    code = ("from pathlib import Path; import subprocess\n"
            f"receipt=Path({str(receipt)!r}); receipt.parent.mkdir(parents=True,exist_ok=True); receipt.write_text('gate-pass\\n')\n"
            f"Path({str(cache / 'verification.json')!r}).write_text('verified')\n"
            "subprocess.run(['git','commit','--allow-empty','-m','sandbox probe'],check=True)\n"
            f"assert Path({str(common / 'config')!r}).read_text()\n"
            f"outside=Path({str(tmp_path / 'outside')!r})\n"
            f"config=Path({str(common / 'config')!r})\n"
            "try: config.write_text('changed')\n"
            "except OSError: pass\n"
            "else: raise AssertionError('shared Git policy writable')\n"
            f"linked=Path({str(linked)!r})\n"
            "try: (linked / 'config.worktree').write_text('changed')\n"
            "except OSError: pass\n"
            "else: raise AssertionError('linked Git policy writable')\n"
            "try: linked.rename(linked.with_name('replaced'))\n"
            "except OSError: pass\n"
            "else: raise AssertionError('linked policy ancestor replaceable')\n"
            "try: outside.write_text('escape')\n"
            "except OSError: pass\n"
            "else: raise AssertionError('outside grant writable')\n")
    prefix = command[:command.index("--")]
    result = run_process([*prefix, "--", sys.executable, "-c", code], cwd=lane, env=env)
    assert result.returncode == 0, result.stderr
    assert payload["granted_writable_dirs"] == grants
    assert receipt.read_text() == "gate-pass\n"
    assert (cache / "verification.json").read_text() == "verified"
    tip = _git(lane, "rev-parse", "HEAD")
    assert tip != base
    finalized = {"exit_code": 0}
    sandbox.finalize_executor_candidate(finalized, "claude", lane, env)
    assert finalized == {"exit_code": 0}
    assert _git(lane, "rev-parse", "HEAD") == tip
    assert _git(repo, "rev-parse", "main") == base


@pytest.mark.boundary_contract(reason="Native package managers must acquire private OS tmp locks without a writable host tmp grant")
def test_private_tmp_allows_package_manager_locks_without_host_writes(tmp_path: Path) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    lane.mkdir()
    runtime.mkdir()
    env = sandbox.configure_claude_environment({}, lane, runtime)
    lock_name = "claude-package-manager-lock-" + tmp_path.name
    code = (
        "from pathlib import Path; import os\n"
        f"lock = Path('/tmp') / {lock_name!r}\n"
        "lock.mkdir(); (lock / 'lock').write_text('locked')\n"
        "assert (lock / 'lock').read_text() == 'locked'\n"
        "runtime = Path(os.environ['XDG_RUNTIME_DIR'])\n"
        "(runtime / 'runtime-lock').write_text('locked')\n"
        "assert runtime.stat().st_mode & 0o777 == 0o700\n"
        "print('package-manager-lock=write/read private-tmp=ok')\n"
    )
    result = run_process([*sandbox.sandbox_prefix(lane, runtime), "--", sys.executable, "-c", code], cwd=lane, env=env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "package-manager-lock=write/read private-tmp=ok"
    assert not (Path('/tmp') / lock_name).exists()


def test_runtime_directory_reclaims_mode_without_following_symlinks(tmp_path: Path) -> None:
    lane, runtime = tmp_path / "lane", tmp_path / "runtime"
    lane.mkdir()
    runtime.mkdir()
    sandbox.configure_claude_environment({}, lane, runtime)
    run = runtime / "claude/run"
    run.chmod(0o777)
    sandbox.configure_claude_environment({}, lane, runtime)
    assert run.stat().st_mode & 0o777 == 0o700
    run.rename(run.with_name("previous-run"))
    outside = tmp_path / "outside"
    outside.mkdir(mode=0o755)
    before = outside.stat().st_mode
    run.symlink_to(outside, target_is_directory=True)
    with pytest.raises(OSError):
        sandbox.configure_claude_environment({}, lane, runtime)
    assert outside.stat().st_mode == before


def test_sandbox_masks_docker_credentials_and_host_daemon_sockets(monkeypatch, tmp_path: Path) -> None:
    """A docker-group member must not reach the daemon or registry auth from a lane."""
    home = tmp_path / "home"
    (home / ".docker").mkdir(parents=True)
    lane = tmp_path / "lane"
    runtime = tmp_path / "runtime"
    lane.mkdir()
    runtime.mkdir()
    daemon = tmp_path / "daemon.sock"  # existence is what the mask keys on
    daemon.write_text("", encoding="utf-8")
    monkeypatch.setattr(sandbox.Path, "home", classmethod(lambda _cls: home))
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: "/usr/bin/bwrap")
    monkeypatch.setattr(sandbox, "_HOST_DAEMON_SOCKETS", (str(daemon), str(tmp_path / "absent.sock")))

    command = sandbox.sandbox_prefix(lane, runtime)

    mask = str(runtime.resolve() / "claude" / "empty-credential")
    docker = str(home / ".docker")
    assert ["--tmpfs", docker, "--remount-ro", docker] in [command[i:i + 4] for i in range(len(command))]
    assert ["--ro-bind", mask, str(daemon.resolve())] in [command[i:i + 3] for i in range(len(command))]
    assert str(tmp_path / "absent.sock") not in command


@pytest.mark.boundary_contract(reason="The real OS sandbox must refuse a connect to the host Docker daemon socket")
def test_lane_cannot_connect_to_the_host_docker_socket(tmp_path: Path) -> None:
    socket_path = Path("/run/docker.sock")
    if not shutil.which("bwrap") or not socket_path.exists():
        pytest.skip("bubblewrap or a host Docker socket is not present")
    lane = tmp_path / "lane"
    runtime = tmp_path / "runtime"
    lane.mkdir()
    runtime.mkdir()
    script = (
        "import socket\n"
        "s = socket.socket(socket.AF_UNIX)\n"
        "try:\n s.connect('/run/docker.sock')\n"
        "except OSError as exc:\n print('refused', type(exc).__name__)\n"
        "else:\n print('connected')\n"
    )
    result = run_process([*sandbox.sandbox_prefix(lane, runtime), "--", sys.executable, "-c", script], cwd=lane)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("refused"), result.stdout


@pytest.mark.boundary_contract(reason="The real OS sandbox must hide listed home credential files from a lane")
@pytest.mark.parametrize("name", [".pypirc", ".cargo/credentials.toml", ".docker/config.json"])
def test_listed_home_credentials_are_unreadable_in_a_real_lane(monkeypatch, tmp_path: Path, name: str) -> None:
    if not shutil.which("bwrap"):
        pytest.skip("bubblewrap not installed")
    home, lane, runtime = tmp_path / "home", tmp_path / "lane", tmp_path / "runtime"
    lane.mkdir()
    runtime.mkdir()
    secret = home / name
    secret.parent.mkdir(parents=True)
    secret.write_text("synthetic-credential-sentinel", encoding="utf-8")
    monkeypatch.setattr(sandbox.Path, "home", classmethod(lambda _cls: home))
    code = ("from pathlib import Path\n"
            f"path = Path({str(secret)!r})\n"
            "try:\n value = path.read_text()\n"
            "except OSError:\n value = ''\n"
            "assert 'synthetic-credential-sentinel' not in value, value\n")
    result = run_process([*sandbox.sandbox_prefix(lane, runtime), "--", sys.executable, "-c", code], cwd=lane)
    assert result.returncode == 0, result.stderr
    assert secret.read_text(encoding="utf-8") == "synthetic-credential-sentinel"
