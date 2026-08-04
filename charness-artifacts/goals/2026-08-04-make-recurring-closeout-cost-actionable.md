# Achieve Goal: Make closeout cost actionable, then repair #496

Status: active
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: G — plan, push, and release the final state in order.
- Current slice intent: complete claims/release review, run the final
  verification lock, then use the separately verified push/CI and release
  readback boundaries.
- Next action: commit the locally proven bundle, bind the exact
  `v3.1.1..candidate` scope, then perform the ordered push/CI and
  release/readback boundaries.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Turn the recurring closeout-cost signal behind #503 into an honest, actionable operator decision surface: identify which repeated proof cost is real, who owns it, what evidence a proposed optimization must preserve, and implement the smallest reversible improvement without weakening a gate or treating a green result as proof that the cost is harmless. Close only when a different observer can distinguish measured recurrence, the chosen intervention, and explicit non-claims.

## Problem

The repo already records recurring closeout-runtime and over-slice signals, but
the signal does not yet answer the operator's useful question: “what safe local
decision should change because of this?” The evidence also mixes recurrence
counts, elapsed seconds, rolling retention, and changing corpora. A broad run
can be expensive and still valuable when it catches a defect, so runtime alone
is not permission to remove proof.

## Current Slice

The work is sequential, not parallel: first complete the local #503 cost-
decision track, then start the independent #496 hollow-refill predicate track.
Each track has its own owner, evidence, and fresh-eye review. Only after both
tracks pass their local proof floors does the final bundle become eligible for
push and release.

## Fixed Decisions

- No gate is weakened, skipped, or made non-blocking solely because it is slow.
- #503 is completed first; #496 starts only after the #503 local closeout is
  complete. Their evidence and implementation scopes must not be mixed.
- The #503 and #496 working bundles are local and reversible. The final bundle
  may push only after both tracks pass their local proof floors and the final
  quality/release gates run against the final state; release publication may
  happen only after independent remote commit/CI readback for the pushed SHA.
- Remote issue closure is not included unless separately requested; a pushed or
  released state must not be described as an issue being closed.
- A report-only result is incomplete unless it records either the chosen local
  action or an evidence-backed “no safe change” disposition with a reopen
  trigger.

## Probe Questions

- Which single cost class is selected within one comparable local cohort? The
  answer must state runner/profile, command family, window start/end, population
  query, denominator, exclusions, retained versus lost records, recurrence
  count, and elapsed-seconds summary. Peak seconds and recurrence count must not
  be ranked as if they were the same unit.
- Who produces the signal, who consumes it, which surface owns the decision, and
  what exact operator action changes when the signal fires?
- Which reversible option preserves the proof boundary? If the answer is “none,”
  what evidence rules out a safe change and when should the question reopen?
- Is the corpus-denominator capability part of the same producer/consumer
  contract as #503, or does it need a separate owner and issue/spec?
- After #503 closes locally, what exact semantic invariant, owner, and
  axis-varying counterexample define #496's hollow-refill predicate? Which
  positive and negative controls prove the repair rather than its warning text?
- At the final bundle, which independent observer and channel will verify the
  pushed commit, CI, and release result separately from the local gate exit code?

## Deferred Decisions

- Cross-machine normalization and a global ranking of all cost classes are
  deferred until a named consumer needs them.
- A new per-run telemetry schema is deferred until a consumer, run identity,
  retention rule, and stale-state behavior are named.
- Gate scheduling, blocking-gate changes, and any proof-floor reduction require
  a later goal with an observed escape, false-fire cost, preservation invariant,
  and fresh proof.
- Relief observed in a later real goal is a follow-up measurement, not a hidden
  completion requirement for this bounded local goal.
- The exact #496 implementation shape remains deferred until its own local
  reproduction and owner read; #503's solution must not preselect it.
- The exact release target, version/tag mechanics, and publication procedure
  remain deferred to Slice G's release plan; the operator's authorization is
  already limited to that final phase.

## Constraints

- The decision record must preserve the distinction between measured cost,
  inferred opportunity, chosen intervention, and non-claim.
- Source and generated/plugin surfaces must be synchronized before validators
  read them.
- The final local proof must use a channel different from the one that produced
  the proposed intervention.
- Push/release is the final irreversible boundary: its authorization is
  conditional on the gates. The operator explicitly granted this final phase in
  this session; the grant does not cover issue closure or any earlier mutation.
  Its success is provisional until a different observer and different evidence
  channel read back commit, CI, and release state.
- The exact release target, version/tag mechanics, and publication procedure
  are decided in Slice G's release plan before any version/tag/publish mutation;
  they are not invented in S7's acceptance prose.

## Success Criteria

- S1: one selected cost cohort has a reproducible metric contract: profile and
  command, window, population/denominator, exclusions, retention, recurrence,
  and elapsed-seconds summary.
