# Achieve Goal: Remove friction-producing structure and close the P0/P1 backlog

Status: draft
Created: 2026-08-28
Activation: pending explicit approval, Goal Binding, and provider-backed parent creation

This is the mutable planning draft. After exact approval it freezes; GitHub owns
execution progress and the current child. This file does not become a progress
mirror.

## Active Operating Frame

Current disposition: real draft/backlog awaiting approval. The repository starts
from clean `main` at `1d9db746a57bb9439f9b6cbc2fc2eb926b517b58`, two coherent
commits ahead of `origin/main`. Those commits preserve the Luna delegation policy
and Git identity guard discovered in the preceding session; they are starting
truth, not a new child created to re-document completed work.

The macro JTBD is simple: Charness must make correct development in consuming
repositories faster and reduce rework. A guard, test, wrapper, artifact, or doc
that does not preserve a unique live capability or fence a real cliff is deletion
work, not safety work.

## Goal

Classify all 16 issues open at the 2026-08-28 provider read, reconcile obsolete
remote state, and resolve the complete P0/P1 set in a generative sequence. Use
the run to dogfood the simplified Achieve, Issue, Task, Setup, Impl, Prove, and
Quality contracts. Remove the structures that repeatedly regenerate friction:
duplicate execution/progress ownership, legacy Goal Draft closeout state,
universal review ceremony, local changed-line/mutation pressure, authoring-time
mirror work, stale docs, and tests that pin those retired contracts.

Completion means that every P0/P1 Work Item is provider-closed with behavioral
evidence, the parent Goal Run is closed through its dedicated readback path, and
only explicitly independent P2 work remains open. Success is preserved
capability with less machinery, not a target line count.

## Open Issue Classification

The classification comes from one provider read per issue with comments included.
No issue body or graph is re-read during routine execution; the parent cursor owns
pickup.

| Issue | Class | Goal disposition | Reason |
| --- | --- | --- | --- |
| #735 | P1 | reuse as Work Item | Clean exported consumer paths still need self-sufficient command/data resolution proof. |
| #732 | absorbed | close in reconciliation | v7 `prove` is already risk-adaptive; remove any universal-review residue instead of reimplementing it. |
| #731 | P2 independent | leave outside this Goal Run | Timeout cleanup and typed non-delivery exist; partial-progress/multi-lens ergonomics remains useful but is not P0/P1. |
| #730 | P1 | reuse as Work Item | The shared init substrate exists, but first-use resolver/action semantics are not uniform across the actual v7 adapter set. |
| #729 | absorbed | close in reconciliation | The semantic one-command review runner already derives identities and schema; #728 owns the remaining status projection gap. |
| #728 | P1 | reuse as Work Item | Reviewer preflight, delivery, timeout, and verdict states exist below the generic task-status boundary but are not projected there canonically. |
| #711 | P2 duplicate | close into #709 | One positive-control measurement-projection slice can cover both issues without another gate. |
| #709 | P2 independent | keep as the consolidated P2 owner | A non-zero summary projection test remains useful but does not block the P0/P1 goal. |
| #705 | P1 | reuse as Work Item | Release prose still combines versioned and presence-only surfaces into an overstated version-drift count. |
| #702 | policy absorbed | close in reconciliation | Keep the citation lesson; do not build a prose-classifier gate for “load-bearing” sentences. |
| #688 | obsolete | close in reconciliation | The exact malformed source/output cannot be reproduced; speculative parser growth would add complexity. |
| #612 | absorbed | close in reconciliation | v7 separates mutation sampling/execution/summary and moved expensive mutation to release-only ownership. |
| #599 | absorbed | close in reconciliation | `scripts/what_reads_this.py` now provides the requested grouped consumer discovery. |
| #584 | absorbed | close in reconciliation | SessionStart/handoff state is gone and shared plan-envelope read measurement covers the live remainder. |
| #583 | obsolete | close in reconciliation | Its concrete Cautilus/handoff members were retired; a generic premise gate has no bounded live failure. |
| #582 | absorbed | close in reconciliation | Narrow README evidence binding remains; the old universal proof/closeout schema family was deliberately retired. |

