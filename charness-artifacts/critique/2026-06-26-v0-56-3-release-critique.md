# Critique Review
Date: 2026-06-26
Packet consumed: charness-artifacts/critique/2026-06-26-054254-packet.md

## Decision Under Review

Publish the current Charness quality/speed/token-efficiency bundle as patch
release v0.56.3 after final goal closeout, broad proof, release-helper
mutation, public verification, and install refresh.

## Release Scope

- Current version: 0.56.2.
- Target version: 0.56.3.
- Bump rationale: patch. The release contains bug fixes, validation repairs,
  script/test speedups, and compatible control-surface refinements; it does not
  remove public skills, rename package ids, or require a migration.
- Operator story: faster quality/release gates and safer closeout helpers with
  the same update path. Run `charness update`; no data migration is expected.

## Surface-Lock Inventory

The prepare packet only reported the clean working tree, so this critique uses
the release range as the surface inventory:

- Range: `origin/main` 61093b75 through HEAD 6458fcde.
- Scope: 35 commits, 87 changed files, 4143 insertions, 2519 deletions.
- Generated/export surfaces: `plugins/charness/**`, `.claude-plugin`, and
  checked-in plugin mirrors for root scripts and public/support skill helpers.
- Consumer-visible behavior: `charness update all` reuses precomputed support
  sync results; `run_evals.py` defaults to bounded scenario parallelism with
  `--jobs 1` preserving the old sequential path; the standing `specdown` gate
  runs with `-jobs 4`; startup, Cautilus, and generic script timeout helpers
  accept positive fractional seconds while preserving integer-compatible use.
- Validation and release behavior: closeout helper tests were narrowed, Cautilus
  timeout tests avoid fixed sleeps, changed-line mutation coverage remains a
  final closeout producer obligation, and release helper proof must still run
  fresh-checkout probes for v0.56.3.
- Documentation/artifacts: the goal artifact records 31 slices; release notes
  must compress them into operator-readable bullets rather than a slice table.

## Failure Angles

- Gawande operational/checklist: publish would be premature while the goal is
  active, versions remain 0.56.2, release ledger still names v0.56.2, and
  fresh-checkout probes are configured but not yet run for v0.56.3.
- Minto communication: a release note copied from the slice log would bury the
  operator story; the consumed packet also under-described the release range by
  looking only at the clean working tree.
- Raskin operator-upgrade: the release should name the few user-visible controls
  (`--jobs`, fractional timeouts, `charness update`) and avoid implying a
  migration or new manual proof burden.

## Counterweight Pass

- Act Before Ship: do not let the clean-tree prepare packet stand alone. The
  release artifact and notes must include the range-aware surface inventory
  above.
- Act Before Ship: complete final goal verification, then run the release helper
  for patch v0.56.3 through bump, sync, verification, publish, public readback,
  fresh-checkout probes, and install refresh.
- Bundle Anyway: include concise release-note bullets for the compatible
  operator-visible changes and the update path.
- Valid but Defer: requested-review enforcement is advisory-only; record this
  non-claim instead of inventing a new release gate now.
- Valid but Defer: `charness update all` progress wording can later say
  sync/reuse if operators report confusion.
- Over-Worry: do not block v0.56.3 on an exhaustive per-slice timing table or
  extra fractional-timeout docs.

## Operator Action Required

- Before publish: fill goal final verification, run final broad proof and
  changed-line mutation coverage producer, and complete the retro/disposition
  floors.
- During publish: use the release helper with patch target v0.56.3 and a
  critique artifact path pointing to this file.
- Release notes: lead with faster quality/release gates, compatible behavior,
  no migration, and `charness update`; mention `run_evals.py --jobs`, standing
  `specdown -jobs 4`, and fractional timeout support.

## Upgrade Path

Operators should run `charness update` after the release is public. Active
Claude/Codex sessions may need a restart to pick up refreshed plugin/cache
state. No data migration or rollback procedure is required by this release
scope.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-06-26-054254-packet.md:27 | action: fix | note: Release prepare packet reported a clean working tree, so the release artifact must include origin/main..HEAD surface inventory before publish.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-2.md:3 | action: fix | note: Goal closeout and final verification remain open; complete them before release publication.
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/latest.md:6 | action: fix | note: Release ledger still proves v0.56.2; v0.56.3 must be produced and verified by the release helper.
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/check_fresh_checkout_probes.py | action: fix | note: Fresh-checkout probes are configured but not yet run for v0.56.3.
- F5 | bin: bundle-anyway | evidence: strong | ref: scripts/run_evals.py:440 | action: document | note: Release notes should mention compatible bounded eval parallelism, specdown jobs, fractional timeouts, no migration, and the update command.
- F6 | bin: valid-but-defer | evidence: strong | ref: .agents/release-adapter.yaml | action: defer | note: Requested-review commands are not configured; record advisory-only enforcement as a non-claim rather than adding a gate in this patch.
- F7 | bin: valid-but-defer | evidence: moderate | ref: charness:2817 | action: defer | note: update-all progress wording can later distinguish syncing from reusing support surfaces if operator confusion appears.
- F8 | bin: over-worry | evidence: moderate | ref: charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-2.md:870 | action: document | note: Do not add an exhaustive timing appendix; concise representative release notes are enough.

## Reviewer Tier Evidence

- Requested tier: high-leverage release critique reviewers.
- Requested spawn fields: host-defaulted; no provider model fields were forced by the parent.
- Host exposure state: host-defaulted
- Application state: host returned parent-delegated reviewer agents Beauvoir, Cicero, Curie, and Euler; no provider-side model-application metadata was exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Deliberately Not Doing

- No exhaustive timing table in release notes.
- No new requested-review enforcement gate in this patch.
- No extra fractional-timeout documentation beyond concise release-note mention.
