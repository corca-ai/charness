"""The `du`-backed scan of the pytest temp tree, and how it decides it failed.

Split out of `standing_test_economics_lib` because telling a lost race apart from
a broken tool is a whole concern with its own retry policy, timeout budget, and
failure taxonomy -- and because a gate that grades a push on this must never read
"I measured nothing" as "nothing is wrong".
"""

from __future__ import annotations

import getpass
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

# Recognize both pytest's own numbered session dirs (`pytest-<n>`) and the standing
# runner's explicit basetemp (`charness-run-<time_ns>`, deliberately not named
# `pytest-*` so pytest's numbered-dir cleanup cannot delete it mid-run — see
# scripts/run_standing_pytest.py default_basetemp). Both hold the same
# `popen-gw*`/seed footprint the drill-down inventory reports.
PYTEST_SESSION_RE = re.compile(r"^(?:pytest|charness-run)-\d+$")
PYTEST_WORKER_RE = re.compile(r"^popen-gw\d+$")
PYTEST_SEED_PREFIXES = ("charness-repo-seed", "charness-git-repo-seed", "managed-home-seed")

# A `du` walk that dies early on a race clears on a retry; one that is broken dies
# every time. Three attempts tells those apart. The TOTAL timeout is what the
# caller's runtime budget sees, so it is capped across attempts rather than per
# attempt -- three 30s attempts would otherwise triple the gate's worst case.
PYTEST_TEMP_SCAN_ATTEMPTS = 3
PYTEST_TEMP_SCAN_RETRY_SECONDS = 0.25
PYTEST_TEMP_SCAN_ATTEMPT_TIMEOUT_SECONDS = 30.0
PYTEST_TEMP_SCAN_TOTAL_TIMEOUT_SECONDS = 30.0

#: Reasons a retry cannot clear and that mean the box cannot run this measurement
#: at all, rather than that the measurement failed. Consumers keep these advisory.
DU_CAPABILITY_GAP_REASONS = frozenset({"du_missing", "du_not_executable", "du_unsupported_options"})
# Measured, not inferred. BusyBox v1.30.1 `du -d 4 -B1` emits, on stderr, exit 1:
#     du: invalid option -- 'B'
#     Usage: du [-aHLdclsxhmk] [FILE]...
# GNU coreutils `du` emits `du: invalid option -- 'Q'` for a bad short option and
# `du: unrecognized option '--bogus'` for a bad long one. `illegal option` covers
# the BSD/macOS getopt wording, which remains the one unprobed entry here.
DU_USAGE_ERROR_TOKENS = ("unrecognized option", "invalid option", "illegal option", "unknown option", "usage:")

#: Whether anything pointed the scan at a specific root. Without
#: `PYTEST_DEBUG_TEMPROOT` the scan falls back to the shared system temp dir, where
#: any other project's pytest tree lands. Note this distinguishes "someone chose a
#: root" from "nobody did" -- it does NOT verify the chosen root is repo-owned, so
#: `PYTEST_DEBUG_TEMPROOT=/tmp` reads as configured and its failures block. That
#: errs closed, which is the safe direction, but do not read `configured` as proof
#: the tree belongs to this repo.
TEMP_ROOT_SOURCE_CONFIGURED = "configured"
TEMP_ROOT_SOURCE_SHARED_FALLBACK = "shared_fallback"


def pytest_temp_root_source() -> str:
    return (
        TEMP_ROOT_SOURCE_CONFIGURED
        if os.environ.get("PYTEST_DEBUG_TEMPROOT")
        else TEMP_ROOT_SOURCE_SHARED_FALLBACK
    )


def pytest_temp_root() -> Path:
    base = Path(os.environ.get("PYTEST_DEBUG_TEMPROOT") or tempfile.gettempdir())
    user = getpass.getuser() if hasattr(getpass, "getuser") else "unknown"
    return base / f"pytest-of-{user}"


