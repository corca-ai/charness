# Resolution Critique — #331 slice-closeout fnmatch coverage gap

Date: 2026-06-07
Issue: #331 (repo-python's `scripts/**/*.py` does not match top-level
`scripts/<file>.py` under fnmatch, so the surface's verify set never ran at slice
closeout for scripts changes).
Reviewer provenance: bounded fresh-eye subagent review (independent agent
context, read-only in the shared parent worktree), run at the bundle boundary;
this is the same reviewer that flagged #331 in the #328 closeout, now reviewing
its fix.

## Scope reviewed

`.agents/surfaces.json` matching-idiom reconciliation + a regression guard:

- `repo-python` source `scripts/**/*.py` -> `scripts/*.py` (the headline #331 fix).
- Sibling-scan reconciliation of every `<dir>/**/*.X` pattern in the manifest to
  the `<dir>/*.X` idiom (fnmatch `*` crosses `/`, so `*.X` covers top-level AND
  nested; the bare `**/` form misses a top-level `<dir>/<file>.X`):
  - `repo-markdown` source `packaging/**/*.md` -> `packaging/*.md` (a **live
    leak**: `packaging/README.md` was matched by nothing in repo-markdown, so it
    skipped check-markdown/doc-links/secrets at closeout);
  - `charness-artifacts/`, `integrations/`, `skills/` `**/*.md` -> `*.md` (latent
    traps, 0 top-level files today);
  - collapsed redundant `docs/**/*.md`, `evals/**/*.md`, `tests/**/*.py` pairs to
    the single `*.X` form;
  - derived `plugins/charness/**/*.md`, `plugins/charness/scripts/**/*.py`,
    `.charness/**/*.json` -> `*.X` (redundant via no-suffix siblings; reconciled
    for consistency).
- `tests/quality_gates/test_surface_obligations.py`: two regression guards
  (repo-python matches a top-level script; repo-markdown matches
  packaging/README.md).

## Findings

- **BLOCKERS: none.** Reviewer verdict SHIP. The fix's primary claims verify:
  fnmatch `*` crosses `/`; all 237 tracked scripts are top-level; the old
  `scripts/**/*.py` matched zero of them. `scripts/*.py` is a strict superset, so
  the change is additive — no path becomes wrongly unmatched.
- **Reviewer's recommended same-commit addition applied.** The reviewer flagged
  `packaging/README.md` as a live instance of the same idiom and warned against
  shipping "fixed the idiom" while a sibling leaks. Resolved by reconciling the
  whole class, not just scripts.
- **Behavior change is intended, not a footgun.** repo-python now contributes the
  broad pytest to scripts closeouts; it flows through the same
  `plan_broad_pytest_policy` lock-gating, so `--plan-only` / `--skip-broad-pytest`
  still work (reviewer verified). Scripts changes were wrongly exempt from the
  standing Python gates.
- **Regression guards are real, not tautological** (reviewer simulated a revert to
  `**/*.py`; the guard's `repo-python in matched_surfaces` assertion fails).

## Structured Findings

- scripts-idiom-fix | bin: act-before-ship | evidence: strong | ref: .agents/surfaces.json repo-python source_paths | action: fix | note: scripts/**/*.py -> scripts/*.py; repo-python now matches all 237 (all-top-level) scripts at closeout; regression-guarded.
- packaging-readme-live-leak | bin: act-before-ship | evidence: strong | ref: .agents/surfaces.json repo-markdown packaging | action: fix | note: packaging/**/*.md -> packaging/*.md closes a live leak where packaging/README.md skipped check-markdown/doc-links/secrets at closeout; regression-guarded.
- latent-md-idiom-traps | bin: act-before-ship | evidence: moderate | ref: .agents/surfaces.json repo-markdown charness-artifacts/integrations/skills | action: fix | note: reconciled to *.md so the first top-level doc added under those dirs does not silently escape the markdown closeout gate.
- derived-redundant-idiom | bin: over-worry | evidence: weak | ref: .agents/surfaces.json derived_paths | action: fix | note: derived **/*.X are redundant via no-suffix siblings (no coverage lost) but reconciled to *.X so the commit's "fixed the idiom" claim is honest manifest-wide.

## Verification proof

- Regression guards + existing surface assertions: `test_surface_obligations.py`
  32 passed (incl. `matched_surfaces == []` for the non-Python path).
- Broad pytest at the bundle boundary: 2375 passed, 4 skipped.
- `validate_surfaces` (28 surfaces) clean; no `**/*.X` patterns remain;
  `check-markdown`, `check_doc_links`, `ruff` clean; plugin mirror unaffected
  (.agents/surfaces.json is not part of the export).

## Counterweight pass

- Reconciling the full idiom (not just scripts) is the sibling-scan discipline,
  not scope creep: one live leak (packaging) plus latent traps, all the same
  one-line root cause, all additive. Stopping at scripts would have shipped a
  knowingly-partial "idiom fixed" claim.
- Touching derived paths is the lowest-value change (redundant), but leaving three
  derived instances of the broken idiom would contradict the commit message;
  fixing them is additive and cheap.
