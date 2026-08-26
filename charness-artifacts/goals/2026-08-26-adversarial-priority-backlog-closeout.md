# Achieve Goal: Adversarially resolve and close the P0–P2 issue backlog

Status: draft
Created: 2026-08-26
Activation: `/goal @charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Operating Principles

- Treat every failure as a structural signal: inspect the pattern and the
  pattern of patterns, run `debug` with a 5-whys root-cause pass, and improve
  the system instead of papering over the symptom with a retry.
- Keep this goal compact. The goal states outcome, boundaries, and control
  state; each phase's detailed contract and completion proof lives in its own
  `charness-artifacts/specs/<goal-slug>/.../spec.md` file.
- Do not call a phase complete until its spec's acceptance criteria and
  verification method have an executed, readable receipt.

## Active Operating Frame

- Current slice: draft complete; 26 current P0–P2 issues await activation-time requalification.
- Current slice intent: coordinate independent issue lanes under one outcome and proof diet; the goal is not a global task lock and does not serialize issue ownership.
- Current disposition: shaped draft, inert until the operator runs the exact activation line.
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md` after confirming the draft is
  still intended.
- Verification cadence: issue premise checks and focused tests first; broad proof only for shared or verdict-bearing changes and at final bundle closeout.
- Gate cadence: stale/duplicate closure uses tracker readback plus current targeted evidence; implementation slices use cheap commit checks, targeted behavior proof, and only the owning broad gate when the changed surface earns it.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Requalify the 26 current P0–P2 issues against tracker truth and the live implementation, close stale or over-scoped records with proportionate evidence, repair only the defects whose premises still hold, and leave no claimed issue open at completion. The goal coordinates independent issue lanes; it is not a single execution lock or a substitute for issue-owned state.

## Phase Specifications

Detailed phase contracts live under `charness-artifacts/specs/`; each phase must satisfy its linked spec before it is marked complete.

- Phase 1: [Requalify scope and ownership](../specs/adversarial-priority-backlog-closeout/phase-01-requalify-scope-and-ownership/spec.md) — completion and verification live in the spec.
- Phase 2: [Resolve consumer and authoring boundaries](../specs/adversarial-priority-backlog-closeout/phase-02-consumer-and-authoring-boundaries/spec.md) — completion and verification live in the spec.
- Phase 3: [Resolve proof, release, and runtime boundaries](../specs/adversarial-priority-backlog-closeout/phase-03-proof-release-and-runtime-boundaries/spec.md) — completion and verification live in the spec.
- Phase 4: [Resolve reporting debt and close the cohort](../specs/adversarial-priority-backlog-closeout/phase-04-reporting-debt-and-tracker-closeout/spec.md) — completion and verification live in the spec.

## Non-Goals

- Do not claim or work the P3 issues #711, #709, #705, #702, #688, #612, #599, #584, #583, or #582.
- Do not keep a refuted, stale, duplicate, or over-scoped issue open merely because an ideal proof channel is expensive; close it with an honest comment and open a new issue if a later concrete defect appears.
- Do not create one global task envelope, reviewer ledger, receipt stream, or implementation branch for the cohort. Each issue or disjoint issue group retains its own owner and closeout.
- Do not push, tag, publish a release, or claim hosted/installed adoption without a separate phase-scoped operator grant.
- Do not run fresh-eye review for bulk issue classification or stale tracker cleanup. A later implementation that changes verdict logic still follows the repo's real change-boundary review rule.

## Boundaries

- GitHub is the source of truth for issue identity, comments, and state; current source, tests, release, and installed readbacks decide whether each premise still holds.
- Issue closure is explicitly authorized for this goal. Every close gets a concise evidence comment, per-issue behavior verdict or typed disposition, and GitHub state readback.
- Push, tag, release, remote CI mutation, and installed-machine mutation are not authorized by this goal draft. Ask only when a live issue cannot close without that specific boundary.
- P0 #723 and #722 run first as the ownership/proof-diet lens; they do not become a new mandatory artifact or global gate for every later lane.
- One writer owns each lane. Independent issue reads, diagnosis, tests, and closeouts run in parallel; shared files are assigned to one integrating owner before mutation.
- Bug-class bulk requalification does not spawn fresh-eye reviewers. Debug/root-cause work precedes a live bug fix; bounded review is reserved for actual substantial or verdict-logic changes.
- The historical active artifacts `2026-08-12-resolve-open-quality-and-trust-backlog.md` and `2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md` own earlier fixed cohorts and are not continuation state for this goal.
- Completion requires all 26 claimed issues to be CLOSED. If an issue needs an operator-only decision or unauthorized publication after every safe lane is exhausted, the goal becomes blocked with that exact boundary instead of claiming completion.

