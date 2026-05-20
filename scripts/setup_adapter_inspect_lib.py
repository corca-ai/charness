from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.setup_agent_docs_lib import _recommendation

WORKTREE_ADAPTER_RELATIVE_PATH = Path(".agents/worktree-adapter.yaml")
WORKTREE_ADAPTER_SEED_COMMAND = (
    "python3 $SKILL_DIR/scripts/seed_worktree_adapter.py --repo-root ."
)
ACTIVE_WORKTREE_THRESHOLD = 1
SETUP_ADAPTER_CANDIDATES: tuple[Path, ...] = (
    Path(".agents/setup-adapter.yaml"),
    Path(".codex/setup-adapter.yaml"),
    Path(".claude/setup-adapter.yaml"),
    Path("docs/setup-adapter.yaml"),
    Path("setup-adapter.yaml"),
)


def _detect_hook_manager(repo_root: Path) -> tuple[str | None, list[str]]:
    """Return the detected Node-style hook manager and the path evidence that triggered it."""
    for candidate in ("lefthook.yml", "lefthook.yaml"):
        if (repo_root / candidate).is_file():
            return "lefthook", [candidate]
    if (repo_root / ".husky").is_dir():
        return "husky", [".husky/"]
    package_json = repo_root / "package.json"
    if package_json.is_file():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            data = None
        if isinstance(data, dict) and "simple-git-hooks" in data:
            return "simple-git-hooks", ["package.json: simple-git-hooks"]
    return None, []


def _probe_active_worktrees(repo_root: Path) -> tuple[int, str]:
    """Return `(worktree_count, probe_status)`.

    `probe_status` is one of `ok`, `not_a_git_repo`, `git_missing`, or
    `timeout`. Exposing the status separately keeps the count honest: a
    timeout or missing git binary previously coerced to `0` and silently
    suppressed the missing-adapter recommendation on slow or non-git layouts.
    """
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError:
        return 0, "git_missing"
    except subprocess.TimeoutExpired:
        return 0, "timeout"
    except OSError:
        return 0, "git_missing"
    if result.returncode != 0:
        return 0, "not_a_git_repo"
    count = sum(1 for line in result.stdout.splitlines() if line.startswith("worktree "))
    return count, "ok"


def _hook_manager_finding(hook_manager: str, evidence: list[str]) -> dict[str, str]:
    return {
        "type": "worktree_adapter_missing_for_hook_manager",
        "message": (
            f"Detected {hook_manager} via {', '.join(evidence)} "
            f"but {WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()} is missing. "
            "`charness worktree prepare` cannot make a fresh worktree usable without it."
        ),
        "recommended_action": "seed_worktree_adapter",
    }


def _active_worktrees_finding(worktree_count: int) -> dict[str, str]:
    return {
        "type": "worktree_adapter_missing_for_active_worktrees",
        "message": (
            f"`git worktree list` reports {worktree_count} worktrees but "
            f"{WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()} is missing. "
            "Seeding the adapter lets `charness worktree prepare` reproduce per-worktree readiness."
        ),
        "recommended_action": "seed_worktree_adapter",
    }


def _probe_unavailable_finding(probe_status: str) -> dict[str, str]:
    return {
        "type": "worktree_probe_unavailable",
        "message": (
            f"`git worktree list` could not run ({probe_status}); "
            "the active-worktrees signal for "
            f"{WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()} is unknown."
        ),
        "recommended_action": "investigate_git_worktree_probe",
    }


def _hook_manager_recommendation(
    hook_manager: str, evidence: list[str], probe_status: str, probe_degraded: bool
) -> dict[str, object]:
    rec_evidence = [
        f"hook manager detected: {hook_manager}",
        f"evidence: {', '.join(evidence)}",
        f"adapter missing: {WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()}",
    ]
    if probe_degraded:
        rec_evidence.append(f"worktree probe degraded: {probe_status}")
    return _recommendation(
        rec_id="worktree_adapter_missing_for_hook_manager",
        target=WORKTREE_ADAPTER_RELATIVE_PATH.as_posix(),
        kind="seed_artifact",
        priority="medium",
        confidence="medium" if probe_degraded else "high",
        enforcement_tier="AUTOMATABLE",
        evidence=rec_evidence,
        suggested_action=WORKTREE_ADAPTER_SEED_COMMAND,
    )


