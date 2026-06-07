# Achieve Goal: #322 roll out the advisory-interpretation contract to remaining inference-layer surfaces

Status: draft
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-322-advisory-interpretation-rollout.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command. It was shaped by the
`2026-06-07-324-325-322-handoff-orchestrator` orchestrator (B4) as a child
`/achieve` goal; the orchestrator does not execute it.

## Active Operating Frame

- Current slice: COMPLETE — S1–S7 done; `Close #322` staged (issue OPEN until
  maintainer push). Bundle verified (broad pytest 2511 passed / 4 skipped),
  bounded fresh-eye critique returned no blockers, schema decision recorded
  (keep-per-surface).
- Next action: maintainer review + push of the staged closeout commit.
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
| S1 | `inventory_skill_ergonomics.py` | richest inference output; sets the pattern | 4-field declaration + ergonomics consumer requirement + test | DONE |
| S2 | `inventory_standing_test_economics.py` | trend signal | declaration + consumer requirement + test | DONE |
| S3 | `inventory_lint_ignores.py` | suppression-pressure trend | declaration + consumer requirement + test | DONE |
| S4 | `check_python_lengths.py` warn-band | advisory length smell | declaration on the warn-band advisory only (not the hard gate) + test | DONE |
| S5 | recommendation rankings (`find-skills`, `quality` Recommended Next Gates) | rankings are proxies | declaration on the recommendation/ranking output + consumer requirement | DONE |
| S6 | runtime/coverage trend | hot spots / coverage brush | declaration + consumer requirement + test | DONE (runtime hot spots; coverage brush noted as deferred) |
| S7 | schema decision + `Close #322` | converge | shared-schema-or-keep-per-surface decision recorded; closeout staged | DONE |

## Slice Log

- **S1 ergonomics** — `INTERPRETATION` in `inventory_skill_ergonomics.py`
  (payload + human, gated `if skills`); consumer line in `automation-promotion.md`;
  test in `test_quality_skill_ergonomics.py`. `Routing: impl`.
- **S2 test-economics** — declaration in the emitter script
  `inventory_standing_test_economics.py` (relocated from the lib at S7 to clear
  the length warn band); consumer line in `automation-promotion.md`; test in
  `test_standing_test_economics.py`.
- **S3 lint-ignores** — `INTERPRETATION` in `lint_ignore_inventory_lib.py`
  (repo-root `scripts/`), printed by `inventory_lint_ignores.py`; consumer line in
  `automation-promotion.md`; test in `test_quality_lint_ignores.py`.
- **S4 length warn-band** — `INTERPRETATION` in `check_python_lengths.py` on the
  warn-band + `--headroom` near-limit ONLY (`ADVISORY:`-prefixed so the standing
  gate surfaces it); cardinal-error guards (no declaration on over-limit / clean
  pass / function-length / exact headroom). Consumer line in
  `automation-promotion.md`; new `test_python_length_interpretation.py`.
- **S5 recommendation rankings** — find-skills `recommendation_interpretation` in
  `list_capabilities_lib.py` (gated on `has_recommendations`, never on the
  verified inventory), surfaced via `list_capabilities.py`; consumer in
  `discovery-order.md`. Quality `Recommended Next Gates` ordering (agent-authored
  prose) declared inference-layer in `gate-classification.md`. Consumer line in
  `automation-promotion.md`; tests in `test_find_skills_task_recommendations.py`
  and `test_quality_skill_docs.py`.
- **S6 runtime hot spots** — `INTERPRETATION` in `render_runtime_summary.py`
  (markdown bullet + JSON, gated on hot spots existing); consumer line in
  `automation-promotion.md`; test in `test_runtime_budget_gate.py`. Coverage
  "brush" beyond runtime hot spots left as a deferred surface (not separately
  instrumented).
- **S7 converge** — schema decision recorded (keep-per-surface; see
  `## Discuss Before Activation` resolution below); bundle verified; bounded
  fresh-eye critique (no blockers); `Close #322` staged.

## Coordination Cues

