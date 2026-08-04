# Achieve Goal: Make mutation and quality-gate runtime actionable without weakening proof floors

Status: active
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-make-mutation-quality-gate-runtime-actionable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: B — canonical-runner mutation coverage candidate implemented;
  post-implementation proof and matched receipts remain.
- Current slice intent: preserve the mapper's exact focused test scope while
  moving scheduling, worker caps, version compatibility, and temp isolation
  back to the canonical standing runner. The slice spans the focused producer,
  its worker-coverage test, and the durable candidate evidence below.
- Next action: run the pre-lock closeout, commit the candidate so the changed-
  line consumer can judge the actual edited pool, then collect three matched
  post-change full-command receipts.
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

Give the quality-gate owner a reproducible, proof-preserving way to identify and reduce structural runtime waste on the real local closeout critical path, starting from the changed-line mutation lane. The goal may produce one safe structural remedy or an evidence-backed no-safe-change disposition; it must not weaken proof floors.

## Non-Goals

- Do not remove, weaken, skip, or make non-blocking any mutation, coverage, or
  changed-line proof floor because it is slow.
- Do not prune tests by file pattern, generalize a repo-wide in-process CLI
  harness, or reuse the rejected nested-CLI candidate as mutation evidence.
- Do not change remote CI, release, push, issue-close, or public-proof
  boundaries in this local goal.
- Do not claim host-wide token, cost, or cross-machine runtime efficiency when
  the host does not expose a goal-scoped metric window.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Measurement boundary: target the local `./scripts/run-quality.sh
  --read-only` path and its changed-line mutation producer/consumer. Pre-push,
  remote CI, release, and installed-host timings are separate proof surfaces.
- Proof boundary: preserve changed-line mapping, failure visibility, mutation
  scope, subprocess/package/environment contracts, and the existing closeout
  floor. Any verdict-logic change requires a second bounded review round that
  reads the repaired surface.
- Economic boundary: retain the fixed ten-second full-closeout materiality bar
  as the default falsifier. A subset speedup is only a selection signal until
  matched full-command relief is shown.
- Candidate boundary: before implementation, produce a phase-level
  producer/consumer/owner manifest for the current mutation pool. An ad hoc
  file list is not a migration unit.

## User Acceptance

The user can inspect one durable decision record and answer:

1. Which mutation/quality-gate phase is expensive, over what comparable window,
   and who owns its producer and consumer?
2. What single structural candidate was tested, what proof invariant did it
   preserve, and did matched full-command runs show at least ten seconds of
   relief?
3. If no remedy was safe, what evidence ruled out the candidates and what
   measured reopen trigger remains?
4. Which claims are local-only, and which remote/provider/live claims were not
   run?

## Agent Verification Plan

### Low-Cost Checks

- Read D51, issue #505's problem-first body, the current mutation mapper, and
  `run-quality.sh` phase ownership before choosing a remedy.
- Run the current mutation mapper with `--detail` and record its mapped pool
  rather than assuming the CLI family is relevant.
- Build a node/phase-level candidate manifest with command, owner, boundary,
  proof purpose, and falsifier before changing implementation.
- Use cheap deterministic validators and focused tests at each boundary; do
  not run the broad final gate until the candidate and proof ledger are frozen.

### High-Confidence Checks

- Run three comparable full `./scripts/run-quality.sh --read-only` receipts and
  report medians for total, standing pytest, and changed-line mutation.
- For one owned family, run before/after measurements through the real command
  and retain the changed-line mapping and failure-path proof.
- Obtain a bounded fresh-eye review with an explicit before snapshot and window
  id. If verdict logic changes, run the required second repaired-surface round.
- Run the strongest final local quality gate and `check_goal_artifact.py` after
  all goal and evidence surfaces are frozen.

### External Or Live Proof

No external or live proof is in scope. The issue is context and destination
only; this goal does not close #505, push, publish, or claim remote CI.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Map the mutation critical path and its owner | The prior goal proved the CLI family is not the mutation bottleneck | Three current baseline receipts, mapper output, phase/consumer manifest, proof ledger | completed — recorded with Slice 1 before implementation |
| B | Falsify or implement one owned structural candidate | A named owner and materiality test are required before code changes | Matched before/after full-command runs, focused preservation checks, rollback/no-safe-change decision | in progress |
| C | Lock the decision and close honestly | Runtime relief is provisional until independently observed | Final quality, fresh-eye review, complete validator, retro, and explicit #505 follow-up | pending |

