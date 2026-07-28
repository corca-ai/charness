"""Is THIS RUN's input trustworthy enough to render a changed-line verdict?

Split out of `check_changed_line_mutation_coverage.py` (D33: a cohesive concept, not a
mechanical spill to dodge the length cap). Everything here answers one question the
verdict logic must not answer for itself: whether the tree the gate is about to judge
is the tree it actually measured.

Three ways it is not, each with its own answer:

* **Contaminated input** — eligible mutation-pool files carry uncommitted worktree or
  index changes that `base..HEAD` cannot see. A clean verdict would be a FALSE GREEN
  for exactly those files. Answered by refusal (`dirty_pool_refusal`) or, under the
  advisory escape hatch, by a recorded `dirty_pool_unverified` plus a loud warning.
* **The repo moved mid-run** — `HEAD` re-resolves to a different commit than the one
  pinned at startup, so the analysis and the tree have drifted apart. Answered by
  `run_state_drift`, which makes the result UNTRUSTED rather than wrong.
* **A git command that failed** — answered by `_git_lines` returning an empty list,
  which every caller here must read as "could not establish", never as "nothing found".

The gate imports these back under its own names, so existing callers and tests keep
working against the surface they already reference.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - import bootstrap
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mutation_changed_files_lib import changed_pool_fingerprint  # noqa: E402


def _git_lines(repo_root: Path, args: list[str]) -> list[str]:
    try:
        result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _head_resolves_to_head(repo_root: Path, head_sha: str) -> bool:
    if head_sha == "HEAD":
        return True
    resolved = _git_lines(repo_root, ["rev-parse", head_sha])
    head = _git_lines(repo_root, ["rev-parse", "HEAD"])
    return bool(resolved) and bool(head) and resolved[0] == head[0]


def uncommitted_pool_changes(repo_root: Path, eligible: set[str]) -> list[str]:
    """Eligible mutation-pool files with uncommitted worktree changes vs HEAD."""
    changed = set(_git_lines(repo_root, ["diff", "--name-only", "HEAD"]))
    changed.update(_git_lines(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(path for path in changed if path in eligible)


def contaminating_pool_changes(repo_root: Path, head_sha: str, eligible: set[str]) -> list[str]:
    """The single detector for "this run's inputs are contaminated".

    Non-empty exactly when the analyzed head resolves to ``HEAD`` *and* eligible
    mutation-pool files carry uncommitted worktree/index changes, i.e. when
    ``base..HEAD`` structurally cannot see them. Both the up-front refusal and the
    legacy late ``warning`` read this one function so they can never disagree.
    """
    if not _head_resolves_to_head(repo_root, head_sha):
        return []
    return uncommitted_pool_changes(repo_root, eligible)


def dirty_pool_refusal(uncommitted: list[str]) -> str:
    """Refuse-fast message for the contaminated-input case.

    The old behaviour emitted this as a ``warning`` only AFTER the ~10 minute
    coverage probe, so the wasted run was already paid for and a contaminated
    green read IDENTICALLY to a real green. Refusing at startup makes the cost
    ~0s and makes the contaminated state unrepresentable as a verdict.
    """
    return (
        f"REFUSING to run: {len(uncommitted)} mutation-pool file(s) have uncommitted "
        f"worktree/index changes that base..HEAD cannot see ({', '.join(uncommitted)}). "
        "A clean verdict would be a FALSE GREEN for them and is indistinguishable from a "
        "real green to the reader. Commit (or stash) those files and re-run, or pass "
        "--allow-dirty for an explicitly ADVISORY read that records itself as unverified."
    )


def _pin_run_state(repo_root: Path, base_sha: str, head_sha: str) -> dict[str, str]:
    """Snapshot what the whole run must stay anchored to.

    ``resolved_head_sha`` pins ``--head-sha HEAD`` to a concrete commit once, so a
    commit landing mid-run cannot re-resolve the range or shift the line mapping
    the ``blocking_detail`` numbers are computed against. ``head_commit`` and the
    changed-pool content fingerprint are the drift tripwires re-read at the end.
    """
    resolved = _git_lines(repo_root, ["rev-parse", head_sha])
    head_commit = _git_lines(repo_root, ["rev-parse", "HEAD"])
    try:
        fingerprint = changed_pool_fingerprint(repo_root, base_sha)
    except (subprocess.CalledProcessError, OSError):
        fingerprint = ""
    return {
        "resolved_head_sha": resolved[0] if resolved else head_sha,
        "head_commit": head_commit[0] if head_commit else "",
        "pool_fingerprint": fingerprint,
    }


def run_state_drift(repo_root: Path, base_sha: str, head_sha: str, pinned: dict[str, str]) -> str | None:
    """Re-read the pinned state at the end; describe any drift, else None.

    A commit (or a worktree edit to a changed pool file) landing WHILE the probe
    runs makes the coverage and the line mapping come from different trees — the
    reported line attributions look plausible and are wrong. There is no way to
    repair that after the fact, so the run reports "untrusted" instead of a verdict.
    """
    now = _pin_run_state(repo_root, base_sha, head_sha)
    drift = []
    if now["head_commit"] != pinned["head_commit"]:
        drift.append(
            f"HEAD moved {pinned['head_commit'][:12] or '<unknown>'} -> "
            f"{now['head_commit'][:12] or '<unknown>'} during the run"
        )
    if now["pool_fingerprint"] != pinned["pool_fingerprint"]:
        drift.append("mutation-pool worktree content changed during the run")
    return "; ".join(drift) if drift else None


def _mark_untrusted(report: dict, drift: str) -> dict:
    """A stale result must never render as ``ok: true``."""
    report["ok"] = False
    report["untrusted"] = True
    report["untrusted_reason"] = (
        f"{drift}: the coverage and the changed-line mapping no longer come from the same "
        "tree, so this run reports NO verdict. Re-run against a settled tree."
    )
    report["changed_line_proof"] = "untrusted"
    return report


def false_green_warning(repo_root: Path, head_sha: str, eligible: set[str]) -> str | None:
    """handoff-4 tripwire: warn when this run is a false-green dry-run.

    When the analyzed head resolves to ``HEAD`` and the worktree has uncommitted
    mutation-pool changes, the ``base..HEAD`` range EXCLUDES those changes — so a
    clean verdict is a false green for them (the exact trap recorded in
    ``charness-artifacts/retro/2026-06-07-producer-rerun-waste.md``: HEAD is the
    parent of the uncommitted changes, so they are judged only post-commit).
    Non-blocking — it warns; the verdict for the in-range lines stands. Since the
    refuse-fast change this is only reachable under ``--allow-dirty`` (the default
    path refuses at startup), and it shares ``contaminating_pool_changes`` with
    that refusal so the two can never disagree about what is contaminated.
    """
    uncommitted = contaminating_pool_changes(repo_root, head_sha, eligible)
    return false_green_message(uncommitted) if uncommitted else None


def false_green_message(uncommitted: list[str]) -> str:
    """The advisory (``--allow-dirty``) wording for an already-detected dirty pool."""
    return (
        f"analyzed head resolves to HEAD but {len(uncommitted)} mutation-pool file(s) have "
        f"uncommitted worktree changes excluded from base..HEAD ({', '.join(uncommitted)}); "
        "those changes are NOT analyzed, so a clean changed-line verdict is a FALSE GREEN for "
        "them. Commit them, then re-run, before trusting this result."
    )


