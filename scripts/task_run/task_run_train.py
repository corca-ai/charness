"""Stack and verify an explicit queue of local lane branches."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
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
    repo_root_from_script,
    runtime_root,
    skill_script,
)
from scripts.task_run import task_run_test_cache as _test_cache  # noqa: E402
from scripts.task_run.task_run_train_core import (  # noqa: E402
    FAIL,
    PASS,
    TrainError,
    _payload_from_decision,
    decide_next_action,
    default_verify_profile,
    landing_review_plan,
    stack_order,
    validate_verify_profile,
)

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
_worktree = import_repo_module(__file__, "scripts.worktree.worktree_create_lib")
_doctor = import_repo_module(__file__, "scripts.worktree.worktree_doctor_lib")
_cleanup = import_repo_module(__file__, "scripts.worktree.worktree_cleanup_lib")
_adapter = import_repo_module(__file__, "scripts.adapter_lib")

PROFILE_RELATIVE_PATH = Path(".agents/train-verify.yaml")
_launch_popen = subprocess.Popen


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


def _run_process(command: Sequence[str], *, cwd: Path, timeout_seconds: float | None = 30):
    return _guard.run_process(command, cwd=cwd, timeout_seconds=timeout_seconds)


def _git(repo_root: Path, *args: str, cwd: Path | None = None) -> str:
    result = _run_process(["git", *args], cwd=cwd or repo_root)
    if result.returncode != 0:
        raise TrainError(result.stderr.strip() or result.stdout.strip() or "git command failed")
    return result.stdout.strip()


def _local_ref(repo_root: Path, value: str) -> str:
    ref = _git(repo_root, "rev-parse", "--symbolic-full-name", value)
    if not ref.startswith("refs/heads/"):
        raise TrainError(f"{value!r} is not a local branch")
    _git(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}")
    return ref


def _branch_ref(repo_root: Path, value: str) -> str:
    name = value.removeprefix("refs/heads/")
    if not name or name.startswith("-"):
        raise TrainError(f"invalid local branch name {value!r}")
    checked = _run_process(["git", "check-ref-format", "--branch", name], cwd=repo_root)
    if checked.returncode != 0:
        raise TrainError(f"invalid local branch name {value!r}")
    ref = f"refs/heads/{name}"
    _git(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}")
    return ref


def _sha(repo_root: Path, ref: str) -> str:
    return _git(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}")


def _prepare_worktree(repo_root: Path, target: Path, dependency_cache: Path) -> dict[str, Any]:
    return _doctor.run_prepare(
        target,
        force=True,
        require_isolation=True,
        source_root=repo_root,
        dependency_cache_root=dependency_cache,
        dependency_reuse=True,
    )


def _create_worktree(
    repo_root: Path,
    target: Path,
    base: str,
    dependency_cache: Path,
) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    result = _worktree.run_create(
        repo_root,
        target_path=target,
        base=base,
        detach=True,
        prepare=False,
        dependency_cache_root=dependency_cache,
        ephemeral=True,
    )
    if not result.get("created"):
        raise TrainError(result.get("error") or "Charness could not create the train worktree")
    return result


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


def _checked_out_path(repo_root: Path, branch_ref: str) -> Path | None:
    output = _git(repo_root, "worktree", "list", "--porcelain")
    path: Path | None = None
    for block in output.split("\n\n"):
        fields = dict(
            line.split(" ", 1) for line in block.splitlines() if " " in line
        )
        if fields.get("branch") == branch_ref and "worktree" in fields:
            path = Path(fields["worktree"])
            break
    return path


def _land_main(repo_root: Path, branch_ref: str, base_sha: str, tip_sha: str) -> tuple[bool, str]:
    checked_out = _checked_out_path(repo_root, branch_ref)
    if checked_out is not None:
        if _sha(checked_out, branch_ref) != base_sha:
            return False, "main changed before the train could land"
        dirty = _run_process(["git", "status", "--porcelain"], cwd=checked_out)
        if dirty.returncode != 0 or dirty.stdout.strip():
            return False, "the main branch worktree is not clean; train was not landed"
        result = _run_process(
            ["git", "merge", "--ff-only", "--no-edit", tip_sha], cwd=checked_out
        )
    else:
        result = _run_process(
            ["git", "update-ref", branch_ref, tip_sha, base_sha], cwd=repo_root
        )
    if result.returncode != 0:
        return False, result.stderr.strip() or "main changed before the train could land"
    return True, ""


def _prepare_landing_review_packet(repo_root: Path, command: Sequence[str]) -> tuple[str, str]:
    """Prepare and identify the canonical packet for a landed train range."""
    result = _run_process(command, cwd=repo_root, timeout_seconds=None)
    payload = _adapter.load_yaml(result.stdout)
    binding = payload.get("reviewed_input_binding", {})
    if result.returncode or payload.get("ok") is not True or binding.get("usable") is False:
        raise TrainError(str(payload.get("error") or "critique packet preparation was unavailable"))
    return str(binding["packet_path"]), str(binding["packet_sha256"])


def _landing_review_trigger(
    repo_root: Path,
    execution_runtime_root: Path,
    base_sha: str,
    landed_sha: str,
    run_id: str,
) -> dict[str, Any]:
    """Start canonical fresh-eye review without waiting and persist its trigger."""
    owner_root = repo_root_from_script(__file__)
    plan = landing_review_plan(
        sys.executable,
        skill_script(owner_root, "critique", "prepare_packet.py"),
        skill_script(owner_root, "critique", "run_review.py"),
        repo_root,
        execution_runtime_root,
        base_sha,
        landed_sha,
        run_id,
    )
    record, record_path, log_path = plan["record"], plan["record_path"], plan["log_path"]
    try:
        packet_path, record["packet_identity"] = _prepare_landing_review_packet(
            repo_root, plan["prepare_command"]
        )
        command = [*plan["review_command"], packet_path]
        log_path.parent.mkdir(parents=True, exist_ok=True)
        review_env = configure_runtime_environment(repo_root, os.environ.copy())
        with log_path.open("wb") as output:
            process = _launch_popen(
                command,
                cwd=repo_root,
                env=review_env,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=output,
                start_new_session=True,
            )
        record.update(
            {
                "status": "launched",
                "process_id": process.pid,
                "non_claim": (
                    "NON-CLAIM: reviewer completion, live findings, and P1 delivery "
                    "are not proven by this launch record."
                ),
            }
        )
    except Exception as exc:
        record.update({"status": "unavailable-skip", "reason": str(exc), "non_claim": "NON-CLAIM: no fresh-eye review was started; this result is not review-passed."})
    try:
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        record["record_error"] = str(exc)
    return record


def _stage_train_branches(
    repo_root: Path,
    branch_refs: Sequence[str],
    base_sha: str,
    root: Path,
    dependency_cache: Path,
    worktrees: list[Path],
) -> tuple[Path, list[str]]:
    stage = root / "worktrees" / "stack"
    _create_worktree(repo_root, stage, base_sha, dependency_cache)
    worktrees.append(stage)
    prefix_shas = [base_sha]
    for branch_ref in branch_refs:
        merged = _run_process(
            [
                "git",
                "-c",
                "user.name=Charness Train",
                "-c",
                "user.email=charness@localhost",
                "merge",
                "--no-ff",
                "--no-edit",
                branch_ref,
            ],
            cwd=stage,
            timeout_seconds=None,
        )
        if merged.returncode != 0:
            name = branch_ref.removeprefix("refs/heads/")
            raise TrainError(
                f"could not stack branch {name}: "
                f"{merged.stderr.strip() or merged.stdout.strip()}"
            )
        prefix_shas.append(_git(stage, "rev-parse", "HEAD"))
    return stage, prefix_shas


def _verify_train_stack(
    repo_root: Path,
    branches: Sequence[str],
    stage: Path,
    prefix_shas: list[str],
    base_sha: str,
    main_branch: str,
    root: Path,
    dependency_cache: Path,
    worktrees: list[Path],
    profile: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[int, bool], str, dict[str, Any]]:
    prepared = _prepare_worktree(repo_root, stage, dependency_cache)
    if prepared.get("status") != PASS:
        raise TrainError(
            "train verification refused: Charness worktree prepare/doctor failed: "
            f"{prepared.get('next_step') or prepared.get('status')}"
        )
    attempts: list[dict[str, Any]] = []
    full_good, full_results = run_verify_profile(
        profile, stage, root / "reports" / "full"
    )
    attempts.append(
        {
            "prefix_count": len(branches),
            "status": PASS if full_good else FAIL,
            "results": full_results,
        }
    )
    outcomes: dict[int, bool] = {0: True, len(branches): full_good}
    main_now = _sha(repo_root, main_branch)
    decision = decide_next_action(
        branches, outcomes, main_at_start=base_sha, main_now=main_now
    )
    while decision["action"] == "verify-prefix":
        count = decision["prefix_count"]
        target = root / "worktrees" / f"prefix-{count}"
        _create_worktree(repo_root, target, prefix_shas[count], dependency_cache)
        worktrees.append(target)
        prepared = _prepare_worktree(repo_root, target, dependency_cache)
        if prepared.get("status") != PASS:
            raise TrainError(
                f"train bisect verification refused at prefix {count}: "
                "Charness prepare/doctor failed"
            )
        good, results = run_verify_profile(
            profile, target, root / "reports" / f"prefix-{count}"
        )
        attempts.append(
            {
                "prefix_count": count,
                "status": PASS if good else FAIL,
                "results": results,
            }
        )
        outcomes[count] = good
        main_now = _sha(repo_root, main_branch)
        decision = decide_next_action(
            branches, outcomes, main_at_start=base_sha, main_now=main_now
        )
    return attempts, outcomes, main_now, decision


def _finalize_train(
    repo_root: Path,
    branches: Sequence[str],
    outcomes: dict[int, bool],
    decision: dict[str, Any],
    main_branch: str,
    base_sha: str,
    prefix_shas: list[str],
    attempts: list[dict[str, Any]],
    root: Path,
    run_id: str,
    main_now: str,
) -> dict[str, Any]:
    if decision["action"] == "requeue":
        return _payload_from_decision(
            decision,
            queue=branches,
            base_sha=base_sha,
            main_sha=main_now,
            candidate_sha=prefix_shas[-1],
            attempts=attempts,
        )

    land_count = decision["land_count"]
    tip_sha = prefix_shas[land_count]
    main_now = _sha(repo_root, main_branch)
    decision = decide_next_action(
        branches, outcomes, main_at_start=base_sha, main_now=main_now
    )
    if decision["action"] == "requeue":
        return _payload_from_decision(
            decision,
            queue=branches,
            base_sha=base_sha,
            main_sha=main_now,
            candidate_sha=prefix_shas[-1],
            attempts=attempts,
        )
    if land_count == 0:
        return _payload_from_decision(
            decision,
            queue=branches,
            base_sha=base_sha,
            main_sha=main_now,
            candidate_sha=tip_sha,
            attempts=attempts,
        )

    landed, error = _land_main(repo_root, main_branch, base_sha, tip_sha)
    main_after = _sha(repo_root, main_branch)
    if not landed and main_after != base_sha:
        moved = decide_next_action(
            branches, outcomes, main_at_start=base_sha, main_now=main_after
        )
        return _payload_from_decision(
            moved,
            queue=branches,
            base_sha=base_sha,
            main_sha=main_after,
            candidate_sha=prefix_shas[-1],
            attempts=attempts,
        )
    if not landed:
        raise TrainError(error)
    if main_after != tip_sha:
        payload = _payload_from_decision(
            decision,
            queue=branches,
            base_sha=base_sha,
            main_sha=main_after,
            candidate_sha=tip_sha,
            attempts=attempts,
        )
        payload.update(
            {
                "status": FAIL,
                "decision": "land-raced",
                "error": "main changed while the fast-forward was completing",
                "landed_sha": main_after,
            }
        )
        return payload
    payload = _payload_from_decision(
        decision,
        queue=branches,
        base_sha=base_sha,
        main_sha=main_after,
        candidate_sha=tip_sha,
        attempts=attempts,
    )
    payload["landed_sha"] = main_after
    payload["landing_review_trigger"] = _landing_review_trigger(
        repo_root, root, base_sha, main_after, run_id
    )
    return payload


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
