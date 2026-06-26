# Critique Review
Date: 2026-06-26

## Decision Under Review

Convert local debug scaffold payload tests from subprocess execution to direct
`payload_for()` calls.

## Failure Angles

- Command proof: source-tree command wrapper behavior is less directly covered.
- Package proof: exported plugin scaffold behavior must remain a real command.
- Validator proof: generated template must still run through the validator.

## Counterweight Pass

- Exported plugin scaffold command proof remains.
- Validator command execution remains subprocess-based.
- Direct calls use the real `payload_for()` implementation.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/test_debug_scaffold.py | action: fix | note: local scaffold subprocess payload checks now call payload_for directly
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/test_debug_scaffold.py | action: defer | note: keep exported plugin command and validator execution as subprocess proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: local payload conversion retained exported command proof and passed
deterministic focused proof.
