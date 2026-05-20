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


def _count_active_worktrees(repo_root: Path) -> int:
    """Return the number of git worktrees reported for `repo_root`, or 0 on any failure."""
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 0
    if result.returncode != 0:
        return 0
    return sum(1 for line in result.stdout.splitlines() if line.startswith("worktree "))


def detect_worktree_adapter_normalization(
    repo_root: Path,
) -> tuple[dict[str, object], list[dict[str, str]], list[dict[str, object]]]:
    """Detect a missing worktree adapter and emit a typed recommendation.

    Fires when `.agents/worktree-adapter.yaml` is absent AND any of:
      * a Node hook manager (lefthook / husky / simple-git-hooks) is detected, or
      * `git worktree list` reports more than one entry (the repo actively uses
        worktrees and benefits from a portable `charness worktree prepare` recipe).

    Both findings can be emitted diagnostically when both conditions hold, but at
    most one recommendation is emitted under the existing
    `worktree_adapter_missing_for_hook_manager` id when a hook manager is
    detected (`priority="medium"`); otherwise the new
    `worktree_adapter_missing_for_active_worktrees` id is used (`priority="advisory"`).
    """
    adapter_exists = (repo_root / WORKTREE_ADAPTER_RELATIVE_PATH).is_file()
    hook_manager_detected, hook_manager_evidence = _detect_hook_manager(repo_root)
    worktree_count = _count_active_worktrees(repo_root)
    has_active_worktrees = worktree_count > ACTIVE_WORKTREE_THRESHOLD
    findings: list[dict[str, str]] = []
    recommendations: list[dict[str, object]] = []
    if not adapter_exists and hook_manager_detected:
        findings.append(
            {
                "type": "worktree_adapter_missing_for_hook_manager",
                "message": (
                    f"Detected {hook_manager_detected} via {', '.join(hook_manager_evidence)} "
                    f"but {WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()} is missing. "
                    "`charness worktree prepare` cannot make a fresh worktree usable without it."
                ),
                "recommended_action": "seed_worktree_adapter",
            }
        )
    if not adapter_exists and has_active_worktrees:
        findings.append(
            {
                "type": "worktree_adapter_missing_for_active_worktrees",
                "message": (
                    f"`git worktree list` reports {worktree_count} worktrees but "
                    f"{WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()} is missing. "
                    "Seeding the adapter lets `charness worktree prepare` reproduce per-worktree readiness."
                ),
                "recommended_action": "seed_worktree_adapter",
            }
        )
    if not adapter_exists and hook_manager_detected:
        recommendations.append(
            _recommendation(
                rec_id="worktree_adapter_missing_for_hook_manager",
                target=WORKTREE_ADAPTER_RELATIVE_PATH.as_posix(),
                kind="seed_artifact",
                priority="medium",
                confidence="high",
                enforcement_tier="AUTOMATABLE",
                evidence=[
                    f"hook manager detected: {hook_manager_detected}",
                    f"evidence: {', '.join(hook_manager_evidence)}",
                    f"adapter missing: {WORKTREE_ADAPTER_RELATIVE_PATH.as_posix()}",
                ],
                suggested_action=WORKTREE_ADAPTER_SEED_COMMAND,
            )
        )
    elif not adapter_exists and has_active_worktrees:
        recommendations.append(
            _recommendation(
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
        )
    return (
        {
            "hook_manager_detected": hook_manager_detected,
            "hook_manager_evidence": hook_manager_evidence,
            "worktree_count": worktree_count,
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
