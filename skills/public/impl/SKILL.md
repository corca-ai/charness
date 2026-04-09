---
name: impl
description: Use when the current implementation contract is clear enough to build a concrete slice. Consume the canonical spec or equivalent artifact, implement the smallest meaningful unit, verify behavior while iterating, and keep the contract synchronized when reality changes it.
---

# Impl

Use this when the work should move from contract into code, config, tests, or
operator-facing artifacts.

`impl` is downstream of `spec`, but not blind to it. The implementation slice
must stay synchronized with the current contract instead of quietly drifting.

## Bootstrap

Read the current implementation contract before changing code.

```bash
# 1. current contract and nearby context
rg --files docs skills
sed -n '1,220p' docs/handoff.md
sed -n '1,220p' skills/public/spec/SKILL.md

# 2. locate the canonical spec/design artifact
rg -n "Current Slice|Success Criteria|Acceptance Checks|Fixed Decisions|Probe Questions|Deferred Decisions|requirements|acceptance" .

# 3. repo patterns and current target area
rg -n "test|spec|fixture|eval|smoke|integration" .
git status --short
```

If the canonical contract artifact is missing, reconstruct the smallest honest
contract first. Do not pretend the task is implementation-ready when the slice
is still undefined.

## Workflow

1. Ingest the current slice.
   - identify the canonical artifact for the work
   - restate the current slice in implementation terms
   - list the acceptance checks that must pass before stopping
2. Confirm the boundary.
   - treat `Fixed Decisions` as fixed for this slice
   - treat `Probe Questions` as explicit learning goals, not as hidden scope
   - keep `Deferred Decisions` visible instead of resolving them accidentally
3. Implement the smallest meaningful unit.
   - prefer a slice that proves one user-visible behavior or one structural seam
   - when a probe exists, design the slice so it answers the probe cleanly
4. Verify while iterating.
   - run the lightest honest checks that prove the target behavior
   - add or strengthen checks when a user-visible branch would otherwise stay
     unproven
   - keep a clear record of what was verified and what still remains open
5. Update the contract when reality changes it.
   - if implementation resolves a probe, update the canonical artifact
   - if implementation reveals a scope or acceptance change, update the
     contract before stopping
   - if the work uncovers concept-defining drift, send it back to `spec` or
     `ideation` instead of burying the change in code
6. Run a fresh-eye review before stopping.
   - review runtime behavior and branch reachability
   - review boundary honesty and ownership
   - review docs/spec synchronization
7. End with execution status.
   - what changed
   - what was verified
   - what contract updates were made
   - what remains for the next slice

## Output Shape

The closeout should usually include:

- `Implemented`
- `Verification`
- `Contract Updates`
- `Residual Risks`
- `Next Slice`

## Guardrails

- Do not implement against a stale or imaginary contract.
- Do not silently expand scope because the adjacent code makes it tempting.
- Do not close the task without checking the named acceptance behaviors.
- Do not leave a resolved probe undocumented in the canonical artifact.
- If a branch or fallback matters to users or operators, prove it with an
  executable check when a local check is available.
- If the change touches shared seams or architectural ownership, do not stop at
  same-context self-review alone.

## References

- `references/contract-consumption.md`
- `references/verification-ladder.md`
- `references/review-gate.md`
- `references/spec-loop.md`
