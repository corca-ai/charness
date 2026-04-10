---
name: impl
description: "Use when work should move into code, config, tests, or operator-facing artifacts. Consume the current implementation contract when it exists, bootstrap a small honest contract inline when it does not, implement the smallest meaningful slice, verify it aggressively, and keep the contract synchronized when reality changes it."
---

# Impl

Use this when the work should move from contract into code, config, tests, or
operator-facing artifacts.

`impl` is downstream of `spec`, but it must also handle the common case where a
user asks for implementation directly and no separate spec step happened. In
that case, `impl` should bootstrap the smallest honest contract for the current
slice instead of pretending the task is already well-defined.

Use Gary Klein-style premortem discipline before closing a slice: ask what the
next maintainer, operator, or user is most likely to misunderstand or break,
then tighten the implementation or closeout around that failure.

## Bootstrap

Read the current implementation contract before changing code. If no canonical
contract exists, bootstrap a small current-slice contract first.

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
# 1. current contract and nearby context
rg --files docs skills
sed -n '1,220p' docs/handoff.md
sed -n '1,220p' skills/public/spec/SKILL.md

# 2. impl adapter resolution and verification survey
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/survey_verification.py" --repo-root .

# 3. locate the canonical spec/design artifact
rg -n "Current Slice|Success Criteria|Acceptance Checks|Fixed Decisions|Probe Questions|Deferred Decisions|requirements|acceptance" .

# 4. repo patterns and current target area
rg -n "test|spec|fixture|eval|smoke|integration" .
git status --short
```

If the canonical contract artifact is missing, reconstruct the smallest honest
contract first. Do not stop just because `spec` was not run as a separate
session. Stop only if the slice is still too ambiguous to define honestly.

Adapter policy:

- if the impl adapter is missing, continue with inferred defaults and manual
  capability discovery
- if the repo has recurring verification expectations worth encoding, create
  `.agents/impl-adapter.yaml` early instead of relearning the same tools each
  session
- if the adapter is invalid, repair it using `references/adapter-contract.md`
  before relying on adapter-defined paths or verification preferences
- treat the verification survey as onboarding, not a closing nicety: look for
  the best self-verification path before you code and again before you stop

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
   - start by surveying the strongest available self-verification path from the
     adapter, installed skills, repo-local scripts, binaries, browser paths,
     APIs, agent runtimes, or other host capabilities
   - use whatever available capability most honestly proves the slice:
     local tests, support skills, integration tools, binaries, APIs, browser
     paths, evals, or other repo-available checks
   - when UI, rendered artifacts, screenshots, or other operator-visible
     presentation changed, inspect the real output in a browser or equivalent
     viewport path if one exists
   - when user-visible agent or tool invocation is part of the slice, prefer a
     real invocation over mock-only proof when the repo exposes one
   - if the repo's preferred verification tools are missing but installable,
     propose the install or setup during onboarding instead of silently
     downgrading the claim
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
6. Run a Gary Klein-style premortem before stopping.
   - ask what wrong next action a maintainer or operator is most likely to take
   - ask which branch, recovery path, setup assumption, or ownership boundary
     is most likely to fail under normal pressure
   - fix the highest-likelihood failure mode or record why it remains open
7. Run a fresh-eye review before stopping.
   - review runtime behavior and branch reachability
   - review boundary honesty and ownership
   - review docs/spec synchronization
8. End with execution status.
   - what changed
   - what was verified
   - what the premortem found
   - what contract updates were made
   - what remains for the next slice

## Output Shape

The closeout should usually include:

- `Implemented`
- `Contract Source`
- `Verification`
- `Premortem`
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
- Do not skip the bounded premortem just because the code looks locally clean.

## References

- `references/adapter-contract.md`
- `references/contract-consumption.md`
- `references/verification-ladder.md`
- `references/review-gate.md`
- `references/spec-loop.md`
