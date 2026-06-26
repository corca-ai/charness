# Critique Review
Date: 2026-06-26

## Decision Under Review

Convert most standing-doc provenance tests from subprocess execution to direct
calls into the checker module.

## Failure Angles

- Command proof: parser/bootstrap behavior might be hidden if all subprocesses
  are removed.
- Plain-output fidelity: inert plain-output assertions must use the real
  formatter.
- Adapter-error path: invalid adapter behavior includes stderr and should keep a
  command smoke.

## Counterweight Pass

- One JSON CLI smoke and one invalid-adapter CLI failure remain.
- Plain-output assertions call `_render_plain()`.
- Direct checks use the real `run()` function against temp repo files.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_standing_doc_provenance.py | action: fix | note: provenance subprocess launches dropped from 11 to 2
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_standing_doc_provenance.py | action: defer | note: keep remaining CLI smokes for command and adapter-error proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this conversion retained command smokes and passed deterministic
focused proof.
