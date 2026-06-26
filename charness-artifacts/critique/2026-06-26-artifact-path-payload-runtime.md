# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only extraction of `resolve_artifact_path.py` payload construction
and convert three path-calculation tests to in-process calls.

## Failure Angles

- Command proof: converting CLI calls can hide parser, import, or bootstrap
  failures.
- Adapter fidelity: tests that pass explicit adapters might drift from real
  resolver payloads.
- Symlink behavior: the extracted helper must preserve current-pointer target
  handling exactly.

## Counterweight Pass

- `main()` still calls the extracted `payload_for()` function, so command and
  direct paths share the same payload construction.
- Exported resolver, invalid-artifact-class, and refresh-current-pointer tests
  still exercise command boundaries.
- The converted symlink test uses a real symlink on disk and the same pointer
  state logic.
- Focused pytest, ruff, and boundary-bypass ratchet passed after extraction.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/resolve_artifact_path.py | action: fix | note: payload construction is now reusable and three repeated command launches were removed
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_artifact_naming.py | action: defer | note: keep exported resolver and refresh-current-pointer command tests as boundary proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this extraction retained command-boundary tests and passed
deterministic focused proof.
