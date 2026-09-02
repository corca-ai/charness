<!-- charness-work-item-key: integrated-closeout -->

## Objective

Prove the composition once and close the run through its readback paths.

## Owned scope

- In a clean clone: `run_standing_pytest.py`, `./scripts/run-quality.sh --full --read-only`, and `./scripts/run-quality.sh --release`, each with its skip list read.
- Read the most recent scheduled `mutation-tests.yml` run on a tree at or after wall-clock-census-and-764 from GitHub. If `Select mutation sample: success` and the run is green, close #764 through the recovery-observer path; if not, record the failing set as the next work and do not claim #764.
- `/goal #<parent>` pickup `ok: true` with the bounded ledger preview showing the three re-admitted classes.
- Close the parent with `issue_tool.py goal-run-close` after exact readback; never `gh issue close`.

## Acceptance

- Three lane outputs recorded from the clean clone.
- The scheduled run URL and its outcome recorded; #764 state consistent with that outcome.
- `verify-closeout` = `verified` for every child before the parent closes.

## Focused verification

The three lanes and the provider readbacks.

## Dependencies

awiki-phase-echo, layout-resolver, release-lane-standing-evidence, wall-clock-census-and-764, wall-clock-rewrite-remainder, lesson-promotion-and-budget.

## Non-claims

Does not claim a mutation score; the sampler's seed rotates per run.
