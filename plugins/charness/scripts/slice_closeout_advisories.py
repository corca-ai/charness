#!/usr/bin/env python3
"""Advisory (#328) slice-closeout helpers.

Surface likely-broken doc/SKILL test pins and the one-shot skill-surface
preflight BEFORE the broad pytest / mutation-coverage producer pays for the
failure. These never block closeout; they print ``WARN``/``ADVISORY`` lines to
stderr so the fix happens before the expensive cycle, not at minute six of the
broad suite.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

DEFAULT_GATE_RUNTIME_BUDGET_SECONDS = 120.0
DEFAULT_OVERSLICE_ARTIFACT_RUN = 3


def advise_prose_pin(repo_root: Path, changed_paths: list[str]) -> None:
    """Point at tests/ assertions that pin doc/SKILL prose or paths the slice
    changed. Reads the working-tree diff directly; the substring/path match is a
    heuristic, so it stays advisory."""
    if not any(path.endswith(".md") for path in changed_paths):
        return
    lib = import_repo_module(__file__, "scripts.check_prose_pin")
    report = lib.build_report(repo_root, paths=None, test_roots=[repo_root / "tests"])
    if report["status"] == "findings":
        print(lib.format_human(report), file=sys.stderr)


def _added_vs_base(repo_root: Path, paths: list[str], base: str = "origin/main") -> list[str]:
    """Paths absent from the base tree — the changed-line gate's range anchor.
    Degrades to no advisory when the anchor ref does not resolve (tmp repos).
    Checks `base:<path>` directly rather than merge-base(base, HEAD): a file
    deleted upstream but present at the merge-base reads as "added" and fires
    a spurious stderr-only advisory — accepted over the extra plumbing."""
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base],
        cwd=repo_root,
        capture_output=True,
    )
    if probe.returncode != 0:
        return []
    added: list[str] = []
    for path in paths:
        exists = subprocess.run(
            ["git", "cat-file", "-e", f"{base}:{path}"],
            cwd=repo_root,
            capture_output=True,
        )
        if exists.returncode != 0:
            added.append(path)
    return added


def advise_new_pool_module(repo_root: Path, changed_paths: list[str]) -> None:
    """A slice that ADDS a new mutation-pool module gets no commit-time signal
    that its environment-dependent branches (import fallbacks, dep-missing
    degrades) are uncovered; the first signal otherwise arrives at the bundle
    boundary, where repair costs a full instrumented producer re-run. Surface
    the documented early self-check (implementation-discipline.md) while the
    branch list is still cheap to walk. The unmocked glue (real git anchor +
    real eligibility glob) is pinned end-to-end by the seeded-repo positive in
    tests/quality_gates/test_slice_closeout_new_pool_advisory.py."""
    changed_py = [path for path in changed_paths if path.endswith(".py")]
    if not changed_py:
        return
    sample = import_repo_module(__file__, "scripts.sample_mutation_files")
    eligible = set(sample.list_eligible(repo_root))
    new_pool = sorted(set(_added_vs_base(repo_root, changed_py)) & eligible)
    if not new_pool:
        return
    print(
        "ADVISORY: new mutation-pool module(s) added vs origin/main: "
        + ", ".join(new_pool)
        + "; walk each branch (import fallbacks, dep-missing degrades) into the "
        "introducing slice's tests, then run the early changed-line self-check "
        "(docs/conventions/implementation-discipline.md) so the bundle producer "
        "CONFIRMS instead of discovering: run the --produce-mutation-coverage "
        "closeout, then python3 scripts/check_changed_line_mutation_coverage.py "
        "--repo-root . --base-sha origin/main --reuse-coverage. Before citing a "
        "CI mutation run as changed-line proof, gate the claim with "
        "python3 scripts/check_mutation_run_proof.py --claim changed-line "
        "(a dispatch-green run proves only the score path).",
        file=sys.stderr,
    )


def advise_skill_surface_preflight(repo_root: Path, changed_paths: list[str]) -> None:
    """When the slice edits a gated skill package, point at the one-shot
    portable-package preflight so the serial gate round-trips (ergonomics,
    ownership-overlap, attention-state, length headroom) surface in one pass
    instead of one commit-time gate failure at a time."""
    edited = [
        path
        for path in changed_paths
        if path.startswith(("skills/public/", "skills/support/"))
        and (path.endswith("/SKILL.md") or "/references/" in path)
    ]
    if not edited:
        return
    print(
        "ADVISORY: edited gated skill surface(s); run the one-shot portable-package "
        "preflight to surface all findings at once: "
        f"python3 scripts/check_skill_surface_preflight.py --path {edited[0]} --run-checks",
        file=sys.stderr,
    )


def resolve_gate_runtime_budget_seconds() -> float:
    """Portable, override-able budget for a single closeout gate's baseline
    runtime. A gate that PASSES but exceeds this is gate-baseline / code-quality
    debt (spec achieve-efficiency-improvements, direction C), distinct from
    cadence waste and from 'necessary safety cost'. The env override mirrors the
    progress-interval knob already used by run_slice_closeout; a richer per-gate
    adapter field is a follow-up probe (spec C budget probe)."""
    raw = os.environ.get("CHARNESS_GATE_RUNTIME_BUDGET_SECONDS")
    if raw is None:
        return DEFAULT_GATE_RUNTIME_BUDGET_SECONDS
    try:
        return max(1.0, float(raw))
    except ValueError:
        return DEFAULT_GATE_RUNTIME_BUDGET_SECONDS


def evaluate_gate_runtime_budget(
    executed_commands: list[dict], *, budget_seconds: float
) -> list[dict]:
    """Per-gate runtime verdict over the gates run_slice_closeout actually ran.
    Returns one record per OVER-BUDGET gate so the durable closeout JSON payload
    carries the signal, not only stderr (spec C2). Scope is honest: this sees
    ONLY gates executed THROUGH run_slice_closeout (sync / verify / broad-pytest);
    the host pre-push hook runs as its own process and is NOT covered here (spec
    C1 — capturing the hook's own runtime is a separate probe). Cached/reused
    gates carry no timing and are excluded from the verdict."""
    over_budget: list[dict] = []
    for entry in executed_commands:
        elapsed = entry.get("elapsed_seconds")
        if elapsed is None:
            continue
        if float(elapsed) > budget_seconds:
            command = str(entry.get("command") or "")
            over_budget.append(
                {
                    "phase": entry.get("phase"),
                    "command": command,
                    "elapsed_seconds": float(elapsed),
                    "budget_seconds": budget_seconds,
                    "over_budget": True,
                }
            )
    return over_budget


def advise_gate_runtime_budget(over_budget: list[dict]) -> None:
    """Non-blocking stderr advisory for gates that passed but exceeded the
    gate-baseline runtime budget. Pairs with the retro gate-baseline-runtime
    waste lens (section-guide / phase-aware-efficiency)."""
    if not over_budget:
        return
    budget = over_budget[0]["budget_seconds"]
    names = ", ".join(
        f"{r['phase']}:{r['command'][:60]} {r['elapsed_seconds']:.1f}s"
        for r in over_budget
    )
    print(
        f"ADVISORY: gate-baseline runtime over budget (> {budget:.0f}s): {names}. "
        "A gate that PASSES but is slow by design is gate-baseline / code-quality "
        "debt, not 'necessary safety cost' — classify it in the retro's "
        "gate-baseline-runtime waste lens (route to the gate-implementation "
        "owner), or raise CHARNESS_GATE_RUNTIME_BUDGET_SECONDS if the cost is "
        "accepted. Note: the host pre-push hook runs as its own process and is "
        "NOT measured here.",
        file=sys.stderr,
    )


def attach_gate_runtime_advisory(payload: dict) -> None:
    """Resolve the budget, evaluate the executed gates, attach the verdict to the
    durable JSON ``payload``, and emit the non-blocking stderr advisory — one call
    so the closeout entrypoint stays within its function-length budget."""
    budget = resolve_gate_runtime_budget_seconds()
    over_budget = evaluate_gate_runtime_budget(
        payload["executed_commands"], budget_seconds=budget
    )
    payload["gate_runtime_advisory"] = {
        "budget_seconds": budget,
        "over_budget": over_budget,
    }
    advise_gate_runtime_budget(over_budget)


def resolve_overslice_artifact_run_threshold() -> int:
    """Override-able threshold for the over-slicing advisory: how many consecutive
    artifact-only commits read as process churn (spec achieve-efficiency, B).
    Floor of 2 — a single artifact-only commit is never churn."""
    raw = os.environ.get("CHARNESS_OVERSLICE_ARTIFACT_RUN")
    if raw is None:
        return DEFAULT_OVERSLICE_ARTIFACT_RUN
    try:
        return max(2, int(raw))
    except ValueError:
        return DEFAULT_OVERSLICE_ARTIFACT_RUN


def trailing_artifact_only_run(commit_path_lists: list[list[str]]) -> int:
    """Count the leading run (most-recent-first) of commits whose changed paths are
    ALL under ``charness-artifacts/`` — the operational-artifact churn signal
    (meaningful-slice-cadence: frequent artifact-only commits are process churn,
    not progress). A commit touching any code/skill/doc path breaks the run."""
    run = 0
    for paths in commit_path_lists:
        if paths and all(p.startswith("charness-artifacts/") for p in paths):
            run += 1
        else:
            break
    return run


def _recent_commit_path_lists(repo_root: Path, max_commits: int) -> list[list[str]]:
    """Per-commit changed-path lists for the last ``max_commits`` commits,
    most-recent-first. Degrades to ``[]`` when the git command fails (e.g. not a
    git repo). Matches the sibling ``_added_vs_base`` returncode-only pattern: the
    closeout context is always a git repo with git present."""
    log = subprocess.run(
        ["git", "log", "-n", str(max_commits), "--format=%H"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if log.returncode != 0:
        return []
    result: list[list[str]] = []
    for sha in log.stdout.split():
        show = subprocess.run(
            ["git", "show", "--pretty=format:", "--name-only", sha],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if show.returncode != 0:
            break
        result.append([line for line in show.stdout.splitlines() if line.strip()])
    return result


def over_slice_run(repo_root: Path) -> tuple[int, int]:
    """The over-slice run value ``advise_over_slicing`` decides on, plus its
    threshold, exposed as ONE computation so the E1 closeout-telemetry record
    (spec achieve-efficiency, E) stores the same number the advisory prints — no
    second, drifting calculation."""
    threshold = resolve_overslice_artifact_run_threshold()
    run = trailing_artifact_only_run(
        _recent_commit_path_lists(repo_root, max_commits=threshold + 1)
    )
    return run, threshold


def advise_over_slicing(repo_root: Path) -> None:
    """Non-blocking advisory (spec achieve-efficiency, B): a run of consecutive
    charness-artifacts/-only commits is over-slicing churn. Enabled by default;
    the threshold tunes via ``CHARNESS_OVERSLICE_ARTIFACT_RUN``. Reads git
    directly and degrades silently when the git command fails (not a git repo)."""
    run, threshold = over_slice_run(repo_root)
    if run < threshold:
        return
    print(
        f"ADVISORY: {run} consecutive charness-artifacts/-only commits — frequent "
        "artifact-only commits are process churn, not progress. Fold artifact / "
        "current-pointer updates into the meaningful unit they support, and do not "
        "re-fire critique or broad proof within one unchanged slice intent "
        "(meaningful-slice-cadence). Update `Current slice intent:` in the goal "
        "frame when the intent actually changes, not per commit.",
        file=sys.stderr,
    )
