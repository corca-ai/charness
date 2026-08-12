# Achieve Goal: Resolve the open quality and trust backlog, then publish

Status: active
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md`

This file is the living goal scratchpad. It is activated by the user's request
in this session after the pre-implementation critique passes.

## Active Operating Frame

- Current slice: Slice 1 and Slice 2 in parallel — premise decomposition remains
  incomplete while low-coupling quality repairs proceed.
- Current slice intent: repair the runtime and fixture truth paths without
  laundering the unfinished #582/#583/#584 umbrella, #528/#539/#542, or
  #589/#590/#606 premise work into a completion claim.
- Next action: re-read and classify #606's quality-ownership premise before
  selecting a repair or a tracker-visible non-closure disposition.
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
| 1 | Re-read every premise; decompose #582, #583, #584; disposition #587 and #605; re-plan dependencies | Prevent umbrella prose or unassigned rows from laundering distinct defects | 22-row ledger updates, ownership map, replan record, tracker-visible dispositions | in-progress |
| 2 | Repair quality verdict and fixture paths: #546, #589, #595, #597, #606, #586, #590 | These affect the proof used by later work | focused behavior tests, two-round review when triggered | in-progress |
| 3 | Repair issue/evidence trust paths: #539, #542, #602 | Closeout and creation semantics are irreversible boundaries | debug/causal evidence, carrier tests, critique | planned |
| 4 | Repair consumer and operator ergonomics: #528, #588, #599, #601, #550; prepare #527 decision | Build on truthful quality and issue surfaces | consumer-facing probes; #527 operator decision or tracker-visible deferral | planned |
| 5 | Decide and, only if justified, add #607 subprocess-settlement capability | It is an enhancement dependent on the quality inventory model | fixture classification and quality-route evidence; otherwise tracker-visible deferral | planned |
| 6 | Reconcile every ledger row and close eligible trackers | Each closure or non-closure needs a visible owner and reason | issue closeout ledger, behavioral verdicts, and non-closure tracker comments | planned |
| 7 | Run retro, final proof, push, release, and independent readbacks | Publication occurs only once over the frozen bundle | retro, release critique, release record, CI/public/install evidence | planned |

## Backlog Recount

- Counted: 22 open issues on 2026-08-12 via `gh issue list --repo corca-ai/charness --state open --limit 100`.
- Claims: #527, #528, #539, #542, #546, #550, #582, #583, #584, #586, #587, #588, #589, #590, #595, #597, #599, #601, #602, #605, #606, and #607.
- Not claimed: none; #587 and #605 begin as evidence/disposition work because their existing framing is explicitly refuted or unproven.
- Premise status: all 22 are currently `unverifiable-by-machine`; the inventory is scope, not a proof that each complaint remains true. Slice selection must re-read the issue and establish a falsifiable local premise.
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
  focused fixture tests (27 passed), selected fixture lane, and its required
  two review rounds; #546 current membership check and selected lane passed.
- Boundary: no issue is represented as closed locally. #546 has a GitHub
  `unproven-defer` carrier; #595 and #597 await final direct-to-default closeout
  and independent GitHub readback. #584 remains OPEN with a split carrier:
  SessionStart is locally proven, while the closed #532's successor contract is
  only specified, not implemented.
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
- Next: re-read #606's quality-ownership premise, then choose a repair or
  explicit tracker-visible non-closure disposition.

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

## Off-Goal Findings

- None yet. Newly found unrelated defects will be filed or deferred through
  `issue` and linked here without expanding this goal.

## Final Verification

- Pending active-run evidence. No release, push, issue closure, hosted CI, or
  installed behavior is claimed by this draft.

## User Verification Instructions

- At closeout, use the final release record and linked tracker carriers to
  inspect the exact published revision and every issue disposition.

## Auto-Retro

- Pending active-run retro. Any transferable finding will receive an applied
  repository change or a tracked issue before completion.
