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
* **A git command that failed** — answered by `probe_run_trust` returning an
  `unestablished_reason`. This bullet used to say the answer was `_git_lines`
  returning an empty list "which every caller must read as could not establish":
  that was a rule for readers, not a mechanism, and every caller in fact read it
  as "nothing found". `_git_lines_or_none` is the mechanism; `_git_lines` remains
  only as a shim for callers that predate it.

The gate imports these back under its own names, so existing callers and tests keep
working against the surface they already reference.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

from runtime_bootstrap import import_repo_module
from scripts.subprocess_only_coverage_advisory import advisory_scope_line, advisory_stderr_line

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - import bootstrap
    sys.path.insert(0, str(REPO_ROOT))

from scripts.checkout_view import CheckoutView, GitCheckout  # noqa: E402
from scripts.git_status_snapshot import GitStatusError  # noqa: E402
from scripts.git_status_snapshot import parse as parse_git_status  # noqa: E402
from scripts.mutation_changed_files_lib import changed_pool_fingerprint  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

_GIT_OID_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


def _git_lines_or_none(repo_root: Path, args: list[str]) -> list[str] | None:
    """Git output, or ``None`` when the command could not be run or failed.

    The distinction this module's own docstring demanded and did not have: a
    failed `git diff` and a genuinely clean tree both produced ``[]``, so every
    caller read "could not establish" as "nothing found" and a run whose inputs
    could not be inspected rendered a clean verdict.
    """
    try:
        result = run_process(["git", *args], cwd=repo_root, timeout_seconds=None)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _git_lines(repo_root: Path, args: list[str]) -> list[str]:
    """Back-compatible shim: failure collapses to empty.

    Retained because callers outside this module import it by name. New trust
    decisions must use ``_git_lines_or_none`` — collapsing here is exactly the
    conflation ``probe_run_trust`` exists to stop.
    """
    return _git_lines_or_none(repo_root, args) or []


def _resolve_pair(repo_root: Path, first: str, second: str) -> tuple[str, str] | None:
    """Resolve two revisions in one coherent Git snapshot."""
    if first.startswith("-") or second.startswith("-"):
        return None
    resolved = _git_lines_or_none(
        repo_root,
        ["rev-parse", first, second],
    )
    if resolved is None or len(resolved) != 2:
        return None
    return resolved[0], resolved[1]


def _head_resolves_to_head(repo_root: Path, head_sha: str) -> bool:
    if head_sha == "HEAD":
        return True
    pair = _resolve_pair(repo_root, head_sha, "HEAD")
    return pair is not None and pair[0] == pair[1]


def uncommitted_pool_changes(
    repo_root: Path,
    eligible: set[str],
    *,
    checkout: CheckoutView | None = None,
) -> list[str]:
    """Eligible mutation-pool files with uncommitted worktree changes vs HEAD.

    Runs the same status snapshot as ``probe_run_trust`` and must share its path
    decoding: this function was left on the raw helper when that fix landed, so on a
    machine with git's default ``core.quotePath`` a dirty non-ASCII-named pool
    file stayed invisible HERE while the sibling detector saw it — two detectors
    disagreeing about the same tree, which is the state this module exists to
    make impossible.
    """
    changed = set(_worktree_status_paths(repo_root, checkout) or [])
    return sorted(path for path in changed if path in eligible)


#: `unestablished_kind` values. They are separated because the two states earn
#: DIFFERENT exit codes, and collapsing them would hand a broken git the leniency
#: that was justified for a dirty worktree.
INSPECTION_FAILED = "inspection-failed"
SCOPE_MISMATCH = "scope-mismatch"


class TrustProbe(NamedTuple):
    """What this run could establish about the tree it is judging.

    ``unestablished_reason`` is the correction. The previous shape was a bare
    list, so "no contamination found" and "could not look" were the same value,
    and the caller rendered a verdict over both.

    ``unestablished_kind`` keeps the two failure modes separable at the caller.
    A git command that will not run is never the normal mid-work state, so it
    must not inherit the non-blocking treatment that exists specifically because
    *a dirty worktree is* normal mid-work.
    """

    contaminated: list[str]
    unestablished_reason: str | None
    unestablished_kind: str | None = None
    resolved_pair: tuple[str, str] | None = None


