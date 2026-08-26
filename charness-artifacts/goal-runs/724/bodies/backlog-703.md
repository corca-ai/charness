<!-- charness-work-item-key: backlog-703 -->
# Existing Work Item #703 — Attention renderer field provenance

## Purpose and premise

Trace every uncovered, scope, and unreachable field to the ordinary attention
renderer. Select only the still-missing path and preserve fields that are not
actually emitted.

## Owned change and acceptance

The focused fixture names exact expected output for the selected path; a value
is not presented as routine attention merely because it exists in a diagnostic
payload.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_attention_state_visibility.py`, then changed-line proof. Local renderer proof does not claim host adoption.
