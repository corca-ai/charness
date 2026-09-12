"""Command-line adapter for the runtime scratch registry."""

from __future__ import annotations

import argparse
from pathlib import Path
from types import ModuleType


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and reclaim Charness-owned runtime scratch roots.")
    parser.add_argument("command", choices=("inspect", "gc", "recover"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--max-roots", type=int, default=256)
    parser.add_argument("--max-entries", type=int, default=100_000)
    parser.add_argument("--execute", action="store_true", help="GC: remove eligible expired scratch roots")
    return parser


def main(core: ModuleType, argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.max_roots <= 0 or args.max_entries <= 0:
        raise SystemExit("--max-roots and --max-entries must be positive")
    options = {
        "runtime_root_path": args.runtime_root,
        "max_roots": args.max_roots,
        "max_entries": args.max_entries,
    }
    if args.command == "inspect":
        payload = core.inspect_scratch_roots(args.repo_root, **options)
    elif args.command == "gc":
        payload = core.gc_scratch_roots(args.repo_root, dry_run=not args.execute, **options)
    else:
        payload = core.recover_scratch_roots(args.repo_root, dry_run=not args.execute, **options)
    yaml_output = core.import_repo_module(__file__, "scripts.yaml_output")
    yaml_output.emit_yaml(payload)
    return 0
