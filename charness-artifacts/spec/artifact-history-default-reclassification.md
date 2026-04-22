# Artifact History-Default Reclassification

Date: 2026-04-22

## Scope

Reclassify `charness` artifact families so visible skill artifacts default to
dated history records, while rolling `latest.md` surfaces become explicit
exceptions instead of the assumed baseline.

This slice decides family semantics only. It does not yet migrate every writer
or choose whether a current pointer should be a plain file or a symlink.

## Decision

`charness` should treat visible skill artifacts as history-default unless the
repo can justify that a current pointer is materially clearer than a dated
record stream.

That means:

- `YYYY-MM-DD-<slug>.md` is the default checked-in visible artifact shape
- `latest.md` is an optional current pointer layered on top when operators need
  a rolling summary
- pointer mechanism is a separate implementation choice from family semantics

## Reclassification

### History-Default Families

- `debug`
  Why: incident reasoning, disproving observations, and seam risk are point-in-time.
- `gather`
  Why: collected evidence and source snapshots are often audit-relevant.
- `retro`
  Why: lessons are explicitly time-bound and should accumulate.
- `quality`
  Why: current posture is useful, but older reviews and gate decisions still matter.
- `release`
  Why: release closeout is an audit surface, not only a rolling status note.
- `announcement`
  Why: finalized human-facing change summaries are meaningful historical records.
- `narrative`
  Why: major story rewrites and aligned brief shifts should stay inspectable over time.
- `cautilus`
  Why: prompt-affecting proof is slice-specific evidence and should not disappear behind one rolling file.

### Current-Pointer Exceptions

- `find-skills`
  Why: startup inventory is high-frequency and the checked-in value is the current capability map, not a log of invocations.
- `hitl`
  Why: checked-in value is a live review surface, while queue/event detail already belongs in hidden runtime state.
- `init-repo`
  Why: the checked-in artifact is a current bootstrap summary rather than a durable sequence of audits.

### Fixed / Named-Artifact Exceptions

- `spec`
  Why: design contracts already live as named checked-in artifacts and do not need an adapter-managed rolling pointer by default.
- `docs/handoff.md`
  Why: it is the repo entry rolling pointer, not a skill-local artifact family.

## Current Drift Against The Decision

- Several writers still materialize `latest.md` as the canonical output even
  for families that should become history-default.
- Shared adapter helpers expose `record_artifact_pattern`, but many writers do
  not yet create dated records before or alongside the current pointer.
- Current policy prose makes `latest.md` sound more default than intended.

## Migration Order

1. Keep policy and skill references honest about history-default semantics.
2. Add a shared helper for `dated record + optional current pointer`.
3. Migrate history-default writers one family at a time, starting with:
   `release`, `announcement`, `cautilus`, `narrative`.
4. Decide separately whether pointer mode should support plain-file copy,
   symlink, or host-dependent choice.

## Non-Goals

- forcing every visible artifact family to keep a `latest.md`
- deciding the pointer implementation mechanism in this slice
- retrofitting noisy current-pointer exceptions into history streams without a
  concrete operator need