- S2: a producer/consumer/owner map names the final reader and the decision it
  can change; “telemetry exists” alone does not satisfy this criterion.
- S3: a local replay or fixture demonstrates the selected action and its
  expected evidence, or demonstrates the evidence-backed no-safe-change path.
  The no-change path must carry a durable option comparison: recorded
  instance/cohort, candidate actions, preservation invariant, why each candidate
  is unsafe or premature, named owner, and measurable reopen trigger.
- S4: preservation checks show no false green, hidden failure, stale-record
  reuse, or truncation of the operator receipt for the selected path.
- S5: the result records expected local relief or explicitly says that relief is
  not yet measurable, with a follow-up trigger rather than an invented claim.
- S6: #496 has a separately recorded reproduction, semantic invariant, owner,
  axis-varying counterexample, and positive/negative proof before its repair is
  considered complete.
- S7: only after S1–S6 pass and a release critique/claims review is recorded,
  push the final state; independently read back the remote commit and CI for
  that exact SHA; only then publish the release/tag if the release procedure
  requires it; and independently read back release/tag/version and target
  commit. Issue CLOSED is not claimed unless separately verified.

## Acceptance Checks

| Criterion | Required check | Evidence that passes |
| --- | --- | --- |
| S1 | Mine/replay the local telemetry and inspect a checked-in decision record | The record contains all S1 fields and uses one comparable unit/window; missing or rotated records are visible |
| S2 | Boundary-ownership review by a fresh observer | Producer, final consumer, owning surface, and changed operator decision agree |
| S3 | Deterministic fixture or replay plus focused tests and a durable option comparison | The chosen action or no-safe-change branch is observable, reversible, owned, and has a reopen trigger |
| S4 | Negative controls for failed emission, stale/rotated state, and output truncation; broad proof when a verdict surface changes | Each failure remains visible and the final receipt still names recovery; no local green is treated as remote proof |
| S5 | Closeout claims review against the record and the selected cohort | Relief is measured, or the non-claim and reopen trigger are explicit |
| S6 | Fresh #496 reproduction and boundary-ownership review, then positive/negative controls | The predicate tracks the semantic invariant and distinguishes the axis-varying counterexample |
| S7 | Release critique/claims review; gated push; independent remote commit/CI readback; then gated release and independent release readback | Release publication occurs only after CI is observed for the exact pushed SHA; remote issue closure remains an explicit non-claim |

## Non-Goals

- Do not weaken, skip, or silently downgrade a proof gate merely because it is
  slow.
- Do not turn rolling telemetry into a per-run receipt until a named consumer,
  run identity, retention rule, and stale-state behavior are defined.
- Do not run #503 and #496 in parallel, or let #503's telemetry decision
  preselect #496's predicate repair.
- Do not push or release from either local track; those actions belong only to
  the final bundle after both tracks pass.
- Do not include production/live proof or remote issue closure unless separately
  requested and verified.
- Do not promise a speed improvement before the chosen cost class has a measured
  baseline and an owner who can explain what evidence the improvement preserves.

## Boundaries

- North Star boundary: judgment support is the default; a new blocking tooth is
  allowed only after a recorded escape, a named false-fire cost, and evidence
  that the tooth catches the right invariant.
- Each working bundle is local and reversible. Push/release is allowed only in
  the final bundle after #503 and #496 local proof; any instance apply or issue
  close requires a separate boundary and readback.
- The chosen report or packet must distinguish measured recurrence from a
  proposed intervention and from what remains unproven.
- If the corpus denominator is part of the solution, its owner must be named;
  it must not be silently assigned to #503 just because the same retro exposed
  both problems.

## User Acceptance

The user can inspect one durable local report or packet and answer, without
re-running the entire session:

1. Which closeout-cost class recurs, over what measured window and denominator?
2. Who produces the signal, who consumes it, and what decision can it change?
3. What smallest reversible intervention was chosen, or why is “no safe change
   yet” the honest result?
4. Which proof channels show that the intervention did not create a false green,
   hide a failed run, or move a receipt behind a truncation boundary?

Completion requires the full sequence: #503's local handoff checkpoint, #496's
independent local reproduction/repair proof, and S7's ordered push/CI-readback/
release/release-readback evidence. Either track may record an evidence-backed
no-safe-change decision, but #503 alone cannot complete this goal. A clean run
by itself is not acceptance, and a later real-world relief claim is not required
for this bounded goal.

## Agent Verification Plan

### Low-Cost Checks

- Read the existing closeout emitter, telemetry miner, quality artifact, and
  #503 evidence together; map producer, consumer, denominator, retention, and
  the exact selected cohort.
- Run the existing deterministic telemetry/quality validators and a small
  fixture or replay for the selected recurrence class; add a narrow validator
  only if the current tools cannot check S1–S4.
- Check source/generated/plugin surfaces before any validator reads them.

### High-Confidence Checks

