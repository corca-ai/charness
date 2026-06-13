# Achieve Goal: achieve-efficiency internal follow-ups (A2 describe-first conditional + floor-addition restraint nudge)

Status: active
Created: 2026-06-14
Activation: `/goal @charness-artifacts/goals/2026-06-14-achieve-efficiency-internal-followups.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: S2 — floor-addition restraint nudge: a non-blocking advisory
  flagging a new blocking floor (new `report["ok"]=False` site / new
  `REQUIRED_SECTIONS` entry) added without a recorded Floor-Addition Restraint call.
- Current slice intent: S2 floor-addition restraint nudge. (S1 A2 done + fresh-eye
  critiqued, zero Act-Before-Ship; committing.) The reviewable-intent unit in
  progress and the commits it spans; critique and broad proof do not re-fire within
  one unchanged intent — update it when the intent changes, not per commit.
- Next action: ship the conservative new-floor detector (git-diff added
  `report["ok"] = False` site / new `REQUIRED_SECTIONS` member) as a non-blocking
  advisory naming the implementation-discipline checklist; both-polarity unit test;
  fresh-eye critique; then bundle-boundary broad proof + closeout.
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

Continue the achieve-efficiency line with **charness-internal** follow-ups from the
spec's Deferred Decisions and the D closeout-floor audit — no cross-repo work.
Two additive refinements that tighten the achieve closeout contract without
removing any floor: **A2** make the describe-first preflight *goal-conditional* so
it also surfaces the conditional `keep` floors the static catalog cannot (closing
the residual Problem-1 churn the D audit named); **floor-addition restraint nudge**
give D's prose restraint-checklist actual (non-blocking) teeth so a new blocking
floor cannot land silently without a recorded restraint call.

Canonical context: `charness-artifacts/spec/achieve-efficiency-improvements.md`
(Probe A2; Deferred `follow-up:floor-addition-restraint-nudge`) and
`charness-artifacts/audit/closeout-floors.md`.

## Non-Goals

- **E2b** (chunker ingests recurring waste) — deliberately NOT here: it needs real
  varied-usage telemetry to be meaningful, and we chose not to dogfood in ceal, so
  E2b stays deferred until natural 0.45.0 usage produces data that trips its
  reopen trigger.
- **Coordination-Cues floor *merge/removal*** — the D audit's `merge` candidate is
  floor *removal*, which the spec's "Deliberately Not Doing" reserves for a
  separate critiqued change; out of scope here (this goal only *adds*).
- ceal / any cross-repo work; a new release; a new run loop.

## Boundaries

- charness-internal only; no `../ceal`, no other repo.
- A2 edits a prompt/skill surface (`describe_goal_closeout_shape.py` + achieve
  references) — keep deterministic skill validation local; no live Cautilus unless
  a log-backed behavior-proof request appears.
- No floor is removed or made blocking; both slices are additive (richer preflight
  output; a non-blocking advisory). No new *blocking* gate — that would be the
  exact reflex D's checklist guards against.
- External side-effect scope: none beyond a normal local closeout; any push is
  operator-approved at the bundle boundary, not per slice.
- Discuss before activation: resolved: additive + charness-internal scope (no cross-repo, no floor removal, no release); the only consequential signal is the deliberate proof non-claim (no live Cautilus / no release), which is the correct default for additive skill refinements — no operator decision needed.

## User Acceptance

- `describe_goal_closeout_shape.py --goal-path <fixture>` emits only the floors that
  fixture triggers (and which are satisfied) — runnable by hand on a multi-floor
  and a bare fixture; the achieve After-phase describe-first step now yields the
  goal-conditional missing-line set in one call (no separate dry `check_goal_artifact`).
- Adding a new blocking floor without recording a Floor-Addition Restraint call
  surfaces a non-blocking advisory naming the checklist; an already-recorded or
  no-new-floor diff stays silent (both polarities demonstrable).

## Agent Verification Plan

### Low-Cost Checks

- Unit tests: A2 over a multi-floor fixture and a bare fixture (only triggered
  floors emitted); the floor-addition nudge fires on a synthetic new-floor diff and
  stays silent otherwise.
- `validate_skills` + skill length/ergonomics gates pass for the achieve surface edits.

### High-Confidence Checks

- A real `achieve` closeout draft built from the A2 goal-conditional output passes
  `check_goal_artifact.py` on the first flip (zero serial-rejection rounds,
  including on the conditional `keep` floors the static catalog used to miss).
- `run_slice_closeout.py` bundle boundary green; `plugins/` mirror synced.

### External Or Live Proof

- None required; explicit non-claim — no live Cautilus / no release in this goal.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | A2: make `describe_goal_closeout_shape.py` goal-aware (`--goal-path`); emit only triggered floors + satisfied state; wire into the achieve After-phase | closes the residual Problem-1 churn the D audit flagged on conditional `keep` floors | multi-floor + bare fixture unit tests; first-flip closeout on a conditional floor | done (6 tests; fresh-eye critique 0 Act-Before-Ship) |
| S2 | floor-addition restraint nudge: a non-blocking advisory flagging a new blocking floor added without a recorded restraint call | gives D's prose checklist teeth (the deferred follow-up) | both-polarity unit test; advisory names the checklist; probe: how to detect "a new floor" (new `report["ok"]=False` / REQUIRED_SECTIONS entry) | planned |

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

### Slice 1: A2: goal-conditional describe_goal_closeout_shape

- Objective: Add a --goal-path mode that emits only the floors THIS goal triggers (and which are missing), folding the dry check_goal_artifact preview into one call; wire into the achieve After-phase (SKILL.md + lifecycle.md).
- Why this approach: Closes the residual Problem-1 churn the D audit named: the static catalog cannot surface runtime-conditional keep floors (rungs 1a/1b/1e, section-placeholder, closeout-delegation, timebox). The mode reuses the LIVE check_complete_evidence + check_timebox_closeout reports, so it cannot drift from the gate.
- Commits: S1 commit (this slice)
- What changed: describe_goal_closeout_shape.py (+_evidence_unsatisfied/_evidence_row/_floor_rows/goal_conditional_shape/render_goal_conditional, --goal-path CLI); SKILL.md After bullet; lifecycle.md Closeout preflight; new test_describe_goal_closeout_shape.py; plugins/ mirror synced.
- Alternatives rejected: Re-deriving floor triggers in the describe (rejected: drift risk — reused report fields instead). A new sibling module (rejected: 98 lines headroom remained; cohesive with the existing describe concept). Covering proof-mismatch/HEAD-freshness (rejected: from-scripts loader weight + not D-audit keep floors; left to the flip gate, stated as an explicit non-claim).
- Targeted verification: 6 new unit tests (multi-floor + bare-grandfathered + rung-1e/1a keep-floor + non-blocking CLI + static-catalog backward-compat); 575 goal/preflight tests green; validate_skills + validate_skill_ergonomics + check_doc_links pass; live dogfood: the mode correctly surfaced this goal's Routing: + Auto-Retro placeholder floors the static catalog misses.
- Test duplication pressure: New test file is the first dedicated suite for describe_goal_closeout_shape's goal-conditional path; no duplication with test_check_artifact_surface_preflight (which only covers the static required_shape/stub). Fixtures are purpose-built, not copied.
- Critique: Bounded fresh-eye slice critique (separate agent context): ZERO Act-Before-Ship. Folded B1 (docstring also names the mutable-HEAD floor) + B2 (--goal-path/--stub mutual exclusion). Deferred V1 (section-placeholder pre-draft surfacing — honest reflection of the #359 floor) + V2 (timebox satisfied is clock-dependent — test asserts only triggered, by design).
- Off-goal findings:
- Lessons carried forward: Conditional-floor modules already expose rich *_scope/*_floor sub-reports (triggered/satisfied/enforced) — the goal-conditional view is pure projection over them, the drift-free way to add A2.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `charness-artifacts/spec/achieve-efficiency-improvements.md` — Probe A2
  (goal-conditional describe) and the deferred `follow-up:floor-addition-restraint-nudge`.
- `charness-artifacts/audit/closeout-floors.md` — the `keep` floors A2 would absorb
  (rungs 1a/1b/1e, section-placeholder, delegation, timebox) and the honest
  non-claim that D's checklist is prose without teeth.
- `docs/conventions/implementation-discipline.md` — the Floor-Addition Restraint
  checklist S2 gives teeth to.
- `skills/public/achieve/scripts/describe_goal_closeout_shape.py` — S1's edit target.

## Interview Decisions

- **Next-work selection:** operator chose charness-internal follow-ups only and
  rejected the ceal cross-repo dogfood (a charness session mutating a separate repo
  was out of scope). The fix already shipped in 0.45.0; measuring it in ceal was
  optional and is dropped.
- **Which internal items:** chose the two *additive* follow-ons (A2 + the restraint
  nudge). Rejected E2b (needs real usage data we opted not to gather) and the
  Coordination-Cues floor *merge* (floor removal — a separate critiqued change per
  the spec). So this goal cannot trip a "Discuss before activation" gate: no
  cross-repo, no removal, no irreversible effect.

## Plan Critique Findings

Pre-activation premortem not yet run; light and optional given the additive,
charness-internal scope. Worth stressing when it runs: (a) S2's "detect a new
floor" is genuinely fuzzy — keep it a probe and ship the conservative detector
(new `report["ok"]=False` site / new `REQUIRED_SECTIONS` entry) rather than
over-reaching; (b) A2 must stay an authoring affordance, not become a new hard
precondition that blocks the flip (the spec's Deliberately-Not-Doing).

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
