# Prescribed Skill Closeout Contract

> Status: current
> Source of truth: the linked executable observers and shared checker
> Last verified: 2026-09-02

This contract covers the two remaining places where a workflow requires proof
that a named review actually ran. It does not make every recommendation a gate,
and it no longer participates in Achieve Goal Draft lifecycle or completion.

## Remaining owners

- Issue bug closeout uses
  [`issue_resolution_observer.py`](../skills/public/issue/scripts/issue_resolution_observer.py)
  to verify the bounded resolution-critique carrier before issue mutation.
- Release preflight uses
  [`publish_release_preflight.py`](../skills/public/release/scripts/publish_release_preflight.py)
  to verify the standalone critique carrier before publish.
- Both call
  [`check_prescribed_skill_executed_lib.py`](../scripts/check_prescribed_skill_executed_lib.py)
  for the shared carrier and typed-skip vocabulary. The thin
  [`check_prescribed_skill_executed.py`](../scripts/check_prescribed_skill_executed.py)
  command exposes the same verdict for direct diagnostics.

These owners keep one shared fact: executed evidence is distinct from a stated
intention to execute. Provider-specific mutation and readback remain owned by
the issue and release workflows themselves.

## Removed ownership

Achieve owns planning until Goal Binding, then reads the provider-backed Goal
Run cursor. It does not own local completion status, Auto-Retro disposition,
host-log receipts, prescribed-skill execution receipts, or a second closeout
ledger. Those former surfaces are historical and must not be reconstructed by
wrappers, documentation, or tests.

## Honest limits

The shared checker verifies carrier form and binding, not reviewer quality. A
typed skip proves only that the workflow reported why independent review was
unavailable. The irreversible issue/release boundary still owns the final
decision and its public readback.
