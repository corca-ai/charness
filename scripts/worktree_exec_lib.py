from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import MutableMapping

from runtime_bootstrap import configure_runtime_environment, import_repo_module

_doctor_checks = import_repo_module(__file__, "scripts.worktree_doctor_checks")
git_common_dir = _doctor_checks.git_common_dir
is_isolated_worktree = _doctor_checks.is_isolated_worktree


class WorktreeExecError(RuntimeError):
    """The command boundary could not establish a safe execution context."""


def _require_isolated_checkout(repo_root: Path) -> None:
    common_dir = git_common_dir(repo_root)
    isolated = is_isolated_worktree(repo_root, common_dir)
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
) -> dict[str, str]:
    """Build the child environment whose runtime outputs cannot land in ``repo_root``."""
    child_env = dict(os.environ if env is None else env)
    configured = configure_runtime_environment(repo_root, child_env)

    # pytest has no standard environment variable for its cache directory. Inject
    # the override at the same process boundary as the other runtime paths so a
    # plain `pytest` invocation, and pytest started by another child, does not fall
    # back to `<repo>/.pytest_cache`. A later explicit command-line override remains
    # an intentional caller choice.
    cache_option = shlex.join(["-o", f"cache_dir={configured['CHARNESS_PYTEST_CACHE_DIR']}"])
    existing_addopts = configured.get("PYTEST_ADDOPTS", "").strip()
    configured["PYTEST_ADDOPTS"] = f"{existing_addopts} {cache_option}".strip()
    configured["CHARNESS_REPO_ROOT"] = str(repo_root.resolve())
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
        result = subprocess.run(command, cwd=repo_root, env=child_env, check=False)
    except OSError as exc:
        raise WorktreeExecError(f"could not execute {command[0]!r}: {exc}") from exc

    # Match the conventional shell status for a child killed by a signal while
    # retaining ordinary command exit codes verbatim.
    return result.returncode if result.returncode >= 0 else 128 - result.returncode
