# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts three synthetic
`check_skill_ownership_overlap.py` subprocess tests to in-process `main()` calls.

## Failure Angles

- Boundary proof: converting the current-repo test would remove useful
  script-bootstrap evidence on real data.
- Scanner fidelity: synthetic fixtures must still exercise JSON output and
  return codes through argparse.
- Value: small scanner conversions can become noise if they do not retain a
  representative CLI smoke.

## Counterweight Pass

- One real subprocess smoke remains for the current repo and seeded allowlist.
- Converted fixtures still exercise argparse, JSON stdout, and return codes via
  `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_skill_ownership_overlap.py | action: fix | note: subprocess calls dropped from 4 to 1 while retaining current-repo CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_repo_copy_invariants.py | action: defer | note: repo-copy invariant subprocesses mix current-repo and synthetic failure proof and need separate review

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this scanner-fixture conversion retained a real current-repo
subprocess smoke and passed deterministic focused proof.
