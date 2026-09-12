#!/usr/bin/env python3
"""Run one command beneath a receipt-bound scratch owner.

This is the standalone adapter for shell producers.  The quality runner passes
an already-open parent root directly; standalone invocations use this adapter so
the same shell command gets a real receipt and lock instead of inventing local
cleanup state.
"""

from __future__ import annotations

import argparse
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

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_scratch = import_repo_module(__file__, "scripts.runtime_scratch")
_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
owned_scratch = _scratch.owned_scratch
run_monitored_phase = _guard.run_monitored_phase


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--producer", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser


def _exit_code(returncode: int) -> int:
    return 128 + -returncode if returncode < 0 else returncode


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    command = list(args.command)
    if command[:1] == ["--"]:
        command.pop(0)
    if not command:
        raise SystemExit("run-owned-scratch-command: a command is required after --")
    owner = owned_scratch(args.repo_root, args.producer)
    returncode = 1
    try:
        root = owner.open()
        environment = os.environ.copy()
        environment["CHARNESS_OWNED_SCRATCH_ROOT"] = str(root)
        result = run_monitored_phase(
            command,
            cwd=args.repo_root.resolve(),
            env=environment,
            phase=f"owned-scratch:{args.producer}",
            timeout_seconds=args.timeout_seconds,
        )
        sys.stdout.write(result.stdout or "")
        sys.stderr.write(result.stderr or "")
        returncode = _exit_code(int(result.returncode))
    except KeyboardInterrupt:
        returncode = 130
    except BaseException:
        returncode = 130
        raise
    finally:
        try:
            owner.close(state="failed" if returncode else "succeeded")
        except Exception as exc:  # cleanup never replaces the child's verdict
            print(f"run-owned-scratch-command: warning: owner cleanup failed: {exc}", file=sys.stderr)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
