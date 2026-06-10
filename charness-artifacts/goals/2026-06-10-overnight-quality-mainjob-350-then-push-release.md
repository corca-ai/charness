# Achieve Goal: Overnight quality-improvement main job (+#350) then operator-authorized push + release

Status: active
Created: 2026-06-10
Activation: `/goal @charness-artifacts/goals/2026-06-10-overnight-quality-mainjob-350-then-push-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 4 — C4 commit-time handoff validation wiring (C4 pulled
  before C3: smaller, deterministic; C3 is the diagnose-first slice).
- Next action: handoff gate in staged_commit_gate_plan/surfaces + test.
- Timebox: 6h
- Activation time: 2026-06-11T06:31:18+09:00
- Implementation stop (reserve start): ~2026-06-11T11:51+09:00; hard end ~12:31.
- Closeout reserve: 40m
- Done-early policy: continue_next_improvement (quality improvement is
  deliberately open-ended inside the timebox: when a slice closes early, pull
  the next-ranked candidate from the slice-1 posture list).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; broad gate + locked
  producer/consumer at the bundle boundary before the push; live release
  proof at the final lane.
- Slice review packet: before fresh-eye slice critique, provide intent,
  changed files and owning/generated surfaces, expected invariants,
  tests/proof, non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Operator-directed overnight run (operator sleeps ~6h; directive: "이제 6시간
잘테니 그 시간동안 품질 개선 하는 걸 메인 잡으로 잡으면 좋겠습니다. 그다음
푸시 릴리즈"), synthesized from the completed post-push/#349 goal's retro,
the refreshed handoff, the open-issue state, and recent-lessons:

1. **QUALITY-IMPROVEMENT MAIN JOB (the bulk of the timebox).** Route through
   the `quality` skill. Slice 1 re-derives the quality posture on current
   main (`charness-artifacts/quality/latest.md` is stale at 2026-06-06 /
   v0.24.1; fifteen releases shipped since) and produces a prioritized,
   bounded candidate list that scopes the following slices — the proven
   2026-06-06 pattern (posture pass = slice 1, candidates scope slices 2-N).
   Slice 2 resolves **#350** (the one already-shaped quality improvement:
   create-skill at-cap checklist line + near-cap >=195/200 surface-preflight
   warning with tests; carrier `Closes #350` staged). Slices 3..N implement
   the top-ranked candidates from slice 1, one bounded slice with per-slice
   closeout each, until the closeout reserve.
2. **DEFERRED-PROOF CONSUMPTION (cheap, opportunistic).** The named deferred
   proof from the completed goal: the first scheduled `mutation-tests.yml`
   run whose headSha is 768ded84 or later (~3h cron; two slots should fire
   inside the window). Check opportunistically at slice boundaries; record
   run id + verdict.
3. **PUSH + RELEASE LANE (final slice, operator-pre-authorized).** Push the
   accumulated commits (763653c7 `Closes #349` + goal closeouts + this
   goal's quality slices and any staged carriers), verify the post-push
   `quality-core.yml` run is green, verify #349 (and #350 if its carrier
   landed) flip CLOSED via `issue_tool.py verify-closeout`, then cut the
   release through the release skill's publish helper (bump level decided
   from the actual delta per version policy) and prove the installed
   surface with the LIVE local probe (installed plugin version == new tag;
   installed checkout SHA == new pushed HEAD — the carried lesson). The
   new-HEAD scheduled mutation run is the NEXT goal's named deferred proof.

## Non-Goals

- Do NOT take on **#184** (product success metrics) — SEVENTH consecutive
  deliberate exclusion; product-level, needs an operator `ideation` session
  shaped into its own goal.
- Do NOT push mid-goal — exactly ONE push + ONE release lane at the end;
  quality slices accumulate locally with per-slice closeout.
- Do NOT manually close #349/#350 — #349 closes via the already-staged
  763653c7 carrier riding the final push; #350 closes via its slice carrier
  if the slice completes (validated with `validate-closeout-draft`), else it
  stays open for the next queue.
- Do NOT take on broad refactors the slice-1 posture pass did not rank
  (e.g. the nose-clone resolve_adapter families are known deliberate
  portability boilerplate — not a candidate unless slice 1 ranks them with
  new evidence).
- Do NOT take on ceal-side `hotl` consumption — the consuming repo's
  follow-up, named in #348.
- Do NOT cut a release on a red post-push quality-core run — repair
  repo-locally, stop, and report instead (no second push, no forced lane).

## Boundaries