- Add the smallest focused tests for the selected contract, including a changed
  corpus, repeated run, stale-state, and failure-recovery case where relevant.
- Obtain a bounded fresh-eye critique of the proposed intervention and, if the
  change alters verdict logic, a second review round that reads the repairs.
- Run the broad standing proof at the bundle boundary and record measured cost
  separately from correctness.
- For the #503→#496 handoff, require the checked-in local closeout record named
  in Slice D and a fresh observer's acceptance before Slice E begins.
- Before any final version/tag/release mutation, run release-specific critique
  and claims review; push and release are separate proof steps.

### External Or Live Proof

- Deferred until the final bundle: after #503 and #496 local proof and a release
  critique/claims review, push the final state under the user's conditional
  approval. Then a different observer/channel reads back the remote commit and
  CI for that exact SHA. Only after that readback may the release/tag step run;
  a separate observer/channel then reads back release/tag/version and target
  commit. Do not claim issue CLOSED unless a separate closeout floor and state
  readback are run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Lock #503's recurring-cost fact and owner | #503 contains recurrence signals but not yet a safe intervention boundary | S1/S2 record: one cohort, complete denominator/window/retention, producer-consumer map, explicit non-claims | completed |
| B | Choose #503's smallest control surface | The remedy could be a report, packet, scheduling change, or no change; choosing by intuition risks another proxy | option comparison, named consumer, preservation invariant, S3 decision, fresh-eye critique | completed |
| C | Implement and exercise #503's reversible local intervention | The goal needs a useful capability, not a new metric without a decision path | focused tests/fixtures, source-export sync, S4 negative controls, changed-line proof where applicable | completed |
| D | Close #503 locally before changing scope | Sequential work prevents #503's cost model from contaminating #496's semantic predicate decision | `charness-artifacts/issue/2026-08-04-issue-503-local-closeout.md` records selected cohort/owner, action or option-comparison no-change result, residuals, exact changed paths, explicit “no predicate recommendation for #496,” and fresh-observer acceptance; no unresolved shared owner; no remote claims; this checkpoint unlocks E | completed |
| E | Reproduce and frame #496 independently | #496 is an independent hollow-refill predicate problem and must not inherit #503's answer; the known starting symptom is an inert empty-string default such as `commands.dry_run` reported as a refill and a warning that recommends dropping a real configuration block | reproduction of the end-to-end symptom, semantic invariant, axis-varying counterexample, producer/consumer map, explicit #503 handoff non-claim, critique | completed |
| F | Repair and prove #496 locally | A warning or type-shaped proxy must not be mistaken for the semantic fix | focused positive/negative tests, changed-line proof, second review if verdict logic changes, local closeout | completed |
| G | Plan, push, and release the final state in order | The irreversible boundary belongs after both local tracks are proven and CI is read back after push | release critique/claims review and target plan, final quality gate, gated push, independent remote commit/CI readback, gated release/tag, independent release/tag readback, explicit remote issue non-claims | in progress |

## Operator Decision Queue

none — the operator resolved the activation choices in this session: run #503
first, then #496; keep both working tracks local; and reserve push/release for
the final bundle after all local proof floors pass. Remote issue closure remains
out of scope unless separately requested.

## Coordination Cues

- Routing: prove + release — claims review is recorded; final broad proof,
  frozen candidate scope, and the ordered remote/public readbacks remain.
- `Gather: n/a — this draft uses checked-in handoff, North Star, retro, and
  issue evidence; no new external source was introduced.`
- `Release: planned — operator-granted final phase only; after #503 and #496
  local proof, push and independently read back commit/CI, then publish and
  independently read back release/tag state.`
- `Issue closeout: n/a — remote issue closure was not requested; push/release
  must not be narrated as issue CLOSED.`

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED by the operator in this session — run
  #503 first and #496 second; keep both working tracks local; and use the
  explicitly granted final phase for push/release only after all local gates.
  Release/tag target and procedure must still be planned and critiqued in Slice
  G before mutation. No remote issue close is included.

## Slice Log

### Slice 1: Lock #503 cohort and owner

