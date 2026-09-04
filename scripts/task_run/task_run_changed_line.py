"""The changed-line gate a `task run` lane passes before its receipt can say done.

On 2026-09-03 one commit was refused by the pre-push hook four times, every time on
lines a lane had changed and nobody had proven (`green-test-is-not-covered-line`):
each lane reported a focused green, the receipt said `completed`, and the parent
found out at the push. The gate that refuses the push already existed
(`scripts/mutation/release_changed_line_coverage.py`); nothing ran it where the
claim was made. This module runs it once at lane completion, in the lane's own
worktree against the lane's own base, and hands the verdict back so the receipt
carries the same `blocking_detail` the hook would print for that tree.

The gate is the release lane's own script, taken from the lane's tree so that the
bytes judged and the bytes judging are the same revision. A tree that has no such
script (a lane in another repository) is recorded `not-applicable`, never `clean`:
no verdict is a statement, not a pass.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable

import yaml


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import run_monitored_phase  # noqa: E402

GATE_SCRIPT = Path("scripts/mutation/release_changed_line_coverage.py")
#: A lane worktree is a fresh checkout, so it has no generated `plugins/` mirror,
#: and the standing runner the gate instruments refuses a missing mirror (measured
#: on the first #785 probe: `focused producer failed`, exit 2, no line named).
#: The push recipe in docs/development.md regenerates the mirror before the hook
#: for the same reason; the gate runner does it here so the verdict reaches the line.
MIRROR_SYNC_SCRIPT = Path("scripts/plugin_export/sync_root_plugin_manifests.py")
PHASE = "changed-line-gate"
MIRROR_PHASE = "changed-line-gate-mirror"
#: The whole-session shape measured in the gate's own docstring is ~4 min; a lane's
#: candidate is one slice, measured at ~24 s. Ten minutes bounds a pathological
#: focused suite without turning the lane into an unbounded wait.
GATE_TIMEOUT_SECONDS = 600.0
COVERAGE_JSON_NAME = "changed-line-coverage.json"
STDOUT_LOG_NAME = "changed-line-gate.stdout.log"
STDERR_LOG_NAME = "changed-line-gate.stderr.log"

NOT_APPLICABLE = "not-applicable"
NO_VERDICT = "no-verdict"


def _load_mapping(text: str) -> dict[str, Any] | None:
    try:
        loaded = yaml.safe_load(text)
    except (TypeError, ValueError, yaml.YAMLError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _consumer_report(payload: dict[str, Any]) -> dict[str, Any]:
    """The consumer's own report, carried inside the wrapper's `consumer_stdout`."""
    consumer_stdout = payload.get("consumer_stdout")
    if not isinstance(consumer_stdout, str):
        return {}
    return _load_mapping(consumer_stdout) or {}


def summarize_blocking_detail(blocking_detail: Any) -> str:
    """One line naming each unproven line, in the form the hook's reader expects."""
    if not isinstance(blocking_detail, dict) or not blocking_detail:
        return ""
    parts: list[str] = []
    for path in sorted(blocking_detail):
        detail = blocking_detail[path]
        if isinstance(detail, dict):
            lines = detail.get("changed_and_missing") or []
            rendered = ", ".join(str(line) for line in lines)
            parts.append(f"{path} lines {rendered}" if rendered else f"{path}")
        else:
            parts.append(f"{path}: {detail}")
    return "; ".join(parts)


def _sync_plugin_mirror(
    worktree: Path, *, timeout_seconds: float, run: Callable[..., Any]
) -> dict[str, Any] | None:
    """Regenerate the generated `plugins/` mirror in the lane tree, when it has the exporter."""
    script = worktree / MIRROR_SYNC_SCRIPT
    if not script.is_file():
        return None
    command = [sys.executable, str(script), "--repo-root", str(worktree)]
    started = time.monotonic()
    outcome = run(
        command,
        cwd=worktree,
        phase=MIRROR_PHASE,
        timeout_seconds=timeout_seconds,
        display=f"{MIRROR_SYNC_SCRIPT.name} --repo-root <lane>",
    )
    return {
        "command": command,
        "exit_code": int(outcome.returncode),
        "duration_ms": int((time.monotonic() - started) * 1000),
        "stderr_tail": (outcome.stderr or "")[-2000:],
    }


