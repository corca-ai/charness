<!-- charness-work-item-key: release-lane-standing-evidence -->

## Objective

A release-only regression cannot cross a push unnoticed: the pre-push clean-clone lane runs `run-quality.sh --release` on every push.

## Owned scope

- The clean-clone push procedure (the shape used for the #768, #769, #770 closeouts) runs `--release`; the hook or wrapper that procedure uses is changed, not the standing lane's marker selection.
- `docs/development.md` states the procedure, the cadence, and the measured runtime.
- Proof: a seeded `release_only` failure in a clean clone is refused by the procedure; the same clone passes once the seed is removed.

## Acceptance

- `docs/development.md` names the pre-push release run with its measured runtime.
- The seeded refusal and the clean pass are both recorded with their command output.

## Focused verification

`./scripts/run-quality.sh --release` in a clean clone; `scripts/check-docs.sh`.

## Dependencies

awiki-phase-echo (order only).

## Non-claims

`release_only` and `slow_corpus` stay deselected from the standing pytest lane. No hosted observer.
