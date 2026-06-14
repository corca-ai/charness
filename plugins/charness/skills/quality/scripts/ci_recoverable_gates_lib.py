"""CI-recoverability triage lens for costly local standing gates.

The existing `ci_local_gate_parity_lib` is the *local-proof* guardrail: it flags
CI steps that run proof the local gate does not, so a required failure can always
appear locally first. This module is the explicit **counterweight**: given the
repo's costly local standing gates (ranked by measured wall-clock) and its CI
workflow steps, it flags the gates whose proof **CI fully re-runs** as candidates
to move off the local hot path — and, crucially, it **never** recommends moving a
gate whose proof CI does *not* re-run (those are reported as `keep-local`).

It is advisory-only (no blocking floor): the operator decides whether to move a
candidate. The "CI fully re-runs this proof" judgment is a portable heuristic —
it matches a gate's distinctive label/script token against CI `run:` step text
(word-boundary), and surfaces the matching CI step + its gate-policy so the
operator can confirm. The heuristic's blind spots are declared so a consumer
answers the interpretation question before acting (advisory-interpretation
contract).
"""
from __future__ import annotations

import re
from typing import Any

# Generic words that would match too broadly if treated as a gate's distinctive
# token. A gate labelled with only one of these is matched by its other stems.
GENERIC_STEMS = frozenset(
    {"node", "npm", "run", "ci", "test", "check", "build", "lint", "setup", "install", "python", "python3"}
)

INTERPRETATION = {
    "measures": (
        "for each costly local standing gate (ranked by measured wall-clock), whether a CI "
        "workflow `run:` step re-runs the same proof token (script path or tool label)"
    ),
    "proxy_for": "which costly local gates CI already backstops, so they are safe to move off the local hot path",
    "blind_spots": (
        "token-identity matching cannot prove two invocations exercise the *same* proof "
        "(different flags/scope/inputs can diverge), and it cannot see a CI step gated behind "
        "an `if:`/path filter that would skip the gate for the change in hand; a match is a "
        "candidate to confirm, not a proven equivalence"
    ),
    "interpretation_question": (
        "does the matched CI step actually re-run THIS gate's full proof for the changes that "
        "reach main, so moving it off the local hot path loses no required signal?"
    ),
}


def _label_stems(label: str) -> set[str]:
    """Distinctive match tokens for a gate label, minus over-generic words."""
    base = label.strip()
    if not base:
        return set()
    variants = {
        base,
        base.replace("-", "_"),
        base.replace("_", "-"),
        base.replace("-", "").replace("_", ""),
        # a tool+subcommand gate labelled `ruff-check` must match the CI command
        # `ruff check`; word-boundary matching keeps the space form precise.
        base.replace("-", " ").replace("_", " "),
    }
    return {stem for stem in variants if len(stem) >= 4 and stem.lower() not in GENERIC_STEMS}


def _stem_in_text(stem: str, text: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(stem)}(?![\w-])", text) is not None


def ci_step_corpus(workflows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten CI workflows into a list of run-step records for matching.

    Each workflow dict is `{"workflow": <path>, "data": <parsed yaml>,
    "gate_policy": <policy|None>}`. Only steps with a `run:` string contribute a
    proof token (a `uses:`-only setup step runs no gate).
    """
    corpus: list[dict[str, Any]] = []
    for workflow in workflows:
        data = workflow.get("data")
        if not isinstance(data, dict):
            continue
        jobs = data.get("jobs")
        if not isinstance(jobs, dict):
            continue
        for job_id, job in jobs.items():
            if not isinstance(job, dict):
                continue
            steps = job.get("steps")
            if not isinstance(steps, list):
                continue
            for step in steps:
                if not isinstance(step, dict):
                    continue
                run = step.get("run")
                if not isinstance(run, str) or not run.strip():
                    continue
                corpus.append(
                    {
                        "workflow": workflow.get("workflow"),
                        "job": job_id,
                        "name": step.get("name"),
                        "run": run,
                        "if": step.get("if"),
                        "gate_policy": workflow.get("gate_policy"),
                    }
                )
    return corpus


def _match_steps(label: str, corpus: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stems = _label_stems(label)
    if not stems:
        return []
    matched: list[dict[str, Any]] = []
    for step in corpus:
        run_text = step["run"]
        if any(_stem_in_text(stem, run_text) for stem in stems):
            matched.append(
                {
                    "workflow": step["workflow"],
                    "job": step["job"],
                    "name": step.get("name"),
                    "if": step.get("if"),
                    "gate_policy": step.get("gate_policy"),
                }
            )
    return matched


def classify_gates(
    gates: list[dict[str, Any]], corpus: list[dict[str, Any]]
) -> dict[str, Any]:
    """Classify each gate as a CI-recoverable candidate or keep-local.

    `gates` is a list of `{"label": str, "wall_clock_ms": int|None}`. A gate is a
    candidate only when a CI run step re-runs its proof token; everything else is
    `keep-local` (never recommended for moving — the safety counterweight).
    Candidates are ranked by wall-clock descending (unknown wall-clock sorts last).
    """
    candidates: list[dict[str, Any]] = []
    keep_local: list[dict[str, Any]] = []
    for gate in gates:
        label = str(gate.get("label", ""))
        if not label:
            continue
        wall_clock = gate.get("wall_clock_ms")
        wall_clock = wall_clock if isinstance(wall_clock, int) else None
        matched = _match_steps(label, corpus)
        record = {"label": label, "wall_clock_ms": wall_clock}
        if matched:
            record["ci_steps"] = matched
            record["ci_gate_policies"] = sorted({m["gate_policy"] for m in matched if m["gate_policy"]})
            candidates.append(record)
        else:
            keep_local.append(record)
    candidates.sort(key=lambda item: (item["wall_clock_ms"] is None, -(item["wall_clock_ms"] or 0), item["label"]))
    keep_local.sort(key=lambda item: (item["wall_clock_ms"] is None, -(item["wall_clock_ms"] or 0), item["label"]))
    return {"candidates": candidates, "keep_local": keep_local}


def gates_from_runtime_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the gate universe (label + wall-clock) from a runtime_budget_lib report.

    Uses the recent-median elapsed as the stable wall-clock signal. The universe is
    every budgeted gate plus every sampled hot spot, de-duplicated by label; a
    budgeted gate with no sample yet carries wall_clock_ms=None.
    """
    by_label: dict[str, int | None] = {}
    for entry in report.get("runtime_hotspots") or []:
        label = entry.get("label")
        if isinstance(label, str) and label:
            median = entry.get("median_recent_elapsed_ms")
            by_label[label] = median if isinstance(median, int) else None
    for entry in report.get("checked") or []:
        label = entry.get("label")
        if isinstance(label, str) and label and label not in by_label:
            median = entry.get("median_recent_elapsed_ms")
            by_label[label] = median if isinstance(median, int) else None
    return [{"label": label, "wall_clock_ms": wall_clock} for label, wall_clock in by_label.items()]
