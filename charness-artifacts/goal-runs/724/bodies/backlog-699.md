<!-- charness-work-item-key: backlog-699 -->
# Existing Work Item #699 — Candidate-bound release critique

## Purpose and premise

Define candidate identity and verdict fields so a superseded HOLD critique cannot
authorize a publish. Re-read same-version candidate A/B behavior before editing.

## Owned change and acceptance

Stale candidate identity is rejected, same-version distinct candidates remain
distinct, and release-planner output names the candidate bound to its verdict.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_release_claims_review.py`, then changed-line proof. No release operation is authorized.
