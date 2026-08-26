<!-- charness-work-item-key: backlog-698 -->
# Existing Work Item #698 — Superseded lifecycle floor

## Purpose and premise

Name the superseded lifecycle floor and its required dispositions/handoff fields.
Re-read the existing transition fixtures before selecting the smallest repair.

## Owned change and acceptance

Superseded runs preserve surfaced improvements, required disposition, and
handoff identity; both positive transition and missing-field refusal are tested.
If verdict logic changes, the repaired surface receives the required second
bounded review round.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_superseded_status.py`, then changed-line proof. No closeout is inferred from a status string alone.
