# Critique Review
Date: 2026-06-26

## Decision Under Review

Convert the pursue-ready return-code test in `test_goal_head_freshness.py` from
two subprocess launches to the existing in-process `check_goal_artifact.main()`
helper.

## Failure Angles

- Command proof: pursue-ready parser behavior might be less directly covered.
- Return-code fidelity: the helper must still assert both success and failure
  return codes.
- Output capture: stdout JSON must still be read from the actual main() output.

## Counterweight Pass

- The helper sets `sys.argv`, calls `main()`, and captures stdout/stderr.
- The test still asserts return codes and JSON payloads for both ready and
  unshaped paths.
- Separate CLI subprocess smokes remain for head freshness and missing goal path.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_goal_head_freshness.py | action: fix | note: pursue-ready subprocess launches dropped from 2 to 0 while return-code assertions remained
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_goal_head_freshness.py | action: defer | note: keep remaining CLI smokes for parser/error command proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this conversion used an existing main() helper and retained command
smokes.
