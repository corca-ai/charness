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
chunked_routing_staleness = SKILL_RUNTIME.load_local_skill_module(
    __file__, "chunked_routing_staleness"
)


def _explicit_handoff_path(args: argparse.Namespace) -> Path | None:
    explicit = args.handoff if args.handoff is not None else args.handoff_path
    return explicit.expanduser().resolve() if explicit is not None else None


def _resolve_handoff_path(args: argparse.Namespace) -> Path:
    # Source stage: input is the handoff doc, not pipeline JSON. A positional
    # path or --handoff-path both name it (positional wins); otherwise resolve
    # via the adapter from --repo-root. The positional makes the natural
    # direct `parse_handoff_entries.py docs/handoff.md` invocation work.
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


def _path_root_for_citations(args: argparse.Namespace) -> Path | None:
    """The tree cited relative links are relative TO.

    Usually the live-filter root, and it is returned first when there is one; the
    `.git` walk is the FALLBACK for an explicit path from another cwd, where the
    live-filter root is deliberately None. The two are separate parameters, not
    separate values in the common case -- widening the live-filter root to cover
    this instead would have armed goal-status lookups for any explicit path, and a
    checked-in FIXTURE snapshot was then judged against today's real artifacts and
    lost an entry (measured).

    `.git` is the marker rather than a guess at depth, and None is still returned
    when there is no tree, because inventing a root is the wrong-base mistake this
    whole change is about.
    """
    live = _repo_root_for_live_filters(args)
    if live is not None:
        return live
    explicit = _explicit_handoff_path(args)
    if explicit is None:
        return None
    for candidate in explicit.resolve().parents:
        if (candidate / ".git").exists():
            return candidate
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
        "reasons over the live backlog (adapter-gated). Default off "
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
        citation_root = _path_root_for_citations(args)
        entries = chunked_routing_lib.parse_handoff_entries(
            text,
            repo_root=repo_root,
            # The handoff's own directory: a cited relative link is relative to
            # THIS file, not to the repo root, and resolving it anywhere else
            # reports live citations as stale.
            artifact_dir=handoff_path.parent,
            path_root=citation_root,
        )
        handoff_count = len(entries)
        issue_count = 0
        issue_source_diagnostic = None
        open_issue_numbers: set[int] = set()
        if args.with_issues:
            issue_repo_root = _repo_root_for_adapter(args)
            issue_entries = chunked_routing_issue_source.build_issue_entries(
                issue_repo_root,
                start_index=max((e.index for e in entries), default=0) + 1,
            )
            issue_count = len(issue_entries)
            open_issue_numbers = set(
                getattr(chunked_routing_issue_source, "LAST_OPEN_ISSUE_NUMBERS", ())
            )
            issue_source_diagnostic = getattr(
                chunked_routing_issue_source,
                "LAST_ISSUE_SOURCE_DIAGNOSTIC",
                None,
            )
            entries = chunked_routing_issue_source.dedup_and_union(entries, issue_entries)

        # Resolvable-ness facts. The path check is offline and always runs when a
        # repo root resolved; the issue-state check needs the tracker, so it runs
        # only under --with-issues (the flag that already sanctions provider
        # calls) and reuses that listing's open set instead of re-asking.
        # The path half of staleness is the SAME lexical+existence question as
        # normalization, so it takes the citation root. Without this the fix was
        # armed for `--handoff-path` from another cwd while the consumer that
        # motivated it -- the MISSING marker -- stayed off for that form, so the
        # slice would have claimed a scope its own output did not demonstrate.
        # Goal-status filtering stays on `repo_root`: that one needs the tree whose
        # goals are live, which a fixture snapshot's containing repo is not.
        staleness_repo_root = repo_root if repo_root is not None else citation_root
        issue_states = None
        issue_state_diagnostic = None
        if args.with_issues:
            # The open set is threaded through explicitly. Reading it back off
            # the issue-source module inside the staleness helper would reach a
            # DIFFERENT module instance (the skill loaders do not cache), so the
            # reuse would be silently dead and every cited issue -- including the
            # ~50 that just came back from the open listing -- would cost its own
            # provider call and blow the CLI timeout.
            known_open = tuple(open_issue_numbers)
            cited = [
                number
                for entry in entries
                for number in entry.referenced_issues
                if number not in open_issue_numbers
            ]
            issue_states, issue_state_diagnostic = (
                chunked_routing_staleness.resolve_states_for_repo(
                    _repo_root_for_adapter(args), cited, known_open=known_open
                )
            )
            if issue_state_diagnostic is not None:
                issue_states = None
            elif issue_states is not None:
                issue_states.update({number: "OPEN" for number in known_open})
        entries = chunked_routing_staleness.annotate_entries(
            entries, repo_root=staleness_repo_root, issue_states=issue_states
        )
        payload = {
            "ok": True,
            "handoff_path": str(handoff_path),
            "entry_count": len(entries),
            "handoff_entry_count": handoff_count,
            "issue_entry_count": issue_count,
            "deduped_issue_count": (issue_count - (len(entries) - handoff_count)) if args.with_issues else 0,
            "entries": [entry.to_dict() for entry in entries],
            "staleness": chunked_routing_staleness.staleness_summary(
                entries,
                paths_checked=staleness_repo_root is not None,
                issue_states_checked=issue_states is not None,
                diagnostic=issue_state_diagnostic,
            ),
        }
        if args.with_issues:
            payload["issue_source_diagnostic"] = issue_source_diagnostic
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
