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

Keep sequence discipline, strong verification, and honest premortem use in the
loop. See `references/sequence-discipline.md`,
`references/verification-ladder.md`, `references/design-lenses.md`, and
`references/review-gate.md`.

## Continuation Default

- WHEN THE USER EXPLICITLY ASKS FOR AUTONOMOUS CONTINUATION, DO NOT PAUSE AT
  SLICE BOUNDARIES JUST TO REPORT COMPLETION.
- Treat commits, verification, and contract updates as continuation
  checkpoints, not default stop points.
- Continue into the next locally decidable slice after each checkpoint.
- Ask only when a real product or policy decision is required, an irreversible
  external side effect needs confirmation, stronger honest verification needs
  permission or setup you do not have, or new evidence creates a conflict you
  cannot resolve locally.

## Bootstrap

Read the current implementation contract before changing code. If no canonical
contract exists, bootstrap a small current-slice contract first.

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
# 1. current contract and nearby context
rg --files docs skills
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
sed -n '1,220p' "$SKILL_DIR/../spec/SKILL.md" 2>/dev/null || true

# 2. impl adapter resolution and verification survey
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/survey_verification.py" --repo-root .

# 3. locate the canonical spec/design artifact
rg -n "Current Slice|Success Criteria|Acceptance Checks|Fixed Decisions|Probe Questions|Deferred Decisions|requirements|acceptance" .
python3 "$SKILL_DIR/../../../scripts/plan_risk_interrupt.py" --repo-root . --json 2>/dev/null || true

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
- if the adapter is invalid, repair it using `references/adapter-contract.md`
  before relying on adapter-defined paths or verification preferences
- if the repo has recurring verification expectations worth encoding, create
  `.agents/impl-adapter.yaml` early instead of relearning the same tools each
  session
- treat the verification survey as onboarding, not a closing nicety: look for
  the best self-verification path before you code and again before you stop

## Workflow

1. Ingest the current slice.
   - identify the canonical artifact for the work or write an inline
     current-slice contract before changing code
   - restate the current slice in implementation terms
   - list the acceptance checks that must pass before stopping
   - if the risk interrupt planner reports a forced interrupt, do not continue
     plain implementation until the named spec handoff says this slice may
     proceed honestly
2. Keep the contract honest.
   - treat `Fixed Decisions` as fixed for this slice
   - treat `Probe Questions` as explicit learning goals, not as hidden scope
   - keep `Deferred Decisions` visible instead of resolving them accidentally
   - if implementation changes scope, acceptance, or a fixed decision, update
     the contract before stopping
3. Implement the smallest meaningful unit.
   - prefer a slice that proves one user-visible behavior or one structural seam
   - prefer the slice that opens the next good move most cleanly
   - when a probe exists, design the slice so it answers the probe cleanly
4. Verify with the strongest honest path.
   - survey repo and adapter capabilities before coding and again before
     stopping
   - prefer executed proof over code inspection when an executable path exists
   - add or strengthen checks when an important branch would otherwise stay
     unproven
   - if the slice changes repo-owned instruction or prompt surfaces such as
     [`AGENTS.md`](../../../AGENTS.md), public/support `SKILL.md`, behavior-steering references, or
     adapter prompt wording, refresh [`charness-artifacts/cautilus/latest.md`](../../../charness-artifacts/cautilus/latest.md)
     from repo-owned cautilus proof before closeout
   - let the repo's cautilus adapter decide whether proof may run
     autonomously, must ask, or should adapt by proof kind and cost; closeout
     should block on missing proof rather than silently launching it
   - for behavior-preserving prompt changes, keep regression proof anchored by
     `cautilus instruction-surface test --repo-root .`; for behavior-improving
     claims, also record the baseline compare path with
     `cautilus workspace prepare-compare` and
     `cautilus mode evaluate --baseline-ref <ref>`
   - when the slice changes reader fit, truth-surface framing, or skill-core
     reasoning shape, add a short scenario-review note instead of treating
     routing preservation as sufficient evidence
   - if stronger proof needs setup or permission, ask instead of silently
     downgrading the claim
5. Sync truth surfaces and re-read the contract before closeout.
   - if the slice changed user-visible capability, operating philosophy,
     supported integrations, install/usage surface, or honest stage claims,
     check [`README.md`](../../../README.md) and the adapter's `truth_surfaces`
   - update the relevant truth surfaces before stopping
   - re-read `Fixed Decisions` and named acceptance checks
   - confirm each item is reflected in the delivered slice or explicitly
     deferred or reclassified in the contract
6. Run the stop gate.
   - when the slice needs premortem, run the standalone `premortem` skill;
     `premortem` always means a fresh bounded subagent review, never a same-agent pass
   - if the slice does not need premortem, record `Premortem: skipped <reason>`
     in the closeout instead of implying it ran
   - if a required premortem is blocked because the host cannot provide
     subagents after the capability check, stop and record `Premortem: blocked <host-signal>`
   - run a fresh-eye review for runtime behavior, boundary honesty, and
     docs/spec synchronization
7. End with execution status.
   - what changed
   - what was verified
   - what truth surfaces were updated, or why none changed
   - what the premortem found
   - what contract updates were made
   - what remains for the next slice
   - if `$SKILL_DIR/../retro/scripts/check_auto_trigger.py` reports `triggered: true`
     for the current repo, run a short `session` retro before the final stop
   - if the user explicitly asked to keep going, treat this as a terse
     progress checkpoint and continue into the next locally decidable slice

## Output Shape

The closeout should usually include:

- `Implemented`
- `Contract Source`
- `Verification`
- `Truth Surface Sync`
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
- Do not close a contract-backed slice without re-reading `Fixed Decisions` and
  named acceptance checks against the delivered slice.
- Do not treat commit, verification, or contract-sync completion as a default
  pause when the user explicitly asked for autonomous continuation.
- Do not stop after a user-visible change without checking whether [`README.md`](../../../README.md)
  and adjacent durable truth surfaces are now stale.
- Do not leave a resolved probe undocumented in the canonical artifact.
- Do not continue ordinary implementation past a forced debug interrupt just
  because the local patch still looks tempting; let the planner and named spec
  handoff decide whether plain `impl` is allowed.
- If a branch or fallback matters to users or operators, prove it with the best
  available verification capability instead of relying on code inspection alone.
- If a stronger verification path exists but needs permissions, setup, or an
  external tool, ask for it rather than pretending the weaker proof is enough.
- If the change touches shared seams or architectural ownership, do not stop at
  same-context self-review alone.
- Do not call a same-agent review a premortem.
- Do not skip a required premortem just because the code looks locally clean.
- Do not reinvent one-off premortem angle selection when the standalone
  `premortem` skill fits the slice.
- If a required premortem is blocked, stop instead of downgrading to a local
  substitute and still calling the slice reviewed.

## References

- `references/adapter-contract.md`
- `references/contract-consumption.md`
- `references/verification-ladder.md`
- `references/design-lenses.md`
- `references/sequence-discipline.md`
- `references/review-gate.md`
- `references/spec-loop.md`
