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
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

try:
    from scripts.core import subprocess_guard as _subprocess_guard
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    import scripts.core.subprocess_guard as _subprocess_guard

_guard_run_process = _subprocess_guard.run_process
subprocess = _subprocess_guard.subprocess


def run_process(*args, **kwargs):
    """Keep the old module-local injection seam while delegating to the guard."""
    if subprocess is _subprocess_guard.subprocess:
        return _guard_run_process(*args, **kwargs)
    original = _subprocess_guard.subprocess
    _subprocess_guard.subprocess = subprocess
    try:
        return _guard_run_process(*args, **kwargs)
    finally:
        _subprocess_guard.subprocess = original


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
# Diagnostic only, and deliberately so. BusyBox v1.30.1 `du -d 4 -B1` emits, on
# stderr, exit 1:
#     du: invalid option -- 'B'
#     Usage: du [-aHLdclsxhmk] [FILE]...
# GNU coreutils emits `du: invalid option -- 'Q'` for a bad short option and
# `du: unrecognized option '--bogus'` for a bad long one. `illegal option` is the
# BSD/macOS getopt wording and is the one entry no run here has ever observed.
#
# Nothing BRANCHES on this list any more: `_scan_with_retry` falls through to the
# next `DU_SCAN_VARIANTS` entry whenever a walk produced no root total, whatever
# stderr said. A wording this list gets wrong therefore costs a less precise
# `reason` string, not a lost measurement -- which is the only honest place to
# leave an inference that cannot be probed from the hosts available.
DU_USAGE_ERROR_TOKENS = (
    "unrecognized option",
    "invalid option",
    "illegal option",
    "unknown option",
    "usage:",
)

#: Ordered `du` invocations to try, with the multiplier that turns their sizes into
#: bytes. `-B1` reports exact bytes and is GNU-only; `-k` is in POSIX, BusyBox
#: (`[-aHLdclsxhmk]`), and BSD/macOS, at the cost of 1KiB granularity. A host whose
#: `du` rejects `-B1` therefore gets a coarser real measurement instead of an
#: advisory capability gap.
DU_SCAN_VARIANTS: tuple[tuple[str, tuple[str, ...], int], ...] = (
    ("bytes", ("-B1",), 1),
    ("kib", ("-k",), 1024),
)
#: Failures where a different option set could plausibly be the difference, so the
#: next variant is worth one spawn. Everything else -- an absent or unrunnable `du`,
#: a timeout, an OS error -- means the binary never produced output, and no option
#: set changes that; those keep the original across-attempts retry instead.
#:
#: `du_exit_nonzero` is in here on purpose: it is the reason an unfamiliar `du`
#: reports a rejected `-B1` in wording `DU_USAGE_ERROR_TOKENS` does not know, which
#: is the whole point of not branching on that wording.
DU_VARIANT_RETRY_REASONS = frozenset({"du_unsupported_options", "du_exit_nonzero"})

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


def du_bytes_many(paths: list[Path], *args: str) -> dict[Path, int]:
    """Read one ``du`` metric for a stable path set in a single process."""
    if not paths:
        return {}
    try:
        result = run_process(
            ["du", *args, *(str(path) for path in paths)],
            cwd=Path.cwd(),
            timeout_seconds=10,
        )
        if result.returncode == 124 and result.stderr.startswith("timed out after "):
            return {}
    except OSError:
        return {}
    values: dict[Path, int] = {}
    for line in result.stdout.splitlines():
        size_text, separator, raw_path = line.partition("\t")
        if not separator:
            size_text, _, raw_path = line.partition(" ")
        try:
            values[Path(raw_path)] = int(size_text)
        except (ValueError, TypeError):
            continue
    return values


