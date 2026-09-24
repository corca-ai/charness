"""Resolve task-run shorthand and explicit preflight inputs."""

from __future__ import annotations

import json
import math
import os
import subprocess
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

from scripts.task_run.task_run_contract import (  # noqa: E402
    ACCEPTANCE_SKELETON_TIMEOUT_SECONDS,
    AcceptanceSkeletonDeclaration,
    BRIEF_CRITIQUE_TIMEOUT_SECONDS,
    TASK_EXECUTOR_DEFAULT,
    TASK_EXECUTORS,
    TaskRunError,
)
from scripts.task_run.task_run_git import (  # noqa: E402
    _git_common_dir,
    _resolve_base_sha,
    _validate_branch,
    _validate_worktree_path,
)
from scripts.task_run.task_run_runtime import (  # noqa: E402
    _resolve_codex,
    _runtime_preview,
    _task_id,
    build_codex_args,
    build_muse_args,
    resolve_executor_executable,
    validate_lane_id,
)
from scripts.task_run.task_run_scope import (  # noqa: E402
    _git_tree_paths,
    normalize_scopes,
    resolve_scope_specs,
    scope_closure_warnings,
)


def _resolve_require_change(
    *,
    require_change: bool | None,
    allow_no_change: bool,
    report_only: bool,
    default: bool,
) -> bool:
    """Whether the lane must change at least one path (#827).

    Report-only lanes never require a change. Otherwise shorthand lanes
    require one unless `--allow-no-change` opts out, while explicit lanes
    require one only when `--require-change` is passed.
    """
    if report_only and require_change:
        raise TaskRunError(
            "--report-only cannot be used with --require-change; "
            "a report-only lane must leave the worktree unchanged"
        )
    if report_only:
        return False
    if require_change is None:
        return default and not allow_no_change
    return bool(require_change) and not allow_no_change


def _resolve_no_progress_seconds(value: float | None) -> float | None:
    """Validate an explicit ``--no-progress-seconds`` budget (#835).

    ``None`` keeps the environment/default budget; otherwise a finite number
    ``>= 0`` where ``0`` turns the stop off.
    """
    if value is None:
        return None
    try:
        resolved = float(value)
    except (TypeError, ValueError) as exc:
        raise TaskRunError("--no-progress-seconds must be a number of seconds") from exc
    if not math.isfinite(resolved) or resolved < 0:
        raise TaskRunError(
            "--no-progress-seconds must be a finite number >= 0; 0 turns the stop off"
        )
    return resolved


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
    from scripts.task_run import task_run_execution as execution
    from scripts.task_run import task_run_support as support
    from scripts.task_run.task_run_runtime import (
        _resolve_codex,
        build_codex_command,
    )
    from scripts.runtime_bootstrap import import_repo_module

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
    tracked = subprocess.run(
        ["git", "-C", str(worktree), "ls-files", "--error-unmatch", path.as_posix()],
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked.returncode != 0:
        return {"status": "invalid", "exit_code": None, "duration_ms": 0}
    started = time.monotonic()
    try:
        outcome = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q", path.as_posix()],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=ACCEPTANCE_SKELETON_TIMEOUT_SECONDS,
            check=False,
        )
        code = outcome.returncode
        output = (outcome.stdout + outcome.stderr)[-1200:]
        status = "green" if code == 0 else "red" if code == 1 else "invalid"
    except subprocess.TimeoutExpired:
        code, output, status = None, "acceptance skeleton timed out", "invalid"
    except OSError as exc:
        code, output, status = None, str(exc), "invalid"
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


