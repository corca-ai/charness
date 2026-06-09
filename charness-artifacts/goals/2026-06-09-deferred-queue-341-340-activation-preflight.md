# Achieve Goal: Clear the tracked deferred queue — #341 mutation regression, #340 specdown routing, activation-preflight surface

Status: draft
Created: 2026-06-09
Activation: `/goal @charness-artifacts/goals/2026-06-09-deferred-queue-341-340-activation-preflight.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation (draft, shaped). Three independent tracked
  items sequenced as slices; the operator chose this set (1+2+4).
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-09-deferred-queue-341-340-activation-preflight.md`.
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
| 1 | #341: root-cause + kill the 5 survived `main` mutants and cover the changed-line blocking-signal gap on the authoritative range; make the next scheduled mutation run green | live regression on main; the dominant recurring class (handoff + recent-lessons); this session's coverage-discipline lesson applies directly | local producer `ok: true` over the post-push range; survived mutants killed (targeted-mutant proof); broad gate green; #341 auto-closes on the green CI run | planned |
| 2 | #340: surface specdown via `find-skills` support-skill routing (not only integration tool); classify its correct layer first | the #1 deferred item from the module-split goal; clear repro + cost recorded in #340 | a test pins specdown in `support_skill_recommendations`/synced-support for a specdown query; inventory refreshed; mirror synced; issue closeout draft validates | planned |
| 3 | activation-preflight-surface: extend the artifact-shape preflight to cover the goal `Activation:` preamble line (preamble extraction) | deferred follow-up named in handoff; small, bounded | preflight flags a missing/malformed Activation preamble; test; spec updated; mirror synced | planned |

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
  an `Issue closeout:` line naming the close-intended issue numbers (#341, #340),
  carrier (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. #341 is the
  auto-closing mutation-marker case — record the CI-run dependency, do not manual-close.

## Slice Log

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

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

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

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <change>` / `issue #N (recurs:|novel:)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
