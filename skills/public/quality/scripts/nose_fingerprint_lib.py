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
- ``rstrip`` each line (trailing-whitespace / line-ending invariant) and join with ``\n``,
- sha256 → 16-hex per member,
- the family fingerprint = sha256 of the **sorted, duplicate-preserving** member-hash
  list → 16-hex.

This is invariant to member order, line offset, and file path; sensitive to member
content, membership, and member multiplicity (do NOT ``set()``-dedup the member hashes,
or ``{A, A, B}`` would collapse to ``{A, B}`` and collide with a real 2-member family).
A pure line-shift keeps the fingerprint stable while nose's id rotates; a genuine span
edit rotates the fingerprint, so real new/changed duplication is still caught.

``FINGERPRINT_ALGO_VERSION`` is stamped into the baselines beside nose's ``tool_version``:
the family SET (which spans nose groups) is still nose-version-scoped, while the IDENTITY
is now ours, so a future normalization change (e.g. landing the deferred token/comment-aware
algorithm) surfaces as algo-version skew — a re-baseline signal, never a corpus-wide false
block. ``family_content_fingerprint`` returns ``None`` when any member span cannot be read
(missing/unreadable file, out-of-range line span); the gate degrades the WHOLE gate to
advisory on ``None`` (FD8), never false-blocks, never silently drops the family.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

FINGERPRINT_ALGO_VERSION = "1"


def normalize_span(lines: list[str]) -> str:
    """Offset/whitespace-tolerant span normalization: rstrip each line, join with ``\n``.

    rstrip-only is deliberately STRICTER than nose's tokenizer (an in-place comment edit
    inside a span rotates this fingerprint where nose would not); that residual is the
    deferred S4-Defer-1 token-aware normalization, not a v1 goal."""
    return "\n".join(line.rstrip() for line in lines)


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def member_fingerprint(repo_root: Path, file: Any, start: Any, end: Any) -> str | None:
    """16-hex content hash of one member span, or ``None`` when it cannot be read.

    ``file`` is repo-relative (nose runs with ``cwd=repo_root``); ``start``/``end`` are
    1-based inclusive. An out-of-range span (the file changed between scan and read) is a
    degrade signal, not a silent partial hash."""
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
    return _sha16(normalize_span(lines[start - 1 : end]))


def family_content_fingerprint(family: dict[str, Any], repo_root: Path) -> str | None:
    """Offset/path-independent content fingerprint for one nose family, or ``None`` when
    any member span is unreadable (whole-gate degrade per FD8).

    Reads the RAW ``nose query`` family's ``locations`` list (keys ``file``/``start``/
    ``end``) — NOT ``family_summary``/``sample_locations`` (those truncate to 6 members).
    The member hashes are kept in a duplicate-preserving list so multiplicity is part of
    the identity."""
    locations = family.get("locations")
    if not isinstance(locations, list) or not locations:
        return None
    member_hashes: list[str] = []
    for location in locations:
        if not isinstance(location, dict):
            return None
        fingerprint = member_fingerprint(
            repo_root, location.get("file"), location.get("start"), location.get("end")
        )
        if fingerprint is None:
            return None
        member_hashes.append(fingerprint)
    return _sha16("\n".join(sorted(member_hashes)))
