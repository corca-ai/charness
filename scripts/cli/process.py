"""Process, checkout, git, and runtime-environment helpers."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli import bootstrap as _bootstrap  # noqa: E402
from scripts.cli.bootstrap import (  # noqa: E402
    _BOOTSTRAP_PYTHON_CACHE,
    BOOTSTRAP_RUNTIME_RELATIVE_PATH,
    CharnessError,
    expect_success,
    resolve_repo_root,
    run,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    _configure_runtime_for_repo,
    _resolve_worktree_lib_root,
    _runtime_bootstrap_module,
    default_home_root,
)
from scripts.cli.common import (  # noqa: E402
    parse_repo_script_payload,
)


def _runtime_root_for_repo(repo_root: Path) -> Path:
    runtime_bootstrap = _runtime_bootstrap_module(repo_root)
    if runtime_bootstrap is None:
        raise CharnessError(
            "Charness runtime owner is unavailable; initialize the managed checkout first"
        )
    return runtime_bootstrap.runtime_root(repo_root)


def invoke_repo_script(repo_root: Path, relative_script: str, *script_args: str) -> str:
    python_executable = resolve_repo_python(repo_root)
    script_path = Path(relative_script)
    if script_path.parts[:1] == ("tools",):
        command = [
            python_executable,
            "-m",
            script_path.with_suffix("").as_posix().replace("/", "."),
        ]
    else:
        command = [python_executable, relative_script]
    result = run([*command, *script_args], cwd=repo_root)
    expect_success(result, f"`{relative_script}` in `{repo_root}`")
    return result.stdout.strip()


def resolve_repo_python(repo_root: Path) -> str:
    _configure_runtime_for_repo(repo_root)
    resolved_root = str(repo_root.resolve())
    cached = _BOOTSTRAP_PYTHON_CACHE.get(resolved_root)
    if cached:
        return cached

    # `bootstrap_runtime.py` is deliberately repair-capable: it validates the
    # contract, rewrites stale launchers, and can install dependencies.  Most
    # CLI invocations only need to reuse the already healthy launcher, though.
    # Keep that common path read-only and leave every absent/unhealthy case to
    # the existing repair flow below.
    fast_path = bootstrap_runtime_fast_path(repo_root)
    if fast_path is not None and bootstrap_runtime_is_healthy(repo_root, *fast_path):
        python_executable = str(fast_path[0])
        _BOOTSTRAP_PYTHON_CACHE[resolved_root] = python_executable
        return python_executable

    result = run(
        [
            sys.executable,
            BOOTSTRAP_RUNTIME_RELATIVE_PATH,
            "--repo-root",
            resolved_root,
            "--base-python",
            sys.executable,
            "--print-python",
        ],
        cwd=repo_root,
    )
    expect_success(result, f"bootstrap runtime for `{repo_root}`")
    python_executable = result.stdout.strip()
    if not python_executable:
        raise CharnessError(
            f"bootstrap runtime for `{repo_root}` did not return a Python executable"
        )
    _BOOTSTRAP_PYTHON_CACHE[resolved_root] = python_executable
    return python_executable


def bootstrap_runtime_fast_path(repo_root: Path) -> tuple[Path, list[str], tuple[int, int]] | None:
    """Return the validated read-only launcher probe inputs, if available.

    Contract errors intentionally return ``None`` here.  The repair-capable
    bootstrap command remains the single authoritative validator and produces
    its established diagnostics for every non-fast-path case.
    """

    contract_path = repo_root / "packaging" / "bootstrap-python.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        schema_version = contract["schema_version"]
        python_section = contract["python"]
        min_version = python_section["min_version"]
        runtime_dir = contract["runtime_dir"]
        requirements_file = contract["requirements_file"]
        required_modules = contract["required_modules"]
    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError):
        return None
    if schema_version != 1 or not isinstance(python_section, dict):
        return None
    if not isinstance(min_version, str) or not min_version:
        return None
    try:
        min_version_parts = min_version.split(".")
        if len(min_version_parts) < 2:
            return None
        minimum = (int(min_version_parts[0]), int(min_version_parts[1]))
    except ValueError:
        return None
    # The reuse path does not read requirements, but malformed contract fields
    # must still reach the authoritative bootstrap validator instead of being
    # silently accepted only because today's launcher happens to be healthy.
    if (
        not isinstance(runtime_dir, str)
        or not runtime_dir
        or not isinstance(requirements_file, str)
        or not requirements_file
    ):
        return None
    if (
        not isinstance(required_modules, list)
        or not required_modules
        or not all(isinstance(module, str) and module for module in required_modules)
    ):
        return None
    launcher_name = "python.cmd" if os.name == "nt" else "python"
    launcher = (
        _runtime_root_for_repo(repo_root)
        / runtime_dir
        / ("Scripts" if os.name == "nt" else "bin")
        / launcher_name
    )
    return launcher, required_modules, minimum


def bootstrap_runtime_is_healthy(
    repo_root: Path, launcher: Path, required_modules: list[str], minimum: tuple[int, int]
) -> bool:
    """Probe the launcher once without inheriting another runtime's path."""

    if not launcher.exists():
        return False

    probe = (
        "import importlib, sys\n"
        f"modules = {required_modules!r}\n"
        f"minimum = {minimum!r}\n"
        "if sys.version_info[:2] < minimum:\n"
        "    sys.exit(1)\n"
        "for name in modules:\n"
        "    try:\n"
        "        importlib.import_module(name)\n"
        "    except Exception:\n"
        "        sys.exit(1)\n"
    )
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    try:
        result = run([str(launcher), "-c", probe], cwd=repo_root, env=env)
    except OSError:
        return False
    return result.returncode == 0