## User Acceptance

- `gh issue list --state open` contains none of the 26 claimed issue numbers.
- Every claimed issue's final comment states why it closed: stale/refuted, consolidated/split, already satisfied, or repaired with the behavior channel named.
- The user can inspect one goal reconciliation table mapping each issue to its owner, disposition, carrier, and final GitHub state.
- No P3 issue, push, release, hosted CI, or installed adoption appears as completed unless a later explicit grant and matching readback are recorded.

## Agent Verification Plan

### Low-Cost Checks

- Re-read each issue and comments with `issue_tool.py read`; capture one-line JTBD, premise state, owner, and sibling decision.
- Use `rg`, current source inspection, focused tests, and exact command readbacks before proposing implementation.
- Validate closeout drafts before GitHub mutation and immediately verify state after each independent close.

### High-Confidence Checks

- For live bugs, reproduce or falsify the exact reported arm and run the first consumer of the repaired output, not only a helper unit test.
- Run changed-surface and owner-specific gates for implementation slices; use broad standing/release proof only when a shared bundle or proof surface requires it.
- Changes to verdict logic receive the repo-required bounded review over the repaired surface; bulk classification and no-change cleanup do not.

### External Or Live Proof

- GitHub comment/state readback is required for every issue close.
- Installed, hosted, remote-CI, or public-release proof runs only for issues whose JTBD names that channel and only after the necessary operator grant.
- A missing external channel is recorded as a typed non-claim; it does not force unrelated local proof or keep a refuted tracker record open.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Requalify all 26 premises; apply #723/#722 ownership diet | Prevent stale framing and over-validation from generating implementation work | Per-issue premise/owner/proof-diet ledger; immediate closeouts for refuted rows | planned |
| 2 | Resolve consumer and authoring boundaries | These determine which implementation and operator paths later proof can trust | Phase-2 spec evidence for #721, #715, #692, #667, #637, #634, #628, #546 | planned |
| 3 | Resolve proof, release, and runtime boundaries | False verdict and orphan-process paths can invalidate later closeout evidence | Phase-3 spec evidence for #701, #700, #699, #698, #697, #695, #694, #693, #669, #668 | planned |
| 4 | Resolve reporting debt and reconcile every tracker row | The goal ends on issue-specific outcomes, not on a green aggregate | Phase-4 spec evidence; all 26 CLOSED; final reconciliation, retro, and successor | planned |

## Backlog Recount

- Counted: 36 open issues on 2026-08-26 after the owner-directed cleanup, using `gh issue list --repo corca-ai/charness --state open --limit 100`.
- Claims: #723, #722, #721, #717, #715, #710, #708, #706, #704, #703, #701, #700, #699, #698, #697, #695, #694, #693, #692, #669, #668, #667, #637, #634, #628, and #546 — 26 current P0–P2 issues.
- Not claimed: #711, #709, #705, #702, #688, #612, #599, #584, #583, and #582 — 10 P3/stale/deferred candidates reserved for a separate cleanup decision.
- Premise state: initial audit only. #669, #715, and #721 were explicitly restored from the cleanup bucket after current-source inspection found live residue; every claimed issue is re-read at activation before work or close.

## Operator Decision Queue

- Decision: authorize push/release/host mutation only if a live issue cannot close without publishing a new carrier.
- Owner: repository operator.
- Why deferred: issue requalification, local implementation, targeted proof, and already-shipped closeouts remain safe and useful without that grant.
- Unblock action: approve the exact phase, target revision, and external operation after its local carrier is ready.
- Revisit trigger: the first live issue whose acceptance boundary requires shared-history or installed/hosted adoption proof.

## Coordination Cues

- Phases: issue, debug, implementation, quality, critique, retro.
- Routing: `charness:issue` owns tracker truth and per-issue closeout; `charness:debug` owns falsifiable root cause for live bugs; `charness:impl` and `charness:quality` own fixes and proportional proof; `charness:critique` runs only at substantial/change boundaries; `charness:retro` owns final waste disposition.
- Gather: n/a — the source of truth is the adapter-selected GitHub issue backend and local repository, not a source imported into a durable gathered asset.
- Release: n/a at draft — no version or publication change is authorized; update this line if an activated issue lane receives a release grant.
- Issue closeout: planned — issue-specific manual/direct carriers after draft validation, with behavior/disposition evidence and `verify-closeout --expect-state CLOSED`; no single cohort carrier.
- Successor goal: n/a at draft — completion must replace this with a learned successor or an explicit no-successor reason.

## Discuss Before Activation

