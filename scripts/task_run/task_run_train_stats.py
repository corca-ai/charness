"""Merge-train throughput stats for `charness train` (#870).

Per-lane metrics answer "how did this lane do"; the train answers "is the
merge train keeping up". `record_landing_for_repo` appends one row per
fast-forward (time, base, landed SHA, branches) to the shared task-run
runtime root; `train_stats_for_repo` derives, over a trailing window:

- landings per hour on the branch the train lands;
- median wait from a lane's terminal result to its landing (integration
  queue). A lane result with no matching landing is reported as waiting,
  not dropped;
- lane waste rate: results that ended failed, premise-blocked, stopped,
  or with no status, over lanes launched.

Lane-done time is the result record's file mtime: the record is persisted
when the lane reaches its terminal state, so mtime is the terminal time
without a second clock.
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

TERMINAL_PHASE = "terminal"
WASTE_STATUSES = frozenset({"failed", "premise-blocked", "stopped"})

LANDINGS_RELATIVE = Path("train") / "landings.jsonl"
LANDING_SCHEMA = "charness.train_landing.v1"


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run.task_run_runtime import (  # noqa: E402
    task_runtime_root,
    utc_now_iso,
)


def parse_window(text: str) -> float:
    """Parse a trailing window to hours: `30m`, `3h`, `1d`, or bare hours."""
    raw = text.strip().lower()
    if not raw:
        raise ValueError("window must not be empty")
    multipliers = {"m": 1 / 60, "h": 1.0, "d": 24.0}
    if raw[-1] in multipliers:
        number, multiplier = raw[:-1], multipliers[raw[-1]]
    else:
        number, multiplier = raw, 1.0
    try:
        hours = float(number) * multiplier
    except ValueError:
        raise ValueError(f"invalid window {text!r}: expected like 30m, 3h, 1d") from None
    if hours <= 0:
        raise ValueError(f"invalid window {text!r}: must be positive")
    return hours


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp


def landing_path(runtime_path: Path) -> Path:
    return runtime_path / LANDINGS_RELATIVE


def _branch_key(value: object) -> str:
    """Compare lane and landing branches by short name either way."""
    text = value if isinstance(value, str) else ""
    return text.removeprefix("refs/heads/")


def record_landing_for_repo(
    repo_root: Path,
    *,
    base_sha: str,
    landed_sha: str,
    branches: Sequence[str],
    run_id: str,
    occurred_at: str | None = None,
) -> dict[str, Any] | None:
    """Append one landing row; fail open so a record miss never fails a land."""
    try:
        runtime_path = task_runtime_root(repo_root)
        path = landing_path(runtime_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "schema_version": LANDING_SCHEMA,
            "occurred_at": occurred_at or utc_now_iso(),
            "base_sha": base_sha,
            "landed_sha": landed_sha,
            "branches": list(branches),
            "run_id": run_id,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        return record
    except OSError:
        return None


def read_landings(runtime_path: Path) -> list[dict[str, Any]]:
    """Read landing rows, skipping malformed lines (stats fail open)."""
    path = landing_path(runtime_path)
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except ValueError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def iter_lane_results(runtime_path: Path) -> list[tuple[float, dict[str, Any]]]:
    """(result mtime, payload) for every persisted lane result, mtime order."""
    root = runtime_path / "task-run"
    found: list[tuple[float, dict[str, Any]]] = []
    if not root.is_dir():
        return found
    for path in sorted(root.glob("*/result.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        found.append((mtime, payload))
    found.sort(key=lambda item: item[0])
    return found


def evaluate_loosening(stats: Mapping[str, Any], thresholds: Mapping[str, Any]) -> dict[str, Any]:
    """Check the adapter-declared loosening threshold against train stats."""
    reasons: list[str] = []
    lands = int(stats.get("lands_in_window", 0))
    rate = float(stats.get("landings_per_hour", 0.0))
    wait = stats.get("median_queue_wait_minutes")
    wasted = int(stats.get("wasted", 0))
    min_lands = thresholds.get("min_lands", 0)
    if lands < int(min_lands):
        reasons.append(f"only {lands} lands in window, need {min_lands}")
    min_rate = float(thresholds.get("min_landings_per_hour", 0.0))
    if rate < min_rate:
        reasons.append(f"landings {rate:.2f}/h below {min_rate:.2f}/h")
    max_wait = thresholds.get("max_queue_wait_minutes")
    if max_wait is not None:
        if wait is None:
            reasons.append("no landed lane to measure queue wait")
        elif float(wait) > float(max_wait):
            reasons.append(f"median queue wait {float(wait):.1f}m above {max_wait}m")
    if thresholds.get("require_no_waste", False) and wasted:
        reasons.append(f"{wasted} wasted lanes in window")
    return {"ok": not reasons, "reasons": reasons}


def train_stats_for_repo(
    repo_root: Path,
    *,
    window_hours: float,
    loosening: Mapping[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Derive train throughput over the trailing window for one repository."""
    if window_hours <= 0:
        raise ValueError("window_hours must be positive")
    moment = now or datetime.now(timezone.utc)
    cutoff = moment - timedelta(hours=window_hours)
    runtime_path = task_runtime_root(repo_root.resolve())
    landings = [
        record
        for record in read_landings(runtime_path)
        if (_parse_time(record.get("occurred_at")) or moment) >= cutoff
    ]
    landings.sort(key=lambda record: _parse_time(record.get("occurred_at")) or moment)
    waits: list[float] = []
    waiting: list[str] = []
    launched = 0
    wasted = 0
    for done_epoch, result in iter_lane_results(runtime_path):
        launched += 1
        status = result.get("status")
        if not status or status in WASTE_STATUSES:
            wasted += 1
        branch = result.get("branch")
        task_id = result.get("task_id")
        if not branch or not task_id:
            continue
        done = datetime.fromtimestamp(done_epoch, tz=timezone.utc)
        if done < cutoff:
            continue
        joins = [
            (_parse_time(record.get("occurred_at")) or moment) - done
            for record in landings
            if _branch_key(branch) in {_branch_key(entry) for entry in record.get("branches") or []}
            and (_parse_time(record.get("occurred_at")) or moment) >= done
        ]
        if not joins:
            waiting.append(str(task_id))
            continue
        waits.append(min(joins).total_seconds() / 60)
    stats: dict[str, Any] = {
        "window_hours": window_hours,
        "lands_in_window": len(landings),
        "landings_per_hour": len(landings) / window_hours,
        "median_queue_wait_minutes": statistics.median(waits) if waits else None,
        "lanes_joined": len(waits),
        "lanes_waiting": waiting,
        "launched": launched,
        "wasted": wasted,
        "waste_rate": (wasted / launched) if launched else 0.0,
    }
    stats["loosening"] = evaluate_loosening(stats, loosening) if loosening is not None else None
    return stats
