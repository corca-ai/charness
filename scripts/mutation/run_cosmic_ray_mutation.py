#!/usr/bin/env python3
"""Run the repo-owned Cosmic Ray mutation workflow.

The GitHub Actions adapter calls this wrapper instead of embedding a long
shell pipeline in `mutation_testing.commands.*`.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
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

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

_abort_lib = import_repo_module(__file__, "scripts.mutation.mutation_baseline_abort_lib")
_sampling = import_repo_module(__file__, "scripts.mutation.mutation_sampling_lib")
_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_CONFIG = Path("cosmic-ray.toml")
DEFAULT_SESSION = Path("reports/mutation/cosmic-ray.sqlite")
DEFAULT_DUMP = Path("reports/mutation/cosmic-ray-dump.jsonl")
DEFAULT_FILTER = Path("scripts/mutation/filter_cosmic_ray_mutants.py")
DEFAULT_COVERAGE_JSON = _sampling.DEFAULT_SAMPLE_COVERAGE_JSON
DEFAULT_TIMEOUT_MARKER = Path("reports/mutation/exec-timeout.json")
DEFAULT_EXEC_TIMEOUT_SECONDS = 9000


class _CommandFailure(RuntimeError):
    def __init__(self, returncode: int, command, output: str = ""):  # noqa: ANN001
        super().__init__(f"command exited {returncode}")
        self.returncode = returncode
        self.command = command
        self.output = output


def resolve(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def run(command: list[str], repo_root: Path) -> None:
    sys.stdout.write(f"+ {' '.join(command)}\n")
    sys.stdout.flush()
    try:
        result = _guard.run_process(command, cwd=repo_root, timeout_seconds=None)
    except FileNotFoundError as exc:
        raise SystemExit(
            "cosmic-ray executable not found; install Cosmic Ray 8.4.6 "
            "or run the GitHub Actions workflow install step first"
        ) from exc
    if result.returncode != 0:
        raise _CommandFailure(result.returncode, command, result.stdout + result.stderr)


def _run_baseline(config: Path, repo_root: Path, *, marker_path: Path) -> None:
    """`cosmic-ray baseline`, with its failure RECORDED rather than only raised.

    The raise alone was not enough. `cmd_full` chains this wrapper to the JS slice
    with `&&`, so a baseline failure silently skips JS mutation entirely and the
    summary then reports "StrykerJS JSON report missing" -- the last collateral
    symptom, for a run in which JS mutation was never invoked (#590). The marker is
    the channel the two summary scripts already read; nothing wrote it from here,
    so the collateral branch they carry was unreachable on this path.

    Output is captured so the marker can name the FAILING NODEIDS, then re-emitted
    verbatim to stdout -- a baseline whose log stopped reaching CI would trade one
    diagnosis problem for another.
    """
    command = ["cosmic-ray", "baseline", str(config)]
    sys.stdout.write(f"+ {' '.join(command)}\n")
    sys.stdout.flush()
    try:
        outcome = _guard.run_monitored_phase(
            command,
            cwd=repo_root,
            phase="cosmic-ray-baseline",
            timeout_seconds=None,
            capture=True,
        )
    except FileNotFoundError as exc:
        raise SystemExit(
            "cosmic-ray executable not found; install Cosmic Ray 8.4.6 "
            "or run the GitHub Actions workflow install step first"
        ) from exc
    combined = outcome.stdout + outcome.stderr
    sys.stdout.write(combined)
    sys.stdout.flush()
    if outcome.returncode == 0:
        return
    failing_nodeids = _abort_lib.parse_failed_nodeids(combined)
    _abort_lib.write_baseline_abort_marker(
        marker_path,
        exit_code=outcome.returncode,
        test_command=" ".join(command),
        failing_nodeids=failing_nodeids,
        log_tail=[] if failing_nodeids else _abort_lib.log_tail_lines(combined),
        stage=_abort_lib.STAGE_COSMIC_RAY_BASELINE,
    )
    raise _CommandFailure(outcome.returncode, command, combined)


def _run_exec_with_timeout(
    config: Path,
    session: Path,
    repo_root: Path,
    timeout_seconds: int,
) -> tuple[bool, int]:
    """Run `cosmic-ray exec` with an internal timeout.

    Returns `(timed_out, returncode)`. `returncode` is 0 on clean completion,
    the process exit code on non-zero exit, or `-1` when the internal timeout
    fired. The caller always proceeds to `cosmic-ray dump` afterward so partial
    results survive both timeout AND crash failure modes (the original #183
    fix only covered timeouts).
    """
    command = ["cosmic-ray", "exec", str(config), str(session)]
    sys.stdout.write(f"+ {' '.join(command)} (internal timeout: {timeout_seconds}s)\n")
    sys.stdout.flush()
    try:
        outcome = _guard.run_monitored_phase(
            command,
            cwd=repo_root,
            phase="cosmic-ray-exec",
            timeout_seconds=timeout_seconds,
            capture=False,
        )
    except FileNotFoundError as exc:
        raise SystemExit(
            "cosmic-ray executable not found; install Cosmic Ray 8.4.6 "
            "or run the GitHub Actions workflow install step first"
        ) from exc
    if outcome.timed_out:
        sys.stdout.write(
            f"cosmic-ray exec exceeded {timeout_seconds}s; "
            "continuing to dump so partial results survive\n"
        )
        sys.stdout.flush()
        return True, -1
    if outcome.returncode != 0:
        sys.stdout.write(
            f"cosmic-ray exec exited {outcome.returncode}; "
            "continuing to dump so any completed mutants are still scored\n"
        )
        sys.stdout.flush()
    return False, outcome.returncode


def _write_timeout_marker(marker_path: Path, exec_timeout_seconds: int) -> None:
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(
        json.dumps(
            {
                "exec_timed_out": True,
                "exec_timeout_seconds": exec_timeout_seconds,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _dump_session(session: Path, dump_path: Path, repo_root: Path) -> int:
    """Write `cosmic-ray dump` output atomically.

    Streams the dump into `<dump_path>.partial` and renames on success so a
    crashed dump never leaves a truncated `dump_path` masquerading as a valid
    JSONL file. Returns the dump subprocess's returncode; 0 means the rename
    happened.
    """
    partial = dump_path.with_suffix(dump_path.suffix + ".partial")
    if partial.exists():
        partial.unlink()
    try:
        with partial.open("w", encoding="utf-8") as output:
            saved_stdout = os.dup(1)
            try:
                os.dup2(output.fileno(), 1)
                result = _guard.run_monitored_phase(
                    ["cosmic-ray", "dump", str(session)],
                    cwd=repo_root,
                    phase="cosmic-ray-dump",
                    timeout_seconds=None,
                    capture=False,
                )
            finally:
                os.dup2(saved_stdout, 1)
                os.close(saved_stdout)
    except FileNotFoundError as exc:
        raise SystemExit(
            "cosmic-ray executable not found; install Cosmic Ray 8.4.6 "
            "or run the GitHub Actions workflow install step first"
        ) from exc
    if result.returncode == 0:
        partial.replace(dump_path)
    else:
        sys.stdout.write(
            f"cosmic-ray dump exited {result.returncode}; leaving partial output at {partial}\n"
        )
        sys.stdout.flush()
    return result.returncode


def _read_module_paths(config: Path, repo_root: Path) -> list[Path]:
    """Resolve the configured ``module-path`` files from the Cosmic Ray config.

    The mutation sampler rewrites ``module-path`` in place, so the defensive
    restore must read the *current* list rather than hardcode it. Returns the
    resolved paths, or an empty list (restore degrades to a no-op) when no TOML
    parser is available or the config cannot be parsed -- a missing parser or a
    malformed config never breaks an otherwise-working run, and Cosmic Ray
    surfaces a genuinely broken config itself.
    """
    try:
        import tomllib as toml_reader  # Python 3.11+
    except ModuleNotFoundError:
        try:
            import tomli as toml_reader  # 3.10 backport
        except ModuleNotFoundError:
            sys.stdout.write(
                "no TOML parser (tomllib/tomli) available; defensive module-path restore disabled\n"
            )
            sys.stdout.flush()
            return []
    try:
        data = toml_reader.loads(config.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.stdout.write(f"could not parse {config} for module-path restore: {exc}\n")
        sys.stdout.flush()
        return []
    raw = data.get("cosmic-ray", {}).get("module-path", [])
    if isinstance(raw, str):
        raw = [raw]
    return [resolve(repo_root, Path(entry)) for entry in raw]


def _restore_module_paths(module_paths: list[Path], repo_root: Path) -> None:
    """Best-effort ``git checkout`` of the configured module-path files.

    Cosmic Ray restores a mutated source only BETWEEN work units, so a kill
    mid-unit (external ``timeout``/signal, the internal exec timeout, or a
    worker crash) leaves the in-progress mutant applied in the working tree
    (#262). Restoring the module-path files here guarantees a killed exec never
    leaves a mutated source behind. Best-effort per file: a single failure
    (file absent, ``git`` not on PATH) is logged and never masks the others or
    the run's original exit code.
    """
    if not module_paths:
        return
    for path in module_paths:
        try:
            result = _guard.run_process(
                ["git", "checkout", "--", str(path)], cwd=repo_root, timeout_seconds=None
            )
        except FileNotFoundError:
            sys.stdout.write("git not found; skipping defensive module-path restore\n")
            sys.stdout.flush()
            return
        if result.returncode != 0:
            sys.stdout.write(
                f"defensive restore of {path} exited {result.returncode}: {result.stderr.strip()}\n"
            )
            sys.stdout.flush()
    sys.stdout.write(f"defensively restored {len(module_paths)} module-path file(s)\n")
    sys.stdout.flush()


def _build_restore_handler(module_paths: list[Path], repo_root: Path):
    """Build a SIGINT/SIGTERM handler that defensively restores module-path
    files, then re-raises the signal so the wrapper still dies with
    ``128+signum`` (defensive cleanup, not a swallowed signal)."""

    def _handler(signum, frame):  # noqa: ANN001 - signal handler signature
        _restore_module_paths(module_paths, repo_root)
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    return _handler


def _install_restore_handlers(handler) -> dict:
    """Install ``handler`` for SIGINT/SIGTERM; return the previous handlers so
    the caller can reinstate them in a ``finally``."""
    return {
        signal.SIGINT: signal.signal(signal.SIGINT, handler),
        signal.SIGTERM: signal.signal(signal.SIGTERM, handler),
    }


def _restore_signal_handlers(previous: dict) -> None:
    for signum, handler in previous.items():
        signal.signal(signum, handler)


def _run_full_mode(
    config: Path,
    session: Path,
    dump_path: Path,
    timeout_marker: Path,
    module_paths: list[Path],
    repo_root: Path,
    exec_timeout_seconds: int,
) -> int:
    """Execute mutants and dump results, defensively restoring the module-path
    files on EVERY exec outcome (try/finally) AND on a wrapper interrupt
    (SIGINT/SIGTERM handler) — Cosmic Ray restores a mutated source only between
    work units, so a kill mid-unit otherwise leaves the tree mutated (#262).
    Returns the exit code to propagate (0 = success)."""
    handler = _build_restore_handler(module_paths, repo_root)
    previous_handlers = _install_restore_handlers(handler)
    try:
        exec_timed_out, exec_returncode = _run_exec_with_timeout(
            config, session, repo_root, exec_timeout_seconds
        )
        if exec_timed_out:
            _write_timeout_marker(timeout_marker, exec_timeout_seconds)
        dump_returncode = _dump_session(session, dump_path, repo_root)
        if dump_returncode == 0:
            sys.stdout.write(f"dump written to {dump_path}\n")
        if exec_timed_out:
            sys.stdout.write(
                f"exec-timeout marker written to {timeout_marker}; "
                "downstream summary will report partial-run status\n"
            )
        # Surface the exec crash to the caller AFTER the dump attempt so the
        # downstream summary still has data to score. Dump failure is secondary
        # signal; preserve the original exec failure if both fired.
        if exec_returncode not in (0, -1):
            return exec_returncode
        if dump_returncode != 0:
            return dump_returncode
        return 0
    finally:
        _restore_module_paths(module_paths, repo_root)
        _restore_signal_handlers(previous_handlers)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--dump", type=Path, default=DEFAULT_DUMP)
    parser.add_argument("--filter-script", type=Path, default=DEFAULT_FILTER)
    parser.add_argument("--coverage-json", type=Path, default=DEFAULT_COVERAGE_JSON)
    parser.add_argument("--timeout-marker", type=Path, default=DEFAULT_TIMEOUT_MARKER)
    parser.add_argument(
        "--baseline-abort-marker",
        type=Path,
        default=_abort_lib.DEFAULT_BASELINE_ABORT_MARKER,
        help="Where a failing `cosmic-ray baseline` records the real blocking signal, "
        "so the summary scripts name it instead of the collateral missing-report symptom.",
    )
    parser.add_argument(
        "--exec-timeout-seconds",
        type=int,
        default=DEFAULT_EXEC_TIMEOUT_SECONDS,
        help=(
            "Internal timeout for `cosmic-ray exec` in seconds. Default 9000 (150 min) "
            "leaves headroom under the workflow's 180-minute job ceiling so the "
            "downstream `cosmic-ray dump` always gets a chance to run."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("dry-run", "full"),
        required=True,
        help="dry-run validates baseline/init; full also executes mutants and dumps results.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    config = resolve(repo_root, args.config)
    session = resolve(repo_root, args.session)
    dump_path = resolve(repo_root, args.dump)
    filter_script = resolve(repo_root, args.filter_script)
    coverage_json = resolve(repo_root, args.coverage_json)
    timeout_marker = resolve(repo_root, args.timeout_marker)
    abort_marker = _abort_lib.resolve_baseline_abort_marker(repo_root, args.baseline_abort_marker)

    if not config.is_file():
        sys.stderr.write(f"Cosmic Ray config not found at {config}\n")
        return 2

    module_paths = _read_module_paths(config, repo_root)

    session.parent.mkdir(parents=True, exist_ok=True)
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    if session.exists():
        session.unlink()
    if dump_path.exists():
        dump_path.unlink()
    if timeout_marker.exists():
        timeout_marker.unlink()
    # This wrapper became a marker WRITER, so it must also be a marker CLEARER.
    # Locally `reports/mutation/` persists, and the JS reader treats any marker as
    # "the baseline aborted, so the JS slice never ran" -- a stale one turns a real
    # JS failure into a collateral note that tells the reader to stop looking. That
    # is #590 in mirror image and strictly worse than the symptom it replaced.
    _abort_lib.delete_stale_baseline_abort_marker(abort_marker)

    try:
        _run_baseline(config, repo_root, marker_path=abort_marker)
        run(["cosmic-ray", "init", str(config), str(session)], repo_root)
        if filter_script.is_file():
            filter_command = [
                sys.executable,
                str(filter_script),
                "--repo-root",
                str(repo_root),
                "--session",
                str(session),
            ]
            if coverage_json.is_file():
                filter_command.extend(["--coverage-json", str(coverage_json)])
            if filter_script.resolve() == (repo_root / DEFAULT_FILTER).resolve():
                filter_module = import_repo_module(
                    __file__, "scripts.mutation.filter_cosmic_ray_mutants"
                )
                previous_argv = sys.argv
                try:
                    sys.argv = filter_command[1:]
                    filter_returncode = int(filter_module.main() or 0)
                except SystemExit as exc:
                    filter_returncode = int(exc.code or 0)
                finally:
                    sys.argv = previous_argv
                if filter_returncode != 0:
                    raise _CommandFailure(filter_returncode, filter_command)
            else:
                run(filter_command, repo_root)
        if args.mode == "full":
            failure = _run_full_mode(
                config,
                session,
                dump_path,
                timeout_marker,
                module_paths,
                repo_root,
                args.exec_timeout_seconds,
            )
            if failure:
                return failure
        else:
            sys.stdout.write("dry-run complete after baseline and session init\n")
    except _CommandFailure as exc:
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
