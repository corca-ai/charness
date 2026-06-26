# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts five quality bootstrap follow-up
`resolve_adapter.py` checks to in-process `main()` calls.

## Failure Angles

- Write proof: bootstrap and init adapter commands must remain subprocesses
  because they mutate adapter files.
- Resolve command proof: at least one direct resolve CLI smoke should remain.
- Timeout behavior: converted resolve calls must still execute main and cancel
  the CLI timeout path normally.

## Counterweight Pass

- Bootstrap and init calls remain real subprocesses.
- The invalid review-fields resolve test remains a real subprocess.
- Converted follow-up resolves still drive argparse through scoped `sys.argv`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap.py | action: fix | note: resolve_adapter subprocess calls dropped from 6 to 1 while retaining write-boundary subprocesses
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_quality_bootstrap.py | action: defer | note: keep bootstrap/init and one direct resolve subprocess as command proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this read-only follow-up conversion retained bootstrap/init and
direct resolve subprocess proof and passed deterministic focused proof.
