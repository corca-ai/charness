#!/usr/bin/env python3
"""How to READ a probe record, and whether its quote is really in the source it cites.

Split from ``probe_record_lib`` on the concept boundary that module's own siblings
already use: ``issue_closeout_rung1_floors`` says of its neighbour that "that module
answers 'how do I read a field out of markdown', and this one answers 'what must the
body carry'". Same split, same reason -- and here it is load-bearing rather than
cosmetic, because every markdown-grammar defect found in slice 1's review
(column-anchored fields, multi-token info strings, four-backtick fences, repeated
fields, relative indentation in a quote) belongs to THIS concern and none of them
belongs to "what does this record establish".

``probe_record_lib`` re-exports this module's public names, so consumers keep one
import site and nothing outside had to learn about the split.

BLIND CLASS of this half specifically: it is a grammar and a substring check. It knows
nothing about claims, arms, or verdicts, and `verify_source_quote` proves a quote is
PRESENT in a source -- never that it is the right quote, and never that the stimulus
beside it follows from what was quoted. The module docstring of ``probe_record_lib``
carries the full list.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.subprocess_guard import run_process

# FIELD LINES START AT COLUMN 0. The permissive `^\s*` this replaces made every indented
# line a candidate field, so a markdown sub-list under a value (`  - the exit status: 0 vs
# 1`) parsed as a field named `the exit status`, left the real field empty, and STOLE the
# continuation target from it. Column-anchoring makes the two shapes disjoint: at column 0
# it is a field, indented it is a continuation, and nothing has to arbitrate.
_FIELD_RE = re.compile(r"^(?:[-*]\s*)?(?P<key>[A-Za-z][A-Za-z0-9 _-]*?)\s*:\s*(?P<value>.*?)\s*$")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<title>.+?)\s*$")
# Any info string, not one token: ```` ```console session ```` and ```` ```py title="x" ````
# are ordinary, and failing to recognise the OPENING fence made every line of the block
# parse as fields while the CLOSING fence then opened a phantom one that swallowed the
# rest of the record.
_FENCE_RE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})\s*(?P<info>.*)$")
_PLACEHOLDER_RE = re.compile(r"^(?:tbd|todo|n/?a|none|-+|\.+|\?+)$", re.IGNORECASE)
# A source ref that names a path this repo can open. `path::node_id` is pytest's form
# and `path:line` the editor form; both keep only the path for reading.
_LOCAL_REF_RE = re.compile(r"^(?P<path>[^\s:]+(?:/[^\s:]+)*\.[A-Za-z0-9_]+)(?:::|:)?")
_NONLOCAL_REF_RE = re.compile(r"^(?:https?://|issue[:# ]|#\d)", re.IGNORECASE)
# "there are no unproven call sites" -- ANCHORED to the leading token, and the ONLY
# separator allowed before a reason is a dash-that-is-not-a-hyphen.
#
# The first cut allowed `[—–:;.,-]`, reasoning that a separator splits a reason from a
# negation. A bounded review falsified that: `,`, `;`, `.` and `-` CONTINUE a sentence
# exactly as `of` does, so `none, but the helper path in adapter.py:41 was not checked`
# and `none. adapter.py:41 remains unchecked` both read as full coverage while SAYING the
# opposite. Worse, an indented markdown sub-list under a bare `none` merges through the
# continuation rule into `none - adapter.py:41 ...`, so the shape an author is most
# likely to reach for was the one that reported the reverse of what it said.
# Only `—`/`–` introduce a parenthetical in a way a continuation cannot, so only those
# are accepted; a trailing period on a bare `none.` is fine because nothing follows it.
_NO_UNPROVEN_SITES_RE = re.compile(r"^none\s*(?:\.\s*$|[—–]\s*\S|$)", re.IGNORECASE)


def _normalize_key(raw: str) -> str:
    return re.sub(r"[ -]+", "_", raw.strip().strip("`*").lower())


def _substantive(value: object) -> bool:
    """A value that says something. Mirrors the closeout floors' `_has_substantive_value`
    rather than importing it: those live in a public skill that must not depend on
    repo-internal `scripts/`, and the dependency direction here is the reverse one."""
    text = str(value or "").strip().strip("`*").strip()
    return bool(text) and not _PLACEHOLDER_RE.match(text)


def parse_probe_record(text: str) -> dict:
    """Split a probe record into its ``Key: value`` fields and its fenced sections.

    Field lines are read only OUTSIDE fences, so a `Claim:` line quoted inside a
    stimulus block is the stimulus, not the record's claim. Sections are keyed by the
    heading above the fence, normalized the same way field keys are, and a heading with
    no fence under it yields an empty section rather than being dropped -- the
    difference between "the author wrote nothing" and "the author wrote no heading" is
    exactly what the required-section check needs to see.
    """
    fields: dict[str, str] = {}
    duplicated: list[str] = []
    sections: dict[str, str] = {}
    filled: set[str] = set()
    last_key: str | None = None
    heading: str | None = None
    fence: str | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        if fence is not None:
            # The FULL opening fence must be matched to close. Truncating it to three
            # characters meant a four-backtick fence -- which is exactly how markdown
            # containing fences is quoted, and this repo's most quotable sources are
            # markdown -- was closed by its own first inner fence. The quote truncated
            # to a prefix, and a prefix of a real quote still verifies, so the loss was
            # silent AND in the accepting direction.
            if line.strip().startswith(fence):
                if heading is not None:
                    # APPEND rather than keep-first. A section written as a command fence
                    # followed by an output fence used to keep only the command, and when
                    # both arms led with the same command that made base==head fire on a
                    # real measurement.
                    body = "\n".join(buffer)
                    # Keyed on `filled`, NOT on the truthiness of the stored value: a
                    # heading seeds `""`, and an EMPTY first fence is still a fence that
                    # ran, so a truthiness guard silently overwrote it instead of
                    # appending the second -- the one case the append was added for.
                    sections[heading] = (
                        f"{sections[heading]}\n{body}".strip("\n") if heading in filled else body
                    )
                    filled.add(heading)
                fence = None
                buffer = []
            else:
                buffer.append(line)
            continue
        if match := _FENCE_RE.match(line):
            fence = match.group("fence")
            buffer = []
            last_key = None
            continue
        if match := _HEADING_RE.match(line):
            heading = _normalize_key(match.group("title"))
            sections.setdefault(heading, "")
            last_key = None
            continue
        if match := _FIELD_RE.match(line):
            key = _normalize_key(match.group("key"))
            # A REPEATED field is ambiguous, and first-wins silently picked a winner. On a
            # proof artifact that is the wrong resolution in both directions: an author
            # who restates a field lower to correct it has the correction discarded, and a
            # record whose intro DEMONSTRATES the format at column 0 resolves against the
            # example while a human reads the real values below. Nothing in the output
            # echoed the fields, so the divergence was invisible. Refuse instead of choose.
            if key in fields:
                if key not in duplicated:
                    duplicated.append(key)
                # The record is refused as ambiguous either way, but leaving `last_key`
                # pointed at the duplicate glues its indented wrap onto the FIRST
                # occurrence's value -- corrupting the very value the refusal reports.
                last_key = None
            else:
                fields[key] = match.group("value").strip()
                last_key = key
            continue
        # INDENTED CONTINUATION. Field values here are prose that cites paths and node
        # ids, and the markdown gate wraps long lines -- so without this, a value that
        # had to wrap is silently stored as its first line and the record reports a
        # truncated claim under a passing verdict. That exact loss is a lesson this repo
        # already paid for three round-trips on a different line-anchored carrier.
        # Indentation is the signal, so an ordinary following paragraph cannot be
        # swallowed, and a blank line ends the value.
        if not line.strip():
            last_key = None
            continue
        if last_key is not None and line[:1].isspace() and last_key in fields:
            fields[last_key] = f"{fields[last_key]} {line.strip()}".strip()
    return {"fields": fields, "sections": sections, "duplicated_fields": duplicated}


def _normalized_lines(text: str) -> list[str]:
    """A block's lines with RELATIVE indentation preserved and the common indent removed.

    The first cut stripped every line, which was a hole in the module's central claim.
    A YAML source

        deliberately_absent:
          planner:
            - some-key

    was `verified` by a record quoting it FLATTENED to column zero -- which is the
    mapping-vs-list confusion of `#528`, passing the check written in response to `#528`.
    The same class exists in Python (a line quoted out of its `if` branch) and in
    markdown (a list item quoted at the wrong depth).

    Dedenting by the block's own minimum, rather than per line, keeps what markdown
    legitimately does to a quote -- indent the whole thing -- while preserving the
    structure that distinguishes a mapping from a list.

    Blank lines are still dropped, which is a REMAINING gap and not an oversight: a quote
    can splice two paragraphs the source separates. Keeping them would refuse a record
    that merely reflowed its quote, and reflowing is the more common author action.
    """
    return _dedent([line.rstrip() for line in text.splitlines() if line.strip()])


def _dedent(lines: list[str]) -> list[str]:
    """Remove the block's own minimum indentation, preserving what is relative to it."""
    if not lines:
        return []
    pad = min(len(line) - len(line.lstrip()) for line in lines)
    return [line[pad:] for line in lines]