Expected reconciliation result: 10 issues close as absorbed, obsolete, policy
dispositioned, or consolidated; four P1 issues enter the Goal Run; #731 and #709
remain independent P2 backlog. The provider readback, not this expected count,
is authoritative.

## Target Ownership Model

- Goal Draft owns approved intent, boundaries, issue classification, Work Item
  design, and proof strategy. It owns no mutable execution or closeout state.
- Goal Binding owns immutable identity between this frozen draft and one GitHub
  parent/initial child manifest.
- Goal Run parent owns shared scope, dependency order, sparse contract changes,
  and one current-child cursor.
- Work Item issues own routine implementation state and their behavioral proof.
- `charness task run` owns isolated Codex execution with explicit branch,
  worktree, scope, model, and external runtime. Host subagents own short
  interactive sidecars. Luna is the explicit fast tier for both in this repo.
- The parent agent owns design, generative order, integration, commits, and final
  verification. Parallel authors never share a write surface.
- Charness-owned commands own cache/temp isolation. Arbitrary direct `python`,
  `pytest`, or `ruff` invocations remain outside that guarantee and may leave
  separately reported ignored residue.

## Initial Work Items And Generative Sequence

| Rank | Key | Priority | Objective | Dependencies | Parallel shape |
| --- | --- | --- | --- | --- | --- |
| 0 | remote-truth-reconciliation | P0 | Create the parent, attach only real Work Items, close the 10 absorbed/obsolete/consolidated issues, and read back the exact resulting open set. | none | provider writes serialized by parent |
| 1 | task-run-parallel-contract | P0 | Make `charness task run` usable as the default isolated writer lane: keep clean-parent preflight, distinguish unrelated parent progress from overlapping writer conflict, admit descendants of declared directory scopes, and persist one typed running/terminal result that `task status` can read. Delete the unconnected claim/submit/review/abort envelope unless a real external scheduler consumer is found. | rank 0 | parent-owned foundational slice; proves the lane used by later ranks |
| 2 | goal-draft-ownership-collapse | P0 | Make the frozen Goal Draft a planning record only. Delete legacy Slice Log/Auto-Retro/closeout/retro-disposition state, validators, helpers, fixtures, tests, and stale lifecycle prose whose execution truth now belongs to Goal Run/Work Items. End shaping with one explicit approval question; waiting for the user's answer is a normal conversational boundary, not a blocked Goal or a magic-keyword protocol. | rank 1 | Luna isolated writer; disjoint from ranks 3–6 |
| 3 | retired-workflow-surface-deletion | P0 | Delete retired decisions, routing, fixtures, tests, and prose that preserve retired handoff, SessionStart, Cautilus, or closeout-artifact ceremony. Compact the 240KB public-skill dogfood history into current per-skill evidence while preserving its 19 live cases. Keep retro-owned session audit and release/install producers whose current consumers remain live. | rank 1 | Luna lanes partitioned into decision/docs, dogfood registry, and current routing scopes |
| 4 | verification-cost-and-test-collapse | P0 | Remove advisory ratio and command-doc probes from ordinary broad runs, delete universal fresh-eye/fingerprint cadence and redundant test/gate ownership, and keep changed-line mutation only at explicit release. Preserve unique release mutation, reviewer delivery, closeout verdict, package/install, and shared-tree fallback capabilities. | rank 1 | Luna lanes partitioned by runner selection, review cadence, and duplicate test families; parent integrates |
| 5 | reviewer-status-carrier | P1 / #728 | Project one canonical reviewer lifecycle through the rank-1 task result/status carrier, then delete duplicate status reconstruction and manual assembly guidance. #729 is closed only by rank 0 as already absorbed. | rank 1 | may run beside ranks 2–4 and 6 in an isolated worktree |
| 6 | uniform-adapter-first-use | P1 / #730 | Give the actual v7 adapter-owning skills one small first-use result shape and actionable absence path by consolidating shared init behavior and deleting retired handoff assumptions. Prove both successful bootstrap and truthful missing/invalid behavior. | rank 1 | may run beside ranks 2–5; parent resolves shared exports |
| 7 | export-self-sufficiency | P1 / #735 | From stable canonical source, prove a clean export/installed consumer uses shipped commands and data without consumer-repo path accidents, including execution outside the source checkout and absence of deleted handoff paths. Generate checked-in export once at integration/release time, not during authoring. | ranks 2, 3, 4, 6 | one source owner, then serialized export sync |
| 8 | release-claim-precision | P1 / #705 | Render versioned and presence-only release surfaces separately using the existing checker split; replace redundant assertions with focused value tests. | rank 7 | small isolated implementation lane |
| 9 | integrated-dogfood-closeout | P0/P1 integration | Exercise fresh `/goal` pickup, Luna host/task fan-out, provider cursor updates, focused/core proof, clean export/install proof, issue closeout, and parent public readback. Then close the parent through the dedicated Goal Run boundary. | ranks 1–8 | one bounded integration Work Item followed by parent-only guarded close |