- Objective: Select one exact gate-runtime cohort from the retained closeout stream, make its denominator/window/retention/elapsed-seconds contract explicit, and assign the decision owner before choosing an intervention.
- Why this approach: The recurring signal mixed gate seconds, recurrence counts, over-slice run length, and changing retention. A comparable unit and owner are prerequisites for a safe local decision.
- Commits: No commit yet; this slice adds the checked-in evidence record and gathers #503 source context. Implementation remains in Slice B.
- What changed: charness-artifacts/issue/2026-08-04-issue-503-slice-a-cohort.md; charness-artifacts/gather/2026-08-04-issue-503-closeout-cost.md and gather/latest.md; goal status/frame; no product or gate behavior changed.
- Alternatives rejected: Rejected ranking over-slice run length against elapsed seconds; rejected attributing historical records to a runner/profile absent from schema; rejected treating 16 matching entries as 16 successful suite runs; rejected weakening or moving the gate from recurrence alone.
- Targeted verification: Ran mine_closeout_telemetry.py against the local stream; directly inspected all 1,325 retained schema-1 records and the 16 exact matching entries; ran inventory_ci_recoverable_gates.py, render_runtime_summary.py, inventory_standing_test_economics.py, and inventory_structural_waste.py as advisory option evidence; authenticated gh issue read was gathered durably; delegated cohort review returned findings and reviewer_boundary_fingerprint.py verify reported clean.
- Test duplication pressure: No tests added or expanded in this record-only slice; no duplicate-pressure sample is applicable.
- Critique: Delegated fresh-eye cohort review: parent-delegated, clean boundary fingerprint. Blockers folded: over-budget entries are not successful suite runs; historical runner/profile provenance is unavailable; the generic gate-implementation owner was not evidence of assignment. Cohort key and report-surface candidate approved as safe for Slice B.
- Off-goal findings: No new issue. The gathered #503 issue source is context for this in-goal track; #496 remains independent and untouched.
- Lessons carried forward: A recurrence stream needs a query and denominator before a remedy. Treat missing provenance and bounded rotation as explicit unknowns, and keep the decision owner separate from the code that emits the signal.
- Metrics: Local host tool metrics are not exposed. Stream window: 1,325 valid records; selected cohort 16 entries; elapsed total 6257.15s, median 447.03s, peak 475.46s, budget 120.0s; over-budget excess 4337.15s. Host-level token/time/tool counts are unclaimed.

### Slice 2: Choose #503's smallest proof-preserving control surface

- Objective: Select and implement the smallest reversible local decision surface for the exact #503 gate-runtime cohort, with a named owner, preservation invariant, falsifier, and reopen trigger.
- Why this approach: The cohort evidence supports a safer report/decision receipt, but does not establish a proof-preserving optimization seam or permission to move the gate. An opt-in receipt makes the next owner decision repeatable without changing proof behavior.
- Commits: No commit yet; Slice B evidence and implementation will be committed with the subsequent local closeout bundle.
- What changed: skills/public/retro/scripts/mine_closeout_telemetry.py; plugins/charness/skills/retro/scripts/mine_closeout_telemetry.py; skills/public/retro/references/closeout-telemetry.md; plugins/charness/skills/retro/references/closeout-telemetry.md; tests/quality_gates/test_retro_closeout_telemetry_mining.py; charness-artifacts/issue/2026-08-04-issue-503-slice-b-decision.md; charness-artifacts/critique/2026-08-04-slice-b-503-metric-report-code-critique.md and its current packet.
- Alternatives rejected: Selected an opt-in detail receipt over gate movement, CI relocation, automatic scheduling, or a new telemetry schema. Deferred a bounded optimization experiment because no named lower-layer seam and separate correctness channel is established. Deferred a report-free no-change record because the next decision needs a durable rerunnable receipt. Kept #496 predicate work separate.
- Targeted verification: The second bounded reviewer read the repaired verdict surface; reviewer_boundary_fingerprint.py verify was clean. Focused standing pytest passed 15 tests. The detail fixture covers malformed, blank, foreign, unsupported-schema, missing-stream, custom recurrence threshold, multiple matching entries, non-finite elapsed values, missing budgets, and default-output parity. Source/plugin miner mirrors are byte-identical. A real --detail replay reported 1,325 retained records, the exact 16-entry cohort, 12 completed and 4 failed parent records, finite paired elapsed summaries, and 4,337.15 seconds excess over the 120-second budget.
- Test duplication pressure: Ran check_dup_ratchet.py --summary as the cheap duplicate-pressure sample. It passed clean with no new fixable-eligible families; the first transient family was removed by sharing the timestamp list. Existing advisory reductions remain advisory and were not rebaselined.
- Critique: Delegated first critique used three bounded angles plus a separate counterweight, with clean boundary fingerprints. The required second repair-read review found four semantic blockers: raw-line re-aggregation under custom --recur-min, non-finite peak leakage, entry-based parent status counts, and mispaired elapsed/budget excess. All four were repaired and regression-tested. The repository's two-round cap records those round-two repairs as accepted-unreviewed; final broad proof remains required.
- Off-goal findings: No #496 predicate recommendation. No gate, emitter schema, CI placement, release, remote issue closure, or cross-repo claim was introduced.
- Lessons carried forward: A decision surface must preserve the evidence boundary it summarizes: audit before aggregation, retain parent-record identity, reject non-finite measurements, and keep elapsed/budget pairs intact. A detailed report is useful only when its owner action and falsifier live in a durable record.
- Metrics: Local host tool metrics are not exposed. The Slice B measurement snapshot was 16 entries / 1,325 retained records; a later live replay is 16 entries / 1,326 retained records through 2026-08-04T01:16:44Z, with 16 finite observations totaling 6,257.15s, median 447.03s, peak 475.46s, and 4,337.15s paired excess over budget. Slice B itself claims 0 seconds relief measured; reopen after a later retained window has at least two occurrences of the exact key.

