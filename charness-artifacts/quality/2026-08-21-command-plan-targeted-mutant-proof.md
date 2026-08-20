# Command-Plan Targeted Mutant Proof

Date: 2026-08-21

## Blocking Target

- Gate: `scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
- Reported blocking target: `scripts/command_plan_preflight.py:274`
- Original branch: `if TARGET_TOKEN_PREFIX in inner or TARGET_TOKEN_SUFFIX in inner:`

## Mutation and Failure

The exact branch was temporarily mutated to `if False and (...)`. The focused
test was then run with:

`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality_gates/test_command_plan_preflight.py -k nested_target_tokens`

It failed as required: the nested target-token case returned `owner-binding`
instead of the expected `target-token` refusal. This confirms the branch is a
behavioral guard, not uncovered defensive prose.

## Restoration and Coverage

The mutation was reverted immediately with the original condition. The full
focused command-plan suite then passed (`25 passed`), and the subsequent
changed-line proof at `19e62aea829e4d40b1ede2d1e2273ea067963dd1` returned
`status: clean`, `23/23`, `blocking=[]`, consumer return code `0`.

This artifact proves the targeted mutant only; it does not claim runtime,
installed, hosted, publication, issue-closeout, or Cautilus truth.
