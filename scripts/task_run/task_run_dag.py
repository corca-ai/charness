#!/usr/bin/env python3
# ruff: noqa: E402
"""Read a static lane DAG and pull ready work once, without persisting status."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping


def _load_repo_runtime_bootstrap() -> None:
    marker = ("scripts", "adapter_lib.py")
    root = next(
        (parent for parent in Path(__file__).resolve().parents if parent.joinpath(*marker).is_file()),
        None,
    )
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core import subprocess_guard as _guard
from scripts.runtime_bootstrap import configure_runtime_environment
from scripts.task_run import task_run_contract as _contract
from scripts.task_run import task_run_runtime as _runtime
from scripts.task_run import task_run_state as _state
from scripts.task_run.task_run_train_core import FAIL, PASS

PLAN_SCHEMA = "charness.task-run-dag/v1"
_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
_DEPENDENCY_KINDS = frozenset({"hard", "soft", "integration-gate"})


class DagError(ValueError):
    """A DAG plan or provider observation is unsafe to act on."""


def _plan_repo_root(value: Mapping[str, Any], plan_path: Path) -> Path:
    repo_value = value.get("repo_root")
    if not isinstance(repo_value, str) or not repo_value.strip():
        raise DagError("plan.repo_root must be a non-empty path")
    repo_root = (plan_path.resolve().parent / repo_value).resolve()
    if not repo_root.is_dir():
        raise DagError(f"plan.repo_root is not a directory: {repo_root}")
    return repo_root


def _plan_provider(value: Mapping[str, Any]) -> dict[str, Any]:
    provider = value.get("provider")
    if not isinstance(provider, dict) or set(provider) != {"repo", "parent_issue"}:
        raise DagError("plan.provider must contain exactly repo and parent_issue")
    provider_repo = provider.get("repo")
    parent_issue = provider.get("parent_issue")
    if not isinstance(provider_repo, str) or not re.fullmatch(r"[^/\s]+/[^/\s]+", provider_repo):
        raise DagError("plan.provider.repo must be owner/repository")
    if type(parent_issue) is not int or parent_issue <= 0:
        raise DagError("plan.provider.parent_issue must be a positive integer")
    return {"repo": provider_repo, "parent_issue": parent_issue}


_LANE_FIELDS = {
        "key", "issue_number", "depends_on", "dependency_kinds", "carrier",
        "brief_path", "scopes", "effort", "base", "stacked_on",
}


def _lane_dependencies(raw: Mapping[str, Any], label: str) -> tuple[list[str], dict[str, str]]:
    dependencies = raw.get("depends_on", [])
    if (
        not isinstance(dependencies, list)
        or any(not isinstance(item, str) for item in dependencies)
        or len(set(dependencies)) != len(dependencies)
    ):
        raise DagError(f"{label}.depends_on must be a unique string list")
    kinds = raw.get("dependency_kinds", {})
    if not isinstance(kinds, dict) or set(kinds) - set(dependencies):
        raise DagError(f"{label}.dependency_kinds must name declared dependencies")
    if any(not isinstance(kind, str) or kind not in _DEPENDENCY_KINDS for kind in kinds.values()):
        raise DagError(f"{label}.dependency_kinds values must be hard, soft, or integration-gate")
    return list(dependencies), dict(kinds)


def _lane_execution(raw: Mapping[str, Any], label: str) -> tuple[str, str]:
    carrier = raw.get("carrier")
    if carrier not in _contract.TASK_EXECUTORS:
        raise DagError(f"{label}.carrier must be one of {_contract.TASK_EXECUTORS}")
    effort = raw.get("effort")
    allowed_efforts = (
        _contract.TASK_MUSE_EFFORTS if carrier == "muse" else _contract.TASK_EFFORTS
    )
    if effort not in allowed_efforts:
        raise DagError(f"{label}.effort is invalid for carrier {carrier!r}")
    return carrier, effort


def _lane_brief_and_scopes(
    raw: Mapping[str, Any], label: str, repo_root: Path
) -> tuple[Path, list[str]]:
    brief_value = raw.get("brief_path")
    if not isinstance(brief_value, str) or not brief_value.strip():
        raise DagError(f"{label}.brief_path must be a non-empty repository path")
    brief_path = (repo_root / brief_value).resolve()
    try:
        brief_path.relative_to(repo_root)
    except ValueError as exc:
        raise DagError(f"{label}.brief_path escapes plan.repo_root") from exc
    if not brief_path.is_file():
        raise DagError(f"{label}.brief_path does not exist: {brief_path}")
    scopes = raw.get("scopes")
    if not isinstance(scopes, list) or not scopes or any(
        not isinstance(scope, str) or not scope.strip() for scope in scopes
    ):
        raise DagError(f"{label}.scopes must be a non-empty string list")
    return brief_path, list(scopes)


def _validate_lane(raw: object, index: int, repo_root: Path) -> dict[str, Any]:
    label = f"plan.lanes[{index}]"
    if not isinstance(raw, dict) or set(raw) - _LANE_FIELDS:
        raise DagError(f"{label} must be a mapping with known fields")
    key = raw.get("key")
    issue_number = raw.get("issue_number")
    if not isinstance(key, str) or not _KEY_RE.fullmatch(key):
        raise DagError(f"{label}.key is invalid")
    if type(issue_number) is not int or issue_number <= 0:
        raise DagError(f"{label}.issue_number must be positive")
    dependencies, kinds = _lane_dependencies(raw, label)
    carrier, effort = _lane_execution(raw, label)
    brief_path, scopes = _lane_brief_and_scopes(raw, label, repo_root)
    base, stacked_on = raw.get("base"), raw.get("stacked_on")
    if base is not None and (
        not isinstance(base, str) or not base.strip() or stacked_on is not None
    ):
        raise DagError(f"{label}.base must be non-empty and exclusive with stacked_on")
    if stacked_on is not None and (
        not isinstance(stacked_on, str) or not _KEY_RE.fullmatch(stacked_on)
    ):
        raise DagError(f"{label}.stacked_on must be a lane key")
    return {
        "key": key,
        "issue_number": issue_number,
        "depends_on": dependencies,
        "dependency_kinds": kinds,
        "carrier": carrier,
        "brief_path": brief_path,
        "scopes": scopes,
        "effort": effort,
        "base": base,
        "stacked_on": stacked_on,
    }


def _validate_lanes(raw_lanes: object, repo_root: Path) -> list[dict[str, Any]]:
    if not isinstance(raw_lanes, list) or not raw_lanes:
        raise DagError("plan.lanes must be a non-empty list")
    lanes = [_validate_lane(raw, index, repo_root) for index, raw in enumerate(raw_lanes)]
    keys = [lane["key"] for lane in lanes]
    issue_numbers = [lane["issue_number"] for lane in lanes]
    if len(set(keys)) != len(keys):
        raise DagError("plan lane keys must be unique")
    if len(set(issue_numbers)) != len(issue_numbers):
        raise DagError("plan lane issue numbers must be unique")
    known = set(keys)

    for lane in lanes:
        missing = set(lane["depends_on"]) - known
        if missing:
            raise DagError(f"lane {lane['key']!r} has unknown dependencies {sorted(missing)!r}")
        stacked_on = lane["stacked_on"]
        if stacked_on is not None and (stacked_on not in lane["depends_on"] or lane["dependency_kinds"].get(stacked_on, "hard") != "hard"):
            raise DagError(f"lane {lane['key']!r}.stacked_on must be a hard dependency")
    _validate_acyclic(lanes)
    return lanes


def validate_plan(value: object, *, plan_path: Path) -> dict[str, Any]:
    """Validate one source-of-truth plan and resolve its repository paths."""
    if not isinstance(value, dict):
        raise DagError("plan root must be a mapping")
    allowed = {"schema", "repo_root", "provider", "max_parallel", "lanes"}
    if set(value) - allowed:
        raise DagError(f"plan has unknown keys: {', '.join(sorted(set(value) - allowed))}")
    if value.get("schema") != PLAN_SCHEMA:
        raise DagError(f"plan.schema must be {PLAN_SCHEMA!r}")
    repo_root = _plan_repo_root(value, plan_path)
    provider = _plan_provider(value)
    max_parallel = value.get("max_parallel")
    if type(max_parallel) is not int or max_parallel <= 0:
        raise DagError("plan.max_parallel must be a positive integer")
    lanes = _validate_lanes(value.get("lanes"), repo_root)
    return {
        "schema": PLAN_SCHEMA,
        "repo_root": repo_root,
        "provider": provider,
        "max_parallel": max_parallel,
        "lanes": lanes,
    }


def _validate_acyclic(lanes: list[dict[str, Any]]) -> None:
    by_key = {lane["key"]: lane for lane in lanes}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str) -> None:
        if key in visiting:
            raise DagError(f"plan dependency cycle includes {key!r}")
        if key in visited:
            return
        visiting.add(key)
        for dependency in by_key[key]["depends_on"]:
            visit(dependency)
        visiting.remove(key)
        visited.add(key)

    for lane in lanes:
        visit(lane["key"])


def load_plan(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DagError(f"could not read plan {path}: {exc}") from exc
    return validate_plan(value, plan_path=path)


def derive_ready(
    plan: Mapping[str, Any],
    child_states: Mapping[str, str],
    *,
    attempted: set[str] | frozenset[str] = frozenset(),
    available_slots: int | None = None,
) -> list[str]:
    """Purely derive open lanes whose hard prerequisites are provider-closed."""
    ready: list[str] = []
    for lane in plan["lanes"]:
        key = lane["key"]
        if child_states.get(key) != "OPEN" or key in attempted:
            continue
        blocked = any(
            lane["dependency_kinds"].get(dependency, "hard") == "hard"
            and child_states.get(dependency) != "CLOSED"
            for dependency in lane["depends_on"]
        )
        if not blocked:
            ready.append(key)
    return ready if available_slots is None else ready[: max(0, available_slots)]


def derive_status(
    plan: Mapping[str, Any], child_states: Mapping[str, str]
) -> list[dict[str, Any]]:
    """Project provider states with a computed readiness explanation; write nothing."""
    rows = []
    for lane in plan["lanes"]:
        state = child_states[lane["key"]]
        blocked_by = [
            dependency
            for dependency in lane["depends_on"]
            if lane["dependency_kinds"].get(dependency, "hard") == "hard"
            and child_states.get(dependency) != "CLOSED"
        ]
        rows.append(
            {
                "key": lane["key"],
                "issue_number": lane["issue_number"],
                "provider_state": state,
                "ready": state == "OPEN" and not blocked_by,
                "blocked_by": blocked_by,
            }
        )
    return rows


def read_provider_children(repo_root: Path, provider_repo: str, parent_issue: int) -> dict[int, str]:
    """Read child state through the issue skill's selected provider adapter."""
    source_root = Path(__file__).resolve().parents[2]
    issue_tool = next(
        (
            path
            for root in (source_root, repo_root)
            for path in (
                root / "skills" / "public" / "issue" / "scripts" / "issue_tool.py",
                root / "skills" / "issue" / "scripts" / "issue_tool.py",
            )
            if path.is_file()
        ),
        None,
    )
    if issue_tool is None:
        raise DagError("issue provider command is missing from the Charness source and target repo")
    command = [
        sys.executable, str(issue_tool), "list-sub-issues", "--repo", provider_repo,
        "--number", str(parent_issue), "--repo-root", str(repo_root),
    ]
    result = _guard.run_process(command, cwd=repo_root, timeout_seconds=60)
    if result.returncode != 0:
        raise DagError(result.stderr.strip() or "provider child-state read failed")
    try:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            import yaml

            payload = yaml.safe_load(result.stdout)
    except Exception as exc:
        raise DagError(f"provider child-state response was unreadable: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise DagError("provider did not verify the child-state read")
    children = payload.get("children")
    if not isinstance(children, list):
        raise DagError("provider child-state response has no children list")
    states: dict[int, str] = {}
    for child in children:
        if not isinstance(child, dict):
            raise DagError("provider child-state row is not a mapping")
        number, state = child.get("number"), child.get("state")
        if (
            type(number) is not int
            or number <= 0
            or not isinstance(state, str)
            or state not in {"OPEN", "CLOSED"}
        ):
            raise DagError("provider child-state row has an invalid issue number or state")
        if number in states:
            raise DagError(f"provider repeated child issue #{number}")
        states[number] = state
    return states


def _lane_states(plan: Mapping[str, Any], provider_reader: Callable[..., Any]) -> dict[str, str]:
    raw = provider_reader(
        plan["repo_root"], plan["provider"]["repo"], plan["provider"]["parent_issue"]
    )
    if not isinstance(raw, Mapping):
        raise DagError("provider reader must return issue-number to state mappings")
    expected = {lane["issue_number"] for lane in plan["lanes"]}
    if set(raw) != expected:
        raise DagError("provider child set does not exactly match the static DAG plan")
    states: dict[str, str] = {}
    for lane in plan["lanes"]:
        state = raw[lane["issue_number"]]
        if not isinstance(state, str) or state not in {"OPEN", "CLOSED"}:
            raise DagError(f"provider state for lane {lane['key']!r} is invalid")
        states[lane["key"]] = state
    return states


def _task_records(repo_root: Path) -> dict[str, dict[str, Any]]:
    payload = _runtime.task_status(repo_root)
    records = payload.get("tasks") if isinstance(payload, Mapping) else None
    if not isinstance(records, list):
        return {}
    return {
        record["task_id"]: record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("task_id"), str)
    }


