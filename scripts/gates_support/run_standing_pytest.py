#!/usr/bin/env python3
"""Canonical runner for the repo's standing pytest gate."""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import os
import shlex
import shutil
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

_EARLY_BYTECODE_GUARD = not sys.dont_write_bytecode
if _EARLY_BYTECODE_GUARD:
    # Python chooses a source module's cache path before executing that module.
    # Hold this guard only across the first bootstrap import; that bootstrap
    # installs the external prefix, after which normal bytecode caching is safe.
    sys.dont_write_bytecode = True

try:
    from scripts.runtime_bootstrap import configure_runtime_environment, import_repo_module
except ImportError:  # pragma: no cover - exercised by the coverage-producer test
    # `coverage run <abspath>` puts the CWD on `sys.path`, not the script's own
    # directory, and `check_changed_line_mutation_coverage` invokes this runner
    # exactly that way from a foreign cwd. Direct invocation finds the sibling;
    # that path does not.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from scripts.runtime_bootstrap import (  # type: ignore[no-redef]
        configure_runtime_environment,
        import_repo_module,
    )

# The repo's ONE child-process owner. Imported through the bootstrap rather than
# `from scripts...` because this script is run directly as often as it is
# imported, and a plain package import fails in the direct-invocation case.
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
if _EARLY_BYTECODE_GUARD:
    sys.dont_write_bytecode = False
heartbeat_interval_from_env = _subprocess_guard.heartbeat_interval_from_env
run_monitored_phase = _subprocess_guard.run_monitored_phase

_quality_universes = import_repo_module(__file__, "scripts.adapters.quality_universes_lib")
_quality_adapter = import_repo_module(__file__, "scripts.adapters.quality_adapter_lib")
DEFAULT_UNIVERSES = _quality_universes.DEFAULT_UNIVERSES
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe
load_quality_adapter = _quality_adapter.load_quality_adapter

# The basetemp lifecycle moved out whole (S6) when this file crossed its length
# cap; `standing_pytest_basetemp` owns where a run's scratch tree lives and what
# survives it.
#
# EXACTLY the names this module's own body calls, and no more. A first draft
# re-bound six further names and justified the block by claiming
# `check_changed_line_mutation_coverage` and the quality runner import
# `default_basetemp` through here; a round-1 reviewer measured that neither does
# -- both reach the runner through its CLI. Each unread alias is a live trap: it
# looks like the seam a test should patch while nothing reads it, which is how a
# monkeypatch ends up binding nothing and a test passes while asserting nothing.
# Import from `standing_pytest_basetemp` directly for anything not listed here.
# The run-record and signal halves of "outlive your caller" (S6 round 2), same
# re-export discipline as the basetemp block below: only what this body calls.
_survival = import_repo_module(__file__, "scripts.gates_support.standing_pytest_run_record")
RUN_RECORD_DIR = _survival.RUN_RECORD_DIR
HEARTBEAT_INTERVAL_ENV = _survival.HEARTBEAT_INTERVAL_ENV
run_record_path = _survival.run_record_path
write_run_record = _survival.write_run_record
_heartbeat_seconds = _survival._heartbeat_seconds
_terminate_reaps_the_child = _survival._terminate_reaps_the_child

_basetemp = import_repo_module(__file__, "scripts.gates_support.standing_pytest_basetemp")
_FAILED_BASETEMP_MARKER = _basetemp._FAILED_BASETEMP_MARKER
_KEPT_BASETEMP_MARKER = _basetemp._KEPT_BASETEMP_MARKER
default_temp_root = _basetemp.default_temp_root
default_pytest_cache_dir = _basetemp.default_pytest_cache_dir
ensure_external_temp_root = _basetemp.ensure_external_temp_root
default_basetemp = _basetemp.default_basetemp
prune_failed_basetemps = _basetemp.prune_failed_basetemps
_failed_basetemp_keep = _basetemp._failed_basetemp_keep
_hold_basetemp_lock = _basetemp._hold_basetemp_lock
_mark_basetemp = _basetemp._mark_basetemp

