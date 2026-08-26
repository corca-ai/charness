<!-- charness-work-item-key: backlog-695 -->
# Existing Work Item #695 — Complete critique shape

## Purpose and premise

Choose one canonical critique-shape owner and require `Execution mode` in every
produced or stub artifact. Re-read the closeout validator and typed-subagent
carrier before editing.

## Owned change and acceptance

All producer paths emit the required field with a valid value; an incomplete
typed-subagent closeout refuses rather than being accepted through a prose-only
fallback.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_describe_goal_closeout_shape.py`, then changed-line proof. A local shape pass is not fresh-eye approval.
