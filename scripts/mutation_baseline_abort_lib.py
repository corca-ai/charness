"""Shared helpers for the mutation coverage-baseline abort marker.

When `scripts/sample_mutation_files.py`'s coverage-baseline pytest run fails,
no mutation manifest is written and the failing nodeids only ever reached the
CI step log. `check_mutation_score.py` then reported nothing but the
collateral "stats missing" symptom, and `check_js_mutation_score.py` appended
an unrelated "StrykerJS JSON report missing" slice on top of it. This marker
records the real blocking signal (the baseline pytest failure, with parsed
nodeids when available) so both downstream summary scripts can name it
instead of the collateral symptom.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_BASELINE_ABORT_MARKER = Path("reports/mutation/baseline-abort.json")
_MARKER_KIND = "coverage-baseline-pytest-failed"
_FAILED_SHORT_SUMMARY_RE = re.compile(r"^FAILED (\S+)(?: - .*)?$", re.MULTILINE)
_FAILED_VERBOSE_RE = re.compile(r"^(\S+::\S+) FAILED\b", re.MULTILINE)
_ERROR_COLLECTION_RE = re.compile(r"^ERROR (\S+)(?: - .*)?$", re.MULTILINE)


def parse_failed_nodeids(text: str) -> list[str]:
    """Extract pytest failing nodeids from combined stdout/stderr.

    Matches the short-summary form (``FAILED <nodeid>``, optionally followed
    by `` - <reason>``), the verbose per-test form (``<nodeid> FAILED``), and
    pytest collection-error lines (``ERROR <nodeid-or-path>``, optionally
    followed by `` - <reason>``), deduping while preserving first-seen order.
    """
    matches = [
        (match.start(), match.group(1))
        for pattern in (_FAILED_SHORT_SUMMARY_RE, _FAILED_VERBOSE_RE, _ERROR_COLLECTION_RE)
        for match in pattern.finditer(text)
    ]
    matches.sort(key=lambda item: item[0])
    nodeids: list[str] = []
    seen: set[str] = set()
    for _position, nodeid in matches:
        if nodeid not in seen:
            seen.add(nodeid)
            nodeids.append(nodeid)
    return nodeids


def resolve_baseline_abort_marker(repo_root: Path, marker_path: Path) -> Path:
    return marker_path if marker_path.is_absolute() else repo_root / marker_path


def delete_stale_baseline_abort_marker(marker_path: Path) -> None:
    # missing_ok (no exists() pre-check): a concurrent run may remove the
    # marker between any check and this unlink; absence is the desired state.
    marker_path.unlink(missing_ok=True)


def write_baseline_abort_marker(
    marker_path: Path,
    *,
    exit_code: int,
    test_command: str,
    failing_nodeids: list[str],
    log_tail: list[str],
) -> None:
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "kind": _MARKER_KIND,
        "exit_code": exit_code,
        "test_command": test_command,
        "failing_nodeids": failing_nodeids,
        "log_tail": log_tail,
    }
    marker_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_baseline_abort_marker(marker_path: Path) -> dict | None:
    """Return the marker payload, or None when absent, unreadable, or malformed.

    Callers use ``None`` as the "no abort recorded" signal, so any read/parse
    failure must fall back to that instead of raising.
    """
    if not marker_path.is_file():
        return None
    try:
        data = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("kind") != _MARKER_KIND:
        return None
    return data


def log_tail_lines(text: str, limit: int = 30) -> list[str]:
    return text.splitlines()[-limit:]
