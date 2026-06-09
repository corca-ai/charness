# Achieve Goal: Clear the tracked deferred queue — #341 mutation regression, #340 specdown routing, activation-preflight surface

Status: complete
Created: 2026-06-09
Activation: `/goal @charness-artifacts/goals/2026-06-09-deferred-queue-341-340-activation-preflight.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **All 3 slices COMPLETE.** Slice 1 (#341) + Slice 2 (#340) fresh-eye
  SHIP + committed; Slice 3 (activation-preflight) already landed in 01021a14 —
  added the enforcement-test gap closer. Next: **bundle boundary** then completion.
- Next action: bundle boundary — re-derive the authoritative `3a42d2e0..HEAD` range
  (slices 2+3 added changed pool files: find-skills scripts + the test), run the
  changed-line producer FIRST, then the broad `run-quality.sh --read-only` gate;
  then final verification + retro + complete flip. (achieve does not push.)
- Slice-3 finding: the goal-activation preflight surface was ALREADY DONE+committed
  (01021a14, 2026-06-08); the spec recorded it DONE, the handoff "Next Session" was
  STALE. Verified live; closed the implicit-enforcement-test gap. Stale handoff item
  recorded as an off-goal finding (correct at next handoff refresh).
- Slice-1 outcome: root-cause was the BLOCKING selection arm (per-file-cap
  structural collision with module-split file sizes), not the survived mutants
  (red herring — score was PASS). Reclassified per-file-cap drops as advisory.
  Proven GREEN end-to-end over `3a42d2e0..HEAD`. #341 auto-closes on the next green
  scheduled run — re-derive over the FINAL pushed range at the bundle boundary.
- Slice-2 outcome: shipped_support_recommendations_for_task surfaces specdown (and
  any tool shipping a support skill) via support routing even when not materialized;
  inventory unchanged; #340 closes via the slice-2 commit (Closes #340) on push.
- Bundle boundary (after slice 3, before push): re-derive the authoritative
  `3a42d2e0..HEAD` range (slices 2+3 added changed pool files), run the changed-line
  producer FIRST, then the broad gate.
- **Why this goal (chosen from the session signals):** the operator selected the
  three highest-signal deferred items — #341 (the live mutation regression on
  main, the dominant recurring class in handoff + recent-lessons), #340 (the #1
  "tracked separately" item from the just-finished module-split goal), and the
  `goal-activation-preflight-surface` follow-up named in the handoff. #184
  (product metrics, needs ideation/spec) and #338 (gather X/Twitter) were left
  for separate goals.
- Carry this session's lesson: a verbatim/large code change re-gates lines as
  *changed* — run the changed-line coverage producer FIRST at the bundle boundary
  and cover pre-existing uncovered branches in the introducing slice, so the
  producer confirms rather than discovers.
- Verification cadence: cheap deterministic checks at commit boundaries; fresh-eye
  critique + per-slice proof at slice boundaries; broad gate + changed-line
  coverage at the bundle boundary; #341's authoritative verdict is the CI
  scheduled mutation run after the fix lands.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Clear the tracked deferred queue in three independent, per-slice-closed-out
slices: (1) **#341** — root-cause the mutation regression on main (5 survived
`main` mutants + the changed-line coverage/selection blocking signal on the
authoritative range) and cover/kill them so the next scheduled mutation run is
green; (2) **#340** — make `find-skills` surface specdown via support-skill
routing (`support_skill_recommendations` / synced-support), not only as an
integration tool, so the canonical discovery path returns specdown's shipped
authoring guidance; (3) **activation-preflight-surface** — extend the
artifact-shape preflight to cover the goal `Activation:` preamble line (needs
preamble extraction) per the preflight-coverage spec. Skill-script changes are
mirror byte-synced; each slice closes out independently.

## Non-Goals

- Do NOT bundle the three slices' closeouts into one commit — per-slice closeout
  (each slice commits with its own fresh-eye critique). This is a queue-clearing
  goal, not a cross-theme proof bundle.
- Do NOT manually close #341 — it auto-closes on the next green scheduled
  mutation run after the fix lands (the mutation-workflow marker owns it); the
  goal's job is to make that run green.
- Do NOT change specdown's behavior or the specdown binary — slice 2 is
  `find-skills` routing/inventory only (surface the already-shipped skill).
- Do NOT take on #338 (gather X/Twitter) or #184 (product metrics) — different
  themes, tracked separately.
- Do NOT cut a real release/push by default — standard `achieve` no-push.

## Boundaries

- **#341 (slice 1).** The local changed-line mutation coverage producer must be
  green (`ok: true`, 0 uncovered) over the authoritative post-push range, and the
  5 survived `main` mutants killed with targeted-mutant proof (cite `path:line`,
  mutate that exact line, record the failing test, revert). The CI scheduled run
  is the authoritative verdict — do NOT manually close #341. Re-derive the
  authoritative range AFTER any push (HEAD moves), since selection/budget drops
  are range-sensitive.
- **#340 (slice 2).** Touches `skills/public/find-skills` scripts → mirror
  byte-sync. A test pins specdown in `support_skill_recommendations` (or the
  synced-support surface) for a specdown-shaped task query; behavior-preserving
  for every other capability (no inventory regression). Classify specdown's
  correct layer (support skill vs synced support vs integration) before wiring.
- **preflight (slice 3).** Artifact-shape preflight change per
  `charness-artifacts/spec/artifact-shape-preflight-coverage.md`; a test covers a
  missing/malformed `Activation:` preamble; behavior-preserving for existing
  preflight checks.
- **Public-skill + generated-surface scope.** Any skill-script change
  mirror-synced (`plugins/charness/...`), deterministic gates own closeout, no
  `#N` anchors in skill-package files.
