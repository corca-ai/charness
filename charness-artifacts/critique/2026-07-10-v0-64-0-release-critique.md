# v0.64.0 Release Critique
Date: 2026-07-10

## Execution

- Independent release-operations and release-story reviewers plus one separate
  counterweight reviewed the locked bundle before any version/tag mutation.
- Packet Consumed: `charness-artifacts/critique/2026-07-10-release-0-64-0-packet.md`
- Target: `references/release-critique.md`

## Decision Under Review

Publish the locally locked main bundle as backward-compatible minor release
v0.64.0 through the repo-owned helper, then independently verify public and
installed surfaces.

## Release Scope

- version: `0.64.0`
- tag: `v0.64.0`
- consumer change: additive privacy-safe usage feedback plus correctness and
  measured operator-path speed/reliability improvements.
- version rationale: minor is correct for the new optional feedback capability;
  patch understates it and major is unsupported because compatibility is kept.

## Capability at Stake

Operators should receive truthful usage review, faster common CLI/gate paths,
and a release whose public/install proof cannot be inferred from local green.

## Angles

- Gawande inventoried version, export, fresh checkout, public readback,
  real-host, install refresh, rollback, and clean-worktree steps.
- Minto/Raskin/Jackson tested the user story, measured-claim boundary, upgrade
  path, minor-version choice, and zero-feedback non-claim.
- Counterweight rejected Cautilus, issue-close, real-feedback, and prose-polish
  requirements that do not belong to this release boundary.

## Surface-Lock Inventory

- version/plugin: packaging manifest, Claude/Codex plugin manifests, marketplace
  metadata, branch release commit, and Git tag;
- exported/runtime: checked-in plugin scripts/schemas/skill references, root CLI
  version/bootstrap behavior, and Markdown gate semantics;
- evidence: release notes/artifact, final quality/goal/critique records,
  fresh-checkout probes, GitHub release URL, and distinct-channel readback;
- installed host: adapter-declared `charness update`, doctor/version/cache
  readback, and required integrations/control-plane real-host checklist.

## Findings

### Act Before Ship

- Commit this final critique packet/record and notes so the helper sees a clean
  worktree; never pass the prepare packet itself as the critique artifact.
- Use `publish_release.py --part minor`; do not hand-edit versions, tag, or push.
- Keep claims limited to bootstrap, Markdown, preflight, and version paths; do
  not call this a broad production runtime speedup or proven product outcome.
- Require helper fresh-checkout probes, public distinct-channel readback,
  real-host proof, and install refresh before S4 completes.

### Bundle Anyway

- Release notes carry explicit zero-feedback, deterministic-no-Cautilus, and
  no-issue-close non-claims plus one `charness update` upgrade action.
- Replace the goal's pending `Release:` line with the final release artifact and
  public/install proof after publication.

### Over-Worry

- Do not hold the release for real feedback, a live evaluator, issue closure,
  hypothetical hosts, or broader UX copy when the locked proof passes.

### Valid but Defer

- Concurrent append locking, rotated-stream reconciliation, deeper host prose,
  and first real feedback evidence retain their existing triggers.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: git status | action: fix | note: commit critique packet record and notes before helper mutation
- F2 | bin: act-before-ship | evidence: strong | ref: release planner target | action: fix | note: use helper-owned minor bump and never manual tagging
- F3 | bin: act-before-ship | evidence: strong | ref: release planner evidence_packets | action: fix | note: require fresh checkout public real-host and install readbacks
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/quality/2026-07-10-repo-wide-quality-speed-release.md | action: fix | note: bound public claims to measured operator paths and zero feedback
- F5 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/release/2026-07-10-v0-64-0-notes.md | action: document | note: include upgrade action and non-claims
- F6 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md | action: defer | note: concurrency rotation and first real feedback keep explicit triggers

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: spawn surface accepted requested fields; runtime model metadata was not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: repo-owned release helper and locked source/export bundle.
- Consumer: GitHub release readers and installed Claude/Codex hosts.
- Owning surface: release helper/artifact plus adapter-owned update/readback.
- Verdict: owned-correctly

## Operator Action Required

- Before publish: validate/commit this critique and notes, confirm clean main and
  origin ancestry, then run helper dry-run followed by the authorized execute.
- After publish: confirm release URL through a distinct channel, run install
  refresh/doctor/readback, and bind all evidence in release latest and the goal.

## Upgrade Path

- Upgrade: `charness update`.
- Verify: `charness version --verbose` and `charness doctor` on the maintained host.
- Partial failure: use helper `--resume --publish-current`; do not retag manually.
- Rollback: return to the prior release through the documented managed checkout
  and plugin update path; preserve the published tag history.

## Deliberately Not Doing

- No Cautilus run, issue closeout, new host prose system, or claim of observed
  product improvement.

## Next Move

Commit this release-prep evidence, run helper dry-run with the notes and critique
record, then execute the user-authorized minor publication only if it stays clean.