Rank 1 first repairs the lane that makes later parallel work cheap. Ranks 2–6
then form one parallel generation after remote truth is fixed. Rank 7 waits for
the surviving source/adapter contract so export proof is not spent on code that
will be deleted. Rank 8 fixes the release claim over the final surface. Rank 9
proves the composition once instead of rerunning broad gates per slice.

## Work Item Acceptance Contracts

### Rank 0 — remote truth

- Establish and read back one parent with exactly the ten listed Work Items.
- Read each proposed close target with comments exactly once at close time,
  publish the absorbed/obsolete/consolidated reason, close, and read back closed.
- Read back four attached P1 issues plus independent open #731/#709; do not turn
  those two P2 issues into parent blockers.

### Rank 1 — task lane

- Clean parent is mandatory at launch; concurrent parent progress after launch
  outside the task scope is reported as `concurrent-parent-progress`, not
  attributed to the lane or turned into lane failure. Parent progress overlapping
  the task's resolved scope is an explicit writer conflict.
- A file scope admits that file; a directory scope admits descendants; every
  changed path outside the resolved scopes still refuses.
- `task run --task-id X` persists one typed running/terminal receipt readable by
  `task status X`, including top-level identity, timeout/interruption, validated
  partial-result state, approval ineligibility on non-delivery, logs,
  branch/base/target, and separate target tracked/untracked/ignored populations.
- The lane's runtime/cache remains outside both worktrees. Remove or reuse the
  old claim/submit/review/abort state after its consumer scan confirms that only
  docs/tests/legacy guidance consume it; do not create a second result store.

### Ranks 2–4 — deletion generation

- Rank 2 leaves one planning-only Goal Draft validator/scaffold plus naming,
  Markdown shape, safe path, planning discussion, and frozen identity. Local
  lifecycle, `/goal @file`, append-slice, closeout, metric-window, Auto-Retro,
  timebox, blocked/superseded, operator-queue, and terminal-evidence helpers
  disappear with their fixtures/tests/docs. `/goal #N`, Binding, Goal Run, and
  Work Item remain the only execution path.
- Rank 2 makes activation end in a direct, bounded approval question containing
  the exact authorized provider effects. An unanswered question remains an
  ordinary user-turn wait; Achieve does not convert it into Goal failure/blocked
  state or require the operator to infer a special response token.
- Rank 3 removes retired decision records D18/D31/D32/D37/D52, retires D46
  historical citations without deleting its live adapter warning behavior,
  removes duplicated dogfood Markdown lists, and reduces each JSON dogfood case
  from an append-only history to current acceptance evidence. Current AGENTS,
  setup generation, retro session audit, export/sync, and install checks remain.
- Rank 4 leaves ordinary implementation on focused tests plus one integrated
  core lane; moves advisory test/production ratio and command-doc probes to
  release/explicit selection; keeps mutation/changed-line only in an explicit
  release lane; and keeps shared-tree fingerprinting only as a fallback. Every
  retained expensive test names its unique escaped failure; every removed gate
  loses its catalog, wrapper, fixture, and prose owner together.