- **Quality slices (main job).** Route via `quality`; slice 1 refreshes
  `charness-artifacts/quality/latest.md` (gates run, lenses, runtime
  signals, prioritized candidates) with one bounded fresh-eye reviewer per
  its contract. Implementation slices follow implementation-discipline:
  sync-before-verify, mirrors byte-synced, critique BEFORE the locked
  producer (carried contract line), changed-line producer/consumer at the
  bundle boundary when mutation-pool files change. Frozen reviewed skill
  surfaces get the carried triangulation (prose-pin scan + dogfood
  observed_evidence + exact-phrase grep) BEFORE any trim. Consult
  `plan_cautilus_proof.py` before any eval thought; refuse when
  `next_action: "none"` — deterministic gates own closeout otherwise.
- **#350 slice.** Surfaces: `skills/public/create-skill/SKILL.md` (+ mirror;
  it is review-required — check its headroom and pinned prose FIRST with the
  same triangulation; if at-cap, apply the deliberate-trim discipline #349
  just exercised), `scripts/check_skill_surface_preflight.py` + its tests
  for the non-blocking near-cap warning. Additive-guard default; any
  `improve` claim needs behavior proof. Carrier `Closes #350` staged via
  `validate-closeout-draft` (shape-describer-first: consult
  `describe_closeout_draft_shape.py` BEFORE drafting — this session's
  carried lesson).
- **Final push + release lane.** Order: bundle gates green (broad
  `run-quality.sh --read-only` + producer/consumer when eligible) -> push ->
  post-push quality-core green (triage per the CI-only failure-recovery
  protocol on failure; red run = NO release, stop-and-report) ->
  verify-closeout #349 (+#350 if staged) -> release publish helper ->
  live installed-surface probe -> record run ids/verdicts in the slice log.
  Release closeout runs the release skill's own fresh-eye critique gate.
- **External side-effect scope:** exactly ONE push and ONE release publish,
  both at the final lane, PRE-AUTHORIZED by the operator's shaping directive
  quoted in `## Goal` (the operator is asleep during execution — that
  directive is the standing authorization; no further confirmation gate
  exists in-window). All other remote access is read-only `gh` plus
  post-publication `verify-closeout` reads and the `issue` skill's
  off-goal filings.
- Discuss before activation: RESOLVED — (a) `production_or_live_proof` /
  push+release autonomy: explicitly operator-ordered in the shaping message
  ("...그다음 푸시 릴리즈") for execution during the sleep window; the lane
  is single, terminal, and gated on green CI with a no-release-on-red stop
  rule. (b) `issue_close_or_split`: #349 via the already-staged carrier;
  #350 close-INTENDED only if its slice completes and validates; never a
  manual close. (c) `broad_bundle_scope`: "품질 개선" is open-ended by
  design — bounded by the slice-1 ranked candidate list, per-slice closeout,
  the 40m reserve, and the Non-Goals fence (no unranked refactors).
  (d) release bump level: decided at lane time from the actual
  origin/main..HEAD delta per the release skill's version policy.
  Re-open this item instead of activating if any of these calls is wrong.

## User Acceptance

What the user can do to verify completion directly (after waking).

- **Quality main job:** `charness-artifacts/quality/latest.md` is refreshed
  (dated 2026-06-10/11, current-version scope) with a prioritized candidate
  list; the slice log shows one closed slice per implemented candidate, each
  with gates green and fresh-eye critique verdicts; `git log` shows the
  slice commits.
- **#350:** `gh issue view 350` shows CLOSED after the push (or the slice
  log records why it stayed open); the near-cap warning fires on a >=195
  skill and the create-skill checklist names the at-cap outcome.
- **Push + release:** `git log origin/main` contains the pushed commits;
  `gh issue view 349` shows CLOSED with 763653c7 as closer; a new release
  tag exists with a green post-push quality-core run id in the slice log;
  `git -C ~/.agents/src/charness rev-parse HEAD` == pushed HEAD and the
  installed plugin version == the new tag.
- **Deferred proof:** the slice log names a green scheduled
  `mutation-tests.yml` run id with headSha at/after 768ded84, or the named
  deferred line with the pre-resolved fallback.

## Agent Verification Plan

### Low-Cost Checks

- Per-commit: the touched validators/tests; `check_skill_surface_preflight`
  headroom BEFORE prose on any reviewed skill; mirror byte-sync;
  `validate_skills` + ergonomics + dogfood registries on skill edits;
  `describe_closeout_draft_shape.py` BEFORE carrier drafts;
  `validate-closeout-draft` for every staged carrier.
