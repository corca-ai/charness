# Session Retro
Date: 2026-04-21

## Context

The earlier `charness update` debugging fixed the divergence message, but the
user correctly pointed out a second class of missed failure: another machine was
already broken by committed plugin-export drift.

## Evidence Summary

- user report from the current thread
- `charness-artifacts/debug/2026-04-11-plugin-export-drift.md`
- `charness-artifacts/debug/2026-04-21-committed-plugin-export-drift.md`
- `.githooks/pre-push`

## Waste

- I initially treated the first update failure as a managed-checkout-only issue
  and did not immediately ask whether the source checkout itself could already
  be exporting a broken committed snapshot.
- I relied too much on the existence of the pre-push hook when the simpler
  defect was that the repo had no standing validator for the committed snapshot.

## Critical Decisions

- add a committed-snapshot packaging validator instead of relying on the
  working-tree validator alone
- keep the fix on repo-owned quality paths instead of adding a runtime repair
  branch to `charness`

## Expert Counterfactuals

- Richard Feynman: the downstream machine only sees the committed snapshot, so
  the quality gate has to validate the same object rather than a nicer local
  working tree.
- Atul Gawande-style checklist lens: the invariant should live in a standing
  repo-owned command, not in assumptions about maintainer workflow.

## Next Improvements

- capability: keep the committed packaging validator in `run-quality.sh`
- memory: when downstream consumers read committed state, validate committed
  state directly instead of trusting the working tree

## Persisted

- yes: `charness-artifacts/retro/2026-04-21-local-origin-packaging-gap.md`
