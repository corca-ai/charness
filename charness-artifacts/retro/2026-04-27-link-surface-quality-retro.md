# Session Retro: Link Surface And CLI Skill Quality

## Mode

session

## Context

This work implemented the pre-Cautilus-upgrade slice for GitHub issues #74,
#73, and #75: portable skill markdown safety, missing inline-code path
detection, and CLI plus bundled-skill quality drift detection.

## Evidence Summary

- Changed surfaces from `run_slice_closeout.py`: checked-in plugin export,
  repo markdown, and repo Python.
- Verification: `./scripts/run-quality.sh` passed with 47 checks and 0
  failures in 42.5s.
- Local proof also included targeted pytest for doc links, backtick migration,
  and CLI skill surface checks.

## Waste

- The first missing-path implementation caught intentional future-path wording
  in `docs/handoff.md` and a glob-like token in `docs/harness-composition.md`.
  That was useful pressure, but it showed the detector needed to distinguish
  actual path references from planned artifact names and glob patterns.
- The first portable-link boundary was too strict for checked-in skill-to-skill
  references, so it had to be narrowed to block repo-doc escapes without
  rejecting links under `skills/`.

## Critical Decisions

- Keep `migrate_backtick_file_refs.py` from rewriting portable skill bodies at
  all. This is lower risk than trying to infer which portable references should
  become placeholders automatically.
- Let `check_doc_links.py` reject portable skill markdown links that escape to
  repo docs, while allowing package-local and `skills/` links.
- Make CLI plus skill drift detection report adapter weaknesses even when the
  standing gate remains passable.

## Expert Counterfactuals

- Kent Beck would have started with the smallest failing examples for
  placeholders, missing paths, and inferred CLI shape. That matched the final
  path and kept the patch bounded.
- John Ousterhout would have separated portable-surface classification from
  token classification earlier. Doing that sooner would have avoided the ruff
  complexity failure.

## Next Improvements

- workflow: For future lint expansion, run the new detector against the live
  repo before deciding the final error taxonomy.
- capability: Add small classification helpers before extending
  `check_doc_links.py` again; the function is a shared lint seam now.
- memory: Treat `migrate_backtick_file_refs.py --dry-run` output as a
  regression signal when changing markdown-link policy, but do not require a
  zero-output state while the migration helper still owns optional cleanups.

## Persisted

yes: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`
