# Charness 5.2.0 Release Critique

Date: 2026-08-13

## Decision Under Review

Publish the compatible minor release `v5.2.0` after pushing the direct issue
carriers for #614, #615, and #616. The decision includes the reader-facing
upgrade, migration, proof-limit, and tracker-boundary claims; it does not treat a
local green gate as publication or issue closure.

## Failure Angles

- An operator could read `charness update` as a repository-state migration or as
  authorization to apply lesson or contract transitions.
- A recorder whose successful run writes immediately could be mistaken for the
  migration and transition commands that preview by default.
- An optimistic rollback sentence could suggest that reinstalling an older
  plugin reverses append-only repo state.
- Release notes could claim hosted issue closure or installed-host/provider proof
  before distinct-channel readback exists.
- A patch bump would understate the additive lifecycle and operator surface,
  while a major bump would overstate compatibility impact.
- Release automation could tag stale version surfaces unless the repo-owned
  helper bumps and verifies all public copies before publication.

## Counterweight Pass

- Real-host proof is not required merely to make the local release delta look
  stronger. The configured trigger evaluated the delta and did not match; the
  notes state this as a scope result, not as host proof.
- The release notes should not enumerate every changed script, fixture, or lint
  rule. They need reader decisions, upgrade steps, state effects, and proof
  limits; implementation detail remains in the version-pinned development guide.
- A supported version-pinned rollback flow would be useful, but its absence is
  disclosed and is not a blocker for a compatible minor release.
- Adding preview modes to the immediate append-only recorders is a legitimate
  future safety improvement. The current commands validate the full candidate
  before writing and now disclose their immediate-write behavior.

## Release Scope

- `v5.2.0` is a minor release: it adds bounded evidence-retention behavior,
  focused/broad coverage consistency, lesson lifecycle history, contract
  graduation/retirement history, and handoff/retro continuity surfaces without
  declaring an incompatible public break.
- The release carries the direct local fixes for #614 and #615 and the additive
  lifecycle capability for #616.
- Issue state remains owned by GitHub. The notes require carrier push followed by
  tracker readback before any `CLOSED` claim.
- Publication state remains owned by the GitHub tag/release and public install
  surfaces, not by the local release commit.

## Surface-Lock Inventory

- `docs/development.md` owns the exact local authoring commands and now
  distinguishes migration preview, immediate lifecycle/proposal append, and
  contract-transition preview/execute behavior.
- `charness-artifacts/release/2026-08-13-v5.2.0-notes.md` owns the reader-facing
  highlights, upgrade/restart/doctor path, migration and rollback limits,
  non-authorization statements, proof limits, and issue-closure boundary.
- `skills/public/release/scripts/publish_release.py` remains the publication
  owner. The release must use its dry run and execute/resume lanes so version
  surfaces, commit, tag, push, hosted release, and readback stay one checked
  contract.
- No live lesson lifecycle or contract-membership transition is part of the
  release preparation.

## Operator Action Required

Before publication, run the repo-owned release helper in dry-run mode, inspect
the structured receipt, then execute only the same reviewed `minor` plan and
notes. After publication, refresh the installed plugin with `charness update`,
restart the host, and read back version and doctor state. If update or drift
recovery fails, follow the doctor's `next_action` and repeat update/restart.

## Upgrade Path

The reader-facing path is `charness update`, host restart, then `charness doctor`
for any failure or remaining drift. There is no supported version-pinned rollback
for this release, and reinstalling an older plugin does not undo repo-local ledger
migrations or append-only events. Consumer-repo migrations remain explicit,
preview-first commands and are not run by plugin update.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: initial Gawande/Raskin release review | action: fix | note: distinguish preview-first migrations and transitions from immediate lifecycle/proposal appenders; development guidance and release notes now do so.
- F2 | bin: act-before-ship | evidence: strong | ref: initial Minto/Jackson release review | action: fix | note: add a reader-first update/restart/doctor path and state the unsupported rollback boundary; the repaired release notes carry both.
- F3 | bin: act-before-ship | evidence: strong | ref: initial release counterweight | action: fix | note: refuse local commit or release-record evidence as proof of issue closure, hosted publication, or installed-host behavior; the notes now name each proof boundary.
- F4 | bin: act-before-ship | evidence: strong | ref: release helper contract | action: fix | note: publish only through the repo-owned helper so the minor bump and generated/public version parity precede tag creation.
- F5 | bin: bundle-anyway | evidence: strong | ref: docs/development.md | action: document | note: recorders append immediately after full validation while migration and transition commands preview; the operator guide now makes the distinction adjacent to the commands.
- F6 | bin: over-worry | evidence: moderate | ref: real-host trigger report | action: defer | note: no trigger matched this delta, so demanding installed-host proof before publication would widen the declared release floor without an owning trigger.
- F7 | bin: valid-but-defer | evidence: moderate | ref: repaired-surface reviewer | action: defer | note: a supported version-pinned rollback flow and preview modes for immediate recorders would improve recovery, but the present limitations are explicit and do not block this compatible minor.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye reviewers.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`, plus read-only bounded
  scopes. The repaired-surface follow-up inherited the active host model because
  that spawn surface did not expose a typed reviewer role.
- Host exposure state: requested_fields_sent
- Application state: unverified; the host accepted the fields but did not confirm
  which model, effort, or service tier it applied.
- Delivery state: findings-received
- Review shape: three independent initial lenses (operational first-use,
  public narrative, and counterweight), followed by one separate reviewer reading
  the repaired documentation surface.
- Boundary proof: the repaired-surface window `v5-2-0-release-final` verified
  `clean` with no parent-declared path, staged, or HEAD movement.

## Fresh-Eye Satisfaction

parent-delegated — four bounded reviews returned substantive findings in
separate agent contexts.

The final reviewer consumed the repaired-surface packet, independently verified
its binding as current, made no worktree or index change, and reported no
remaining act-before-ship or bundle-anyway item.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-13-v5-2-0-release-final-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-13-v5-2-0-release-final-packet.json`
- Packet SHA256: `eb8b5c8a5b998c8e162496a34a5ea918128f2955478869472460f5a0ad4a05e5`
- Identity SHA256: `c0ca65dfcbb569f0129f2075b2c7b536b6e5de36f05f077860775c23b7cb2220`
- Packet Markdown SHA256: `a7a088d2c147290b18d5d5e22aed943f432b30b1737f474110736f891a0aeeb5`

## Boundary Ownership

- Producer: development guidance, release notes, the release planner, and the
  repo-owned publish helper produce the claims and state transitions reviewed
  here.
- Consumer: maintainers upgrading the installed plugin, consumer repositories
  deciding whether to migrate state, and GitHub readers deciding whether a
  release or issue is actually published/closed.
- Owning surface: command semantics stay beside their development commands;
  reader decisions stay in release notes; version/tag/release mutations stay in
  the publish helper; hosted state stays in GitHub readback.
- Verdict: owned-correctly

## Deliberately Not Doing

- Do not claim or manufacture real-host/provider proof when the configured
  trigger did not match.
- Do not add a new dry-run mode to the immediate append-only recorders inside
  this release boundary.
- Do not enumerate every implementation file, test, or `PLR2004` exception in
  reader-facing release notes.
- Do not close issues or declare the release published from local evidence.

## Next Move

Validate and commit this release surface, push the direct carriers, read back the
remote branch and issue states, then run the release helper dry-run and execute
the reviewed `5.2.0` publication plan. Close with public release/install readback
and a reconciled handoff.
