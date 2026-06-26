# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts two simple narrative scenario-block
adapter tests to in-process `main()` calls.

## Failure Angles

- Write proof: converting init adapter would remove command proof for adapter
  file creation.
- Complex review proof: volatile and missing-path review should still have at
  least one command-entry smoke.
- Timeout behavior: narrative scripts arm CLI timeouts; in-process conversion
  must still execute the same main path and cancel it normally.

## Counterweight Pass

- Init adapter remains a real subprocess and continues to prove file creation
  through the command entrypoint.
- The complex volatile review remains a real subprocess.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_narrative_scenario_blocks.py | action: fix | note: run_script calls dropped from 4 to 2 while retaining volatile-review and init-write CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_narrative_scenario_blocks.py | action: defer | note: keep remaining subprocesses as review/write command proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this adapter JSON conversion retained volatile-review and
init-write subprocess proof and passed deterministic focused proof.
