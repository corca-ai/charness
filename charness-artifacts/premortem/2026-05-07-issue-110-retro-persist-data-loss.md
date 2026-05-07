# Premortem: Issue #110 Retro Persist Data Loss

Date: 2026-05-07

## Decision

Close GitHub issue #110 with a compact repo slice that fixes the silent
overwrite of `recent-lessons.md` in `persist_retro_artifact`:

- normalize `--artifact-name` so a missing `.md` is auto-appended; emit a
  stderr notice and an `artifact_name_normalized: true` flag in the JSON result
- guard the summary refresh: when lesson selection yields zero candidates and
  the existing `summary_path` is non-empty and is not the empty-stub digest,
  preserve the file and return `summary_skipped_reason:
  no_candidates_existing_summary_protected`
- expose `--force-empty-summary` on the CLI as the explicit opt-in to write the
  empty-stub digest anyway
- add a SKILL.md note for the legacy hand-curated summary case so a first
  retro after legacy adoption does not surprise an operator

## Likely Misread

A future operator could misread the new behavior as "summary refresh stopped
working" when the input markdown does not yield extractable lessons (no
`Context`/`Waste`/`Next Improvements` sections). The guard returns exit code 0
with a stderr warning, and the JSON result names the protection reason; the
operator must still understand that the markdown shape, not the helper, caused
the empty index. Mitigation: structured `summary_skipped_reason` and the
SKILL.md migration note both name the legacy-summary case explicitly, and
`--force-empty-summary` is the named escape hatch.

## Counterweight Triage

Act Before Ship:

- Use a stub-signature check, not just emptiness, so a real stub digest can
  still be replaced and a hand-curated summary stays protected.
- Sync `plugins/charness/` mirrors before validators so packaging and lint
  gates see the new helper symbols.
- Emit normalization and protection signals on stderr and in the JSON result
  so callers can detect both states without reading the file.

Bundle Anyway:

- Add three regression tests covering: artifact-name normalization,
  legacy-summary preservation on zero-candidate refresh, and
  `--force-empty-summary` opt-in.
- Update `skills/public/retro/SKILL.md` with the legacy migration note in the
  same slice as the helper change, since the helper change is the reason the
  note becomes accurate.

Over-Worry:

- Do not turn the guard into a global "never overwrite non-empty markdown"
  rule; it stays scoped to the zero-candidate refresh path.
- Do not require the operator to bump a config flag to keep current behavior;
  the guard is a default-on safety net.
- Do not refactor `recent_lessons_lib.build_indexed_recent_lessons` for this
  slice; only the persistence wrapper needs to change.

Valid But Defer:

- A full inventory of other helper scripts that could overwrite hand-curated
  artifacts can wait until a similar incident report arrives; this slice only
  closes the named retro path.
- Adding a structured "legacy migration" doctor command can follow if more
  repos report the same first-run surprise.

## Fresh-Eye Satisfaction

parent-delegated

This is a small local-risk slice (data-loss safety net plus SKILL.md note);
deterministic validators and the new regression tests cover the behavior
contract. No bounded reviewer subagent was spawned because the slice does not
change prompt-affecting surfaces or public-skill ergonomics beyond the one
documented note, and Cautilus stays `disabled` by repo adapter.

## Scenario Review

Consumer prompt:

> Run a retrospective and persist it. The repo had a hand-curated
> `recent-lessons.md` from before the retro skill existed.

Expected result:

- `persist_retro_artifact.py` writes the new artifact under `output_dir`
  with a `.md` extension even if the operator forgot it
- when extraction returns zero candidates, the existing hand-curated summary
  is preserved and the JSON result records
  `summary_skipped_reason: no_candidates_existing_summary_protected`
- a stderr warning surfaces both the normalization and the protection events
- `--force-empty-summary` remains the only path that writes the empty-stub
  digest into a non-stub existing summary

Observed decision:

- `tests/quality_gates/test_retro_persistence.py` extends the suite with three
  cases that lock in the contract above; all 5 retro persistence tests pass.
- `skills/public/retro/SKILL.md` step 5 names the legacy hand-curated case so
  the next operator does not need to rediscover the safety net.
- Cautilus remained disabled by repo adapter; deterministic validators and
  this scenario review are the accepted proof for this slice.
