#!/usr/bin/env python3

"""Generate a release note's derived claim block, and check a note against it.

WHEN this runs is a separate question from when it was WRITTEN, and conflating
them is a recorded mistake. It is written early — at the first slice of a
release — so every later slice lands under it and its claim surfaces are
captured as they change. It is RUN late, over the final tree, because notes
generated early are contradicted by the tree that ships.

The two modes are the two ends of that gap. `--sync` regenerates the derived
block into a note the author is still writing. `--check` re-derives at publish
and refuses a note the tree disagrees with, naming the surface and the direction
of the disagreement.

Non-claim: this proves the note matches a derivation, never that the derivation
is the whole truth. Claim surfaces live in `release_claim_surfaces.SURFACES`,
and a surface nobody registered is invisible here.
"""
from __future__ import annotations

import argparse
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
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)

_claims = SKILL_RUNTIME.load_local_skill_module(__file__, "release_notes_claims")
_surfaces = SKILL_RUNTIME.load_local_skill_module(__file__, "release_claim_surfaces")
_lint = SKILL_RUNTIME.load_local_skill_module(__file__, "lint_release_narrative")
_yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
emit_yaml = _yaml_output.emit_yaml

SKELETON_HEADING = "## Derived claim surfaces"

_SKELETON = """# {title}

## Summary

<!-- Authored narrative. Bare quantities belong in a claim marker, not in prose:
     write a marker spelled {{{{claim:<surface-id>.count=<value>}}}} rather than a
     digit, and re-run --sync to settle it.
     The placeholder here is deliberately not a parseable marker, so it is
     invisible to the audit rather than shipping a value: a skeleton carrying a
     REAL marker ships a concrete value that goes wrong the moment the tree
     moves, which is the class this mechanism exists to refuse. -->

{heading}

These are measured from the tree this release ships, not authored. Regenerate
with `generate_release_notes.py --sync`.

{block}
"""


def render_block(repo_root: Path, *, require_git: bool = False, tracked_tree=None) -> str:
    return _claims.render_derived_block(
        _surfaces.derive_surfaces(
            repo_root, require_git=require_git, tracked_tree=tracked_tree
        )
    )


def sync_notes_text(text: str, block: str) -> tuple[str, str]:
    """``text`` with its derived block replaced by ``block``, and what happened.

    A note with no block gets one APPENDED rather than being rewritten from the
    skeleton: by the time `--sync` runs against an existing file, the authored
    prose is the valuable part, and regenerating over it would destroy the work
    the generator exists to support.
    """
    begin = text.find(_claims.BLOCK_BEGIN)
    end = text.find(_claims.BLOCK_END)
    if begin == -1 or end == -1 or end < begin:
        separator = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        return f"{text}{separator}{SKELETON_HEADING}\n\n{block}\n", "appended"
    tail = end + len(_claims.BLOCK_END)
    return f"{text[:begin]}{block}{text[tail:]}", "replaced"


def _title_for(notes_file: Path) -> str:
    return f"Release notes: {notes_file.stem}"


def _do_sync(notes_file: Path, block: str) -> dict[str, object]:
    if not notes_file.exists():
        notes_file.parent.mkdir(parents=True, exist_ok=True)
        notes_file.write_text(
            _SKELETON.format(title=_title_for(notes_file), heading=SKELETON_HEADING, block=block),
            encoding="utf-8",
        )
        return {"action": "created", "notes_file": str(notes_file)}
    text = notes_file.read_text(encoding="utf-8")
    updated, action = sync_notes_text(text, block)
    if updated != text:
        notes_file.write_text(updated, encoding="utf-8")
        return {"action": action, "notes_file": str(notes_file)}
    return {"action": "unchanged", "notes_file": str(notes_file)}


def _do_check(notes_file: Path, repo_root: Path, *, require_git: bool, versions: tuple[str, ...]) -> dict[str, object]:
    """Both arms, because `--check` is read as the verdict.

    Running the claim arm alone printed `status: clean` over a note carrying
    "twelve public skill scripts still declare one" — a green light from the
    command the skill's own workflow tells an author to run, over half the rule.
    Whatever refuses at the publish boundary has to refuse here first, or the
    cheap check teaches the expensive one to be a surprise.
    """
    findings = _claims.audit_notes_file(notes_file, repo_root, require_git=require_git)
    prose = _lint.lint_file(notes_file, versions=versions)
    prose_blocking = _lint.blocking(prose)
    over_claims = [finding for finding in findings if finding["direction"] == "over-claim"]
    blocking_total = len(findings) + len(prose_blocking)
    return {
        "notes_file": str(notes_file),
        "status": "clean" if not blocking_total else "disagrees",
        "finding_count": blocking_total,
        # Surfaced separately because it is the direction that actually failed
        # and the direction a consumer ACTS on: a note claiming more than the
        # tree has sends someone migrating a surface that is not there.
        "over_claim_count": len(over_claims),
        "findings": findings,
        "narrative_blocking": prose_blocking,
        "narrative_advisory": [finding for finding in prose if finding not in prose_blocking],
        "surfaces_checked": list(_surfaces.SURFACE_IDS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root the claim surfaces are derived from")
    parser.add_argument("--notes-file", type=Path, help="Release notes file to sync or check")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--sync", action="store_true", help="Write the derived block into --notes-file (creating it from a skeleton when absent)")
    mode.add_argument("--check", action="store_true", help="Re-derive and refuse a --notes-file the tree disagrees with")
    parser.add_argument("--require-git-file-listing", action="store_true", help="Refuse to derive from a non-git tree rather than falling back to a glob")
    parser.add_argument("--version", action="append", default=[], help="A release version the notes may name without grounding it; repeatable")
    parser.add_argument("--detail", action="store_true", help="Emit the full derivation payload instead of the rendered block")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if (args.sync or args.check) and args.notes_file is None:
        parser.error("--sync and --check both require --notes-file")

    if args.check:
        payload = _do_check(
            args.notes_file,
            repo_root,
            require_git=args.require_git_file_listing,
            versions=tuple(args.version),
        )
        emit_yaml(payload)
        return 1 if payload["finding_count"] else 0

    block = render_block(repo_root, require_git=args.require_git_file_listing)
    if args.sync:
        emit_yaml(_do_sync(args.notes_file, block))
        return 0
    if args.detail:
        emit_yaml({"surfaces": _surfaces.derive_surfaces(repo_root, require_git=args.require_git_file_listing)})
        return 0
    print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
