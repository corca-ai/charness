# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts three quality tool recommendation tests
to in-process `main()` calls.

## Failure Angles

- Environment fidelity: recommendations must still observe an isolated `PATH`
  so test results do not depend on installed local tools.
- Command proof: converting every fixture would remove recommendation script CLI
  bootstrap proof from this file.
- Scope drift: narrative recommendation defaults differ from quality defaults
  and should not be accidentally routed through the quality helper.

## Counterweight Pass

- The in-process helper sets `PATH` via pytest monkeypatch before calling main.
- The narrative recommendation test remains a real subprocess.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_tool_recommendations.py | action: fix | note: subprocess-backed helper calls dropped from 4 to 1 while retaining narrative CLI proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_quality_tool_recommendations.py | action: defer | note: keep one recommendation subprocess as command bootstrap proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this recommendation conversion retained narrative subprocess proof
and passed deterministic focused proof.
