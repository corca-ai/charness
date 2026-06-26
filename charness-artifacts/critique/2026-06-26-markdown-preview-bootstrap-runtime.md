# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts two `bootstrap_markdown_preview.py`
tests to in-process `main()` calls.

## Failure Angles

- Bootstrap proof: converting every test would remove evidence that the script
  can be launched as a command.
- Backend proof: the execute path must still prove fake `glow` discovery and
  artifact writing.
- Environment fidelity: in-process execute must still honor the test-scoped
  `PATH` containing fake `glow`.

## Counterweight Pass

- The scaffold-and-execute test remains a real subprocess and continues to prove
  command bootstrap plus fake backend execution.
- The converted existing-config test still runs fake `glow` through the normal
  preview path after setting `PATH` with pytest monkeypatch.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_markdown_preview_bootstrap.py | action: fix | note: subprocess-backed helper calls dropped from 3 to 1 while retaining full execute CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_quality_markdown_preview_bootstrap.py | action: defer | note: keep the remaining scaffold-and-execute subprocess as command bootstrap proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this bootstrap-test conversion retained the full execute
subprocess smoke and passed deterministic focused proof.
