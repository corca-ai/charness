#!/usr/bin/env python3
"""CLI wrapper around ``check_prescribed_skill_executed_lib.check``.

See ``docs/prescribed-skill-closeout-contract.md`` for the closeout
contract this gate enforces across achieve/issue/release closeouts.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def _load_lib():
    lib_path = Path(__file__).resolve().with_name("check_prescribed_skill_executed_lib.py")
    spec = importlib.util.spec_from_file_location("check_prescribed_skill_executed_lib", lib_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {lib_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LIB = _load_lib()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gate that the prescribed sub-skill for a closeout was executed "
            "(an existing non-empty evidence file) or explicitly skipped with "
            "an enum-valid reason."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root for resolving relative evidence paths")
    parser.add_argument("--kind", default=None, help="Optional closeout kind label for the report (e.g. achieve-after, issue-resolution, release)")
    parser.add_argument("--require", action="append", default=[], metavar="NAME", help="Required evidence name (repeatable)")
    parser.add_argument("--evidence", action="append", default=[], metavar="NAME:PATH", help="Evidence file path for a required name (repeatable)")
    parser.add_argument("--skip", action="append", default=[], metavar="NAME:REASON", help="Skip reason for a required name (repeatable); REASON must start with one of host-blocked-subagent, host-log-not-exposed, evaluator-unavailable")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout (default true; flag retained for parity)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.require:
        print(json.dumps({"ok": False, "error": "no --require names supplied"}, ensure_ascii=False, sort_keys=True))
        return 2
    try:
        evidence = dict(LIB.parse_evidence_arg(raw) for raw in args.evidence)
        skips = dict(LIB.parse_skip_arg(raw) for raw in args.skip)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    result = LIB.check(
        repo_root=args.repo_root.expanduser().resolve(),
        required=args.require,
        evidence=evidence,
        skips=skips,
        kind=args.kind,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
