# Session Retro: Install Tools Floor Cleanup

## Mode

session

## Context

This slice continued the quality ratchet after the per-file `80.0%` coverage
floor landed. The work targeted `install_tools.py` because it was still close
to the floor and carried duplicate lifecycle follow-up rendering already needed
by `doctor_lib.py`.

## Evidence Summary

- Changed files hit `checked-in-plugin-export` and
  `integrations-and-control-plane`, which triggered auto-retro.
- `./scripts/run-quality.sh --review` passed with `36 passed, 0 failed`, total
  `41.9s`.
- `check-coverage` reports `87.3%` aggregate control-plane coverage and
  `install_tools.py` at `84.2%`.

## Waste

The only notable waste was mechanical: the coverage trace helper exceeded the
repo length limit after adding scenarios, so the first full review failed late.
The failure was cheap to fix, but it shows coverage harness growth needs the
same production-surface discipline as the files it probes.

## Critical Decisions

- Moved `render_repo_followup` into `control_plane_lifecycle_lib.py` instead of
  keeping separate install and doctor implementations.
- Folded a one-use nonexecuting install wrapper back into `install_one`, reducing
  branch surface before adding trace scenarios.
- Kept the next target as `control_plane_lib.py`, now the weakest tracked file,
  rather than ratcheting floors immediately.

## Expert Counterfactuals

- John Ousterhout's complexity lens would have asked first whether a branch or
  helper could disappear before adding more test paths. That was the useful move
  for the one-use wrapper.
- Gary Klein's premortem lens points at the next likely failure: helper trace
  scenarios becoming a large hidden second implementation. Keep future coverage
  probes focused on branches that survive refactoring.

## Next Improvements

- workflow: check helper-file length before the full review when coverage trace
  scenarios grow.
- capability: continue using `run-slice-closeout.py` after plugin export changes;
  it caught all relevant surface obligations in one pass.
- memory: keep `control_plane_lib.py` as the next cleanup target in handoff and
  quality artifacts.

## Persisted

yes: `charness-artifacts/retro/2026-04-15-install-tools-floor-cleanup.md`