def _active_worktrees_recommendation(worktree_count: int) -> dict[str, object]:
    return _recommendation(
        rec_id="worktree_adapter_missing_for_active_worktrees",
        target=WORKTREE_ADAPTER_RELATIVE_PATH.as_posix(),
        kind="seed_artifact",
        priority="advisory",
        confidence="medium",
        enforcement_tier="AUTOMATABLE",
        evidence=[
            f"git worktrees: {worktree_count}",
            "no Node hook manager detected",
            f"adapter missing: {WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()}",
        ],
        suggested_action=WORKTREE_ADAPTER_SEED_COMMAND,
    )


def detect_worktree_adapter_normalization(
    repo_root: Path,
) -> tuple[dict[str, object], list[dict[str, str]], list[dict[str, object]]]:
    """Detect a missing worktree adapter and emit a typed recommendation.

    Fires when `.agents/worktree-adapter.yaml` is absent AND any of:
      * a Node hook manager (lefthook / husky / simple-git-hooks) is detected, or
      * `git worktree list` reports more than one entry (the repo actively uses
        worktrees and benefits from a portable `charness worktree prepare` recipe).

    Both findings can be emitted diagnostically when both conditions hold, but at
    most one recommendation is emitted: the hook-manager id when that signal
    fires (medium priority, high or medium confidence depending on probe state),
    otherwise the active-worktrees id (advisory priority). A failed probe
    (timeout, git_missing) emits a separate `worktree_probe_unavailable`
    finding so operators see the diagnostic gap.
    """
    adapter_exists = (repo_root / WORKTREE_ADAPTER_RELATIVE_PATH).is_file()
    hook_manager_detected, hook_manager_evidence = _detect_hook_manager(repo_root)
    worktree_count, worktree_probe_status = _probe_active_worktrees(repo_root)
    probe_degraded = worktree_probe_status in {"timeout", "git_missing"}
    has_active_worktrees = worktree_count > ACTIVE_WORKTREE_THRESHOLD
    findings: list[dict[str, str]] = []
    recommendations: list[dict[str, object]] = []
    if not adapter_exists and hook_manager_detected:
        findings.append(_hook_manager_finding(hook_manager_detected, hook_manager_evidence))
    if not adapter_exists and has_active_worktrees:
        findings.append(_active_worktrees_finding(worktree_count))
    if probe_degraded and not adapter_exists:
        findings.append(_probe_unavailable_finding(worktree_probe_status))
    if not adapter_exists and hook_manager_detected:
        recommendations.append(
            _hook_manager_recommendation(
                hook_manager_detected, hook_manager_evidence, worktree_probe_status, probe_degraded
            )
        )
    elif not adapter_exists and has_active_worktrees:
        recommendations.append(_active_worktrees_recommendation(worktree_count))
    return (
        {
            "hook_manager_detected": hook_manager_detected,
            "hook_manager_evidence": hook_manager_evidence,
            "worktree_count": worktree_count,
            "worktree_probe_status": worktree_probe_status,
            "adapter_exists": adapter_exists,
            "adapter_path": WORKTREE_ADAPTER_RELATIVE_PATH.as_posix(),
            "seed_command": WORKTREE_ADAPTER_SEED_COMMAND,
        },
        findings,
        recommendations,
    )


def detect_setup_adapter_normalization(
    repo_root: Path,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Promote setup-adapter absence from a warning to an advisory recommendation."""
    adapter_path: Path | None = next(
        (repo_root / candidate for candidate in SETUP_ADAPTER_CANDIDATES if (repo_root / candidate).is_file()),
        None,
    )
    adapter_exists = adapter_path is not None
    recommendations: list[dict[str, object]] = []
    if not adapter_exists:
        recommendations.append(
            _recommendation(
                rec_id="setup_adapter_missing",
                target=SETUP_ADAPTER_CANDIDATES[0].as_posix(),
                kind="seed_artifact",
                priority="advisory",
                confidence="high",
                enforcement_tier="NON_AUTOMATABLE",
                evidence=[
                    "No setup adapter found in any candidate path.",
                    "Using default surface paths and durable artifact location.",
                ],
                suggested_action=(
                    f"Create {SETUP_ADAPTER_CANDIDATES[0].as_posix()} to record preset "
                    "provenance and override surface paths if needed."
                ),
            )
        )
    return (
        {
            "adapter_exists": adapter_exists,
            "adapter_path": adapter_path.relative_to(repo_root).as_posix() if adapter_path is not None else None,
            "candidates": [candidate.as_posix() for candidate in SETUP_ADAPTER_CANDIDATES],
        },
        recommendations,
    )
