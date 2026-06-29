#!/usr/bin/env python3

"""Outcome-grade wiring for the A/B efficiency harness (run_skill_efficiency_ab.py).

Kept in its own module so the harness stays under its length budget and the OUTCOME
layer (grade_skill_outcome.py) is bolted on through one narrow seam: resolve a per-eval
assertion set, grade each preserved evidence bundle, aggregate per arm, and render the
report section folded into the A/B report.

Why this exists: an efficiency number is trustworthy only ALONGSIDE an outcome check —
a leaner token/time number can just mean an arm did LESS. Folding the discriminating
per-eval grade next to the deltas is what makes the comparison honest (methodology spec
`charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md`
§ "Evaluation Ownership + the Outcome Gap").

Advisory, never a gate (mirrors both tools): no assertion set -> skipped-with-reason,
never an error; deterministic checks grade for free; judge-kind needs --judge-cmd
(ask-before-run spend) and is SKIPPED otherwise. The grader's offline self-test gates
grading exactly like the A/B instrument self-test gates the live matrix.
floor-addition-restraint: advisory measurement only, no new blocking floor added.
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

import grade_skill_outcome

# A grade failure on one bundle must never drop the arm: these are the realistic
# faults (missing/garbled observed packet, a malformed assertion set surfacing late,
# or a `regex: true` pattern that slipped past the schema check -> re.error, which is
# NOT a ValueError subclass).
_GRADE_FAULTS = (OSError, ValueError, KeyError, json.JSONDecodeError, re.error)


def resolve_assertion_set(spec_path: Path | str) -> dict | None:
    """The per-eval outcome assertion set is the sibling `outcome-assertions.json` next
    to the spec. Absent (most evals today) -> None: outcome grading is skipped for that
    arm and reported honestly. A malformed set raises (fail fast, before more spend)."""
    candidate = Path(spec_path).parent / "outcome-assertions.json"
    if not candidate.is_file():
        return None
    return grade_skill_outcome.load_assertion_set(candidate)


class GraderGate:
    """Runs the grader's offline self-test at most once; outcome grading is only trusted
    when it passes (a grader that can't rank good>bad must never produce a verdict we'd
    trust — mirrors run_skill_efficiency_ab's instrument self-test gate). The matrix
    already spent by grade time, so a failure just skips grading-with-reason."""

    def __init__(self, selftest=grade_skill_outcome.selftest):
        self._selftest = selftest
        self.ready: bool | None = None

    def ok(self) -> bool:
        if self.ready is None:
            self.ready = self._selftest() == 0
            if not self.ready:
                print("  [outcome] grader self-test failed; skipping outcome grading", file=sys.stderr)
        return self.ready


def grade_arm(preserved_dirs: list[Path], assertion_set: dict | None, judge_fn, gate: GraderGate,
              out_name: str = "outcome-grade.md") -> list[dict]:
    """Grade each preserved bundle dir against the assertion set, writing a per-run
    report alongside the bundle and returning the list of grade() dicts. No assertion
    set or an untrustworthy grader -> empty list (grading skipped). One bundle's grade
    failure is logged and skipped, never fatal to the arm."""
    outcomes: list[dict] = []
    if assertion_set is None or not gate.ok():
        return outcomes
    for bundle_dir in preserved_dirs:
        try:
            bundle = grade_skill_outcome.load_bundle(bundle_dir)
            result = grade_skill_outcome.grade(assertion_set, bundle, judge_fn)
            (Path(bundle_dir) / out_name).write_text(
                grade_skill_outcome.build_report(result) + "\n", encoding="utf-8")
            outcomes.append(result)
        except _GRADE_FAULTS as exc:
            print(f"  [outcome] grade failed for {bundle_dir}: {exc}", file=sys.stderr)
    return outcomes


def aggregate_arm(outcomes: list[dict], assertion_set: dict | None, attempted: int = 0) -> dict:
    """Per-arm outcome summary: mean [min-max] pass_rate over runs that produced a
    scored rate, plus skipped/error totals (so the report shows whether the live judge
    ran). `assertion_set` is carried so the report names 'no set' honestly vs a real 0.
    `attempted` is the count of bundles grading was actually run on (set present + grader
    trusted); `grade_failed = attempted - graded` surfaces bundles that errored out of
    grading, so an all-failed arm cannot read as a clean empty (vs 'nothing to grade')."""
    summary: dict = {
        "eval_id": assertion_set["evalId"] if assertion_set else None,
        "runs_graded": len(outcomes),
        "grade_failed": max(0, attempted - len(outcomes)),
        "pass_rate": None,
        "skipped": sum(o.get("skipped", 0) for o in outcomes),
        "errors": sum(o.get("errors", 0) for o in outcomes),
    }
    rates = [o["pass_rate"] for o in outcomes if o.get("pass_rate") is not None]
    if rates:
        summary["pass_rate"] = {
            "mean": round(statistics.mean(rates), 3),
            "min": min(rates), "max": max(rates), "n": len(rates),
        }
    return summary


def render_outcome_section(outcome_by_arm: dict | None) -> str:
    """Markdown 'Outcome grade' block folded into the A/B report (leading blank line so
    it appends cleanly). Empty string when no arm has an assertion set — nothing to add.
    Kept separate from the matcher pass_rate table: this grades discriminating per-eval
    assertions, the matcher scores routing/coverage."""
    if not outcome_by_arm or all(s.get("eval_id") is None for s in outcome_by_arm.values()):
        return ""
    lines = [
        "",
        "## Outcome grade (advisory)",
        "",
        "Per-eval discriminating assertions graded over each run's evidence bundle "
        "(separate from the matcher pass_rate above, which scores routing/coverage). "
        "Pairs the efficiency deltas with whether the work was actually done — a leaner "
        "number can just mean an arm did less.",
        "",
        "| arm | outcome pass_rate (mean [min–max]) | runs graded | judge skipped | errors |",
        "| --- | --- | --- | --- | --- |",
    ]
    for arm, summary in outcome_by_arm.items():
        if summary.get("eval_id") is None:
            lines.append(f"| {arm} | no outcome-assertions.json — skipped | n/a | n/a | n/a |")
            continue
        rate = summary.get("pass_rate")
        cell = "n/a" if not rate else f"{rate['mean']:g} [{rate['min']:g}–{rate['max']:g}]"
        graded = str(summary["runs_graded"])
        if summary.get("grade_failed"):
            graded += f" (+{summary['grade_failed']} grade-failed)"
        lines.append(f"| {arm} | {cell} | {graded} | {summary['skipped']} | {summary['errors']} |")
    lines.append("")
    lines.append(
        "- Deterministic checks grade for free; judge-kind assertions are SKIPPED unless "
        "`--judge-cmd` (ask-before-run spend) ran — a high `judge skipped` count means the "
        "live judge did not run.")
    return "\n".join(lines)