def _contains_block(haystack: list[str], needle: list[str]) -> bool:
    """Is ``needle`` a contiguous run of ``haystack``, compared at matching relative depth?

    Each WINDOW is dedented rather than the haystack as a whole, so a block nested inside
    its source matches a record that quoted it without the surrounding indentation --
    while a block whose INTERNAL structure was flattened does not.
    """
    if not needle:
        return False
    return any(
        _dedent(haystack[index : index + len(needle)]) == needle
        for index in range(len(haystack) - len(needle) + 1)
    )


def _read_source(repo_root: Path, rel: str, revision: str | None) -> tuple[str | None, str | None]:
    """``(body, error)`` for one source, from the worktree or from a pinned revision.

    Pinning exists because the most quotable sources here are LIVING documents. A record
    that quotes a living document verifies today and reads `absent` the next time anyone
    edits that file -- and the record would then be reporting a provenance failure for a
    repair that was fine, which trains readers to ignore the signal. `Source revision:`
    makes the frozen target explicit and visible in the record instead of implicit in
    whenever the check happened to run.
    """
    if revision:
        try:
            done = run_process(
                ["git", "show", f"{revision}:{rel}"], cwd=repo_root, timeout_seconds=None
            )
        except OSError as exc:  # pragma: no cover - git absent from PATH
            return None, f"could not run git to read `{rel}` at `{revision}`: {exc}"
        if done.returncode != 0:
            return None, f"could not read `{rel}` at revision `{revision}`: {done.stderr.strip()}"
        return done.stdout, None
    try:
        return (repo_root / rel).read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"could not read `{rel}`: {exc}"


