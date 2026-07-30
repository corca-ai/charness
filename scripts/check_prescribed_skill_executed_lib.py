"""Portable closeout-evidence check shared by achieve/issue/release closeouts.

The lighter self-substitution pattern (#230 + #229) emerges when an agent
inline-paraphrases a prescribed sub-skill (`retro`, `critique`,
`probe_host_logs.py`) instead of executing it. This library is the gate
that the three sibling skills wrap with their own evidence shape; the
contract lives at ``docs/prescribed-skill-closeout-contract.md``.

The library is intentionally policy-free: callers declare the required
evidence names and supply each name's path-or-skip. The library checks
file existence + non-empty content for paths and validates skip reasons
against a small enum so a free-text "host limit" cannot become the new
lighter substitute.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ALLOWED_SKIP_REASONS = frozenset(
    {
        "host-blocked-subagent",
        "host-log-not-exposed",
        "evaluator-unavailable",
    }
)
MIN_SKIP_LENGTH = 40

# Minimum length of the skip *detail* — the text after the enum head and its
# colon — checked alongside ``MIN_SKIP_LENGTH`` on the whole string.
#
# Some callers (``issue_resolution_critique``, ``publish_release_preflight``)
# manufacture the enum head themselves from a shorthand the author wrote. On
# those carriers the enum check validates a constant the caller supplied, so the
# length floor is the only surviving tooth — and the head's own characters were
# paying it down: ``host-blocked-subagent: `` is 23 characters, so the 40-char
# total floor accepted a 17-character signal and skipped a mandatory fresh-eye
# critique on a GitHub issue close (B2). This floor measures only the text the
# author actually chose, so head length can no longer set the bar.
#
# 20, not 40. The pre-fix effective bar for manufactured-head callers was already
# ~17; the repo's own genuine host signals run 24-39 characters, so a 40-char
# detail floor would sit ABOVE observed honest usage and buy padding rather than
# signal. Length is not the real tooth here and cannot be: a fluent 40-character
# excuse passes any length floor. What distinguishes a skipped critique from an
# executed one is that the skip is now LOUD — see ``_skip_advisories`` in
# ``issue_resolution_critique.py``. This floor only refuses terseness.
MIN_SKIP_DETAIL_LENGTH = 20

# Cap how much of an evidence file is scanned for a binding token. A retro or
# probe artifact references its goal/issue/release identity in the first
# screenful when it does at all; reading more buys nothing and risks a large
# file stalling the gate.
_BINDING_CONTENT_SCAN_BYTES = 65536

# A bare numeric-cluster token (e.g. ``230-229`` or ``185``) is matched on
# non-alphanumeric boundaries, not raw substring, so ``185`` does not falsely
# bind a file whose body merely contains ``21850`` or ``0185abc``. Slug tokens
# carry their own distinctiveness and match as substrings.
_NUMERIC_CLUSTER_TOKEN = re.compile(r"^\d+(?:[-_]\d+)*$")

# A *bare* numeric token (``27``) is far weaker than a compound cluster
# (``230-229``): boundary matching alone still bound it to any standalone digit
# run in the body, so a critique of a different issue bound a #27 closeout
# purely through its ``Date: 2026-07-27`` header (B4), and ``v0.42.1`` /
# ``14:32:05`` bound #42 / #32. In CONTENT a bare number therefore has to be
# CITED, not merely present: ``#27``, ``issue 27``, ``issues/27``, ``gh-27``.
# Every checked-in critique/retro artifact in this repo names its issue that way
# (``Issue: #367``, ``Target: issue #184``, ``Closes #349``,
# ``corca-ai/charness#429``), so the citation requirement refuses coincidence
# without refusing the forms the repo actually writes.
# The separator class admits the markdown a real artifact wraps a citation in
# (``goal **253**``, ``issue `184` ``, ``the fix (#253)``), and the trailing
# citation RUN lets a list inherit its marker: this repo writes
# ``issues 118, 119, and 120`` and ``Resolve issues 356 and 357``, and binding
# only the first member would refuse a correct bundled closeout. A run cannot
# manufacture a coincidence, because it still has to start at a marker --
# ``Date: 2026-07-27`` has none.
_BARE_NUMERIC_TOKEN = re.compile(r"^\d+$")
_CITATION_SEPARATOR = r"[\s#:/_\-*`\[(\"']"
_NUMERIC_CITATION_PREFIX = re.compile(
    r"(?:#"
    rf"|(?:^|[^0-9a-z])(?:issues?|gh|prs?|goal|slice|no\.?|number){_CITATION_SEPARATOR}{{0,3}}"
    rf")(?:(?:\d+|and|&|,|;){_CITATION_SEPARATOR}{{0,3}})*$"
)

# Date/time/timestamp runs carry no closeout identity, but they are digit runs
# on clean boundaries, so they are masked out of a BASENAME before a bare
# numeric token is matched against it: ``2026-05-14-013911-packet.md`` must not
# bind #2026, #14 or #5 while ``2026-05-28-185-foo.md`` still binds #185.
# ``-`` is deliberately NOT a time-tail separator: a bundled-artifact basename
# like ``2026-07-30-12-13-closeout.md`` is this repo's own naming shape, and
# reading ``-12-13`` as a clock would mask away two real issue numbers. Harmless
# here (charness issues are 3-digit) and not harmless in a consuming repo whose
# whole backlog is #1-#99, which is what this skill ships into.
_DATELIKE_RUN = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:[t _]\d{2}[:_]?\d{2}(?:[:_]?\d{2})?)?|\d{6,}"
)


def _boundary_match(token: str, haystack: str) -> bool:
    return (
        re.search(rf"(?<![0-9a-z]){re.escape(token)}(?![0-9a-z])", haystack)
        is not None
    )


def _token_matches(token: str, haystack: str, *, in_name: bool = False) -> bool:
    """True when ``token`` (already lowercased) occurs in ``haystack``.

    Numeric-cluster tokens require non-alphanumeric neighbours so a short issue
    number cannot bind on a coincidental digit run; other tokens use plain
    containment. A bare numeric token additionally must be *cited* when matched
    against file content, and is matched against a date-masked basename, so a
    date/time/version digit run cannot manufacture a binding it did not earn.
    """
    if not _NUMERIC_CLUSTER_TOKEN.match(token):
        return token in haystack
    if not _BARE_NUMERIC_TOKEN.match(token):
        # Compound clusters (``230-229``) are distinctive on their own.
        return _boundary_match(token, haystack)
    if in_name:
        if len(token) >= 6:
            # A token that is itself timestamp-shaped must not be masked away.
            return _boundary_match(token, haystack)
        masked = _DATELIKE_RUN.sub(lambda m: "." * len(m.group(0)), haystack)
        return _boundary_match(token, masked)
    for match in re.finditer(
        rf"(?<![0-9a-z]){re.escape(token)}(?![0-9a-z])", haystack
    ):
        if _NUMERIC_CITATION_PREFIX.search(haystack[: match.start()]):
            return True
    return False


def evidence_binds_to_context(
    path: Path, *, tokens: list[str]
) -> tuple[bool, str]:
    """Return ``(binds, reason)`` for whether an evidence file pertains to its
    closeout context.

    File *presence* is necessary but not sufficient: a closeout can cite any
    pre-existing artifact in the repo and pass the presence check (the #233 F1
    hole). An evidence file *binds* to its context when its basename or its
    content contains at least one distinctive context token (a goal slug, an
    issue number, a release version).

    Token containment is deliberately the binding signal rather than mtime:
    a fresh ``git clone`` resets every file's mtime to checkout time, so an
    ``mtime >= context-date`` rule would pass for every stale file in a cloned
    tree and silently reopen the exact hole this guards. Basename/content
    containment is clone-safe.

    ``tokens`` empty means the caller could not derive a context identity; the
    caller opts out of binding and only the presence check applies.
    """
    if not tokens:
        return True, "no binding tokens supplied"
    lowered = [token.lower() for token in tokens if token]
    if not lowered:
        return True, "no binding tokens supplied"
    name = path.name.lower()
    for token in lowered:
        if _token_matches(token, name, in_name=True):
            return True, f"basename contains {token!r}"
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read(_BINDING_CONTENT_SCAN_BYTES).lower()
    except OSError:
        content = ""
    for token in lowered:
        if _token_matches(token, content):
            return True, f"content contains {token!r}"
    hint = ""
    if any(_BARE_NUMERIC_TOKEN.match(token) for token in lowered):
        hint = (
            " (a bare number must be CITED in the content — e.g. '#27', "
            "'issue 27' — or appear in the basename; a bare digit run inside a "
            "date, time or version does not bind)"
        )
    return False, (
        f"none of the binding tokens {sorted(set(lowered))} appear in the "
        f"evidence basename or content{hint}; the file does not bind to this "
        "closeout"
    )


def parse_evidence_arg(raw: str) -> tuple[str, str]:
    """Parse a ``name:path`` pair. Raises ``ValueError`` on malformed input."""
    if ":" not in raw:
        raise ValueError(f"--evidence value {raw!r} must be NAME:PATH")
    name, _, path = raw.partition(":")
    name = name.strip()
    path = path.strip()
    if not name or not path:
        raise ValueError(f"--evidence value {raw!r} must be NAME:PATH (both non-empty)")
    return name, path


def parse_skip_arg(raw: str) -> tuple[str, str]:
    """Parse a ``name:reason`` pair. Raises ``ValueError`` on malformed input."""
    if ":" not in raw:
        raise ValueError(f"--skip value {raw!r} must be NAME:REASON")
    name, _, reason = raw.partition(":")
    name = name.strip()
    reason = reason.strip()
    if not name or not reason:
        raise ValueError(f"--skip value {raw!r} must be NAME:REASON (both non-empty)")
    return name, reason


def _validate_skip_reason(reason: str) -> tuple[bool, str | None]:
    head, _, detail = reason.partition(":")
    head = head.strip()
    if head not in ALLOWED_SKIP_REASONS:
        return False, (
            f"skip reason must start with one of "
            f"{sorted(ALLOWED_SKIP_REASONS)} followed by ':' and a detail"
        )
    # A repeated head is the same manufactured-constant hole one level down: a
    # caller that prepends ``host-blocked-subagent: `` to an author shorthand
    # that itself begins with an enum head would otherwise let the duplicated
    # head fund the detail floor.
    stripped = detail.strip()
    while True:
        next_head, sep, rest = stripped.partition(":")
        if sep and next_head.strip() in ALLOWED_SKIP_REASONS:
            stripped = rest.strip()
            continue
        break
    if len(reason) < MIN_SKIP_LENGTH:
        return False, (
            f"skip reason too short ({len(reason)} chars; min {MIN_SKIP_LENGTH}); "
            "append the concrete host signal or evaluator condition"
        )
    if len(stripped) < MIN_SKIP_DETAIL_LENGTH:
        return False, (
            f"skip detail too short ({len(stripped)} chars after the "
            f"{head!r} head; min {MIN_SKIP_DETAIL_LENGTH}); the enum head does not "
            "count toward the floor — append the concrete host signal or "
            "evaluator condition"
        )
    return True, None


def check(
    *,
    repo_root: Path,
    required: list[str],
    evidence: dict[str, str],
    skips: dict[str, str],
    kind: str | None = None,
) -> dict[str, Any]:
    """Validate that every required evidence name has either a real file or a
    valid skip reason. Returns a structured report.

    ``evidence`` paths resolve relative to ``repo_root`` when not absolute.
    """
    repo_root = repo_root.resolve()
    satisfied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid_skips: list[dict[str, Any]] = []
    missing_evidence_files: list[dict[str, Any]] = []

    for name in required:
        if name in evidence:
            raw_path = evidence[name]
            resolved = Path(raw_path)
            if not resolved.is_absolute():
                resolved = (repo_root / raw_path).resolve()
            else:
                resolved = resolved.resolve()
            if not resolved.is_file() or resolved.stat().st_size == 0:
                missing_evidence_files.append({"name": name, "path": str(resolved)})
                continue
            satisfied.append({"name": name, "via": "evidence", "path": str(resolved)})
            continue
        if name in skips:
            reason = skips[name]
            ok, detail = _validate_skip_reason(reason)
            if not ok:
                invalid_skips.append({"name": name, "reason": reason, "detail": detail})
                continue
            skipped.append({"name": name, "reason": reason})
            continue
        missing.append(name)

    ok = not (missing or invalid_skips or missing_evidence_files)
    return {
        "ok": ok,
        "kind": kind,
        "required": list(required),
        "satisfied": satisfied,
        "skipped": skipped,
        "missing": missing,
        "invalid_skips": invalid_skips,
        "missing_evidence_files": missing_evidence_files,
    }