STANDING_PYTEST_TARGETS = (
    "tests/quality_gates",
    "tests/control_plane",
    "tests/test_*.py",
    "tests/charness_cli",
    # `tests/test_*.py` is a FLAT glob: it does not reach a subdirectory. A suite added
    # under `tests/<dir>/` and not named here runs under a bare `pytest` and is invisible
    # to the standing command -- and the mutation-coverage producer instruments THIS
    # command, so such a suite contributes no coverage to the changed-line gate while
    # looking green locally. That is the shape that lets a whole directory of tests exist
    # and prove nothing; `check_test_completeness.py` reports the gap, and this is the
    # line that closes it.
    "tests/coverage_debt",
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

_environment = import_repo_module(__file__, "scripts.gates_support.standing_pytest_environment")


def usable_cpu_count() -> int:
    """Compatibility seam for tests and callers that patch process width."""
    return _environment.usable_cpu_count()


def choose_pytest_command(env: dict[str, str] | None = None) -> list[str]:
    env = os.environ if env is None else env
    if importlib.util.find_spec("pytest") is not None:
        python = (
            env.get("CHARNESS_STANDING_PYTEST_PYTHON", sys.executable).strip() or sys.executable
        )
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
    current_python_pytest = [
        env.get("CHARNESS_STANDING_PYTEST_PYTHON", sys.executable).strip() or sys.executable,
        "-m",
        "pytest",
    ]
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
    """Compatibility seam for tests and callers that patch xdist detection."""
    return _environment.xdist_version()


def choose_sched_chunk(env: dict[str, str] | None = None) -> tuple[str | None, str | None]:
    """`(chunk, suppression_reason)` for `--dist load`; chunk None means leave default.

    Returns the REASON alongside the value because suppression is not a neutral
    fallback here: this repo's `pytest` and `run-quality-*` runtime bars are sized for
    the scheduled-on-demand regime, and a suppressed flag puts the gate back on the
    ~52s path where those bars go red having regressed nothing. Three of the four
    suppression paths are involuntary (old xdist, an unrelated `PYTEST_ADDOPTS`
    tuning), so without a reason the operator sees only "run-quality-full exceeded its
    budget" with no pointer to the cause. `build_pytest_command` prints it, mirroring
    the stderr warning the `has_xdist` branch already prints for the same reason.

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
    shares. `seeded_quality_runner_repo` now uses that same source-hash cache and every
    test mutates an isolated clone, so scattering no longer pays a per-worker rebuild
    of the shared quality-runner seed. Other module-scoped fixtures can still give up
    locality; the measured 45.5s -> 26.9s remains a net observation, not a claim that
    scattering is free.
    """
    env = os.environ if env is None else env
    override = env.get("CHARNESS_PYTEST_SCHED_CHUNK", "").strip()
    if override:
        if override == "off":
            return None, "CHARNESS_PYTEST_SCHED_CHUNK=off"
        try:
            chunk = int(override)
        except ValueError as exc:
            raise SystemExit(
                "standing-pytest: CHARNESS_PYTEST_SCHED_CHUNK must be a positive integer or 'off'"
            ) from exc
        if chunk < 1:
            raise SystemExit("standing-pytest: CHARNESS_PYTEST_SCHED_CHUNK must be >= 1")
        return str(chunk), None
    # An operator who already tuned this in PYTEST_ADDOPTS wins: our command-line flag
    # would silently beat theirs, because pytest PREPENDS both PYTEST_ADDOPTS and ini
    # `addopts` to argv, so the later (ours) wins argparse's last-one-wins. Scoped to
    # the env var only: an ini `addopts` tuning is still overridden silently. That is
    # a real gap for a downstream repo using this runner, and no gap for this one --
    # `pyproject.toml` sets no `addopts`.
    if "--maxschedchunk" in env.get("PYTEST_ADDOPTS", ""):
        return None, "PYTEST_ADDOPTS already sets --maxschedchunk"
    installed = xdist_version()
    if installed < MIN_XDIST_FOR_SCHED_CHUNK:
        shown = ".".join(str(part) for part in installed) if installed else "unknown"
        return (
            None,
            f"pytest-xdist {shown} is below {'.'.join(str(p) for p in MIN_XDIST_FOR_SCHED_CHUNK)}",
        )
    return "1", None


def _resolved_standing_targets(repo_root: Path) -> tuple[str, ...]:
    adapter = load_quality_adapter(repo_root)
    if adapter.get("valid") is False:
        errors = "; ".join(str(error) for error in adapter.get("errors", []))
        raise SystemExit(f"pytest: quality adapter is invalid{f': {errors}' if errors else '.'}")
    universe = resolve_universe(
        adapter,
        "pytest_targets",
        default=DEFAULT_UNIVERSES["pytest_targets"],
    )
    files = matching_files(repo_root, universe)
    refusal = refuse_if_declared_and_empty(universe, files, "pytest")
    if refusal is not None:
        raise SystemExit(refusal)
    if not files and not universe.declared:
        patterns = ", ".join(universe.patterns) or "<empty>"
        print(
            f"pytest: discovered empty pytest_targets universe (patterns: {patterns}); "
            "the standing target set is unestablished.",
            file=sys.stderr,
        )
    return universe.patterns


def expand_targets(repo_root: Path, targets: tuple[str, ...] | None = None) -> list[str]:
    if targets is None:
        targets = _resolved_standing_targets(repo_root)
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
        # `slow_corpus` rides the same switch as `release_only` rather than getting its
        # own flag: both name "runs in the FULL lane, not the standing one", and the
        # release lane already turns this switch off. A second flag would let the two
        # drift into a lane that runs neither.
        command.extend(["-m", "not release_only and not slow_corpus"])
    command.extend(["--basetemp", str(basetemp)])
    pytest_cache_dir = default_pytest_cache_dir(repo_root, env)
    ensure_external_temp_root(repo_root, pytest_cache_dir)
    command.extend(["-o", f"cache_dir={pytest_cache_dir}"])
    if has_xdist(command[:3], env):
        command.extend(["-n", choose_xdist_workers(env)])
        sched_chunk, suppression_reason = choose_sched_chunk(env)
        if sched_chunk is not None:
            command.extend(["--maxschedchunk", sched_chunk])
        else:
            print(
                f"standing-pytest: per-test scheduling is off ({suppression_reason}); xdist will "
                "pre-assign contiguous test blocks and the suite will run substantially slower, "
                "which can exceed runtime budgets sized for the scheduled regime",
                file=sys.stderr,
            )
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
    configure_runtime_environment(repo_root)
    runner_owned_basetemp = args.basetemp is None
    basetemp = args.basetemp or default_basetemp(repo_root)
    ensure_external_temp_root(repo_root, basetemp)
    basetemp.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CHARNESS_QUALITY_MODE"] = args.mode
    env["PYTEST_DEBUG_TEMPROOT"] = str(default_temp_root(repo_root, env))
    # Read by `tests/conftest.py`'s bare-run guard so this runner's SERIAL fallback
    # (old xdist, a `-p no:xdist` in PYTEST_ADDOPTS) is not mistaken for a bare
    # `python3 -m pytest`. Deliberately a dedicated name: `PYTEST_DEBUG_TEMPROOT`
    # cannot serve, because it survives in any shell descended from a run that set
    # it, which is the ambient-runner-state class `_scrub_ambient_runner_state`
    # already exists for.
    env["CHARNESS_STANDING_PYTEST"] = "1"
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
    lock_context = (
        _hold_basetemp_lock(basetemp) if runner_owned_basetemp else contextlib.nullcontext()
    )
    with lock_context:
        write_run_record(repo_root, {"state": "running", "command": shlex.join(command)})
        # SC11. This was a bare `subprocess.run` -- the repo's LONGEST child on a
        # plain call with no session, no heartbeat, and no group kill, while the
        # monitored primitive it needed already shipped and had three other
        # callers. Two full-suite runs were lost to exactly that: an agent's
        # wrapper timed out, the pytest process tree was never tracked, and ~20
        # minutes went with it, twice.
        #
        # `capture=False` is the load-bearing argument and the reason this needed
        # a new mode rather than a swap -- but NOT for the reason first written
        # here. The first comment said capturing would trade a watchable suite
        # for a silent one; round 2 measured that under `run-quality.sh`, the
        # dominant caller, every check already runs in a subshell redirected to a
        # log file, so there is no live progress for an operator to watch either
        # way. The real argument: with `capture=True` the body is buffered into
        # `PhaseOutcome.stdout`, and this runner never prints `outcome.stdout` --
        # so the entire pytest body would be DISCARDED on failure, which is the
        # one moment it is needed. Direct invocation additionally keeps its live
        # progress, which is a real but secondary gain.
        #
        # `timeout_seconds` stays None by DEFAULT. Imposing a bound here would
        # kill legitimate long runs, and the loss this repairs was never caused by
        # the absence of a bound -- it was caused by an untracked tree. What the
        # monitored shape buys unconditionally is the part that was missing: the
        # child owns its session, so a kill reaps every xdist worker instead of
        # orphaning them, and the heartbeat makes a live run distinguishable from
        # a hung one.
        #
        # `_terminate_reaps_the_child` is what keeps that session from becoming a
        # NEW leak, and it is not optional. This runner is usually NESTED: both
        # `run-quality.sh` (which queues it) and the closeout/release lanes wrap
        # their child in a bounded `run_monitored_phase` of their own. The
        # child's own session puts it OUTSIDE the outer guard's process group, so
        # an outer 1800s kill would take this runner down and leave a 16-worker
        # pytest tree running unattended -- the same orphaned tree SC11 exists to
        # prevent, arriving by a new route. A round-1 reviewer found this; the
        # handler turns SIGTERM into an exception so the guard's own
        # `except BaseException: _kill_tree` reaps the tree on the way out.
        try:
            with _terminate_reaps_the_child():
                outcome = run_monitored_phase(
                    command,
                    cwd=repo_root,
                    phase="standing-pytest",
                    timeout_seconds=args.timeout_seconds,
                    heartbeat_seconds=_heartbeat_seconds(),
                    env=env,
                    capture=False,
                )
        except BaseException:
            # A record saying `running` forever is worse than no record: a later
            # session cannot tell a live run from a corpse, which is the exact
            # ambiguity this record exists to remove. Mark the basetemp too, or
            # every interrupted run leaks one permanently -- `prune_failed_basetemps`
            # only considers roots carrying the failed marker.
            write_run_record(
                repo_root,
                {
                    "state": "interrupted",
                    "command": shlex.join(command),
                    "returncode": None,
                    "timed_out": False,
                    "basetemp": str(basetemp),
                },
            )
            if runner_owned_basetemp:
                _mark_basetemp(basetemp, _FAILED_BASETEMP_MARKER)
            raise
        returncode = outcome.returncode
        write_run_record(
            repo_root,
            {
                "state": "timed-out" if outcome.timed_out else "finished",
                "command": shlex.join(command),
                "returncode": returncode,
                "elapsed_seconds": outcome.elapsed_seconds,
                "timed_out": outcome.timed_out,
                # The basetemp is the run's own artifact directory, and on a
                # failure it is KEPT. Recording it is what makes a run whose
                # caller died still diagnosable.
                "basetemp": str(basetemp),
            },
        )
        if outcome.timed_out:
            print(outcome.stderr.strip() or "the standing pytest run timed out", file=sys.stderr)
        if returncode == 0 and not args.keep_basetemp:
            shutil.rmtree(basetemp, ignore_errors=True)
        elif returncode == 0:
            _mark_basetemp(basetemp, _KEPT_BASETEMP_MARKER)
        elif runner_owned_basetemp:
            _mark_basetemp(basetemp, _FAILED_BASETEMP_MARKER)
        if runner_owned_basetemp:
            prune_failed_basetemps(
                basetemp.parent,
                current_failed=basetemp if returncode != 0 else None,
                keep=_failed_basetemp_keep(env),
            )
    return returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--mode",
        choices=("full", "read-only"),
        default=os.environ.get("CHARNESS_QUALITY_MODE", "full"),
    )
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
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help=(
            "Kill the whole pytest process group after this many seconds and report the "
            "timeout as a result. Unbounded by default: the standing suite is a legitimate "
            "multi-minute run, and a bound short enough to catch a hang is short enough to "
            "kill a healthy one."
        ),
    )
    parser.add_argument(
        "--print-last-run",
        action="store_true",
        help=(
            "Print the record of the most recent run and exit. Reads back a run whose "
            "caller died before it could report -- the case a wrapper timeout creates."
        ),
    )
    parser.add_argument("--print-targets", action="store_true")
    parser.add_argument("--print-expanded-targets", action="store_true")
    parser.add_argument("--print-temp-root", action="store_true")
    parser.add_argument("--print-command", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.print_last_run:
        path = run_record_path(args.repo_root.resolve())
        if not path.exists():
            print(f"no standing-pytest run record at {path}", file=sys.stderr)
            return 1
        print(path.read_text(encoding="utf-8"), end="")
        return 0
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
