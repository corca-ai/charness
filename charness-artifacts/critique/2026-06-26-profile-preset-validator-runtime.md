# Critique Review
Date: 2026-06-26

## Decision Under Review

Convert three simple profile/preset validator failure tests from subprocess
execution to direct validator function calls.

## Failure Angles

- Command proof: parser/bootstrap behavior for those exact error cases is no
  longer exercised.
- Error fidelity: direct exceptions must preserve the same operator-facing
  message fragments.
- Boundary creep: adapter validation in the same file is slower but more
  boundary-sensitive.

## Counterweight Pass

- The direct calls use the real `validate_profile()` and `validate_preset()`
  functions against temp files.
- The tests still assert the same message fragments.
- Gitignored-file and adapter-validation command tests remain subprocess-based.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_profile_and_preset_validation.py | action: fix | note: three pure validator subprocesses were removed without touching adapter command tests
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_profile_and_preset_validation.py | action: defer | note: adapter validation remains a separate boundary-sensitive optimization target

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this conversion retained same-file command tests and passed
deterministic focused proof.