- Discuss before activation: resolved — the owner requested one broad P0–P2 goal, explicitly authorized evidence-backed issue closures, required issue-level parallelism, rejected fresh-eye cost for bulk bug classification, and did not authorize push or release. P0 #723/#722 remain first, while #669/#715/#721 stay live after adversarial cleanup review.

## Slice Log

No implementation slice has run. The current artifact is an inert Before-phase draft.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [Design north star](../../docs/design-north-star.md) — keep teeth where a wrong issue verdict or closure escapes; issue closeout gets distinct tracker readback and behavior evidence.
2. GitHub open issue bodies/comments for the 36-issue post-cleanup inventory — tracker identity and freshness source.
3. [Tracker requalification packet](../issues/2026-08-22-tracker-requalification.md) — prior per-issue probe/disposition evidence, used as history rather than current truth.
4. [Recent lessons](../retro/recent-lessons.md) — premise-first, exact-quantity, timeout, and structural-property lessons shaping the proof diet.
5. [Handoff](../../docs/handoff.md) — release/claims state; its #689/#690/#691/#713 open-issue statements are stale and do not select this cohort.

## Interview Decisions

- Scope family: all open issues, only top priority, or P0–P2. Chosen: current P0–P2 cohort of 26; rejected all-open because P3 cleanup would dilute live boundary work, and rejected P0-only because shared P1/P2 owners determine whether P0 fixes stay small.
- Execution family: one claimed task, issue-group lanes, or one lane per issue. Chosen: issue or disjoint issue-group lanes under one goal outcome; rejected one claimed task because it serializes independent work, while strict one-lane-per-issue is unnecessary when files and root cause are genuinely shared.
- Closure family: archive-until-perfect, proportional evidence, or automatic stale close. Chosen: adversarial judgment plus proportional evidence and reopen/new-issue tolerance; rejected archival proof because it preserves stale records, and rejected automatic closure because #669/#715/#721 demonstrate live residue can hide behind apparent fixes.
- Host axis: Codex and Claude have different hook/subagent capabilities. The goal records host-specific evidence per lane and never promotes one host's path or model controls to a global contract.
- Publication family: local/issue closeout now, push/release later only if needed. Chosen because the user authorized issue closure but not shared-history publication.

## Plan Critique Findings

- Owner-directed audit, no fresh-eye plan reviewer: bulk issue classification review was explicitly judged wasteful for this run.
- Adversarial correction folded: #669 remained live because SIGTERM may still interrupt `Popen` before the child handle is bound; #715 remained live because the resolver is optional rather than mandatory worker admission; #721 remained live because the typed persistence producer is not the prescribed debug authoring path.
- Counterweight: do not turn those three misses into a universal new gate. Each stays an issue-owned lane; #723/#722 define the ownership diet before adding enforcement.
- Over-worry rejected: one release, one global receipt, or broad standing proof per issue would add cost without improving stale/no-change closure truth.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: this goal and four phase specs; the 26 GitHub issue bodies/comments; per-issue premise/owner ledger; source, tests, release, and installed evidence actually selected by each lane. Retro, packet, reviewer, lock, and closeout records are terminal evidence, not semantic inputs.
- Frozen target: each implementation lane binds its own committed semantic target; final goal closeout freezes the integrated target SHA plus the exact 26-issue reconciliation snapshot.
- Fresh-eye: none for bulk premise audit or no-change cleanup by owner decision; substantial implementation uses an independent bounded reviewer when the changed boundary requires it, while GitHub state readback and behavior tests remain distinct evidence channels.
- Verification lock: final goal closeout records the repo-owned closeout/quality lock and its evidence path over the frozen integrated target; any semantic code/spec or claimed-cohort edit invalidates and rebinds the lock.
- Complete flip: only after all 26 issue states read CLOSED, every per-issue behavior/disposition is recorded, final packet/review/lock obligations are resolved, and terminal retro/status bookkeeping is written outside the reviewed identity.

## Off-Goal Findings

- None at draft time. New P3 or unrelated findings route through `charness:issue` and are referenced here without silently expanding the cohort.

## Final Verification

No final verification is claimed by this draft. The activated run must record the frozen target, 26-issue CLOSED reconciliation, final quality/lock evidence, retro, host-metric availability, and disposition review before completion.

## User Verification Instructions

After completion, run the goal validator and list the 26 claimed issue numbers from GitHub; compare the returned CLOSED states and final comments with the reconciliation table recorded here.

## Auto-Retro

The activated run owns Auto-Retro. Every surfaced improvement must end as an applied structural change, a tracked issue, a repo-local guard, or an explicit no-action reason before the goal can complete.
