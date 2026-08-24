# Spec — Issue #713: Slice-Bound Impl Risk Planning

Date: 2026-08-24
Status: approved
Primary consumer: `../ceal`
Source issue: `corca-ai/charness#713`

## Problem

Ceal, the highest-priority Charness consumer, entered `impl` for a test-only
slice and was stopped by a current debug interrupt whose affected seam was
unrelated to the slice. The planner already supports path-scoped
classification, but the public `impl` bootstrap invokes it without `--paths`
before the current slice is bound. That turns a global discovery fact into an
ordinary implementation blocker and makes unrelated consumer work pay for a
different seam.

This is the P0 friction slice. Issues #689, #690, and #691 are requalified
immediately after it against Ceal, but they are not silently closed by this
change: #689 needs a real Node mutation roundtrip, #690 needs the exact
historical hollow draft, and #691 currently exposes a Ceal adoption gap because
ten superseded goals omit `Superseded by:`.

## Capability Contract

Before `impl` interprets a risk-interrupt verdict as permission or refusal, it
must identify the current contract/target and freeze the planned current-slice
path set, including owned source, test, generated, and contract surfaces. It
then invokes the existing planner with those explicit paths.

- `status: not-applicable` with `required: false` allows ordinary `impl` to
  start, while preserving the interrupt as unrelated context.
- `status: blocked`, an unknown/malformed state, or any required result without
  a valid handoff stops ordinary implementation.
- `status: handoff-recorded` proceeds into ordinary implementation only when
  both `impl_status: allowed` and `chosen_next_step: impl` hold. Every other
  next step (`critique`, `factor-first`, or `hitl`) remains binding and stops
  ordinary implementation even if `impl_status` was written as allowed.
- A pathless planner run may be used only to discover that a current interrupt
  exists. It is not authoritative for the current slice and cannot by itself
  stop or clear implementation.
- If planned paths are not yet known, `impl` must finish binding the slice rather
  than guess paths, omit `--paths`, or bypass the planner.

The planned set is an auditable pre-mutation hypothesis, not proof of
completeness. At the `prove` stop gate, `run_slice_closeout.py` recomputes the
actual tracked, staged, and untracked paths from Git and invokes the same
planner. That actual-path verdict is authoritative: unexpected paths reopen the
slice binding, and any actual debug/handoff overlap remains protected. A green
bootstrap result alone can never close the slice.

Because closeout sync, verification, or coverage commands may create generated
or artifact paths, successful closeout performs a second Git observation after
those commands. It unions the live worktree set with any committed campaign/base
range and re-applies the same fail-closed planner interpretation before success.
Post-decision usage and telemetry writes remain confined to gitignored runtime
surfaces; they do not create a second source-visible mutation channel.

Git observation itself has three semantic states: observed non-empty, observed
empty, and unavailable. Closeout records that state. Unavailable never falls
back to caller-selected `--paths`; it invokes the existing pathless/global
planner so a current interrupt fails closed, while a consumer with no current
interrupt can still use the closeout surface without a Git repository.

The planner's classification semantics remain the authority; this slice fixes
the caller contract, not the planner.

## Current Slice

Change the public `impl` skill and checked-in plugin export so bootstrap order
is contract/target discovery -> planned path freeze -> path-scoped interrupt
planning -> strict state interpretation. Update executable skill-contract pins
and focused structural tests so a future edit cannot restore a globally
authoritative pathless call. Bind the final safety claim to the existing
Git-derived closeout planner rather than inventing a second path collector, and
repair that closeout caller so it applies the same fail-closed state mapping.
Keep that mapping in the cohesive `slice_closeout_risk_interrupt.py` policy
module so the already-large closeout orchestrator does not absorb another
verdict vocabulary; this is an interpreter of planner output, not a second
planner.

## Fixed Decisions

- Preserve planner classification for non-empty slice paths. Distinguish
  `changed_paths: None` (pathless/global discovery) from `changed_paths: []`
  (an authoritative Git observation found no slice paths); the latter is scoped
  `not-applicable`, not a global forced-interrupt decision.