def _record_is_active(record: Mapping[str, Any]) -> bool:
    if record.get("status") != "running":
        return False
    liveness = record.get("liveness")
    return not isinstance(liveness, Mapping) or liveness.get("alive") is not False


def _launch_lane(repo_root: Path, lane: Mapping[str, Any]) -> dict[str, Any]:
    from scripts.task_run import task_run

    prompt = Path(lane["brief_path"]).read_text(encoding="utf-8")
    return task_run.run_task(
        repo_root,
        lane=lane["key"],
        base=lane.get("base"),
        scopes=lane["scopes"],
        prompt=prompt,
        executor=lane["carrier"],
        effort=lane["effort"],
    )


def _is_candidate_sha(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{40,64}", value))


def _lane_result(key: str, payload: object) -> dict[str, Any]:
    receipt = payload if isinstance(payload, Mapping) else {"status": "failed"}
    kind = _state.result_kind_for_receipt(receipt)
    result = {
        "key": key,
        "task_id": receipt.get("task_id", key),
        "result_kind": kind.value,
        "exit_code": _state.exit_code_for_result_kind(kind),
        "blocker": _state.blocker_for_receipt(receipt),
    }
    candidate_sha = receipt.get("target_sha")
    if _is_candidate_sha(candidate_sha):
        result["candidate_sha"] = candidate_sha
    return result


def pull_once(
    plan: Mapping[str, Any],
    *,
    provider_reader: Callable[..., Any] = read_provider_children,
    task_reader: Callable[[Path], dict[str, dict[str, Any]]] = _task_records,
    launcher: Callable[[Path, Mapping[str, Any]], object] = _launch_lane,
) -> dict[str, Any]:
    """Fill free slots from one provider snapshot, refreshing only after a run exits.

    This foreground invocation waits for its launched lanes. It never polls: each
    additional provider read follows a completed lane, and the command exits when
    no ready lane or free slot remains.
    """
    repo_root = Path(plan["repo_root"])
    launched: set[str] = set()
    lane_results: list[dict[str, Any]] = []
    states = _lane_states(plan, provider_reader)
    records = task_reader(repo_root)
    attempted = {lane["key"] for lane in plan["lanes"] if lane["key"] in records}
    external_active = {key for key, record in records.items() if _record_is_active(record)}
    candidate_shas = {
        lane["key"]: records[lane["key"]].get("target_sha")
        for lane in plan["lanes"]
        if lane["key"] in records
    }
    futures: dict[concurrent.futures.Future[object], str] = {}
    worker_count = plan["max_parallel"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as pool:
        while True:
            occupied = len(external_active - launched) + len(futures)
            free_slots = max(0, plan["max_parallel"] - occupied)
            ready = derive_ready(
                plan, states, attempted=attempted | launched, available_slots=free_slots
            )
            by_key = {lane["key"]: lane for lane in plan["lanes"]}
            for key in ready:
                launch_lane = dict(by_key[key])
                stacked_on = launch_lane["stacked_on"]
                if stacked_on is not None:
                    stacked_sha = candidate_shas.get(stacked_on)
                    launch_lane["base"] = stacked_sha if _is_candidate_sha(stacked_sha) else ""
                futures[pool.submit(launcher, repo_root, launch_lane)] = key
                launched.add(key)
            if not futures:
                break
            completed, _pending = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for future in completed:
                key = futures.pop(future)
                try:
                    lane_result = _lane_result(key, future.result())
                    if "candidate_sha" in lane_result:
                        candidate_shas[key] = lane_result["candidate_sha"]
                    lane_results.append(lane_result)
                except Exception as exc:
                    lane_results.append(
                        {"key": key, "task_id": key, "result_kind": _state.ResultKind.FAILED.value,
                         "exit_code": _state.exit_code_for_result_kind(_state.ResultKind.FAILED),
                         "blocker": str(exc)[:300]}
                    )
            states = _lane_states(plan, provider_reader)
            records = task_reader(repo_root)
            attempted.update(
                lane["key"] for lane in plan["lanes"] if lane["key"] in records
            )
            external_active = {
                key for key, record in records.items() if _record_is_active(record)
            }

    lane_order = {lane["key"]: index for index, lane in enumerate(plan["lanes"])}
    lane_results.sort(key=lambda result: lane_order[result["key"]])
    kind = next(
        (
            _state.ResultKind(result["result_kind"])
            for result in lane_results
            if result["result_kind"] != _state.ResultKind.SUCCESS.value
        ),
        _state.ResultKind.SUCCESS,
    )
    return {
        "schema": "charness.task-run-dag-pull/v1",
        "status": PASS if kind is _state.ResultKind.SUCCESS else FAIL,
        "result_kind": kind.value,
        "exit_code": _state.exit_code_for_result_kind(kind),
        "provider": dict(plan["provider"]),
        "provider_states": derive_status(plan, states),
        "launched": lane_results,
    }


def status_once(
    plan: Mapping[str, Any], *, provider_reader: Callable[..., Any] = read_provider_children
) -> dict[str, Any]:
    states = _lane_states(plan, provider_reader)
    return {
        "schema": "charness.task-run-dag-status/v1",
        "status": PASS,
        "result_kind": _state.ResultKind.SUCCESS.value,
        "exit_code": _state.exit_code_for_result_kind(_state.ResultKind.SUCCESS),
        "provider": dict(plan["provider"]),
        "lanes": derive_status(plan, states),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read and pull a static task-run DAG once")
    commands = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("status", "Read provider child state and derive the current ready view"),
        ("pull", "Launch ready lanes into free slots, then exit without polling"),
    ):
        subparser = commands.add_parser(command, help=help_text)
        subparser.add_argument("--plan-file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = load_plan(args.plan_file)
        configure_runtime_environment(plan["repo_root"])
        payload = status_once(plan) if args.command == "status" else pull_once(plan)
    except (DagError, OSError, ValueError, subprocess.SubprocessError) as exc:
        kind = _state.ResultKind.FAILED
        payload = {
            "schema": "charness.task-run-dag/v1",
            "status": FAIL,
            "result_kind": kind.value,
            "exit_code": _state.exit_code_for_result_kind(kind),
            "error": str(exc),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
