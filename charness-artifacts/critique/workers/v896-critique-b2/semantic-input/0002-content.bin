"""Lane runner command construction and receipt recording."""

from __future__ import annotations

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

from scripts.task_run import task_run_progress as _progress  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402

build_codex_command = _support.build_codex_command
build_muse_command = _support.build_muse_command


def build_lane_prompt(
    prompt: str, *, require_change: bool, scopes: Sequence[str]
) -> str:
    """Shape the lane prompt; implementation lanes get carrier directives.

    A require-change lane once spent a full model run in analysis without a
    scoped edit (#815): the user prompt used to travel verbatim, so nothing
    told the executor it was in an implementation lane. Require-change lanes
    now name the scope, demand prompt entry into the edit loop, and define a
    typed early blocker; all other lanes pass through untouched.
    """
    if not require_change:
        return prompt
    scope_list = ", ".join(scopes)
    return (
        "[charness task-run: implementation lane]\n"
        f"Scope: {scope_list}. This is an implementation lane, not a critique lane.\n"
        "After the minimum contract reads, enter the scoped edit/test loop "
        "promptly and prioritize producing the first scoped diff.\n"
        "Emit progress lines as you go, one per line: CONTRACT-READ when "
        "contract reads are done, EDITING when the first scoped edit lands, "
        "TESTING when verification runs.\n"
        "If discovery shows the real owner of the requested behavior (the file "
        "that must change or the test that owns it) lies outside the declared "
        "scope, do not keep exploring adjacent files: stop promptly and reply "
        "BLOCKED: scope mismatch - real owner <path> is outside declared scope.\n"
        "If you cannot make a scoped change, stop promptly and reply with a "
        "typed blocker on its own line: BLOCKED: <concrete reason>. Do not "
        "consume the run in further analysis once blocked.\n"
        "---\n"
        f"{prompt}"
    )


def lane_receipt_blockers(
    *,
    progress: dict[str, Any],
    require_change: bool,
    scope: Any,
) -> list[str]:
    """Blocker lines naming how a finished lane stalled, if it did (#815).

    A typed `BLOCKED:` line becomes a `lane reported blocker` entry so the
    receipt and next step carry the lane's own reason. A changeless
    require-change lane that never emitted `EDITING` names that stall
    instead; lanes that edited or changed scope need no lane entry.
    """
    if progress["blocker"] is not None:
        return [f"lane reported blocker: {progress['blocker']}"]
    if (
        require_change
        and not scope.get("changed_paths")
        and not scope.get("disallowed_paths")
        and "EDITING" not in progress["phases"]
    ):
        return [
            "lane stalled: require-change lane ended without EDITING and no scoped change"
        ]
    return []


def apply_lane_receipt(
    payload: dict[str, Any],
    blockers: list[str],
    *,
    delivery: Any,
    require_change: bool,
    scope: Any,
    stderr_text: str = "",
    guard_phases: Sequence[str] = (),
) -> None:
    """Record `lane_progress` on the receipt and append lane stall blockers.

    Guard-observed phases merge in canonical order: the live watcher may
    have seen markers that aged out of the terminal transcript scan window,
    and the durable receipt must not be weaker than the live relay (#815).
    """
    parsed = _progress.lane_progress(delivery.get("text") or "", stderr_text)
    phases = [
        phase
        for phase in _progress.LANE_PHASES
        if phase in parsed["phases"] or phase in guard_phases
    ]
    progress = {
        "phases": phases,
        "blocker": parsed["blocker"],
        "merged_guard_phases": [phase for phase in phases if phase not in parsed["phases"]],
    }
    payload["lane_progress"] = progress
    blockers.extend(
        lane_receipt_blockers(progress=progress, require_change=require_change, scope=scope)
    )


def prepare_lane_execution(
    payload: dict[str, Any],
    resolved: dict[str, Any],
    git_worktree_dir: Path,
    execution_runtime_path: Path,
    *,
    prompt: str,
    require_change: bool,
    scopes: Sequence[str],
    executor: str,
    executable: str,
    effort: str,
    worktree: Path,
) -> tuple[list[Path], str, list[str]]:
    """Resolve sandbox grants, shape the lane prompt, and build its command.

    One call prepares everything the lane runner needs to execute: writable
    grants (recorded on the receipt), the shaped prompt (implementation
    directives for require-change lanes, verbatim otherwise), and the
    executor command carrying that prompt.
    """
    writable_dirs = lane_writable_dirs(
        payload,
        resolved,
        git_worktree_dir,
        execution_runtime_path,
        executor=executor,
        worktree=worktree,
    )
    lane_prompt = build_lane_prompt(
        prompt, require_change=require_change, scopes=scopes
    )
    command = lane_command(
        executor=executor,
        executable=executable,
        effort=effort,
        prompt=lane_prompt,
        execution_runtime_path=execution_runtime_path,
        writable_dirs=writable_dirs,
        worktree=worktree,
    )
    return writable_dirs, lane_prompt, command