- Distinguish an unavailable Git observer from both states above. Record it and
  use global planning; do not crash, silently clear, or trust `--paths`.
- `run_slice_closeout.py` is an existing caller of the planner and must refuse
  unknown/malformed states, blocked handoffs, and allowed handoffs whose chosen
  next step is not `impl`.
- No bypass, ignore flag, allowlist, or weakening of overlap behavior.
- The command surface is
  `plan_risk_interrupt.py --repo-root . --detail --paths
  <current-slice-path>...` after the path set is known.
- The source public skill is authoritative; the plugin mirror is generated by
  `scripts/sync_root_plugin_manifests.py`, not hand-maintained independently.
- Caller-level regression coverage must prove ordering, explicit path binding,
  the complete state mapping, the bare/global discovery-only rule, and source /
  generated-plugin semantic parity.
- Bootstrap path completeness is not claimed. Final completeness is owned by
  the Git-derived changed-path collection in `run_slice_closeout.py`.
- Ceal tracked files are read-only in this slice. Consumer mutations require a
  separate explicit scope and isolated worktree.

## Probe Questions

- Does the skill's ordering make the path set knowable before interpretation,
  including when the initial request names only a behavior and not files?
- Does the exact planner command keep generated/owned surfaces in the slice
  instead of naming only the first source file?
- Can a future prose edit retain `--paths` while still telling an agent to stop
  on the earlier global result, or proceed on `handoff-recorded` with
  `impl_status: blocked`, or to proceed on an allowed handoff whose next step is
  not `impl`? The focused structural test must reject that ambiguity.

## Deferred Decisions

- Whether another workflow should expose a structured slice-path manifest.
- Whether path discovery should become a separate executable planner.
- Ceal migrations for the ten #691 superseded goals.
- GitHub closeout for #689, #690, #691, and #713.

## Non-Goals

- No new task system, autonomous worker protocol, or general orchestration
  surface.
- No planner semantic change and no weakening of current-debug protection.
- No Ceal tracked-file edits in this slice.
- No claim that #689, #690, or #691 is consumer-resolved.
- No Cautilus run without the separately required ask-before-run grant.

## Constraints

This is an operator-facing skill-contract change and therefore requires source
and plugin parity, deterministic contract proof, changed-line proof, and a
bounded fresh-eye review. Cautilus remains ask-before-run; its absence must be
recorded as a non-claim, not described as evaluator proof. The implementation
worker is write-capable and must use an isolated Charness worktree.

## Success Criteria

1. The public `impl` workflow identifies the active contract/target and freezes
   explicit planned current-slice paths before interpreting the interrupt
   planner. Verification: focused structural contract test and fresh-eye
   reading.
2. The authoritative command supplies `--paths <current-slice-path>...`, and
   the skill states that a pathless/global run is discovery-only.
   Verification: focused contract test.
3. The skill maps every planner state fail-closed: only scoped
   `not-applicable/required:false` and
   `handoff-recorded/impl_status:allowed/chosen_next_step:impl` proceed;
   blocked, blocked handoff, non-impl next step, unknown, and malformed output
   stop. Verification: focused structural and closeout-caller tests plus
   existing risk-interrupt behavioral tests.
4. Source skill, executable contract pins, and checked-in plugin export agree.
   Verification: focused skill-contract tests and mirror sync/check.
5. The `prove` stop gate uses the normal (not `--predict-commit`, not explicit
   `--paths`) `run_slice_closeout.py` path, recomputes actual paths from Git,
   applies the same fail-closed mapping, and exposes the embedded
   `risk_interrupt_plan`; bootstrap planning is not accepted as final proof.
   Sync/verify-created paths are re-observed before success and cannot escape
   the risk decision. Verification: focused closeout-caller tests, a
   sync-created interrupt regression, and closeout receipt.
6. The exact #713 implementation path set returns scoped `not-applicable`
   without listing the read-only prior handoff as if it were mutated.
   Verification: recorded planner command and output after the design commit.
7. No Ceal or GitHub mutation is claimed. Verification: worktree status and
   explicit closeout non-claims.

