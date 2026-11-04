"""Claude lanes: OS write confinement, private home and private Git administration.

The complete Claude process (including hooks and file tools) runs behind bwrap;
Claude's Bash-only sandbox cannot enforce this boundary. Runtime retention is
owned by the enclosing task-run runtime. By default a trusted host imports the lane branch after execution. Explicitly
granting the checkout’s common Git directory selects native shared Git instead.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import managed_checkout_root  # noqa: E402
from scripts.core.subprocess_guard import run_process  # noqa: E402
from scripts.task_run.task_run_claude_auth import (  # noqa: E402
    claude_auth_proxy as claude_auth_proxy,
)
from scripts.task_run.task_run_claude_review import reviewer_home  # noqa: E402
from scripts.task_run.task_run_contract import TASK_CLAUDE_MODEL, TaskRunError  # noqa: E402

_SECRET_DIRECTORIES = (".claude", ".codex", ".ceal", ".ssh", ".aws", ".azure", ".kube", ".gnupg", ".config", ".local/state/ceal")
_SECRET_FILES = (".claude.json", ".netrc", ".npmrc", ".git-credentials", ".bashrc", ".bash_profile", ".profile", ".zshrc", ".zshenv", ".zprofile")
_GIT_ENV_KEYS = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES")


def _bounded_paths(worktree: Path, runtime: Path) -> tuple[Path, Path]:
    worktree, runtime = worktree.resolve(), runtime.resolve()
    home = Path.home().resolve()
    if any(home.is_relative_to(path) for path in (worktree, runtime)):
        raise TaskRunError("Claude worktree/runtime must not cover the operator home")
    if worktree.is_relative_to(runtime) or runtime.is_relative_to(worktree):
        raise TaskRunError("Claude worktree/runtime roots must be separate bounded directories")
    return worktree, runtime


def _paths(runtime: Path) -> tuple[Path, Path, Path]:
    root = runtime.resolve() / "claude"
    return root, root / "home", root / "git"


def _git(worktree: Path, *args: str, git_dir: Path | None = None) -> str:
    env = {key: value for key, value in os.environ.items()
           if key not in _GIT_ENV_KEYS and not key.startswith("GIT_CONFIG_")}
    if git_dir is not None:
        env.update(GIT_DIR=str(git_dir), GIT_WORK_TREE=str(worktree))
    result = run_process(["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false",
                          "-c", "protocol.ext.allow=never", *args], cwd=worktree, env=env)
    if result.returncode:
        # Git output can contain hook/provider bodies. The operation name is enough.
        raise TaskRunError(f"Claude private Git operation failed: {args[0]}")
    return result.stdout.strip()


def _prepare_git(worktree: Path, runtime: Path) -> None:
    root, _home, private = _paths(runtime)
    marker = root / "git-identity.json"
    if marker.exists():
        identity = json.loads(marker.read_text(encoding="utf-8"))
        if identity["worktree"] != str(worktree):
            raise TaskRunError("Claude runtime belongs to another worktree")
        return
    branch = _git(worktree, "symbolic-ref", "--short", "HEAD")
    base = _git(worktree, "rev-parse", "HEAD")
    common = Path(_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    _git(worktree, "init", "--bare", str(private))
    (private / "objects/info/alternates").write_text(str(common / "objects") + "\n", encoding="utf-8")
    _git(worktree, "config", "core.bare", "false", git_dir=private)
    _git(worktree, "config", "core.worktree", str(worktree), git_dir=private)
    hook_result = run_process(["git", "config", "--path", "core.hooksPath"], cwd=worktree)
    hooks = Path(hook_result.stdout.strip()) if hook_result.returncode == 0 else common / "hooks"
    if not hooks.is_absolute():
        hooks = worktree / hooks
    _git(worktree, "config", "core.hooksPath", str(hooks.resolve()), git_dir=private)
    # Resolve the trusted repository identity before isolating HOME. The agent
    # cannot change this private configuration, and ambient author overrides
    # are removed from its environment.
    for setting in ("user.name", "user.email"):
        _git(worktree, "config", setting, _git(worktree, "config", "--get", setting), git_dir=private)
    _git(worktree, "symbolic-ref", "HEAD", f"refs/heads/{branch}", git_dir=private)
    _git(worktree, "update-ref", f"refs/heads/{branch}", base, git_dir=private)
    _git(worktree, "read-tree", "HEAD", git_dir=private)
    # Preserve the lane's actual staged candidate on a same-worktree continuation.
    index = Path(_git(worktree, "rev-parse", "--path-format=absolute", "--git-path", "index"))
    if index.is_file():
        shutil.copyfile(index, private / "index")
    marker.write_text(json.dumps({"worktree": str(worktree), "branch": branch, "base": base}), encoding="utf-8")


def _sandbox_git(worktree: Path, runtime: Path, *args: str) -> str:
    """Never interpret the agent's private Git configuration on the host."""
    root, home, private = _paths(runtime)
    env = {"PATH": os.defpath, "HOME": str(home), "TMPDIR": str(root / "tmp"),
           "GIT_DIR": str(private), "GIT_WORK_TREE": str(worktree),
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
    result = run_process([*sandbox_prefix(worktree, runtime), "--", "git", *args], cwd=worktree, env=env)
    if result.returncode:
        raise TaskRunError(f"Claude sandboxed Git operation failed: {args[0]}")
    return result.stdout.strip()


def _copy_bundle_for_host(bundle: Path, runtime: Path) -> Path:
    """A no-follow byte copy crosses from untrusted runtime into host storage."""
    source_fd = os.open(bundle, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(source_fd, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise TaskRunError("Claude candidate bundle must be a regular file")
        with tempfile.NamedTemporaryFile(dir=runtime.parent, prefix="claude-import-", delete=False) as target:
            shutil.copyfileobj(source, target)
            replacement = Path(target.name)
    trusted = runtime.parent / "claude-candidate.bundle"
    os.replace(replacement, trusted)
    return trusted


def finalize_claude_git(worktree: Path, execution_runtime_path: Path) -> None:
    """Import a verified bundle without running private Git config on the host.

    The canonical host worktree owns the destination branch. Private queries and
    bundle production stay sandboxed with no auth. Host index state is rebuilt
    from the imported commit; any uncommitted work remains visible as dirty.
    """
    worktree, runtime = _bounded_paths(worktree, execution_runtime_path)
    root, _home, private = _paths(runtime)
    marker = root / "git-identity.json"
    if not marker.is_file():
        return
    identity = json.loads(marker.read_text(encoding="utf-8"))
    branch = _git(worktree, "symbolic-ref", "--short", "HEAD")
    current = _git(worktree, "rev-parse", "HEAD")
    if identity != {"worktree": str(worktree), "branch": branch, "base": current}:
        raise TaskRunError("Claude lane Git identity changed before import")
    ref = f"refs/heads/{branch}"
    tip = _sandbox_git(worktree, runtime, "rev-parse", "--verify", ref)
    if re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", tip) is None:
        raise TaskRunError("Claude private task branch has no valid commit")
    if _sandbox_git(worktree, runtime, "symbolic-ref", "--short", "HEAD") != branch:
        raise TaskRunError("Claude changed the private task branch")
    if tip != current:
        bundle = root / "candidate.bundle"
        _sandbox_git(worktree, runtime, "bundle", "create", str(bundle), ref, f"^{current}")
        trusted = _copy_bundle_for_host(bundle, runtime)
        _git(worktree, "bundle", "verify", str(trusted))
        _git(worktree, "fetch", "--no-write-fetch-head", "--no-tags", str(trusted), ref)
        _git(worktree, "merge-base", "--is-ancestor", current, tip)
        _git(worktree, "update-ref", ref, tip, current)
    _git(worktree, "read-tree", "HEAD")
    identity["base"] = tip
    marker.write_text(json.dumps(identity), encoding="utf-8")


def _shared_git_dir(worktree: Path, writable_dirs: Sequence[Path]) -> Path | None:
    """Only an explicit grant of this checkout's common dir opts into native Git."""
    if not writable_dirs:
        return None
    common = Path(_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    if common not in [Path(path).resolve() for path in writable_dirs]:
        return None
    return Path(_git(worktree, "rev-parse", "--absolute-git-dir"))


def configure_claude_environment(
    env: dict[str, str], worktree: Path, execution_runtime_path: Path,
    *, writable_dirs: Sequence[Path] = (),
) -> dict[str, str]:
    """Isolate home and auth without logging or copying the real credential store."""
    worktree, execution_runtime_path = _bounded_paths(worktree, execution_runtime_path)
    root, home, private = _paths(execution_runtime_path)
    for directory in (root, home, home / ".claude", root / "tmp", root / "cache"):
        directory.mkdir(parents=True, exist_ok=True)
    (root / "run").mkdir(mode=0o700, exist_ok=True)
    runtime_fd = os.open(root / "run", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fchmod(runtime_fd, 0o700)
    finally:
        os.close(runtime_fd)
    configured = dict(env)
    for name in list(configured):
        if name in _GIT_ENV_KEYS or name.startswith(("GIT_CONFIG_", "GIT_AUTHOR_", "GIT_COMMITTER_")):
            configured.pop(name, None)
    # This native flag forces an additional Bash sandbox on Linux even when
    # sandbox.enabled is false. Auth is isolated by our parent-side proxy.
    for name in ("CLAUDE_CODE_SUBPROCESS_ENV_SCRUB", "BASH_ENV", "ENV", "ZDOTDIR", "SSH_AUTH_SOCK", "GIT_SSH_COMMAND", "GIT_ASKPASS",
                 "ANTHROPIC_CUSTOM_HEADERS", "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY"):
        configured.pop(name, None)
    configured.update(
        HOME=str(home), CLAUDE_CONFIG_DIR=str(home / ".claude"),
        CODEX_HOME=str(home / ".codex"), CEAL_HOME=str(home / ".ceal"),
        XDG_STATE_HOME=str(home / ".local/state"),
        CLAUDE_CODE_TMPDIR=str(root / "tmp"), TMPDIR=str(root / "tmp"),
        TMP=str(root / "tmp"), TEMP=str(root / "tmp"),
        XDG_CONFIG_HOME=str(home / ".config"), XDG_CACHE_HOME=str(root / "cache"),
        XDG_RUNTIME_DIR=str(root / "run"),
        CHARNESS_CLAUDE_GIT_MODE="shared" if _shared_git_dir(worktree, writable_dirs) else "private",
        DISABLE_AUTOUPDATER="1",
        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
    )
    if not any(configured.get(name) for name in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN")):
        credentials = Path.home() / ".claude/.credentials.json"
        try:
            token = json.loads(credentials.read_text(encoding="utf-8"))["claudeAiOauth"]["accessToken"]
        except (OSError, ValueError, KeyError, TypeError):
            token = None
        if token:
            configured["CLAUDE_CODE_OAUTH_TOKEN"] = token
    return configured


def _settings(worktree: Path, runtime: Path, writable_dirs: Sequence[Path] = ()) -> Path:
    root, _home, _private = _paths(runtime)
    home = Path.home()
    sensitive = [home / path for path in (*_SECRET_DIRECTORIES, *_SECRET_FILES)]
    sensitive.append(reviewer_home(runtime))
    deny = [f"Read(/{path}/**)" for path in sensitive]
    deny += [f"Read(/{path})" for path in sensitive]
    deny += [f"Edit(/{path}/**)" for path in sensitive]
    deny += [f"Edit(/{path})" for path in sensitive]
    deny += ["Read(//proc/**)", "Read(**/.env)", "Read(**/.env.*)", "Read(**/*.pem)", "Read(**/*.key)", "Bash(git push *)"]
    grants = [permission for path in writable_dirs
              for permission in (f"Edit(/{path}/**)", f"Read(/{path}/**)")]
    settings = {
        "permissions": {
            "defaultMode": "dontAsk", "disableBypassPermissionsMode": "disable",
            "allow": [*grants, "Bash(*)", f"Edit(/{worktree}/**)", f"Read(/{worktree}/**)", f"Read(/{runtime.resolve()}/**)", f"Edit(/{runtime.resolve()}/**)"],
            "deny": deny,
        },
        # Outer bwrap covers the whole process, including hooks/file tools. The
        # built-in Bash-only sandbox would need socat and widen git write access.
        "sandbox": {"enabled": False, "allowUnsandboxedCommands": False},
    }
    settings_path = root / "settings.json"
    settings_path.write_text(json.dumps(settings), encoding="utf-8")
    return settings_path


def _credential_files(worktree: Path) -> list[Path]:
    """Find known secret filenames in source, without traversing dependencies."""
    paths: set[Path] = set()
    credential_names = {"credentials", "credentials.json", ".credentials.json", ".netrc", ".npmrc", "id_rsa", "id_ed25519"}
    for root, directories, files in os.walk(worktree, followlinks=False):
        directories[:] = [name for name in directories if name not in
                          {".git", "node_modules", ".cache", ".venv", "venv", "__pycache__"}]
        for name in files:
            if name.startswith(".env") or name.endswith((".pem", ".key")) or name in credential_names:
                path = Path(root) / name
                if path.is_file():
                    paths.add(path.resolve())
    for path in Path.home().glob(".env*"):
        if path.is_file():
            paths.add(path.resolve())
    return sorted(paths)


def sandbox_prefix(worktree: Path, execution_runtime_path: Path, *,  # noqa: C901 - one ordered bwrap argv; split tracked in #888
                   writable_dirs: Sequence[Path] = ()) -> list[str]:
    """Return the OS boundary shared by Claude and the adversarial safety probe."""
    bwrap = shutil.which("bwrap")
    if bwrap is None:
        raise TaskRunError("Claude executor requires bubblewrap for whole-process confinement")
    worktree, runtime = _bounded_paths(worktree, execution_runtime_path)
    home = Path.home().resolve()
    root, _home, private = _paths(runtime)
    root.mkdir(parents=True, exist_ok=True)
    mask = root / "empty-credential"
    mask_fd = os.open(mask, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(mask_fd).st_mode):
            raise TaskRunError("Claude credential mask must be a regular file")
        os.ftruncate(mask_fd, 0)
    finally:
        os.close(mask_fd)
    command = [bwrap, "--die-with-parent", "--new-session", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--ro-bind", "/", "/", "--proc", "/proc", "--dev", "/dev"]
    # Native tools can use OS /tmp rather than TMPDIR for locks. Give them
    # private scratch storage; never grant writes to the host temporary root.
    # Later binds restore the worktree, runtime and explicit caches under /tmp.
    command.extend(("--tmpfs", "/tmp"))
    # Preserve read access to known temporary trees (including private Git's
    # object source), then restore only their explicitly writable descendants.
    read_paths = [worktree, runtime, *writable_dirs]
    if (worktree / ".git").exists():
        read_paths.append(Path(_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve())
    temporary_root = Path("/tmp")
    read_roots = {temporary_root / path.relative_to(temporary_root).parts[0]
                  for path in read_paths if path.is_relative_to(temporary_root) and path != temporary_root}
    for path in sorted(read_roots):
        command.extend(("--ro-bind", str(path), str(path)))
    # Explicit grants precede all secret and policy masks.
    for path in writable_dirs:
        command.extend(("--bind", str(path), str(path)))
    for name in _SECRET_DIRECTORIES:
        path = home / name
        if path.exists():
            command.extend(("--tmpfs", str(path), "--remount-ro", str(path)))
    for name in _SECRET_FILES:
        path = home / name
        if path.exists():
            command.extend(("--ro-bind", str(mask), str(path)))
    # A process must not reach host Unix sockets (SSH agents, daemon APIs).
    for path in (Path("/run/user") / str(os.getuid()),):
        if path.exists():
            command.extend(("--tmpfs", str(path), "--remount-ro", str(path)))
    command.extend(("--bind", str(worktree), str(worktree), "--bind", str(runtime), str(runtime)))
    # Policy and Git identity remain protected through the writable grants.
    # Shared Git is read-only unless the caller explicitly grants it.
    root, _home, private = _paths(runtime)
    # Make each policy-bearing ancestor a mountpoint too. A file-only mount
    # otherwise permits renaming its ancestor and recreating a writable policy.
    for directory in (root, private):
        if directory.exists():
            command.extend(("--bind", str(directory), str(directory)))
    command.extend(("--ro-bind", str(mask), str(mask)))
    for path in (worktree / ".git", root / "git-identity.json", root / "settings.json", private / "config"):
        if path.exists():
            command.extend(("--ro-bind", str(path), str(path)))
    shared_git = _shared_git_dir(worktree, writable_dirs)
    if shared_git is None and private.exists() and (worktree / ".git").is_file():
        # Scope private discovery to this worktree's mount namespace. Exported
        # selectors would override every foreign cwd/-C lookup in child tools.
        pointer = root / "git-discovery"
        pointer.write_text(f"gitdir: {private}\n", encoding="utf-8")
        command.extend(("--ro-bind", str(pointer), str(pointer),
                        "--ro-bind", str(pointer), str(worktree / ".git")))
    if shared_git is not None:
        common = Path(_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        # Mount each linked-admin ancestor so renaming it cannot replace policy.
        for directory in reversed((shared_git, *shared_git.parents)):
            if directory != common and directory.is_relative_to(common):
                command.extend(("--bind", str(directory), str(directory)))
        for path in (common / "config", common / "config.worktree", shared_git / "config.worktree"):
            if path.exists():
                command.extend(("--ro-bind", str(path), str(path)))
    private_review = reviewer_home(runtime)
    if private_review.exists():
        command.extend(("--tmpfs", str(private_review), "--remount-ro", str(private_review)))
    for path in _credential_files(worktree):
        command.extend(("--ro-bind", str(mask), str(path)))
    command.extend(("--chdir", str(worktree)))
    return command


def build_claude_command(
    executable: str, worktree: Path, execution_runtime_path: Path, *, model: str = TASK_CLAUDE_MODEL,
    writable_dirs: Sequence[Path] = (),
) -> list[str]:
    """Prepare a resumable isolated lane; stdin supplies its prompt."""
    worktree, runtime = _bounded_paths(worktree, execution_runtime_path)
    configure_claude_environment({}, worktree, runtime, writable_dirs=writable_dirs)
    if _shared_git_dir(worktree, writable_dirs) is None:
        _prepare_git(worktree, runtime)
    settings = _settings(worktree, runtime, writable_dirs)
    # Load only the managed plugin; private HOME must not import operator settings.
    plugin = managed_checkout_root(Path.home()) / "plugins" / "charness"
    return [*sandbox_prefix(worktree, runtime, writable_dirs=writable_dirs), "--", executable, "-p", "--model", model,
            "--output-format", "stream-json", "--verbose", "--permission-mode", "dontAsk",
            "--permission-prompts", "none", "--settings", str(settings), "--setting-sources", "project",
            "--plugin-dir", str(plugin), "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']


def finalize_executor_candidate(
    result: dict[str, Any], executor: str, worktree: Path, env: Mapping[str, str],
) -> None:
    if executor != "claude":
        return

    runtime = Path(env["CHARNESS_RUNTIME_ROOT"])
    if env.get("CHARNESS_CLAUDE_GIT_MODE") == "shared":
        return
    try:
        finalize_claude_git(worktree, runtime)
    except (OSError, TaskRunError):
        result["exec_error"] = "Claude private Git import failed; inspect retained runtime"
        result["exit_code"] = 1
