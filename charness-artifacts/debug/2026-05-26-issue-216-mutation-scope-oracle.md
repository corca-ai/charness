# Issue 216 Mutation Scope Oracle Debug
Date: 2026-05-26
Source: GitHub issue #216, mutation workflow run 26415240334

## Problem

The scheduled mutation workflow failed even though the reachable Python score
was above threshold:

- score: 92.2% vs 80% threshold
- executable: 102/102
- blocking signal: `Scope gaps (uncovered sampled mutants): 1`

The sampled file manifest marked `scripts/setup_artifact_policy_lib.py` fully
mutation-line covered (`mutable: 103`, selected executable count included it),
but the post-init filter skipped one mutant as `Filtered uncovered mutation
line`.

## Correct Behavior

The sampler and post-init Cosmic Ray filter must use the same mutation-line
coverage classifier. A mutant selected as covered by the sampler must not later
be counted as an uncovered sampled mutant by the filter.

## Observed Facts

- `scripts/setup_artifact_policy_lib.py:34` was the only skipped uncovered
  sampled mutant in run 26415240334.
- The mutant operator was `core/ReplaceAndWithOr` inside
  `detect_charness_artifact_policy`.
- Line 34 is inside the multi-line list comprehension assigned on line 33.
- The coverage artifact had line 33 in `executed_lines`; the contexts payload
  also named line 34.

## Reproduction

Downloaded the workflow artifact for run 26415240334 and compared the sample
manifest with `mutation-report/python/mutants.jsonl`. The sampled file manifest
classified `scripts/setup_artifact_policy_lib.py` as mutation-line covered, but
the filter report classified the line-34 mutant as uncovered.

## Candidate Causes

- The sampler and filter implemented different mutation coverage oracles.
- The coverage artifact lacked execution for the statement (ruled out: line 33
  executed, and line 34 appeared in coverage contexts).
- The score checker misread the report (ruled out: it correctly treated one
  uncovered sampled mutant as fatal).

## Hypothesis

If sampler and filter both classify mutation-line coverage with the same
statement-span helper, then a continuation-line mutant in an executed multi-line
statement is selected and filtered consistently, and the false scope gap
disappears.

## Verification

- Added `scripts/mutation_line_coverage_lib.py` and routed both sampler and
  filter through it.
- Added regression coverage proving a covered multi-line continuation mutant is
  not filtered as uncovered.
- Re-ran the committed-head mutation gate: Python passed at 94.2% reachable
  score with `Scope gaps (uncovered sampled mutants): 0`; JS passed at 91.9%.

## Root Cause

The sampler and the post-init filter used different coverage oracles.

- `scripts/mutation_sampling_lib.py` treated mutants on continuation lines of
  an executed multi-line statement as covered by using statement spans.
- `scripts/filter_cosmic_ray_mutants.py` checked only exact membership in
  `coverage.json` `executed_lines`.

In run 26415240334, the skipped mutant was:

- `scripts/setup_artifact_policy_lib.py:34`
- `detect_charness_artifact_policy`
- `core/ReplaceAndWithOr`

Line 34 is inside the multi-line list comprehension assigned on line 33. The
coverage artifact had line 33 in `executed_lines`, and the contexts payload
also named line 34, but the filter ignored the statement-span rule that the
sampler already used.

## Detection Gap

The existing tests covered both sides separately:

- sampler statement-span behavior in
  `tests/quality_gates/test_mutation_sampling_line_coverage.py`
- exact-line filter behavior in
  `tests/quality_gates/test_quality_mutation_testing.py`

No test asserted that a Cosmic Ray mutation location accepted by the sampler is
also accepted by the filter.

## Sibling Search

Mental model: coverage-aware sampling and filtering can each implement a
reasonable local rule, but any divergence becomes a false fatal scope gap.

Scanned sibling patterns:

- annotation-union skip and trivial-entry-guard skip are still duplicated
  between sampler and filter; they currently share the same source helpers in
  `scripts/filter_cosmic_ray_mutants.py`, so they are lower risk for this
  slice.
- score summary correctly treats scope gaps as fatal; no summary change is
  needed.
- sample manifest changed-file scope gaps already use separate changed-line
  logic and are not the same bug.

## Prevention

The fix moves statement-span mutation coverage classification into
`scripts/mutation_line_coverage_lib.py` and makes both sampler and filter use
the shared helper. The regression test
`test_filter_uses_statement_spans_for_multiline_mutation_coverage` verifies
that a covered multi-line continuation mutant is not filtered as uncovered.
