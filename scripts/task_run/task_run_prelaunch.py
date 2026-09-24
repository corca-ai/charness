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


def _scope_file_deficits(
    plan: Mapping[str, Any],
    target: Path,
    scope_specs: Sequence[Mapping[str, Any]],
    changed_paths: Sequence[Any],
) -> list[str]:
    from scripts.task_run import task_run_scope as scope

    preflight = plan.get("scope_preflight")
    required = preflight.get("required_scope_paths", []) if isinstance(preflight, Mapping) else []
    required = required if isinstance(required, list) else []
    missing = {
        path
        for path in required
        if isinstance(path, str) and not (target / path).exists()
    }
    missing.update(
        path
        for path in changed_paths
        if isinstance(path, str)
        and any(scope._scope_matches(path, spec) for spec in scope_specs)
        and not (target / path).exists()
    )
    for spec in scope_specs:
        path = str(spec.get("path", ""))
        if spec.get("kind") == "glob" and not spec.get("matches"):
            if not any(
                isinstance(changed, str) and scope._scope_matches(changed, spec)
                for changed in changed_paths
            ):
                missing.add(path)
        elif spec.get("kind") == "directory" and not (target / path).is_dir():
            missing.add(path)
    if missing:
        message = "in-scope file deficit: required scope files are absent from the candidate: "
        return [message + ", ".join(sorted(missing))]
    return []


def _coverage_mapping_deficits(
    verifiers: Mapping[str, Any], target: Path, changed_paths: Sequence[Any]
) -> list[str]:
    from scripts.gates_support import select_verifiers

    state = str(verifiers.get("status") or "missing")
    if state != "configured":
        return [] if state == "not-configured" else [
            f"coverage mapping deficit: scope-to-verifier mapping is {state}"
        ]
    blockers: list[str] = []
    unmatched = verifiers.get("unmatched_paths", [])
    unmatched = (
        [path for path in unmatched if isinstance(path, str)]
        if isinstance(unmatched, list)
        else []
    )
    if verifiers.get("bundle_status") == "missing-bundle" or unmatched:
        raw_scope_paths = verifiers.get("scope_paths", [])
        scope_paths = raw_scope_paths if isinstance(raw_scope_paths, list) else []
        paths = unmatched or scope_paths
        blockers.append(
            "coverage mapping deficit: declared scope has no mapped verifier for: "
            + ", ".join(str(path) for path in paths)
        )
    try:
        manifest = select_verifiers.load_surfaces(target, required=False)
    except select_verifiers.SurfaceError:
        manifest = None
    if manifest is None:
        blockers.append("coverage mapping deficit: the selected surfaces manifest is missing")
    elif changed_paths:
        paths = [path for path in changed_paths if isinstance(path, str)]
        try:
            actual = select_verifiers.match_surfaces(manifest, paths)
        except select_verifiers.SurfaceError:
            actual = None
        if actual is None:
            blockers.append("coverage mapping deficit: changed candidate paths could not be mapped")
        else:
            bundle, _notes = select_verifiers.bundle_status(actual)
            unmatched = actual.get("unmatched_paths") or []
            if bundle == "missing-bundle" or unmatched:
                blockers.append(
                    "coverage mapping deficit: changed candidate paths have no mapped verifier for: "
                    + ", ".join(str(path) for path in unmatched)
                )
    return blockers


def _mapped_suite_deficits(verifiers: Mapping[str, Any], target: Path) -> list[str]:
    mapped = verifiers.get("mapped_suites", [])
    mapped = mapped if isinstance(mapped, list) else []
    missing = sorted(
        {
            path
            for path in mapped
            if isinstance(path, str) and not (target / path).is_file()
        }
    )
    if not missing:
        return []
    return [
        "mapped suite deficit: suites selected at launch are missing from the candidate: "
        + ", ".join(missing)
    ]