class WorktreeTrustSnapshot(NamedTuple):
    """Dirty paths and the live HEAD from one porcelain-v2 status."""

    paths: list[str]
    head_oid: str | None


def _parse_status_snapshot(payload: bytes) -> WorktreeTrustSnapshot:
    snapshot = parse_git_status(payload)
    return WorktreeTrustSnapshot(snapshot.dirty_destination_paths(), snapshot.head_oid)


def _worktree_trust_snapshot(
    repo_root: Path, checkout: CheckoutView | None = None
) -> WorktreeTrustSnapshot | None:
    """Dirty paths and HEAD from one coherent checkout observation."""
    try:
        snapshot = (checkout or GitCheckout(repo_root)).status()
    except (GitStatusError, OSError):
        return None
    return WorktreeTrustSnapshot(snapshot.dirty_destination_paths(), snapshot.head_oid)


def _worktree_status_paths(
    repo_root: Path, checkout: CheckoutView | None = None
) -> list[str] | None:
    snapshot = _worktree_trust_snapshot(repo_root, checkout)
    return None if snapshot is None else snapshot.paths


def probe_run_trust(
    repo_root: Path,
    head_sha: str,
    eligible: set[str],
    *,
    checkout: CheckoutView | None = None,
) -> TrustProbe:
    """Decide whether this run's inputs can support a verdict at all.

    Three ways they cannot, each previously invisible:

    * **The inspection failed.** A `git diff` that errors returned ``[]``, which
      every caller read as a clean pool.
    * **The mutation pool resolved to nothing.** The contamination check is an
      intersection with ``eligible``, so an empty pool makes it vacuously clean —
      the same could-not-look-reads-as-nothing-found shape one layer up, on the
      very set that defines this gate's scope.
    * **The analyzed head is not ``HEAD``.** Coverage is collected from the LIVE
      worktree while the line mapping is computed against the requested head, so
      when they differ the two halves describe different trees. The old detector
      short-circuited to ``[]`` here, which under-approximated in the dangerous
      direction: an explicit older ``--head-sha`` over a dirty pool reported no
      contamination at all. Reproduced before the fix.
    """
    snapshot = _worktree_trust_snapshot(repo_root, checkout)
    if snapshot is None:
        return TrustProbe(
            [],
            "could not inspect the worktree for uncommitted mutation-pool changes",
            INSPECTION_FAILED,
        )
    live_head = snapshot.head_oid
    if live_head is None:
        return TrustProbe(
            [],
            "could not inspect the worktree for uncommitted mutation-pool changes",
            INSPECTION_FAILED,
        )
    if head_sha == "HEAD":
        pair = (live_head, live_head)
    elif _GIT_OID_RE.fullmatch(head_sha):
        pair = (head_sha, live_head)
    else:
        resolved = _git_lines_or_none(repo_root, ["rev-parse", "--verify", head_sha])
        if resolved is None or len(resolved) != 1:
            return TrustProbe(
                [],
                f"could not resolve `{head_sha}` or `HEAD` to compare them",
                INSPECTION_FAILED,
            )
        pair = (resolved[0], live_head)
    # NOT guarded: an empty `eligible` set. A reviewer read it as the same
    # could-not-look-reads-as-nothing-found shape one layer up, and refusing on it
    # was written and then removed: the gate cannot distinguish a mis-resolved pool
    # from a repo that legitimately has none, `test_passes_when_no_eligible_pool_file_changed`
    # pins the legitimate case, and the changed set is intersected with the same
    # pool anyway — so the run already reports "no eligible mutation-pool files
    # changed" and exits 0, which is the honest statement for both. Refusing here
    # would re-break the empty-scope contract this slice just repaired.
    contaminated = sorted(set(snapshot.paths) & eligible)
    if pair[0] != pair[1]:
        return TrustProbe(
            contaminated,
            f"the analyzed head `{pair[0][:12]}` is not the checked-out HEAD "
            f"`{pair[1][:12]}`, but coverage is collected from the HEAD worktree, "
            "so the mapping and the measurement describe different trees",
            SCOPE_MISMATCH,
            pair,
        )
    return TrustProbe(contaminated, None, None, pair)


