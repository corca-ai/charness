# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts four markdown-preview support variants
to in-process `render_markdown_preview.main()` calls.

## Failure Angles

- Backend fidelity: converting the Python wrapper must not bypass fake `glow`
  execution.
- Environment fidelity: timeout and `PATH` settings must remain test-scoped.
- Command proof: at least one full render command smoke and backend checker
  subprocess proof should remain.

## Counterweight Pass

- In-process helper sets environment variables through pytest monkeypatch before
  calling main.
- Fake `glow` still runs through the renderer subprocess path inside the module.
- Full render and backend checker subprocess tests remain real.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/test_markdown_preview_support.py | action: fix | note: subprocess-backed run_helper calls dropped from 7 to 3 while retaining full-render/backend subprocess proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/test_markdown_preview_support.py | action: defer | note: keep remaining preview and backend checker subprocesses as command proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this preview variant conversion retained full-render and backend
checker subprocess proof and passed deterministic focused proof.
