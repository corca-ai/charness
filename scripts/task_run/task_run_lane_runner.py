"""Lane runner command construction and receipt recording."""

from __future__ import annotations

import json
import os
import uuid
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

from scripts.task_run import task_run_friction as _friction  # noqa: E402
from scripts.task_run import task_run_lesson_injection as _lesson_injection  # noqa: E402
from scripts.task_run import task_run_progress as _progress  # noqa: E402
from scripts.task_run import task_run_scope as _scope  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402

build_codex_command = _support.build_codex_command
build_muse_command = _support.build_muse_command

STEER_ENVELOPE_KIND = "charness.task_steer.v1"
ORCHESTRATION_POINTERS_RELATIVE_PATH = Path(
    ".charness/task-run/orchestration-pointers.md"
)


def read_steer_queue(queue_path: Path) -> list[dict[str, Any]]:
    """Read the latest typed envelope for each message in the lane queue."""
    try:
        lines = queue_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    records: dict[str, dict[str, Any]] = {}
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and record.get("kind") == STEER_ENVELOPE_KIND:
            message_id = record.get("message_id")
            if isinstance(message_id, str):
                records[message_id] = record
    return list(records.values())


def enqueue_steer(queue_path: Path, task_id: str, message: str) -> dict[str, Any]:
    """Append a typed accept/nack envelope for one queued lane message."""
    from scripts.task_run.task_run_runtime import utc_now_iso

    stamp = utc_now_iso()
    normalized = message.strip()
    record = {
        "kind": STEER_ENVELOPE_KIND,
        "message_id": str(uuid.uuid4()),
        "task_id": task_id,
        "message": normalized,
        "queued_at": stamp,
        "delivered_at": None,
        "disposition": "accepted" if normalized else "nacked",
        "reason": None if normalized else "empty-message",
        "resume_path": None,
    }
    if normalized:
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        with queue_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    return record


