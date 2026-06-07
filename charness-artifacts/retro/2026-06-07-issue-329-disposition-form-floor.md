# Retro — #329 retro disposition-form floor

Date: 2026-06-07

## Mode

session

## Context

Activated the shaped achieve goal `2026-06-07-329-disposition-form-floor` and ran
it end to end: built a narrow presence/enum **form** floor (#329) that rejects the
named-invalid prose-only `Disposition: memory` and requires one of
`applied: <change>` / `issue #N` / `none — <reason>`, form-only (never a content
classifier). Landed a shared single-source grammar (`scripts/disposition_form.py`),
folded it into the achieve closeout (rung 1c) and the session-retro validator
(BOTH-reach, per the activation default), grandfathered by an enforce-from-date,
and staged `Closes #329`. Routed via `find-skills` → `achieve` (impl + quality;
in-repo, no external source).

## Evidence Summary

- New `scripts/disposition_form.py` (single source of grammar) + 21-case test;
  wired into `goal_artifact_disposition.apply_disposition_rungs` (achieve
  `## Auto-Retro`) and `validate_retro_artifact` (session `## Next Improvements`).
- Enforce-from-date `DISPOSITION_FORM_RULE_DATE = 2026-06-08` (day after today),
  so #330 (frozen `complete`, Created 2026-06-07, carries `memory ->`/`fix (folded)`),
  this #329 goal, and the triggering retros are all grandfathered.
- Corpus safety: 0 completed goals retroactively form-failed;
  `validate_retro_artifact --all` validated all 152 retros clean.
- Bounded fresh-eye review: SHIP-WITH-NITS; both real findings folded before ship
  (`charness-artifacts/critique/2026-06-07-issue-329-disposition-form-floor.md`).
- Broad pytest green; ruff / check_python_lengths / ergonomics / attention-state /
  export-safe / plugin-import-smoke green; mirror byte-synced.

## Waste

- **Two self-introduced gate regressions surfaced only at the broad-pytest
  boundary, not at the commit boundary (biggest process waste).** My `(#329)`
  comments in the portable achieve leaf tripped `validate_skill_ergonomics`'
  `portable_package_issue_anchor`, and a stray `skipped` term in a docstring
  tripped `validate_attention_state_visibility`. Both are **already wired as
  commit-boundary slice-closeout gates** (`.agents/surfaces.json` #314/#328), but
  at the slice boundary I ran only ruff + lengths + targeted pytest + export-safe +
  plugin-smoke — I did NOT run the slice-closeout surface-gate runner on my changed
  `scripts/`+`skills/` surfaces, so the broad gate (7 min) caught what a cheap
  commit-boundary sweep would have caught immediately. No harm shipped (caught
  before close), but it cost a full broad-pytest round-trip.
- **The dateless-retro grandfather gap was caught by the reviewer, not by me.** My
  retro floor fail-closed on a missing `Date:` line; 93/152 frozen retros predate
  that header, so 4 would have been retroactively failed under `--all` — a direct
  Goodhart Non-Goal violation. The bounded review found it; I folded a filename-date
  fallback before ship. Cheap to fix, avoidable by probing the real corpus up front.

## Critical Decisions

- **Shared single-source grammar in `scripts/disposition_form.py`, consumed by the
  portable achieve skill via parent-walk — not a cross-boundary `skills/public`
  import.** The export rewrites `skills/public/X` → `skills/X`, so a hardcoded
  cross-skill path would break in the installed plugin; the `scripts/` shared-helper
  pattern (already used for `check_prescribed_skill_executed_lib`) ships to
  `plugins/charness/scripts/` and resolves via parent-walk in both tree and export.
  This satisfied the goal Boundary "do not fork disposition parsing" without the
  portability landmine.
- **Enforce-from-date = the day AFTER today (2026-06-08).** The Goodhart-correct
  off-by-one: everything created/dated through 2026-06-07 (incl. the very dogfood
  instances the issue cites) is grandfathered; the floor takes effect for the next
  session's artifacts. Tests exercise it with synthetic future/past dates.
- **Folded the floor into `apply_disposition_rungs`, not the wrapper.** The wrapper
  sat at 348/360 code lines (no headroom); the rung lives in the smaller leaf and
  runs first on its own enforce-date, so it is independent of rungs 1a/1b.

## Expert Counterfactuals

- A **release-engineer / portability lens** (the harness "keep host/repo specifics
  out of portable packages" discipline) would have flagged the `(#329)` anchors in
  the portable achieve leaf before I wrote them, and would have reflexively run the
  commit-boundary structural gates on a new portable-skill edit. That single habit
  would have erased the session's biggest waste — the broad-gate round-trip — and is
  exactly what the `surfaces.json` slice-closeout gates exist to automate.
- A **frozen-corpus archivist lens** would have probed "does my enforce path
  actually grandfather the *real* historical corpus, including its older header
  conventions?" before trusting a single `Date:`-line parse — catching the dateless
  fail-closed gap that the reviewer ultimately found.

## Sibling Search

- axis: other disposition-bearing surfaces beyond Auto-Retro + Next-Improvements | location: charness-artifacts/retro/recent-lessons.md, docs/handoff.md "Next Session" | decision: not a sibling — distinct derived/handoff surfaces (no action needed) | proof: `recent-lessons.md` is a generated digest of retros that are now gated at source, and handoff "Next Session" candidates are not improvement dispositions; gating derived surfaces would double-judge the same lessons, so the floor stays at the two primary authoring surfaces #329 named.

## Next Improvements

- workflow: when a slice touches a NEW `scripts/*.py` or a portable skill package,
  run the slice-closeout surface-gate runner on the changed surfaces (it already
  wires `validate_skill_ergonomics` + `validate_attention_state_visibility` per
  #314/#328) at the commit boundary — do not defer those cheap structural gates to
  the broad-pytest bundle boundary. Disposition: issue #332 — escalated this
  recurring trap (3rd instance: #308/#325/#329) to make the commit-boundary
  structural sweep non-discretionary; memory-only reminders have not stopped it
  (source: this retro).
- workflow: when building an enforce-from-date grandfather, probe the REAL corpus
  (including older header/date conventions) before trusting a single date-line
  parse; add a filename/identity fallback so frozen artifacts are not fail-closed
  into retroactive enforcement. Disposition: applied: landed the filename-date
  fallback in `validate_retro_artifact._retro_observed_date` + regression tests
  this run (source: this retro).
- capability: extend the disposition-form floor's reach to other emitters only if a
  real invalid form ships from them. Disposition: none — the two surfaces #329
  named (achieve Auto-Retro + session Next-Improvements) are now gated at source and
  derived digests inherit it; no third surface has shipped an invalid form, so no
  new teeth are warranted yet.

## Persisted

yes: charness-artifacts/retro/2026-06-07-issue-329-disposition-form-floor.md
