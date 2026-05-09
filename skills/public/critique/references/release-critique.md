# Release Critique

Critique a pending release before the tag, plugin manifest, install
artifact, or operator update instruction locks in. The substrate
(multi-angle review with one counterweight pass and four-bin triage) is
shared with other `critique` targets; this reference shapes the angle
distribution and output for *release lock-in*.

## When This Lens Fires

Pick this reference when the pending change is a release surface that is
about to commit. Trigger phrases:

- `release critique`, `release premortem`, `pre-release review`
- before cutting a tag, bumping plugin version, regenerating install
  manifests, or sending operator update instructions
- before posting release notes or announcement digest
- when the release scope locks user-visible surface that consumers will
  upgrade onto

If the release artifact does not yet exist (only a decision about whether
to release, or a spec draft), route to `premortem-decision.md` or
`spec-critique.md`.

## Anchor Angle Distribution

For release lock-in, the anchor weighting emphasizes operator surface and
external readability:

- **Atul Gawande (checklist / operational)** — strong default. What
  release-time step is missing? Did the manifest sync run before the tag?
  Did doctor pass on a clean clone? Did the install artifact land on at
  least one fresh host?
- **Barbara Minto (structure / communication)** — strong default. Are the
  release notes legible to an operator who did not follow the develop
  thread? Does the announcement digest density match the reader's time
  budget?
- **Jef Raskin (humane interface)** — strong when the release changes
  operator-facing surface: CLI help, doctor output, README Quick Start,
  install/update instruction, error message wording.
- **Michael Jackson (problem framing)** — moderate. Is the release framed
  by the user problem it solves, or by the internal slice that finished?
- **Gerald Weinberg (diagnostic)** — light. Useful when the release packs
  a fix and the question is whether the fix is at the right layer.

Default slate for a non-trivial release: Gawande + Minto + Raskin. Add
Jackson when the release narrative is hard to compress into a user-facing
story.

## Counterweight Bins

The four bins from `counterweight-triage.md` apply directly. Release-
specific tightening:

- **Act Before Ship** — concerns that require holding the release until
  fixed: a manifest sync gap, an install path regression, a doctor signal
  that fails on a clean checkout, a release-note line that misrepresents
  scope.
- **Bundle Anyway** — cheap fixes touchable in the same release: a
  doctored README first-touch line, a missing entry in the release notes,
  a follow-up issue that should be filed before the version is announced.
- **Over-Worry** — concerns about hypothetical install hosts, speculative
  consumers who have not been observed, aesthetic concerns about release
  note phrasing when the operator action is already clear.
- **Valid but Defer** — concerns that are real but belong in the next
  release: a deeper refactor of an upgrade path, a help-text rewrite, a
  follow-up announcement after the operator dogfood data lands.

## Surface-Lock Inventory

Every release critique records the user-facing surfaces this release locks.
Without this inventory the angle pass cannot triage which surfaces actually
moved. Inventory entries name:

- generated artifacts (CLI reference, plugin manifests, install manifests,
  bootstrap files)
- consumer-visible behavior (default flags, doctor exit codes, install
  prerequisites, prompt/skill semantics)
- documentation surfaces (README Quick Start, operator-acceptance, release
  notes, announcement digest)
- adapter or integration manifests that consumers may already have on disk

The inventory feeds the counterweight pass: a concern that names a surface
not in the inventory is suspect and triages toward `Over-Worry` unless the
reviewer can show the surface actually changed.

## Output Shape

In addition to the substrate `Output Shape` from `SKILL.md`, release
critique records:

- `Release Scope` — version, tag, and one line naming what changes for
  consumers
- `Surface-Lock Inventory` — the surfaces named above
- `Operator Action Required` — for each `Act Before Ship` concern, the
  concrete release-time step or release-note edit
- `Upgrade Path` — when the release changes consumer-visible behavior, the
  upgrade instruction or rollback path operators need
