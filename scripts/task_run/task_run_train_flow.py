"""Staging, verification, and finalization helpers for merge trains."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


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
    skill_script,
)
from scripts.task_run.task_run_train_core import (  # noqa: E402
    FAIL,
    PASS,
    TrainError,
    _payload_from_decision,
    decide_next_action,
    landing_review_plan,
)

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
_train_stats = import_repo_module(__file__, "scripts.task_run.task_run_train_stats")
_worktree = import_repo_module(__file__, "scripts.worktree.worktree_create_lib")
_doctor = import_repo_module(__file__, "scripts.worktree.worktree_doctor_lib")
_cleanup = import_repo_module(__file__, "scripts.worktree.worktree_cleanup_lib")
_adapter = import_repo_module(__file__, "scripts.adapter_lib")
_launch_popen = subprocess.Popen


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


def _checked_out_path(repo_root: Path, branch_ref: str) -> Path | None:
    output = _git(repo_root, "worktree", "list", "--porcelain")
    path: Path | None = None
    for block in output.split("\n\n"):
        fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
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
        result = _run_process(["git", "merge", "--ff-only", "--no-edit", tip_sha], cwd=checked_out)
    else:
        result = _run_process(["git", "update-ref", branch_ref, tip_sha, base_sha], cwd=repo_root)
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
        record.update(
            {
                "status": "unavailable-skip",
                "reason": str(exc),
                "non_claim": "NON-CLAIM: no fresh-eye review was started; this result is not review-passed.",
            }
        )
    try:
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
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
                f"could not stack branch {name}: {merged.stderr.strip() or merged.stdout.strip()}"
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
    verify_profile: Callable[[Mapping[str, Any], Path, Path], tuple[bool, list[dict[str, Any]]]],
) -> tuple[list[dict[str, Any]], dict[int, bool], str, dict[str, Any]]:
    prepared = _prepare_worktree(repo_root, stage, dependency_cache)
    if prepared.get("status") != PASS:
        raise TrainError(
            "train verification refused: Charness worktree prepare/doctor failed: "
            f"{prepared.get('next_step') or prepared.get('status')}"
        )
    attempts: list[dict[str, Any]] = []
    full_good, full_results = verify_profile(profile, stage, root / "reports" / "full")
    attempts.append(
        {
            "prefix_count": len(branches),
            "status": PASS if full_good else FAIL,
            "results": full_results,
        }
    )
    outcomes: dict[int, bool] = {0: True, len(branches): full_good}
    main_now = _sha(repo_root, main_branch)
    decision = decide_next_action(branches, outcomes, main_at_start=base_sha, main_now=main_now)
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
        good, results = verify_profile(profile, target, root / "reports" / f"prefix-{count}")
        attempts.append(
            {
                "prefix_count": count,
                "status": PASS if good else FAIL,
                "results": results,
            }
        )
        outcomes[count] = good
        main_now = _sha(repo_root, main_branch)
        decision = decide_next_action(branches, outcomes, main_at_start=base_sha, main_now=main_now)
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
    decision = decide_next_action(branches, outcomes, main_at_start=base_sha, main_now=main_now)
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
        moved = decide_next_action(branches, outcomes, main_at_start=base_sha, main_now=main_after)
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
    # The landing record is best effort: a stats miss must never fail a land.
    _train_stats.record_landing_for_repo(
        repo_root,
        base_sha=base_sha,
        landed_sha=main_after,
        branches=list(branches[:land_count]),
        run_id=run_id,
    )
    return payload
