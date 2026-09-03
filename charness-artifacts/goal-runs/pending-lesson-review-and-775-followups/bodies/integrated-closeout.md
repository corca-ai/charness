<!-- charness-work-item-key: integrated-closeout -->

## Objective

Prove the composition once and close the parent through the guarded Goal Run close.

## Owned scope

- Standing, full read-only, and release lanes green in a clean clone with the skip list read.
- The most recent scheduled `mutation-tests.yml` run read from GitHub; #764's state made consistent with it through its own recovery-observer path.
- Every child `verify-closeout` verified with an issue-owned closeout comment; session retro persisted.
- Parent closed only through the guarded close after exact readback.

## Acceptance

- Three lanes recorded with counts and not-run lists; `verify-closeout` verified for every child; the terminal observation recorded.

## Focused verification

The three lanes in a clean clone; `goal_run_pickup.py` before the close.

## Dependencies

lane-changed-line-done, timeout-bound-census, lesson-review-783, runtime-root-retention, checkout-first-routing-and-8-0-3

## Non-claims

Does not close #764 by hand.