- Each deletion cluster records its consumer search and focused positive/
  negative control. No line-count target substitutes for equal capability.

### Rank 5 — reviewer task result

- Task status distinguishes preflight refusal, started/no delivery, timeout or
  interruption, delivered non-approval, and delivered verdict without log
  archaeology.
- No approval is projected without delivered identity/schema-bound evidence.
  `run_reviewer_worker.py` plus `reviewer_delivery.py` remain the approval owner;
  recovered partial text is diagnostic-only. Manual packet assembly is
  diagnostic only or deleted if it has no live caller.

### Rank 6 — adapter first use

- Every actual adapter-owning v7 skill returns the same small configured,
  absent, and invalid envelope with one actionable next step.
- Shared init mechanics have one owner; skill-specific semantic fields remain
  local. Retired handoff counts, fixtures, and branches are absent.

### Rank 7 — export consumer

- A clean export/fresh install runs documented consumer commands from outside
  both Charness source and the consumer repository root.
- Every runtime dependency and data path used by those commands ships or has an
  explicit install contract. Deleted handoff/SessionStart paths are negative
  controls, not compatibility assets.
- Authoring edits canonical source only; export sync/layout validation runs once
  after ranks 2–6 stabilize.

### Rank 8 — release truth

- Release evidence reports versioned and presence-only surface counts separately
  and tests each by value. No new gate or aggregate model is introduced.

### Rank 9 — integrated proof and close

- Fresh `/goal` pickup, cursor advance, Luna host/task fan-out, final focused/
  core/standing checks, clean export/install, child closes, and parent guarded
  close all bind the final commit and provider identities.
- Final report includes before/after code/test/gate counts and runtime, but claims
  only the capabilities actually exercised. Push/release remains a separate grant.

## Deletion Decision Rule

Deletion candidates are tested in this order:

1. name the live capability and its producer/consumer;
2. use grouped consumer discovery, not filename intuition;
3. if another smaller contract protects the same escaped failure, keep one owner
   and delete the duplicate code, fixture, test, validator, wrapper, and prose;
4. if no live consumer exists, delete the surface rather than catalog-excluding
   or documenting it;
5. preserve a surface only when removing it loses a demonstrated capability or
   lets a wrong result escape at an irreversible boundary.

No new wrapper is accepted unless it removes at least two existing owners. No
new gate is accepted merely to enforce a prose rule. Historical artifacts may
remain as history, but cannot stay in current routing, validation, or generated
consumer truth.

## Non-Goals

- Implement #731 or #709; they remain independent P2 work.
- Reintroduce SessionStart, shell activation, ambient cache hooks, handoff files,
  progress mirrors, lesson-session receipts, Cautilus, or universal closeout
  bundles.
- Guarantee cache-free behavior for arbitrary direct commands.
- Turn every advisory export inventory into a blocking gate.
- Add a generic premise checker, prose-citation classifier, proof-ladder schema,
  provider-selection framework, or compatibility shim without a live consumer.
- Preserve test count, line count, wrapper count, or generated mirror count as
  goals in themselves.
- Publish a release, push, tag, mutate installed hosts, or run remote CI without
  a separate phase-scoped user grant.

## Boundaries

- Preserve the parent checkout. Do not reset, restore, stash, clean, or delete
  unrelated user state. Start writers in clean named worktrees and integrate
  coherent commits into the clean parent.
- Separate tracked, untracked, and ignored residue in receipts. Task-owned lanes
  fail on their own residue; ignored direct-command residue is reported but is
  not Git dirty.
- Deletion and proof-surface edits receive one bounded independent final review
  over the integrated diff through an isolated Luna task lane. Do not require a
  fingerprint or a review round per reversible micro-slice. Retain the
  shared-parent fingerprint only as a fallback for an untyped reviewer that
  cannot be isolated; it is not the default review path.
