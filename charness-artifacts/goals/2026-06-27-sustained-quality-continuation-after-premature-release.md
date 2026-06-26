# Achieve Goal: Sustained quality continuation after premature release

Status: active
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-sustained-quality-continuation-after-premature-release.md`

This goal continues the prior quality timebox after the `v0.56.5` release was
cut too early relative to the user's intent to keep discovering quality slices.

## Active Operating Frame

- Current slice: support-skill helper reference and stale handoff cleanup.
- Current slice intent: correct a concrete support-skill reference drift and
  stale handoff instruction discovered while re-entering quality discovery.
- Next action: patch the source and plugin mirror surfaces, run focused
  validators, then continue to the next quality candidate if the slice stays
  cheap.
- Verification cadence: focused deterministic checks at each small slice;
  broader proof only when code, generated surfaces, or release boundaries move.

## Goal

Continue aggressive Charness quality improvement after the prior goal was
closed early. Keep discovering and implementing additional high-leverage quality
slices across bugs, test speed, script speed, execution speed, token efficiency,
and operator/agent usability. Commit and push useful slices; decide whether a
follow-up release is warranted only after additional release-worthy changes
accumulate.

## Non-Goals

- Do not cut another release merely to compensate for the premature closeout.
- Do not weaken standing quality gates to create speed.
- Do not add a broad blocking floor for every discovered documentation drift.
- Do not run Cautilus unless the repo planner allows a named log-backed lane.

## Boundaries

- The `v0.56.5` release already exists. New changes belong to this continuation
  goal and need a separate release decision later.
- Push is in scope for completed local quality slices.
- Release is not automatic for each slice; route through `release` only if the
  final bundle changes installed/operator behavior enough to warrant it.
- Done-early policy: continue_next_improvement while cheap, local proof remains
  available.

## User Acceptance

- Review the continuation commits pushed after `v0.56.5`.
- Run focused tests or validators named in `## Final Verification`.
- Inspect the updated handoff/quality artifacts for honest non-claims.

## Agent Verification Plan

- `find-skills` recommendation confirms `quality` for the improvement route.
- Quality planner primers and report-first inventories guide slice selection.
- Focused validators cover changed docs/skill surfaces.
- `check_changed_surfaces.py` and sync checks run if generated/plugin surfaces
  are touched.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Re-enter quality discovery and repair stale reference drift | User clarified the timebox should continue; startup found a stale handoff and support-skill helper path | find-skills route, quality planner, focused validators | in_progress |
| 2 | Repair remaining support helper reference drift | Continue discovery beyond the first cleanup | support package scan and focused proof | complete |
| 3 | Closeout/push/release decision | Avoid another premature release | final validators, commit/push, release recommendation | pending |

## Operator Decision Queue

none — no operator-only decision is currently queued; follow-up release remains
deferred until enough release-worthy changes accumulate.

## Coordination Cues

Routing: `find-skills` recommended `quality` for this continuation quality
discovery route.
Gather: n/a — no external URLs or source links were introduced as working
context for this continuation slice.
Release: n/a — this slice intentionally does not cut a release.
Issue closeout: n/a — this continuation has not claimed tracked issue closeout.

## Slice Log

- Re-entry evidence:
  - User clarified that the original three-hour goal meant continued discovery,
    not early release once one slice passed.
  - `find-skills` recommended `quality` as the public skill route.
  - `quality` planner required report-first evidence and current-primer reads.
  - Runtime summary: `run-quality-read-only` remains the main standing cost
    (`38.1s` latest, `65.7s` recent median) but within budget.
  - Handoff candidate check: `route_public_fetch.py` is no longer near-limit
    (`85/360` Python code lines), so the handoff's "split remaining near-limit
    web-fetch helper" instruction is stale.
  - Support-skill reference drift: `skills/support/web-fetch/SKILL.md` and the
    plugin mirror list `<repo-root>/scripts/route_public_fetch.py` and
    `<repo-root>/scripts/classify_fetch_response.py`, but the runnable helpers
    live under the support skill's `scripts/` directory.
  - Slice 1 repair: changed web-fetch references to
    `scripts/route_public_fetch.py`, `scripts/classify_fetch_response.py`, and
    `scripts/acquire_public_url.py`; updated `docs/handoff.md` to remove the
    stale near-limit split instruction and point #392 back to current
    gather/web-fetch behavior evidence.
  - Sync proof: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
    refreshed `plugins/charness/support/web-fetch/SKILL.md` and marketplace
    surfaces.
  - Focused proof: `check_skill_surface_preflight.py` for web-fetch,
    `check_doc_authoring_preflight.py --path docs/handoff.md`,
    `check_references_link_inventory.py` for web-fetch, `validate_skills.py`,
    `validate_skill_ergonomics.py`, `check_skill_ownership_overlap.py`,
    `check_doc_links.py`, `check_command_docs.py`, `check-markdown.sh`,
    `check-secrets.sh`, `validate_packaging.py`,
    `validate_packaging_committed.py`, `validate_cautilus_proof.py`, and
    `validate_cautilus_diagnostics.py` passed.
- Slice 2 evidence:
  - Follow-up scan found the same support-helper reference drift in
    `gather-notion`, `gather-slack`, and `markdown-preview`: their `## References`
    sections pointed at `<repo-root>/scripts/...` helpers while the shipped
    helpers live inside each support skill package.
  - Repaired root support skill references and provenance references to use
    package-local `scripts/...` paths, then synced plugin mirrors.
  - Drift check: `rg -n '<repo-root>/scripts/' skills/support
    plugins/charness/support` returned no matches after the repair.
  - Focused proof: `check_references_link_inventory.py` over support
    `SKILL.md`/references, `validate_skills.py`, `validate_skill_ergonomics.py`,
    `check_doc_links.py`, `check_command_docs.py`, `check-markdown.sh`,
    `check-secrets.sh`, `validate_packaging.py`,
    `validate_packaging_committed.py`, `validate_cautilus_proof.py`,
    `validate_cautilus_diagnostics.py`, `check_skill_ownership_overlap.py`, and
    support helper `py_compile` passed.

## Context Sources

- User clarification in chat: "계속 발굴하라는 거 맞음".
- Prior completed goal:
  `charness-artifacts/goals/2026-06-27-sustained-quality-speed-token-release-round-4.md`
- `docs/handoff.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/quality/latest.md`

## Interview Decisions

- Continue rather than only acknowledge because the user corrected the intended
  operating shape.
- Treat `v0.56.5` as already published and keep additional slices local until a
  new release decision is justified.
- Prefer measured current candidates over stale handoff text when they conflict.

## Plan Critique Findings

- Same-agent critique: another immediate release would compound the premature
  release mistake. Folded response: release is deferred until the continuation
  bundle warrants it.
- Same-agent critique: broad `<repo-root>/scripts/...` reference existence
  enforcement would currently flag many historical path conventions. Folded
  response: fix the concrete support-skill drift first and leave broader cleanup
  as a later candidate.

## Off-Goal Findings

- Broader `<repo-root>/scripts/...` reference cleanup may be useful, but it needs
  a separate source-of-truth decision because many public skill references use
  that convention today.

## Final Verification

Retro: skipped: not-closeout-yet: continuation goal is still active.
Host log probe: skipped: not-closeout-yet: continuation goal is still active.
Disposition review: skipped: not-closeout-yet: continuation goal is still active.

## User Verification Instructions

- Inspect changed support-skill references and handoff text after slice 1.
- Run focused validators named in the slice log.

## Auto-Retro

Retro dispositions: pending until closeout.
