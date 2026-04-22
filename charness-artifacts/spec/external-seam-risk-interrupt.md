# Problem

`#52` is still open because `charness` can talk about premortem and stop gates
without reliably interrupting a live patch-debug-patch loop. The current public
skills still let external-seam risk stay too implicit:

- `debug` preserves diagnosis, but it does not force seam-specific risk,
  disproving observations, or the next interruption decision into a structured
  handoff.
- `impl` says to use premortem, but there is no repo-owned planner/gate that
  makes a risky `debug -> impl` transition stop before ordinary implementation
  continues.
- repeated seam-shaped fixes can still look locally productive enough that the
  generalization/factor-first move arrives too late.

# Current Slice

Ship a first repo-owned `risk interrupt` contract that makes `#52` closeable:

- `debug` artifacts must record seam-specific risk and the next interruption
  decision explicitly.
- a repo-owned planner must read that artifact and decide whether ordinary impl
  closeout may continue.
- the same planner must also run before ordinary `impl` continues from a debug
  artifact; closeout is only the last backstop, not the first interrupt point.
- `run-slice-closeout.py` must block when the current debug artifact says the
  next move is not ordinary implementation and the slice has not refreshed a
  spec artifact.
- `impl` / `spec` must consume the planner contract in their public wording so
  the enforced path is visible, not chat-only.

# Fixed Decisions

- This slice targets the workflow boundary from `debug` into `spec` / `impl`,
  not generic debugging quality.
- The interruption unit is a repo-owned planner, not a prose-only reminder.
- The durable source of truth for the interruption decision starts in the debug
  artifact, not in chat memory.
- The current debug artifact must carry:
  - interrupt id
  - risk class
  - seam summary
  - disproving observation
  - what local reasoning cannot prove
  - generalization pressure
  - next step / interruption decision
- Risk classes that imply a forced interruption in this slice are:
  - `external-seam`
  - `host-disproves-local`
  - `repeated-symptom`
- `operator-visible-recovery` and `contract-freeze-risk` are still recorded, but
  this first slice treats them as review signals rather than automatic hard
  blocks unless a stronger forced-interrupt class is also present.
- When a forced interruption is present, the debug artifact next step cannot
  remain plain `impl`; for this first slice it must become `spec`.
- when a forced interruption is present, the visible carry-forward artifact for
  this slice is still a spec artifact keyed by the same interrupt id.
- a refreshed spec artifact only clears the block when it explicitly records:
  - `Interrupt Source`
  - `Seam Summary`
  - `Chosen Next Step`
  - `Impl Status`
  - `Impl Status Reason`
  - `What Disproving Observation Is Resolved`
- the closeout block is current-slice-affine: it should trigger only when the
  current slice touched the current debug artifact or its named handoff artifact
  rather than letting one stale `debug/latest.md` block unrelated work forever.
- `run-slice-closeout.py` will treat missing or unresolved spec carry-forward as
  the concrete block condition for now.
- This slice does not add a standalone `premortem` durable artifact; it uses
  refreshed spec/debug artifacts as the visible carry-forward seam.
- the planner must not trust debug self-report alone when stronger evidence is
  already present. `host-disproves-local` and `repeated-symptom` evidence must
  auto-reject plain `impl`.

# Probe Questions

- Should a later slice let `plan_risk_interrupt.py` inspect spec artifacts and
  clear the block when a spec explicitly resolves the interruption decision?
- Should the planner eventually key off implementation-diff evidence, not just
  debug latest + spec refresh?
- Should `premortem` gain a dedicated durable artifact once the trigger policy
  is stable?

# Deferred Decisions

- a global planner for all review-worthy decisions
- a standalone premortem artifact schema
- automatic repeated-seam detection from git history or code ownership
- extending the same required interrupt contract to `release`, `quality`, or
  other caller skills

# Non-Goals

- solving all anti-myopia cases in one slice
- inferring external seam risk from arbitrary code diffs alone
- teaching `debug` to fix the bug itself
- introducing product-specific seam catalogs into public skills

# Deliberately Not Doing

- relying on `impl` closeout prose alone
- keeping seam risk as a free-form note with no machine-readable trigger
- blocking closeout on a new hidden runtime file that future maintainers will
  not read
- declaring `#52` fixed without a repo-owned gate

# Constraints

- keep the public-core wording concise enough for retrieval
- prefer validator/planner enforcement over essay-length instructions
- keep the carry-forward artifact visible and checked in
- avoid a design that requires every implementation slice to create a new mode
  or fill out a large template

# Success Criteria

- `debug` artifacts have canonical sections for seam risk and interruption
  decision, with validator-backed required fields
- the debug scaffold emits that structure by default
- `plan_risk_interrupt.py` emits a stable JSON/text decision from the current
  debug artifact
- `impl` bootstrap checks the planner before the next ordinary patch continues
- `run-slice-closeout.py` blocks when a pending forced interruption exists and
  no spec artifact with the matching interrupt id was refreshed in the current
  slice
- `debug`, `impl`, and `spec` public contracts visibly agree on the new
  planner-driven handoff
- repo-owned tests and dogfood evidence cover the new contract

# Acceptance Checks

- `pytest -q tests/test_debug_artifact.py tests/test_debug_scaffold.py tests/test_risk_interrupt.py`
- `python3 scripts/check-skill-contracts.py --repo-root .`
- `python3 scripts/validate-skills.py --repo-root .`
- `python3 scripts/validate-public-skill-dogfood.py --repo-root .`
- `python3 scripts/check-doc-links.py --repo-root .`
- `./scripts/check-markdown.sh`
- `./scripts/check-secrets.sh`
- `python3 scripts/run-slice-closeout.py --repo-root . --plan-only`

# Premortem

- Likely wrong move: add a planner that only echoes the debug artifact without
  creating a real blocking condition before the next patch.
- Likely wrong move: add a block that can be satisfied by any doc churn instead
  of by a refreshed spec handoff.
- Likely wrong move: let the debug artifact self-report plain `impl` even after
  a host observation already disproved local reasoning.
- Tightening move for this slice: require a structured interrupt decision in the
  debug artifact, run the planner before ordinary impl continues, and block
  closeout until a spec artifact with the same interrupt id explicitly clears
  the interruption.

# Canonical Artifact

- `charness-artifacts/spec/external-seam-risk-interrupt.md`

# First Implementation Slice

1. Extend debug artifact schema, scaffold, and validator with seam-risk and
   interrupt-decision sections plus interrupt id.
2. Add `scripts/plan_risk_interrupt.py` and a small shared parser/helper.
3. Wire the planner into `impl` bootstrap and `run-slice-closeout.py`.
4. Update `debug`, `spec`, and `impl` contracts plus contract pins/dogfood so
   spec carry-forward fields are explicit.
5. Add focused tests for the new artifact and planner behavior.