## Acceptance Checks

- `python3 -m pytest -q tests/quality_gates/test_skill_docs_contracts.py` —
  caller contract.
- `python3 -m pytest -q tests/test_risk_interrupt.py` — disjoint/overlap planner
  behavior.
- `python3 scripts/check_skill_contracts.py` — executable public-skill pins.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` followed by the
  focused assertion that source and exported `impl/SKILL.md` bytes agree —
  generated parity.
- `python3 skills/shared/scripts/plan_risk_interrupt.py --repo-root . --detail
  --paths skills/public/impl/SKILL.md plugins/charness/skills/impl/SKILL.md
  scripts/check_skill_contracts.py scripts/run_slice_closeout.py
  scripts/slice_closeout_risk_interrupt.py
  plugins/charness/scripts/run_slice_closeout.py
  plugins/charness/scripts/slice_closeout_risk_interrupt.py
  tests/quality_gates/test_skill_docs_contracts.py
  tests/quality_gates/test_run_slice_closeout_review_obligations.py` —
  scoped-disjoint premise check after the design artifact is committed.
- `python3 scripts/run_slice_closeout.py --repo-root . --plan-only
  --ack-cautilus-skill-review` with no explicit `--paths` — normal closeout
  collection of tracked, staged, and untracked paths; assert the emitted
  `risk_interrupt_plan`. This acknowledgement records that the public-skill
  scenario recommendations were inspected; it is not a Cautilus execution.
- `bash .githooks/pre-commit` — standing broad gate.

## Boundary Ownership

- `impl` skill: sequence, explicit current-slice binding, and interpretation
  language.
- risk-interrupt planner: overlap/disjoint classification and handoff payload.
- spec/debug artifacts: durable causal state and carry-forward.
- Ceal: consumer acceptance evidence and any later adoption migration.

## Critique

- Interrupt Source: `reviewer-boundary-runtime-output-unignored-2026-08-21`
- Seam Summary: `impl` bootstrap -> current-slice path binding -> risk planner
  -> ordinary implementation permission/refusal.
- Chosen Next Step: `impl`
- Impl Status: `allowed`
- Impl Status Reason: the first fresh-eye contract review returned `BLOCK`
  because planned `--paths` were self-asserted, the command incorrectly listed
  a read-only handoff as changed scope, state interpretation was ambiguous, and
  substring-only tests could not enforce the sequence. This revision binds
  final authority to Git-derived closeout paths, narrows the implementation
  path list, defines the complete state mapping, and requires structural plus
  plugin-parity tests. The first repair-reading review removed three blockers
  and retained two: `--predict-commit` bypassed the planner, and allowed
  handoffs did not require `chosen_next_step: impl`. This revision moves final
  proof to normal closeout and makes both callers fail closed on the complete
  state tuple. Final Luna xhigh repair reading returned `APPROVE` with no
  remaining blocker.
- What Disproving Observation Is Resolved: canonical reviewer runtime output is
  ignored and source-like drift remains visible; the remaining #713 failure is
  the caller's pathless interpretation, isolated by Ceal's unrelated test-only
  reproduction and the current skill command.
- Fresh-Eye Contract Review: Luna xhigh `codex exec` round 1 delivered `BLOCK`
  with five findings; repair-reading round 2 delivered `BLOCK` with two
  remaining findings. Both are consumed as repair input; final repair reading
  delivered `APPROVE`. It made no implementation, test, parity, closeout, or
  external-mutation claim.

## First Implementation Slice

After a repair-reading review allows implementation, use an isolated worktree
to update the public `impl` skill, its executable contract pin/test, the
closeout caller and focused review-obligation tests, and their generated plugin
exports. Prove the focused caller contract, exact source/plugin bytes, existing
planner behavior, strict closeout state mapping, and Git-derived closeout before
broad gates. Do not modify Ceal, the planner library, GitHub state,
release/version surfaces, or unrelated friction issues. Because the closeout
caller renders a verdict about other changes, this is a proof-surface slice and
the two-round implementation review rule applies if round 1 causes repairs.
