# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts the stale-index
`build_debug_seam_risk_index.py` test to an in-process `main()` call.

## Failure Angles

- Command proof: converting both tests would remove evidence that write mode
  works through the command entrypoint.
- Error fidelity: the in-process helper must preserve the `__main__` wrapper's
  `ValidationError` stderr and return-code behavior.
- File proof: index creation must remain covered by the retained subprocess.

## Counterweight Pass

- Write mode remains a real subprocess and continues to prove JSON output plus
  file creation.
- The converted helper catches `ValidationError`, prints stderr, and returns 1
  to match CLI behavior.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_debug_seam_risk_index.py | action: fix | note: run_script calls dropped from 2 to 1 while retaining write-mode CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_debug_seam_risk_index.py | action: defer | note: keep the remaining write subprocess as command and file-output proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this stale-check conversion retained write-mode subprocess proof
and passed deterministic focused proof.
