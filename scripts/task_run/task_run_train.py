"""Stack and verify an explicit queue of local lane branches."""

from __future__ import annotations

import os
import shlex
import subprocess
import uuid
import xml.etree.ElementTree as ET
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

from scripts.runtime_bootstrap import (  # noqa: E402
    configure_runtime_environment,
    import_repo_module,
    runtime_root,
)
from scripts.task_run import task_run_test_cache as _test_cache  # noqa: E402
from scripts.task_run.task_run_train_core import (  # noqa: E402
    FAIL,
    PASS,
    TrainError,
    default_verify_profile,
    exit_code_for_decision,  # noqa: F401 - re-exported for the `charness train` entrypoint
    stack_order,
    validate_verify_profile,
)
from scripts.task_run.task_run_train_flow import (  # noqa: E402
    _branch_ref,
    _finalize_train,
    _local_ref,
    _sha,
    _stage_train_branches,
    _verify_train_stack,
)

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
_doctor = import_repo_module(__file__, "scripts.worktree.worktree_doctor_lib")
_cleanup = import_repo_module(__file__, "scripts.worktree.worktree_cleanup_lib")
_adapter = import_repo_module(__file__, "scripts.adapter_lib")

PROFILE_RELATIVE_PATH = Path(".agents/train-verify.yaml")


def load_verify_profile(
    repo_root: Path, profile_path: Path | None = None
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    path = profile_path
    if path is None:
        path = repo_root / PROFILE_RELATIVE_PATH
        if not path.is_file():
            return default_verify_profile()
    elif not path.is_absolute():
        path = repo_root / path
    try:
        data = _adapter.load_yaml_file(path)
    except Exception as exc:
        raise TrainError(f"could not load verify profile {path}: {exc}") from exc
    errors = validate_verify_profile(data)
    if errors:
        raise TrainError(f"invalid verify profile {path}: {'; '.join(errors)}")
    return data


def _junit_failures(path: Path) -> set[str]:
    if not path.is_file():
        raise TrainError(f"verify command did not write its JUnit report: {path}")
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise TrainError(f"could not read JUnit report {path}: {exc}") from exc
    failures: set[str] = set()
    for case in root.iter("testcase"):
        if case.find("failure") is not None or case.find("error") is not None:
            failures.add(f"{case.get('classname', '')}::{case.get('name', '')}")
    return failures


def run_verify_profile(
    profile: Mapping[str, Any],
    worktree: Path,
    report_root: Path,
    *,
    cache_root: Path | None = None,
) -> tuple[bool, list[dict[str, Any]]]:
    """Execute declared commands on a prepared candidate and classify outcomes."""
    report_root.mkdir(parents=True, exist_ok=True)
    baseline = {
        (item["command_id"], item["testcase"])
        for item in profile["known_failures"]
    }
    results: list[dict[str, Any]] = []
    cache_root = Path(cache_root) if cache_root is not None else _test_cache.train_cache_root(report_root)
    for entry in profile["commands"]:
        command_id = entry["id"]
        plan = (
            _test_cache.prepare_verify(cache_root, worktree, command_id, entry["argv"])
            if cache_root is not None
            else None
        )
        if plan is not None and plan["skip_result"] is not None:
            results.append(plan["skip_result"])
            continue
        command = plan["command"] if plan is not None else entry["argv"]
        report_kind = entry.get("report", "exit-code")
        env = configure_runtime_environment(worktree, os.environ.copy())
        report_path = report_root / f"{command_id}.xml"
        if report_kind == "junit-xml":
            report_path.unlink(missing_ok=True)
            current = env.get("PYTEST_ADDOPTS", "").strip()
            report_option = shlex.join(["--junitxml", str(report_path)])
            env["PYTEST_ADDOPTS"] = f"{current} {report_option}".strip()
        outcome = _guard.run_monitored_phase(
            command,
            cwd=worktree,
            phase=f"train-verify:{command_id}",
            timeout_seconds=None,
            env=env,
            capture=True,
        )
        failures = _junit_failures(report_path) if report_kind == "junit-xml" else set()
        known_failures = sorted(
            testcase for testcase in failures if (command_id, testcase) in baseline
        )
        new_failures = sorted(
            testcase for testcase in failures if (command_id, testcase) not in baseline
        )
        known_only = bool(known_failures) and len(known_failures) == len(failures)
        timed_out = bool(getattr(outcome, "timed_out", False))
        known_failure_exit = known_only and outcome.returncode == 1 and not timed_out
        good = not new_failures and not timed_out and (
            outcome.returncode == 0 or known_failure_exit
        )
        result = {
            "command_id": command_id,
            "status": PASS if good else FAIL,
            "exit_code": outcome.returncode,
            "timed_out": timed_out,
            "known_failures": known_failures,
            "new_failures": new_failures,
        }
        if not good:
            for key, value in (("stdout_tail", outcome.stdout), ("stderr_tail", outcome.stderr)):
                if value:
                    result[key] = value[-4000:]
        combined = _test_cache.finish_verify(plan, result) if plan is not None else result
        results.append(combined)
    return all(result["status"] == PASS for result in results), results


def run_train(
    repo_root: Path,
    queue: Sequence[str],
    *,
    main_ref: str = "main",
    profile_path: Path | None = None,
) -> dict[str, Any]:
    """Stack a local queue, verify candidates only after forced Charness prepare, and land."""
    repo_root = repo_root.resolve()
    worktrees: list[Path] = []
    payload: dict[str, Any] = {"status": FAIL, "decision": "refused"}
    try:
        branches = stack_order(queue)
        branch_refs = tuple(_branch_ref(repo_root, branch) for branch in branches)
        if len(set(branch_refs)) != len(branch_refs):
            raise TrainError("the train queue contains duplicate local branch refs")
        main_branch = _local_ref(repo_root, main_ref)
        base_sha = _sha(repo_root, main_branch)
        profile = load_verify_profile(repo_root, profile_path)
        run_id = uuid.uuid4().hex
        root = runtime_root(repo_root) / "train-runs" / run_id
        dependency_cache = root.parent / _doctor.DEPENDENCY_CACHE_DIR_NAME
        stage, prefix_shas = _stage_train_branches(
            repo_root,
            branch_refs,
            base_sha,
            root,
            dependency_cache,
            worktrees,
        )
        attempts, outcomes, main_now, decision = _verify_train_stack(
            repo_root,
            branches,
            stage,
            prefix_shas,
            base_sha,
            main_branch,
            root,
            dependency_cache,
            worktrees,
            profile,
            run_verify_profile,
        )
        payload = _finalize_train(
            repo_root,
            branches,
            outcomes,
            decision,
            main_branch,
            base_sha,
            prefix_shas,
            attempts,
            root,
            run_id,
            main_now,
        )
        return payload
    except (OSError, RuntimeError, TrainError, subprocess.SubprocessError) as exc:
        payload.update({"status": FAIL, "decision": "refused", "error": str(exc)})
        return payload
    finally:
        cleanup_failures = []
        for target in reversed(worktrees):
            result = _cleanup.run_cleanup(
                repo_root, target_path=target, yes=True, force=True
            )
            if result.get("status") != PASS:
                cleanup_failures.append(
                    {"path": str(target), "error": result.get("error") or result.get("status")}
                )
        if cleanup_failures:
            payload["cleanup_failures"] = cleanup_failures
            if payload.get("status") == PASS:
                payload["status"] = FAIL
                payload["error"] = (
                    "train completed but Charness could not remove every temporary worktree"
                )
