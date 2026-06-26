# Critique Review
Date: 2026-06-26

## Decision Under Review

Convert most repeated skill-ergonomics gate subprocess assertions to direct
calls into the validator module.

## Failure Angles

- Command proof: removing too many subprocesses could miss root wrapper or
  helper command failures.
- Formatter drift: plain-output assertions must still use the actual formatter,
  not a duplicated approximation.
- Rule coverage: broad mechanical conversion could accidentally skip return-code
  semantics for failing rule cases.

## Counterweight Pass

- One skill-helper CLI success smoke and two root-wrapper failure smokes remain.
- Plain-output checks call the actual `_format_human()` function.
- Direct tests still assert `has_failures()`-derived return-code semantics.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_skill_ergonomics_gate.py | action: fix | note: repeated validator subprocess launches dropped from 23 to 3
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_skill_ergonomics_gate.py | action: defer | note: keep remaining CLI smokes to preserve command-wrapper proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this conversion retained command smokes and passed deterministic
focused proof.
