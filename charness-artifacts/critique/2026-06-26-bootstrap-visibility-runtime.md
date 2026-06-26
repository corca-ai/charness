# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts find-skills and announcement bootstrap
visibility resolve-adapter tests to in-process `main()` calls.

## Failure Angles

- Command proof: converting all three tests would remove command-entry evidence
  for bootstrap visibility.
- Hyphenated path: `find-skills` cannot be imported as a normal dotted package.
- Timeout behavior: converted scripts must still execute their normal main path
  and cancel CLI timeouts.

## Counterweight Pass

- The narrative fallback test remains a real subprocess and continues to prove a
  command entrypoint in this file.
- `find-skills` is loaded by path with `load_path_module`, matching the
  hyphenated on-disk skill directory.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_bootstrap_visibility.py | action: fix | note: run_script calls dropped from 3 to 1 while retaining narrative fallback CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_bootstrap_visibility.py | action: defer | note: keep remaining subprocess as command proof for fallback-rich docs

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this adapter JSON conversion retained narrative fallback
subprocess proof and passed deterministic focused proof.
