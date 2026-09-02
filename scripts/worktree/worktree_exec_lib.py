from __future__ import annotations

import os
from pathlib import Path
from typing import MutableMapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import (  # noqa: E402
    MANAGED_RUNTIME_PATH_KEYS,
    configure_runtime_environment,
    import_repo_module,
)

_doctor_checks = import_repo_module(__file__, "scripts.worktree.worktree_doctor_checks")
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
git_checkout_facts = _doctor_checks.git_checkout_facts
checkout_isolation = _doctor_checks.checkout_isolation


class WorktreeExecError(RuntimeError):
    """The command boundary could not establish a safe execution context."""


def _require_isolated_checkout(repo_root: Path) -> None:
    facts = git_checkout_facts(repo_root, include_hooks_path=False)
    isolated = checkout_isolation(facts)
    if isolated is True:
        return
    if isolated is False:
        raise WorktreeExecError(
            f"{repo_root} is the primary worktree; worktree exec refuses to run a write-capable "
            "command there. Create a linked worktree first, or use the command directly when "
            "you intentionally accept parent-worktree writes."
        )
    raise WorktreeExecError(
        f"could not establish that {repo_root} is an isolated linked worktree; refusing to "
        "run the command"
    )


def prepare_exec_environment(
    repo_root: Path,
    env: MutableMapping[str, str] | None = None,
    *,
    runtime_root: Path | None = None,
) -> dict[str, str]:
    """Build the child environment whose runtime outputs cannot land in ``repo_root``."""
    child_env = dict(os.environ if env is None else env)
    if runtime_root is not None:
        for key in MANAGED_RUNTIME_PATH_KEYS:
            child_env.pop(key, None)
        child_env["CHARNESS_RUNTIME_ROOT"] = str(runtime_root.resolve())
    configured = configure_runtime_environment(repo_root, child_env)

    configured.pop("CHARNESS_REPO_ROOT", None)
    return configured


def run_exec(
    repo_root: Path,
    command: list[str],
    *,
    allow_main: bool = False,
    env: MutableMapping[str, str] | None = None,
) -> int:
    """Run one command in an isolated worktree with external runtime paths."""
    repo_root = repo_root.resolve()
    if not repo_root.is_dir():
        raise WorktreeExecError(f"worktree path does not exist: {repo_root}")
    if not command:
        raise WorktreeExecError("worktree exec requires a command after `--`")
    if not allow_main:
        _require_isolated_checkout(repo_root)

    child_env = prepare_exec_environment(repo_root, env)
    try:
        result = run_process(command, cwd=repo_root, env=child_env, timeout_seconds=None)
    except OSError as exc:
        raise WorktreeExecError(f"could not execute {command[0]!r}: {exc}") from exc

    # Match the conventional shell status for a child killed by a signal while
    # retaining ordinary command exit codes verbatim.
    return result.returncode if result.returncode >= 0 else 128 - result.returncode
