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
- I relied too much on the existence of the pre-push hook, even though the
  active local-origin managed-update flow bypasses push entirely.

## Critical Decisions

- add a committed-snapshot packaging validator instead of relying on the
  working-tree validator alone
- block local-origin managed updates before pull when the source repo's
  committed snapshot is already broken

## Expert Counterfactuals

- Richard Feynman: the downstream machine only sees the committed snapshot, so
  the quality gate has to validate the same object rather than a nicer local
  working tree.
- Atul Gawande-style checklist lens: if a local dev flow bypasses a standing
  hook, the equivalent invariant must live in a repo-owned command on the real
  execution path.

## Next Improvements

- workflow: when a managed update pulls from a local repo path, preflight the
  source checkout's committed snapshot before pull
- capability: keep the committed packaging validator in `run-quality.sh`
- memory: remember that local-origin update flows bypass push-time hooks

## Persisted

- yes: `charness-artifacts/retro/2026-04-21-local-origin-packaging-gap.md`
