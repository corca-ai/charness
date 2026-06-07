# issue-331 slice-closeout fnmatch idiom
Date: 2026-06-07

## Mode

session

## Context

Closed #331 (the fnmatch closeout-coverage gap filed during the #328 session),
prompted by the operator's "retrospect waste + design the next chunk" request.
The designed S1 critique turned a one-line `repo-python` scripts fix into a
manifest-wide idiom reconciliation once the sibling-scan ran. This retro also
durably records the #328-session waste the operator asked to reflect on.

## Evidence Summary

- `.agents/surfaces.json`: `scripts/**/*.py` -> `scripts/*.py` (repo-python), plus
  reconciling every `<dir>/**/*.X` to `<dir>/*.X` (repo-markdown md patterns,
  derived paths). Enumeration confirms 0 broken `**/*.X` patterns remain.
- Key fact: all 237 tracked `scripts/*.py` are top-level, so the bare
  `scripts/**/*.py` matched zero of them; the whole repo-python verify set never
  ran at scripts closeout. Live sibling leak: `packaging/README.md` skipped the
  markdown closeout checks.
- 2 regression guards added; `test_surface_obligations.py` 32 passed; broad pytest
  2375 passed, 4 skipped; fresh-eye reviewer SHIP.

## Waste

- **Boundary-ratchet false-green on an untracked file.** Ran
  `check_boundary_bypass_ratchet` standalone (rc=0, "clean"), then `git add -A` +
  predict-commit failed it — the ratchet scans `git ls-files`, and my new test was
  untracked at the standalone run. One convert-to-in-process round-trip. Same
  class as recent-lessons' `--head-sha HEAD`-while-parent false-green.
- **Issue-closeout commit body schema learned after committing.** First #328
  commit was prose -> `verify-closeout` failed (missing jtbd/boundary/.../critique
  binding) -> schema spelunking + amend.
- Minor: a surfaces.json Edit missed a trailing-comma context and had to retry.

## Critical Decisions

- **Option A (`scripts/*.py`), not Option B (a recursive-`**` matcher).** fnmatch
  `*` already crosses `/`, so `scripts/*.py` is a strict superset; a "proper glob"
  matcher would NARROW the many patterns that rely on `*` crossing `/` and break
  matches. B was the wrong direction.
- **Fix the idiom class, not just scripts.** The sibling-scan found a live leak
  (packaging/README.md) plus latent traps; reconciled all of them rather than ship
  a knowingly-partial "idiom fixed" claim.

## Expert Counterfactuals

- A "fix the class, not the instance" lens (the retro sibling-scan discipline,
  echoed by the fresh-eye reviewer): without enumerating every `<dir>/**/*.X`
  pattern, the scripts fix would have shipped while `packaging/README.md` kept
  silently escaping the markdown closeout gate — the exact latent-debt class #331
  is about, recurring one surface over.

## Sibling Search

- axis: surface-pattern idiom hygiene | location: scripts/validate_surfaces.py (no lint for the broken `<dir>/**/*.X`-without-sibling idiom) | decision: valid follow-up outside the slice | proof: the idiom recurred (scripts then packaging) and only a manual sibling-scan caught it; nothing but two path-specific regression guards prevents reintroduction | follow-up: deferred handoff-surface-idiom-lint

## Next Improvements

- workflow: stage tracked files (`git add`) before running tracked-file-scanning
  gates (boundary-ratchet scans `git ls-files`); a standalone run over an
  untracked working tree gives a false green. Disposition: memory -> recent-lessons
  digest refreshed this session (source: this retro).
- workflow: for an issue closeout, write the structured closeout body and run
  `verify-closeout` as a draft (no `--expect-state`) BEFORE committing, so the
  jtbd/boundary/.../Critique schema does not force an amend. Disposition: memory
  -> recent-lessons digest refreshed this session (source: this retro).
- capability: a `validate_surfaces` lint that flags any `<dir>/**/*.X` source
  pattern lacking a `<dir>/*.X` sibling, so the idiom footgun cannot return.
  Disposition: deferred -> handoff Next Session candidate (anchor
  surface-idiom-lint), not filed, to avoid issue sprawl for a small hardening.

## Persisted

yes: charness-artifacts/retro/2026-06-07-issue-331-closeout-fnmatch-idiom.md
