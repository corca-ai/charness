# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts repeated `validate_usage_episodes.py`
checks to in-process `main()` calls inside the slice-closeout usage episode
tests.

## Failure Angles

- Closeout proof: converting `_run_closeout(...)` would remove the actual
  command boundary under test.
- Validator fidelity: converted validator checks must still exercise argparse,
  JSON stdout, and return codes.
- Environment behavior: quality-mode suppression must continue to be proven by
  the closeout subprocess, not by an in-process shortcut.

## Counterweight Pass

- `_run_closeout(...)` remains a real subprocess for every closeout scenario.
- Converted validator checks still drive argparse through pytest-scoped
  `sys.argv`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_slice_closeout_usage_episode.py | action: fix | note: run_script calls dropped from 4 to 1 while retaining closeout subprocess proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_slice_closeout_usage_episode.py | action: defer | note: keep closeout command execution as the behavior boundary

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: this validator conversion retained slice-closeout subprocess proof
and passed deterministic focused proof.
