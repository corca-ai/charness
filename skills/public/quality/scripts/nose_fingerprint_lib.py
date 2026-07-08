#!/usr/bin/env python3
"""Offset/path-independent content fingerprint for nose clone families (item 5, slice 4).

The dup-ratchet gate and the clone advisory historically keyed code-clone newness on
nose's ``family_id``. That id folds each member span's normalized content AND its line
offset AND its file path, so editing any scanned member file — even inserting lines
*above* an unchanged duplicated span — rotates the whole family id with zero new
duplication, false-blocking the hard arm and forcing a manual re-baseline (deferred
decision D30; the 2026-06-21 rotation debug). nose 0.15.0 (schema v6) still emits no
position-independent content identity, so the gate computes its own here.

The fingerprint is derived from member span CONTENT only:

- read each member's source span by its raw ``nose query`` location ``(file, start, end)``
  (repo-relative ``file`` — nose runs with ``cwd=repo_root``; 1-based inclusive lines),
- normalize each span (see below) and sha256 -> 16-hex per member,
- the family fingerprint = sha256 of the **sorted, duplicate-preserving** member-hash
  list -> 16-hex.

This is invariant to member order, line offset, and file path; sensitive to member
content, membership, and member multiplicity (do NOT ``set()``-dedup the member hashes,
or ``{A, A, B}`` would collapse to ``{A, B}`` and collide with a real 2-member family).
A pure line-shift keeps the fingerprint stable while nose's id rotates; a genuine span
edit rotates the fingerprint, so real new/changed duplication is still caught.

``FINGERPRINT_ALGO_VERSION`` is stamped into the baselines beside nose's ``tool_version``:
the family SET (which spans nose groups) is still nose-version-scoped, while the IDENTITY
is now ours, so a normalization change (landing here as algo v2) surfaces as algo-version
skew — a re-baseline signal, never a corpus-wide false block. ``family_content_fingerprint``
returns ``None`` when any member span cannot be read (missing/unreadable file, out-of-range
line span); the gate degrades the WHOLE gate to advisory on ``None`` (FD8), never
false-blocks, never silently drops the family.

Algo v1 (rstrip-only): ``rstrip`` each line and join with ``\n`` (``normalize_span``).
Offset/whitespace-tolerant, but STRICTER than nose's own tokenizer — an in-place comment
edit or an internal-whitespace edit inside a duplicated span (no line-count change)
rotates the v1 fingerprint where nose's normalized id would not (the deferred S4-Defer-1
residual).

Algo v2 (token/comment-aware, the S4-Defer-1 resolution) — Python members ONLY
(``file`` ends in ``.py``): ``textwrap.dedent`` the joined raw span text, tokenize it
(``tokenize.generate_tokens``), drop two classes of token: comment/line-boundary noise
(``COMMENT``/``NL``/``NEWLINE``/``ENCODING``/``ENDMARKER``) AND ``INDENT``/``DEDENT``.
The second class is NOT whitespace noise — ``INDENT``/``DEDENT`` encode BLOCK-NESTING
structure, so dropping them makes the hash nesting-insensitive: a body statement hashes
the same whether it sits at top level or one level deeper inside an ``if``/``for``/etc.,
because after ``dedent`` the two spans' token streams are identical once INDENT/DEDENT
are removed. Every other token's exact string survives, so an identifier/literal/operator
change still rotates the hash. This nesting-insensitivity is DELIBERATE and safe, not an
oversight: nose's own family grouping (mode ``syntax``/``semantic``/``near``) already
clusters such block-nesting variants into ONE family (an
``extract-method-from-block``-shaped near-duplicate) — the fingerprint only needs to be
a stable identity for members nose has ALREADY decided belong together, so it is never
asked to distinguish members nose itself treats as interchangeable. The one-shot
migration tool's collision assertion (``distinct(v2 fingerprints) ==
distinct(nose family ids)`` over the live scan) is the enforcement backstop: if this
v2/nose alignment ever breaks (nose starts splitting block-nesting variants into
separate families while v2 still collapses them), the assertion fails closed and the
migration refuses to proceed rather than silently mis-migrating. A span that is not
standalone-parseable (e.g. a bracket-unbalanced fragment, or a dangling ``else:``)
legitimately fails ``tokenize`` — on ANY of ``tokenize.TokenError`` /
``IndentationError`` / ``SyntaxError`` the member falls back, PER MEMBER, to the v1
rstrip normalization; it never crashes and never degrades the whole family. Non-``.py``
members (the corpus's 39 ``.mjs`` clone members, as of this writing) always use v1
regardless of the requested algo — a JS/TS-aware tokenizer is not in scope here; this is
an accepted, documented v2 gap, not an oversight.

``member_fingerprint`` / ``family_content_fingerprint`` take an explicit ``algo``
keyword (default ``FINGERPRINT_ALGO_VERSION``; ``"1"`` reproduces v1 behavior exactly
regardless of file extension) so a caller — notably the one-shot algo-migration tool —
can compute a family's fingerprint under BOTH algorithms from the same scan.
``family_member_hashes`` exposes the sorted, duplicate-preserving per-member hash list
itself (schema v3 baselines store it; the reduction pre-pass diffs it as a multiset).
"""

from __future__ import annotations

import hashlib
import io
import textwrap
import tokenize
from pathlib import Path
from typing import Any

FINGERPRINT_ALGO_VERSION = "2"