def acceptance_deficit_blockers(
    payload: Mapping[str, Any],
    resolved_target: Path,
    scope_specs: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
) -> list[str]:
    plan = payload.get("prelaunch_plan")
    if not isinstance(plan, Mapping):
        return ["acceptance deficit: launch preflight and verifier plan are missing"]
    changed = candidate.get("changed_paths")
    changed = changed if isinstance(changed, list) else []
    blockers = _scope_file_deficits(plan, resolved_target, scope_specs, changed)
    verifiers = plan.get("scope_verifiers")
    if not isinstance(verifiers, Mapping):
        return [*blockers, "coverage mapping deficit: no scope-to-verifier plan was recorded"]
    return [
        *blockers,
        *_coverage_mapping_deficits(verifiers, resolved_target, changed),
        *_mapped_suite_deficits(verifiers, resolved_target),
    ]


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
    plan = payload.get("prelaunch_plan")
    sections: list[str] = []
    if isinstance(plan, Mapping):
        verifiers = plan.get("scope_verifiers")
        if isinstance(verifiers, Mapping):
            gates = verifiers.get("completion_gates")
            if isinstance(gates, list) and gates:
                sections.append(
                    "Task-run completion gates selected for the declared scope: "
                    + ", ".join(f"`{gate}`" for gate in gates if isinstance(gate, str))
                    + "."
                )
            surfaces = verifiers.get("matched_surface_ids")
            if isinstance(surfaces, list) and surfaces:
                sections.append(
                    "Verifier surfaces selected for the declared scope: "
                    + ", ".join(f"`{surface}`" for surface in surfaces if isinstance(surface, str))
                    + f" (bundle status: {verifiers.get('bundle_status', 'unknown')})."
                )
            commands = verifiers.get("verify_commands")
            if isinstance(commands, list) and commands:
                sections.append(
                    "Mapped verifier commands:\n"
                    + "\n".join(f"- `{command}`" for command in commands if isinstance(command, str))
                )
        scope_preflight = plan.get("scope_preflight")
        findings = (
            scope_preflight.get("would_touch_outside_declared")
            if isinstance(scope_preflight, Mapping)
            else None
        )
        if isinstance(findings, list) and findings:
            sections.append(
                "Scope preflight findings (resolve before executor launch):\n"
                + "\n".join(
                    f"- would-touch-outside-declared: `{finding['path']}`"
                    for finding in findings
                    if isinstance(finding, Mapping) and isinstance(finding.get("path"), str)
                )
            )
    if isinstance(acceptance, Mapping) and acceptance.get("path"):
        sections.append(
            "Critical acceptance skeleton: run `python3 -m pytest -q "
            + str(acceptance["path"])
            + "` and make it pass before reporting completion."
        )
    if not sections:
        return prompt
    return prompt.rstrip() + "\n\n" + "\n\n".join(sections)


def run_prelaunch_gates(
    payload: dict[str, Any],
    resolved: Mapping[str, Any],
    prompt: str,
    *,
    brief_critic=None,
) -> str | None:
    """Record a bounded brief review and premise results before executor launch."""
    from scripts.task_run.task_run_state import ResultKind

    scope_preflight = resolved.get("scope_preflight")
    findings = (
        scope_preflight.get("would_touch_outside_declared")
        if isinstance(scope_preflight, Mapping)
        else None
    )
    omitted_paths = sorted(
        {
            finding["path"]
            for finding in findings
            if isinstance(finding, Mapping)
            and isinstance(finding.get("path"), str)
            and finding["path"]
        }
        if isinstance(findings, list)
        else set()
    )
    if omitted_paths:
        payload["prelaunch"] = {
            "status": "blocked",
            "scope_preflight": {
                "status": "blocked",
                "omitted_paths": omitted_paths,
            },
        }
        return (
            "scope mismatch: brief evidence names repository paths outside declared --scope: "
            + ", ".join(omitted_paths)
        )

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
