# Critique Review
Date: 2026-06-26

## Decision Under Review

Publish the current Charness sustained quality round-3 bundle as patch release
v0.56.4 after final closeout evidence, broad proof, fresh-eye review, release
helper mutation, public verification, and install refresh.

## Release Scope

- Current version: 0.56.3.
- Target version: 0.56.4.
- Bump rationale: patch. The release contains compatible test/runtime
  validation speedups and closeout evidence improvements. It does not rename
  public skills, change package ids, remove install surfaces, or require a
  migration.
- Operator story: faster local tests and cleaner release/goal closeout evidence
  with the same update path. Run `charness update`; no data migration is
  expected.

## Surface-Lock Inventory

- Range under review: `v0.56.3..HEAD` before publish.
- Main code surface: shared loaded-script runner in `tests/script_main.py`.
- Test surfaces: control-plane, quality-gate, scaffold, packaging, setup,
  agent-browser, mutation, and skill-output schema tests converted away from
  incidental Python subprocess startup.
- Artifact surfaces: round-3 goal, host probe JSON, retro, disposition review,
  recent-lessons digest, and release notes.
- Deliberate non-conversions: generated/exported command execution, web-fetch
  browser cleanup, Cautilus eval commands, release-host proof, and committed
  packaging checks remain process-backed.

## Failure Angles

- Gawande operational/checklist: publishing before the release helper runs would
  leave the round-3 goal active, release proof stuck on v0.56.3, and the branch
  ahead of origin.
- Minto communication: a release note framed as dozens of slices would hide the
  simple operator story: faster tests, same update path, no migration.
- Raskin operator-upgrade: converting subprocess tests in process must not
  imply public command behavior changed; the notes must say test helper only.
- Jackson problem framing: not every remaining subprocess candidate is waste;
  some are the behavior under test and should remain as boundary proof.

## Counterweight Pass

- Act Before Ship: run the release helper for patch v0.56.4 so the current HEAD
  is covered by a new release artifact, tag, push, public verification, and
  install refresh.
- Act Before Ship: preserve the fresh-eye finding as release-boundary evidence;
  it correctly identifies the pre-publish state as incomplete.
- Bundle Anyway: include release notes that call out the shared test helper,
  boundary inventory reduction, and deliberate remaining process boundaries.
- Valid but Defer: do not add a new hard gate for every clean-convertible
  candidate; the boundary inventory remains advisory where judgment is needed.
- Over-Worry: do not block release on converting Cautilus/web-fetch/release-host
  subprocesses because those are intentionally process-boundary-shaped.

## Fresh-Eye Review

Fresh-eye reviewer `Galileo` performed a read-only release closeout review. The
review found no code/test blocker in `tests/script_main.py` or the sampled
converted tests, but correctly identified two release blockers before publish:
current HEAD was not yet covered by a release artifact, and the round-3 goal was
still active/pending release proof. This critique treats both as act-before-ship
release-helper obligations.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/latest.md:6 | action: fix | note: v0.56.3 release proof does not cover current HEAD; publish v0.56.4 through the release helper.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-3.md:3 | action: fix | note: goal remains active until v0.56.4 release proof is recorded and the goal is marked complete.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/script_main.py:10 | action: document | note: release notes should describe the shared test helper as test-surface-only and not a public runtime change.
- F4 | bin: valid-but-defer | evidence: strong | ref: scripts/inventory_boundary_bypass.py | action: defer | note: leave remaining process-boundary candidates advisory where subprocess behavior is the point of the test.
- F5 | bin: over-worry | evidence: moderate | ref: tests/test_web_fetch_cleanup.py | action: document | note: do not convert browser cleanup and generated command subprocesses merely to improve inventory counts.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye release closeout review.
- Requested spawn fields: agent_type=explorer; model/reasoning/service tier inherited from parent and not forced.
- Host exposure state: applied
- Application state: host-confirmed: spawn_agent returned reviewer id
  `019f0445-ffd1-78f1-815d-b8c26298847e`; `wait_agent` returned completed
  findings before release execution.

## Fresh-Eye Satisfaction

parent-delegated

## Deliberately Not Doing

- No exhaustive per-slice timing appendix in release notes.
- No conversion of subprocess tests where process isolation is the behavior
  under test.
- No migration or rollback instructions beyond the standard `charness update`
  path because the release is compatible.