def _checkpoint_interrupted_lane(
    resolved_target: Path, base_sha: str, scope_specs: list[dict[str, Any]]
) -> dict[str, Any]:
    """Commit declared-scope changes as the WIP candidate, or record the skip.

    Stale harness residue or an empty lane must not become a candidate commit
    (#816). The scope verdict in completion classifies the same population, so
    this reuses its refreshed specs rather than redefining them.
    """
    refreshed_specs = _support._refresh_scope_specs(resolved_target, scope_specs)
    changed = _support._candidate_carrier(resolved_target, base_sha)["changed_paths"]
    scoped = _support._paths_in_scopes(changed, refreshed_specs)
    if not scoped:
        return {
            "status": "skipped",
            "reason": "no scoped changes: no WIP candidate commit created",
            "changed_paths": [],
            "correctness_verified": False,
        }
    return _support._commit_wip_candidate(resolved_target, scoped)


def _in_scope_candidate_paths(candidate: Mapping[str, Any]) -> Sequence[str] | None:
    """The candidate changes the scope verdict admitted, or None when unclassified.

    The scope verdict already split ``changed_paths`` into admitted and
    ``disallowed_paths``; the persistence path reuses that classification
    instead of re-deriving it, mirroring the interrupted-lane WIP checkpoint
    above (#816). ``None`` keeps the historical stage-everything shape for
    callers with no classification to reuse.
    """
    changed = candidate.get("changed_paths")
    disallowed = candidate.get("disallowed_paths")
    if not isinstance(changed, list) or not isinstance(disallowed, list):
        return None
    denied = set(disallowed)
    return [path for path in changed if path not in denied]


def persist_incomplete_candidate(
    worktree: Path,
    *,
    paths: Sequence[str] | None = None,
    git: Callable[..., Any] | None = None,
    git_output: Callable[..., str] | None = None,
) -> dict[str, Any]:
    """Copy a useful dirty candidate onto the lane branch so HEAD carries it (#797).

    ``paths`` carries the scope verdict's admitted set: only those paths are
    staged and committed, so out-of-scope residue never rides the candidate
    commit. An empty set records a skip instead of an empty commit (#816).
    ``None`` keeps the historical stage-everything shape for callers with no
    classification to reuse.
    """
    if paths is not None and not list(paths):
        return {
            "status": "skipped",
            "reason": "no in-scope changes: no persistence commit created",
            "changed_paths": [],
            "correctness_verified": False,
        }
    try:
        return _support._commit_lane_snapshot(
            worktree,
            message=_support.PERSIST_CANDIDATE_COMMIT_MESSAGE,
            paths=None if paths is None else list(paths),
            git=git,
            git_output=git_output,
        )
    except (OSError, _support.TaskRunError, TypeError, AttributeError, ValueError) as exc:
        return {"status": "failed", "error": str(exc), "correctness_verified": False}


def lane_writable_dirs(
    payload: dict[str, Any],
    resolved: dict[str, Any],
    git_worktree_dir: Path,
    execution_runtime_path: Path,
    *,
    executor: str,
    worktree: Path,
) -> list[Path]:
    """Sandbox grants the lane runner honors, recorded on the receipt.

    Codex lanes get workspace-write plus `--add-dir` grants beyond the
    worktree itself: its sandbox holds a workdir's `.agents/` read-only
    (measured 2026-09-02), so the worktree's `.agents/` is granted when
    present. Muse lanes root their single `--workspace` at the lane
    worktree itself and take no `--add-dir` grants (#814); the receipt
    records that root as `workspace` instead of `writable_dirs`.
    """
    if executor != "codex":
        payload["workspace"] = str(worktree)
        return []
    writable_dirs = [resolved["git_common_dir"], git_worktree_dir, execution_runtime_path]
    worktree_agents_dir = Path(payload["worktree_path"]) / ".agents"
    if worktree_agents_dir.is_dir():
        writable_dirs.append(worktree_agents_dir)
    payload["writable_dirs"] = [str(path) for path in writable_dirs]
    return writable_dirs


def lane_command(
    *,
    executor: str,
    executable: str,
    effort: str,
    prompt: str,
    execution_runtime_path: Path,
    writable_dirs: Sequence[Path],
    worktree: Path,
) -> list[str]:
    """Build the lane runner command for the selected executor.

    Codex lanes read the prompt from stdin (`-`); `muse exec` takes no stdin
    prompt, so muse lanes carry it via a prompt file in the lane-private
    execution root. Muse lanes root their single `--workspace` at the lane
    worktree itself (#814); the Codex `--add-dir` grants in `writable_dirs`
    do not apply to them.
    """
    if executor == "muse":
        prompt_file = execution_runtime_path / "prompt.md"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt, encoding="utf-8")
        return build_muse_command(
            executable,
            effort=effort,
            prompt_file=prompt_file,
            worktree=worktree,
        )
    return build_codex_command(
        executable,
        effort=effort,
        writable_dirs=writable_dirs,
    )


def record_lane_runner(
    payload: dict[str, Any],
    *,
    executor: str,
    executable: str,
    effort: str,
    timeout_seconds: int,
) -> None:
    """Record the lane runner block and its legacy `codex` alias."""
    block = {
        "kind": executor,
        "executable": executable,
        "model": _support.TASK_MODEL if executor == "codex" else _support.TASK_MUSE_MODEL,
        "effort": effort,
        "timeout_seconds": timeout_seconds,
        "timeout_scope": f"{executor}-exec",
    }
    payload["executor"] = block
    if executor == "codex":
        # Legacy alias: result.json readers address the runner as "codex".
        payload["codex"] = block