- Provider issue creation, relationship mutation, close, and parent close use
  Issue-owned preflight/readback. Rank 0 performs one fresh comments-inclusive
  read per closure immediately before mutation; this is closeout synchronization,
  not a routine full-graph pickup. Exact draft approval authorizes only the
  provider mutations listed in this Goal; push/release authority remains separate.
- Canonical source is edited once. Generated plugin/export surfaces are synced
  only after source stabilization and validated at the release/install boundary.
- Preserve package/install behavior, provider identity and readback, clean
  parent/external task runtime, truthful reviewer non-delivery, and the small
  gates whose false green can escape.

## User Acceptance

The operator can verify completion by observing all of the following:

- the Goal Run parent shows only the ten initial Work Items above, with every
  P0/P1 child closed and #731/#709 explicitly outside the parent;
- the ten stale issues are closed with concise absorbed/obsolete/consolidated
  reasons rather than counted as remaining implementation;
- a fresh `/goal #N` reads the parent and current child without rescanning all
  child bodies;
- independent work uses explicit Luna host/task lanes and returns consumable
  results while the parent continues integration work;
- setup-generated AGENTS/docs use short progressive disclosure and do not revive
  handoff, SessionStart, universal review, or mutation ceremony;
- a clean exported/installed consumer can use the shipped Charness paths without
  resolving hidden files from the source or consumer repository;
- before/after source, test, gate, tracked/untracked/ignored, and core-runtime
  figures are reported together with the unique capabilities intentionally kept.

## Agent Verification Plan

### Low-Cost Checks

- One focused test command for each coherent Work Item and one composite docs
  check for its final docs delta.
- `scripts/what_reads_this.py` or an equivalent grouped consumer search before
  deleting a surface whose consumer is not obvious.
- Worktree preflight and post-run tracked/untracked/ignored classification for
  every `charness task run` lane.

### High-Confidence Checks

- The default core lane once after ranks 1–6 integrate, and once on the final
  integrated P0/P1 tree only if later ranks changed a core verdict surface.
- Standing pytest once on the final coherent commit, fail-fast before any
  release-only expensive check.
- One bounded independent Luna review of the final deletion/proof-surface diff,
  followed by focused repair proof if it finds a real blocker.
- Clean named-worktree export, packaging, CLI help/doctor, and fresh-install
  probes for #735 and the final tree.

### External Or Live Proof

- Issue-owned exact parent/child relationship and state readback after graph
  establishment, each child close, and guarded parent close.
- Public GitHub readback of the final parent state. No release publication is
  claimed unless a later explicit grant adds and completes that boundary.
- Changed-line mutation runs only once in a separately authorized final release
  lane; this Goal does not run it merely because code changed.

## Slice Plan

The Initial Work Items table is the complete planned decomposition. GitHub child
bodies will carry their executable scope and focused proof after approval; no
second local phase-spec tree or progress ledger will be created.

## Backlog Recount

- Counted: 16 GitHub issues open in `corca-ai/charness` on 2026-08-28, each read
  once with comments during shaping.
- Claims: close 10 absorbed/obsolete/consolidated issues; resolve existing P1
  #735, #730, #728, and #705; execute six new P0/integration Work Items; close
  one ten-child Goal Run parent after exact provider readback.
- Not claimed: implementation or closure of independent P2 #731 and #709;
  arbitrary direct-command cache freedom; push, tag, release, remote CI, or
  installed-host mutation without a later grant.

## Discuss Before Activation

- Discuss before activation: resolved — activation remains conditional on the
  operator explicitly approving these exact draft bytes. That approval permits
  the parent/ten-child graph and the issue relationship/comment/close mutations
  listed here; it does not permit push, tag, release, remote CI, or installed-
  host mutation.

## Slice Log

N/A — this legacy required heading is intentionally not used as progress state;
the first P0 Work Item removes it from future Goal Draft contracts.

## Context Sources

1. `docs/design-north-star.md`: judgment on reversible work, distinct evidence
   only at real cliffs, and equal-capability-before-deletion.
