# Achieve Goal: Dogfood charness 0.45.0 in ceal — validate achieve-efficiency improvements

Status: draft
Created: 2026-06-13
Activation: `/goal @charness-artifacts/goals/2026-06-13-ceal-achieve-efficiency-dogfood.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Current slice intent: before activation. The reviewable-intent unit in progress
  and the commits it spans; critique and broad proof do not re-fire within one
  unchanged intent — update it when the intent changes, not per commit
  (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-13-ceal-achieve-efficiency-dogfood.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Validate, in **ceal** (`../ceal`) — the repo where the original achieve-waste was
reported — that charness **0.45.0**'s achieve-efficiency improvements actually
reduce that waste, and characterize what direction **E** (closeout-telemetry,
currently charness-internal) needs to also work there. Concretely: update ceal to
0.45.0, run a representative achieve+retro cycle under the new contract, compare
the three originally-reported waste symptoms against ceal's pre-0.45.0 retro
baseline, and produce a recorded decision on the deferred follow-ons (E2b,
ceal-propagation of E's emitter, A2). This is the keystone that closes the
original loop and generates the real data E2b's reopen trigger depends on.

## Non-Goals

- Implementing E2b, A2, or the Coordination-Cues floor merge in this goal — those
  are **decision-gated** by what the dogfood finds, not pre-committed.
- Fixing ceal's product code or doing broad ceal refactors.
- Building a new run loop or execution engine.
- Mutating charness skills, except a narrow version-skew defect the dogfood
  surfaces (then routed through `issue`/`impl`, not done inline here).
- Cutting another charness release (0.45.0 already shipped).

## Boundaries

- **Cross-repo:** the work happens in `../ceal` (`charness update` there + a real
  achieve/retro run). The charness repo is touched only to record this goal/its
  outcome, or to file/fix a surfaced version-skew defect.
- **External side-effect scope:** the only outward action is `charness update`
  inside ceal (a local install refresh). No publish/push of ceal, and no charness
  release/push, unless the operator explicitly asks. Approval is phase-scoped and
  does not carry forward.
- Discuss before activation: (1) cross-repo autonomous execution in `../ceal` — confirm it is in scope versus operator-supervised; (2) whether this goal WIRES E's (charness-internal) telemetry emitter into ceal's own closeout (a real ceal change) or only CHARACTERIZES the gap (default: characterize); (3) which real ceal task is the dogfood vehicle for the "representative achieve cycle". Resolve or confirm these before `/goal` activation.

## User Acceptance

- ceal's charness install reports `0.45.0` (`charness --version` in `../ceal`).
- At least one real achieve+retro cycle ran in ceal under the 0.45.0 contract,
  with the goal artifact + retro committed in ceal.
- A written comparison of the three originally-reported waste symptoms (validator
  post-hoc churn; over-slicing / per-commit premortem; slow-gate-invisible-to-retro)
  vs ceal's pre-0.45.0 retro corpus, stating which improved and which did not.
- A recorded decision (here + charness spec Deferred Decisions) on each follow-on:
  E2b (proceed / keep deferred), ceal-propagation of E's emitter (do / defer), A2
  (needed / not).

## Agent Verification Plan

### Low-Cost Checks

- `charness --version` in ceal == 0.45.0; describe-first preflight + the
  over-slice / gate-runtime advisories are present in ceal's installed achieve/retro.

### High-Confidence Checks

- A full ceal achieve cycle reaches a clean closeout under the 0.45.0 contract
  (describe -> fill -> verify, with zero serial-rejection rounds on the floors the
  preflight + dry-check surface).
- The comparison artifact cites specific ceal retro lines (before) against the
  dogfood run (after), not a vibe.

### External Or Live Proof

- None beyond the local ceal install refresh. Explicit non-claim: this goal does
  NOT cut a public release or push ceal.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Update ceal to charness 0.45.0; confirm the new surfaces are present | prerequisite for any validation | `charness --version`==0.45.0 in ceal; describe-first + advisories present | planned |
| S2 | Run a representative achieve+retro cycle in ceal under the new contract | the actual dogfood | committed ceal goal + retro artifacts; closeout transcript | planned |
| S3 | Characterize the E-in-ceal gap (emitter wiring vs skills-only) | E validation depends on it | written gap analysis; closeout-telemetry present-or-absent in ceal | planned |
| S4 | Compare waste symptoms vs ceal's pre-0.45.0 baseline; decide each follow-on | the deliverable | comparison + per-follow-on decision written back to the spec | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
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

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `charness-artifacts/spec/achieve-efficiency-improvements.md` — Deferred
  Decisions (ceal propagation / version-skew; E2b; A2) and the honest non-claim
  that telemetry is per-repo (charness cannot see ceal's stream).
- `docs/handoff.md` — achieve-efficiency complete; the deferred follow-ons list.
- `charness-artifacts/release/latest.md` — 0.45.0 shipped (tag `v0.45.0`).
- `../ceal/charness-artifacts/retro/` — the pre-0.45.0 waste baseline (the
  retro corpus where the three symptoms were originally observed).

## Interview Decisions

- **Next-work selection:** chose ceal-dogfood over A2 / E2b / consumer
  announcement because it closes the *original* loop (the reported ceal waste) and
  unblocks E2b's data-dependent reopen trigger. Rejected starting E2b directly
  (blocked on real ceal data) and A2 (a refinement, lower value now).
- **Scope shape:** chose *validate + characterize* over *implement-E-in-ceal-now*,
  to keep the goal bounded and decision-gated. Whether to actually wire E's
  emitter into ceal is a `Discuss before activation` item, not a baked-in slice.

## Plan Critique Findings

Pre-activation premortem not yet run; **recommended before activation** given the
cross-repo scope. Risks to stress when it runs (already surfaced into
`Discuss before activation`): (a) ceal may not cleanly update to 0.45.0
(version-skew — the spec's central design constraint); (b) E cannot be honestly
"validated" in ceal without emitter wiring, risking a hollow claim — hence the
characterize-vs-wire decision gate; (c) "representative cycle" is undefined until
a real ceal vehicle is named.

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

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