## Operator Decision Queue

none — the operator selected #505, local mutation-lane scope, the ten-second
materiality bar, and proof-preserving local work before this draft was saved.

## Coordination Cues

Routing: quality — selected for mutation-lane measurement and validation design;
critique — selected for candidate and final claims review; impl — reserved for a
proof-preserving remedy only after the owner manifest passes.
Gather: charness-artifacts/gather/2026-08-05-issue-505-source.md — issue #505 was
captured through authenticated `gh` after the public URL route stopped at a
CAPTCHA.
Release: n/a — this goal does not touch release surfaces.
Issue closeout: n/a — #505 is context and follow-up destination, not an issue
being closed by this goal.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — the operator selected #505 as the next
  goal, limited it to the local mutation/quality-gate lane, retained the fixed
  ten-second bar and all proof floors, and deferred push, release, remote CI,
  and issue closeout.

## Slice Log

### Slice 1: B — Make focused mutation coverage use the canonical runner

- Phase/owner manifest: `run-quality.sh` queues `check-changed-line-mutation-coverage`;
  `prepush_focused_changed_line_coverage.py` owns the focused producer and
  consumer invocation; `suggest_mutation_coverage_command.py` owns changed-pool
  to standing-test mapping; `mutation_coverage_producer.py` owns coverage setup,
  shard combine, and the focused artifact; `check_changed_line_mutation_coverage.py`
  owns the changed-line verdict; `run_standing_pytest.py` owns xdist activation,
  worker width, scheduler compatibility, and external temp isolation. The
  mapped pool before this edit was `scripts/retro_persistence_lib.py`,
  `scripts/validate_inventory_consumption.py`,
  `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`, and
  `skills/public/retro/scripts/persist_retro_artifact.py`; all four mapped to
  30 standing test files and 667 collected tests. This is the migration unit,
  not a file-count candidate list.

- Objective: Replace the focused changed-line coverage producer's serial bare-pytest launch with the canonical standing runner, preserving the mapped target set, release_only scope, subprocess coverage, focused artifact path, and consumer verdict semantics.
- Why this approach: Slice A established the current owner: check-changed-line-mutation-coverage consumes 120.4–120.9 seconds of a 123.5–124.0 second read-only quality run. The mapper selects four changed pool files, 30 standing test files, and 667 collected tests. An unmodified xdist spike over the same mapped tests passed and exported coverage in 47.68 seconds, clearing the fixed ten-second materiality bar before implementation.
- Commits: Not committed yet; the implementation and goal evidence are the current worktree slice.
- What changed: scripts/prepush_focused_changed_line_coverage.py now emits python3 scripts/run_standing_pytest.py with repeated sorted --pytest-target flags and explicit --include-release-only, so worker caps, scheduler-version compatibility, affinity, and external temp isolation remain owned by the canonical runner. Tests pin exact target multiplicity and prove two xdist workers export subprocess coverage into the focused JSON.
- Alternatives rejected: Rejected hand-assembled -n 16 flags because they duplicate runner portability policy and fail on missing/old xdist or constrained affinity. Rejected mapper/test-scope changes because the measured owner is launch scheduling, not target discovery. Broad coverage, verdict semantics, unmapped-file policy, remote CI, release, push, issue close, and Cautilus remain out of scope.
- Targeted verification: Three sequential pre-change ./scripts/run-quality.sh --read-only receipts passed 85/0: totals 123.96s, 123.75s, 124.25s; changed-line mutation 120.6s, 120.4s, 120.9s. The unmodified xdist coverage spike passed 667 tests and exported coverage in 47.68s. Pre-edit focused producer/consumer suite: 57 passed. After the implementation and probe repair: 57 passed. The first real post-edit gate run reached the canonical runner in 50.42s, then correctly returned exit 3/unestablished because the mutation-pool source file was uncommitted; no clean verdict is claimed until the slice is committed and rerun.
- Test duplication pressure: No production test family was pruned. One existing integration test was strengthened with two temporary test files and worker identity records; no duplicate-pressure expansion beyond the focused proof was introduced.
- Critique: Delegated critique executed with three distinct unnamed Codex reviewers: problem framing, diagnostic/boundary ownership, and operational counterweight. All converged on reusing the canonical runner, preserving release_only explicitly, and proving worker-level coverage. The prepared packet is `charness-artifacts/critique/2026-08-04-194549-packet.md` with its JSON binding beside it. Boundary fingerprint verification was parent-attributed for the three edited paths with no undeclared drift. Reviewer envelopes were unbound on this Codex host; reviewers performed read-only inspection by instruction. Findings received. No verdict logic changed, so the second repaired-surface round is not triggered.
- Off-goal findings: No external source or side effect was added. No push, release, remote CI, issue close, or Cautilus run occurred. Cross-invocation locking for the fixed focused artifact remains deferred and predates this candidate.
- Lessons carried forward: A focused coverage producer is still a proof boundary even when it only changes scheduling. Reuse the canonical runner instead of copying worker policy, and make scope changes such as release_only inclusion explicit when translating a wrapper command.
- Metrics: Baseline receipt sources: /tmp/charness-mutation-goal-baseline-1.log, -2.log, -3.log. Candidate spike source: /tmp/charness-mutation-xdist-spike.log. Candidate gate source: /tmp/charness-mutation-xdist-candidate-gate.log. These receipts establish local Linux x86_64 / Python 3.10.12 behavior only; no host-wide token, cost, provider, or remote claim is made.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [Design North Star](../../docs/design-north-star.md) — judgment on reversible
   local work and distinct evidence at proof boundaries.