2. `AGENTS.md` and `docs/parallel-execution.md`: explicit Luna sidecars,
   disjoint writers, serialized parent integration.
3. Current v7 `achieve`, `issue`, `impl`, `prove`, `quality`, `setup`, and
   `release` skill sources and their installed 7.0.0 copies.
4. One bounded Achieve lesson projection from
   `charness-artifacts/retro/recent-lessons.md`; no session receipt was created.
5. One provider read with comments for each open issue #735, #732, #731, #730,
   #729, #728, #711, #709, #705, #702, #688, #612, #599, #584, #583, and #582.
6. Current repository census: clean tracked/untracked state before drafting,
   119 ignored residue roots, 634 files under `tests/`, and 203,671 Python test
   lines.
7. Read-only Luna `charness task run` deletion census from an isolated named
   worktree. It timed out at 900 seconds without a final analysis, while proving
   zero tracked/untracked/ignored lane residue and exposing the false parent-
   progress failure. Its partial consumer scans are evidence, not a verdict.
8. Starting commits `5ba365adde9a113683b84e46b9ccd3106c145452` and
   `1d9db746a57bb9439f9b6cbc2fc2eb926b517b58`.
9. Quality dogfood packets: configured adapter with no declaration gaps, default
   planner summary of 90 lines, 21 skills scanned, five-gate default core, 100
   broad/release queue labels, 122 packaged validator decisions, and measured
   medians of 169–221 seconds for broad pytest/quality plus 283 seconds for
   changed-line mutation.
10. Four read-only Luna ownership audits over Achieve, task/reviewer,
    quality/proof/tests, and docs/setup/export. Their focused cohorts passed 48,
    49, and 88 tests where run; those passes establish current behavior, not that
    the behavior should be retained.

## Interview Decisions

- Questions asked in this entry: 0. The operator already fixed the consequential
  choices: include the full session-friction pattern, classify every open issue,
  execute all P0/P1, allow obsolete/absorbed close, use a generative sequence,
  use Luna/task parallelism by default, prefer deletion, and dogfood the new
  skills.
- P2 choice: leave only live independent P2 ownership outside this parent rather
  than either implementing it now or hiding it in successor ceremony.
- Release choice: release publication is excluded until separately authorized;
  this prevents approval of a local Goal Draft from silently granting push/tag.
- Rejected alternative: keep all 16 issues as children. It would reproduce the
  remote-count-is-work bug and make absorbed history block current execution.
- Rejected alternative: establish numerical deletion quotas. Counts are reported
  as outcomes; unique capability and escaped-failure ownership decide deletion.

## Plan Critique Findings

One read-only Luna planning critique completed against the draft and current
contracts.

- Applied: made the initial Work Item count exact and kept integration as a
  bounded child followed by a separate guarded parent-close transition.
- Applied: assigned #729 closure only to rank 0.
- Applied: made the task-run concurrency conflict rank 1, before all task-based
  fan-out.
- Applied: narrowed fingerprint deletion. The shared-tree untyped-reviewer
  fallback survives; routine isolated work does not pay for it.
- Applied: rank 0 performs one fresh close-time issue read rather than treating
  shaping reads as irreversible closeout evidence.
- Applied: split the umbrella verification deletion into retired-workflow and
  verification-cost/test Work Items.
- Applied: #730/#735 now include negative missing-path and outside-source
  consumer proof.
- Applied: the rank-1 task receipt is canonical; rank 5 may project reviewer
  state through it but may not add another lifecycle store.
- Applied from ownership audit: rank 2 now names the planning core to keep and
  the complete local lifecycle/closeout helper families to delete, including
  `/goal @file`, status flips, Slice Log, metric window, timebox, blocked/
  superseded, and Auto-Retro state.
- Applied from live dogfood: shaping ended with an instruction to type a keyword
  instead of a direct approval question, then automatic continuation converted
  the unanswered turn into `blocked`. Rank 2 now owns deletion of that implicit
  activation protocol and requires one explicit bounded question instead.