def _du_usage_error(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(token in lowered for token in DU_USAGE_ERROR_TOKENS)


def du_scan_once(root: Path, timeout: float) -> tuple[subprocess.CompletedProcess[str] | None, str]:
    """Run the quick `du` walk once, naming which way it failed.

    `check=True` is deliberately NOT used. `du` exits nonzero merely because some
    entry vanished mid-walk, yet it keeps walking and still prints the totals for
    everything it did see -- so a nonzero exit is not by itself a failed
    measurement. The caller decides that from the output, not from the status.
    """
    try:
        result = subprocess.run(
            ["du", "-d", "4", "-B1", str(root)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return None, "du_missing"
    except PermissionError:
        return None, "du_not_executable"
    except subprocess.TimeoutExpired:
        return None, "du_timeout"
    except OSError:
        return None, "du_oserror"
    except subprocess.SubprocessError:
        return None, "du_subprocess_error"
    if result.returncode == 0:
        return result, ""
    if _du_usage_error(result.stderr):
        # BusyBox and some BSD `du` builds reject `-B`. That is this box lacking a
        # capability, not a measurement that broke, and it is identical on a retry.
        return None, "du_unsupported_options"
    return result, "du_exit_nonzero"


def du_reported_root_total(stdout: str, root: Path) -> bool:
    """True when `du` printed the scanned root's own total line.

    That line is the last thing `du` emits, so its presence means the walk reached
    the end and the totals are usable even if some entry vanished on the way. Its
    absence means `du` died early and there is nothing to grade.
    """
    for line in stdout.splitlines():
        size_str, _, raw_path = line.partition("\t")
        if not raw_path:
            continue
        try:
            int(size_str)
        except ValueError:
            continue
        if Path(raw_path) == root:
            return True
    return False


def _scan_with_retry(
    root: Path, attempts: int, total_timeout: float
) -> tuple[subprocess.CompletedProcess[str] | None, str, int]:
    """Scan until a usable walk lands, the attempts run out, or the clock does."""
    budget = max(1, attempts)
    deadline = time.monotonic() + total_timeout
    attempt = 0
    reason = ""
    while attempt < budget:
        attempt += 1
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None, reason or "du_timeout", attempt
        result, reason = du_scan_once(root, min(PYTEST_TEMP_SCAN_ATTEMPT_TIMEOUT_SECONDS, remaining))
        if result is not None and du_reported_root_total(result.stdout, root):
            # `du` printed the root's own total, so it finished its accounting. A
            # nonzero exit here only means some entry vanished under it; the
            # numbers it did print are the ones the caller grades.
            return result, reason, attempt
        if reason in DU_CAPABILITY_GAP_REASONS:
            return None, reason, attempt
        if attempt < budget:
            # Let the losing race finish before looking again. Only the failure
            # path pays this, and only on a run that would otherwise prove nothing.
            time.sleep(PYTEST_TEMP_SCAN_RETRY_SECONDS)
    return None, reason, attempt


def _parse_du_footprint(stdout: str, root: Path) -> dict[str, Any]:
    seed_totals: dict[str, dict[str, int]] = {
        prefix: {"count": 0, "disk_bytes": 0} for prefix in PYTEST_SEED_PREFIXES
    }
    total_disk_bytes = 0
    session_names: set[str] = set()
    matched_paths: list[Path] = []
    for line in stdout.splitlines():
        try:
            size_str, raw_path = line.split("\t", 1)
            size = int(size_str)
        except ValueError:
            continue
        path = Path(raw_path)
        if path == root:
            total_disk_bytes = size
            continue
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if rel_parts and PYTEST_SESSION_RE.match(rel_parts[0]):
            session_names.add(rel_parts[0])
        if any(parent in matched_paths for parent in path.parents):
            continue
        for prefix in PYTEST_SEED_PREFIXES:
            if path.name.startswith(prefix):
                seed_totals[prefix]["count"] += 1
                seed_totals[prefix]["disk_bytes"] += size
                matched_paths.append(path)
                break
    return {
        "session_count": len(session_names),
        "total_disk_bytes": total_disk_bytes,
        "seed_totals": seed_totals,
    }


def pytest_temp_footprint_quick(
    attempts: int = PYTEST_TEMP_SCAN_ATTEMPTS,
    total_timeout: float = PYTEST_TEMP_SCAN_TOTAL_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    root = pytest_temp_root()
    root_source = pytest_temp_root_source()
    if not root.exists():
        return {"status": "missing", "root": str(root), "root_source": root_source}
    result, reason, attempt = _scan_with_retry(root, attempts, total_timeout)
    if result is None:
        return {
            "status": "unavailable",
            "root": str(root),
            "root_source": root_source,
            "reason": reason,
            "attempts": attempt,
            "capability_gap": reason in DU_CAPABILITY_GAP_REASONS,
        }
    return {
        "status": "available",
        "root": str(root),
        "root_source": root_source,
        **_parse_du_footprint(result.stdout, root),
        # Kept on the SUCCESS path too: a scan that failed once and succeeded on
        # the retry is the exact flaky state the retry exists to absorb, and
        # reporting it only on failure would erase the evidence that it happened.
        "attempts": attempt,
        "partial": reason == "du_exit_nonzero",
    }
