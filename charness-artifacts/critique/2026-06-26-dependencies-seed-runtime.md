# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a small local-only cleanup that converts two `seed_dependencies.py`
subprocess behaviors to in-process `main()` calls.

## Failure Angles

- Boundary proof: converting all calls would weaken evidence for writing,
  overwrite refusal, and invalid-input behavior.
- Recommendation path: plugin fallback discovery depends on environment, so the
  in-process test must clear the disabling env var explicitly.
- SystemExit handling: mutually exclusive input errors should remain real CLI
  proof instead of being hidden by helper behavior.

## Counterweight Pass

- Real subprocess proof remains for explicit write, refusal without `--force`,
  and explicit-plus-recommendation rejection.
- The converted tests still exercise argparse, JSON stdout, and return-code
  behavior through `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_setup_seed_dependencies.py | action: fix | note: subprocess calls dropped from 7 to 5 while retaining write/refusal/error CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_setup_seed_dependencies.py | action: defer | note: further reduction requires separating setup subprocesses from the behavior under assertion

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this narrow conversion retained real subprocess smokes for the
meaningful CLI boundaries and passed deterministic focused proof.
