# Achieve Goal: #322 roll out the advisory-interpretation contract to remaining inference-layer surfaces

Status: draft
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-322-advisory-interpretation-rollout.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command. It was shaped by the
`2026-06-07-324-325-322-handoff-orchestrator` orchestrator (B4) as a child
`/achieve` goal; the orchestrator does not execute it.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-07-322-advisory-interpretation-rollout.md`.
- Mode: spec-light rollout — replicate the `nose` pilot's 4-field
  `interpretation` self-declaration across the remaining inference-layer
  surfaces; promote to a `spec` only if a shared schema/validator emerges.
- Timebox: until objective complete (no hard wall-clock cap); re-pick the next
  surface at each boundary.
- Activation time: (set at `/goal` activation)
- Closeout reserve: ~15% for final verification + bounded critique + retro.
- Done-early policy: continue_next_improvement
- Verification cadence: cheap deterministic checks at commit boundaries; targeted
  `pytest` per surface (the self-declaration shape + the consumer-requirement
  reference); broad `pytest` + one bounded fresh-eye `critique` at the bundle
  boundary (does any declaration attach to a verified fact? is any surface noisy?).
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Roll out the existing **advisory-interpretation contract**
(`skills/shared/references/advisory-interpretation-contract.md`, piloted on the
`nose` clone advisory) to the remaining inference-layer surfaces. For each
surface: add the 4-field `interpretation` self-declaration (measures /
proxy-for / blind-spots / interpretation-question) to the inventory output, and
add the consumer-must-answer requirement to the consuming skill's reference.
Inference-layer only — verified facts (green gates, exact counts, AST results)
stay trusted and untouched. Stage `Close #322`.

Remaining surfaces (from the issue body):

1. `inventory_skill_ergonomics.py` ergonomics heuristics (`subcheck_counts`,
   `host_surface_reference` advisory).
2. `inventory_standing_test_economics.py` test-economics trend
   (`test_file_count` / `nested_cli_file_count` growth).
3. `inventory_lint_ignores.py` suppression-pressure trend.
4. `check_python_lengths.py` advisory warn-band (length smell).
5. Recommendation rankings: `find-skills` recommendation engine and `quality`
   `Recommended Next Gates`.
6. Runtime/coverage trend (`render_runtime_summary.py` hot spots; coverage brush).

## Non-Goals

- **Attaching self-declaration to verified facts** — rollout is inference-layer
  only; green gates, exact counts, and AST results stay trusted.
- **A repeated distrust banner** — keep each surface low-noise (positive-form
  blind-spot declaration), not a banner that trains the reader to ignore it.
- **Re-piloting `nose`** — the `nose` clone advisory already emits the
  declaration; it is the template, not a rollout target (only touch it if the
  shared schema work requires aligning it).
- **Pushing/tagging or publishing** — `Close #322` is staged; the issue stays
  OPEN until the maintainer's push.
- **Forcing a shared schema/validator now** — promote to a `spec` only if the
  rollout grows a genuine shared schema need; otherwise keep it per-surface.

## Boundaries

- **Inference-layer only.** A surface qualifies only if its number is a *sensor
  reading* (proxy / ranking / heuristic / trend), not a verified fact. Do not
  attach the declaration to deterministic verified outputs.
- **Low-noise, positive-form.** Each declaration is a terse 4-field block, not a
  distrust banner; the consuming skill reference carries the consumer-must-answer
  requirement once, not per-invocation.
- **Consumer requirement is paired.** Every surface that gains a self-declaration
  must also gain the consumer-must-answer line in its consuming skill reference —
  a declaration with no consumer requirement is half the contract.
- **Spec-light by default.** Promote to a `spec` (shared self-declaration
  schema/validator) only if the rollout grows beyond a handful of surfaces or the
  per-surface duplication becomes the real cost; record the decision either way.
- `mutate → sync → verify → publish` are hard phase barriers; sync generated /
  plugin / export surfaces before validators.
- Bounded fresh-eye reviewers run in the shared parent worktree, inspecting
  prior versions read-only (`git show <ref>:<path>`), never mutating the index.

## User Acceptance

What the user can do to verify completion directly:

- Each named inference-layer surface emits the 4-field `interpretation`
  self-declaration (measures / proxy-for / blind-spots / interpretation-question)
  in its inventory output, mirroring the `nose` pilot.
- Each consuming skill reference carries the consumer-must-answer requirement
  for its surface.
- No declaration is attached to a verified fact (green gates, exact counts, AST
  results stay untouched) — spot-check a deterministic surface and confirm it is
  unchanged.
- Each surface stays low-noise (a terse positive-form block, not a banner).
- `Close #322` staged; `gh issue view 322` still OPEN. If a shared
  schema/validator emerged, a `spec` exists; if not, the explicit
  keep-per-surface decision is recorded.

## Agent Verification Plan

### Low-Cost Checks

- At commit boundaries: `run_slice_closeout.py` deterministic aggregate.
- Targeted `pytest` per surface: the inventory output carries the 4-field
  declaration with non-empty values; the consuming reference carries the
  consumer-must-answer line.

### High-Confidence Checks

- Broad `pytest` at the bundle boundary.
- One bounded fresh-eye `critique` for the rollout: does any declaration attach
  to a verified fact (the cardinal error)? is any surface noisy? is any
  consumer requirement missing its pair?
- Changed-line mutation-coverage gate where source changed (consumer over
  `base→worktree`, never `--head-sha HEAD`).
- A cheap test-duplication pressure sample whenever a slice adds/expands tests
  (the per-surface tests will be near-identical — watch for a shared helper
  opportunity, which is also the shared-schema promotion signal).

### External Or Live Proof