def contaminating_pool_changes(repo_root: Path, head_sha: str, eligible: set[str]) -> list[str]:
    """The single detector for "this run's inputs are contaminated".

    Non-empty when eligible mutation-pool files carry uncommitted worktree/index
    changes that the analyzed range structurally cannot see. Both the up-front
    refusal and the legacy late ``warning`` read this one function so they can
    never disagree.

    Kept as a list for its existing callers; ``probe_run_trust`` is the surface
    that also reports what could NOT be established, and a caller deciding
    whether to render a verdict must use that one instead.
    """
    return probe_run_trust(repo_root, head_sha, eligible).contaminated


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


def _pin_run_state(
    repo_root: Path,
    base_sha: str,
    head_sha: str,
    *,
    resolved_pair: tuple[str, str] | None = None,
    checkout: CheckoutView | None = None,
) -> dict[str, str]:
    """Snapshot what the whole run must stay anchored to.

    ``resolved_head_sha`` pins ``--head-sha HEAD`` to a concrete commit once, so a
    commit landing mid-run cannot re-resolve the range or shift the line mapping
    the ``blocking_detail`` numbers are computed against. ``head_commit`` and the
    changed-pool content fingerprint are the drift tripwires re-read at the end.
    End-of-run drift re-reads without ``resolved_pair``; startup may reuse the
    pair ``probe_run_trust`` already observed. Pass ``checkout`` only for that
    startup pin so dirty-path inspection and the fingerprint share one status
    snapshot. Drift must omit it: a cached ``GitCheckout.status()`` cannot see
    worktree edits that landed during the run.
    """
    if resolved_pair is not None:
        resolved = [resolved_pair[0]]
        head_commit = [resolved_pair[1]]
    elif head_sha == "HEAD":
        resolved = _git_lines(repo_root, ["rev-parse", "HEAD"])
        head_commit = resolved
    else:
        pair = _resolve_pair(repo_root, head_sha, "HEAD")
        resolved = [pair[0]] if pair is not None else []
        head_commit = [pair[1]] if pair is not None else []
    try:
        fingerprint = changed_pool_fingerprint(repo_root, base_sha, checkout=checkout)
    except OSError:
        fingerprint = ""
    return {
        "resolved_head_sha": resolved[0] if resolved else head_sha,
        "head_commit": head_commit[0] if head_commit else "",
        "pool_fingerprint": fingerprint,
    }


def run_state_drift(
    repo_root: Path, base_sha: str, head_sha: str, pinned: dict[str, str]
) -> str | None:
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
    if not _head_resolves_to_head(repo_root, head_sha):
        # Deliberately silent, and NOT a widening this module forgot. The message
        # below asserts "analyzed head resolves to HEAD", so emitting it for an
        # explicit earlier ref would state something false. The non-HEAD dirty
        # case is not ignored — `probe_run_trust` reports it as unestablished in
        # its own words, which is the accurate claim for that shape.
        return None
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


def write_blocking_stderr(
    blocking: list[str],
    blocking_targets: dict,
    advisory: dict | None = None,
    scope: dict | None = None,
) -> None:
    """The operator-facing narration for a changed-line BLOCK.

    Lives here rather than in the gate for the reason this module exists: it is
    about how far the run's own inputs can be trusted, and the `advisory` argument
    is exactly a caveat on that trust ("these lines may be exercised by a spawn
    whose coverage was never attributed"). The gate imports it back under its old
    private name, so its callers and tests are unchanged.
    """
    missing_targets = sorted(set(blocking) - set(blocking_targets))
    if missing_targets:
        sys.stderr.write(
            "changed-line blocker could not produce exact proof targets for: "
            f"{', '.join(missing_targets)}\n"
        )
    sys.stderr.write(
        f"\n{len(blocking)} changed file(s) have uncovered changed lines; the mutation gate "
        "drops them before mutation (the #260 blocking signal). Use blocking_targets to bind "
        "manual mutant proof to the exact path:line before editing, then cover the listed lines "
        "before merge.\n"
    )
    hint = advisory_stderr_line(advisory or {})
    if hint:
        sys.stderr.write(f"ADVISORY (not a blocker): {hint}")
    scope_line = advisory_scope_line(scope)
    if scope_line:
        sys.stderr.write(f"ADVISORY SCOPE (not a blocker): {scope_line}")
