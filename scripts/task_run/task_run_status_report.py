"""Fixed-shape periodic status report for orchestration periods (#872).

Renders the operator-kept 30-minute shape from the three sources the lanes
already record, without changing what lanes record:

- lane metrics: task-run results plus `train_stats_for_repo` (870),
- the friction log (`task_run_friction`),
- the decision ledger (`task_run_ledger`).

Every section carries measured numbers; the report ends the improvements
section with the fixed `improvements found:` line the per-lane retro already
requires (`docs/agent-task-runs.md`), extended to the period.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import (  # noqa: E402
    task_run_events,
    task_run_friction,
    task_run_ledger,
    task_run_runtime,
    task_run_train_stats,
)

BLOCKING_FRICTION_KINDS = frozenset({"block", "premise-failure", "conflict-resolution"})

OPERATOR_RESOLUTION = "operator-needed"

_MEASURED_BY = "measured by next-period train stats (landings/h, median queue wait, waste rate)"


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


def _window_events(
    path: Path, source: str, *, cutoff: datetime, moment: datetime
) -> tuple[list[dict[str, Any]], int]:
    """Validated window events from a jsonl store; malformed lines fail open."""
    if not path.is_file():
        return [], 0
    events: list[dict[str, Any]] = []
    skipped = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = task_run_events.validate_event(json.loads(line))
        except (ValueError, task_run_events.EventSchemaError):
            skipped += 1
            continue
        if event["source"] != source:
            skipped += 1
            continue
        stamp = _parse_time(event.get("occurred_at")) or moment
        if stamp >= cutoff:
            events.append(event)
    return events, skipped


def _fact_text(facts: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = facts.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    return ""


def _event_summary(event: Mapping[str, Any]) -> str:
    facts = event.get("facts")
    facts = facts if isinstance(facts, Mapping) else {}
    return _fact_text(facts, "decision", "topic", "blocker", "error", "next_step", "resolution")


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[str(item.get(key))] = counts.get(str(item.get(key)), 0) + 1
    return counts


def _fmt(value: float | None, unit: str) -> str:
    return "n/a" if value is None else f"{value:.1f}{unit}"


def render_period_status(
    *,
    runtime_path: Path,
    repo_root: Path,
    window_hours: float = 0.5,
    now: datetime | None = None,
) -> str:
    """Render the fixed-shape period report as Markdown.

    `runtime_path` is the external task runtime root (task results, landing
    records, friction log); `repo_root` locates the decision ledger. All
    counts are measured from those stores; nothing is prose-claimed.
    """
    if window_hours <= 0:
        raise ValueError("window_hours must be positive")
    moment = now or datetime.now(timezone.utc)
    cutoff = moment - timedelta(hours=window_hours)

    tasks = task_run_runtime.read_task_results(runtime_path)
    current = task_run_train_stats.train_stats_for_repo(
        repo_root, window_hours=window_hours, now=moment
    )
    # The train-stats API only derives trailing windows, so the disjoint
    # previous period comes from exact subtraction: landings in the trailing
    # double window minus landings in the current one.
    double = task_run_train_stats.train_stats_for_repo(
        repo_root, window_hours=2 * window_hours, now=moment
    )
    previous_lands = max(
        0, int(double.get("lands_in_window", 0)) - int(current.get("lands_in_window", 0))
    )
    friction, friction_skipped = _window_events(
        task_run_friction.friction_log_path(runtime_path),
        "friction-log",
        cutoff=cutoff,
        moment=moment,
    )
    decisions, ledger_skipped = _window_events(
        task_run_ledger.decision_ledger_path(repo_root),
        "decision-ledger",
        cutoff=cutoff,
        moment=moment,
    )

    lines = [
        f"# Period status: last {window_hours:g}h (as of {moment.isoformat()})",
        "",
        "## Goals",
        "",
        _goals_section(tasks),
        "",
        "## Lane states",
        "",
        *_lane_rows(tasks),
        "",
        "## Friction",
        "",
        _friction_section(friction, friction_skipped),
        "",
        "## Improvements",
        "",
        _improvements_section(current, previous_lands, window_hours, decisions),
        "",
        "## Decisions",
        "",
        _decisions_section(decisions, ledger_skipped, friction),
        "",
        "## Next actions",
        "",
        *_next_actions_section(tasks, friction, current),
        "",
    ]
    return "\n".join(lines)


def _goals_section(tasks: list[dict[str, Any]]) -> str:
    counts = _count_by(tasks, "status")
    breakdown = (
        ", ".join(f"{total} {status}" for status, total in sorted(counts.items()))
        or "no lanes recorded"
    )
    return f"{len(tasks)} goal(s): {breakdown}."


def _lane_rows(tasks: list[dict[str, Any]]) -> list[str]:
    rows = ["| task | status | branch | note |", "| --- | --- | --- | --- |"]
    for task in tasks:
        note = _fact_text(task, "blocker", "result_kind", "next_step")
        rows.append(
            f"| {task.get('task_id')} | {task.get('status')} "
            f"| {task.get('branch') or '-'} | {note or '-'} |"
        )
    if not tasks:
        rows.append("| - | none | - | no lanes recorded |")
    return rows


def _friction_section(events: list[dict[str, Any]], skipped: int) -> str:
    counts = _count_by(events, "event_kind")
    kinds = ", ".join(f"{total} {kind}" for kind, total in sorted(counts.items())) or "none"
    repeated = [event for event in events if event.get("facts", {}).get("escalation")]
    blocking = [event for event in events if event.get("event_kind") in BLOCKING_FRICTION_KINDS]
    head = (
        f"{len(events)} friction event(s): {kinds}; "
        f"{len(repeated)} repeated, {len(blocking)} blocking."
    )
    if skipped:
        head += f" {skipped} unreadable line(s) skipped."
    rows = ["| kind | task | detail | repair-or-next |", "| --- | --- | --- | --- |"]
    for event in events:
        facts = event.get("facts")
        facts = facts if isinstance(facts, Mapping) else {}
        detail = _fact_text(facts, "blocker", "error", "escalation") or _event_summary(event)
        repair = _fact_text(facts, "next_step", "resolution") or "repair: pending"
        rows.append(
            f"| {event.get('event_kind')} | {facts.get('task_id', '-')} "
            f"| {detail or '-'} | {repair} |"
        )
    if not events:
        rows.append("| - | - | no friction recorded | - |")
    return "\n".join([head, "", *rows])


def _improvements_section(
    current: Mapping[str, Any],
    previous_lands: int,
    window_hours: float,
    decisions: list[dict[str, Any]],
) -> str:
    lands = int(current.get("lands_in_window", 0))
    rate = float(current.get("landings_per_hour", 0.0))
    previous_rate = previous_lands / window_hours
    wait = _fmt(current.get("median_queue_wait_minutes"), "m")
    launched = int(current.get("launched", 0))
    wasted = int(current.get("wasted", 0))
    waste = f"{wasted}/{launched} ({wasted / launched:.0%})" if launched else "0/0 (n/a)"
    adopted = [_event_summary(event) for event in decisions]
    adopted = [item for item in adopted if item]
    found = "; ".join(adopted) if adopted else "none"
    proactive = (
        "; ".join(
            f"{event.get('event_kind')}: {_event_summary(event) or 'no summary'}"
            for event in decisions
        )
        or "none"
    )
    return "\n".join(
        [
            f"train: {lands} landings in window "
            f"({rate:.2f}/h; previous window {previous_lands} landings, "
            f"{previous_rate:.2f}/h); median queue wait {wait}; waste {waste}.",
            f"improvements found: {found}.",
            f"proactive changes: {proactive}; {_MEASURED_BY}.",
        ]
    )


def _decisions_section(
    decisions: list[dict[str, Any]], skipped: int, friction: list[dict[str, Any]]
) -> str:
    rows = ["| decision | kind | summary |", "| --- | --- | --- |"]
    for event in decisions:
        rows.append(
            f"| {event.get('event_id')} | {event.get('event_kind')} "
            f"| {_event_summary(event) or '-'} |"
        )
    if not decisions:
        rows.append("| - | none | no decisions recorded |")
    if skipped:
        rows.append(f"| - | skipped | {skipped} unreadable line(s) skipped |")
    operator_needed = [
        event
        for event in friction
        if event.get("event_kind") == "conflict-resolution"
        and event.get("facts", {}).get("resolution") == OPERATOR_RESOLUTION
    ]
    needs = (
        "; ".join(
            f"{event.get('facts', {}).get('task_id')}: {_event_summary(event) or 'conflict'}"
            for event in operator_needed
        )
        or "none"
    )
    return "\n".join([*rows, "", f"needs the operator: {needs}."])


def _next_actions_section(
    tasks: list[dict[str, Any]],
    friction: list[dict[str, Any]],
    stats: Mapping[str, Any],
) -> list[str]:
    rows = ["| action | state | trigger | owner |", "| --- | --- | --- | --- |"]
    for event in friction:
        if event.get("event_kind") not in BLOCKING_FRICTION_KINDS:
            continue
        facts = event.get("facts")
        facts = facts if isinstance(facts, Mapping) else {}
        trigger = _fact_text(facts, "blocker", "error") or _event_summary(event)
        state = "operator-needed" if facts.get("resolution") == OPERATOR_RESOLUTION else "blocked"
        action = _fact_text(facts, "next_step") or f"resolve {event.get('event_kind')}"
        rows.append(
            f"| {action} | {state} | {trigger or '-'} | {facts.get('task_id', 'unassigned')} |"
        )
    waiting = stats.get("lanes_waiting") or []
    for task_id in waiting:
        rows.append(f"| land {task_id} | waiting-for-landing | fast-forward on main | integrator |")
    for task in tasks:
        if task.get("status") == "running":
            rows.append(
                f"| finish {task.get('task_id')} | in-progress "
                f"| terminal result | {task.get('task_id')} |"
            )
    if len(rows) == 2:
        rows.append("| - | idle | no blocked, waiting, or running lanes | - |")
    return rows
