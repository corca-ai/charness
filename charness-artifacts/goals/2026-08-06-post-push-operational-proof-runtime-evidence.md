# Achieve Goal: 푸시 이후 운영 증거와 런타임 비용의 구조적 개선

Status: draft
Created: 2026-08-06
Activation: `/goal @charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md` after confirming the draft is
  still intended.
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

현재 푸시된 main의 원격 CI·이슈 상태를 독립적으로 닫고, 이번 회고가 남긴 런타임 비용과 mutation producer 선택의 불확실성을 측정 가능한 구조적 개선으로 전환한다. 먼저 현재 SHA를 기준으로 remote readback을 수행한 뒤, 동일 호스트에서 isolated validator와 contended quality phase를 controlled A/B로 비교하고, mutation-coverage suggestion helper가 필요한 producer 명령을 빠짐없이 제시하는지 검증한다. 근거가 충분한 경우에만 가장 작은 gate/workflow 개선을 적용하고, source/plugin sync·fresh-eye·전체 품질 gate를 다시 통과시킨다.

## Non-Goals

- Do not retune the 15.5-second runtime floor from one host-local sample or
  convert an advisory signal into a blocking gate without controlled evidence.
- Do not run Cautilus, publish a release/tag/version bump, create a PR, or push
  a new commit unless that boundary is explicitly activated and gated.
- Do not widen the typed non-Markdown command detector into arbitrary strings or
  shell-language parsing; keep portability and consumer execution separate.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Default scope for this draft is read-only remote verification plus local
  measurement and, only if evidence warrants it, a source/plugin quality
  improvement. Any later publish is a separate final phase with one gate and
  one explicit push boundary.

## User Acceptance

- The current pushed SHA has a completed GitHub Actions result read by head SHA,
  and the GitHub open-issue query is empty or its exact residual is recorded.
- A checked-in runtime evidence artifact compares isolated and contended runs
  with commands, samples, units, and a conclusion that does not outrun the
  evidence.
- The mutation producer suggestion path is either proven complete for the
  measured slice or its missing producer class is recorded as a bounded
  follow-up; no mutation floor is weakened.
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

### High-Confidence Checks

- Run a same-host controlled comparison between the declaration validator alone
  and the equivalent contended quality phase, recording repeated samples and
  units before proposing any budget change.
- Preserve existing receipts, failure propagation, source/plugin mirrors, and
  the changed-line mutation floor. Use a bounded fresh-eye review if verdict
  logic changes.

### External Or Live Proof

- Use GitHub Actions and GitHub issue adapter readbacks as distinct observers
  after the already-published SHA; record provider/installed-host behavior as
  non-claims unless separately exercised.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Close the current pushed-SHA remote proof loop | The last session deliberately stopped at push while CI was asynchronous | CI head-SHA result, empty/residual issue list, handoff reconciliation | draft |
| 2 | Measure isolated-vs-contended runtime cost | The runtime-budget diagnosis is still moderate without A/B evidence | durable runtime sample with units, commands, and unchanged-floor decision | draft |
| 3 | Make mutation producer selection complete or explicitly bounded | Manual producer expansion was a repeat source of waste | helper output, focused producer proof, or a bounded repo-local follow-up | draft |

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

Routing: achieve → quality → retro → handoff — the next run crosses goal, validation, measurement, and closeout phases.
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

## Interview Decisions

- Scope: post-push verification and local evidence first; a new publish is not
  implied by this draft. This preserves the user's one-push boundary from the
  preceding session.
- Runtime decision: measure before changing the budget. A passing gate or one
  isolated timing is insufficient to establish a new floor.
- Producer decision: use the repository helper as the first source of truth,
  then record any missing class rather than silently hand-expanding forever.

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

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

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

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
