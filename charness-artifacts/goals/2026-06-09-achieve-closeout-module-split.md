# Achieve Goal: Split the at-cap achieve closeout module family

Status: draft
Created: 2026-06-09
Activation: `/goal @charness-artifacts/goals/2026-06-09-achieve-closeout-module-split.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **Slice 2** — split `goal_artifact_closeout_evidence.py` (348/360).
  Slice 1 (disposition grammar leaf) SHIPPED: verdict parity byte-identical over
  68 goals, headroom 352->250, fresh-eye SHIP. Active.
- Next action: extract the sibling-loader + evidence-binding boilerplate from
  `goal_artifact_closeout_evidence.py` into one cohesive module; keep
  `check_complete_evidence` + the parse/token public surface stable; verdict parity
  against the frozen golden baseline (`/tmp/GOLDEN_baseline.json`, sha 28e3f24a).
- **Why this goal (chosen from the session signals):** the #339 work had to route
  logic through the shared grammar + wire new floors from the CLI THREE times to
  avoid the at-cap closeout files; recent-lessons flags this as deferred structural
  debt "so the next at-cap addition starts from a split, not another workaround."
  Alternatives weighed (see Interview Decisions): #340 (find-skills/specdown — small
  bug, different surface), #338 (gather X/Twitter — gather theme), #184 (product
  metrics — needs ideation/spec, not a code slice), an edit-time `#N`-anchor
  authoring guard (authoring-preflight theme). The at-cap split is the one THIS
  session created and the only one that is a concrete, well-scoped, this-repo
  structural slice.
- Carry the #339 lessons: cover any NEW module's lines IN the introducing slice (so
  the bundle-boundary mutation producer confirms, not discovers); keep NO `#N`
  anchors in skill-package files; run the changed-line coverage producer FIRST at
  the bundle boundary; verify byte-identical closeout-gate verdicts on the live
  corpus (the behavior-preserving proof).
- Verification cadence: cheap deterministic checks at commit boundaries;
  before/after closeout-gate verdict parity + fresh-eye critique at slice
  boundaries; broad gate + changed-line coverage at the bundle boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Split the at-cap achieve closeout module family (goal_artifact_disposition.py 352/360, goal_artifact_closeout_evidence.py 348/360) into cohesive sub-modules, behavior-preserving, plugin mirror byte-synced, restoring real headroom so the next floor/rung addition starts from a clean split rather than another shared-grammar/CLI workaround.

## Non-Goals

- Do NOT change any closeout BEHAVIOR. This is a pure structural refactor; the
  closeout gate (`check_goal_artifact.py`) must produce byte-identical verdicts
  before/after on the live goal corpus.
- Do NOT touch the shared grammar `scripts/disposition_form.py` (it has ample
  headroom and is the wrong layer); this goal is the achieve-skill closeout
  module family only.
- Do NOT split into incoherent fragments — each new module is ONE cohesive
  concern with a clear name, not a line-count dump.
- Do NOT take on #340 (find-skills/specdown), #338 (gather X/Twitter), #184
  (product metrics), or the edit-time `#N`-anchor authoring guard — different
  themes, tracked separately (see Context Sources).
- Do NOT cut a real release/push by default — standard `achieve` no-push.

## Boundaries

- **Behavior-preserving (the load-bearing boundary).** A before/after verdict
  parity check of the closeout gate over the live `charness-artifacts/goals/*`
  corpus is a REQUIRED low-cost proof: the JSON verdict must be byte-identical
  pre/post-split. Public symbols other modules import (`apply_disposition_rungs`,
  `check_complete_evidence`, the rung helpers) keep their names + signatures.
- **Headroom restored.** After the split each touched file (and each new module)
  sits well under the `check_python_lengths` warn band, with room for the next
  rung/floor — not merely 1–2 lines under the hard cap.
- **Loading patterns preserved.** The skill modules cannot `from scripts.` import
  directly; the parent-walk loaders (`_load_shared_form`, the sibling `_load_*`
  helpers, `load_repo_module_from_skill_script`) must keep working in both the
  working tree and the installed plugin export (`check_plugin_import_smoke` +
  `check_export_safe_imports` are the proof).
- **Public-skill + generated-surface scope.** Touches achieve skill scripts ->
  mirror-sync (`plugins/charness/...`) byte-synced, public-skill dogfood,
  deterministic gates own closeout. No `#N` anchors in skill-package files.