def update_steer_queue(queue_path: Path, record: Mapping[str, Any]) -> None:
    """Append a delivery update; queue readers retain the newest version."""
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def build_lane_prompt(
    prompt: str,
    *,
    require_change: bool,
    scopes: Sequence[str],
    lesson_injection_block: str = "",
    orchestration_pointer_file: Path | None = None,
) -> str:
    """Shape the lane prompt; implementation lanes get carrier directives.

    A require-change scope is a write boundary, not evidence that the requested
    change is warranted. The carrier requires concept, consumer, owner, and
    evidence-level validation before editing, then defines progress and
    typed-blocker signals; all other lanes pass through untouched.
    """
    shaped = prompt
    if require_change:
        scope_list = ", ".join(scopes)
        shaped = (
            "[charness task-run: implementation lane]\n"
            f"Scope: {scope_list}. The declared scope limits edits, not judgment "
            "about whether the requested change is valid.\n"
            "Before editing, apply one claim-boundary frame: validate the concept "
            "and premise; name a real consumer and distinct observable state; "
            "follow the contract to its canonical behavior owner rather than a "
            "substitute; and state the evidence level with an observer and "
            "falsifier that can see that level. A fixture or simulation may own an "
            "honestly labelled lower-level claim, but must never substitute for or "
            "be reported as product or release behavior. If the available observer "
            "cannot see the requested level, proceed only when the claim can be "
            "explicitly narrowed within user intent while retaining the higher "
            "non-claim. If a required premise is false, the required owner is "
            "outside scope, or the claim cannot be narrowed honestly, do not edit; "
            "stop promptly and reply on its own line: "
            "BLOCKED: premise/scope mismatch - <concrete reason>.\n"
            "After the first scoped edit has landed (after you emitted EDITING), "
            "never run git restore, git reset, git checkout, or git clean to undo "
            "scoped files, even if you discover a scope problem. Keep the "
            "candidate as it is, stop promptly, and reply on its own line with "
            "the typed request: BLOCKED: scope mismatch - real owner <path> is "
            "outside declared scope - <concrete reason and needed hunk>. Name the "
            "exact out-of-scope path so the receipt carries a "
            "scope_extension_request.\n"
            "Emit progress lines as you go, one per line: CONTRACT-READ when "
            "contract and premise validation are done, EDITING when the first "
            "scoped edit lands, TESTING when verification runs.\n"
            "Briefs must declare one estimate as `Lane size: <minutes> minutes; "
            "<commit_units> commit units`. Launch warns above 60 minutes or four "
            "commit units and suggests a split.\n"
            "Before creating a shared helper, builder, interface, or simulator, "
            "search the repository with `rg` for an existing primitive and reuse "
            "it when suitable. Report new shared primitives as candidates instead "
            "of silently landing duplicates.\n"
            "The final report must include `Shared-primitive candidates:` followed "
            "by each candidate's name, path, and purpose, or `none`.\n"
            "If sibling lanes share a new interface, builder, or simulator, define "
            "and land it in a seam lane before fan-out; each sibling must declare "
            "that seam lane as a hard `depends_on`.\n"
            "If you cannot make a scoped change, stop promptly and reply with a "
            "typed blocker on its own line: BLOCKED: <concrete reason>. Do not "
            "consume the run in further analysis once blocked.\n"
            "---\n"
            f"{prompt}"
        )
    injections = []
    if lesson_injection_block:
        injections.append(lesson_injection_block)
    if orchestration_pointer_file is not None:
        try:
            pointer_text = orchestration_pointer_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            pointer_text = ""
        if pointer_text:
            injections.append(
                "Orchestration pointers (re-injected for this lane):\n" + pointer_text
            )
    if not injections:
        return shaped
    return shaped + "\n\n" + "\n\n".join(injections)


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
    guard_blocker: str = "",
) -> None:
    """Record `lane_progress` on the receipt and append lane stall blockers.

    Guard-observed phases merge in canonical order: the live watcher may
    have seen markers that aged out of the terminal transcript scan window,
    and the durable receipt must not be weaker than the live relay (#815).
    When the transcript carries no blocker but the guard stopped the lane,
    the guard stop reason is the blocker, so a lost marker write cannot
    silently drop the typed stall.
    """
    parsed = _progress.lane_progress(delivery.get("text") or "", stderr_text)
    blocker = parsed["blocker"] or guard_blocker or None
    phases = [
        phase
        for phase in _progress.LANE_PHASES
        if phase in parsed["phases"] or phase in guard_phases
    ]
    progress = {
        "phases": phases,
        "blocker": blocker,
        "merged_guard_phases": [phase for phase in phases if phase not in parsed["phases"]],
    }
    payload["lane_progress"] = progress
    payload["scope_extension_request"] = _scope.parse_scope_extension_request(blocker)
    if payload["scope_extension_request"] and payload.get("runtime_root"):
        _friction.append_friction_event(
            Path(str(payload["runtime_root"])),
            "block",
            task_id=str(payload.get("task_id") or "unknown-task"),
            facts={
                "producer": "task_run_lane_runner",
                "blocker": str(blocker or "")[:500],
                "scope_extension_request": payload["scope_extension_request"],
            },
        )
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
    repo_root_value = payload.get("repo_root") or resolved.get("repo_root")
    if repo_root_value:
        lesson_block, lesson_result = _lesson_injection._prepare_lesson_injection(
            Path(str(repo_root_value)), prompt
        )
    else:
        lesson_block = ""
        lesson_result = _lesson_injection.lesson_injection_unavailable(
            "task run did not provide a repository root",
            _lesson_injection._declared_recurrence_classes(prompt),
        )
    payload["lesson_injection"] = lesson_result
    lane_prompt = build_lane_prompt(
        prompt,
        require_change=require_change,
        scopes=scopes,
        lesson_injection_block=lesson_block,
        orchestration_pointer_file=(
            Path(str(repo_root_value)) / ORCHESTRATION_POINTERS_RELATIVE_PATH
            if repo_root_value
            else None
        ),
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
        command = build_muse_command(
            executable,
            effort=effort,
            prompt_file=prompt_file,
            worktree=worktree,
        )
        command.extend(["--session-id", str(uuid.uuid4())])
        return command
    command = build_codex_command(
        executable, effort=effort, writable_dirs=writable_dirs
    )
    command[-1:-1] = [
        "--json",
        "--output-last-message",
        str(execution_runtime_path / "codex.last-message.txt"),
    ]
    return command


def steered_lane_invocation(
    executor: str,
    command: Sequence[str],
    prompt: str,
    messages: Sequence[Mapping[str, Any]],
    session_id: str | None,
) -> tuple[list[str], str, str]:
    """Build the next same-worktree invocation with typed messages in its prompt."""
    rendered = "\n\n[Charness steer messages]\n" + "\n".join(
        f"{item['message_id']} ({item['queued_at']}): {item['message']}"
        for item in messages
    )
    amended_prompt = prompt + rendered
    if executor == "muse" and session_id:
        prompt_path = Path(command[command.index("--prompt-file") + 1])
        prompt_path.write_text(amended_prompt, encoding="utf-8")
        return list(command), amended_prompt, "session-resume"
    if executor == "codex" and session_id:
        output_path = Path(command[command.index("--output-last-message") + 1])
        return (
            [
                command[0], "exec", "resume", session_id, "--json",
                "--output-last-message", str(output_path), "-",
            ],
            amended_prompt,
            "session-resume",
        )
    return list(command), amended_prompt, "relaunch-in-place"


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
