---
name: impl
description: Use when work should move into code, config, tests, or operator-facing artifacts. Consume the current implementation contract when it exists, bootstrap a small honest contract inline when it does not, implement the smallest meaningful slice, verify it aggressively, and keep the contract synchronized when reality changes it.
---

# Impl

Use this when the work should move from contract into code, config, tests, or
operator-facing artifacts.

`impl` is downstream of `spec`, but it must also handle the common case where a
user asks for implementation directly and no separate spec step happened. In
that case, `impl` should bootstrap the smallest honest contract for the current
slice instead of pretending the task is already well-defined.

## Bootstrap

Read the current implementation contract before changing code. If no canonical
contract exists, bootstrap a small current-slice contract first.

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
contract first. Do not stop just because `spec` was not run as a separate
session. Stop only if the slice is still too ambiguous to define honestly.

## Workflow

1. Ingest the current slice.
   - identify the canonical artifact for the work when one exists
   - if it does not exist, write an inline current-slice contract before
     changing code
   - restate the current slice in implementation terms
   - list the acceptance checks that must pass before stopping
2. Confirm that the slice is honest enough to build.
   - when a contract exists, treat `Fixed Decisions` as fixed for this slice
   - treat `Probe Questions` as explicit learning goals, not as hidden scope
   - keep `Deferred Decisions` visible instead of resolving them accidentally
   - when no prior spec exists, separate what is fixed, what is being probed,
     and what is explicitly deferred inside the implementation closeout
3. Implement the smallest meaningful unit.
   - prefer a slice that proves one user-visible behavior or one structural seam
   - when a probe exists, design the slice so it answers the probe cleanly
4. Verify while iterating.
   - use whatever available capability most honestly proves the slice:
     local tests, support skills, integration tools, binaries, APIs, browser
     paths, evals, or other repo-available checks
   - if stronger verification requires setup or permission, ask for it instead
     of silently downgrading the claim
   - add or strengthen checks when a user-visible branch would otherwise stay
     unproven
   - keep a clear record of what was verified, what required extra permission,
     and what still remains open
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
- `Contract Source`
- `Verification`
- `Contract Updates`
- `Residual Risks`
- `Next Slice`

## Guardrails

- Do not implement against a stale or imaginary contract.
- Do not require a separate `spec` session when an honest current-slice
  contract can be written inline.
- Do not silently expand scope because the adjacent code makes it tempting.
- Do not close the task without checking the named acceptance behaviors.
- Do not leave a resolved probe undocumented in the canonical artifact.
- If a branch or fallback matters to users or operators, prove it with the best
  available verification capability instead of relying on code inspection alone.
- If a stronger verification path exists but needs permissions, setup, or an
  external tool, ask for it rather than pretending the weaker proof is enough.
- If the change touches shared seams or architectural ownership, do not stop at
  same-context self-review alone.

## References

- `references/contract-consumption.md`
- `references/verification-ladder.md`
- `references/review-gate.md`
- `references/spec-loop.md`