- Discuss before activation: CONFIRMED — the activation-discussion detector fires
  a false positive here because this goal's own SUBJECT is "split" and it lists
  tracked issues (#340/#338/#184) as explicitly out-of-scope context. There is no
  real consequential decision: no live/prod proof, no genuine issue close/split,
  no cross-theme bundle, no proof-level non-claim. This is a pure
  behavior-preserving refactor (proven by the closeout-gate verdict-parity check),
  default no-push, single-theme. Safe to activate directly; re-open this line if a
  reviewer disagrees.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

What the user can do to verify completion directly.

- Run the closeout gate (`check_goal_artifact.py`) on the live goal corpus before
  and after; confirm byte-identical verdicts (no behavior change).
- Run `check_python_lengths.py --headroom` on the two formerly-at-cap files and
  confirm real headroom is restored (well under the warn band).
- Confirm the full achieve/closeout/disposition test surface passes unchanged and
  the plugin mirror is byte-synced + import-smoke green.
- Confirm each new module is one cohesive, well-named concern (the fresh-eye
  critique attests cohesion, not just line count).

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched/new file.
- The touched scripts' pytest modules; a before/after closeout-gate verdict-parity
  check over the live `charness-artifacts/goals/*` corpus (byte-identical JSON).
- `check_export_safe_imports` + `check_plugin_import_smoke` + mirror byte-sync.

### High-Confidence Checks

- The full achieve/closeout/disposition/coordination/surface test surface green.
- Broad gate (`run-quality.sh --read-only`) at the bundle boundary; run the
  changed-line mutation coverage producer FIRST (cover any relocated/new line in
  the introducing slice). Fresh-eye `critique` at each slice boundary judging
  module cohesion + behavior preservation.

### External Or Live Proof

- None by default (no-push). Record `Release: n/a — <reason>` unless a release
  is bundled at the operator's request.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Split `goal_artifact_disposition.py` (352/360): extract the rung floor functions and/or the shared section-scope/fence-mask/loader helpers into one cohesive module; keep `apply_disposition_rungs` + the rung names/signatures stable | it is the more at-cap of the two and the one #339's rung 1f had to squeeze into | verdict parity on the corpus; headroom restored; rung tests + critique SHIP | planned |
| 2 | Split `goal_artifact_closeout_evidence.py` (348/360): extract the sibling-loader + evidence-binding boilerplate into one cohesive module; keep `check_complete_evidence` stable | it is the wrapper #339's proof-mismatch wiring could not touch; the CLI workaround was forced by its cap | verdict parity; headroom restored; closeout-evidence tests + critique SHIP | planned |
| 3 | Bundle closeout: broad gate; changed-line coverage; retro; demonstrate a fresh rung can be added to the new module without hitting the cap | prove the debt is actually retired, not relocated | broad gate PASS; coverage 0 uncovered; retro + dispositions | planned |

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

### Slice 1: Slice 1 — extract disposition grammar leaf

- Objective: Split goal_artifact_disposition.py (352/360) into a cohesive leaf goal_artifact_disposition_grammar.py holding the markdown grammar + disposition-scope primitives; keep the rung verdicts + public surface stable.
- Why this approach: The grammar/scope primitives (fence-mask, section-body, Created-date parse, scope predicate, Auto-Retro content probes, bound-retro resolver) are one cohesive parse substrate the rungs build verdicts on — the cleanest seam between 'what the rungs parse' and 'what the rungs decide'. Pure leaf (no sibling import, mutates no report).
- Commits:
- What changed: NEW skills/public/achieve/scripts/goal_artifact_disposition_grammar.py (152/360). goal_artifact_disposition.py 352->250/360, keeps the rung-verdict logic + _load_shared_form + RECURRENCE_LINEAGE_RULE_DATE, adds _load_local_module loader + a re-bind block keeping disposition_gate_applies/auto_retro_is_blank/find_disposition_optout/retro_lists_improvements/_mask_fences as module attributes. Mirror byte-synced to plugins/charness/skills/achieve/scripts/.
- Alternatives rejected: Extracting the three rung floor functions instead (rejected: leaves rungs 1a/1f with the orchestrator — a split-rungs seam, less cohesive than grammar-vs-verdicts). Splitting only one file (rejected by goal scope — both at-cap).
- Targeted verification: Verdict parity over all 68 live goals byte-identical except wall-clock remaining_minutes (untouched timebox module). Headroom 250 + 152 (110/208 left). 264 disposition/closeout tests pass. check_export_safe_imports (447) + check_plugin_import_smoke green. Mirror byte-synced.
- Test duplication pressure: none — pure behavior-preserving move; no new logic to test. Existing disposition/form/coordination tests already pin the moved functions' behavior; the verdict-parity corpus is the move proof.
- Critique: full — fresh-eye general-purpose bounded reviewer in shared worktree: AST-level body comparison of every moved symbol = byte-identical vs HEAD; all importers reachable; grammar cohesive; loader does not register into sys.modules and resolves __file__-relative in the export. VERDICT SHIP.
- Off-goal findings:
- Lessons carried forward: _load_local_module deliberately does NOT insert into sys.modules (avoids global shadowing); __file__-relative spec resolves the sibling in the SAME export dir, so the leaf loads identically in tree and plugin export.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **The motivating debt (this session):** `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`
   — the #339 work routed around the at-cap files 3×; recent-lessons records the
   deferred split.
2. **The at-cap files:** `skills/public/achieve/scripts/goal_artifact_disposition.py`
   (352/360) and `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
   (348/360), plus the length gate `scripts/check_python_lengths.py`.
3. **The split-pattern precedent:** the prior `run_slice_closeout.py` module-split
   goal `charness-artifacts/goals/2026-06-08-run-slice-closeout-module-split.md`
   (orchestrator + cohesive reporting module, behavior-preserving, mirror byte-synced).
4. **Recent-lessons:** `charness-artifacts/retro/recent-lessons.md`.
5. **Tracked-but-out-of-scope queue (NOT this goal):** #340 (find-skills surfaces
   specdown as an integration, not the support skill), #338 (gather X/Twitter
   exact-source fallback), #184 (product metrics — needs ideation/spec), the
   edit-time `#N`-anchor authoring guard (authoring-preflight theme), and the
   `goal-activation-preflight-surface` follow-up in `docs/handoff.md`.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (chosen by the operator's "next thing to do" from the session
  signals).** Family: {at-cap closeout module split; #340 find-skills/specdown;
  #338 gather X/Twitter; #184 product metrics; an edit-time `#N`-anchor authoring
  guard}. Chosen: **the at-cap closeout module split** — the only candidate THIS
  session created (it forced 3 workarounds), a concrete well-scoped this-repo
  structural slice, and flagged in recent-lessons. Rejected: #340/#338 (different
  surfaces/themes), #184 (product-level, needs `ideation`/`spec`, not a code slice),
  the `#N`-guard (authoring-preflight theme; bundling it would be the cross-theme
  over-anchoring trap). `axis: theme` — each rejected item is tracked separately.
