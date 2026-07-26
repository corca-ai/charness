#!/usr/bin/env python3
"""Canonical runner for the repo's standing pytest gate."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
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
# `--maxschedchunk` first shipped as a command-line option in pytest-xdist 3.2.0
# (changelog #855, 2023-02-07). Below that the flag is an unknown option and pytest
# exits 4 before collecting anything, so the floor follows the same rule as
# `usable_cpu_count`: a scheduling tweak must never be why the suite cannot start.
#
# This floor is load-bearing, not theoretical. `packaging/mutation-requirements.txt`
# pins `pytest-xdist>=3,<4`, so 3.0 and 3.1 are both inside the repo's own supported
# range and both predate the flag. A first draft of this constant guessed 2.3 and
# would have passed the flag to exactly those two versions.
MIN_XDIST_FOR_SCHED_CHUNK = (3, 2)


def usable_cpu_count() -> int:
    """CPUs this process may actually run on. The repo's owner for PROCESS WIDTH.

    Deliberately not routed through the quality skill's `runtime_profile_lib`, which
    owns the same stdlib read for a different question. That one is a writer/reader
    CONTRACT -- the recorder stamps a profile id the budget gate looks budgets up
    under, so two derivations there mean two machines. Worker width is a local
    performance choice with no cross-process consumer, and importing a skill module
    for it proved actively worse: this runner is re-entered as a bare child process
    (coverage-instrumented, sys.path[0] elsewhere), where the import raised
    `ModuleNotFoundError` and took the whole gate down over a tuning number.

    Same `OSError` handling as that lib, for the same reason: affinity can be refused
    by a seccomp/LSM policy, and worker width must never be why the suite cannot start.
    """
    try:
        return len(os.sched_getaffinity(0)) or 1
    except (AttributeError, OSError):
        return os.cpu_count() or 1


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
    # The leaf MUST NOT start with "pytest-". This basetemp lives under the shared
    # PYTEST_DEBUG_TEMPROOT/pytest-of-<user> rootdir, and nested pytest runs spawned
    # by tests inherit PYTEST_DEBUG_TEMPROOT and run pytest's numbered-dir cleanup
    # (make_numbered_dir_with_cleanup, prefix "pytest-") over that same rootdir at
    # process exit. pytest's explicit --basetemp branch creates this dir WITHOUT a
    # cleanup lock file, so a "pytest-*" name would be an unlocked deletion candidate
    # and a nested run's exit-time cleanup could rename+remove it — and every live
    # xdist worker's popen-gw* subdir — mid-run, producing mass FileNotFoundError in
    # tmp_path setup. A non-"pytest-" prefix is invisible to that cleanup glob.
    return temp_root / f"pytest-of-{user}" / f"charness-run-{time.time_ns()}"


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

    # Affinity, not the box's total. `os.cpu_count()` answers "how many CPUs does
    # this machine have", never "how many may this process use", so a run under
    # `taskset`, a cpuset, or a container CPU limit spawned 16 workers onto 4 usable
    # CPUs. Measured on this suite: 94.2s at 16 workers vs 64.1s at 4 on the same 4
    # cores -- oversubscription cost 32% of wall and ~76s of CPU. See
    # `usable_cpu_count` above for why this repo keeps a second affinity reader.
    #
    # No `or CAP` fallback: `usable_cpu_count` cannot return falsy, and a fallback to
    # the CAP would mean "we could not tell, so assume the maximum" -- reinstating the
    # exact oversubscription this fix removed, from the branch meant to be safe.
    cpu_count = usable_cpu_count()
    return str(min(cpu_count, DEFAULT_XDIST_WORKER_CAP))


def xdist_version() -> tuple[int, ...]:
    """This interpreter's pytest-xdist version as a tuple, or `()` when unknown.

    Takes no `env`, deliberately: the lookup reads THIS process's installed metadata,
    so the answer is scoped to the runner's interpreter, not to the one
    `CHARNESS_STANDING_PYTEST_PYTHON` may name. An `env` parameter here would advertise
    a targeting this cannot do. `has_xdist` already carries the same same-interpreter
    assumption and handles the mismatch by refusing xdist entirely, which also
    suppresses this flag.

    Deliberately not `packaging.version`: `pyproject.toml` puts the repo root on the
    test-session `sys.path`, and this repo HAS a root `packaging/` directory with no
    `__init__.py`. Importing `packaging` here would resolve to that namespace package
    on any in-repo run and raise on the `.version` attribute -- the exact
    script-basename shadowing the pytest config block warns about, one directory up.
    A leading-digit split is enough for a two-component floor.
    """
    try:
        raw = importlib.metadata.version("pytest-xdist")
    except importlib.metadata.PackageNotFoundError:
        return ()
    parts: list[int] = []
    for chunk in raw.split(".")[:3]:
        digits = ""
        for char in chunk:
            if not char.isdigit():
                break
            digits += char
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def choose_sched_chunk(env: dict[str, str] | None = None) -> str | None:
    """Per-test scheduling granularity for `--dist load`, or None to leave it default.

    `--dist load` does NOT hand tests out one at a time. `LoadScheduling.schedule`
    first gives every worker a CONSECUTIVE chunk of `len(collection) // nworkers // 4`
    -- 85 of this suite's 5445 tests per worker, 1360 pre-assigned -- before any worker
    has reported a single timing, and only the remainder is scheduled on demand.

    Consecutive is the part that hurts, and it is deliberate upstream: contiguous
    chunks preserve pytest's fixture-locality ordering. But this suite's slow tests are
    not scattered, they are ADJACENT -- `tests/charness_cli/` holds the subprocess-heavy
    install/update lifecycle tests and sorts first -- so the pre-assignment reliably
    hands one or two workers a block that is minutes long while the rest get seconds.
    Nothing rebalances it, because those tests were never in the on-demand pool.

    Measured on this suite (36 usable CPUs, 16 workers): 14 of 16 workers finished at
    t=23s and one ran alone to t=109s; the run spent 78s of a 110s wall at one or two
    concurrent tests. `--maxschedchunk 1` floors the initial chunk at 2 per worker and
    schedules the rest on demand; the standing gate went 45.5s -> 26.9s (4.2x -> 11.3x
    effective parallelism).

    Returns "1" rather than a width-derived number because the imbalance this removes
    is not width-dependent: a 4-worker run pre-assigns 340 tests each, which is worse
    per worker, not better. Measured neutral there (64.8s -> 64.5s under `taskset -c
    0-3`) only because 4 workers on 4 CPUs are already saturated -- so there is no
    low-core case to special-case, just no win to claim.

    Scattering does give up some of the fixture locality upstream's chunking buys, and
    the trade is favourable rather than free. The dominant shared state -- the
    `seeded_charness_repo` / `seeded_managed_home` family -- is safe, because it lives
    in `tests/seed_cache.py`'s source-hash-keyed FILESYSTEM cache that every worker
    shares. What does get rebuilt per worker is module-scoped `tmp_path_factory` state
    that never went through that cache, chiefly `seeded_quality_runner_repo` in
    `tests/quality_gates/support.py` (~80 consumers): under contiguous chunks it was
    built once or twice, now up to once per worker. The measured 45.5s -> 26.9s is NET
    of that duplicated setup, so the trade pays -- but seed-cache-backing that fixture
    is the next win here, not a claim that nothing was given up.
    """
    env = os.environ if env is None else env
    override = env.get("CHARNESS_PYTEST_SCHED_CHUNK", "").strip()
    if override:
        if override == "off":
            return None
        try:
            chunk = int(override)
        except ValueError as exc:
            raise SystemExit(
                "standing-pytest: CHARNESS_PYTEST_SCHED_CHUNK must be a positive integer or 'off'"
            ) from exc
        if chunk < 1:
            raise SystemExit("standing-pytest: CHARNESS_PYTEST_SCHED_CHUNK must be >= 1")
        return str(chunk)
    # An operator who already tuned this in PYTEST_ADDOPTS wins: our command-line flag
    # would silently beat theirs, because pytest PREPENDS both PYTEST_ADDOPTS and ini
    # `addopts` to argv, so the later (ours) wins argparse's last-one-wins. Scoped to
    # the env var only: an ini `addopts` tuning is still overridden silently. That is
    # a real gap for a downstream repo using this runner, and no gap for this one --
    # `pyproject.toml` sets no `addopts`.
    if "--maxschedchunk" in env.get("PYTEST_ADDOPTS", ""):
        return None
    if xdist_version() < MIN_XDIST_FOR_SCHED_CHUNK:
        return None
    return "1"


def expand_targets(repo_root: Path, targets: tuple[str, ...] = STANDING_PYTEST_TARGETS) -> list[str]:
    expanded: list[str] = []
    for target in targets:
        if any(char in target for char in "*?["):
            matches = sorted(str(path.relative_to(repo_root)) for path in repo_root.glob(target))
            expanded.extend(matches or [target])
        else:
            expanded.append(target)
    return expanded


def combined_targets(
    repo_root: Path,
    extra_pytest_targets: list[str] | None = None,
    pytest_targets: list[str] | None = None,
) -> list[str]:
    """Resolve the standing target set, optionally replacing it with a focused set."""
    base_targets = list(pytest_targets) if pytest_targets else expand_targets(repo_root)
    return [*base_targets, *(extra_pytest_targets or [])]


def build_pytest_command(
    repo_root: Path,
    *,
    basetemp: Path,
    include_release_only: bool,
    extra_pytest_targets: list[str] | None = None,
    pytest_targets: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> list[str]:
    env = os.environ if env is None else env
    command = [*choose_pytest_command(env), "-q"]
    if not include_release_only:
        command.extend(["-m", "not release_only"])
    command.extend(["--basetemp", str(basetemp)])
    if has_xdist(command[:3], env):
        command.extend(["-n", choose_xdist_workers(env)])
        sched_chunk = choose_sched_chunk(env)
        if sched_chunk is not None:
            command.extend(["--maxschedchunk", sched_chunk])
    else:
        print(
            "standing-pytest: pytest-xdist is not active; pytest will run serially "
            "and may exceed runtime budgets. Install or enable with: pip install pytest-xdist",
            file=sys.stderr,
        )
    command.extend(combined_targets(repo_root, extra_pytest_targets, pytest_targets))
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
        pytest_targets=getattr(args, "pytest_target", []),
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
        "--pytest-target",
        action="append",
        default=[],
        help=(
            "Focused pytest path or nodeid replacing the standing target set; repeat for "
            "multiple targets while retaining xdist and temp isolation."
        ),
    )
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
        print(
            "\n".join(
                combined_targets(
                    args.repo_root.resolve(), args.extra_pytest_target, args.pytest_target
                )
            )
        )
        return 0
    if args.print_temp_root:
        temp_root = default_temp_root(args.repo_root.resolve())
        ensure_external_temp_root(args.repo_root.resolve(), temp_root)
        print(temp_root)
        return 0
    return run_standing_pytest(args)


if __name__ == "__main__":
    raise SystemExit(main())
