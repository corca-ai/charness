# issue-328 preflight gate-phase coverage
Date: 2026-06-07

## Mode

session

## Context

Resolved #328 (cheap upstream pre-checks: prose-pin scan + authoring-preflight
prompt) and closed the gate-phase coverage gap under the
`2026-06-08-preflight-gate-phase-coverage` achieve goal. S1 triaged #327
(verdict: not re-pointed), S2-S4 landed the work, S5 was closeout.

## Evidence Summary

- New: `scripts/check_prose_pin.py` (advisory prose/path-pin pre-check, 0.5s on
  the full repo), `scripts/slice_closeout_advisories.py` (extracted closeout
  advisories). Edited: `check_skill_surface_preflight.py` (`--run-checks` now runs
  the full 6-gate portable-package set), `run_slice_closeout.py` (476 -> 457 code
  lines after extraction), `.agents/surfaces.json` (27 -> 28 surfaces, new
  `python-scan-hygiene`), `docs/conventions/authoring-preflight.md`.
- Tests added: `test_check_prose_pin.py` (4), `test_skill_surface_preflight.py`
  (+2), `test_surface_obligations.py` (+4 incl. boundary-ratchet + gitignore-scan
  + retro-index acceptance cases), `test_authoring_preflight_reference.py` (+1).
- Broad pytest at the bundle boundary: 2373 passed, 4 skipped. ruff / doc-links /
  markdown / attention-state / validate_surfaces / packaging / gitignore-scan /
  boundary-ratchet all clean.

## Waste

- My first advisory wiring pushed `run_slice_closeout.py` to 476/480 code lines (4
  left), forcing a mid-slice extraction. Mild rework — but the length advisory
  fired at slice time, which is exactly the catch-debt-at-slice-time behavior this
  goal builds, so it was cheap and self-demonstrating, not silent.
- The goal + handoff framed #328 as OPEN; it had actually been auto-closed by a
  stray `resolves #328` in the handoff commit body. Reconciling that (close-event
  + commit inspection) was a short detour before real work could start.

## Critical Decisions

- **Did not re-point to #327.** Triage verdict: mutation *score* passes
  consistently; the FAILs are the intermittent changed-line selection-budget
  signal on *scheduled* main runs only. Low-severity, non-blocking; primary kept.
- **Dedicated `python-scan-hygiene` surface, not a repo-python fnmatch fix.** The
  scoped surface closes the gitignore-scan gap for top-level/nested/skill scripts
  without the broad-pytest closeout-cost blast radius of widening repo-python;
  the broader fix was filed as #331.
- **Reopened #328 honestly** rather than landing work under a falsely-closed
  issue, then closed it via the carrier commit.

## Expert Counterfactuals

- A "read the matcher before trusting it" lens (Hyrum / least-surprise):
  `surfaces_lib.path_matches_patterns` uses `fnmatch`, which is NOT recursive, so
  `scripts/**/*.py` silently does not match top-level `scripts/<file>.py`. Had I
  trusted the natural assumption "repo-python covers all repo Python" and wired
  gitignore-scan there, the gate would have shipped latent for the most common
  script class — the exact debt this goal targets. An empirical
  `check_changed_surfaces` probe (not assumption) surfaced it before it bit.

## Sibling Search

- axis: gate-phase coverage | location: repo-python surface verify set (boundary-ratchet, ruff, lengths, attention-state, broad-pytest) | decision: valid follow-up outside the slice | proof: `check_changed_surfaces --paths scripts/rca_link_advisory.py` matches only checked-in-plugin-export, not repo-python | follow-up: https://github.com/corca-ai/charness/issues/331

## Next Improvements

- workflow: At task start, verify the target issue's real state (open/closed +
  last close event) before trusting the goal/handoff "open" framing. Disposition:
  memory -> recorded in this retro + recent-lessons digest refresh this session.
- capability: broaden slice-closeout coverage to top-level scripts (the
  repo-python fnmatch gap). Disposition: issue -> filed as #331 with the decision
  framing (source-path widening vs recursive `**`, needs a closeout-cost critique).
- memory: the non-recursive-fnmatch surface-matching quirk is a repeat trap for
  anyone wiring a gate into a surface. Disposition: memory -> recent-lessons digest
  refresh this session (source: this retro).

## Persisted

yes: charness-artifacts/retro/2026-06-07-issue-328-preflight-gate-phase-coverage.md
