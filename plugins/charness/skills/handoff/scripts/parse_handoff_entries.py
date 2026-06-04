#!/usr/bin/env python3
"""Parse handoff ``## Next Session`` entries into structured records.

CLI surface:

    python3 parse_handoff_entries.py --repo-root <path>
    python3 parse_handoff_entries.py --handoff-path <path>

Emits a JSON array of HandoffEntry records on stdout. Used as the first
step of the handoff chunked-routing pipeline. See
``references/chunked-routing.md`` for the contract (in the charness source
repo the full implementation contract is ``docs/handoff-chunked-routing.md``,
which is not vendored with the skill).
"""
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
chunked_routing_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_lib")
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
chunked_routing_issue_source = SKILL_RUNTIME.load_local_skill_module(
    __file__, "chunked_routing_issue_source"
)


def _explicit_handoff_path(args: argparse.Namespace) -> Path | None:
    explicit = args.handoff if args.handoff is not None else args.handoff_path
    return explicit.expanduser().resolve() if explicit is not None else None


def _resolve_handoff_path(args: argparse.Namespace) -> Path:
    # Source stage: input is the handoff doc, not pipeline JSON. A positional
    # path or --handoff-path both name it (positional wins); otherwise resolve
    # via the adapter from --repo-root. The positional makes the natural
    # `parse_handoff_entries.py docs/handoff.md` invocation work (#248).
    explicit = _explicit_handoff_path(args)
    if explicit is not None:
        return explicit
    repo_root = _repo_root_for_adapter(args)
    adapter = resolve_adapter.load_adapter(repo_root)
    return (repo_root / adapter["artifact_path"]).resolve()


def _repo_root_for_adapter(args: argparse.Namespace) -> Path:
    root = args.repo_root if args.repo_root is not None else Path.cwd()
    return root.expanduser().resolve()


def _repo_root_for_live_filters(args: argparse.Namespace) -> Path | None:
    if args.repo_root is not None:
        return args.repo_root.expanduser().resolve()
    if args.handoff is None and args.handoff_path is None:
        return Path.cwd().resolve()
    explicit = _explicit_handoff_path(args)
    cwd = Path.cwd().resolve()
    if explicit == cwd / "docs" / "handoff.md":
        return cwd
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "handoff",
        nargs="?",
        type=Path,
        default=None,
        help="Handoff artifact path (positional convenience; same as --handoff-path).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repo root used to resolve the handoff adapter (default: cwd)",
    )
    parser.add_argument(
        "--handoff-path",
        type=Path,
        help="Explicit handoff artifact path; overrides --repo-root resolution.",
    )
    parser.add_argument(
        "--with-issues",
        action="store_true",
        help=(
            "Also union open tracker issues into the entries so the chunker "
            "reasons over the live backlog (adapter-gated; #249). Default off "
            "keeps the source stage offline."
        ),
    )
    return parser.parse_args()


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff parse_handoff_entries")
    try:
        args = parse_args()
        handoff_path = _resolve_handoff_path(args)
        if not handoff_path.is_file():
            print(
                json.dumps(
                    {"ok": False, "error": f"handoff artifact not found: {handoff_path}"},
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 2
        text = handoff_path.read_text(encoding="utf-8")
        repo_root = _repo_root_for_live_filters(args)
        entries = chunked_routing_lib.parse_handoff_entries(text, repo_root=repo_root)
        handoff_count = len(entries)
        issue_count = 0
        issue_source_diagnostic = None
        if args.with_issues:
            issue_repo_root = _repo_root_for_adapter(args)
            issue_entries = chunked_routing_issue_source.build_issue_entries(
                issue_repo_root,
                start_index=max((e.index for e in entries), default=0) + 1,
            )
            issue_count = len(issue_entries)
            issue_source_diagnostic = getattr(
                chunked_routing_issue_source,
                "LAST_ISSUE_SOURCE_DIAGNOSTIC",
                None,
            )
            entries = chunked_routing_issue_source.dedup_and_union(entries, issue_entries)
        payload = {
            "ok": True,
            "handoff_path": str(handoff_path),
            "entry_count": len(entries),
            "handoff_entry_count": handoff_count,
            "issue_entry_count": issue_count,
            "deduped_issue_count": (issue_count - (len(entries) - handoff_count)) if args.with_issues else 0,
            "entries": [entry.to_dict() for entry in entries],
        }
        if args.with_issues:
            payload["issue_source_diagnostic"] = issue_source_diagnostic
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
