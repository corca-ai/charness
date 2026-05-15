# Session Retro: Mutation Testing Cosmic Ray Migration

## Context

This session picked up the handoff item to remove mutmut from the Charness
mutation-testing workflow and migrate the repo dogfood path to Cosmic Ray.
The work touched checked-in plugin exports, integration/control-plane adjacent
scripts, quality references, workflow configuration, and closeout surfaces.

## Evidence Summary

- `docs/handoff.md` named the mutmut 3.x subprocess-trampoline limit and the
  Cosmic Ray pivot.
- Fresh-eye critique packet:
  `charness-artifacts/critique/2026-05-15-101818-packet.md`.
- Closeout ran `run_slice_closeout.py --ack-cautilus-skill-review` and the
  full planned pytest gate.

## Waste

- The first pass treated Cosmic Ray dry-run as if the normal summary step could
  still run. Fresh-eye review caught that dry-run creates no dump, so PR mode
  would have failed after a successful baseline/init.
- A local `.artifacts/cosmic-ray-venv` created for proof leaked into repo-wide
  Python filename scans until it was removed. The verification environment was
  useful, but it should have been outside the repo or cleaned before broad
  gates.
- `run_slice_closeout.py` initially blocked because the workflow, Cosmic Ray
  config, and critique packet had no declared surface. The fix was useful but
  should have been obvious when adding a new workflow/config family.

## Critical Decisions

- Move mutmut configuration out completely instead of trying to preserve a
  dual-runner setup.
- Keep the public `quality` mutation-testing contract runner-neutral while
  documenting Cosmic Ray as Charness repo dogfood support.
- Leave `commands.sample` disabled for the first Cosmic Ray run because
  full-suite baseline cost was too high for a per-mutant command; keep the
  sampler helper as future support.
- Add a dedicated `mutation-testing-workflow` surface so future workflow/config
  edits carry explicit sync and verification obligations.

## Expert Counterfactuals

- A Gary Klein premortem would have asked "how does the PR path fail after the
  happy-path dry-run?" before implementation, surfacing the missing dump/summary
  mismatch without waiting for reviewer feedback.
- A Nicole Forsgren-style operability lens would have separated local proof
  tooling from repo-scanned source earlier, avoiding the `.artifacts` venv leak
  into broad gates.

## Next Improvements

- workflow: For workflow migrations with mode branches, add one test that pins
  each mode's artifact assumptions before running closeout.
- capability: Keep new workflow/config families in `.agents/surfaces.json` in
  the same slice that introduces them.
- memory: Preserve the mutmut structural limit as historical dogfood evidence,
  but make new handoff state point to first-run Cosmic Ray observation rather
  than re-debating the pivot.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`
