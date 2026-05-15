#!/usr/bin/env python3
"""Run the repo-owned Cosmic Ray mutation workflow.

The GitHub Actions adapter calls this wrapper instead of embedding a long
shell pipeline in `mutation_testing.commands.*`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path("cosmic-ray.toml")
DEFAULT_SESSION = Path("reports/mutation/cosmic-ray.sqlite")
DEFAULT_DUMP = Path("reports/mutation/cosmic-ray-dump.jsonl")
DEFAULT_FILTER = Path("scripts/filter_cosmic_ray_mutants.py")


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--dump", type=Path, default=DEFAULT_DUMP)
    parser.add_argument("--filter-script", type=Path, default=DEFAULT_FILTER)
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

    if not config.is_file():
        sys.stderr.write(f"Cosmic Ray config not found at {config}\n")
        return 2

    session.parent.mkdir(parents=True, exist_ok=True)
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    if session.exists():
        session.unlink()
    if dump_path.exists():
        dump_path.unlink()

    try:
        run(["cosmic-ray", "baseline", str(config)], repo_root)
        run(["cosmic-ray", "init", str(config), str(session)], repo_root)
        if filter_script.is_file():
            run(["python3", str(filter_script), "--repo-root", str(repo_root), "--session", str(session)], repo_root)
        if args.mode == "full":
            run(["cosmic-ray", "exec", str(config), str(session)], repo_root)
            with dump_path.open("w", encoding="utf-8") as output:
                subprocess.run(
                    ["cosmic-ray", "dump", str(session)],
                    cwd=repo_root,
                    check=True,
                    stdout=output,
                    text=True,
                )
            sys.stdout.write(f"dump written to {dump_path}\n")
        else:
            sys.stdout.write("dry-run complete after baseline and session init\n")
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
