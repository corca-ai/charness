# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a small local-only cleanup that converts two `render_skill_routing.py`
subprocess tests to in-process `main()` calls.

## Failure Angles

- Boundary proof: removing all subprocess calls would erase script bootstrap
  proof for the setup routing helper.
- Value: the slice could be too small if it added more ceremony than runtime
  savings.
- Isolation: monkeypatched `sys.argv` and captured stdout could leak between
  tests if not pytest-scoped.

## Counterweight Pass

- One real subprocess JSON smoke remains.
- The converted tests still exercise argparse and stdout JSON through `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.
- The slice is intentionally small and local; it follows the same retained-CLI
  pattern as the larger validator reductions.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_setup_render_skill_routing.py | action: fix | note: subprocess calls dropped from 3 to 1 while retaining a real JSON CLI smoke
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_setup_seed_usage_episodes.py | action: defer | note: seed/overwrite behavior mutates files and needs a separate retained-boundary review

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this two-test conversion retained a real subprocess smoke, changed
one low-risk test file, and passed deterministic focused proof.
