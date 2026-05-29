#!/usr/bin/env python3
"""Parse handoff ``## Next Session`` entries into structured records.

CLI surface:

    python3 parse_handoff_entries.py --repo-root <path>
    python3 parse_handoff_entries.py --handoff-path <path>

Emits a JSON array of HandoffEntry records on stdout. Used as the first
step of the handoff chunked-routing pipeline. See
``docs/handoff-chunked-routing.md`` for the contract.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
chunked_routing_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_lib")
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
chunked_routing_issue_source = SKILL_RUNTIME.load_local_skill_module(
    __file__, "chunked_routing_issue_source"
)


def _resolve_handoff_path(args: argparse.Namespace) -> Path:
    # Source stage: input is the handoff doc, not pipeline JSON. A positional
    # path or --handoff-path both name it (positional wins); otherwise resolve
    # via the adapter from --repo-root. The positional makes the natural
    # `parse_handoff_entries.py docs/handoff.md` invocation work (#248).
    explicit = args.handoff if args.handoff is not None else args.handoff_path
    if explicit is not None:
        return explicit.expanduser().resolve()
    repo_root = args.repo_root.expanduser().resolve()
    adapter = resolve_adapter.load_adapter(repo_root)
    return (repo_root / adapter["artifact_path"]).resolve()


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
        default=Path.cwd(),
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
        entries = chunked_routing_lib.parse_handoff_entries(text)
        handoff_count = len(entries)
        issue_count = 0
        if args.with_issues:
            repo_root = args.repo_root.expanduser().resolve()
            issue_entries = chunked_routing_issue_source.build_issue_entries(
                repo_root,
                start_index=max((e.index for e in entries), default=0) + 1,
            )
            issue_count = len(issue_entries)
            entries = chunked_routing_issue_source.union_entries(entries, issue_entries)
        payload = {
            "ok": True,
            "handoff_path": str(handoff_path),
            "entry_count": len(entries),
            "handoff_entry_count": handoff_count,
            "issue_entry_count": issue_count,
            "entries": [entry.to_dict() for entry in entries],
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