- Discuss before activation: RESOLVED — this goal intends to close #341 and #340
  (the `issue_close_or_split` activation-discussion trigger fires legitimately).
  The consequential decisions, all operator-selected (1+2+4) and resolved: (a)
  the goal targets #341 + #340 closeout + the preflight surface; (b) it is one
  queue-clearing goal with **per-slice** closeout, not a single cross-theme proof
  bundle (re-split into three goals if a reviewer prefers); (c) #341's verdict is
  the CI scheduled mutation run, not a manual close. No live/prod proof beyond the
  scheduled CI run #341 already requires. Safe to activate; re-open if a reviewer
  disagrees with the single-goal framing.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication. For #341, the scheduled
  CI mutation run is the named external verdict lane.

## User Acceptance

What the user can do to verify completion directly.

- #341: the scheduled mutation run (or the local changed-line producer over the
  post-push range) is green — 0 survived blocking mutants, 0 uncovered changed
  lines; #341 auto-closes on that green run.
- #340: `find-skills --recommend-for-task "<specdown authoring query>"` returns
  specdown via support-skill routing, not only `tool_recommendations`.
- preflight: the artifact-shape preflight flags a goal artifact with a
  missing/malformed `Activation:` preamble.
- Each slice: the find-skills/achieve/mutation test surface passes, mirror
  byte-synced, and the per-slice fresh-eye critique attests correctness.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched file.
- The touched scripts' pytest modules; `issue_tool.py validate-closeout-draft`
  for #341/#340; `check_export_safe_imports` + `check_plugin_import_smoke` +
  mirror byte-sync for any skill-script change.
- The local changed-line mutation coverage producer over the post-push range
  (slice 1).

### High-Confidence Checks

- The full find-skills + achieve + mutation test surface green.
- Broad gate (`run-quality.sh --read-only`) at the bundle boundary; run the
  changed-line mutation coverage producer FIRST and cover any newly-gated line in
  the introducing slice. Fresh-eye `critique` at each slice boundary.

### External Or Live Proof