Phase-appropriate routing is deferred to `find-skills`
(`--recommend-for-task` / `--recommendation-role --next-skill-id`). Expected
owners to confirm at runtime: `impl` (the per-surface rollout), `spec` (only if a
shared schema emerges), `quality` (verification cadence + the inference-layer
surfaces it owns), `issue` (#322 closeout + any split). `debug: n/a — #322 is a
contract rollout, not a behavior defect.` Record actual routes at completion.

- **Routing** — `find-skills --recommend-for-task` routed the per-surface rollout
  to `impl` (public skill); verification routed through `quality`'s inference-layer
  surfaces; closeout via `issue` tooling. `Routing: find-skills -> impl` (recorded).
- **Gather step** — `Gather: n/a — issue #322 body via gh; no external source.`
- **Release step** — `Release: n/a — no release surface (inference-layer prose +
  inventory output only; no version bump/tag/publish).`
- **Issue closeout step** — `Issue closeout:` #322, carrier = direct-commit, close
  keyword `Close #322` staged in
  `charness-artifacts/issue/2026-06-07-issue-322-closeout-commit-message.md`;
  classification feature; ledger + `Critique #322` present;
  `issue_validate_closeout_draft.py` rehearsal green; `gh issue view 322` = OPEN
  (stays open until maintainer push).

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

### Spec promotion — S7 resolution (recorded)

**Keep per-surface (spec-light); no shared schema/validator forced.** Across the
six rolled-out surfaces plus the pilot, the 4-field declaration is irreducibly
per-surface content (the value of the contract), and the per-kind render wording
is deliberate honest framing — not duplication to eliminate. The only genuinely
near-identical duplication is the test-assertion shape (small, clear). A shared
schema would add indirection without removing the irreducible per-surface
content, so the rollout did not grow a genuine shared-schema need. Deferred
capability (not built, surfaced to the operator): a meta-validator that
enumerates the inference-layer surfaces and asserts each emits the 4-field
declaration AND a paired consumer line — a regression backstop beyond #322's
scope; file as a sub-issue only if the operator wants it tracked.

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

Reviewer provenance: bounded fresh-eye `critique` subagent (independent context,
read-only in the shared parent worktree) run at the bundle boundary. Result:
`charness-artifacts/critique/2026-06-07-issue-322-advisory-interpretation-rollout.md`.
**No blockers, no should-fix; one dispositioned NIT.** Seeded concerns, resolved:

- **Verified-fact contamination (cardinal error)** — none found. The two
  highest-risk surfaces (length, find-skills) each have a verified-fact variant
  adjacent to the inference-layer one; the declaration is gated (warn-band-only;
  ranking-produced-only; hot-spots-only) and cardinal-error negative-assertion
  tests guard the over-limit / clean-pass / function-length / plain-inventory /
  empty-report facts.
- **Noise accumulation** — each declaration is terse positive-form; the consumer
  requirement lives once-per-reference (the per-surface list in
  `automation-promotion.md`, plus `discovery-order.md` and `gate-classification.md`),
  not per-invocation.
- **Half-contract risk** — none; every surface's test asserts BOTH halves.
- **NIT (dispositioned, kept):** lint-ignores and test-economics emit the human
  declaration on every successful on-demand run (matching the `nose` pilot); not
  the cardinal error (fully inference-layer surfaces, declaration is about the
  measure). See the critique artifact for the disposition rationale.

## Off-Goal Findings

- **Meta-validator for the contract (deferred capability, not filed).** A gate
  enumerating the inference-layer surfaces and asserting each emits the 4-field
  declaration AND a paired consumer line would prevent a future half-contract
  surface. Not built and not filed as a sub-issue: the keep-per-surface decision
  did not require it and scope did not clearly grow. Surfaced to the operator —
  file as a sub-issue only if they want it tracked (the goal's "split if scope
  grows" frame applies if/when it becomes spec-worthy).
- **Coverage "brush" trend** (named in S6's surface line) was not separately
  instrumented beyond `render_runtime_summary.py` runtime hot spots; recorded as
  a deferred surface, not a regression.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>` at the After-phase. The complete gate
rejects a literal `TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-07-322-advisory-interpretation-rollout.md
Host log probe: skipped: no-installed-machine-state-change: the rollout adds
  inference-layer prose + inventory-output declarations only; no install/update,
  tool-doctor, or operator-machine surface changed, so there is no host-log
  probe to run.
Disposition review: charness-artifacts/critique/2026-06-07-issue-322-advisory-interpretation-rollout.md
  (bounded fresh-eye critique — the dispositioned NIT and the deferred
  meta-validator capability are recorded there and in `## Off-Goal Findings`).

## User Verification Instructions

Staged (committed locally, NOT pushed): the rollout + `Close #322` closeout
commit. `gh issue view 322` is still OPEN; it auto-closes only on the maintainer's
push/merge. Proof levels the agent did NOT run: push/tag, GitHub release, any
provider/live proof.

Commands the user can run to verify directly:

- Declarations present (spot-check a few surfaces):
  - `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . | grep INTERPRETATION`
  - `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . | grep INTERPRETATION`
  - `python3 skills/public/quality/scripts/inventory_lint_ignores.py --repo-root . | grep INTERPRETATION`
  - `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "hitl review" --summary | grep recommendation_interpretation`
- Cardinal-error spot-check (a verified fact stays clean): a clean
  `check_python_lengths.py` pass prints `Validated ... file(s).` with NO
  `INTERPRETATION` line; an over-limit failure carries none either.
- Paired consumer requirements: `grep -n "Per-surface interpretation questions" skills/public/quality/references/automation-promotion.md`
  and the `Interpreting the recommendation ranking` section in
  `skills/public/find-skills/references/discovery-order.md`.
- Tests: `python3 -m pytest tests/quality_gates/test_python_length_interpretation.py tests/quality_gates/test_runtime_budget_gate.py tests/test_find_skills_task_recommendations.py -q`.
- `gh issue view 322` → OPEN.

## Auto-Retro

Retro dispositions (full detail in
`charness-artifacts/retro/2026-06-07-322-advisory-interpretation-rollout.md`):

1. **Meta-validator for the contract** — disposition: deferred capability,
   surfaced to operator, not built (out of #322 scope; keep-per-surface did not
   require it).
2. **Surfacing-prefix tripwire** (a check that a declaration on a STANDING
   `run-quality.sh` gate carries a surfaced prefix) — disposition: deferred (low
   frequency; the warn-band comment + this retro lesson cover it).
3. **Near-limit-append trap** (constants, not just functions, can push a file
   into the warn band) — disposition: already covered by the existing
   recent-lessons headroom lesson; no new entry needed. The rollout dogfooded the
   length contract and resolved the two warn-band hits in-flight.
4. **Boundary-bypass ratchet block (biggest rework cycle)** — a new test file used
   subprocess calls and was blocked at commit; rewritten in-process. Disposition:
   reinforces the existing #308-class authoring-preflight repeat-trap (read the
   gated-surface constraint before authoring); no new tooling — the gap was
   discipline. Recorded as the concrete instance in the retro.
5. **Commit-exit misread** (read piped `tail`'s exit, not `git commit`'s) —
   disposition: noted, no action; too minor for a standing lesson.
