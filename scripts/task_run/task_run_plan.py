"""Resolve task-run shorthand and explicit preflight inputs."""

from __future__ import annotations

import math
import re
import shlex
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
    TASK_EXECUTOR_DEFAULT,
    TASK_EXECUTORS,
    TaskRunError,
)
from scripts.task_run.task_run_git import (  # noqa: E402
    _base_is_fresh,
    _git_common_dir,
    _resolve_base_sha,
    _validate_branch,
    _validate_worktree_path,
)
from scripts.task_run import task_run_prelaunch as _prelaunch  # noqa: E402
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
    _scope_matches,
    normalize_scopes,
    resolve_scope_specs,
    scope_closure_warnings,
)
from scripts.task_run import task_run_scope_evidence as _scope_evidence  # noqa: E402
from scripts.gates_support import select_verifiers as _select_verifiers  # noqa: E402
from scripts.task_run import task_run_changed_line as _changed_line  # noqa: E402
from scripts.mutation.sample_mutation_files import list_eligible as _list_eligible  # noqa: E402

_LANE_SIZE_LIMIT_MINUTES = 60
_LANE_SIZE_LIMIT_COMMIT_UNITS = 4
_LANE_SIZE_RE = re.compile(
    r"(?im)^\s*Lane size:\s*(?P<minutes>\d+)\s*minutes?\s*;\s*"
    r"(?P<units>\d+)\s*commit units?\s*$"
)
_LANE_SIZE_PREFIX_RE = re.compile(r"(?im)^\s*Lane size\s*:")


def _lane_size_hygiene(prompt: str) -> dict[str, Any]:
    """Read the brief estimate against #843-7's 60-minute / four-unit calibration."""
    declarations = list(_LANE_SIZE_RE.finditer(prompt))
    result: dict[str, Any] = {
        "limits": {
            "minutes": _LANE_SIZE_LIMIT_MINUTES,
            "commit_units": _LANE_SIZE_LIMIT_COMMIT_UNITS,
        },
        "estimated_minutes": None,
        "estimated_commit_units": None,
    }
    if len(declarations) != 1:
        malformed = bool(_LANE_SIZE_PREFIX_RE.search(prompt)) or len(declarations) > 1
        result.update(
            status="invalid" if malformed else "missing",
            warning=(
                "brief must declare one lane size as `Lane size: <minutes> minutes; "
                "<commit_units> commit units`."
            ),
        )
        return result

    minutes, units = (int(declarations[0][field]) for field in ("minutes", "units"))
    result.update(estimated_minutes=minutes, estimated_commit_units=units)
    if minutes < 1 or units < 1:
        result.update(
            status="invalid",
            warning="lane size estimates must use positive minutes and commit units.",
        )
    elif minutes > _LANE_SIZE_LIMIT_MINUTES or units > _LANE_SIZE_LIMIT_COMMIT_UNITS:
        result.update(
            status="oversize",
            warning=(
                f"estimated lane size is {minutes} minutes and {units} commit units; "
                "split it into smaller lanes, landing any shared seam interfaces, "
                "builders, and simulator in a hard-dependency lane before sibling fan-out."
            ),
        )
    else:
        result.update(status="within-limit", warning=None)
    return result


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




def _parse_executor_order(value: str | None) -> list[str]:
    """Validate the caller's ordered executor candidates before lane setup."""
    requested = TASK_EXECUTOR_DEFAULT if value is None else value
    executors = [item.strip() for item in requested.split(",")]
    allowed = ", ".join(TASK_EXECUTORS)
    if not executors or any(not item for item in executors):
        raise TaskRunError(
            f"--executor must be one of: {allowed}; use commas to provide fallback order"
        )
    invalid = [item for item in executors if item not in TASK_EXECUTORS]
    if invalid:
        raise TaskRunError(
            f"--executor must be one of: {allowed}; got {', '.join(invalid)}"
        )
    if len(set(executors)) != len(executors):
        raise TaskRunError("--executor entries must be unique")
    return executors


def _resolve_executor_paths(executor_order: Sequence[str], codex: str) -> dict[str, str]:
    """Resolve every explicitly requested candidate before creating a lane."""
    paths = {}
    for candidate in executor_order:
        executable_name = (
            codex
            if codex != "codex" and (candidate == "codex" or len(executor_order) == 1)
            else candidate
        )
        if candidate == "codex" and executable_name == "codex":
            paths[candidate] = _resolve_codex(executable_name)
        else:
            paths[candidate] = resolve_executor_executable(
                executable_name, executor=candidate
            )
    return paths


