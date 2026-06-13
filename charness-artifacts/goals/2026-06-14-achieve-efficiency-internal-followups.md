# Achieve Goal: achieve-efficiency internal follow-ups (A2 describe-first conditional + floor-addition restraint nudge)

Status: active
Created: 2026-06-14
Activation: `/goal @charness-artifacts/goals/2026-06-14-achieve-efficiency-internal-followups.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: bundle closeout — both slices (S1 A2 + S2 nudge) done and
  fresh-eye critiqued (each zero Act-Before-Ship, folds applied). Now the
  bundle-boundary broad proof + goal closeout.
- Current slice intent: bundle-boundary verification + closeout. Critique and broad
  proof do not re-fire within one unchanged intent — update it when the intent
  changes, not per commit.
- Next action: commit S2, run `run_slice_closeout.py --verification-lock
  --produce-mutation-coverage` (new mutation-pool code in slice_closeout_advisories /
  describe_goal_closeout_shape), then fill the closeout via the new `--goal-path`
  describe (dogfood), write retro, flip to complete.
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
| S2 | floor-addition restraint nudge: a non-blocking advisory flagging a new blocking floor added without a recorded restraint call | gives D's prose checklist teeth (the deferred follow-up) | both-polarity unit test; advisory names the checklist; probe: how to detect "a new floor" (new `report["ok"]=False` / REQUIRED_SECTIONS entry) | done (10 tests; fresh-eye critique 0 Act-Before-Ship; conservative detector = new ok=False site + new floor-set member, line-anchored) |

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

### Slice 2: floor-addition restraint nudge (non-blocking advisory)

- Objective: Give the prose Floor-Addition Restraint checklist non-blocking teeth: advise_floor_addition_restraint flags a new blocking floor (new report ok=False site / new REQUIRED_*/_SECTIONS/_EVIDENCE_NAMES member in skills//scripts/) added without a recorded restraint call, naming the checklist. Wired into run_slice_closeout._run_preexecution_blocks.
- Why this approach: Resolves follow-up:floor-addition-restraint-nudge (the deferred D follow-up). A blocking gate is rejected (it is the exact reflex the rule names); a conservative before/after detector + recorded-call check is the advisory teeth.
- Commits: S2 commit (this slice)
- What changed: scripts/slice_closeout_advisories.py (+detectors+advisory); scripts/run_slice_closeout.py (binding + 1 call in _run_preexecution_blocks, not main()); docs/conventions/implementation-discipline.md (Teeth para); spec + audit deferred entries -> resolved; new test_floor_addition_restraint_advisory.py.
- Alternatives rejected: A blocking floor (rejected: the reflex D names). An AST tokenizer for code-only counting (rejected: line-anchored regex is simpler + robust — verified it ignores the module's own prose mentions). Scanning all changed files for floors incl tests/ (rejected: a report ok=False in tests/ is a fixture, not a floor — scoped to skills//scripts/).
- Targeted verification: 10 unit tests (pure-detector polarities + B1 non-floor-set exclusion + B2 prose-marker non-match + 4 git-integration both-polarity); 261 advisory/closeout tests green; dogfood: detect_new_floors returns [] on its own changed source (no self-false-fire); run_slice_closeout imports + binds the advisory.
- Test duplication pressure: First dedicated suite for the floor-addition nudge; pure detectors are unit-tested without git, integration via a real tmp git repo. No overlap with existing slice_closeout advisory tests (over-slice/gate-runtime/new-pool).
- Critique: Bounded fresh-eye slice critique (separate agent context): ZERO Act-Before-Ship. Folded B1 (exclude OPTIONAL/ADVISORY/EXEMPT/NARRATION/RECORDED_WORK non-floor sets) + B2 (anchor the restraint marker to line-start so prose paraphrasing the form cannot wrongly silence). Deferred V1 (generated-surface coincidental match), V2 (a required-section rename reads as new member — arguably correct), V3 (multi-file marker test).
- Off-goal findings:
- Lessons carried forward: A heuristic detector over source is honest as a conservative non-blocking advisory; line-anchoring both the floor regex and the marker regex removed the two self-reference traps (own prose counting as a floor; prose describing the marker silencing it).
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