- Applied from task audit: rank 1 emits a durable timeout/non-delivery receipt,
  surfaces top-level task identity, and removes the legacy envelope when its
  final consumer scan confirms only docs/tests remain. Rank 5 preserves the
  provenance-bound reviewer worker/delivery chain because it owns a distinct
  approval capability.
- Rejected from task audit: preserve exact-file-only scope. It prevents a
  bounded implementation lane from creating or discovering files under an
  explicitly owned directory and reproduces the wrapper friction this Goal is
  removing. Existing-file scopes remain exact; declared directory scopes admit
  descendants and still refuse every other path.
- Applied from docs audit: preserve current AGENTS/setup/export/install owners,
  delete only retired decision records and citations, and compact rather than
  blindly remove the 19-case dogfood registry.
- Applied from quality audit: move advisory ratio and command-doc probes out of
  ordinary broad execution. Preserve release mutation, reviewer delivery,
  closeout verdict, and packaging gates until a smaller owner is proven; high
  runtime alone is not equality of capability.
- Rejected as over-broad: a new standalone Quality-planner rewrite. The default
  planner is a 90-line summary; the 1,207-line observation came from an explicit
  `--detail` diagnostic. Rank 4 targets real queue and ownership costs instead.
- Counterweight retained: one final standing pytest run and one integrated
  independent deletion/proof-surface review are proportionate for this repo-wide
  cut. Per-slice broad proof and release mutation remain excluded.
- Over-worry rejected: rereading every issue graph during routine pickup. Only
  exact close targets are reread at the provider mutation boundary.

## Off-Goal Findings

- `docs/goal-lifecycle.md` still labels the v7 design as conditional and points
  to the completed #724 transition. It belongs to the P0 truth cleanup.
- The current Goal artifact scaffold/checker still requires Slice Log,
  Auto-Retro, and closeout evidence despite the v7 Achieve skill declaring the
  frozen draft a planning-only record. This is confirmed duplicate ownership,
  not a request for another validator.
- `task run` currently compares parent status populations at exit and fails when
  the parent agent made legitimate concurrent progress. Its scope checker also
  treats every `--scope` as one exact file, so a declared directory such as
  `tests` does not authorize descendants, and a one-shot `--task-id` is not
  visible through `task status`. These are confirmed dogfood defects in the
  lane intended to replace consumer-owned wrappers.
- Existing ignored residue includes historical handoff, Cautilus, reviewer-round,
  pycache, pytest, ruff, coverage, and artifact roots. Direct-command residue is
  a non-claim; Charness-owned task isolation is separately tested.
- The partial Luna census found 12 currently cataloged consumer validators, all
  wired, dominated by artifact/closeout validators; deletion must remove their
  catalog/adoption entries with the obsolete producers, not add exclusions.
- `skills/public/achieve/scripts/` is about 9.4K lines and the current
  achieve/goal test cohort about 4.1K lines. Reviewer/task source plus focused
  reviewer/task tests are about 9.3K lines. These are deletion-search baselines,
  not quotas.
- `docs/public-skill-dogfood.json` is a 240KB historical change log presented as
  current docs, and `docs/deferred-decisions.md` is 967 lines. Both have live
  validators/tests, so their data, producer, validator, and tests must shrink
  together to the surviving current contract rather than receive a blind file
  delete or a compatibility shim.
- A lexical mirror/generated search touches 168 test files. That number proves
  broad coupling worth classifying; it does not prove 168 deletions.

## Final Verification

Not executed — this is a pre-approval Goal Draft. Final proof is defined in the
Agent Verification Plan and will bind the final integrated commit and provider
readbacks, not the current shaping checkout.

## User Verification Instructions

Before activation, review the final briefing and approve the exact frozen draft.
After activation, resume only with `/goal #<parent>`; routine pickup should show
the current child and the provider's observational sub-issue count without a
full graph scan.

## Auto-Retro

N/A — no session-emission receipt, progress mirror, or automatic retro lifecycle
is created. A final retro is optional only if the completed run yields a durable
lesson not already represented by the code/docs deletion.