def _validate_executor_efforts(executor_order: Sequence[str], effort: str) -> None:
    """Reject an effort preset unsupported by any executor in the fallback list."""
    for candidate in executor_order:
        if candidate == "muse":
            build_muse_args(
                effort=effort, prompt_file=Path("prompt.md"), worktree=Path("worktree")
            )
        else:
            build_codex_args(effort=effort)


def _verifier_command_targets(repo_root: Path, command: str) -> list[str]:
    """Extract focused test targets or the standing pytest set from a command."""
    from scripts.gates_support.run_standing_pytest import expand_targets

    try:
        tokens = shlex.split(command)
    except ValueError:
        return []
    targets = [
        tokens[index + 1]
        for index, token in enumerate(tokens[:-1])
        if token in {"--pytest-target", "--target"}
    ]
    if targets:
        return targets
    direct = [
        token.removeprefix("./")
        for token in tokens
        if token.removeprefix("./").startswith("tests/")
        and token.removeprefix("./").endswith(".py")
    ]
    if direct:
        return direct
    return expand_targets(repo_root) if any("pytest" in token for token in tokens) else []


def _mapped_suite_paths(repo_root: Path, commands: Sequence[str]) -> list[str]:
    """Resolve test files selected by the existing repo-owned verifier commands."""
    root = repo_root.resolve()
    suite_paths: set[str] = set()

    def add_target(value: str) -> None:
        target = value.removeprefix("./")
        target_path = Path(target)
        if target_path.is_absolute() or ".." in target_path.parts:
            return
        candidate = root / target
        if any(marker in target for marker in ("*", "?", "[")):
            try:
                matches = sorted(root.glob(target))
            except OSError:
                matches = []
            for match in matches:
                add_target(match.relative_to(root).as_posix())
            return
        if candidate.is_dir():
            try:
                for child in candidate.rglob("*.py"):
                    if child.name.startswith("test_") or child.name.endswith("_test.py"):
                        suite_paths.add(child.relative_to(root).as_posix())
            except OSError:
                return
        elif (candidate.is_file() or target.startswith("tests/")) and target.endswith(".py"):
            if candidate.name.startswith("test_") or candidate.name.endswith("_test.py"):
                suite_paths.add(target)

    for command in commands:
        for target in _verifier_command_targets(root, command):
            add_target(target)
    return sorted(suite_paths)