def verify_source_quote(
    repo_root: Path, source_ref: str, source_text: str, *, revision: str | None = None
) -> dict:
    """Is the quoted source text actually present in the cited source?

    WHAT THIS IS AND IS NOT, corrected after a bounded review found the first version of
    this docstring crediting itself with `#528`. It is NOT `#528`'s countermeasure --
    the base/HEAD arm rule is, per the goal's own refutation table. Walk `#528` through
    this check and it does not fire: the vocabulary is defined in a docstring in
    `scripts/quality_bootstrap_absence.py` carrying the mapping shape verbatim, so the
    author quotes those real lines into `Source text:` and writes the invented
    list-shaped YAML into `Stimulus:`, and nothing here compares the two. A correct
    quote paired with a contradicting stimulus is `verified`.

    What it DOES buy is that the correct shape now sits on the page four lines above the
    wrong one, where a distinct observer sees the mismatch immediately instead of having
    to go find the source. That is a P4 legibility tooth, not a mechanical one, and
    saying so is the difference between a remedy set that covers two failures and one
    that reports three.

    Checking the QUOTE rather than the stimulus is still deliberate: the stimulus is
    derived and the derivation is judgment, but the quote is either in the file or it is
    not. What the check genuinely refuses is a record citing a source that does not say
    what the record claims it says.

    Returns ``status`` of ``verified`` / ``absent`` / ``unresolvable``, never a bare
    bool: `unresolvable` (a GitHub issue body, a URL) is not a failure and must not
    render as one, but it is not a verification either, and the record owes a degraded
    reason for it exactly as `evaluate_source_preservation` requires.
    """
    # `local` DRIVES THE DEGRADED-REASON ESCAPE in `resolve_probe_record`, so it is set from
    # the POSITIVE nonlocal test and never from "we fell off the end of the path grammar".
    # A round-2 review measured why that distinction is the whole rule: keyed the other way,
    # `local` was False for anything `_LOCAL_REF_RE` failed to match, and that regex requires
    # a dot-extension -- so `Source ref: adapterTYPO` was EXCUSED while `adapterTYPO.py` was
    # refused. Deleting three characters was cheaper than the typo the previous repair had
    # just closed, and an author who hits "Fix the ref" reaches the escape by SHORTENING the
    # thing they were told to fix. Extension-less real files (`Makefile`, `LICENSE`) sat in
    # the same excused bucket. The repair shipped the class it repaired; this is round 2
    # catching it, which is what the two-round rule on a proof surface is for.
    ref = (source_ref or "").strip().strip("`")
    nonlocal_ref = bool(_NONLOCAL_REF_RE.match(ref))
    if not ref or not _substantive(source_text):
        return {
            "status": "unresolvable",
            "reason": "no source ref or no quoted source text",
            "path": None,
            "local": not nonlocal_ref,
        }
    if nonlocal_ref:
        return {
            "status": "unresolvable",
            "reason": f"`{ref}` is not a path this repo can open",
            "path": None,
            "local": False,
        }
    match = _LOCAL_REF_RE.match(ref)
    if match is None:
        return {
            "status": "unresolvable",
            "reason": f"`{ref}` does not name a readable path, and is not one of the forms this "
            "repo cannot read by nature (an issue ref, a URL)",
            "path": None,
            "local": True,
        }
    rel = match.group("path")
    # A ref must resolve INSIDE the repo. `Path.__truediv__` lets an absolute ref replace
    # the root outright, so `/tmp/my-notes.txt` -- a file the author wrote themselves and
    # no reviewer can open from the repo -- read back as `verified`. Self-verifying
    # provenance is worse than none, because it carries the word.
    try:
        inside = (repo_root / rel).resolve().is_relative_to(repo_root.resolve())
    except (OSError, ValueError):  # pragma: no cover - unresolvable path shapes
        inside = False
    if not inside:
        return {
            "status": "unresolvable",
            "reason": f"`{rel}` resolves outside the repo, so no reviewer can open it from here",
            "path": rel,
            "local": True,
        }
    body, error = _read_source(repo_root, rel, revision)
    if error is not None:
        return {"status": "unresolvable", "reason": error, "path": rel, "local": True}
    if _contains_block(_normalized_lines(body), _normalized_lines(source_text)):
        return {"status": "verified", "reason": None, "path": rel, "local": True}
    return {
        "status": "absent",
        "reason": f"the quoted source text does not appear in `{rel}`",
        "path": rel,
        "local": True,
    }