2. [Issue #505 gathered source](../gather/2026-08-05-issue-505-source.md) —
   problem-first evidence, target outcome, and non-goals.
3. [D51](../../docs/deferred-decisions.md#d51-release-branchci-barrier-and-quality-gate-runtime)
   — existing owner and reopen context for quality-gate runtime.
4. [Completed structural runtime goal](2026-08-04-reduce-closeout-runtime-structural-waste.md)
   — baseline, rejected CLI candidate, 10-second falsifier, and #505/#506
   follow-ups.
5. [Efficiency improvements spec](../spec/achieve-efficiency-improvements.md)
   — prior gate-baseline-runtime and operational-waste design constraints.

## Interview Decisions

- Priority: chose #505 over #506 because the user wants the next goal to pursue
  measurable runtime value; #506 remains a supporting reviewer-tool follow-up.
- Scope: chose the local changed-line mutation lane over pre-push, remote CI, or
  release timing because it is the measured critical phase with a named mapper
  and owner. The other surfaces remain separate.
- Economic test: retained the ten-second full-closeout bar from the prior goal;
  isolated subset relief is not sufficient.
- Outcome: allow either one proof-preserving remedy or an evidence-backed
  no-safe-change result. A no-change result is not failure when ownership or
  materiality cannot be established.
- Side effects: chose no push, release, remote CI, issue close, or Cautilus run.
  Those boundaries require separate approval and proof.

## Plan Critique Findings

- Folded: the previous file-count candidate must become a node/phase-level
  manifest before implementation; this is now Slice A and a boundary.
- Folded: the mutation mapper, not the CLI directory, decides whether a family
  is relevant to the changed-line lane.
- Folded: the final gate reports proof pass/fail separately from volatile wall
  time; exact timing is a receipt, not an optimization claim by itself.
- Deferred: #506's reviewer snapshot helper repair is not part of this goal
  unless the selected remedy changes the review boundary.
- Counterweight: mutation coverage may be expensive because it protects a real
  proof boundary; a faster run is acceptable only if failure visibility and
  changed-line semantics remain intact.

## Off-Goal Findings

#506 reviewer snapshot/window binding remains a separate follow-up. The prior
CLI-family migration remains rejected. Host token/cost metrics, remote CI,
release ordering, push, issue close, and Cautilus remain out of scope.

## Final Verification

Retro: not applicable — this draft has no executed slice or closeout retro.
Host log probe: not applicable — no goal-scoped runtime window exists before
activation.
Disposition review: not applicable — this draft contains no completion claim.

## User Verification Instructions

Before activation, verify that #505 is still the intended next work and that
the local mutation lane—not pre-push or remote CI—is the selected boundary. At
closeout, inspect the phase manifest, three matched receipts, preservation
checks, fresh-eye review, and the explicit remedy/no-safe-change decision.

## Auto-Retro

Retro dispositions: none — no slices have executed; closeout will disposition
  any surfaced improvement from the executed window.
Structural follow-up: none — no retro exists before activation; classify any
  transferable waste only after the goal produces evidence.
