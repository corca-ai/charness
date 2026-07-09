# Critique Review
Date: 2026-07-09

## Decision Under Review

Standing-test economics inventory bucket repair: classify nested CLI test files
into standing-only, mixed release_only/standing, and all-release-only buckets,
including function-level and alias-based pytest release markers, while retaining
legacy `nested_cli_release_only_*` payload keys.

Packet Consumed: `n/a (bounded reviewer prompts used the committed diff and live inventory output directly)`

## Failure Angles

- Marker semantics: direct `pytest.mark.release_only` was not enough once the
  inventory claimed structural pytest marker parsing; alias imports needed the
  same handling.
- Public contract: new fields had to be additive, with old compatibility keys
  preserved for downstream consumers.
- Operability: wording must not keep saying module-only after function-level
  release-only files are included in the all-release-only bucket.

## Counterweight Pass

- Act Before Ship: none after alias handling and all-release-only wording were
  fixed.
- Bundle Anyway: one alias regression test was added; broader matrix expansion
  is confidence work, not a blocker.
- Over-Worry: removing old `nested_cli_release_only_*` compatibility keys would
  be churn and is intentionally not done.
- Valid but Defer: `standing_test_economics_lib.py` is near its length ceiling;
  the next nontrivial addition should split another helper instead of growing it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/surface_marker_lib.py:39 | action: fix | note: release-only alias markers needed structural parsing before the bucket split could be trusted
- F2 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_standing_test_economics.py:334 | action: fix | note: alias marker tests now cover module-level and function-level paths
- F3 | bin: over-worry | evidence: moderate | ref: skills/public/quality/scripts/standing_test_economics_lib.py:355 | action: document | note: legacy nested_cli_release_only fields remain as compatibility aliases
- F4 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/standing_test_economics_lib.py | action: defer | note: module is at 341/360 code lines and should not take the next nontrivial addition

## Reviewer Tier Evidence

- Requested tier: high-leverage where available; runtime exposed explicit model fields only.
- Requested spawn fields: model=gpt-5.4-mini, reasoning_effort=medium.
- Host exposure state: requested_fields_sent
- Application state: host accepted reviewer and counterweight spawns and returned independent reports.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: quality skill inventory scripts and marker parser.
- Consumer: quality reviewers deciding whether nested CLI cost belongs to standing tests, release-only tests, or mixed files.
- Owning surface: public quality skill package plus generated plugin export.
- Verdict: owned-correctly
