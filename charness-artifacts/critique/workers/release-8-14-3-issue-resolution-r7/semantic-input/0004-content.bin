"""Interrupted-lane WIP checkpoint decisions."""

from __future__ import annotations

from pathlib import Path
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
from scripts.task_run import task_run_support as _support  # noqa: E402


def _checkpoint_interrupted_lane(
    resolved_target: Path, base_sha: str, scope_specs: list[dict[str, Any]]
) -> dict[str, Any]:
    """Commit declared-scope changes as the WIP candidate, or record the skip.

    Stale harness residue or an empty lane must not become a candidate commit
    (#816). The scope verdict in completion classifies the same population, so
    this reuses its refreshed specs rather than redefining them.

    A lane that ends mid-merge either commits the fully-resolved merge as
    its WIP merge candidate or raises the distinct unresolved-merge blocker
    (#877): a pending merge is never an empty lane, so merge handling
    precedes the empty-lane skip. A resolved merge that reaches outside the
    declared scope raises instead of committing out-of-scope content. A lane
    that ends with a clean tree on top of its own commits names the branch
    tip.
    """
    refreshed_specs = _support._refresh_scope_specs(resolved_target, scope_specs)
    carrier = _support._candidate_carrier(resolved_target, base_sha)
    merging, conflicted = _support._merge_state(resolved_target)
    if merging and conflicted:
        raise _contract.UnresolvedMergeError(conflicted)
    if merging:
        # dirty_paths, not changed_paths: the merge commit changes
        # HEAD-relative state, and base-relative cancellation would hide a
        # path restored to its base version that the commit still changes.
        admitted = set(_support._paths_in_scopes(carrier["dirty_paths"], refreshed_specs))
        outside = sorted(path for path in carrier["dirty_paths"] if path not in admitted)
        if outside:
            raise _contract.MixedScopeMergeError(outside)
        return _support._commit_merge_candidate(resolved_target)
    scoped = _support._paths_in_scopes(carrier["changed_paths"], refreshed_specs)
    if not scoped:
        return {
            "status": "skipped",
            "reason": "no scoped changes: no WIP candidate commit created",
            "changed_paths": [],
            "correctness_verified": False,
        }
    if carrier["carrier_kind"] == "commit-only":
        return _support._tip_candidate(carrier["head_sha"])
    return _support._commit_wip_candidate(resolved_target, scoped)