# Token types dropped by v2 normalization, two classes:
# - comment/line-boundary noise: COMMENT, blank-line NL, statement NEWLINE.
#   ENCODING/ENDMARKER are tokenizer bookkeeping, not span content.
# - INDENT/DEDENT: BLOCK-NESTING structure, NOT whitespace noise. Dropping these
#   makes the hash nesting-insensitive (an identical body statement hashes the same
#   at top level or one level deeper inside an if/for/etc.) -- deliberate and safe
#   because nose's own family grouping already clusters such block-nesting variants
#   into one family; see the module docstring and the migration tool's collision
#   assertion, which fails closed if that v2/nose alignment ever breaks.
# Everything else (NAME, OP, NUMBER, STRING, keywords) survives verbatim, so a real
# identifier/literal/operator edit still rotates the hash (SC: content-sensitivity
# is preserved under v2).
_V2_DROP_TOKEN_TYPES = frozenset(
    {
        tokenize.COMMENT,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENCODING,
        tokenize.ENDMARKER,
    }
)


def normalize_span(lines: list[str]) -> str:
    """Algo v1: offset/whitespace-tolerant span normalization: rstrip each line,
    join with ``\n``. STRICTER than nose's tokenizer (an in-place comment/internal-
    whitespace edit inside a span rotates this where nose would not); kept as the
    v2 per-member fallback for a span that does not tokenize standalone, and as the
    always-used normalization for non-Python members."""
    return "\n".join(line.rstrip() for line in lines)


def _normalize_span_v2(lines: list[str]) -> str:
    """Algo v2: token-aware normalization for a Python span. Dedents the joined raw
    span text (a nested/indented span must dedent to tokenize as a standalone unit),
    tokenizes it, and joins the surviving token strings with a single space. Raises
    ``tokenize.TokenError`` / ``IndentationError`` / ``SyntaxError`` on a span that is
    not standalone-parseable; the caller catches those and falls back to v1."""
    text = textwrap.dedent("\n".join(lines) + "\n")
    tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    pieces = [tok.string for tok in tokens if tok.type not in _V2_DROP_TOKEN_TYPES]
    return " ".join(pieces)


def _normalize_member(lines: list[str], *, algo: str, is_python: bool) -> str:
    """Pick the normalization for one member span: v2 tokenize-aware for a ``.py``
    member under algo v2, falling back to v1 rstrip on ANY tokenize failure; v1 for
    every non-Python member and for algo ``"1"`` regardless of extension."""
    if algo == "2" and is_python:
        try:
            return _normalize_span_v2(lines)
        except (tokenize.TokenError, IndentationError, SyntaxError):
            pass
    return normalize_span(lines)


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def member_fingerprint(
    repo_root: Path, file: Any, start: Any, end: Any, *, algo: str = FINGERPRINT_ALGO_VERSION
) -> str | None:
    """16-hex content hash of one member span, or ``None`` when it cannot be read.

    ``file`` is repo-relative (nose runs with ``cwd=repo_root``); ``start``/``end`` are
    1-based inclusive. An out-of-range span (the file changed between scan and read) is a
    degrade signal, not a silent partial hash. ``algo`` selects the normalization
    (default the current ``FINGERPRINT_ALGO_VERSION``; ``"1"`` forces v1 rstrip-only)."""
    if not isinstance(file, str) or not file:
        return None
    if not isinstance(start, int) or isinstance(start, bool):
        return None
    if not isinstance(end, int) or isinstance(end, bool):
        return None
    try:
        content = (repo_root / file).read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    lines = content.splitlines()
    if start < 1 or end < start or end > len(lines):
        return None
    span_lines = lines[start - 1 : end]
    normalized = _normalize_member(span_lines, algo=algo, is_python=file.endswith(".py"))
    return _sha16(normalized)


def family_member_hashes(
    family: dict[str, Any], repo_root: Path, *, algo: str = FINGERPRINT_ALGO_VERSION
) -> list[str] | None:
    """Sorted, duplicate-preserving per-member hash list for one nose family, or
    ``None`` when any member span is unreadable (mirrors ``family_content_fingerprint``'s
    whole-family degrade). Schema v3 baselines store this list per family; the CLI's
    reduction pre-pass compares it as a multiset (``collections.Counter``) against a
    vanished baseline family's member hashes.

    Reads the RAW ``nose query`` family's ``locations`` list (keys ``file``/``start``/
    ``end``) — NOT ``family_summary``/``sample_locations`` (those truncate to 6 members)."""
    locations = family.get("locations")
    if not isinstance(locations, list) or not locations:
        return None
    member_hashes: list[str] = []
    for location in locations:
        if not isinstance(location, dict):
            return None
        fingerprint = member_fingerprint(
            repo_root, location.get("file"), location.get("start"), location.get("end"), algo=algo,
        )
        if fingerprint is None:
            return None
        member_hashes.append(fingerprint)
    return sorted(member_hashes)


def fingerprint_from_member_hashes(member_hashes: list[str]) -> str:
    """Family fingerprint from an already-computed sorted member-hash list (no file
    I/O). Lets a caller that already called ``family_member_hashes`` (e.g. the nose
    report collection point, which stamps both fields) derive the fingerprint without
    re-reading and re-tokenizing every member span a second time."""
    return _sha16("\n".join(member_hashes))


def family_content_fingerprint(
    family: dict[str, Any], repo_root: Path, *, algo: str = FINGERPRINT_ALGO_VERSION
) -> str | None:
    """Offset/path-independent content fingerprint for one nose family, or ``None`` when
    any member span is unreadable (whole-gate degrade per FD8). Composed from
    ``family_member_hashes`` so both share the exact same per-member normalization."""
    member_hashes = family_member_hashes(family, repo_root, algo=algo)
    if member_hashes is None:
        return None
    return fingerprint_from_member_hashes(member_hashes)
