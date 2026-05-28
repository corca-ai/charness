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


def _token_matches(token: str, haystack: str) -> bool:
    """True when ``token`` (already lowercased) occurs in ``haystack``.

    Numeric-cluster tokens require non-alphanumeric neighbours so a short
    issue number cannot bind on a coincidental digit run; other tokens use
    plain containment.
    """
    if _NUMERIC_CLUSTER_TOKEN.match(token):
        return (
            re.search(
                rf"(?<![0-9a-z]){re.escape(token)}(?![0-9a-z])", haystack
            )
            is not None
        )
    return token in haystack


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
        if _token_matches(token, name):
            return True, f"basename contains {token!r}"
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read(_BINDING_CONTENT_SCAN_BYTES).lower()
    except OSError:
        content = ""
    for token in lowered:
        if _token_matches(token, content):
            return True, f"content contains {token!r}"
    return False, (
        f"none of the binding tokens {sorted(set(lowered))} appear in the "
        "evidence basename or content; the file does not bind to this closeout"
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
    head, _, _ = reason.partition(":")
    head = head.strip()
    if head not in ALLOWED_SKIP_REASONS:
        return False, (
            f"skip reason must start with one of "
            f"{sorted(ALLOWED_SKIP_REASONS)} followed by ':' and a detail"
        )
    if len(reason) < MIN_SKIP_LENGTH:
        return False, (
            f"skip reason too short ({len(reason)} chars; min {MIN_SKIP_LENGTH}); "
            "append the concrete host signal or evaluator condition"
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
