#!/usr/bin/env python3
"""Offline prompt-surface mutation generator (S1 of the prompt-mutation-pilot
goal, charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md).

A RANKING + scenario-coverage tool, never a deletion prover: `split` cuts a
skill's SKILL.md + references into section-level mutation units (a stable,
content-addressed manifest); `generate` builds one throwaway mutant git commit
per selected unit -- with that unit's section removed from the installed-
plugin mirror tree (`plugins/charness/skills/<skill>/**`, the surface
`capture-skill-run.sh` actually resolves) -- on a `refs/prompt-mutants/...`
namespace, using object-database plumbing ONLY; `cleanup` deletes those refs
once downstream capture experiments are done. See prompt_mutant_lib.py for the
splitting algorithm and git-plumbing mechanics; this module is CLI wiring only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from prompt_mutant_lib import (
    PromptMutantError,
    build_split_manifest,
    cleanup_mutant_refs,
    generate_mutants,
    list_skill_files_worktree,
    read_worktree_file,
)

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
GRANULARITY_CHOICES = ["section"]


def _cmd_split(args: argparse.Namespace) -> int:
    try:
        manifest = build_split_manifest(
            args.repo_root, args.skill, args.granularity, list_skill_files_worktree, read_worktree_file
        )
    except PromptMutantError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    try:
        result = generate_mutants(args.repo_root, args.skill, args.baseline_ref, args.unit_id or None)
    except PromptMutantError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "skill": result["skill"],
                "baseline_sha": result["baseline_sha"],
                "unit_count": len(result["units"]),
                "out": str(args.out),
            },
            ensure_ascii=False,
        )
    )
    return 0


def _cmd_cleanup(args: argparse.Namespace) -> int:
    deleted = cleanup_mutant_refs(args.repo_root, args.skill)
    print(json.dumps({"skill": args.skill, "deleted": deleted}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Split a skill's prompt surface into section-level mutation units and build/cleanup "
            "throwaway mutant git refs over the installed-plugin mirror tree. Advisory tooling for "
            "the prompt-mutation-pilot goal; never a commit/CI gate."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    split_parser = subparsers.add_parser(
        "split", help="Split a skill's prompt surface into mutation units and print a manifest."
    )
    split_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    split_parser.add_argument("--skill", required=True)
    split_parser.add_argument("--granularity", choices=GRANULARITY_CHOICES, default="section")
    split_parser.add_argument(
        "--json", action="store_true", help="Present for CLI-shape compatibility; output is always JSON."
    )
    split_parser.set_defaults(func=_cmd_split)

    generate_parser = subparsers.add_parser(
        "generate", help="Build one mutant commit per selected unit against a baseline ref."
    )
    generate_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    generate_parser.add_argument("--skill", required=True)
    generate_parser.add_argument("--baseline-ref", required=True)
    generate_parser.add_argument(
        "--unit-id", action="append", default=[], help="Repeatable; defaults to every unit of --skill."
    )
    generate_parser.add_argument("--out", type=Path, required=True, help="Where to write the mutation manifest JSON.")
    generate_parser.set_defaults(func=_cmd_generate)

    cleanup_parser = subparsers.add_parser("cleanup", help="Delete all refs/prompt-mutants/<skill>/* refs.")
    cleanup_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    cleanup_parser.add_argument("--skill", required=True)
    cleanup_parser.set_defaults(func=_cmd_cleanup)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.repo_root = args.repo_root.resolve()
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