- Opportunistic `gh run list --workflow mutation-tests.yml` at slice
  boundaries for the 768ded84+ deferred proof.

### High-Confidence Checks

- Fresh-eye slice critique BEFORE the locked producer for every
  implementation slice (carried ordering contract); quality posture pass
  uses its own bounded fresh-eye reviewer.
- Bundle boundary (pre-push): broad `run-quality.sh --read-only` + locked
  changed-line producer + consumer over the full origin/main..HEAD range
  when any mutation-pool file changed (confirm via the consumer's
  eligibility verdict, never assumption).
- Fresh-eye goal-closeout disposition review at the end.

### External Or Live Proof

- Post-push quality-core run verdict on the new HEAD (in-window; release
  gates on it).
- Release publish + LIVE installed-surface probe (installed version == new
  tag; checkout SHA == new pushed HEAD).
- verify-closeout reads for #349 (+#350 if staged) after the push.
- New-HEAD scheduled mutation coverage: the NEXT goal's named deferred
  proof (cron may not fire again in-window after a late push — pre-resolved
  fallback carried forward).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Quality posture refresh on current main -> prioritized bounded candidate list | latest.md is 15 releases stale; the operator made quality the main job — ranking before implementing prevents unranked-refactor drift over 6h | refreshed quality/latest.md, gates summary, ranked candidates scoping slices 3..N | done |
| 2 | #350: create-skill at-cap checklist line + near-cap preflight warning + tests, carrier staged | already-shaped, bounded, directly a quality-gate improvement; closes the recurrence loop #349 opened | gates green, tests for the warning, draft_verified carrier `Closes #350` | done |
| 3..N | Top-ranked slice-1 candidates, one bounded slice each with per-slice closeout, until reserve | continue_next_improvement inside the operator's quality mandate | per-slice: gates green, critique verdict, commit | planned |
| final | Push -> post-push quality-core green -> verify-closeout #349(/#350) -> release cut -> live probe | operator-pre-authorized terminal lane ("그다음 푸시 릴리즈"); closes the staged-carrier loop | run ids + verdicts, CLOSED payloads, new tag, live-probe match | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id`
recommendation engine) — never a hard-coded phase-to-skill list here.
`achieve` owns this slot and the floors below; `find-skills` owns *which*
skill answers a boundary. Fill during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current
  phase or boundary, and record the route it returns. At completion,
  recorded implementation / debug / quality / issue work needs this
  `Routing:` evidence or a `Routing: n/a — <reason>` opt-out.
- Routing: slice 1 — find-skills `--recommend-for-task` (read-only, posture
  refresh task text) returned no overriding support/tool route; goal-mandated
  `quality` skill confirmed as the slice-1..N main-job route.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing
  at the gathered asset, or write `Gather: n/a — <reason>` when no external
  context applies.
- **Release step** — this run touches a release surface by design; add a
  `Release:` line pointing at the release proof (publish-helper record +
  live-probe evidence).
- **Issue closeout step** — add an `Issue closeout:` line naming the
  close-intended issue numbers, carrier, and `validate-closeout-draft` /
  `verify-closeout` proof. If a tracked issue appears in `## Context
  Sources` as context only, use `Issue closeout: n/a — <reason>`.

## Slice Log

- **Activation (2026-06-11T06:31+09:00).** Goal activated; fresh-eye plan
  critique (bounded subagent, read-only) verdict: **proceed-with-adjustments**,
  no blockers. Folded adjustments: (1) deferred mutation proof consumed at
  activation instead of opportunistically; (2) #350 slice must keep the four
  preflight-output consumers green (`check_artifact_surface_preflight.py`,
  `staged_commit_gate_plan.py`, `slice_closeout_advisories.py`,
  `skill_issue_anchor_scan.py`) — no exit-code or JSON-shape break;
  (3) bundle-boundary producer/consumer eligibility is near-certain (mutants
  pool contains create-skill SKILL.md and scripts/ surfaces) — budget the
  locked producer before the push; (4) activation edit rides the first slice
  commit. Over-worry (not folded): create-skill at-cap fallback (188/200,
  one-line addition cannot hit cap); push-autonomy contradiction (directive
  supersedes older handoff line).
