# Critique Review
Date: 2026-06-26

## Decision Under Review

Convert three `validate_surfaces.py` manifest-validation tests to direct
`load_surfaces()` calls.

## Failure Angles

- Command proof: parser/bootstrap behavior for those cases no longer runs.
- Message fidelity: direct `SurfaceError` assertions must preserve the same
  failure text fragments.
- Scope creep: command-routing tests in the file should remain subprocess-based.

## Counterweight Pass

- Duplicate-id and bare-recursive validate-surfaces command smokes remain.
- Direct calls assert the same `SurfaceError` text fragments.
- check_changed_surfaces/select_verifiers routing tests were left at the CLI
  boundary.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_surface_obligations.py | action: fix | note: three pure manifest-validation subprocesses were removed
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_surface_obligations.py | action: defer | note: keep command-routing tests as subprocess proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this conversion retained command-routing tests and passed
deterministic focused proof.
