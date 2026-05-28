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