- **Deferred proof CONSUMED (activation).** Scheduled `mutation-tests.yml`
  on headSha 768ded84 fired three times pre-activation: run **27279937136**
  (2026-06-10T13:32Z, **failure** — overall score PASS 88.2% vs 80%, but the
  changed-line coverage/selection blocking signal FAILED; auto-filed #351),
  then runs **27290330577** (16:28Z, success) and **27299766603** (19:10Z,
  success) on the SAME SHA; #351 auto-closed 17:03Z. Disposition (CORRECTED
  during slice 1): the red run's blocking signal was REAL and by-design —
  the fd3c2c6c..768ded84 range changed 10 eligible Python files vs the
  5-file workload cap, so eligible files were necessarily budget-dropped.
  The two "green" reruns were VACUOUS: scheduled base = previous completed
  run's headSha, so same-SHA reruns diff base==head (empty) and auto-closed
  #351 without the backlog ever being scheduled-lane mutation-tested.
  Mitigation: the local pre-push changed-line gate is the primary lane and
  covered those commits before the push. Scheduled-lane semantics (vacuous
  green auto-close; base advances past budget-dropped backlog) fed to
  slice 1 as candidate C4 (renamed C3 in the posture artifact).
- **Slice 1 DONE (2026-06-11 ~07:1x+09:00).** Posture refreshed:
  `charness-artifacts/quality/latest.md` re-derived at v0.39.0+3 staged
  commits (prior archived to `history/2026-06-06-quality-review.md`).
  Broad gates: initially 71/2 (`validate-handoff-artifact` empty Discuss —
  introduced by bc70d76a AFTER the prior session's final gate run;
  `validate-retro-lesson-index` stale) — both repaired, re-run **73/0**.
  NEW BUG found+reverted: `quality_bootstrap_lib.py` allowlist rewrite
  silently dropped live `standing_doc_provenance` +
  `changed_line_mutation_gate` adapter blocks (= candidate C2). Ranked
  candidates scoping slices 3..5: C2 bootstrap data-loss fix; C3 scheduled
  mutation lane base/auto-close semantics (constraints: craken-agents#127,
  #341); C4 commit-time handoff validation wiring. Fresh-eye posture
  reviewer (high-leverage, read-only): REVISE -> folded (attribution,
  47-issue noise count, vacuous-arm precision); artifact validators green
  (140 lines, consumption + closeout contract OK). Routing: quality.
- **Slice 2 DONE (#350, 2026-06-11 ~07:5x+09:00).** Both issue guards
  landed additively: create-skill Guardrails at-cap line (+1, 189/200,
  core 156/160 exactly at ratchet buffer — the real binding constraint was
  core_nonempty, not the 200 total the plan critique sized); non-blocking
  `near_cap` warning (>=195) in `check_skill_surface_preflight.py --path`
  with 3 boundary tests (195 fires/194 absent/200 coexists-with-blocked).
  Live probe: hitl 196/200 warns, exit 0. Consumers green (136+10+21
  tests), broad gate 73/0, mirrors byte-synced. Fresh-eye slice critique:
  **SHIP** (3 nits recorded as F2/F3 dispositions in the critique
  artifact). Carrier `Closes #350` **draft_verified** (direct-commit,
  feature class, shape-describer consulted first); resolution critique
  checked in at
  charness-artifacts/critique/2026-06-11-issue-350-resolution-critique.md.
  Routing: quality (goal-mandated) -> impl-shaped slice.
- **Slice 3 DONE (C2, 2026-06-11 ~08:3x+09:00).** Unknown top-level
  adapter fields now round-trip through `quality_bootstrap_lib.py`
  (`_raw_adapter` capture -> `_unknown_fields` in build -> rendered
  verbatim after policy items; statuses `preserved`). Restores the no-op
  path: live probe on this repo = `adapter_status: unchanged`, both
  previously-dropped blocks preserved, file untouched. 2 regression tests
  (no-op byte-identical; rewrite survival), suite 15/15, broad gate 73/0,
  lib mirror byte-synced. Sibling scan clean (init/seed helpers refuse
  without --force; markdown-preview preserves existing). Fresh-eye
  critique: **SHIP-WITH-NITS** — 3 latent pre-existing renderer nits
  recorded in Off-Goal Findings for closeout disposition. Scheduled
  mutation run 27308933212 (768ded84) was in progress at the slice-2
  boundary — check at next boundary. Routing: quality -> impl-shaped
  slice.

## Context Sources

Durable references this goal was shaped from. A fresh session can
reconstruct the originating context by following them in order.

1. **Operator directive (this shaping session):** quality improvement as
   the main job during a ~6h sleep window, then push + release — the
   standing authorization for the final lane.
2. **The completed prior goal + its retro:**
   `charness-artifacts/goals/2026-06-10-postpush-verify-346-348-closed-349-hitl-boundary.md`
   (Final Verification non-claims: the 768ded84+ scheduled mutation run is
   this goal's deferred-proof input; #349 closes on this push) and
   `charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md`
   (shape-describer-first carrier drafting; triangulation-before-trim on
   frozen surfaces; the zsh `===` trap).
3. **Open issues:** corca-ai/charness#350 (slice 2; filed by the prior
   goal's resolution critique), #349 (carrier staged — final lane verifies
   CLOSED), #184 (excluded, seventh time).
4. **Handoff:** `docs/handoff.md` (Next Session: push lane + #349 CLOSED
   verification, #350 candidate, deferred mutation proof, #184 exclusion).
5. **Recent lessons:** `charness-artifacts/retro/recent-lessons.md`
   (release-helper persistence trap; at-cap fold-then-revert lineage;
   verify-closeout arg-sketch trap — now twice; describe-shape lesson).
6. **Quality posture:** `charness-artifacts/quality/latest.md` (2026-06-06,
   v0.24.1 — STALE; its candidate-list-scopes-slices pattern is reused, its
   content is re-derived by slice 1).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value,
and rejected-alternatives reason.

- **What is the main job (operator: quality improvement during ~6h sleep,
  then push + release).** Family: {quality main job + terminal lane; queue
  cleanup (#350 only) + idle; #184; defer everything to wake-up}. Chosen:
  **quality main job scoped by a fresh posture pass, #350 as the first
  implementation slice, terminal push + release lane** — matches the
  directive verbatim, reuses the proven posture-pass-scopes-slices pattern,
  and closes both open quality loops (#349 carrier, #350). Rejected: #184
  (seventh exclusion — operator ideation required); idling (the directive
  names quality as the job).
- **Push/release placement.** Family: {terminal single lane; push early +
  release late; multiple pushes}. Chosen: **terminal single lane** — one
  external side-effect window, gated on green CI, no-release-on-red;
  mid-goal pushes would multiply the lanes the operator authorized once.
- **Quality scope control.** Family: {free-form improvement; ranked
  candidate list from a posture pass; fixed pre-named slices}. Chosen:
  **ranked candidate list** — the artifact is 15 releases stale, so
  pre-naming slices now would anchor on stale evidence; free-form risks
  unranked-refactor drift over 6h.
- **#350 claim shape.** Family: {additive guard; improve}. Chosen:
  **additive-guard default, improve only with behavior proof** — the
  checklist line and warning are additive; the cautilus planner owns
  whether any eval is due.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised
but not folded, and reviewer provenance. A fresh-eye plan critique runs at
activation per the verification cadence.

- **Provenance:** self-critique by the shaping session.
- **Autonomous push/release while the operator sleeps could overreach.**
  Folded: the directive is quoted as the standing authorization; the lane
  is single and terminal; release gates on a green post-push quality-core
  run with an explicit no-release-on-red stop-and-report rule; no mid-goal
  pushes is in Non-Goals.
- **Open-ended "quality improvement" could sprawl across 6h.** Folded:
  slice 1 must produce a ranked bounded candidate list before any
  implementation slice beyond #350; Non-Goals fence unranked refactors and
  the known nose-clone boilerplate; per-slice closeout + 40m reserve.
- **#350 touches a review-required skill that may itself be at-cap.**
  Folded: headroom + triangulation FIRST; the #349 deliberate-trim
  discipline is the named fallback; stop-and-report if the edit needs
  load-bearing prose.
- **A late push leaves no in-window scheduled mutation slot for the new
  HEAD.** Folded: pre-resolved fallback carried forward — the new-HEAD
  mutation run is the NEXT goal's named deferred proof; the 768ded84+ run
  is expected in-window for the CURRENT origin/main.
- **Over-worry (raised, not folded):** that the posture pass duplicates
  slice gates — the posture pass is the ranking instrument, not a gate
  rerun; its fresh-eye reviewer is scoped by the quality skill's own
  contract.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Slice-3 reviewer nits (latent, pre-existing, adapter_lib renderer):
  (a) `_yaml_scalar` does not escape `\n` — invalid YAML if a value ever
  contains a newline (unreachable today: repo `load_yaml` cannot produce
  multiline strings); (b) unsupported YAML constructs (block scalars,
  inline comments) inside unknown blocks normalize lossily on a LEGITIMATE
  rewrite (no-op path is safe — that is the live-repo case); (c) known
  falsy explicit fields (`spec_pytest_reference_format: ""`,
  `preset_version: null`) drop on rewrite while statuses say preserved.
  Disposition at goal closeout (file one renderer-hygiene issue or defer).

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
