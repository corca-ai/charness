"""Prelaunch gates: brief critique, premise checks, acceptance skeleton."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import (  # noqa: E402
    run_monitored_phase,
    run_process,
)
from scripts.task_run import task_run_friction as _friction  # noqa: E402
from scripts.task_run.task_run_contract import (  # noqa: E402
    ACCEPTANCE_SKELETON_TIMEOUT_SECONDS,
    BRIEF_CRITIQUE_TIMEOUT_SECONDS,
    AcceptanceSkeletonDeclaration,
    TaskRunError,
)


def _resolve_prelaunch_contract(value: Mapping[str, Any] | None) -> dict[str, Any]:
    value = value if isinstance(value, Mapping) else {}
    critical = value.get("critical_lane", False)
    brief_critique = value.get("brief_critique", False)
    if not isinstance(critical, bool) or not isinstance(brief_critique, bool):
        raise TaskRunError("critical-lane and brief-critique inputs must be booleans")
    skeleton = value.get("acceptance_skeleton")
    if skeleton is not None:
        skeleton = str(skeleton).strip()
        path = Path(skeleton)
        if not skeleton or path.is_absolute() or ".." in path.parts:
            raise TaskRunError("--acceptance-skeleton must be a repo-relative test path")
    if critical and not skeleton:
        raise TaskRunError("--critical-lane requires --acceptance-skeleton")
    raw_checks = value.get("premise_checks", [])
    if not isinstance(raw_checks, (list, tuple)):
        raise TaskRunError("--premise-check inputs must be a list")
    checks = []
    ids: set[str] = set()
    for item in raw_checks:
        if isinstance(item, Mapping):
            item_id, premise, decision = (
                item.get("id"), item.get("premise"), item.get("decision_needed")
            )
        elif isinstance(item, (list, tuple)) and len(item) == 3:
            item_id, premise, decision = item
        else:
            raise TaskRunError("each --premise-check needs ID, PREMISE, and DECISION")
        fields = [str(field).strip() if field is not None else "" for field in (item_id, premise, decision)]
        if not all(fields) or fields[0] in ids:
            raise TaskRunError("premise-check IDs must be unique and every field non-empty")
        ids.add(fields[0])
        checks.append(dict(zip(("id", "premise", "decision_needed"), fields)))
    return {
        "enabled": bool(value.get("brief_critique") or critical or skeleton or checks),
        "critical_lane": critical,
        "acceptance_skeleton": skeleton,
        "premise_checks": checks,
    }


def _brief_critique_prompt(brief: str, checks: Sequence[Mapping[str, Any]]) -> str:
    return (
        "Review this task brief read-only against repository code and available provider docs. "
        "Use this fresh context; treat style as advisory. Set premise_failure true only when a central factual premise makes the task "
        "invalid; one blocked item never sets it. Check each premise independently. Return one JSON object with "
        "premise_failure (boolean), premise_failure_reason, findings, and premise_checks "
        "(array of objects with id, kind: success or premise-blocked, and evidence). "
        "Do not edit files.\n\nTASK BRIEF:\n"
        + brief
        + "\n\nPREMISES:\n"
        + json.dumps(list(checks), ensure_ascii=False)
    )


def _run_brief_critique(
    *, payload: dict[str, Any], resolved: Mapping[str, Any], prompt: str,
    premise_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    from scripts.runtime_bootstrap import import_repo_module
    from scripts.task_run import task_run_execution as execution
    from scripts.task_run import task_run_support as support
    from scripts.task_run.task_run_runtime import (
        _resolve_codex,
        build_codex_command,
    )

    exec_lib = import_repo_module(__file__, "scripts.worktree.worktree_exec_lib")

    executable = _resolve_codex("codex")
    command = build_codex_command(executable, effort="medium")
    command[command.index("--sandbox") + 1] = "read-only"
    task_root = Path(resolved["runtime_path"]) / "task-run" / str(payload["task_id"])
    stdout_log, stderr_log = task_root / "brief-critique.stdout.log", task_root / "brief-critique.stderr.log"
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    target = Path(resolved["target_path"])
    execution_root = Path(payload["execution_runtime_root"])
    configured_env = support.scrubbed_lane_env(
        payload,
        exec_lib.prepare_exec_environment(
            target, os.environ.copy(), runtime_root=execution_root
        ),
        "codex",
    )
    outcome = execution._execute_codex(
        command,
        prompt=_brief_critique_prompt(prompt, premise_checks),
        target_path=target,
        configured_env=configured_env,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=BRIEF_CRITIQUE_TIMEOUT_SECONDS,
    )
    try:
        parsed = json.loads(stdout_log.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        parsed = None
    if outcome.get("exit_code") != 0 or not isinstance(parsed, Mapping):
        return {
            "status": "timed-out" if outcome.get("timed_out") else "unavailable",
            "error": str(outcome.get("exec_error") or "review returned no JSON result")[:300],
        }
    return {
        "status": "completed",
        "premise_failure": parsed.get("premise_failure") is True,
        "premise_failure_reason": str(parsed.get("premise_failure_reason") or "")[:500],
        "findings": parsed.get("findings"),
        "premise_checks": parsed.get("premise_checks"),
    }


def _typed_premise_results(
    declarations: Sequence[Mapping[str, Any]], review: Mapping[str, Any]
) -> list[dict[str, Any]]:
    from scripts.task_run.task_run_state import ResultKind

    observed = review.get("premise_checks")
    by_id: dict[str, Mapping[str, Any]] = {}
    duplicates: set[str] = set()
    if isinstance(observed, list):
        for item in observed:
            item_id = item.get("id") if isinstance(item, Mapping) else None
            if not isinstance(item_id, str):
                continue
            if item_id in by_id:
                duplicates.add(item_id)
            else:
                by_id[item_id] = item
    results = []
    for declaration in declarations:
        item = {} if declaration["id"] in duplicates else by_id.get(declaration["id"], {})
        kind = item.get("kind")
        passed = kind == ResultKind.SUCCESS.value and isinstance(item.get("evidence"), str)
        results.append(
            {
                "id": declaration["id"],
                "kind": ResultKind.SUCCESS.value if passed else ResultKind.PREMISE_BLOCKED.value,
                "evidence": str(item.get("evidence") or "no typed premise evidence returned")[:500],
                "decision_needed": declaration["decision_needed"],
            }
        )
    return results


def run_acceptance_skeleton(worktree: Path, path_value: str) -> dict[str, Any]:
    """Run one committed pytest skeleton and retain a bounded result."""
    path = Path(path_value)
    candidate = worktree / path
    try:
        resolved_candidate = candidate.resolve(strict=True)
        inside_worktree = resolved_candidate.is_relative_to(worktree.resolve())
    except OSError:
        inside_worktree = False
    if path.is_absolute() or ".." in path.parts or not inside_worktree or not candidate.is_file():
        return {"status": "invalid", "exit_code": None, "duration_ms": 0}
    tracked = run_process(
        ["git", "-C", str(worktree), "ls-files", "--error-unmatch", path.as_posix()],
        cwd=worktree,
    )
    if tracked.returncode != 0:
        return {"status": "invalid", "exit_code": None, "duration_ms": 0}
    started = time.monotonic()
    try:
        outcome = run_monitored_phase(
            [sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q", path.as_posix()],
            cwd=worktree,
            phase="task-run:acceptance-skeleton",
            timeout_seconds=ACCEPTANCE_SKELETON_TIMEOUT_SECONDS,
        )
    except OSError as exc:
        code, output, status = None, str(exc), "invalid"
    else:
        if outcome.timed_out:
            code, output, status = None, "acceptance skeleton timed out", "invalid"
        else:
            code = outcome.returncode
            output = (outcome.stdout + outcome.stderr)[-1200:]
            status = "green" if code == 0 else "red" if code == 1 else "invalid"
    return {
        "status": status,
        "exit_code": code,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "output": output,
    }


def acceptance_skeleton_prompt(prompt: str, payload: Mapping[str, Any]) -> str:
    prelaunch = payload.get("prelaunch")
    acceptance = prelaunch.get("acceptance_skeleton") if isinstance(prelaunch, Mapping) else None
    if not isinstance(acceptance, Mapping) or not acceptance.get("path"):
        return prompt
    return (
        prompt.rstrip()
        + "\n\nCritical acceptance skeleton: run `python3 -m pytest -q "
        + str(acceptance["path"])
        + "` and make it pass before reporting completion."
    )


def run_prelaunch_gates(
    payload: dict[str, Any],
    resolved: Mapping[str, Any],
    prompt: str,
    *,
    brief_critic=None,
) -> str | None:
    """Record a bounded brief review and premise results before executor launch."""
    from scripts.task_run.task_run_state import ResultKind

    declaration = resolved["prelaunch"]
    if not declaration["enabled"]:
        return None
    payload["phase"] = "prelaunch"
    checks = declaration["premise_checks"]
    started = time.monotonic()
    try:
        review = (brief_critic or _run_brief_critique)(
            payload=payload,
            resolved=resolved,
            prompt=prompt,
            premise_checks=checks,
        )
    except Exception as exc:  # noqa: BLE001 - advisory review cannot fail open as success
        review = {"status": "unavailable", "error": str(exc)[:300]}
    duration_ms = int((time.monotonic() - started) * 1000)
    review = review if isinstance(review, Mapping) else {"status": "invalid"}
    valid_review = review if review.get("status") == "completed" else {}
    results = _typed_premise_results(checks, valid_review)
    findings = review.get("findings")
    findings = [str(item)[:500] for item in findings if isinstance(item, str)][:10] if isinstance(findings, list) else []
    skeleton = declaration.get("acceptance_skeleton")
    acceptance: AcceptanceSkeletonDeclaration | None = None
    blocker = None
    if skeleton:
        baseline = run_acceptance_skeleton(Path(resolved["target_path"]), skeleton)
        acceptance = {
            "path": skeleton,
            "baseline": baseline,
            "status": "red" if baseline["status"] == "red" else baseline["status"],
        }
        if baseline["status"] != "red":
            blocker = "acceptance skeleton must be committed and failing before launch"
    payload["prelaunch"] = {
        "brief_critique": {
            "status": review.get("status", "invalid"),
            "executor": "codex",
            "timeout_seconds": BRIEF_CRITIQUE_TIMEOUT_SECONDS,
            "duration_ms": duration_ms,
            "premise_failure": review.get("status") == "completed" and review.get("premise_failure") is True,
            "findings": findings,
            "error": str(review.get("error") or "")[:300],
        },
        "premise_checks": results,
        "acceptance_skeleton": acceptance,
    }
    if payload["prelaunch"]["brief_critique"]["premise_failure"]:
        payload["prelaunch"]["status"] = "blocked"
        if resolved.get("runtime_path"):
            _friction.append_friction_event(
                Path(str(resolved["runtime_path"])),
                "premise-failure",
                task_id=str(payload.get("task_id") or "unknown-task"),
                facts={
                    "producer": "task_run_prelaunch",
                    "reason": str(review.get("premise_failure_reason") or "false task premise")[:500],
                },
            )
        return str(review.get("premise_failure_reason") or "brief critique found a false task premise")[:500]
    if blocker:
        payload["prelaunch"]["status"] = "blocked"
        return blocker
    if review.get("status") != "completed" or any(
        item["kind"] == ResultKind.PREMISE_BLOCKED.value for item in results
    ):
        payload["prelaunch"]["status"] = "partial"
    else:
        payload["prelaunch"]["status"] = "passed"
    return None


def finish_acceptance_skeleton(payload: dict[str, Any], worktree: Path) -> dict[str, Any] | None:
    prelaunch = payload.get("prelaunch")
    acceptance = prelaunch.get("acceptance_skeleton") if isinstance(prelaunch, Mapping) else None
    if not isinstance(acceptance, dict) or not acceptance.get("path"):
        return None
    final = run_acceptance_skeleton(worktree, str(acceptance["path"]))
    acceptance["final"] = final
    acceptance["status"] = "green" if final["status"] == "green" else "red"
    return acceptance
