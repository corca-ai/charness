# v1.0.5 Release Critique
Date: 2026-07-14

## Decision Under Review

Publish patch release v1.0.5 after advisory disposition, Cautilus 0.19.3
compatibility repair, test-matrix organization, and issue-resolution proof.

## Release Scope

- Version: 1.0.5
- Tag: `v1.0.5`
- Consumer change: parsed Cautilus commands select JSON explicitly; validation
  fixtures and test organization match the supported integration contract.
- No public CLI, skill trigger, persisted-state, or migration change.

## Execution

Two high-leverage angle reviewers ran read-only with distinct lenses, followed
by a separate high-leverage counterweight. Parent fingerprint verification
reported no worktree, index, untracked-path, or HEAD drift after every review.

## Packet Consumed

`charness-artifacts/critique/2026-07-13-225535-packet.md`

## Failure Angles

- Gawande operational sequencing: sync, external-tool ownership, mutation proof
  scope, commit/release gate order, publish readback, install refresh, rollback.
- Minto plus Raskin operator communication: release-note hierarchy, attribution,
  update/restart/rollback action, and evidence non-claims.
- Counterweight: distinguish a real publication blocker from expected pre-bump
  state and wording improvements.

## Surface-Lock Inventory

- Version and install surfaces: `packaging/charness.json`, Claude/Codex plugin
  manifests, marketplace manifests, tag, and GitHub release.
- Generated copies: the three synced plugin script/exemption mirrors.
- Integration behavior: two Cautilus parsing subprocess command shapes and the
  proposal evidence fixture.
- Proof surfaces: split test matrices, boundary exemptions, debug/spec/quality
  artifacts, and these release notes.
- Operator surface: `charness update`, session restart, and rollback to tag
  `v1.0.4` through the existing install method.

## Findings

- Version manifests remaining at 1.0.4 are expected candidate state, but the
  release cannot be called complete until the repo helper stamps/syncs 1.0.5,
  runs its release gate and fresh-checkout probes, publishes, and reads back the
  public release through a distinct channel.
- The original notes could imply v1.0.5 authored earlier issue fixes. The intro
  now attributes this patch to advisory cleanup and compatibility around the
  closeout, preserving the landed-commit boundary.
- Rollback now names tag `v1.0.4`, the existing install method, and host restart.
- The 81-gate read-only result is pre-release proof, not release-gate proof.
- Provider mutation run 29289933683 passed on `c6a1e828` at 89.0% Python and
  93.0% JavaScript. It is intentionally not release-HEAD proof.
- Cautilus compatibility is correctly owned: both JSON-parsing subprocesses
  request `--json`, tests assert the shape, and no evaluation claim is made.

## Counterweight Pass

- Act Before Ship: helper-owned version stamp, release gate, fresh-checkout
  probes, public creation/readback, and install refresh must execute before the
  release-complete claim.
- Bundle Anyway: tighten issue-fix attribution and rollback wording in the notes;
  both edits are included.
- Over-Worry: do not require the provider mutation workflow to run again on the
  notes/test-organization commit; committed-HEAD local gates own that proof.
- Valid but Defer: decompose the two near-limit production validators only with
  behavior-led characterization work, not for line-count compliance in release.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: packaging/charness.json | action: fix | note: use the release helper to stamp, sync, gate, publish, and read back v1.0.5 before completion claim
- F2 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-07-14-v1.0.5-notes.md | action: fix | note: completed edit distinguishes advisory packaging from earlier production fixes
- F3 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/release/2026-07-14-v1.0.5-notes.md | action: fix | note: completed edit names rollback tag, install method, and restart
- F4 | bin: over-worry | evidence: strong | ref: https://github.com/corca-ai/charness/actions/runs/29289933683 | action: document | note: successful provider proof stays scoped to c6a1e828
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/2026-07-14-quality-review.md | action: defer | note: refactor warned production validators only alongside behavior work

## Operator Action Required

1. Commit the candidate, then rerun committed-HEAD mutation/closeout proof.
2. Run the release helper dry-run and execute path for patch version 1.0.5.
3. Confirm the public tag/release through a distinct observer and refresh the
   maintainer install with `charness update`.
4. Restart active host sessions; use tag `v1.0.4` through the existing install
   method and restart again if rollback is needed.

## Upgrade Path

Run `charness update`, then restart Claude Code or Codex. No data migration is
required. Rollback uses tag `v1.0.4` through the same install method.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`,
  `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden; accepted fields do not prove provider use.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: Cautilus CLI schema/serialization and repository release helper.
- Consumer: parsing adapters, plugin/install manifests, and operators.
- Owning surface: adapters select JSON, tests guard command shape, helper owns
  version/publication state, and release artifact owns verified readback.
- Verdict: owned-correctly

## Deliberately Not Doing

- No Cautilus evaluation, public API change, migration, or provider mutation
  claim for the uncommitted release-cleanup diff.
- No line-count-only refactor of cohesive or high-risk production modules.

## Next Move

Validate this critique, commit the candidate, obtain committed-HEAD closeout
proof, then run the release helper and separately observe the public result.
