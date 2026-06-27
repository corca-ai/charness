#!/usr/bin/env python3
"""Canonical runner for the repo's standing pytest gate."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

STANDING_PYTEST_TARGETS = (
    "tests/quality_gates",
    "tests/control_plane",
    "tests/test_*.py",
    "tests/charness_cli",
)
DEFAULT_XDIST_WORKER_CAP = 16


def repo_tmp_key(repo_root: Path) -> str:
    return hashlib.sha256(str(repo_root).encode()).hexdigest()[:12]


def default_temp_root(repo_root: Path, env: dict[str, str] | None = None) -> Path:
    env = env or os.environ
    if env.get("PYTEST_DEBUG_TEMPROOT"):
        return Path(env["PYTEST_DEBUG_TEMPROOT"])
    cache_root = Path(env.get("XDG_CACHE_HOME") or Path(env.get("HOME", "/tmp")) / ".cache")
    return cache_root / "charness" / "pytest-tmp" / repo_tmp_key(repo_root)


def ensure_external_temp_root(repo_root: Path, temp_root: Path) -> None:
    resolved_repo = repo_root.resolve()
    resolved_temp = temp_root.resolve()
    try:
        resolved_temp.relative_to(resolved_repo)
    except ValueError:
        return
    raise SystemExit(
        "standing-pytest: pytest temp root "
        f"{str(temp_root)!r} is inside the repo {str(repo_root)!r}; point "
        "XDG_CACHE_HOME or PYTEST_DEBUG_TEMPROOT outside the repo"
    )


def default_basetemp(repo_root: Path, env: dict[str, str] | None = None) -> Path:
    temp_root = default_temp_root(repo_root, env)
    ensure_external_temp_root(repo_root, temp_root)
    user = subprocess.run(
        ["id", "-un"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.strip() or "unknown"
    return temp_root / f"pytest-of-{user}" / f"pytest-{time.time_ns()}"


def choose_pytest_command(env: dict[str, str] | None = None) -> list[str]:
    env = os.environ if env is None else env
    if importlib.util.find_spec("pytest") is not None:
        python = env.get("CHARNESS_STANDING_PYTEST_PYTHON", sys.executable).strip() or sys.executable
        return [python, "-m", "pytest"]
    return ["pytest"]


def _plugin_disabled(plugin_name: str, addopts: str) -> bool:
    try:
        parts = shlex.split(addopts)
    except ValueError:
        parts = addopts.split()
    for index, part in enumerate(parts):
        if part == "-p" and index + 1 < len(parts) and parts[index + 1] == f"no:{plugin_name}":
            return True
        if part == f"-pno:{plugin_name}":
            return True
    return False


def has_xdist(pytest_command: list[str], env: dict[str, str] | None = None) -> bool:
    env = os.environ if env is None else env
    if env.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD"):
        return False
    if _plugin_disabled("xdist", env.get("PYTEST_ADDOPTS", "")):
        return False
    current_python_pytest = [env.get("CHARNESS_STANDING_PYTEST_PYTHON", sys.executable).strip() or sys.executable, "-m", "pytest"]
    if pytest_command != current_python_pytest:
        return False
    return importlib.util.find_spec("xdist") is not None


def choose_xdist_workers(env: dict[str, str] | None = None) -> str:
    env = os.environ if env is None else env
    override = env.get("CHARNESS_PYTEST_WORKERS", "").strip()
    if override:
        if override in {"auto", "logical"}:
            return override
        try:
            workers = int(override)
        except ValueError as exc:
            raise SystemExit(
                "standing-pytest: CHARNESS_PYTEST_WORKERS must be a positive integer, "
                "'auto', or 'logical'"
            ) from exc
        if workers < 1:
            raise SystemExit("standing-pytest: CHARNESS_PYTEST_WORKERS must be >= 1")
        return str(workers)

    cpu_count = os.cpu_count() or DEFAULT_XDIST_WORKER_CAP
    return str(min(cpu_count, DEFAULT_XDIST_WORKER_CAP))


def expand_targets(repo_root: Path, targets: tuple[str, ...] = STANDING_PYTEST_TARGETS) -> list[str]:
    expanded: list[str] = []
    for target in targets:
        if any(char in target for char in "*?["):
            matches = sorted(str(path.relative_to(repo_root)) for path in repo_root.glob(target))
            expanded.extend(matches or [target])
        else:
            expanded.append(target)
    return expanded


def combined_targets(repo_root: Path, extra_pytest_targets: list[str] | None = None) -> list[str]:
    return [*expand_targets(repo_root), *(extra_pytest_targets or [])]


def build_pytest_command(
    repo_root: Path,
    *,
    basetemp: Path,
    include_release_only: bool,
    extra_pytest_targets: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> list[str]:
    env = os.environ if env is None else env
    command = [*choose_pytest_command(env), "-q"]
    if not include_release_only:
        command.extend(["-m", "not release_only"])
    command.extend(["--basetemp", str(basetemp)])
    if has_xdist(command[:3], env):
        command.extend(["-n", choose_xdist_workers(env)])
    else:
        print(
            "standing-pytest: pytest-xdist is not active; pytest will run serially "
            "and may exceed runtime budgets. Install or enable with: pip install pytest-xdist",
            file=sys.stderr,
        )
    command.extend(combined_targets(repo_root, extra_pytest_targets))
    return command


def run_standing_pytest(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    basetemp = args.basetemp or default_basetemp(repo_root)
    ensure_external_temp_root(repo_root, basetemp)
    basetemp.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CHARNESS_QUALITY_MODE"] = args.mode
    env["PYTEST_DEBUG_TEMPROOT"] = str(default_temp_root(repo_root, env))
    command = build_pytest_command(
        repo_root,
        basetemp=basetemp,
        include_release_only=args.include_release_only,
        extra_pytest_targets=getattr(args, "extra_pytest_target", []),
        env=env,
    )
    if args.print_command:
        print(shlex.join(command))
        return 0
    result = subprocess.run(command, cwd=repo_root, env=env, check=False)
    if result.returncode == 0 and not args.keep_basetemp:
        shutil.rmtree(basetemp, ignore_errors=True)
    return result.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--mode", choices=("full", "read-only"), default=os.environ.get("CHARNESS_QUALITY_MODE", "full"))
    parser.add_argument("--basetemp", type=Path)
    parser.add_argument("--include-release-only", action="store_true")
    parser.add_argument("--keep-basetemp", action="store_true")
    parser.add_argument(
        "--extra-pytest-target",
        action="append",
        default=[],
        help="Additional pytest path or nodeid appended to the standing target set.",
    )
    parser.add_argument("--print-targets", action="store_true")
    parser.add_argument("--print-expanded-targets", action="store_true")
    parser.add_argument("--print-temp-root", action="store_true")
    parser.add_argument("--print-command", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.print_targets:
        print("\n".join(STANDING_PYTEST_TARGETS))
        return 0
    if args.print_expanded_targets:
        print("\n".join(combined_targets(args.repo_root.resolve(), args.extra_pytest_target)))
        return 0
    if args.print_temp_root:
        temp_root = default_temp_root(args.repo_root.resolve())
        ensure_external_temp_root(args.repo_root.resolve(), temp_root)
        print(temp_root)
        return 0
    return run_standing_pytest(args)


if __name__ == "__main__":
    raise SystemExit(main())
