# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a small local-only cleanup that converts two
`seed_usage_episodes_adapter.py` subprocess tests to in-process `main()` calls.

## Failure Angles

- Boundary proof: converting file-write and overwrite-refusal tests would weaken
  the useful shipped CLI evidence.
- Schema proof: dry-run output still needs to be captured and validated exactly.
- Isolation: monkeypatched `sys.argv` and captured streams could leak between
  tests if not pytest-scoped.

## Counterweight Pass

- Real subprocess proof remains for initial adapter write and overwrite
  refusal.
- The converted tests still exercise argparse and stdout through `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_setup_seed_usage_episodes.py | action: fix | note: subprocess calls dropped from 5 to 3 while retaining write/refusal CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_setup_seed_dependencies.py | action: defer | note: dependency recommendation seeding needs separate proof review before conversion

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this two-test conversion retained real subprocess smokes for the
file-write boundary and passed deterministic focused proof.
