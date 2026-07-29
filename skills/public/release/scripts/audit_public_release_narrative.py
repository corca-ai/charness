#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_path_portability = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.path_portability_lib")


REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Scope",
    "## Verification",
    "## Release State",
    "## Public Release Verification",
)

REQUIRED_STATE_LEDGER_LABELS: tuple[str, ...] = (
    "local release mutation",
    "branch/tag push",
    "GitHub release record",
    "public release surface verification",
    "audit narrative",
)


_FENCE_RE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,}).*?(?:^[ \t]*\1[ \t]*$|\Z)")
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def strip_display_code(text: str) -> str:
    """``text`` with fenced blocks and inline-code spans blanked out, line count
    preserved so any positional reasoning stays valid.

    Content rendered AS CODE is shown to the reader, not asserted to them. Both
    audits below were blind to this and it broke them in opposite directions: a
    fenced *example* of the release-state ledger satisfied the five-entry check
    while the real section below it was empty (a false PASS at the publish
    boundary — D1's own escape class surviving the D1 fix), and a fenced install
    one-liner containing a `main` URL was refused as a rotting evidence link when
    it is neither evidence nor a link the reader follows (D2's blast radius).
    """
    def blank(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    return _INLINE_CODE_RE.sub("", _FENCE_RE.sub(blank, text))


def _release_state_block(artifact_text: str) -> str | None:
    """The body under the `## Release State` heading, or ``None`` when no such
    heading line exists.

    Matches the heading by PREFIX, not by exact equality. Heading *presence* is
    tested elsewhere as a substring (`REQUIRED_HEADINGS`), and when the two
    disagreed the audit failed open: `## Release State (ledger)` satisfied the
    substring test, produced no block here, and the caller's early return left
    all five ledger entries unchecked while reporting `passed` (D1). A suffixed
    heading is legitimate authoring, so the fix is to locate it, not to refuse
    it — and a heading the substring test found but this cannot locate is now a
    blocker in the caller rather than a silent pass.
    """
    lines = artifact_text.splitlines()
    try:
        start = next(
            i for i, line in enumerate(lines)
            if line.strip() == "## Release State" or line.strip().startswith("## Release State ")
        )
    except StopIteration:
        return None
    block: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        block.append(line)
    return "\n".join(block)


def _audit_artifact(artifact_path: Path, *, target_tag: str) -> list[str]:
    blockers: list[str] = []
    if not artifact_path.is_file():
        blockers.append(f"durable release artifact missing: {artifact_path}")
        return blockers
    raw_text = artifact_path.read_text(encoding="utf-8")
    # Headings and ledger entries are read from the ASSERTED text only. A fenced
    # *example* of the ledger satisfied all five entry checks while the real
    # section below it was empty — D1's own escape class, one indirection over.
    text = strip_display_code(raw_text)
    if target_tag not in raw_text:
        blockers.append(
            f"release artifact {artifact_path} does not mention target tag `{target_tag}`; "
            "the audit narrative may be stale relative to this publish"
        )
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            blockers.append(f"release artifact {artifact_path} is missing section `{heading}`")
    state_block = _release_state_block(text)
    if state_block is None:
        # An unlocatable ledger is an UNESTABLISHED scope, not a satisfied one.
        # Returning here left the five entry checks below unrun while the audit
        # still reported `passed` (D1). Only report it when the
        # section was not ALREADY reported as missing outright, so an artifact
        # with no ledger at all does not draw two blockers that contradict each
        # other about whether a heading exists.
        if "## Release State" in text:
            blockers.append(
                f"release artifact {artifact_path} mentions `## Release State` but no such "
                "heading line was found (it may appear only in prose or inside a code fence), so "
                "the five-entry release state ledger was never checked; put `## Release State` "
                "on its own heading line"
            )
        return blockers
    for label in REQUIRED_STATE_LEDGER_LABELS:
        if label not in state_block:
            blockers.append(
                f"release state ledger in {artifact_path} is missing required entry `{label}`"
            )
    return blockers


# Source-tree links in published notes, in both renderings GitHub serves them:
# `github.com/<owner>/<repo>/(blob|tree|raw)/<ref>/<path>` and
# `raw.githubusercontent.com/<owner>/<repo>/<ref>/<path>`. The second was never
# matched at all. The path is no longer pinned to the repo-specific
# `charness-artifacts/` literal — this is a portable public skill, and a link
# that rots does so regardless of which directory it points into.
_SOURCE_TREE_POINTER_RE = re.compile(
    r"(?:github\.com/[^/\s)]+/[^/\s)]+/(?:blob|tree|raw)|raw\.githubusercontent\.com/[^/\s)]+/[^/\s)]+)"
    r"/(?:refs/(?:tags|heads)/)?(?P<ref>[^/\s)]+)(?:/(?P<path>[^\s)]*))?"
)
# An immutable ref: a version tag (`v2.11.3`, `v1.0`, `2.11.3-rc1`) or a commit
# sha, short or full. Anything else — `main`, `master`, a branch, `HEAD` — moves
# under the reader.
#
# A branch NAMED like a version (`1.0.0`) is accepted, and a tag can be moved
# with `git tag -f`. Neither is distinguishable from a ref string alone, so the
# rule is "version-shaped or sha-shaped", not "provably immutable" — stated here
# rather than implied by the constant's name.
_IMMUTABLE_REF_RE = re.compile(
    r"(?i)^(?:v?\d+(?:\.\d+)+[0-9A-Za-z.\-+]*|[0-9a-f]{7,40})$"
)


def _ref_is_immutable(ref: str) -> bool:
    return _IMMUTABLE_REF_RE.match(ref) is not None


def audit_notes_file(notes_file: Path, *, target_tag: str) -> list[str]:
    """Blockers for source-tree pointers in a release notes FILE."""
    if not notes_file.is_file():
        return [f"public release notes file missing: {notes_file}"]
    return audit_notes_text(notes_file.read_text(encoding="utf-8"), target_tag=target_tag)


def audit_notes_text(notes_text: str, *, target_tag: str) -> list[str]:
    """Blockers for source-tree pointers in release notes TEXT.

    The rule is that a PUBLISHED note must not point at content that can change
    after publication. The discriminator was exactly inverted (D2): the blocker
    fired only when the ref EQUALED the release tag, so the one immutable pointer
    was refused and every mutable one — `main`, a branch, a raw-host link — was
    passed. ``target_tag`` is no longer the test; ref immutability is.

    Text-level so the same rule can audit a PUBLISHED body read back after
    `--generate-notes`, which composes the notes at creation time and so has no
    file to inspect beforehand.
    """
    blockers: list[str] = []
    # A URL rendered as code is shown to the reader, not offered as a reference
    # to follow — an install one-liner in a fenced block is the common case, and
    # refusing it blocked publish with advice ("pin to the release tag") that is
    # impossible when the link points at a different repository.
    text = strip_display_code(notes_text)
    for match in _SOURCE_TREE_POINTER_RE.finditer(text):
        ref = match.group("ref")
        # Trailing sentence/markup punctuation is not part of the path; it only
        # reaches the operator-facing message, but a message that misquotes the
        # path it is complaining about costs the reader a search.
        # The path group is optional: `.../tree/main` with no path is still a
        # mutable pointer, and requiring a path let it through unmatched.
        path = (match.group("path") or "").rstrip(".,;:`\"'>") or "(repository root)"
        if _ref_is_immutable(ref):
            continue
        blockers.append(
            f"public release notes point at source-tree record `{path}` at MUTABLE ref "
            f"`{ref}`; that content can change after publication. Pin the link to the release "
            f"tag `{target_tag}` or a commit sha, or inline the content into the notes"
        )
    return blockers


# A maximal digits-and-separators run: the version-shaped tokens in a filename
# stem, stopping at any letter. Compared for EQUALITY after normalizing `-` to
# `.`, rather than searched for as a bounded substring.
#
# Boundary-anchored searching kept producing false matches as it was widened to
# cover dash-separated names: `v3-2-1-notes.md` matched target `2.1` (left
# boundary `-`, right boundary `-`), and a single-component tag like `v14`
# matched the day field of every `...-07-14-...-notes.md`. Token equality has no
# boundary to get wrong.
_VERSION_RUN_RE = re.compile(r"\d+(?:[-.]\d+)*")


def find_drafted_notes(repo_root: Path, output_dir: str, *, target_tag: str) -> list[Path]:
    """Notes files already drafted for ``target_tag`` under the adapter's
    ``output_dir``, sorted by name.

    Existence only — the caller decides what a drafted-but-unsupplied note means.
    This exists because the audits above all read notes the publisher CHOSE to
    hand over; none of them could see notes the publisher wrote and then did not
    pass. v2.11.0 shipped that way: its notes were authored, committed, and left
    in this directory while publish took the `--generate-notes` default, so the
    published body was one `**Full Changelog**` link and the section amending
    2.10.0's now-wrong migration instruction reached nobody.

    The version is matched by EQUALITY against the version-shaped tokens in the
    stem, dot-or-dash separated. Every rule here was found by a reviewer or a
    test against real filenames, never reasoned out: a plain substring test makes
    `v2.1` match `v2.11.0`; a dotted-only token silently missed
    `2026-07-14-v1-0-7-public-notes.md`, a shape this repo used three times, which
    would have reproduced the v2.11.0 defect while the audit reported `passed`;
    and the bounded-substring search that fixed THAT matched `v3-2-1-notes.md`
    for target `2.1`. Comparing whole tokens removes the boundary entirely.

    Deliberately NOT decided here: whether `v1.2.3-rc1-notes.md` belongs to
    `v1.2.3`. A pre-release suffix and a role word (`-notes`, `-public`) are the
    same shape after the version, so a filename cannot settle it. The match stays
    permissive and the caller names every candidate instead of asserting which
    one is right — a forced question, not a declared answer.
    """
    notes_dir = repo_root / output_dir
    version = target_tag[1:] if target_tag.startswith("v") else target_tag
    if not version:
        return []
    wanted = version.replace("-", ".")

    def names_this_version(stem: str) -> bool:
        return any(run.replace("-", ".") == wanted for run in _VERSION_RUN_RE.findall(stem))
    # No try/except here, deliberately. An `except OSError` guard was written for
    # an unreadable `output_dir` and the blocking changed-line gate showed it was
    # never executed: `Path.glob` swallows the scandir error and yields nothing,
    # so the guard was dead and the test that "proved" it passed because the glob
    # returned empty, not because anything was caught. A dead guard is worse than
    # none — it reads as a handled case.
    #
    # What actually happens, stated rather than guarded: an unreadable or absent
    # output_dir yields no candidates and the arm stays silent. That is a
    # fail-open this function cannot distinguish from "this repo drafts no
    # notes", and it is why the missing-directory case is a non-claim below.
    candidates = [path for path in notes_dir.glob("*.md") if path.is_file()]
    return sorted(
        (path for path in candidates
         if "notes" in path.stem.lower() and names_this_version(path.stem)),
        key=lambda path: path.name,
    )


def _display_path(path: Path, repo_root: Path) -> str:
    """``path`` rendered for an operator-facing blocker: repo-relative when it is
    inside the repo, the raw path when it is not.

    `output_dir` is an unvalidated free string in the release adapter, so an
    absolute one makes a bare `relative_to` raise — after the bump and after the
    pre-push gates, stranding a publish over a display string. The repo's
    canonical renderer already handles that, so this defers to it rather than
    re-deriving the try/except a duplication gate correctly flagged against
    `control_plane_lib._manifest_path_for_payload`.
    """
    return _path_portability.repo_relative(repo_root, path)


def drafted_notes_blockers(
    repo_root: Path,
    drafted_notes: list[Path],
    *,
    target_tag: str,
    notes_file: Path | None,
) -> list[str]:
    """Blockers for notes drafted for ``target_tag`` that publish is not shipping.

    The premise is "the publisher wrote the operator's notes and then published
    something else", so the test is not "was a notes file passed" but "was one of
    THESE passed": handing over `latest.md`, or the previous release's notes,
    satisfies the premise just as fully as `--generate-notes` did for v2.11.0.

    Silent for repos that draft no notes, so this fires on the observed defect
    rather than on the `--generate-notes` path as such. It names every candidate
    and refuses to pick: a pre-release draft and a role-suffixed draft are
    indistinguishable by filename, so asserting one would be a verdict surface
    handing out an instruction it cannot support.
    """
    if not drafted_notes:
        return []
    resolved = notes_file.resolve() if notes_file is not None else None
    if resolved is not None and any(path.resolve() == resolved for path in drafted_notes):
        return []
    shown = ", ".join(f"`{_display_path(path, repo_root)}`" for path in drafted_notes)
    supplied = (
        f"publish was invoked with `--notes-file {_display_path(notes_file, repo_root)}`, which is none of them"
        if notes_file is not None
        else "publish was invoked without `--notes-file`, so the published body would be auto-generated from commits"
    )
    # "candidates", not "are drafted": with only `v1.2.3-rc1-notes.md` on disk,
    # stating that v1.2.3's notes exist asserts the very thing `find_drafted_notes`
    # says a filename cannot settle. The premise has to be as provisional as the
    # remedy already is.
    return [
        f"drafted notes files match `{target_tag}` ({shown}) but {supplied}; "
        f"the drafted notes would reach nobody. Pass the one that belongs to this release with "
        f"`--notes-file`. If a candidate belongs to a different release (a pre-release suffix, say) "
        f"or is superseded, rename or delete it AND COMMIT that — publish refuses a dirty worktree, "
        f"so an uncommitted deletion only trades this refusal for another"
    ]


def build_payload(
    repo_root: Path,
    *,
    target_tag: str,
    artifact_path: Path | None = None,
    notes_file: Path | None = None,
) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        return {
            "status": "blocked",
            "blockers": [f"release adapter is invalid: {adapter['errors']}"],
            "target_tag": target_tag,
        }
    output_dir = adapter["data"]["output_dir"]
    resolved_artifact = artifact_path or (repo_root / output_dir / "latest.md")
    blockers: list[str] = []
    blockers.extend(_audit_artifact(resolved_artifact, target_tag=target_tag))
    notes_blockers: list[str] = []
    if notes_file is not None:
        notes_blockers = audit_notes_file(notes_file, target_tag=target_tag)
        blockers.extend(notes_blockers)
    drafted_notes = find_drafted_notes(repo_root, output_dir, target_tag=target_tag)
    blockers.extend(drafted_notes_blockers(repo_root, drafted_notes, target_tag=target_tag, notes_file=notes_file))
    return {
        "status": "blocked" if blockers else "passed",
        "blockers": blockers,
        "target_tag": target_tag,
        "artifact_path": str(resolved_artifact),
        "notes_file": str(notes_file) if notes_file is not None else None,
        "notes_blockers": notes_blockers,
        "drafted_notes": [str(path) for path in drafted_notes],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose public release narrative should be audited")
    parser.add_argument("--target-tag", required=True, help="Release tag the audit narrative must reference")
    parser.add_argument("--artifact-path", type=Path, help="Path to the release audit artifact (defaults to adapter output_dir/latest.md)")
    parser.add_argument("--notes-file", type=Path, help="Path to the public release notes file to audit")
    parser.add_argument("--json", action="store_true", help="Emit the full narrative-audit payload as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    payload = build_payload(
        repo_root,
        target_tag=args.target_tag,
        artifact_path=args.artifact_path.resolve() if args.artifact_path else None,
        notes_file=args.notes_file.resolve() if args.notes_file else None,
    )
    if args.json or payload["status"] == "passed":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("public release narrative audit blocked:")
        for blocker in payload["blockers"]:
            print(f"- {blocker}")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
