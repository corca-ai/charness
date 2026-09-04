"""Compatibility façade for the task-run implementation owners.

Existing imports use this module as the support surface. The implementations
are grouped by Git state, scope resolution, runtime persistence, process
execution, and completion evidence so callers retain one stable import path.
"""

from __future__ import annotations

from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import task_run_contract as _contract  # noqa: E402
from scripts.task_run import task_run_evidence as _evidence  # noqa: E402
from scripts.task_run import task_run_execution as _execution  # noqa: E402
from scripts.task_run import task_run_git as _git_owner  # noqa: E402
from scripts.task_run import task_run_runtime as _runtime  # noqa: E402
from scripts.task_run import task_run_scope as _scope  # noqa: E402

FAIL = _contract.FAIL
PASS = _contract.PASS
SCHEMA_VERSION = _contract.SCHEMA_VERSION
TASK_EFFORTS = _contract.TASK_EFFORTS
TASK_MODEL = _contract.TASK_MODEL
TaskRunError = _contract.TaskRunError
_GIT_DISCOVERY_ENV = _contract._GIT_DISCOVERY_ENV
_BRANCH_RE = _contract._BRANCH_RE
_TASK_ID_RE = _contract._TASK_ID_RE

_changed_paths = _git_owner._changed_paths
_candidate_carrier = _git_owner._candidate_carrier
_collect_populations = _git_owner._collect_populations
_collect_populations_with_metadata = _git_owner._collect_populations_with_metadata
_git = _git_owner._git
_git_common_dir = _git_owner._git_common_dir
_git_dir = _git_owner._git_dir
_git_env = _git_owner._git_env
_git_output = _git_owner._git_output
_commit_wip_candidate = _git_owner._commit_wip_candidate
_commit_lane_snapshot = _git_owner._commit_lane_snapshot
PERSIST_CANDIDATE_COMMIT_MESSAGE = _git_owner.PERSIST_CANDIDATE_COMMIT_MESSAGE
_is_inside = _git_owner._is_inside
_parse_nul_paths = _git_owner._parse_nul_paths
_population_delta = _git_owner._population_delta
_require_git_root = _git_owner._require_git_root
_resolve_base_sha = _git_owner._resolve_base_sha
_snapshot_payload = _git_owner._snapshot_payload
_validate_branch = _git_owner._validate_branch
_validate_worktree_path = _git_owner._validate_worktree_path

_execute_codex = _execution._execute_codex
_result_delivery = _execution._result_delivery
_MAX_RESULT_TEXT_BYTES = _execution._MAX_RESULT_TEXT_BYTES

_failure_payload = _runtime._failure_payload
_runtime_preview = _runtime._runtime_preview
_task_id = _runtime._task_id
build_codex_args = _runtime.build_codex_args
build_codex_command = _runtime.build_codex_command
read_task_result = _runtime.read_task_result
read_task_results = _runtime.read_task_results
runner_liveness = _runtime.runner_liveness
utc_now_iso = _runtime.utc_now_iso
task_execution_runtime_root = _runtime.task_execution_runtime_root
task_result_path = _runtime.task_result_path
task_runtime_root = _runtime.task_runtime_root
validate_lane_id = _runtime.validate_lane_id
write_task_result = _runtime.write_task_result
_resolve_codex = _runtime._resolve_codex

_generated_files = _scope._generated_files
_SUSPICIOUS_RUNTIME_PARTS = _scope._SUSPICIOUS_RUNTIME_PARTS
_glob_matches = _scope._glob_matches
_glob_path_matches = _scope._glob_path_matches
_is_glob_scope = _scope._is_glob_scope
_normalize_scope = _scope._normalize_scope
_path_cause = _scope._path_cause
_paths_in_scopes = _scope._paths_in_scopes
_paths_with_directories = _scope._paths_with_directories
_refresh_scope_specs = _scope._refresh_scope_specs
_scope_matches = _scope._scope_matches
_scope_result = _scope._scope_result
_validate_glob_scope = _scope._validate_glob_scope
_git_tree_paths = _scope._git_tree_paths
normalize_scopes = _scope.normalize_scopes
resolve_scope_specs = _scope.resolve_scope_specs


def _completion_evidence(*args: Any, **kwargs: Any) -> Any:
    """Delegate evidence while retaining the historical monkeypatch seam."""
    return _evidence._completion_evidence(*args, glob_matches=_glob_matches, **kwargs)


def record_create(payload: dict[str, Any], create_payload: dict[str, Any]) -> None:
    """Record the create payload, surfacing prepare's dependency path at the top (#792)."""
    payload["create"] = create_payload
    payload["created"] = bool(create_payload.get("created"))
    reuse = (create_payload.get("prepare") or {}).get("dependency_reuse")
    if isinstance(reuse, dict):
        payload["dependency_reuse"] = reuse
