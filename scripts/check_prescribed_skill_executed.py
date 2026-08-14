#!/usr/bin/env python3
"""CLI wrapper around ``check_prescribed_skill_executed_lib.check``.

See ``docs/prescribed-skill-closeout-contract.md`` for the closeout
contract this gate enforces across achieve/issue/release closeouts.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from yaml_output import emit_yaml


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
    parser.add_argument("--context-token", action="append", default=[], metavar="TOKEN", help="Closeout context identity (issue number, goal slug, release version; repeatable). Every evidence file must bind to at least one, by basename or by cited content. Omitting these leaves the run presence-only, which the report records as binding_checked=false.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.require:
        emit_yaml({"ok": False, "error": "no --require names supplied"})
        return 2
    try:
        evidence = dict(LIB.parse_evidence_arg(raw) for raw in args.evidence)
        skips = dict(LIB.parse_skip_arg(raw) for raw in args.skip)
    except ValueError as exc:
        emit_yaml({"ok": False, "error": str(exc)})
        return 2
    result = LIB.check(
        repo_root=args.repo_root.expanduser().resolve(),
        required=args.require,
        evidence=evidence,
        skips=skips,
        kind=args.kind,
        tokens=args.context_token,
    )
    emit_yaml(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
