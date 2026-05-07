---
name: impl
description: "Use when work should move into code, config, tests, or operator-facing artifacts. Consume the current implementation contract when it exists, bootstrap a small honest contract inline when it does not, implement the smallest meaningful slice, verify it aggressively, and keep the contract synchronized when reality changes it."
---
# Impl

Use this when the work should move from contract into code, config, tests, or operator-facing artifacts.

`impl` is downstream of `spec`, but direct implementation prompts still get a
small honest contract instead of pretending the task is already well-defined.
Keep sequence discipline, strong verification, and honest premortem use in the
loop. See `references/sequence-discipline.md`, `references/verification-ladder.md`, `references/design-lenses.md`, and `references/review-gate.md`.

## Continuation Default

- When the user explicitly asks for autonomous continuation, do not pause at
  slice boundaries just to report completion; treat commits, verification, and
  contract updates as checkpoints and continue into the next locally decidable slice.
- Ask only for real product/policy decisions, irreversible external side effect,
  unavailable stronger proof, or evidence conflicts you cannot resolve locally.

## Bootstrap

Read the current implementation contract before changing code. If no canonical
contract exists, bootstrap a small current-slice contract first.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
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
- if recurring verification expectations matter, create
  `<repo-root>/.agents/impl-adapter.yaml` early
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
   - apply `../../shared/references/source-bound-records.md` for multi-source external writes
   - for skill packages, scheduled workflows, or external lookup contracts, use
     the prescribed path from `SKILL.md`, not an author-composed smoke probe
4. Verify with the strongest honest path.
   - survey repo and adapter capabilities before coding and again before stopping
   - prefer executed proof over code inspection when an executable path exists
   - for validation-shaped review, closeout, or operator reading work, run
     deterministic gates first; query evaluator tools only for explicit behavior
     evaluation, prompt regression, baseline compare, or insufficient local proof
   - add or strengthen checks when an important branch would otherwise stay unproven
   - for browser-facing output, resolve browser/runtime support through `find-skills`
     and say explicitly that it did not run when runtime proof is unavailable
   - for external named targets or third-party APIs, verify runtime state before acting
   - for skill self-tests, external lookup contracts, and scheduled or delegated workflows, apply `../../shared/references/prescribed-path-self-test.md`
   - if the slice changes repo-owned instruction or prompt surfaces such as `<repo-root>/AGENTS.md`, public/support `SKILL.md`, behavior-steering references, or adapter prompt wording, let the repo's cautilus adapter decide prompt/evaluator proof policy before closeout
   - if the adapter run mode is `disabled`, do not run Cautilus; record the disabled validator result and use deterministic gates until the adapter is re-enabled
   - generic review or closeout wording must not silently launch Cautilus
   - for behavior-preserving prompt changes, keep regression proof anchored by
     `cautilus eval test --repo-root . --adapter-name <repo-owned-adapter>` or
     a repo-owned dogfood wrapper when the adapter permits Cautilus execution;
     for behavior-improving claims, also record the baseline compare path with
     `cautilus workspace prepare-compare` and `cautilus eval evaluate --input <observed.json>`
   - if stronger proof needs setup or permission, ask instead of silently
     downgrading the claim
5. Sync truth surfaces and re-read the contract before closeout.
   - if the slice changed user-visible capability, operating philosophy,
     supported integrations, install/usage surface, or honest stage claims,
     check `<repo-root>/README.md` and the adapter's `truth_surfaces`
   - update the relevant truth surfaces before stopping
   - re-read `Fixed Decisions` and named acceptance checks
   - confirm each item is reflected in the delivered slice or explicitly
     deferred or reclassified in the contract
6. Run the stop gate.
   - every task-completing repo slice records premortem before closeout; scale the pass instead of asking whether it is needed
   - record `Premortem: short <scope>` for small local-risk slices, or `Premortem: full <artifact-or-subagent-status>` after using standalone `premortem` for design, release, workflow, compatibility, host-proof, prompt-surface, public-skill, validator, or export decisions
   - `premortem` always means a fresh bounded subagent review, never a same-agent pass
   - use `Premortem: not-applicable <reason>` only for inspect/status/routing-only requests that do not complete repo work
   - if the required premortem is blocked because the host cannot provide
     subagents after the capability check, stop and record `Premortem: blocked <host-signal>`
   - run a fresh-eye review for runtime behavior, boundary honesty, and
     docs/spec synchronization
7. End with execution status.
   - what changed, what was verified, and what truth surfaces moved
   - what the premortem found and what contract updates were made
   - what remains for the next slice
   - if `$SKILL_DIR/../retro/scripts/check_auto_trigger.py` reports `triggered: true`
     for the current repo, run a short `session` retro before the final stop
   - if the user explicitly asked to keep going, treat this as a terse
     progress checkpoint and continue into the next locally decidable slice

## Output Shape

The closeout should usually include:

`Implemented`, `Contract Source`, `Verification` naming code/fixture and
runtime/evaluator proof, `Truth Surface Sync`, `Premortem`, `Contract Updates`,
`Residual Risks`, and `Next Slice`.

## Guardrails

- Do not implement against a stale or imaginary contract, require a separate
  `spec` session when an honest inline contract works, or silently expand scope.
- Do not close the task without checking the named acceptance behaviors.
- Do not close a contract-backed slice without re-reading `Fixed Decisions` and
  named acceptance checks against the delivered slice.
- Do not treat commit, verification, or contract-sync completion as a default
  pause when the user explicitly asked for autonomous continuation.
- Do not stop after a user-visible change without checking whether `<repo-root>/README.md`
  and adjacent durable truth surfaces are now stale.
- Do not leave a resolved probe undocumented in the canonical artifact.
- Do not continue ordinary implementation past a forced debug interrupt just
  because the local patch still looks tempting; let the planner and named spec
  handoff decide whether plain `impl` is allowed.
- If a branch or fallback matters to users or operators, prove it with the best
  available verification capability instead of relying on code inspection alone.
- If a stronger verification path exists but needs permissions, setup, or an
  external tool, ask for it rather than pretending the weaker proof is enough.
- Do not call a same-agent review a premortem.
- Do not skip premortem for task-completing repo work just because the code
  looks locally clean.
- Do not reinvent one-off premortem angle selection when the standalone
  `premortem` skill fits the slice.
- If the required premortem is blocked, stop instead of downgrading to a local
  substitute and still calling the slice reviewed.

## References

- `references/adapter-contract.md`
- `references/contract-consumption.md`
- `references/verification-ladder.md`
- `references/external-api-contract.md`
- `references/design-lenses.md`
- `references/sequence-discipline.md`
- `references/review-gate.md`
- `references/spec-loop.md`
- `../../shared/references/source-bound-records.md`
- `../../shared/references/prescribed-path-self-test.md`
