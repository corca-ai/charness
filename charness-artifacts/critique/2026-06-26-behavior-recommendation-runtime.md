# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts two `recommend_behavior_test.py`
success-path tests to in-process `main()` calls.

## Failure Angles

- CLI bootstrap: converting every test would remove proof that the script can be
  invoked as a command.
- Error fidelity: argparse failures must still surface the expected stderr text
  and exit code.
- Output fidelity: converted success paths must still exercise argparse, stdout,
  JSON parsing, markdown rendering, and return codes.

## Counterweight Pass

- The `--state executed` missing-report case remains a real subprocess and
  continues to prove CLI stderr behavior.
- Converted paths still exercise argparse through pytest-scoped `sys.argv`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_behavior_recommendation.py | action: fix | note: subprocess calls dropped from 3 to 1 while retaining argparse-error CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_quality_behavior_recommendation.py | action: defer | note: do not convert the remaining subprocess unless another success CLI smoke is added

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this success-path conversion retained an argparse-error subprocess
smoke and passed deterministic focused proof.
