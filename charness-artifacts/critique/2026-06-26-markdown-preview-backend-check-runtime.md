# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts three `check_glow_backend.py` subprocess
calls to in-process `main()` calls.

## Failure Angles

- Command proof: the backend checker itself no longer gets a subprocess smoke in
  this test.
- Environment fidelity: healthy/missing/timeout cases must still see the
  intended `PATH` and timeout values.
- Exit-code fidelity: the conversion must keep return-code assertions, not only
  payload assertions.

## Counterweight Pass

- The test still asserts return codes from `main()` for all three cases.
- Environment changes use pytest monkeypatch.
- Markdown-preview full render command proof remains in the same file.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/test_markdown_preview_support.py | action: fix | note: backend-check Python process launches dropped from 3 to 0 and focused duration improved
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/test_markdown_preview_support.py | action: defer | note: keep remaining markdown-preview command smokes as CLI proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this wrapper conversion retained broader markdown-preview command
proof and passed deterministic focused proof.