- **Split scope (chosen).** Family: {split both at-cap files; split only the more
  at-cap one}. Chosen: **both** — they are one cohesive closeout family and leaving
  one at-cap keeps the debt live. Rejected: only-one (debt persists; the next
  addition to the untouched file hits the same wall).

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique. (Shaping-phase
self-critique; a fresh-eye plan critique is part of activation.)

- **A refactor that silently changes behavior.** Folded: Boundaries + Verification
  require a before/after closeout-gate verdict-parity check (byte-identical JSON)
  over the live corpus, and public symbol names/signatures are pinned.
- **Splitting into incoherent line-count fragments.** Folded: Non-Goals require one
  cohesive concern per module; the fresh-eye slice critique judges cohesion, not
  just headroom.
- **Parent-walk / plugin-export loading breaks when modules move.** Folded:
  Boundaries pin the loading patterns + require `check_plugin_import_smoke` +
  `check_export_safe_imports` + byte-synced mirror as proof.
- **Over-worry (raised, not folded):** that headroom is illusory if the split just
  relocates lines. Mitigated by Slice 3's "demonstrate a fresh rung can be added"
  acceptance, but kept visible as a real risk the fresh-eye critique should probe.

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

1. The closeout gate (`check_goal_artifact.py`) returns byte-identical verdicts on
   the live goal corpus before and after the split (no behavior change).
2. `check_python_lengths.py --headroom` shows real headroom restored on both
   formerly-at-cap files and each new module.
3. The full achieve/closeout test surface passes; the plugin mirror is byte-synced
   and import-smoke green.
4. Each new module is one cohesive, well-named concern.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <change>` / `issue #N (recurs:|novel:)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
