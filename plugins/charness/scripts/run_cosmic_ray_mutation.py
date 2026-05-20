#!/usr/bin/env python3
"""Run the repo-owned Cosmic Ray mutation workflow.

The GitHub Actions adapter calls this wrapper instead of embedding a long
shell pipeline in `mutation_testing.commands.*`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path("cosmic-ray.toml")
DEFAULT_SESSION = Path("reports/mutation/cosmic-ray.sqlite")
DEFAULT_DUMP = Path("reports/mutation/cosmic-ray-dump.jsonl")
DEFAULT_FILTER = Path("scripts/filter_cosmic_ray_mutants.py")
DEFAULT_TIMEOUT_MARKER = Path("reports/mutation/exec-timeout.json")
DEFAULT_EXEC_TIMEOUT_SECONDS = 9000


def resolve(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def run(command: list[str], repo_root: Path) -> None:
    sys.stdout.write(f"+ {' '.join(command)}\n")
    sys.stdout.flush()
    try:
        subprocess.run(command, cwd=repo_root, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "cosmic-ray executable not found; install Cosmic Ray 8.4.6 "
            "or run the GitHub Actions workflow install step first"
        ) from exc


def _run_exec_with_timeout(
    config: Path,
    session: Path,
    repo_root: Path,
    timeout_seconds: int,
) -> bool:
    """Run `cosmic-ray exec` with an internal timeout.

    Returns True when exec finished cleanly within `timeout_seconds`. Returns
    False when the timeout fired so callers can flip the partial-run flag.
    Other failures still propagate via CalledProcessError.
    """
    command = ["cosmic-ray", "exec", str(config), str(session)]
    sys.stdout.write(f"+ {' '.join(command)} (internal timeout: {timeout_seconds}s)\n")
    sys.stdout.flush()
    try:
        subprocess.run(command, cwd=repo_root, check=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        sys.stdout.write(
            f"cosmic-ray exec exceeded {timeout_seconds}s; "
            "continuing to dump so partial results survive\n"
        )
        sys.stdout.flush()
        return False
    except FileNotFoundError as exc:
        raise SystemExit(
            "cosmic-ray executable not found; install Cosmic Ray 8.4.6 "
            "or run the GitHub Actions workflow install step first"
        ) from exc
    return True


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--dump", type=Path, default=DEFAULT_DUMP)
    parser.add_argument("--filter-script", type=Path, default=DEFAULT_FILTER)
    parser.add_argument("--timeout-marker", type=Path, default=DEFAULT_TIMEOUT_MARKER)
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
    timeout_marker = resolve(repo_root, args.timeout_marker)

    if not config.is_file():
        sys.stderr.write(f"Cosmic Ray config not found at {config}\n")
        return 2

    session.parent.mkdir(parents=True, exist_ok=True)
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    if session.exists():
        session.unlink()
    if dump_path.exists():
        dump_path.unlink()
    if timeout_marker.exists():
        timeout_marker.unlink()

    try:
        run(["cosmic-ray", "baseline", str(config)], repo_root)
        run(["cosmic-ray", "init", str(config), str(session)], repo_root)
        if filter_script.is_file():
            run(["python3", str(filter_script), "--repo-root", str(repo_root), "--session", str(session)], repo_root)
        if args.mode == "full":
            exec_completed = _run_exec_with_timeout(
                config, session, repo_root, args.exec_timeout_seconds
            )
            if not exec_completed:
                _write_timeout_marker(timeout_marker, args.exec_timeout_seconds)
            with dump_path.open("w", encoding="utf-8") as output:
                subprocess.run(
                    ["cosmic-ray", "dump", str(session)],
                    cwd=repo_root,
                    check=True,
                    stdout=output,
                    text=True,
                )
            sys.stdout.write(f"dump written to {dump_path}\n")
            if not exec_completed:
                sys.stdout.write(
                    f"exec-timeout marker written to {timeout_marker}; "
                    "downstream summary will report partial-run status\n"
                )
        else:
            sys.stdout.write("dry-run complete after baseline and session init\n")
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
