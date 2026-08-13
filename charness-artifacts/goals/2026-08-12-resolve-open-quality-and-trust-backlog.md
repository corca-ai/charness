# Achieve Goal: Resolve the open quality and trust backlog, then publish

Status: active
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md`

This file is the living goal scratchpad. It is activated by the user's request
in this session after the pre-implementation critique passes.

## Active Operating Frame

- Current slice: the four rows a bounded closeout review pulled back from the
  cohort carrier (#597, #607, #590, #584) have been worked. Three are repaired
  with two review rounds each and carry local proof; #584 remains held on this
  ledger's Umbrella Closure Contract, unchanged. Seven cohort issues are CLOSED
  and independently read back; the rest are OPEN.
- Current slice intent: the repaired rows now need their tracker-visible carriers
  and, where eligible, the `issue` closeout floor. No row is claimed closed by the
  repair work itself.
- Next action: post the tracker carriers for #597, #607, #590, and #609, then
  author direct-to-default closeout carriers for the rows whose local proof is
  complete and run `verify-closeout --expect-state CLOSED` per row.
  `direct-to-default` means the carrier commit plus that readback
  (`skills/public/issue/references/closeout-discipline.md:91-104`); the green
  hosted CI on the default branch does not discharge it.
- Verification cadence: run cheap deterministic checks at commit boundaries;
  use fresh-eye critique and focused behavioral proof at every meaningful slice;
  reserve release quality, tracker readback, and installed readback for closeout.
- Gate cadence: use `run_slice_closeout.py --skip-broad-pytest` before each
  commit; bind the final bundle with its verification lock before publication.
- History boundary: this frame stays current; completed evidence moves to Slice
  Log and the owning quality, critique, debug, issue, release, and retro records.

## Goal

Resolve the current GitHub open-issue backlog in evidence-led dependency order.
For every claimed issue, either ship and independently prove the reported
capability or preserve an explicit, tracker-visible reason it cannot honestly
close. After the final retrospective finds no unresolved release blocker, push
and publish the resulting release with the required distinct-channel readbacks.

## Problem

The opening backlog mixes proof surfaces that can report a misleading verdict,
issue and evidence workflows at irreversible boundaries, consumer-facing helper
failures, operator-discovery gaps, and three umbrellas that may hide dependent
work. A single goal is useful only if every opening issue retains an individual
premise, owner, evidence channel, and tracker-visible outcome.

## Fixed Decisions

- The 22 numbered issues in the opening recount are the fixed cohort; newly
  opened issues are late arrivals under the execution ledger, not silent scope
  expansion.
- Local proof, issue closure, and final release are separate boundaries. One
  final publication is allowed only under the conditional approval in Boundaries.
- A row with an unproven, refuted, or decision-dependent premise has an explicit
  tracker-visible disposition; it is not closed by release association.

## Probe Questions

- Does each issue still name a live, falsifiable failure at its actual owner and
  first reader? Slice 1 writes the answer to the execution ledger.
- Which selected repairs change proof verdict logic and therefore require a
  second repaired-surface fresh-eye review? Slice 1 records that classification
  before a repair slice begins.
- For #607, does the quality inventory model justify a new settlement classifier
  after the preceding evidence is known, or is a scoped tracker deferral safer?

## Non-Goals

- Do not force a `CLOSED` state for an issue whose premise, required product
  decision, consumer behavior, or provider behavior remains unproven.
- Do not turn the three umbrella issues into a new generic meta-gate; their
  common diagnostic is a routing aid, while each real owner remains explicit.
- Do not treat local tests, a green quality gate, or a release tag as terminal
  proof of issue behavior, GitHub state, hosted CI, or installed consumer state.
- Do not publish intermediate slices; publication is one final bundle boundary.

## Boundaries

- The current tracker inventory is the semantic scope. GitHub issue bodies and
  comments are re-read before designing each individual resolution.
- [Open backlog execution ledger](./2026-08-12-open-backlog-execution-ledger.md)
  is the required row-level premise, owner, evidence, and disposition contract.
- Bug-class work uses `debug` and a causal fresh-eye review before repair;
  changes to proof verdict logic receive the required second review after repairs.
- External side-effect scope: the user approved one final push and release
  bundle only after retro, locked verification, and release critique report no
  unresolved blocker. A failure, material scope change, or weakened proof
  revokes that conditional approval and leaves publication unperformed.
- Issue closure uses the `issue` workflow's carrier, behavior verdict, critique,
  and GitHub readback floors. It is not inferred from the final release.

## User Acceptance

- The tracker has a per-issue disposition for every issue in the opening
  inventory: independently proven resolution and closed state, or an explicit
  unresolved/deferred reason with its owner.
- A release record lets the user verify the pushed revision, publication,
  distinct public observation, and installed `version` and `doctor` readback.
- The final retro explains any material waste or residual risk before release.

## Agent Verification Plan

### Low-Cost Checks

- Re-read each selected issue and comments through `issue_tool.py read`; run
  targeted tests, artifact validators, generated-surface sync, and changed-surface
  checks at the owning slice boundary.
- Record a premise recheck before claiming any issue is fixed or obsolete.

### High-Confidence Checks

- Run the owning quality plan and behavioral tests for each cluster; run the
  full release quality command only against the frozen final candidate.
- Run bounded fresh-eye review for every substantial slice and two rounds when
  a proof surface's verdict logic changes; run a midpoint goal-claims review.

### External Or Live Proof

- Before final publication, run the required retro and release critique. If
  both are clean and final evidence is locked, push once, observe remote CI by a
  distinct channel, publish, observe the public release independently, refresh
  the installed tool, and read back `version` and `doctor`.
- Verify every issue close separately through GitHub and a behavior channel
  distinct from its tracker state.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Activation critique and readiness binding | Do not execute from an unreviewed broad plan | critique record, clean reviewer fingerprints, reviewed-input identity, completed ledger | completed |
| 1 | Re-read every premise; decompose #582, #583, #584; disposition #587 and #605; re-plan dependencies | Prevent umbrella prose or unassigned rows from laundering distinct defects | 22-row ledger updates, ownership map, replan record, tracker-visible dispositions | completed — per-row proof/split/defer recorded; final tracker reconciliation remains Slice 6 |
| 2 | Repair quality verdict and fixture paths: #546, #589, #595, #597, #606, #586, #590 | These affect the proof used by later work | focused behavior tests, two-round review when triggered | completed — local proof or tracker-visible defer recorded; final bundle verification remains separate |
| 3 | Repair issue/evidence trust paths: #539, #542, #602 | Closeout and creation semantics are irreversible boundaries | debug/causal evidence, carrier tests, critique | completed |
| 4 | Repair consumer and operator ergonomics: #528, #588, #599, #601, #550; prepare #527 decision | Build on truthful quality and issue surfaces | consumer-facing probes; #527 operator decision or tracker-visible deferral | completed — #527 has an operator-owned tracker-visible defer; #528 remains separately owned OPEN split |
| 5 | Decide and, only if justified, add #607 subprocess-settlement capability | It is an enhancement dependent on the quality inventory model | fixture classification and quality-route evidence; otherwise tracker-visible deferral | completed (`1570ba32`; local proof carrier OPEN) |
| 6 | Reconcile every ledger row and close eligible trackers | Each closure or non-closure needs a visible owner and reason | issue closeout ledger, behavioral verdicts, and non-closure tracker comments | completed — all 22 rows reconcile to OPEN tracker/carrier evidence; no row earned a closure claim before final bundle proof |
| 7 | Run retro, final proof, push, release, and independent readbacks | Publication occurs only once over the frozen bundle | retro, release critique, release record, public/install evidence | published, closeout partially proven — `5.1.0` was pushed, tagged at `1024e500`, released, and read back; the post-publication fresh-eye closeout review has now run (`../critique/2026-08-13-v5.1.0-post-publication-closeout-review.md`) and left two residues: the pre-publication claims review's distinct-observer property is unproven (escalated to [#609](https://github.com/corca-ai/charness/issues/609)), and the post-publication session retro is still owed. The release closed no issues. |

## Backlog Recount

- Counted: 22 open issues on 2026-08-12 via `gh issue list --repo corca-ai/charness --state open --limit 100`.
- Claims: #527, #528, #539, #542, #546, #550, #582, #583, #584, #586, #587, #588, #589, #590, #595, #597, #599, #601, #602, #605, #606, and #607.
- Not claimed: none; #587 and #605 begin as evidence/disposition work because their existing framing is explicitly refuted or unproven.
- Premise status at opening inventory: all 22 were `unverifiable-by-machine`; the inventory is scope, not a proof that each complaint remains true. Later local proof and tracker-visible dispositions are recorded in the execution ledger; every newly selected row still requires a current issue re-read and falsifiable local premise.
- Cohort rule: a new or newly discovered related issue is linked as an off-goal
  dependency unless this goal is explicitly amended. It cannot silently become a
  completion requirement, but it blocks the affected row or umbrella when needed.

## Operator Decision Queue

- Decision: product direction for #527's skill-documentation and invocation-mode choices if the implementation brief exposes unresolved alternatives.
- Owner: operator.
- Why deferred: the opening diagnostic and smaller bug-class slices do not need it.
- Unblock action: choose the documented minimum viable public-skill surface or explicitly defer #527.
- Revisit trigger: before #527 transitions from investigation to implementation.

## Coordination Cues

- Phases: debug, quality, implementation, issue, release, retro.
- Routing: `issue` owns tracker re-reads and closeout; `debug` owns bug hypotheses; `quality` owns verification cadence; `impl` owns repairs; `release` owns final publication; `retro` owns the pre-publication learning review.
- Gather: n/a — tracker evidence is acquired through the selected GitHub issue backend, not an external source imported into the repository.
- Release: planned — final bundle only, under the user's conditional approval recorded in Boundaries.
- Issue closeout: planned — eligible issues use a direct-commit carrier, draft validation, critique, behavior verdict, and GitHub `CLOSED` readback.

## Discuss Before Activation

- Discuss before activation: resolved — the user explicitly requested the largest practical combined backlog goal, its immediate activation, and a final push/release only after a retro finds no issue. The goal therefore claims all current open issues as investigation/resolution scope, but does not pre-authorize an unsupported closure or override the #527 product decision queue.

## Slice Log

### Runtime, SessionStart, and Fixture Evidence (2026-08-12)

- Objective: turn three locally decidable proof gaps into tested behavior or an
  explicit non-closure disposition.
- Commits: `e3822458` (SessionStart routing), `a9b9c4d3` (planner-read-cost
  contract), `08b01ddc` (fixture evidence), `c9d25da4` (runtime advisories).
- Evidence: #595 focused runtime tests (50 passed), selected runtime-budget
  quality lane, debug/critique artifacts, and a fresh-eye repair review; #597
  focused fixture tests (27 passed) and its selected fixture lane; #546 current
  membership check and selected lane passed.
- **Correction (2026-08-13).** This entry previously claimed #597 took "its
  required two review rounds". No artifact supports that. Its only durable review
  record is `../critique/2026-08-12-issue-597-quality-fixture-gate-repair-critique.md`,
  which records `Requested tier: standard`, no round-2 section, and two
  `action: fix` findings on the verdict surface — so the second-round obligation
  was triggered and never discharged. Caught by the bug-carrier closeout review;
  the owed round is being run before #597 may close. #595's single round is
  defensible under the discharge clause (all four findings are `document` or
  `defer`, no `fix`), but the blanket phrasing was unproven for it too.
- Boundary: no issue is represented as closed locally. #546 has a GitHub
  `unproven-defer` carrier; #595 and #597 await final direct-to-default closeout
  and independent GitHub readback. #584 remains OPEN: SessionStart and the
  #532 representative planner-read-cost slice are locally proven, while a
  broader planner rollout is deliberately deferred.
- #589: local proof is complete: a validator-accepted local prescription has a
  reachable reconciled state only when every exact adapter command is declared;
  legacy/sample lineage remains advisory metadata. GitHub remains OPEN with a
  local-proof carrier; final direct-to-default action and hosted readback remain
  required.
- #586: inspected candidate is a superseded helper, while both real closeout
  consumers invoke the equivalent guarded loop. GitHub remains OPEN with an
  `unproven-defer` carrier until a reproducible operator-path bypass exists.
- #590: the reporting repair has an independent successful scheduled-CI
  descendant with all three mutation stages recorded; GitHub remains OPEN with
  a local/hosted proof carrier pending final cohort closeout.
- #606: local proof is complete: the canonical writer emits an integrity-bound
  baseline; guarded regeneration requires reviewable confirmation for a changed
  baseline; malformed JSON, non-object JSON, and non-file targets retain
  structured refusal. GitHub remains OPEN pending final direct-to-default
  carrier and readback.
- #582: the #525 README-proof Evidence-cell residual is locally proven by the
  existing Specdown reader; #524 taxonomy and #535 generic rebind remain
  separate deliberate non-implementations, so the umbrella remains OPEN.
- #583: cited pickup specs are deleted and #597 repaired its empty-fixture
  fail-open; no bounded generic premise gate is justified, so it remains OPEN
  with a re-read disposition.
- Historical next at this Slice Log point: record #584's local-proof carrier,
  then re-read the #528/#539/#542 trust-path premises in ledger order. The
  current route is owned by the Active Operating Frame above.

### Frozen Cohort Reconciliation and Retro (2026-08-13)

- Reconciliation: the execution ledger's 22 carrier issue numbers exactly match
  the live `gh issue list --state open` set; each exact carrier URL appears in
  its issue-reader comment list. There are no ledger-only or tracker-only rows.
- Retro: `charness-artifacts/retro/2026-08-13-session-retro.md` records #607's
  conservative proof review, #527's operator defer, the corrected carrier-read
  method, and #503's existing ownership of historical runtime telemetry.
- Boundary: this is reconciliation and learning evidence, not a push, release,
  close, remote-CI, public-observer, or installed-consumer claim. Slice 7 owns
  those separate channels.

## Context Sources

1. [Design north star](../../docs/design-north-star.md) — P4/P5 require a
   distinct observer and evidence channel at proof-surface, issue-close, push,
   and publication boundaries.
2. [Opening handoff](../../docs/handoff.md) — the completed five-issue sequence
   and instruction to re-inventory open tracker work.
3. [Current open tracker inventory](https://github.com/corca-ai/charness/issues) —
   source of truth for the 22 claimed issue identities and state.
4. [Recent lessons](../retro/recent-lessons.md) — warns against hand-editing a
   baseline, stale evidence identity, and overclaiming a passing gate.
5. [Session retro](../retro/2026-08-12-session-retro.md) — the prior release
   sequencing lesson and the previous release's proof boundary.

## Interview Decisions

- Scope family: one bounded issue, related cluster, or the complete open backlog.
  Chosen: complete backlog with issue-level evidence boundaries, because the user
  requested the largest practical combined goal. Rejected: a single issue would
  leave shared quality/evidence dependencies unsequenced.
- Publication family: local-only closeout, per-slice publication, or one final
  release. Chosen: one final release after retro and final proof, because the
  user explicitly requested release last and intermediate publication would
  create avoidable irreversible boundaries.
- Consumer axis: host/provider behavior is variable; selected concrete evidence
  remains GitHub, CI, public HTTP, and the maintainer-installed CLI, with no
  claim that these prove every consumer or provider adapter.

## Plan Critique Findings

- Spec critique (2026-08-12): three named reviewers and one counterweight pass
  found missing per-issue ownership, premise, and umbrella closure rules. These
  repairs are folded into the execution ledger, fixed-cohort rule, Slice 1
  replan gate, and Slice 6 tracker-visible non-closure requirement.
- Fresh-eye evidence: diagnostic review clean boundary fingerprint; the first
  structure/framing fingerprints were quarantined after a shared snapshot path
  was overwritten, then retried with clean unique snapshots. Counterweight
  accepted the ledger, #587/#605, umbrella, replan, and activation bindings;
  it rejected extra #527 and frozen-release constraints as over-worry.
- Activation readiness predicate: the execution ledger covers all 22 rows; the
  final packet binds the goal and ledger; two named angles plus a counterweight
  are received with clean unique reviewer fingerprints; their findings are
  folded or explicitly deferred; and this artifact passes pursue readiness.
  Any semantic plan or ledger change requires a new packet and critique before
  execution.

## Closeout Binding Plan

- Reviewed inputs: the live 22-issue GitHub inventory, issue bodies/comments
  re-read per slice, the goal artifact, owner quality records, and generated
  release surfaces. Retros, packets, reviews, and locks are terminal evidence.
- Frozen target: freeze the final semantic diff at a committed candidate; bind
  the release packet and critique to that exact revision before push.
- Fresh-eye: bounded reviewers provide a distinct observer for plan, slices,
  midpoint goal claims, closeout claims, and release claims; GitHub/HTTP/installed
  readbacks provide channels distinct from local tests.
- Verification lock: the release workflow records the locked quality receipt and
  its evidence location; any semantic edit after locking invalidates the packet.
- Complete flip: only after retro, final quality, review, publication/readbacks,
  issue closeout dispositions, and terminal records are bound and verified.

### Four Held-Back Rows Repaired With Two Review Rounds (2026-08-13)

- Objective: repair the four rows the bounded closeout review pulled from the
  cohort carrier, and close the release-resume ergonomics gap the claims-review
  contract named. Every one changes verdict logic on a proof surface, so each owed
  two bounded review rounds.
- Commits: `dd473642` (the repairs), `dfb29e0e` (coverage for the refusal branches
  the subprocess tests cannot reach).
- Evidence: two-round critique
  `../critique/2026-08-13-four-proof-surface-repairs-two-round-critique.md`; six
  bounded reviewers across two windows, both `reviewer_boundary_fingerprint.py`
  verifies `clean` with empty `parent_declared` and run before the first fold; the
  locked closeout completed and the changed-line mutation-coverage consumer is
  green over `origin/main`.
- What the rounds found, which is why the rule exists: round 1 found a live defect
  on every surface, and round 2 found a defect INSIDE a round-1 repair on every
  surface — including one repair that silently disabled a sibling repair, and one
  that reopened the exact class the sibling fold had closed. All were reproduced
  executably by the parent before repair.
- Boundary: this is local proof and a fresh-eye record. No issue is closed, no
  push or release occurred, and the three deferred residues are tracked as #610,
  #611, and #613 rather than carried as prose.

## Off-Goal Findings

- [#609](https://github.com/corca-ai/charness/issues/609),
  [#610](https://github.com/corca-ai/charness/issues/610),
  [#611](https://github.com/corca-ai/charness/issues/611), and
  [#613](https://github.com/corca-ai/charness/issues/613) — late arrivals from the
  post-publication closeout review and this session's two review rounds. #609 is
  locally resolved; the other three are filed and deliberately not implemented.
  The execution ledger's Late Arrivals section owns their state.
- [#608](https://github.com/corca-ai/charness/issues/608) — its local repair now
  supplies the supported marked-record and bound-claims-review stage; it remains
  a late arrival outside the fixed 22-row cohort. The locked changed-line proof
  now covers its repaired topology, while later publication still retains
  rollback, quality, synchronization, and no-issue-close boundaries.

## Final Verification

- Publication is complete and independently observed. `5.1.0` is tagged at
  `1024e500` on `origin`, the default branch head at publication time was the
  historical `4aa76a19` (local `HEAD` has advanced since), and a
  credential-free REST readback returns `draft: false` /
  `target_commitish: main` (`../probe/2026-08-13-v5.1.0-post-publication-observables.md`).
  Hosted Quality Core succeeded on the default branch head (run `31650565315`,
  both jobs). The locked changed-line verification, pre-publication retro, final
  release critique, marked prepared record, and a claims-review record all exist.
- Two release-closeout residues remain, both recorded rather than waived: the
  pre-publication claims review's distinct-observer property is **unproven**
  ([#609](https://github.com/corca-ai/charness/issues/609)), and the
  post-publication session retro is still owed, which is why the
  `RECONCILE REQUIRED` disposition in `../release/latest.md` has no recorded
  reviewer judgment.
- No issue closure is claimed. The release closed no issues, and the 22-issue
  cohort disposition is unfinished work owned by the execution ledger.

## User Verification Instructions

- At closeout, use the final release record and linked tracker carriers to
  inspect the exact published revision and every issue disposition.

## Auto-Retro

- Retro: `charness-artifacts/retro/2026-08-13-session-retro.md`
- Retro dispositions: applied: #607 focused conservative-classification
  regressions and the exact carrier-URL reconciliation method are committed;
  #503 already owns the historical telemetry remeasurement boundary.
- Structural follow-up: applied: #607 focused tests and the frozen
  reconciliation method; the #503 telemetry boundary remains intentionally
  owned by its existing record.
