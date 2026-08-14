#!/usr/bin/env python3
"""Corpus-discovery runner for the improvement-disposition gate (rung 1).

Calibration is **discovery, not "assert 0"**: run the real deterministic floor
(``check_complete_evidence``) over every completed goal artifact and report what
it would do, so a human can confirm:

- pre-rule goals (Created < the rule date) are grandfathered — 0 deterministic
  refusals. **This 0 is structural, not a finding.** ``apply_disposition_rungs``
  returns at ``if not in_scope: return`` before any ``disposition_blank`` can be
  set, so "pre-rule" and "rung-1a refused" are mutually exclusive by control
  flow: ``pre_rule_rung1a_refusals`` is 0 for every possible corpus, and
  ``--fail-on-pre-rule-refusal`` cannot return 1 *while that ordering holds*. It
  trips on ANY writer of the ``disposition_blank`` key reachable for a pre-rule
  goal — a rung reordered above the scope check is one such shape, not the only
  one. Reported with ``pre_rule_refusal_detectability`` so the number states what
  produced it rather than reading as confirmation the grandfather was exercised.
  The flag is a TRIPWIRE, and the situation it was written for is the LEAK, not
  the current corpus: ``tests/quality_gates/test_pre_rule_refusal_tripwire.py``
  forces the mutually-exclusive pair through ``summarize`` and pins that the
  count reaches 1 and the flag's exit path returns 1. That probe is why this is
  an armed guard rather than one nobody has ever seen work;
- the floor is **not inert** — in-scope goals that lack a bound
  ``Disposition review:`` line or carry a blank ``## Auto-Retro`` are surfaced
  (these are the cases a post-rule closeout must now satisfy).

Exit code is always 0 unless ``--fail-on-pre-rule-refusal`` is passed and a
*pre-rule* goal is refused (which would mean the grandfather leaked). The runner
never gates a closeout itself; it is a read-only audit/observation surface.

**Every count states the population it selects.** ``in_scope`` is the
*fail-closed* population: ``disposition_gate_applies`` treats a missing or
malformed ``Created:`` as in-scope so a goal cannot dodge both rungs by
corrupting one line. That is the right gate behaviour and the wrong thing to
report as a bare number — an ``in_scope`` of N answers "how many goals does the
floor fire on", not "how many goals the floor fires on were dated into it", and
those two diverge silently the moment a goal loses its ``Created:`` line. So the
summary splits it:

- ``in_scope_dated`` — carries a parseable ``Created`` on/after the rule date.
  This is the DATED DENOMINATOR: goals genuinely inside the floor's stated
  window.
- ``in_scope_undatable`` — in scope ONLY because the date could not be read.
  A non-zero value here is not a floor result; it is a corpus defect, and
  ``in_scope_undatable_goals`` names each one so it can be repaired rather than
  absorbed into a headline number.

``in_scope == in_scope_dated + in_scope_undatable`` by construction.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import runpy
from pathlib import Path

GOAL_DIR = "charness-artifacts/goals"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_yaml_output():
    """Reach the repo-level YAML emitter from BOTH the authoring and installed layouts.

    This module loads its siblings by relative path rather than through
    `skill_runtime_bootstrap`, so the ancestor walk is the one spelling that finds
    `scripts/yaml_output.py` at the repo root here and at the plugin root once
    exported.
    """
    helper = next(
        (
            ancestor / "scripts" / "yaml_output.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "scripts" / "yaml_output.py").is_file()
        ),
        None,
    )
    if helper is None:
        raise ImportError("scripts/yaml_output.py not found")
    return runpy.run_path(str(helper))


emit_yaml = _load_yaml_output()["emit_yaml"]

_ce = _load("goal_artifact_closeout_evidence", "goal_artifact_closeout_evidence.py")
_disp = _load("goal_artifact_disposition", "goal_artifact_disposition.py")

_STATUS = re.compile(r"^Status:\s*(\S+)", re.MULTILINE)
_REVIEW_LINE = re.compile(
    r"^[\s>*-]*Disposition[- ]review\s*:", re.MULTILINE | re.IGNORECASE
)


def normalized_status(status: str | None) -> str | None:
    """The status token, case-folded and stripped of trailing punctuation.

    `_STATUS` captures the first whitespace-delimited token, so the corpus's
    real spellings include `COMPLETE` (followed by a parenthetical) alongside
    `complete`. A case-sensitive `== "complete"` comparison dropped such a goal
    out of EVERY reported bucket -- it is neither `completed_goals` nor
    `rows_without_status`, because its status is truthy -- so a completed,
    in-scope goal went unexamined by the fields whose whole purpose is naming
    the goals the floor fires on.
    """
    if status is None:
        return None
    folded = status.strip().rstrip(".,;:").lower()
    return folded or None


def audit_goal(repo_root: Path, path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    status_match = _STATUS.search(text)
    status = status_match.group(1) if status_match else None
    report = _ce.check_complete_evidence(repo_root, text)
    scope = report.get("disposition_scope", {})
    return {
        "goal": path.name,
        "status": status,
        # The raw token is kept for fidelity; every count keys off the normalized
        # one, so a spelling variant cannot silently leave the population.
        "status_normalized": normalized_status(status),
        "created": scope.get("created"),
        "in_scope": scope.get("in_scope"),
        "auto_retro_blank": report.get("auto_retro_blank"),
        "retro_improvements_present": report.get("retro_improvements_present"),
        "has_disposition_review_line": bool(_REVIEW_LINE.search(_disp._mask_fences(text))),
        "rung1a_block_the_blank": "disposition_blank" in report,
        "disposition_optout": report.get("disposition_optout", {}).get("reason"),
        "evidence_ok": report["ok"],
    }


def summarize(rows: list[dict]) -> dict:
    """The reported summary, as a pure function of the audited rows.

    Extracted from ``main`` so the denominator statement is assertable directly
    against the real corpus. Left inline, the only way to test the shipped
    numbers was to re-derive them in the test — which is how a summary comes to
    disagree with the rows it summarizes and no test notices.
    """
    completed = [r for r in rows if r["status_normalized"] == "complete"]
    pre_rule = [r for r in completed if r["in_scope"] is False]
    in_scope = [r for r in completed if r["in_scope"] is True]
    pre_rule_refused = [r for r in pre_rule if r["rung1a_block_the_blank"]]
    in_scope_missing_review = [r for r in in_scope if not r["has_disposition_review_line"]]
    in_scope_blank = [r for r in in_scope if r["rung1a_block_the_blank"]]
    # `created` is the PARSED date (ISO string) or None, never the raw line, so
    # `not created` is exactly "the scope verdict could not be taken from a date"
    # — the fail-closed remainder — rather than a guess about the text.
    in_scope_undatable = [r for r in in_scope if not r["created"]]
    in_scope_dated = [r for r in in_scope if r["created"]]
    # Files the glob picked up that carry no `Status:` line at all -- co-located
    # non-goal artifacts (early-close reports, host-log probes). They are audited
    # and then dropped from every count, so they are REPORTED rather than
    # silently discarded: a denominator that hides its own intake is the defect
    # this summary exists to not have.
    without_status = [r for r in rows if not r["status_normalized"]]
    # The THIRD drop bucket. Intake splits three ways, not two: no status at all,
    # a status that is not `complete`, and the completed population. Reporting
    # only the first two left `audited_files - rows_without_status -
    # completed_goals` files dropped with no field naming them -- and the reader
    # cannot tell an `active` goal (correctly excluded) from a spelling variant
    # that fell out by accident. The distinct values are listed for exactly that.
    other_status = [r for r in rows if r["status_normalized"] and r["status_normalized"] != "complete"]
    return {
        "audited_files": len(rows),
        "rows_without_status": len(without_status),
        "rows_with_other_status": len(other_status),
        "other_status_values": sorted({r["status_normalized"] for r in other_status}),
        "completed_goals": len(completed),
        "pre_rule_grandfathered": len(pre_rule),
        "in_scope": len(in_scope),
        # The three lines below are the denominator statement: what `in_scope`
        # counts, how much of it was dated into the window, and how much is in
        # scope only because a date could not be read.
        "in_scope_dated": len(in_scope_dated),
        "in_scope_undatable": len(in_scope_undatable),
        "in_scope_undatable_goals": [r["goal"] for r in in_scope_undatable],
        # Read from the constant, never derived from the audited rows. Derived, it
        # rendered `[]` on an empty corpus (no goals dir, or --completed-only with
        # no complete goals) while `in_scope_population` still referred to it, and
        # its TYPE varied str-vs-list between runs.
        "disposition_rule_date": _disp.DISPOSITION_RULE_DATE.isoformat(),
        "in_scope_population": (
            "goals whose normalized `Status:` is `complete` ONLY -- audited_files "
            "splits exactly into rows_without_status + rows_with_other_status + "
            "completed_goals -- then fail-closed: Created >= "
            "disposition_rule_date, PLUS every such goal whose Created could not "
            "be parsed (in_scope == in_scope_dated + in_scope_undatable)"
        ),
        "pre_rule_rung1a_refusals": len(pre_rule_refused),
        # COMPUTED, not a constant. As a constant this field asserted "this count
        # CANNOT be non-zero" in the one run where it IS non-zero -- the report would
        # have told the reader the tripwire's only signal was not evidence, at the
        # exact moment it fired. A field that denies the thing it accompanies is
        # the class this audit surface exists to report.
        "pre_rule_refusal_detectability": (
            "structurally 0: apply_disposition_rungs returns at `if not in_scope` "
            "before any disposition_blank is set, so pre-rule and rung-1a-refused "
            "are mutually exclusive for every corpus -- this count CANNOT be "
            "non-zero, and is therefore not evidence about the grandfather"
            if not pre_rule_refused
            else (
                "ORDERING ASSUMPTION VIOLATED: a pre-rule goal was refused by rung 1a, "
                "which control flow is supposed to make impossible -- the grandfather "
                "leaked. This count IS evidence and the tripwire is the reason you are "
                "reading it; inspect the rungs above the in-scope check. Goals: "
                + ", ".join(r["goal"] for r in pre_rule_refused)
            )
        ),
        "in_scope_blank_refusals": len(in_scope_blank),
        "in_scope_missing_disposition_review_line": [r["goal"] for r in in_scope_missing_review],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the goal corpus against the disposition floor.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root containing the goal corpus to audit.",
    )
    parser.add_argument(
        "--completed-only",
        action="store_true",
        help=(
            "Only PRINT rows for goals whose normalized Status is complete; the summary "
            "always covers every audited file."
        ),
    )
    parser.add_argument(
        "--fail-on-pre-rule-refusal",
        action="store_true",
        help="Fail if a pre-rule goal is refused by the disposition floor.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    goals_dir = repo_root / GOAL_DIR
    audited = [audit_goal(repo_root, path) for path in sorted(goals_dir.glob("*.md"))]
    # The summary always reads the FULL audited set; `--completed-only` trims the
    # printed rows, not the denominator. Summarizing the trimmed list would have
    # made `audited_files` / `rows_without_status` report the filter's output as
    # if it were the intake -- a denominator that moves with a display flag.
    summary = summarize(audited)
    rows = [r for r in audited if r["status_normalized"] == "complete"] if args.completed_only else audited
    emit_yaml({"summary": summary, "rows": rows})
    if args.fail_on_pre_rule_refusal and summary["pre_rule_rung1a_refusals"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