### Slice 3: Implement and exercise #503's reversible local intervention

- Objective: Exercise the selected opt-in detail receipt across the failure classes and generated surfaces required to prove it remains advisory, finite, schema-bounded, and default-compatible.
- Why this approach: The report is only useful if it cannot turn malformed, unsupported, missing, non-finite, or multi-entry telemetry into a false clean or misattributed verdict. This slice supplies the negative controls and pre-lock quality proof before local #503 closeout.
- Commits: No commit yet; implementation, evidence artifacts, and the local #503 carrier remain one meaningful work unit.
- What changed: The Slice B miner, references, focused tests, dogfood registry entry, decision record, critique packet/artifact, and goal log are now exercised as one generated/source evidence surface. No emitter, gate, CI, release, or remote issue state changed.
- Alternatives rejected: Did not run Cautilus because the repo adapter is ask-before-run and the planner says no live proof is required for this preserve-class change. Did not run broad pytest in the pre-lock slice because reviewer-driven edits could stale it; the locked broad bundle remains mandatory later. Did not accept the duplicate-ratchet transient family; refactored the repeated timestamp expression instead.
- Targeted verification: run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review completed. Structural/artifact preflight, packaging, committed packaging, doc links, command docs, evidence durability, markdown, secrets, Cautilus validators, skill validators, py_compile, ownership overlap, ergonomics, dup-ratchet, public-skill validation/dogfood, critique artifacts, ruff, Python lengths, attention visibility, test-copy invariants, boundary-bypass ratchet, shell, scan hygiene, and browser-orphan guard all passed. Focused telemetry-miner standing pytest passed 15 tests; source/plugin byte parity passed; live detail replay passed.
- Test duplication pressure: The cheap duplicate-pressure sample initially caught one new repeated timestamp-expression family. The implementation was refactored to compute one matching timestamp list; rerun check_dup_ratchet.py --summary passed clean with zero new fixable-eligible families.
- Critique: Slice B's bounded critique and capped second repair-read are carried forward. The closeout gate accepted the current artifact/packet shape and the explicit retro dogfood contract refresh. A separate fresh observer is still required for the #503 local carrier before #496 starts.
- Off-goal findings: No #496 predicate recommendation; no remote issue closure; no Cautilus execution; no release or push; no claim that the report produced runtime relief.
- Lessons carried forward: A proof surface's closeout must make both its positive path and its refusal classes visible. A pre-lock gate can be useful without pretending to be the final broad proof, provided the deferred proof is named and remains a hard phase barrier.
- Metrics: Local host tool metrics are not exposed. Slice C claims 0 seconds measured relief. Focused test result: 15 passed in 1.61s. Slice C replay: 16 entries / 1,326 retained records through 2026-08-04T01:16:44Z; 6,257.15s total finite elapsed; 4,337.15s paired excess over budget.

### Slice 4: Close #503 locally before changing scope

- Objective: Carry the selected #503 cohort, owner, reversible action, residuals, exact changed paths, and a fresh-observer acceptance into a local closeout carrier before starting the independent #496 track.
- Why this approach: A local decision surface is not complete until a different observer can distinguish its measured recurrence, selected intervention, remaining unknowns, and explicit boundary against #496 and remote state.
- Commits: No commit yet; the #503 carrier and all supporting artifacts remain bundled with the implementation before the first meaningful commit.
- What changed: charness-artifacts/issue/2026-08-04-issue-503-local-closeout.md plus current snapshot clarifications in Slice A, Slice B, and the goal. No product or remote issue state changed.
- Alternatives rejected: Did not close the remote GitHub issue; the carrier explicitly keeps it open and out of scope. Did not begin #496 in parallel. Did not hide the one-record stream growth: the 1,325 Slice A snapshot and 1,326 live replay are both named with their windows.
- Targeted verification: Delegated fresh-eye reviewer Boole reread the carrier and supporting records after correction and accepted with no remaining blocker. reviewer_boundary_fingerprint.py verify returned parent-attributed with drift: [] for the review window. The reviewer confirmed 1,326 current records through 2026-08-04T01:16:44Z, statuses 949/248/129, unchanged 16-entry cohort, and 4,337.15s paired excess. The pre-lock deterministic closeout and focused 15-test proof remain the implementation evidence.
- Test duplication pressure: No new code was added in this checkpoint; the Slice C duplicate-pressure sample remains clean with zero new fixable-eligible families.
- Critique: Fresh observer required two factual repairs—live population snapshot and carrier self-inclusion in exact changed paths—and then accepted the repaired carrier. This is a separate closeout acceptance, not a same-agent substitute for the earlier verdict-logic review.
- Off-goal findings: Remote issue closure, #496 predicate semantics, release, push, CI, and runtime relief remain unclaimed. The local carrier explicitly says no #496 predicate recommendation.
- Lessons carried forward: A closeout snapshot must be time-bound when the source stream can grow during the goal. Durable carriers should name both the evidence snapshot and the carrier itself in changed-path inventory so a fresh observer can audit the exact boundary.
- Metrics: Local host tool metrics are not exposed. Current live stream: 1,326 retained schema-1 records, 949 completed, 248 failed, 129 blocked; selected cohort unchanged at 16 entries, 12 completed and 4 failed parent records, 6,257.15s total, 4,337.15s paired excess. #503 local relief remains 0 seconds measured.

