# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts three
`inventory_ubiquitous_language.py` synthetic scanner tests to in-process
`main()` calls.

## Failure Angles

- Boundary proof: converting the current-repo contract smoke would weaken real
  data entrypoint evidence.
- Unconfigured path: adapter-absent behavior is the first-run boundary and
  should retain CLI proof.
- Scanner fidelity: converted fixtures must still exercise argparse, JSON
  stdout, and return codes.

## Counterweight Pass

- Real subprocess proof remains for unconfigured and current-repo states.
- Converted fixtures still exercise argparse, JSON stdout, and return codes via
  `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_ubiquitous_language.py | action: fix | note: subprocess calls dropped from 5 to 2 while retaining unconfigured/current-repo CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_quality_ubiquitous_language.py | action: defer | note: do not convert retained first-run or current-repo subprocess smokes

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this synthetic scanner conversion retained real unconfigured and
current-repo subprocess smokes and passed deterministic focused proof.
