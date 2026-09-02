#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


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

_EARLY_BYTECODE_GUARD = not sys.dont_write_bytecode
if _EARLY_BYTECODE_GUARD:
    # The target is only known after argparse. Do not let an inherited local
    # prefix write the launcher/importer caches into that target in the meantime.
    sys.dont_write_bytecode = True

from scripts.runtime_bootstrap import (  # noqa: E402
    configure_runtime_environment,
    import_repo_module,
)
from scripts.yaml_output import emit_yaml  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a command in an isolated worktree with external runtime caches."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--allow-main",
        action="store_true",
        help="Allow an intentional command in the primary worktree; parent writes are then possible.",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command after `--`.")
    args = parser.parse_args()
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    try:
        configure_runtime_environment(args.repo_root)
        lib = import_repo_module(__file__, "scripts.worktree.worktree_exec_lib")
        return lib.run_exec(args.repo_root, command, allow_main=args.allow_main)
    except (RuntimeError, ImportError, OSError) as exc:
        emit_yaml(
            {
                "status": "fail",
                "repo_root": str(args.repo_root.resolve()),
                "command": command,
                "error": str(exc),
            }
        )
        return 2
    finally:
        if _EARLY_BYTECODE_GUARD:
            sys.dont_write_bytecode = False


if __name__ == "__main__":
    sys.exit(main())
