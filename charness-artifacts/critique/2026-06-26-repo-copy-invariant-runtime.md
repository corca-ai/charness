# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts four synthetic
`check_test_repo_copy_invariants.py` subprocess tests to in-process `main()`
calls.

## Failure Angles

- Boundary proof: converting the current-repo test would remove useful
  script-bootstrap evidence on real data.
- Scanner fidelity: synthetic fixtures must still exercise stderr diagnostics
  and return codes through argparse.
- Value: repo-copy checks protect expensive fixture behavior, so the conversion
  must retain the guard's real entrypoint smoke.

## Counterweight Pass

- One real subprocess smoke remains for the current repo invariant check.
- Converted fixtures still exercise argparse, stderr output, and return codes
  via `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_repo_copy_invariants.py | action: fix | note: subprocess calls dropped from 5 to 1 while retaining current-repo CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_startup_probe_measure.py | action: defer | note: timeout/probe tests depend on real process behavior and should stay subprocess-backed

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this synthetic-fixture conversion retained a real current-repo
subprocess smoke and passed deterministic focused proof.