### Slice 5: Reproduce and frame #496 independently

- Objective: Reproduce the hollow-refill warning end to end, identify its producer and consumer, state the semantic invariant, and distinguish the inert command-default axis from a meaningful empty scope before repair.
- Why this approach: #496 is a separate semantic predicate problem. The #503 telemetry decision must not preselect a repair for a quality-policy warning whose observed empty value changes meaning across policy fields.
- Commits: No commit yet; this diagnosis and its repair remain one local implementation bundle.
- What changed: charness-artifacts/gather/2026-08-04-issue-496-hollow-refill.md; charness-artifacts/debug/2026-08-04-debug-review-followup-2.md; charness-artifacts/critique/2026-08-04-slice-e-496-hollow-refill-semantic-repair-critique.md and refreshed packet; goal frame. The source repair is recorded in Slice F, not attributed to this framing slice.
- Alternatives rejected: Rejected a generic empty-string/list/map suppression because prompt_asset_policy.exemption_globs=[] is a real scan-scope boundary. Rejected changing the generic recursive helper without policy context. Rejected carrying #503's cost/report decision into #496. Deferred sub-key deliberately_absent syntax and top-level symmetry.
- Targeted verification: Authenticated issue evidence was gathered durably after the public typed fetch hit a captcha. The exact partial mutation_testing fixture reproduced commands.dry_run and commands.sample plus the harmful whole-block warning; the prompt-asset partial fixture reproduced a meaningful empty exemption scope. Debug validation passed. Three bounded code angles plus a counterweight returned the field-aware producer/consumer ownership and axis-varying counterexample; all four pre-implementation boundary windows verified clean.
- Test duplication pressure: No new duplication family was introduced by the framing artifacts; code duplication pressure is recorded with the Slice F implementation proof.
- Critique: The pre-implementation critique classified exact mutation command filtering, safe leaf-level warning text, end-to-end proof, and the axis counterexample as act/bundle items. It explicitly deferred a generic semantic-emptiness framework, top-level symmetry, and sub-key absence vocabulary.
- Off-goal findings: #503 remains locally closed with no predicate recommendation for #496. Remote issue closure, release, push, and Cautilus execution remain out of scope for this slice.
- Lessons carried forward: A value-level recursion report is not the semantic invariant. The owning policy boundary must carry the narrow exception, while the warning consumer must preserve supplied siblings when it cannot represent sub-key absence.
- Metrics: Local host tool metrics are not exposed. #496 reproduction: partial full+summary commands yielded the two hollow leaves before repair; prompt_asset_policy empty exemption scope remained reportable. No runtime relief or broad correctness claim is made here.

### Slice 6: Repair and prove #496 locally