def run_changed_line_gate(
    worktree: Path,
    *,
    base_sha: str,
    log_dir: Path,
    timeout_seconds: float = GATE_TIMEOUT_SECONDS,
    run: Callable[..., Any] = run_monitored_phase,
) -> dict[str, Any]:
    """Run the lane tree's changed-line gate over `base_sha..HEAD` and type its verdict.

    The returned mapping is the receipt's `changed_line_gate` field:

    - `status`: the gate's own status (`clean`, `blocked`, `unestablished`,
      `partial`, `unproven`, `noop`, `no-verdict`) or `not-applicable`;
    - `blocking`: True for any exit the pre-push hook would refuse on, which is
      every non-zero exit, so a lane can never be `done` where the push would stop;
    - `blocking_detail` and `blocking_targets`: the consumer's per-file unproven
      lines, verbatim, so the parent reads at the receipt what the hook prints;
    - `summary`: the one-line rendering of that detail, or the gate's reason.
    """
    script = worktree / GATE_SCRIPT
    if not script.is_file():
        return {
            "status": NOT_APPLICABLE,
            "blocking": False,
            "reason": f"the lane tree has no {GATE_SCRIPT.as_posix()}; no changed-line verdict exists for it",
            "summary": f"changed-line gate not applicable: no {GATE_SCRIPT.as_posix()} in the lane tree",
        }
    log_dir.mkdir(parents=True, exist_ok=True)
    mirror = _sync_plugin_mirror(worktree, timeout_seconds=timeout_seconds, run=run)
    if mirror is not None and mirror["exit_code"] != 0:
        return {
            "status": NO_VERDICT,
            "blocking": True,
            "mirror_sync": mirror,
            "reason": (
                f"the plugin mirror could not be regenerated in the lane tree "
                f"(exit {mirror['exit_code']}), so the gate's focused suite would refuse to run"
            ),
            "summary": "changed-line gate no-verdict: plugin mirror regeneration failed in the lane tree",
        }
    coverage_json = log_dir / COVERAGE_JSON_NAME
    command = [
        sys.executable,
        str(script),
        "--repo-root",
        str(worktree),
        "--base-sha",
        base_sha,
        "--coverage-json",
        str(coverage_json),
        "--refuse-unestablished",
    ]
    started = time.monotonic()
    outcome = run(
        command,
        cwd=worktree,
        phase=PHASE,
        timeout_seconds=timeout_seconds,
        display=f"{GATE_SCRIPT.name} --base-sha {base_sha[:12]}",
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    (log_dir / STDOUT_LOG_NAME).write_text(outcome.stdout, encoding="utf-8")
    (log_dir / STDERR_LOG_NAME).write_text(outcome.stderr, encoding="utf-8")

    verdict: dict[str, Any] = {
        "command": command,
        "exit_code": int(outcome.returncode),
        "duration_ms": duration_ms,
        "mirror_sync": mirror,
        "logs": {
            "stdout": str(log_dir / STDOUT_LOG_NAME),
            "stderr": str(log_dir / STDERR_LOG_NAME),
        },
        "coverage_json": str(coverage_json),
    }
    if getattr(outcome, "timed_out", False):
        verdict.update(
            {
                "status": NO_VERDICT,
                "blocking": True,
                "reason": f"the changed-line gate exceeded {int(timeout_seconds)} s and was stopped",
            }
        )
        verdict["summary"] = f"changed-line gate: {verdict['reason']}"
        return verdict

    payload = _load_mapping(outcome.stdout)
    if payload is None or "status" not in payload:
        # `safe_load` turns a traceback's `Name: text` line into a mapping, so
        # the shape check is on the field the gate always writes, not on the type.
        verdict.update(
            {
                "status": NO_VERDICT,
                "blocking": True,
                "reason": (
                    f"the changed-line gate exited {outcome.returncode} without a readable "
                    "payload, so its exit code stands for nothing"
                ),
            }
        )
        verdict["summary"] = f"changed-line gate: {verdict['reason']}"
        return verdict

    report = _consumer_report(payload)
    status = str(payload.get("status") or NO_VERDICT)
    reason = str(payload.get("reason") or "")
    blocking_detail = report.get("blocking_detail") if isinstance(report, dict) else None
    verdict.update(
        {
            "status": status,
            # Every non-zero exit is one the pre-push hook refuses on; a payload
            # without a verdict blocks too, whatever byte the child returned.
            "blocking": outcome.returncode != 0 or status == NO_VERDICT,
            "reason": reason,
            "analyzed_changed_pool_files": list(payload.get("analyzed_changed_pool_files") or []),
            "unmapped_changed_pool_files": list(payload.get("unmapped_changed_pool_files") or []),
            "blocking_detail": blocking_detail if isinstance(blocking_detail, dict) else {},
            # Verbatim: the consumer writes a mapping of path -> [{line, source}],
            # and the receipt is where the parent reads it, so its shape is the
            # consumer's, not a projection of it.
            "blocking_targets": report.get("blocking_targets") or {},
        }
    )
    detail = summarize_blocking_detail(verdict["blocking_detail"])
    if verdict["blocking"]:
        verdict["summary"] = f"changed-line gate {status} (exit {outcome.returncode}): " + (
            detail or reason or "the gate refused without naming a reason"
        )
    else:
        verdict["summary"] = f"changed-line gate {status}: {reason}".rstrip(": ")
    return verdict
