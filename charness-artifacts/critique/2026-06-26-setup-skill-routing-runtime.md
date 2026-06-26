# Critique Review
Date: 2026-06-26

## Decision Under Review

Convert the remaining render-skill-routing subprocess test to the existing
in-process `main()` helper.

## Failure Angles

- Command proof: no test in the file now spawns `render_skill_routing.py` as a
  separate process.
- Output capture: the helper must still exercise argv parsing and stdout.
- Write boundary confusion: nearby seed-retro-memory tests should stay
  subprocess-based because they write files.

## Counterweight Pass

- The helper sets `sys.argv`, calls `main()`, and captures stdout/stderr.
- Focused tests assert the same JSON payload and markdown content.
- Seed-retro-memory write tests remain subprocess-based.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_setup_render_skill_routing.py | action: fix | note: render-skill-routing subprocess launches dropped to zero and ratchet candidate count decreased
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_setup_retro_memory.py | action: defer | note: keep write-boundary seed-retro-memory tests as commands

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this conversion used an existing main() helper and passed
deterministic focused proof.