- Objective: Repair the hollow-refill predicate at the mutation policy boundary, replace destructive nested warning advice, synchronize the shipped plugin surface, and prove positive and negative controls without broadening semantic emptiness.
- Why this approach: The diagnosis established two owners: the mutation bootstrap report owns the exact inert-leaf exception, while the warning renderer owns the unsafe whole-block remedy. A narrow repair preserves #493 nested truth and real mutation commands.
- Commits: No commit yet; the #503 and #496 artifacts, source/plugin changes, tests, and closeout carriers remain one final local bundle until the verification lock.
- What changed: scripts/quality_bootstrap_lib.py; scripts/quality_bootstrap_absence.py; plugins/charness/scripts/quality_bootstrap_lib.py; plugins/charness/scripts/quality_bootstrap_absence.py; tests/quality_gates/test_quality_bootstrap.py; tests/quality_gates/test_quality_bootstrap_absence.py; refreshed #496 debug/critique/goal artifacts. The generic recursive helper and unrelated policy defaults were not changed.
- Alternatives rejected: Rejected a generic semantic-emptiness abstraction, top-level symmetry, changing the recursive helper, and a new sub-key absence vocabulary. Rejected warning-only repair because the hollow leaves would remain in the operator receipt. Kept full and summary outside the allowlist; only missing summary is directly asserted because full is structurally outside the suppression set.
- Targeted verification: Generated source/plugin mirrors were synchronized before proof. The focused standing suite passed 85 tests, including exact full+summary suppression, missing summary reporting, explicit empty command slots, report_paths and prompt_asset_policy empty-scope controls, fresh-bootstrap silence, warning wording, and complete source/plugin JSON plus stderr parity. The required second repaired-surface reviewer found one proof gap; after a clean boundary verify, the test now compares the complete payload and reran green. Round 2 is capped and the repair is recorded accepted-unreviewed. A separate fresh observer accepted the #496 local carrier after two wording corrections; the final reread boundary was clean.
- Test duplication pressure: Ran the focused quality bootstrap/absence/policy-merge standing targets: 85 passed in 1.87s. The earlier duplicate-ratchet sample remains clean with zero new fixable-eligible families; no new code duplication was introduced by the parity assertion.
- Critique: Pre-implementation critique returned F1–F6 with exact allowlist, safe warning, end-to-end controls, and axis counterexample. Round 2 read the repaired source/plugin/test surface and accepted the implementation except for complete-payload parity; that blocker was fixed after reviewer boundary verification and is accepted-unreviewed under the two-round cap. The carrier acceptance reviewer also required an explicit #503-to-#496 non-claim, then accepted the corrected carrier with no remaining blocker.
- Off-goal findings: #503's selected report decision remains unchanged and supplies no #496 predicate recommendation. No gate was weakened, no emitter schema changed, no Cautilus evaluation ran, no remote issue was closed, and no push/release occurred.
- Lessons carried forward: A verdict-logic repair owes a second review of the repaired surface. A selected-key parity test can leave an unproven receipt; compare the complete consumer payload and stderr across source and shipped entrypoints.
- Metrics: Local host tool metrics are not exposed. Focused result: 85 passed in 1.87s. Measured #496 runtime relief is not applicable; the repair changes report truthfulness and warning safety, not the closeout gate or execution cost.

### Slice 7: Freeze local proof and prepare the ordered release boundary

- Objective: Complete the release critique/claims review and final local proof,
  then preserve the exact conditions required before any remote or public state
  change.
- Why this approach: S7 is an irreversible boundary. The release record must
  distinguish the full unreleased candidate from this goal's two slices and
  keep local green, remote CI, public release, installed refresh, and baton
  observations separate.
- Commits: No commit yet; the local bundle is ready for its first meaningful
  commit after packet rebinding.
- What changed: release critique and packet, v3.2.0 notes, delegated claims
  review, midpoint claims update, and the final verification-lock record. No
  version/tag/push/public-release mutation has occurred.
- Alternatives rejected: Did not run Cautilus because policy is ask-before-run
  and the deterministic dogfood decision is recorded. Did not call the public
  release helper before its branch-push/CI ordering was resolved. Did not claim
  current stream population as a fixed historical number; the #503 carrier's
  1,326-record snapshot remains time-bound.
- Targeted verification: Release critique round 2 returned four findings with
  clean boundary windows; the required rollback, compatibility, source-tree
  probe-label, and release-boundary wording repairs are recorded. The distinct
  claims observer returned clean boundary verification and accepted the notes
  subject to four pre-ship conditions. The final verification lock completed
  with all recorded structural, synchronization, validation, standing-pytest,
  scan-hygiene, and browser-orphan checks passing; durable broad-proof record:
  `.charness/closeout/broad-pytest-proof.json`, 46.31 seconds.
- Test duplication pressure: The final lock's duplicate-ratchet and Python
  length checks passed; the near-limit warnings remain advisory and are not
  disguised as a clean code-size result.
- Critique: The clean release round found that the release helper's current
  tag-before-CI ordering cannot satisfy S7 by itself. The claims review found
  no incorrect local figure, but required future wording until remote/public/
  installed readbacks exist. These are active release gates, not deferred
  implementation notes.
- Off-goal findings: No issue was closed, no Cautilus evaluation ran, no gate
  was weakened, and no remote/public/install state was changed.
- Lessons carried forward: Freeze the all-unreleased candidate and notes before
  publishing; use a separate branch/CI observer before tag/public release; keep
  post-publication install and baton evidence as observations rather than
  terminal-green completion.
- Metrics: Local host tool metrics are unavailable. Final lock elapsed time was
  46.31 seconds in the durable broad-proof record; no remote CI or publication
  timing is claimed yet.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `docs/design-north-star.md` — judgment first, teeth only where a wrong
   answer escapes, and independent observation at irreversible boundaries.
2. `docs/handoff.md` — #503's recurring closeout-runtime/over-slice signal and
   the remaining #496 boundary.
3. `charness-artifacts/retro/2026-08-04-session-retro.md` — measured recurrence,
   waste classes, and the seven improvement dispositions from the completed
   goal.
4. `charness-artifacts/critique/2026-08-04-decide-where-a-recurring-lesson-lives-disposition-review.md`
   — the prior claims review's separation of #503 from the corpus-denominator
   capability.

## Interview Decisions

- Scope: run #503 first and #496 second in one sequential goal, with separate
  slice contracts and evidence packets. This prevents parallel scope creep while
  preserving a single final push/release boundary.