- **Skipped (named so closeout cannot silently claim them):** no push/tag/GitHub
  release by the agent (maintainer's); no provider/live proof.

## Slice Plan

Dynamic — re-pick the next surface at each boundary. Each surface is one small
slice (declaration + consumer requirement + test).

| Slice | Surface | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | `inventory_skill_ergonomics.py` | richest inference output; sets the pattern | 4-field declaration + ergonomics consumer requirement + test | planned |
| S2 | `inventory_standing_test_economics.py` | trend signal | declaration + consumer requirement + test | planned |
| S3 | `inventory_lint_ignores.py` | suppression-pressure trend | declaration + consumer requirement + test | planned |
| S4 | `check_python_lengths.py` warn-band | advisory length smell | declaration on the warn-band advisory only (not the hard gate) + test | planned |
| S5 | recommendation rankings (`find-skills`, `quality` Recommended Next Gates) | rankings are proxies | declaration on the recommendation/ranking output + consumer requirement | planned |
| S6 | runtime/coverage trend | hot spots / coverage brush | declaration + consumer requirement + test | planned |
| S7 | schema decision + `Close #322` | converge | shared-schema-or-keep-per-surface decision recorded; closeout staged | planned |

## Coordination Cues

Phase-appropriate routing is deferred to `find-skills`
(`--recommend-for-task` / `--recommendation-role --next-skill-id`). Expected
owners to confirm at runtime: `impl` (the per-surface rollout), `spec` (only if a
shared schema emerges), `quality` (verification cadence + the inference-layer
surfaces it owns), `issue` (#322 closeout + any split). `debug: n/a — #322 is a
contract rollout, not a behavior defect.` Record actual routes at completion.

- **Routing** — query `find-skills` per phase; record `Routing:` evidence.
- **Gather step** — `Gather: n/a — issue body via gh; no external source.`
- **Release step** — `Release: n/a — no release surface (inference-layer prose +
  inventory output only).`
- **Issue closeout step** — `Issue closeout:` names #322 (carrier = direct
  commit), close-keyword state, and the `validate-closeout-draft` /
  `verify-closeout` proof.

## Discuss Before Activation

Discuss before activation: RESOLVED via the orchestrator's mid-run stop-and-ask
this session. Consequential defaults and their resolutions:

- **#322 issue close / split** — **RESOLVED**: `Close #322` is staged (issue
  stays OPEN until maintainer push); split into a tracked sub-issue only if scope
  clearly grows (operator: "split if scope grows") — e.g. if a shared
  schema/validator becomes its own `spec`-worthy unit.
- **Spec promotion** — **RESOLVED / deferred to S7 by design**: spec-light by
  default; promote to a shared schema/validator `spec` only if the rollout grows
  beyond a handful of surfaces. Recorded either way.

## Slice Log

## Context Sources

A fresh session can reconstruct the originating context by following these in
order:

- **GitHub issue #322** — full body with the structural pattern, the pilot, and
  the list of remaining inference-layer surfaces.
- **Contract + pilot:** `skills/shared/references/advisory-interpretation-contract.md`,
  `skills/public/quality/scripts/inventory_nose_clones.py` (the pilot emitter),
  `skills/public/quality/references/automation-promotion.md` (the consumer
  requirement), `charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md`.
- **Generalizes:** `automation-promotion.md` ("do not repeat an automated
  finding without repository-level interpretation") and the
  `agent-assessment-invariant.md` from passive prohibition into an active
  requirement; the fresh-eye subagent review remains the independent backstop.
- **Pilot origin:** the `2026-06-06-quality-scan-closeout-discipline` achieve
  goal (slice 5).
- **Orchestrator parent:** `charness-artifacts/goals/2026-06-07-324-325-322-handoff-orchestrator.md` (B4).

## Interview Decisions

For each Before-phase question: family considered, chosen value, rejected
reason, and the anti-anchoring axis result.

1. **Rollout shape** — family: {per-surface inline declaration now, build a
   shared schema/validator first}. **Chosen:** per-surface inline (spec-light),
   matching the `nose` pilot; promote to a shared schema only if duplication
   becomes the real cost. Rejected *schema-first* — over-builds before the
   rollout reveals the genuine shared shape. `axis: abstraction-timing` — let the
   shared schema emerge from N surfaces, not be guessed at surface 1.
2. **Surface eligibility** — family: {all advisory outputs, strictly
   sensor-reading proxies/rankings/trends}. **Chosen:** strictly inference-layer
   (sensor readings); verified facts stay trusted. Rejected *all advisory* —
   attaching a distrust declaration to a verified fact is the cardinal error the
   contract forbids. `single-point: the inference-vs-verified boundary.`

## Plan Critique Findings

Reviewer provenance: to be run as a bounded fresh-eye `critique` at the bundle
boundary during pursuit. Seeded concerns to fold:

- **Verified-fact contamination** — the cardinal error. Bind a spot-check that a
  deterministic surface stays untouched; the critique explicitly hunts for any
  declaration on a verified output.
- **Noise accumulation** — N surfaces each adding a block risks banner fatigue;
  keep each terse and positive-form, and watch whether the consumer requirement
  belongs once-per-reference rather than per-output.
- **Half-contract risk** — a self-declaration with no paired consumer
  requirement is incomplete; the per-surface test asserts BOTH halves.

## Off-Goal Findings

(None yet — file off-goal findings via `issue`, recording only the reference and
reason here. Per the operator decision, split #322 into a tracked sub-issue if a
shared schema/validator becomes its own `spec`-worthy unit.)

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>` at the After-phase. The complete gate
rejects a literal `TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

(Final results recorded at closeout; the user-runnable checks are in
`## User Acceptance`.) At closeout this section names the exact commands the user
can run, what is staged versus pushed, and which proof levels the agent did not
run (push/tag, GitHub release, provider/live).

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