def _du_usage_error(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(token in lowered for token in DU_USAGE_ERROR_TOKENS)


def du_scan_once(
    root: Path,
    timeout: float,
    options: tuple[str, ...] = DU_SCAN_VARIANTS[0][1],
) -> tuple[subprocess.CompletedProcess[str] | None, str]:
    """Run the quick `du` walk once, naming which way it failed.

    `check=True` is deliberately NOT used. `du` exits nonzero merely because some
    entry vanished mid-walk, yet it keeps walking and still prints the totals for
    everything it did see -- so a nonzero exit is not by itself a failed
    measurement. The caller decides that from the output, not from the status.

    ``options`` carries the size-unit flags of one `DU_SCAN_VARIANTS` entry; it
    defaults to the GNU byte-exact form so existing callers are unchanged.
    """
    try:
        result = run_process(
            ["du", "-d", "4", *options, str(root)],
            cwd=root,
            timeout_seconds=timeout,
        )
    except FileNotFoundError:
        return None, "du_missing"
    except PermissionError:
        return None, "du_not_executable"
    except subprocess.SubprocessError:
        return None, "du_subprocess_error"
    except OSError:
        return None, "du_oserror"
    if result.returncode == 124 and result.stderr.startswith("timed out after "):
        return None, "du_timeout"
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
) -> tuple[subprocess.CompletedProcess[str] | None, str, int, int]:
    """Scan until a usable walk lands, the attempts run out, or the clock does.

    Each attempt walks `DU_SCAN_VARIANTS` in order and stops at the first variant
    that prints the root's own total. Falling through on ANY unusable walk -- not
    only on one whose stderr matched a known usage wording -- is what keeps
    `DU_USAGE_ERROR_TOKENS` out of the control flow: an unfamiliar `du` that
    rejects `-B1` in words nobody here has seen still gets measured by `-k`.

    Returns the bytes multiplier of the variant that succeeded alongside the walk.
    """
    budget = max(1, attempts)
    deadline = time.monotonic() + total_timeout
    attempt = 0
    reason = ""
    while attempt < budget:
        attempt += 1
        for _label, options, multiplier in DU_SCAN_VARIANTS:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None, reason or "du_timeout", attempt, 1
            result, reason = du_scan_once(
                root, min(PYTEST_TEMP_SCAN_ATTEMPT_TIMEOUT_SECONDS, remaining), options
            )
            if result is not None and du_reported_root_total(result.stdout, root):
                # `du` printed the root's own total, so it finished its accounting. A
                # nonzero exit here only means some entry vanished under it; the
                # numbers it did print are the ones the caller grades.
                return result, reason, attempt, multiplier
            if reason not in DU_VARIANT_RETRY_REASONS:
                break
        if reason in DU_CAPABILITY_GAP_REASONS:
            # Every variant hit a usage error, so this box cannot run the walk at all
            # and a retry would report the same thing.
            return None, reason, attempt, 1
        if attempt < budget:
            # Let the losing race finish before looking again. Only the failure
            # path pays this, and only on a run that would otherwise prove nothing.
            time.sleep(PYTEST_TEMP_SCAN_RETRY_SECONDS)
    return None, reason, attempt, 1


def _parse_du_footprint(stdout: str, root: Path, multiplier: int = 1) -> dict[str, Any]:
    seed_totals: dict[str, dict[str, int]] = {
        prefix: {"count": 0, "disk_bytes": 0} for prefix in PYTEST_SEED_PREFIXES
    }
    total_disk_bytes = 0
    session_names: set[str] = set()
    matched_paths: list[Path] = []
    for line in stdout.splitlines():
        try:
            size_str, raw_path = line.split("\t", 1)
            size = int(size_str) * multiplier
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
    result, reason, attempt, multiplier = _scan_with_retry(root, attempts, total_timeout)
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
        **_parse_du_footprint(result.stdout, root, multiplier),
        # 1 when `du -B1` reported exact bytes, 1024 when the portable `-k` fallback
        # measured in KiB blocks. Reported so a consumer can tell a byte-exact total
        # from a rounded-up one instead of assuming precision the walk did not have.
        "size_granularity_bytes": multiplier,
        # Kept on the SUCCESS path too: a scan that failed once and succeeded on
        # the retry is the exact flaky state the retry exists to absorb, and
        # reporting it only on failure would erase the evidence that it happened.
        "attempts": attempt,
        "partial": reason == "du_exit_nonzero",
    }