- #341's authoritative verdict is the **CI scheduled mutation run after push**
  (record `Release:` / CI-lane scope). Slices 2 + 3: none by default (no-push).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #341: root-cause + kill the 5 survived `main` mutants and cover the changed-line blocking-signal gap on the authoritative range; make the next scheduled mutation run green | live regression on main; the dominant recurring class (handoff + recent-lessons); this session's coverage-discipline lesson applies directly | local producer `ok: true` over the post-push range; survived mutants killed (targeted-mutant proof); per-file-cap blocking arm reclassified advisory → end-to-end GREEN over `3a42d2e0..HEAD`; fresh-eye SHIP; #341 auto-closes on the green CI run | **done** |
| 2 | #340: surface specdown via `find-skills` support-skill routing (not only integration tool); classify its correct layer first | the #1 deferred item from the module-split goal; clear repro + cost recorded in #340 | tests pin specdown in `support_skill_recommendations` (non-materialized shipped path) + weak-text guard; inventory refreshed; mirror synced; fresh-eye SHIP; closeout draft validates | **done** |
| 3 | activation-preflight-surface: extend the artifact-shape preflight to cover the goal `Activation:` preamble line (preamble extraction) | deferred follow-up named in handoff; small, bounded | **ALREADY DONE in 01021a14** (goal-activation surface + `_extract_preamble`; spec recorded DONE, handoff was stale); verified live; closed the implicit missing-Activation enforcement-test gap | **done** |

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
  - `Routing:` session-start `find-skills` bootstrap → `achieve` (goal owner) for
    the lifecycle; Slice 1 was debug-root-cause + impl + mutation-quality work
    owned by `achieve` per its coordination contract (the goal artifact is the
    slice memory surface); fresh-eye slice critique delegated to a separate agent
    context. Slice 2 routing recorded when it runs.
- **Issue closeout** —
  - **#341:** carrier = the **CI scheduled mutation run** (auto-closing
    mutation-marker, `mutation-tests.yml` "Close recovered mutation issue"); do NOT
    manual-close. Slice 1 made the next run green (per-file-cap blocking arm
    reclassified advisory; proven over `3a42d2e0..HEAD`). Dependency: the fix must be
    **pushed** before the next scheduled run; re-derive the authoritative range post-push.
  - **#340:** classification `bug`, carrier `direct-commit` (slice-2 commit `Closes
    #340`). `issue_tool.py validate-closeout-draft --number 340 --classification bug
    --carrier direct-commit` → `status: draft_verified, ok: true` (jtbd / root-cause /
    debug-artifact / siblings(decision+proof) / prevention / resolution-critique all
    satisfied). Closes on push to main.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers (#341, #340),
  carrier (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. #341 is the
  auto-closing mutation-marker case — record the CI-run dependency, do not manual-close.

Filled floor lines (completion):

- Routing: session-start `find-skills` bootstrap routed to `achieve`, which owned the goal lifecycle and deferred slice impl/debug/quality/issue-closeout boundaries to their own skills per its coordination contract; fresh-eye slice critiques delegated to separate agent contexts. find-skills owns the route — no hard-coded phase→skill map.
- Gather: n/a — every `## Context Sources` entry is an in-repo file or a local `gh issue view`; no external URL / Slack / Notion / Docs / Drive source was consumed.
- Release: n/a — no release surface touched (no version bump or install-manifest edit); the plugin mirror byte-sync is the only generated-surface change and is not a release.
- Issue closeout: #341 carrier = the CI scheduled mutation run (auto-closing mutation-marker; do NOT manual-close) — slice 1 made the next run green; #340 classification `bug`, carrier `direct-commit` (slice-2 commit `Closes #340`), `issue_tool.py validate-closeout-draft --number 340` → `draft_verified, ok: true`. Both close on push.

## Slice Log

### Slice 1: Slice 1 — #341 mutation regression: per-file-budget reclassification + kill 5 main() mutants

