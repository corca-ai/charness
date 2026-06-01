# Issue 272 Mutation Report Clarity Debug
Date: 2026-06-01
Source: GitHub issue #272

## Problem

The scheduled mutation issue reported `Status: FAIL` while also reporting
`Killed: 78`, `Survived: 0`, and a `100.0%` reachable score. The single status
line made the report read like a mutation-score failure even though the actual
failing condition was the changed-line coverage/selection blocker.

## Correct Behavior

Given a mutation run whose reachable killed/survived score passes, when a
non-score blocking signal fails the gate, then the summary should show the
overall gate status separately from the mutation-score result and from the
blocking-signal result.

## Observed Facts

- Issue #272 body reports `Status: FAIL (100.0% reachable score vs 80%
  threshold)`, `Killed: 78`, and `Survived: 0`.
- The same body lists a blocking signal: changed lines were left
  test-uncovered, or eligible changed files were dropped before mutation.
- `scripts/check_mutation_score.py` rendered one overloaded status row:
  `Status: **{status}** ({score}% reachable score vs {threshold}% threshold)`.
- `mutation_metrics` folded changed-line blockers into `score_passes`, so the
  overall `status` became `FAIL` even when the killed/survived score itself
  passed.
- `skills/public/quality/references/mutation-testing.md` already states the
  changed-line signal is distinct from a score break.

## Reproduction

Use the existing changed-line blocker fixture in
`tests/quality_gates/test_quality_mutation_score_validity.py`:

```bash
pytest -q tests/quality_gates/test_quality_mutation_score_validity.py::test_check_mutation_score_fails_when_changed_lines_uncovered
```

Before the fix, the generated summary had one status row that combined
`FAIL` with the passing score text. After the fix, the same fixture shows:

- `Status: **FAIL**`
- `Mutation score: **PASS** (100.0% reachable score vs 50% threshold)`
- `Blocking signals: **FAIL** (changed-line coverage/selection)`

## Candidate Causes

- The scoring function had no separate rendered concept for the score result.
- The report had no separate rendered concept for non-score blockers.
- The issue auto-file body was missing the explanatory reference text.

## Hypothesis

If the summary renders `Mutation score:` and `Blocking signals:` as separate
rows, while keeping the top-level status and exit code unchanged, then issue
reports like #272 will be read as "score passed, blocker failed" instead of
"survived mutants caused failure."

## Verification

- PASS: `pytest -q tests/quality_gates/test_quality_mutation_score_validity.py
  tests/quality_gates/test_check_mutation_score_partial.py` (30 passed).
- PASS: `ruff check scripts/check_mutation_score.py
  tests/quality_gates/test_quality_mutation_score_validity.py`.
- PASS: `python3 -m py_compile scripts/check_mutation_score.py`.
- Export sync run: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

## Root Cause

The mutation summary collapsed two different truths into one line: overall gate
status and killed/survived score. The gate was correct to fail because the
changed-line blocker fired, but the rendered summary made that failure look like
a score failure even when no Python mutants survived.

## Detection Gap

- mutation summary rendering | no test asserted the "score passes, blocker
  fails" report shape | added assertions for separate `Mutation score: PASS`
  and `Blocking signals: FAIL` rows.
- quality reference | docs described the distinction but did not show how to
  read the rendered summary | added a reference note explaining the three rows.

## Sibling Search

- Mental model: one status line was treated as enough for a multi-axis gate.
- same layer: `check_js_mutation_score.py` still renders one status line, but
  its blockers are JS-specific and not the #272 changed-line confusion; decision:
  diagnostic-only for this slice; proof: not inspected.
- abstraction up: auto-filed mutation issues consume this summary directly;
  decision: fixed by changing the summary producer; proof: issue #272 body is
  generated from the ambiguous producer text.
- specialization down: changed-line blocker details already list exact targets;
  decision: no change here; proof: #272 body includes changed-line proof targets.

## Seam Risk

- Interrupt ID: issue-272-mutation-report-clarity
- Risk Class: none
- Seam: GitHub scheduled workflow issue body consumes local summary markdown.
- Disproving Observation: none; the local summary producer is the rendered issue
  source.
- What Local Reasoning Cannot Prove: the next scheduled workflow will generate
  a new issue body until this commit is pushed and the scheduled run executes.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md

## Prevention

Keep overall status, mutation-score result, and non-score blockers separate in
the summary. A passing killed/survived score can coexist with an overall failed
gate when changed-line coverage, sampling, or manifest proof fails.
