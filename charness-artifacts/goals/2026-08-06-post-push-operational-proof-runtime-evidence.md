# Achieve Goal: 푸시 이후 증거·slice 실행·런타임 비용의 구조적 개선

Status: active
Created: 2026-08-06
Activation: `/goal @charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 1 — frozen published baseline and slice-manifest contract.
- Current slice intent: bind the exact published target, captured CI/issue
  context, owner-anchored source/plugin roots, explicit captured-vs-current
  validation, and a bounded fresh-eye record before later preflight slices.
- Next action: finish the focused surface checks and `run_slice_closeout.py
  --skip-broad-pytest`, then commit the verified slice; do not push.
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

현재 푸시된 main의 원격 증거를 재확인한 뒤, 지난 goal에서 반복된 상태·증거·명령 재조립을 구조적으로 제거한다. 하나의 slice manifest가 live premise, target SHA, carrier, behavior proof, critique packet, source/plugin surfaces, remote readback을 소유하게 하고, 구현 전 premise preflight와 최종 bundle preflight가 stale/duplicate/부분 해결을 조기에 거부하게 한다. Quality runner에는 isolated-vs-contended runtime 진단과 완전한 mutation producer command discovery를 붙이며, publish ledger가 immutable push SHA를 기준으로 issue/CI/goal/handoff 상태를 reconcile한다. 모든 개선은 source/plugin sync, bounded fresh-eye, focused regression, 전체 품질 gate를 통과한 뒤에만 적용한다.

## Non-Goals

- Do not retune the 15.5-second runtime floor from one host-local sample or
  convert an advisory signal into a blocking gate without controlled evidence.
- Do not run Cautilus, publish a release/tag/version bump, create a PR, or push
  a new commit unless that boundary is explicitly activated and gated.
- Do not widen the typed non-Markdown command detector into arbitrary strings or
  shell-language parsing; keep portability and consumer execution separate.
- Do not turn the slice manifest into a second source of truth for issue bodies;
  GitHub remains the issue-state source and the manifest owns only execution and
  proof identity.
- Do not build a universal scheduler or publish automation before the narrow
  runtime, producer, and closeout seams have falsifiable evidence.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Default scope for this draft is read-only remote verification plus local
- measurement and structural source/plugin quality improvements. Any later
  publish is a separate final phase with one gate, one immutable ledger, and one
  explicit push boundary.
- The manifest, preflight, bundle, runtime diagnostic, producer discovery, and
  publish ledger are all in scope; consumer installation/provider roundtrip,
  release versioning, and new issue closeouts are not.

## User Acceptance

- The current pushed SHA has a completed GitHub Actions result read by head SHA,
  and the GitHub open-issue query is empty or its exact residual is recorded.
- A checked-in runtime evidence artifact compares isolated and contended runs
  with commands, samples, units, and a conclusion that does not outrun the
  evidence.
- The mutation producer suggestion path is either proven complete for the
  measured slice or its missing producer class is recorded as a bounded
  follow-up; no mutation floor is weakened.
- A slice manifest and final-bundle preflight can reproduce the selected slice's
  inputs, generated surfaces, proof commands, and closeout state without manual
  reconstruction.
- Premise preflight rejects a stale, duplicate, already-shipped, or
  partial-repair premise before implementation, with the decision persisted.
- The publish ledger reconciles one immutable push SHA to issue state, CI state,
  goal state, and handoff state, and refuses stale `OPEN`/`pending` claims.
- If code or workflow changes land, source/plugin parity, focused regression,
  bounded fresh-eye review, and the full applicable quality gate pass.

## Agent Verification Plan

### Low-Cost Checks

- Read `docs/handoff.md`, `charness-artifacts/retro/recent-lessons.md`, the
  current quality artifact, and live GitHub state before shaping a slice.
- Query CI with `gh run list` filtered to the exact current head SHA; do not use
  a parent or push exit code as the CI result.
- Run the mutation suggestion helper and inspect its producer set before
  selecting focused tests.
- Run the slice-manifest and premise-preflight commands before shaping any
  implementation slice; record the exact source/export/consumer reader roots.
- Run final-bundle preflight in dry-run mode before any commit or publish-boundary
  gate; it must list all generated and proof surfaces it will validate.

### High-Confidence Checks

- Run a same-host controlled comparison between the declaration validator alone
  and the equivalent contended quality phase, recording repeated samples and
  units before proposing any budget change.
- Preserve existing receipts, failure propagation, source/plugin mirrors, and
  the changed-line mutation floor. Use a bounded fresh-eye review if verdict
  logic changes.
- Exercise the manifest from a clean checkout or disposable fixture, mutate one
  input identity, and verify that the preflight refuses the stale packet.
- Exercise publish-ledger reconciliation against a known completed CI run and a
  deliberately pending fixture without writing GitHub state.

### External Or Live Proof

- Use GitHub Actions and GitHub issue adapter readbacks as distinct observers
  after the already-published SHA; record provider/installed-host behavior as
  non-claims unless separately exercised.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Freeze the current published baseline and slice-manifest contract | Every later improvement needs one identity-bearing execution record | manifest schema, current-head readback, source/plugin/consumer root matrix | implementation complete; closeout pending |
| 2 | Add implementation-time premise preflight | Stale, duplicate, and already-shipped premises caused rework across the 15-hour run | live issue/tree differential fixtures, refusal reasons, persisted decision | draft |
| 3 | Build final-bundle preflight and proof-command generation | Manual sync, probe refresh, packet binding, and gate selection were repeatedly reconstructed | dry-run bundle plan, generated command set, artifact/surface inventory | draft |
| 4 | Make runtime diagnosis controlled and owner-aware | Broad gate timing was mistaken for validator cost | isolated-vs-contended repeated samples, units, attribution, unchanged-floor decision | draft |
| 5 | Complete mutation producer discovery | Focused producer expansion required manual additions | helper completeness matrix, focused producer proof, bounded residual | draft |
| 6 | Reconcile publish state through an immutable ledger | Goal/handoff claims lagged the pushed issue and CI state | push-SHA ledger, issue/CI readback, stale-claim refusal fixtures | draft |
| 7 | Integrate, fresh-eye review, and close the structural loop | All improvements must survive together at the real proof boundary | source/plugin parity, critique, full gate, retro dispositions, updated handoff | draft |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Coordination Cues

Routing: achieve — this goal coordinates premise, implementation, quality, critique, retro, and handoff phases.
Routing: impl — the manifest, preflight, bundle, runtime, producer, and ledger changes are implementation work.
Routing: quality — runtime attribution, mutation producer completeness, and full-gate posture belong to quality.
Routing: critique — the structural contract and any verdict-logic changes require before-the-fact fresh-eye review.
Routing: retro — each improvement must be dispositioned as applied, bounded, or deliberately deferred with a destination.
Routing: handoff — the publish ledger and next action must be reconciled into the continuation baton.
Gather: n/a — no new public external source is intended; GitHub is read through the issue/CI adapters.
Release: n/a — this draft does not authorize a release surface.
Issue closeout: n/a — this draft does not resolve a new tracked issue; live issue state is only a post-push proof input.

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

- Discuss before activation: confirmed — activate only after reading the pushed
  SHA's current CI and issue state; keep any new publish behind a separate final
  gate and do not infer runtime budget changes from a single sample.

## Slice Log

### Slice 1: Freeze published baseline and slice-manifest contract

- Objective: Bind the published target, captured remote proof, owner-anchored reader roots, and source/plugin parity for later evidence slices.
- Why this approach: Later preflight and ledger work needs one stable identity record instead of reconstructing target and surface state manually.
- Commits: Closeout commit for Slice 1; recorded before commit because the slice log is part of the supported artifact state.
- What changed: Added the checked-in slice manifest, offline validator and CLI, source/plugin mirror, 24 focused regressions, durable design and implementation critique records, and the captured-vs-current verification boundary.
- Alternatives rejected: Deferred live refresh, command execution, scheduler/orchestration, installed/provider proof, and a second packaging ownership registry to later named slices.
- Targeted verification: Focused pytest: 24 passed; manifest CLI captured validation and --verify-current passed; checked-in plugin missing-manifest boundary and help guidance passed; source/plugin files are byte-identical; packet and critique artifact bindings validate.
- Test duplication pressure: Changed-scope nose clone sample scanned scripts and tests: advisory findings only, no new slice-specific family; baseline scanner version skew (0.19.0 to 0.20.0) was recorded and not re-baselined.
- Critique: Design critique passed with a clean boundary fingerprint. Implementation review round 1 found repairs; the required round 2 found and drove repairs for frozen evidence, target/ref binding, CI naming/non-claim, owner anchors, and structured path errors. The capped round-2 repairs are recorded accepted-unreviewed; no third round is claimed.
- Off-goal findings: No new issue, release, push, provider installation, Cautilus evaluation, or runtime-budget decision was performed.
- Lessons carried forward: Keep captured records frozen by default, make current revalidation opt-in, bind every remote claim to repository/ref/SHA, and make source-checkout-only limits visible at the operator boundary.
- Metrics: 5 reader roots; 3 parity pairs; target e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5; CI run 31062451122; captured open issues 0.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `docs/design-north-star.md` — the governing design standard and what it says
   about this goal's boundaries, teeth, and irreversible decisions.
2. `charness-artifacts/retro/2026-08-06-session-retro.md` — waste,
   counterfactuals, and the runtime/mutation follow-ups this goal turns into
   evidence.
3. `docs/handoff.md` — the first continuation command and current remote proof.
4. `charness-artifacts/quality/latest.md` — current quality receipts and
   non-claims.
5. `scripts/run-quality.sh` and `scripts/suggest_mutation_coverage_command.py`
   — the owners of the two measured seams.
6. `scripts/plan_cautilus_proof.py`, `scripts/run_slice_closeout.py`, and the
   existing issue/quality adapters — adjacent command and proof contracts that
   must remain explicit rather than copied into a new orchestrator.

## Interview Decisions

- Scope: post-push verification and local evidence first; a new publish is not
  implied by this draft. This preserves the user's one-push boundary from the
  preceding session.
- Runtime decision: measure before changing the budget. A passing gate or one
  isolated timing is insufficient to establish a new floor.
- Producer decision: use the repository helper as the first source of truth,
  then record any missing class rather than silently hand-expanding forever.
- Automation shape: prefer one manifest plus narrow composable commands over a
  monolithic “close everything” command; dry-run output must be reviewable before
  any write or gate execution.
- State ownership: GitHub owns issue state, GitHub Actions owns CI state, the
  manifest owns execution identity, and the publish ledger owns reconciliation;
  no surface may silently become a second source of truth.

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

## Plan Critique Findings

- Act before ship: bind every CI and issue claim to the exact pushed head SHA and
  use a different observer/channel than the push command.
- Over-worry rejected: no universal runtime scheduler redesign or broad command
  language parser; the smallest evidence-producing seam is the target.
- Valid but defer: installed consumer/provider roundtrip, Cautilus, release
  publication, and a new GitHub issue remain outside this draft unless reshaped.
- Act before ship: the final-bundle command must refuse incomplete generated
  mirrors, unbound critique inputs, missing behavior channels, or a carrier/CI
  SHA mismatch before the broad gate begins.
- Over-worry rejected: do not generalize premise detection to every prose claim;
  start with issue/tree/commit identity and add another class only with a
  reproducible escape.

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

- Reviewed inputs: the published baseline SHA and its remote `origin/main`
  readback, exact-head GitHub Actions run and jobs, live open-issue readback,
  this goal's semantic sections, the runtime/quality records, mutation-producer
  helper and tests, source/plugin/export inventories, and each slice's fixed
  proof packet. Slice logs, retro, critique packet, reviewer boundary
  fingerprints, lock receipts, and terminal status are derived evidence, not
  semantic inputs.
- Frozen target: bind the first manifest and all later slice packets to the
  exact published SHA read back from `origin/main`; bind implementation slices
  to their exact local commit or worktree fingerprint before proof. Any
  semantic-input, generated-surface, or target-SHA change invalidates the lock
  and requires rebinding.
- Fresh-eye: use an unnamed bounded reviewer context with a boundary
  fingerprint; a proof-surface verdict-logic repair requires a second bounded
  round over the repaired surface, capped at two rounds. Use GitHub Actions and
  issue-adapter readbacks as distinct external observers, not as a substitute
  for the reviewer.
- Distinct evidence channel: the manifest/preflight behavior must be exercised
  by fixtures or direct artifact observation that did not create the identity
  under review; runtime claims come from repeated labeled samples; remote CI
  and issue claims come from exact-SHA readbacks rather than the publish command.
- Verification lock: record focused proof, source/plugin parity, the applicable
  `run_slice_closeout.py` lock and quality-gate outputs, plus the final ledger
  reconciliation artifact. A broad lock is taken only after critique repairs
  are complete; later semantic edits require a fresh lock.
- Complete flip: write terminal evidence and `Status: complete` only after the
  manifest, preflight, bundle, runtime, producer, and ledger acceptance rows
  are each proven or explicitly dispositioned, all required fresh-eye review
  and gates pass, the bound retro/disposition evidence exists, and a final
  validator reads the reconciled state. The terminal record must not be used as
  its own semantic input.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

1. Run the exact head-SHA GitHub Actions and open-issue queries recorded in the
   final artifact.
2. Inspect the runtime evidence artifact's sample units and conclusion before
   accepting any budget decision.
3. If a code change was applied, rerun the applicable quality gate and compare
   source/plugin mirrors before accepting the slice.
4. Inspect the slice manifest and final-bundle dry-run to see exactly which
   inputs and proof commands were selected.
5. Confirm a stale or mismatched identity is refused by premise/bundle
   preflight, while a valid published SHA is reconciled into the ledger and
   handoff without a second push.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
