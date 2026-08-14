#!/usr/bin/env python3
"""Offline prompt-surface mutation generator (S1 of the prompt-mutation-pilot
goal, charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md).

A RANKING + scenario-coverage tool, never a deletion prover: `split` cuts a
skill's SKILL.md + references into mutation units (a stable,
content-addressed manifest); `generate` builds one throwaway parentless
snapshot commit per selected unit -- either removing the unit or rewriting it
in place with provided replacement text, always on the installed-plugin mirror
tree (`plugins/charness/skills/<skill>/**`, the surface `capture-skill-run.sh`
actually resolves) -- and returns raw snapshot SHAs only; `cleanup` deletes
legacy `refs/prompt-mutants/...` refs once downstream capture experiments are
done. See prompt_mutant_split_lib.py for the splitting algorithm and git-plumbing
mechanics; this module is CLI wiring only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from prompt_mutant_files_lib import list_skill_files_worktree, read_worktree_file
from prompt_mutant_lib import (
    GRANULARITIES,
    PromptMutantError,
    build_split_manifest,
    cleanup_mutant_refs,
    generate_mutants,
)

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
# Single source: the CLI cannot accept a granularity the splitter does not implement.
GRANULARITY_CHOICES = list(GRANULARITIES)
SENTINEL_CHANNELS = {"required_command_fragment", "required_summary_fragment", "trace_command_marker"}


def _parse_sentinel(raw: str) -> dict:
    """Parse repeatable --sentinel values.

    Accepted shapes:
    - CHANNEL=VALUE
    - JSON object with channel/value/deterministic and optional name/reason
    """
    text = raw.strip()
    if text.startswith("{"):
        try:
            sentinel = json.loads(text)
        except json.JSONDecodeError as exc:
            raise PromptMutantError(f"--sentinel is not valid JSON: {exc}") from exc
        if not isinstance(sentinel, dict):
            raise PromptMutantError("--sentinel JSON must be an object")
    else:
        if "=" not in text:
            raise PromptMutantError("--sentinel must be CHANNEL=VALUE or a JSON object")
        channel, value = text.split("=", 1)
        sentinel = {"channel": channel.strip(), "value": value}

    channel = sentinel.get("channel")
    value = sentinel.get("value")
    if channel not in SENTINEL_CHANNELS:
        raise PromptMutantError(f"--sentinel channel must be one of {sorted(SENTINEL_CHANNELS)!r}, got {channel!r}")
    if not isinstance(value, str) or not value:
        raise PromptMutantError("--sentinel value must be a non-empty string")
    if sentinel.get("deterministic", True) is not True:
        raise PromptMutantError("--sentinel deterministic must be true")
    name = sentinel.get("name")
    reason = sentinel.get("reason")
    if name is not None and not isinstance(name, str):
        raise PromptMutantError("--sentinel name must be a string when present")
    if reason is not None and not isinstance(reason, str):
        raise PromptMutantError("--sentinel reason must be a string when present")
    return {"channel": channel, "value": value, "deterministic": True, "name": name, "reason": reason}


def _cmd_split(args: argparse.Namespace) -> int:
    try:
        manifest = build_split_manifest(
            args.repo_root, args.skill, args.granularity, list_skill_files_worktree, read_worktree_file
        )
    except PromptMutantError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    emit_yaml(manifest)
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    try:
        sentinels = [_parse_sentinel(raw) for raw in args.sentinel]
        result = generate_mutants(
            args.repo_root,
            args.skill,
            args.baseline_ref,
            args.unit_id or None,
            args.replacement_text,
            args.granularity,
        )
        result["sentinels"] = sentinels
    except PromptMutantError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit_yaml(
        {
            "skill": result["skill"],
            "baseline_provenance_sha": result["baseline_sha"],
            "baseline_snapshot_sha": result["baseline_snapshot_sha"],
            "unit_count": len(result["units"]),
            "out": str(args.out),
        }
    )
    return 0


def _cmd_cleanup(args: argparse.Namespace) -> int:
    deleted = cleanup_mutant_refs(args.repo_root, args.skill)
    emit_yaml({"skill": args.skill, "deleted": deleted})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Split a skill's prompt surface into mutation units and build/cleanup "
            "throwaway parentless snapshot commits over the installed-plugin mirror tree. Advisory "
            "tooling for the prompt-mutation-pilot goal; never a commit/CI gate."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    split_parser = subparsers.add_parser(
        "split", help="Split a skill's prompt surface into mutation units and print a manifest."
    )
    split_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    split_parser.add_argument("--skill", required=True)
    split_parser.add_argument(
        "--granularity",
        choices=GRANULARITY_CHOICES,
        default="section",
        help="Mutation unit size. `section` (default) is one heading plus its body; "
        "`paragraph` additionally emits blank-line-separated blocks inside each "
        "section, which distinguishes load-bearing prose from decoration within a "
        "section that survives as a whole.",
    )
    split_parser.set_defaults(func=_cmd_split)

    generate_parser = subparsers.add_parser(
        "generate", help="Build one parentless snapshot commit per selected unit and emit raw snapshot SHAs."
    )
    generate_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    generate_parser.add_argument("--skill", required=True)
    generate_parser.add_argument("--baseline-ref", required=True)
    generate_parser.add_argument(
        "--unit-id", action="append", default=[], help="Repeatable; defaults to every unit of --skill."
    )
    generate_parser.add_argument(
        "--granularity",
        choices=GRANULARITY_CHOICES,
        default="section",
        help="Must match the granularity the selected --unit-id values came from; a "
        "paragraph unit id is unknown to a section-granularity split.",
    )
    generate_parser.add_argument(
        "--replacement-text",
        help="When set, rewrite selected units to this exact text instead of removing them.",
    )
    generate_parser.add_argument(
        "--sentinel",
        action="append",
        default=[],
        help=(
            "Repeatable all-arm canary witness to copy into the manifest. "
            "Use CHANNEL=VALUE or a JSON object with channel/value/deterministic plus optional name/reason."
        ),
    )
    generate_parser.add_argument("--out", type=Path, required=True, help="Where to write the mutation manifest JSON.")
    generate_parser.set_defaults(func=_cmd_generate)

    cleanup_parser = subparsers.add_parser(
        "cleanup", help="Delete legacy refs/prompt-mutants/<skill>/* prompt-mutant refs."
    )
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