def _scope_verifier_plan(
    repo_root: Path,
    *,
    scope_paths: Sequence[str],
    tree_paths: set[str],
) -> dict[str, Any]:
    """Precompute the existing surface verifier bundle and task-run gate names."""
    result: dict[str, Any] = {
        "status": "not-configured",
        "scope_paths": list(scope_paths),
        "matched_surface_ids": [],
        "unmatched_paths": [],
        "verify_commands": [],
        "mapped_suites": [],
        "bundle_status": "not-configured",
        "completion_gates": [],
        "notes": [],
    }
    try:
        manifest = _select_verifiers.load_surfaces(repo_root, required=False)
    except _select_verifiers.SurfaceError as exc:
        result.update(
            status="invalid",
            bundle_status="missing-bundle",
            notes=[str(exc)],
        )
        manifest = None
    if manifest is None and result["status"] == "invalid":
        return result
    if manifest is not None:
        mapped = _select_verifiers.match_surfaces(manifest, list(scope_paths))
        bundle_status, notes = _select_verifiers.bundle_status(mapped)
        recommendations = _select_verifiers.command_reasons(mapped, "verify")
        verify_commands = _select_verifiers.dedupe_preserve_order(
            [
                str(item["command"])
                for item in recommendations
                if isinstance(item.get("command"), str)
            ]
        )
        result.update(
            status="configured",
            surfaces_manifest_path=manifest["path"],
            matched_surface_ids=[
                str(surface["surface_id"])
                for surface in mapped.get("matched_surfaces", [])
                if isinstance(surface, Mapping) and isinstance(surface.get("surface_id"), str)
            ],
            unmatched_paths=list(mapped.get("unmatched_paths") or []),
            verify_commands=verify_commands,
            mapped_suites=_mapped_suite_paths(repo_root, verify_commands),
            bundle_status=bundle_status,
            notes=notes,
        )

    gate_script = _changed_line.GATE_SCRIPT.as_posix()
    if gate_script in tree_paths:
        try:
            eligible = set(_list_eligible(repo_root))
        except Exception:  # noqa: BLE001 - other repos may not configure this release pool
            eligible = set()
        if eligible.intersection(scope_paths):
            result["completion_gates"].append(
                _changed_line.GATE_SCRIPT.stem.replace("_", "-")
            )
    return result


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
    executor_order = _parse_executor_order(executor)
    resolved_executor = executor_order[0]
    if lane is not None:
        if any(value is not None for value in (target_path, branch)):
            raise TaskRunError(
                "--lane cannot be combined with --path or --branch; "
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
        resolved_base = "HEAD" if base is None else base
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
    tree_paths, tree_directories = _git_tree_paths(resolved_repo, base_sha)
    scope_warnings = scope_closure_warnings(scope_specs, tree_paths)
    scope_paths = _prelaunch.scope_candidate_paths(
        scope_specs, tree_paths, tree_directories
    )
    evidence_paths = _scope_evidence.suggest_scopes(prompt)
    would_touch_outside = [
        {
            "code": "would-touch-outside-declared",
            "path": path,
            "basis": "the brief/task evidence names this repository path",
        }
        for path in evidence_paths
        if not any(_scope_matches(path, spec) for spec in scope_specs)
    ]
    required_scope_paths = sorted(
        str(spec["path"])
        for spec in scope_specs
        if spec.get("kind") == "exact" and str(spec.get("path", "")) not in tree_paths
    )
    scope_preflight = {
        "status": "findings" if would_touch_outside else "clear",
        "evidence_paths": evidence_paths,
        "would_touch_outside_declared": would_touch_outside,
        "required_scope_paths": required_scope_paths,
    }
    scope_verifiers = _scope_verifier_plan(
        resolved_repo,
        scope_paths=scope_paths,
        tree_paths=tree_paths,
    )
    git_common_dir = (
        Path(repo_snapshot["git_common_dir"])
        if repo_snapshot is not None
        else _git_common_dir(resolved_repo)
    )
    executor_paths = _resolve_executor_paths(executor_order, codex)
    codex_path = executor_paths[resolved_executor]
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        raise TaskRunError("--timeout-seconds must be a positive integer")
    resolved_no_progress = _resolve_no_progress_seconds(no_progress_seconds)
    resolved_prelaunch = _prelaunch._resolve_prelaunch_contract(prelaunch)
    tip_sha = (
        str(repo_snapshot["head"])
        if repo_snapshot is not None
        else _resolve_base_sha(resolved_repo, "HEAD")
    )
    base_fresh = _base_is_fresh(resolved_repo, base_sha, tip_sha)
    base_warning = (
        None
        if base_fresh
        else (
            f"base {base_sha[:12]} does not contain dependency tip {tip_sha[:12]}; "
            "the selected base was kept and no automatic rebase was performed."
        )
    )
    lane_size = _lane_size_hygiene(prompt)
    launch_warnings = [warning for warning in (base_warning, lane_size["warning"]) if warning]
    launch_warnings.extend(
        f"brief evidence names {finding['path']!r} outside declared scope"
        for finding in would_touch_outside
    )
    resolved_prelaunch["scope_preflight"] = scope_preflight
    resolved_prelaunch["scope_verifiers"] = scope_verifiers
    resolved_prelaunch["launch_hygiene"] = {
        "base_freshness": {
            "status": "fresh" if base_fresh else "stale",
            "base_sha": base_sha,
            "dependency_tip_sha": tip_sha,
            "warning": base_warning,
        },
        "lane_size": lane_size,
        "warnings": launch_warnings,
    }
    if lane is None:
        resolved_task_id = _task_id(resolved_branch, task_id)
        runtime_path = _runtime_preview(resolved_repo)
    _validate_executor_efforts(executor_order, effort)
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
        "scope_preflight": scope_preflight,
        "scope_verifiers": scope_verifiers,
        "codex_path": codex_path,
        "executor": resolved_executor,
        "executor_order": executor_order,
        "executor_paths": executor_paths,
        "effort": effort,
        "timeout_seconds": timeout_seconds,
        "task_id": resolved_task_id,
        "runtime_path": runtime_path,
        "prepare": resolved_prepare,
        "require_change": resolved_require_change,
        "report_only": report_only,
        "no_progress_seconds": resolved_no_progress,
        "prelaunch": resolved_prelaunch,
    }