- Control type: prefer an evidence/decision surface before a blocking gate or
  automatic skip. A speed-driven gate change is rejected until an observed
  escape, false-fire cost, and invariant proof exist.
- Proof budget: use cheap deterministic checks per slice and one broad bundle
  proof; do not repeat the full suite after every documentation-only adjustment.
  The broad run remains required when the corpus, verdict logic, or generated
  consumer changes.
- External boundary: keep push/release out of both working tracks and perform it
  only in the final bundle after local proof and a different-channel readback
  plan are ready. Remote issue closure remains excluded.

## Plan Critique Findings

Three named angle reviewers and one separate counterweight reviewed the draft
before lock-in. The reviewers found three act-before-activation repairs: bind a
fresh packet after the draft stops changing, make the cohort/denominator and
producer/consumer contract explicit, and require same-slice local evidence of an
action or an evidence-backed no-safe-change result. They also found the
#503-first scope must remain an explicit operator confirmation. The counterweight
classified a later real-goal relief measurement as valid-but-defer and rejected
inventing a unified telemetry schema or weakening gates without a recorded
escape. Those findings are folded into Problem, Fixed/Probe/Deferred Decisions,
Success Criteria, Acceptance Checks, and the activation discussion above.

Fresh-Eye Satisfaction: parent-delegated — three angle reviewers plus one
separate counterweight returned findings; all four reviewer boundary fingerprints
verified clean before parent writes. The final packet must be regenerated after
any further draft edit.

Scope-update note: the operator later resolved the pending choices as sequential
#503 then #496, with final push/release only after both local proof tracks. This
requires a fresh critique of the expanded #496 and release boundary before
activation; the earlier review is retained as evidence for the #503 design, not
as approval of the expanded scope.

Expanded-scope fresh-eye findings: three angle reviewers identified act-before-
activation repairs. Slice D needs a checked-in #503 local-closeout handoff with
the selected cohort/owner, action or no-change disposition, residuals, changed
paths, and an explicit non-recommendation for #496. Slice E must reproduce the
known hollow-refill symptom independently and record its producer/consumer
owner before choosing a repair. Slice G must order final proof as local S1–S6,
release critique/claims review, push, independent remote commit/CI readback,
release publication, and independent release/tag readback. S3 must make the
no-safe-change path falsifiable with an option comparison and reopen trigger.
The repair-read then identified three remaining blockers: the User Acceptance
completion sentence allowed stopping after #503, Slice D did not make the full
handoff fields executable, and this section still called the applied repairs
“pending.” The current update folds those three repairs into User Acceptance,
Slice D, and this record. A fresh packet was generated after this edit and
verified current; the goal remains an inactive draft until activation.

## Off-Goal Findings

#496 is now an in-goal second track, but remains an independent hollow-refill
predicate decision with its own owner, reproduction, proof, and review. The
corpus-denominator packet capability remains a separate owner decision unless
the #503 track proves it is the same producer/consumer contract. No new issue is
created by this scope update.

## Final Verification

Final local proof is now recorded. The midpoint claims review is bound at
`charness-artifacts/issue/2026-08-04-goal-midpoint-claims-review.md`; it accepts
S1 through S6 locally after the final lock; S7 remains the remote/public
boundary.
The separate release claims review is bound at
`charness-artifacts/issue/2026-08-04-release-3.2.0-claims-review.md`; it accepts
the notes with four explicit pre-ship conditions and does not promote remote or
publication claims.

Broad verification lock: `python3 scripts/run_slice_closeout.py --repo-root .
--verification-lock --refresh-broad-pytest-proof --ack-cautilus-skill-review`
completed at `2026-08-04T02:25:42Z`; durable proof is
`.charness/closeout/broad-pytest-proof.json` (46.31 seconds, all recorded
checks passed). The lock included standing pytest, structural/artifact
validation, sync, packaging, docs, skill, Cautilus-policy, shell, scan-hygiene,
and browser-orphan checks.

Retro: pending final closeout — `charness:retro` is required after the release
readbacks and before the goal is marked complete.
Host log probe: unavailable — host-level tool logs are not exposed; no token,
turn, or tool-count claim is made.
Disposition review: S1–S6 locally accepted; S7 remains pending the exact remote
commit/CI and independent release/tag/version readbacks.

## User Verification Instructions

The operator has resolved the scope. Activate with:

`/goal @charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`

At closeout, verify S1–S6 locally first. Then run S7 in order: release
critique/claims review and target plan, push, independent remote commit/CI
readback for the exact SHA, release/tag publication, and independent
release/tag readback. Do not claim remote issue CLOSED.

## Auto-Retro

Retro dispositions: pending final closeout — no disposition is claimed before
the final retro reads the completed work unit.
Structural follow-up: pending final closeout — the final retro must scan the
chosen waste class's siblings before closeout.