- Objective: Make the next scheduled mutation run green so #341 auto-closes: root-cause the FAIL, kill the 5 survived main() mutants, and clear the blocking signal.
- Why this approach: Root-cause (refined): the FAIL was the BLOCKING selection arm, not the survived mutants (score was PASS 95% — red herring). The two module-split files closeout_loaders.py (134 covered-mutable-lines) and disposition_grammar.py (153) each exceed the per-file mutation budget (80) and are dropped by select_budgeted_sample's per-file cap (FIRST check) — seed-independent, permanent. Operator chose Option A: reclassify a covered changed file dropped solely by the per-file workload cap from blocking selection_excluded_changed_files to the non-blocking advisory changed_files_excluded_by_per_file_budget bucket. Coverage arm (uncovered changed lines) stays blocking; per-file budget unchanged (no relaxation).
- Commits:
- What changed: scripts/mutation_manifest_lib.py (new split_per_file_budget_exclusions + wire into build_manifest + MD surfacing); scripts/mutation_sample_manifest_score_lib.py (advisory key); tests/test_resolve_adapter_main_inprocess.py NEW (in-process kill of the 5 main() mutants); tests/quality_gates/test_quality_mutation_sampling.py (split unit test + scope-gap blocking/non-blocking test + MD assertions); charness-artifacts/spec/mutation-changed-line-premerge-gate.md (Deferred Decisions #341 partial-resolution note); plugins/charness/scripts mirror byte-synced.
- Alternatives rejected: Deeper line-subset mutation of oversized files (largest, deferred follow-up). Defer-only (file the selection-budget follow-up, leave #341 open) — rejected: under-delivers the goal's 'next run green' intent. Raise per-file budget — forbidden (no budget relaxation).
- Targeted verification: Targeted-mutant proof: each of the 5 mutants mutated at exact path:line, new test fails, reverted (file clean). End-to-end over the real range 3a42d2e0..HEAD with fresh coverage: selection_excluded_changed_files=[] -> scope-gap blocking=[] -> GREEN; 2 oversized files moved to advisory bucket. Producer ok:true (0 uncovered changed lines). 85 mutation/producer tests + full tests/quality_gates suite (1783 passed) green; ruff/py_compile/length/export-safe/plugin-smoke green; mirror byte-synced. NON-CLAIM: next CI scheduled run not run (authoritative verdict; #341 auto-closes on it).
- Test duplication pressure: New tests target distinct seams: split_per_file_budget_exclusions (no prior unit), the resolve_adapter main() in-process kill (no prior test ran that main directly), and scope-gap blocking/non-blocking classification. No duplicate of existing select_budgeted_sample tests (those exercise the sampler, not the manifest split). Low duplication.
- Critique: Fresh-eye reviewer (separate agent context), read-only: VERDICT SHIP. Verified invariants independently (uncovered-changed-line arm untouched -> no escape; partition predicate exactly matches select_budgeted_sample's first per-file check incl. workload==cap boundary; in-process test attributes lines 45/48 to its dynamic context so the cron selects it; ensure_ascii assertion locale-robust). One non-blocking cosmetic note: the selection_excluded blocking heading wording still says 'Selection budget or nodeid' though per-file-cap is now advisory — documented in the new comment + MD section.
- Off-goal findings:
- Lessons carried forward: The dominant recurring mutation class had a NON-coverage driver this time: per-file-cap structural collision with module-split file sizes. Producer-green (coverage arm) is necessary but NOT sufficient for the scheduled run to pass; the selection arm must also be checked. Re-derive over the FINAL pushed range at the bundle boundary (slices 2+3 add changed pool files).
- Metrics:

### Slice 2: Slice 2 — #340: surface specdown via find-skills support-skill routing

- Objective: Make find-skills surface specdown (and any tool shipping a charness-support skill) via support_skill_recommendations, not only as a binary tool_recommendation, so the canonical discovery path returns the shipped authoring guidance instead of sending the agent to reverse-engineer the binary.
- Why this approach: Classified specdown's layer first: it is an EXTERNAL INTEGRATION that ALSO ships a charness-support skill (support_skill_source), materialized under support/specdown/ only on charness update. support_recommendations_for_task iterates only local support_entries, so in a repo where the skill is not materialized there is no entry and the support route misses it. Fix: shipped_support_recommendations_for_task surfaces integrations whose support_state != integration-only (specdown, cautilus, agent-browser), gated by the SAME strong-trigger logic, deduped against materialized support skills, merged into support_skill_recommendations. Fed to the recommendation path only — inventory arrays unchanged (no inventory regression).
- Commits:
- What changed: skills/public/find-skills/scripts/list_capabilities_lib.py (new shipped_support_recommendations_for_task); list_capabilities.py (new _task_support_recommendations helper merges materialized+shipped, deduped); capability_sources.py (surface integration summary in the entry so the recommendation carries it); tests/test_find_skills_task_recommendations.py (+2 tests: surfaces-when-not-materialized, weak-text guard); tests/test_find_skills.py + tests/test_find_skills_synced_support.py (integration entry now carries summary); charness-artifacts/find-skills/latest.{md,json} refreshed (corrected stale cross-worktree state); plugins/charness mirror byte-synced.
- Alternatives rejected: Add specdown to the support_skills INVENTORY array — rejected: changes the inventory for a non-materialized skill (inventory regression). Materialize specdown locally — rejected: machine-state, not a code fix. Promote-only to support (drop tool_recommendation) — rejected: issue asks for BOTH routes.
- Targeted verification: Live #340 acceptance on the real repo: specdown appears in support_skill_recommendations (layer 'synced support skill', support_state 'upstream-consumed', summary populated) AND tool_recommendations for a specdown query. 44 find-skills tests pass (incl. new + shape-updated). ruff/length/export-safe/plugin-smoke green; mirror byte-synced. Behavior-preserving: test cautilus (integration-only) stays out of support routing; browserlike (materialized) not duplicated.
- Test duplication pressure: New tests cover the previously-untested non-materialized shipped-support path and the strong-trigger guard. Existing materialized/dedup cases (specdown materialized, browserlike) already covered — no duplication; the 2 shape updates are additive (summary field).
- Critique: Fresh-eye reviewer (separate agent context), read-only: VERDICT SHIP for #340. Verified dedup correctness (no double-surface; materialized browserlike single-entry), the support_state filter matches support_state_for_manifest, the inventory-refresh staleness claim TRUE (HEAD artifact from a different worktree with the 3 skills materialized; CI regenerates the refreshed values), and ran the acceptance. Actionable polish folded THIS slice: shipped recs had empty summary -> surfaced the integration summary in capability_sources. Over-worry (not folded): aliased-integration dedup divergence is unreachable today (the 2 aliased manifests are integration-only).
- Off-goal findings:
- Lessons carried forward: An integration can ship a support skill that materializes only on install; find-skills support routing must reason from support_skill_source, not just locally-materialized support_entries, or consumer repos lose the canonical discovery path. Resolves #340.
- Metrics:

### Slice 3: Slice 3 — activation-preflight-surface (already landed; closed the enforcement-test gap)

- Objective: Extend the artifact-shape preflight to cover the goal Activation preamble line (preamble extraction), and ensure a missing/malformed Activation preamble is flagged.
- Why this approach: FINDING: the goal-activation preflight surface was ALREADY implemented and committed in 01021a14 (2026-06-08, 'goal-activation preflight surface — Activation preamble (Slice 3)') — check_artifact_surface_preflight.py has the goal-activation surface with template_preamble=_GOAL_TEMPLATE + _extract_preamble, author-time-only (validator=None, commit_boundary=False), with the enforcement owner named (check_goal_artifact.py / goal_artifact_lib.check_goal's Activation:-line requirement). The spec (artifact-shape-preflight-coverage.md:124-136) correctly records it DONE; the docs/handoff.md 'Next Session' deferred item was STALE. Verified live: --type goal-activation surfaces the Activation shape; check_goal flags a missing Activation line (exit 1). The only genuine gap: the boundary's 'a test covers a missing/malformed Activation preamble' was only IMPLICITLY exercised (the existing bad-case test omits Activation but does not assert that issue). Closed it with an explicit enforcement test.
- Commits:
- What changed: tests/quality_gates/test_goal_artifact_lib.py — new test_check_goal_flags_missing_activation_preamble_line pinning the enforcement the preflight surface points at (missing Activation flagged; well-formed Activation raises no issue). No skill-package or code change (feature already shipped) → no mirror sync.
- Alternatives rejected: Re-implement the preflight surface — rejected: already done (01021a14), would be redundant. Extend check_goal to flag MALFORMED (present-but-wrong) Activation — rejected: out of the spec's designed scope (author-time surface + presence enforcement) and risks flagging pre-existing goals (behavior change). Edit the stale handoff now — deferred to the handoff/retro step (do not make handoff the running scratchpad mid-goal); recorded as a finding.
- Targeted verification: 93 tests pass (test_goal_artifact_lib + test_check_artifact_surface_preflight, incl. the 4 existing goal-activation/preamble tests + the new enforcement test). Live: preflight --type goal-activation surfaces the shape; check_goal flags missing Activation (exit 1). ruff clean. Behavior-preserving (additive test only).
- Test duplication pressure: New test pins the missing-Activation enforcement explicitly (previously only implicit in the bad-status test). No duplication with the preflight preamble-extraction tests (those cover _extract_preamble; this covers check_goal's verdict).
- Critique: Fresh-eye slice critique pending (spawned at slice boundary).
- Off-goal findings: docs/handoff.md 'Next Session' lists goal-activation-preflight-surface as a deferred follow-up, but it was completed in 01021a14. Stale handoff pointer — recorded; correct at the next handoff refresh. Not filed as an issue (handoff staleness, not a code defect).
- Lessons carried forward: Before implementing a deferred follow-up named only in the handoff, cross-check the OWNING spec's status — the spec (DONE) was authoritative over the stale handoff. Saved a redundant re-implementation.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **#341 (mutation regression on main):** `gh issue view 341` — FAIL on
   `3a42d2e0` (v0.32.0), 5 survived `main` mutants + changed-line
   coverage/selection blocking signal. Spec:
   `charness-artifacts/spec/mutation-changed-line-premerge-gate.md`.
2. **#340 (specdown support routing):** `gh issue view 340` — `find-skills`
   returns specdown only as `tool_recommendations`, not a support skill, though
   specdown ships an installable skill. Surface:
   `skills/public/find-skills/scripts/capability_sources.py` + `list_capabilities.py`.
3. **activation-preflight-surface (deferred follow-up):** `docs/handoff.md`
   "Next Session" + `charness-artifacts/spec/artifact-shape-preflight-coverage.md`.
4. **Recent-lessons:** `charness-artifacts/retro/recent-lessons.md` — the
   recurring mutation-changed-line class (#219→…→#335→#341) and the in-slice
   coverage guardrail.
5. **This session's completed module-split goal + retro:**
   `charness-artifacts/goals/2026-06-09-achieve-closeout-module-split.md` and
   `charness-artifacts/retro/2026-06-09-achieve-closeout-module-split.md` — the
   coverage-discipline refinement (moved/changed lines re-gate uncovered branches).
6. **Tracked-but-out-of-scope (NOT this goal):** #338 (gather X/Twitter), #184
   (product metrics — needs ideation/spec).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (operator-selected).** Family: {#341 mutation regression;
  #340 specdown routing; #184 product metrics; activation-preflight-surface;
  #338 gather X/Twitter}. Chosen: **#341 + #340 + activation-preflight-surface**
  (operator picked 1+2+4). Rejected: #184 (product-level, needs `ideation`/`spec`,
  not a code slice), #338 (gather theme, separate goal). `axis: theme` — each is
  tracked independently.
- **Single multi-slice goal vs three separate goals.** Chosen: **one
  queue-clearing goal with per-slice closeout** — keeps one operating frame while
  each slice commits + critiques independently (no cross-theme proof bundle).
  Rejected: three separate goals (more frame overhead; the operator asked for one
  goal). Re-splittable if a reviewer prefers — flagged in Boundaries.
- **Slice order.** Chosen: **#341 → #340 → preflight** — the live regression on
  main first, then the routing bug, then the bounded preflight feature. Rejected:
  preflight-first (lowest urgency).

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. (Shaping-phase self-critique; a fresh-eye
plan critique is part of activation.)

- **Cross-theme bundle dilutes closeout.** Folded: Non-Goals forbid bundling the
  three slices' closeouts; per-slice fresh-eye critique + commit; re-splittable.
- **#341 shifts with the push (HEAD moves; selection/budget is range-sensitive).**
  Folded: slice 1 re-derives the authoritative range post-push; CI scheduled run
  is the verdict; do-not-manual-close pinned.
- **specdown routing change regresses other capabilities.** Folded:
  behavior-preserving boundary + a no-inventory-regression test; classify the
  correct layer (support vs synced-support vs integration) before wiring.
- **Over-worry (raised, not folded):** that #341's survived `main` mutants are in
  an unrelated `main()` CLI and unkillable without contrived tests — kept visible
  for the fresh-eye critique to probe during slice 1 root-cause.

## Off-Goal Findings

_None yet. File off-goal findings through `issue`; record only the reference and
reason here._

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-09-deferred-queue-341-340-activation-preflight.md
Host log probe: skipped: host-log-not-exposed: this runtime exposes no host
session-timing log and the goal was not `Host metric window:`-instrumented, so
token/turn/tool-call counts cannot be measured without fabrication; the retro's
Waste section names the qualitative waste (coverage round-trip, #N-anchor
recurrence, length-limit trims) instead.
Disposition review: charness-artifacts/retro/2026-06-09-deferred-queue-341-340-activation-preflight.md
(the retro's `## Sibling Search` + `## Next Improvements` are the disposition review).

## User Verification Instructions

After the run reports complete, the user can independently verify:

1. The scheduled mutation run (or local producer over the post-push range) is
   green and #341 auto-closed.
2. `find-skills --recommend-for-task "<specdown query>"` surfaces specdown via
   support routing; #340 closed.
3. The artifact-shape preflight flags a missing/malformed `Activation:` preamble.
4. The find-skills/achieve/mutation test surface passes and the plugin mirror is
   byte-synced.

## Auto-Retro

Retro dispositions: applied: corrected the stale `goal-activation-preflight-surface` item in `docs/handoff.md` (slice 3 nearly re-implemented already-done work) + covered the `split_per_file_budget_exclusions` contention-only early-return branch (`mutation_manifest_lib.py:124`) in the introducing test (commit `6e751831`, producer re-run now `ok: true`) + persisted the "cross-check the owning spec before implementing a handoff-named deferred item" and "enumerate every branch incl. empty-result early returns in the introducing slice" lessons to recent-lessons. Per-improvement:

- applied: corrected the stale handoff `goal-activation-preflight-surface` item.
- applied: covered the `mutation_manifest_lib.py:124` contention-only branch (`6e751831`).
- accepted-risk: the #N-anchor-in-skill-package-docstrings recurrence was caught by the commit-time `validate_skill_ergonomics` sweep — nothing escaped, already dispositioned accepted-risk in recent-lessons; the commit-sweep is the backstop.

Structural follow-up: applied: coverage-producer empty-result-branch round-trip covered in `6e751831` + the in-slice-coverage guardrail re-persisted to recent-lessons (a refinement of the recurring #339 lesson, not a novel class per the `## Sibling Search` decision); the #N-anchor edit-time guard stays `none — accepted-risk` (recommended to the operator, not filed autonomously — outward-facing; the commit-sweep backstop catches it across recurrences).