def resolve_task_inputs(
    resolved_repo: Path,
    *,
    target_path: Path | None,
    branch: str | None,
    base: str | None,
    lane: str | None,
    scopes: Sequence[str],
    prompt: str,
    codex: str,
    executor: str | None = None,
    effort: str | None = None,
    task_id: str | None,
    prepare: bool | None,
    require_change: bool | None,
    skip_prepare: bool,
    allow_no_change: bool,
    timeout_seconds: int,
    repo_snapshot: Mapping[str, Any] | None = None,
    report_only: bool = False,
    no_progress_seconds: float | None = None,
    prelaunch: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if prepare and skip_prepare:
        raise TaskRunError("--prepare and --skip-prepare cannot be used together")
    if require_change and allow_no_change:
        raise TaskRunError("--require-change and --allow-no-change cannot be used together")
    resolved_executor = executor or TASK_EXECUTOR_DEFAULT
    if resolved_executor not in TASK_EXECUTORS:
        allowed_executors = ", ".join(TASK_EXECUTORS)
        raise TaskRunError(f"--executor must be one of: {allowed_executors}")
    if lane is not None:
        if any(value is not None for value in (target_path, branch, base)):
            raise TaskRunError(
                "--lane cannot be combined with --path, --branch, or --base; "
                "choose shorthand or the fully explicit form"
            )
        if task_id is not None:
            raise TaskRunError("--task-id is derived from --lane; omit it in shorthand mode")
        resolved_lane = validate_lane_id(lane)
        runtime_path = _runtime_preview(resolved_repo)
        resolved_task_id = resolved_lane
        resolved_branch = _validate_branch(resolved_repo, f"task/{resolved_lane}")
        resolved_target = _validate_worktree_path(
            resolved_repo, runtime_path / "task-run" / resolved_task_id / "worktree"
        )
        resolved_base = "HEAD"
        resolved_prepare = not skip_prepare if prepare is None else prepare
        resolved_require_change = _resolve_require_change(
            require_change=require_change,
            allow_no_change=allow_no_change,
            report_only=report_only,
            default=True,
        )
    else:
        if any(value is None for value in (target_path, branch, base)):
            raise TaskRunError(
                "explicit task runs require --path, --branch, and --base; "
                "otherwise pass --lane <id>"
            )
        resolved_lane = None
        resolved_target = _validate_worktree_path(resolved_repo, target_path)
        resolved_branch = _validate_branch(resolved_repo, branch)
        resolved_base = base
        resolved_prepare = bool(prepare) and not skip_prepare
        resolved_require_change = _resolve_require_change(
            require_change=require_change,
            allow_no_change=allow_no_change,
            report_only=report_only,
            default=False,
        )
    if not prompt.strip():
        raise TaskRunError("--prompt or --prompt-file must contain non-empty instructions")
    if effort is None:
        raise TaskRunError("task runs require the orchestrator-selected --effort")
    if repo_snapshot is not None and resolved_base == "HEAD":
        base_sha = str(repo_snapshot["head"])
    else:
        base_sha = _resolve_base_sha(resolved_repo, resolved_base)
    normalized_scopes = normalize_scopes(scopes)
    scope_specs = resolve_scope_specs(resolved_repo, normalized_scopes, base_sha)
    tree_paths, _tree_directories = _git_tree_paths(resolved_repo, base_sha)
    scope_warnings = scope_closure_warnings(scope_specs, tree_paths)
    git_common_dir = (
        Path(repo_snapshot["git_common_dir"])
        if repo_snapshot is not None
        else _git_common_dir(resolved_repo)
    )
    if resolved_executor == "codex" and codex == "codex":
        codex_path = _resolve_codex(codex)
    else:
        executable_name = codex if codex != "codex" else resolved_executor
        codex_path = resolve_executor_executable(
            executable_name, executor=resolved_executor
        )
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        raise TaskRunError("--timeout-seconds must be a positive integer")
    resolved_no_progress = _resolve_no_progress_seconds(no_progress_seconds)
    resolved_prelaunch = _resolve_prelaunch_contract(prelaunch)
    if lane is None:
        resolved_task_id = _task_id(resolved_branch, task_id)
        runtime_path = _runtime_preview(resolved_repo)
    if resolved_executor == "muse":
        # Validate the muse effort preset; the real prompt file and worktree
        # are written at execution time, these paths only exercise validation.
        build_muse_args(
            effort=effort, prompt_file=Path("prompt.md"), worktree=Path("worktree")
        )
    else:
        build_codex_args(effort=effort)
    return {
        "lane": resolved_lane,
        "target_path": resolved_target,
        "branch": resolved_branch,
        "base": resolved_base,
        "base_sha": base_sha,
        "git_common_dir": git_common_dir,
        "scopes": normalized_scopes,
        "scope_specs": scope_specs,
        "scope_warnings": scope_warnings,
        "codex_path": codex_path,
        "executor": resolved_executor,
        "effort": effort,
        "task_id": resolved_task_id,
        "runtime_path": runtime_path,
        "prepare": resolved_prepare,
        "require_change": resolved_require_change,
        "report_only": report_only,
        "no_progress_seconds": resolved_no_progress,
        "prelaunch": resolved_prelaunch,
    }