def invoke_repo_json_script(
    repo_root: Path,
    relative_script: str,
    *script_args: str,
    allow_failure: bool = False,
) -> object:
    python_executable = resolve_repo_python(repo_root)
    result = run([python_executable, relative_script, *script_args], cwd=repo_root)
    if result.returncode != 0 and not allow_failure:
        expect_success(result, f"`{relative_script}` in `{repo_root}`")
    stdout = result.stdout.strip()
    if not stdout:
        if result.returncode != 0:
            raise CharnessError(
                f"`{relative_script}` in `{repo_root}` exited with code {result.returncode} and produced no payload output\nSTDERR:\n{result.stderr}"
            )
        return None
    try:
        return parse_repo_script_payload(stdout, relative_script)
    except CharnessError as exc:
        raise CharnessError(f"{exc}\nREPO ROOT: {repo_root}\nSTDERR:\n{result.stderr}") from exc


def _run_repo_json_command(repo_root: Path, command: list[str]) -> tuple[object | None, int, str]:
    result = run(command, cwd=repo_root)
    stdout = result.stdout.strip()
    payload: object | None = None
    if stdout:
        try:
            payload = parse_repo_script_payload(stdout, " ".join(command))
        except CharnessError as exc:
            raise CharnessError(f"{exc}\nREPO ROOT: {repo_root}\nSTDERR:\n{result.stderr}") from exc
    return payload, result.returncode, result.stderr


def _load_worktree_lib(args: argparse.Namespace):
    repo_root = _resolve_worktree_lib_root(args)
    repo_text = str(repo_root)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    from scripts.worktree import worktree_doctor_lib

    return worktree_doctor_lib


def _load_worktree_audit_lib(args: argparse.Namespace):
    repo_root = _resolve_worktree_lib_root(args)
    repo_text = str(repo_root)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    from scripts.worktree import worktree_audit_lib

    return worktree_audit_lib


def _load_worktree_cleanup_lib(args: argparse.Namespace):
    repo_root = _resolve_worktree_lib_root(args)
    repo_text = str(repo_root)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    from scripts.worktree import worktree_cleanup_lib

    return worktree_cleanup_lib


def _load_worktree_create_lib(args: argparse.Namespace):
    repo_root = _resolve_worktree_lib_root(args)
    repo_text = str(repo_root)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    from scripts.worktree import worktree_create_lib

    return worktree_create_lib


def _load_worktree_exec_lib(args: argparse.Namespace):
    repo_root = _resolve_worktree_lib_root(args)
    repo_text = str(repo_root)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)

    # The target is not known when this monolithic CLI starts. Install its
    # external runtime before importing the executor, so the executor itself
    # cannot create a local bytecode cache in the target checkout.
    target = _resolve_worktree_target(args)
    _configure_runtime_for_repo(target)

    from scripts.worktree import worktree_exec_lib

    return worktree_exec_lib


def _load_task_run_lib(args: argparse.Namespace):
    repo_root = _resolve_worktree_lib_root(args)
    repo_text = str(repo_root)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    from scripts.task_run import task_run

    return task_run


def _load_train_lib(args: argparse.Namespace):
    repo_root = _resolve_worktree_lib_root(args)
    repo_text = str(repo_root)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    from scripts.task_run import task_run_train

    return task_run_train


def _resolve_worktree_target(args: argparse.Namespace) -> Path:
    target = args.repo_root if args.repo_root is not None else Path.cwd()
    return Path(target).resolve()


def _load_catalog_lib():
    """Load the stable catalog backend from the selected Charness checkout."""
    if _bootstrap.EMBEDDED_REPO_ROOT is not None:
        repo_root = _bootstrap.EMBEDDED_REPO_ROOT
    else:
        repo_root, _managed_checkout = resolve_repo_root(default_home_root(), None)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from scripts.adapters import capability_catalog

    return capability_catalog
