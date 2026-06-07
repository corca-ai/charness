# Resolution Critique — #328 cheap upstream pre-checks + gate-phase coverage

Date: 2026-06-07
Issue: #328 (cheap upstream pre-checks: prose-pin scan + authoring-preflight
prompt) — resolved alongside the gate-phase coverage gap from the
`2026-06-08-preflight-gate-phase-coverage` achieve goal.
Reviewer provenance: bounded fresh-eye subagent review (independent agent
context, read-only in the shared parent worktree), run at the bundle boundary
per the goal's high-confidence verification plan.

## Scope reviewed

- **S2 prose-pin pre-check:** new `scripts/check_prose_pin.py` (advisory; flags
  tests/ string literals that are verbatim substrings of prose removed from a
  changed `.md` doc/SKILL file, and tests/ references to renamed/deleted
  doc/SKILL paths). Wired as a slice-closeout advisory via new
  `scripts/slice_closeout_advisories.py`, called from `run_slice_closeout.py`.
- **S3 authoring-preflight prompt:** extended
  `check_skill_surface_preflight.py --run-checks` to the full portable-package
  gate set via a `_check_commands` seam (validate_skill_ergonomics,
  check_skill_ownership_overlap, validate_attention_state_visibility); doc
  sections in `authoring-preflight.md`; a closeout `ADVISORY:` pointer.
- **S4 gate-phase coverage:** new `python-scan-hygiene` surface in
  `.agents/surfaces.json` runs `inventory-gitignore-scan-hygiene` at slice
  closeout for top-level scripts, nested scripts, and skill scripts; confirmed
  `validate-retro-lesson-index` already reachable at closeout.

## Findings

- **BLOCKERS: none.** The fresh-eye reviewer returned SHIP. The change is
  additive/advisory-only: the prose-pin and skill-surface advisories run before
  the `_maybe_block_*` gates and return nothing, so they never alter closeout
  exit status; the new surface adds a deduped verify command without breaking the
  `matched_surfaces == []` test (which uses a non-Python path).
- **Honest-non-claim discipline:** `validate-retro-lesson-index` was already
  reachable at slice closeout via the `retro-lesson-selection-index` surface — so
  S4 *confirmed* it (with a test) rather than claiming a new wire. The boundary
  ratchet was likewise already at closeout/pre-commit for the tests/ class; the
  real gap it had was authoring-time surfacing (S3's preflight affordance).
- **One non-blocking parser nit, fixed in-session:** the reviewer found that the
  removed-line parser's `startswith("---")` could swallow a removed *content*
  line beginning with `--` (a silent false-negative; advisory-only, safe failure
  direction). Fixed by parsing `-` body lines only inside a hunk (`@@` boundary).
- **#328 accidental close:** the issue had been auto-closed by a stray
  `resolves #328` in the handoff commit `12e9d54b` before any work landed.
  Reopened with a note; closing via this carrier commit.

## Structured Findings

- prose-pin-dash-parser | bin: act-before-ship | evidence: moderate | ref: scripts/check_prose_pin.py removed_lines | action: fix | note: removed-line parser gated on `@@` hunk boundary so removed content starting with `--` is no longer mistaken for a diff header; fixed and re-tested in-session.
- top-level-scripts-fnmatch-gap | bin: valid-but-defer | evidence: strong | ref: .agents/surfaces.json repo-python source_paths | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/331 | note: repo-python `scripts/**/*.py` does not match top-level `scripts/<file>.py` under fnmatch, so its whole verify set skips top-level scripts at closeout; bigger blast radius (closeout cost), deferred to its own critique.
- prose-pin-path-substring | bin: over-worry | evidence: weak | ref: scripts/check_prose_pin.py find_path_pins | action: defer | note: bare `path in text` could prefix-collide for a future gone-path without a distinguishing suffix; current inputs are full suffixed paths (verified no collision), advisory-only.

## Verification proof

- Targeted tests: `test_check_prose_pin.py` (4), `test_skill_surface_preflight.py`
  + `test_authoring_preflight_reference.py` (22), `test_surface_obligations.py`
  (30) — all pass.
- Broad pytest at the bundle boundary: 2373 passed, 4 skipped.
- Deterministic gates clean: `ruff`, `check_python_lengths --require-git-file-listing`
  (advisory warn-band only), `check_doc_links`, `check-markdown`,
  `validate_attention_state_visibility`, `validate_surfaces` (28 surfaces),
  `validate_packaging` + `validate_packaging_committed`,
  `inventory_gitignore_scan_hygiene --require-empty` (my own `rglob` does not trip
  it), `check_boundary_bypass_ratchet` (the new subprocess test did not increase
  the convertible count).
- Plugin mirror: `plugins/charness/scripts/*` copies byte-match canonical sources.

## Counterweight pass

- The `--` parser false-negative was a real correctness nit but advisory-only and
  in the safe direction; fixing it in-session was cheap and correct, not
  over-engineering.
- The #331 fnmatch gap is real and on-theme but has genuine closeout-cost blast
  radius; deferring it to its own critique/slice is the proportionate call, not
  avoidance — the new scripts in this commit were independently verified clean
  against the affected gates so nothing latent ships.
- The new `python-scan-hygiene` surface is one dedicated verify-only surface, not
  duplicated gate logic: it reuses the existing checker and is the in-architecture
  way to scope the gate to filesystem-scanning Python.
