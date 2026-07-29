"""Which drafted notes files belong to a release tag.

Split out of `audit_public_release_narrative.py` when that file passed its length
cap. A cohesive concept, not a mechanical spill: everything here answers one
question — "was anything drafted for THIS tag, and could we even look?" — while
the audit next door decides what a drafted-but-unshipped note MEANS for publish.
The version-token matching, the role-word convention, and the readable/absent/
unreadable split all belong to the first question and to nothing else.
"""
from __future__ import annotations

import re
from pathlib import Path

_VERSION_RUN_RE = re.compile(r"\d+(?:[-.]\d+)*")


class NotesDirectoryUnreadable(OSError):
    """The drafted-notes directory exists but could not be listed.

    Distinct from absent on purpose: absent means this repo drafts no notes and
    publish proceeds, while unreadable means the arm has no idea what is in
    there. Collapsing them let an unreadable directory read as "nothing was
    drafted" — the arm's own comment admitted the fail-open and it stayed.
    """


#: The filename role word that means "these are the release notes".
#:
#: A widening to ("notes", "release", "changelog", "announcement") was written
#: here and REVERTED after a bounded review, because the evidence ran the other
#: way. No draft in this repo's 51-file `charness-artifacts/release/` was ever
#: missed by requiring `notes`, so the widening closed no observed miss — while
#: `release`, matched inside a directory literally named `release`, made a dated
#: `<date>-<version>-release-record.md` match, and the refusal's remedy tells the
#: operator to "rename or delete it and commit that". A verdict surface at an
#: irreversible boundary instructing an operator to delete durable evidence to
#: get past a gate is worse than the miss it was guarding against.
#:
#: What this does NOT close, stated rather than implied: a draft with no role
#: word at all (`v1.2.3.md`, the name `--notes-file charness-artifacts/release/
#: v1.2.3.md` naturally produces) is still invisible to this arm. An allowlist
#: relocates that miss rather than closing it. The answer is to publish the
#: recognized shape as a convention so a drafter can follow it — written into
#: `references/adapter-contract.md` in the same commit, because an earlier
#: version of this comment claimed the contract already documented it and it did
#: not: a claim rendered over a scope nobody established, inside the rationale of
#: the fix for that class.
_NOTES_ROLE_WORD = "notes"
_STEM_TOKEN_SEPARATORS = re.compile(r"[-_]")


def _reads_as_notes(stem: str) -> bool:
    """Whether ``stem`` carries the notes role word as a whole token.

    Token equality, not a bare substring: the substring form is what made the
    reverted `release` widening match a dated release RECORD, and it would match
    `footnotes` or `denotes` here for the same reason. Position is deliberately
    free — this repo uses both `v0.55.0-notes` and `notes-v0.56.7`, so a
    last-token rule would drop five real drafts.
    """
    return _NOTES_ROLE_WORD in _STEM_TOKEN_SEPARATORS.split(stem.lower())


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

    # ABSENT and UNREADABLE are different answers and used to be the same one.
    # An absent directory is the normal state for a repo that drafts no notes, so
    # it stays silent and publishable. An unreadable one is a directory this
    # function could not look inside, and reporting "no drafted notes" for it is
    # a claim about contents nobody read.
    #
    # `Path.glob` was the reason the distinction could not be made: it swallows
    # the scandir error and yields nothing, which is why an `except OSError`
    # guard written here once was DEAD and its test passed because the glob
    # returned empty rather than because anything was caught. `iterdir` raises,
    # so the guard below is reachable — verified by executing it, not by adding
    # it back and assuming.
    # EVERY stat is inside the guard, not just the listing. `is_dir()` raises on
    # an unreadable PARENT and the per-entry `is_file()` raises under `chmod 444`
    # (names readable, entries not stattable) -- two modes that escaped the first
    # version of this guard as raw PermissionErrors, i.e. the traceback-where-a-
    # verdict-belongs shape this arm was being repaired for. Both executed.
    try:
        if not notes_dir.is_dir():
            return []
        candidates = [
            path for path in notes_dir.iterdir()
            if path.suffix == ".md" and path.is_file()
        ]
    except OSError as exc:
        raise NotesDirectoryUnreadable(
            f"could not read the drafted-notes directory `{output_dir}`: {exc}"
        ) from exc
    return sorted(
        (path for path in candidates
         if _reads_as_notes(path.stem) and names_this_version(path.stem)),
        key=lambda path: path.name,
    )


