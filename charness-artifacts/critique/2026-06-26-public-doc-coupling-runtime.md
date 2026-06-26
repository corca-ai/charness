# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts three JSON
`check_public_doc_coupling.py` subprocess tests to in-process `main()` calls.

## Failure Angles

- Boundary proof: converting all calls would remove proof for human advisory
  output, which is how the gate appears in run-quality logs.
- JSON fidelity: converted tests must still exercise argparse and stdout JSON.
- Value: advisory scanner changes should not weaken the current clean-baseline
  invariant.

## Counterweight Pass

- Real subprocess proof remains for clean text output and advisory text output.
- Converted fixtures still exercise argparse, JSON stdout, and return codes via
  `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_check_public_doc_coupling.py | action: fix | note: subprocess calls dropped from 5 to 2 while retaining human text output CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_check_public_doc_coupling.py | action: defer | note: do not convert retained human-output subprocess smokes

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this JSON-fixture conversion retained real human-output
subprocess smokes and passed deterministic focused proof.
