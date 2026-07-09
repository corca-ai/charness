# Release Critique
Date: 2026-07-09

## Execution

Standalone release critique executed with three bounded fresh-eye angle reviews
and one separate counterweight review.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-07-09-v0-63-1-release-packet-packet.md`

## Target

`references/release-critique.md`

## Change

Publish Charness `0.63.1` as a patch release from `origin/main..HEAD`, using
the repo-owned release helper for bump, sync, verification, tag push, GitHub
release creation, distinct-channel verification, and install refresh.

## Capability at Stake

Operators should be able to update to the latest Charness release and receive
the proof-honesty, validation, quality-inventory, markdown-preview, and debug
planner repairs without install-surface drift or misleading release notes.

## Release Scope

- current version: `0.63.0`
- target version: `0.63.1`
- tag: `v0.63.1`
- consumer delta: proof-honesty and maintenance ergonomics repairs, with no
  migration required.

## Surface-Lock Inventory

- versioned release surfaces: `packaging/charness.json`, checked-in Claude and
  Codex plugin manifests, marketplace metadata, tag `v0.63.1`, and the GitHub
  release record.
- generated/exported surfaces: checked-in plugin mirror under
  `plugins/charness/` and release artifact under `charness-artifacts/release/`.
- operator-visible behavior: prompt-mutation marker scoring evidence, A/B
  validation failures before spend, standing-test economics inventory wording,
  markdown preview helper CLI behavior/help, and debug planner `--repo-root`
  help.
- operator docs/release communication: release notes file
  `charness-artifacts/release/2026-07-09-v0-63-1-notes.md`, release artifact,
  and existing evergreen `charness update` instructions.

## Angles

- Gawande / operational checklist: require clean worktree, helper-owned bump and
  push, full release quality gate, fresh-checkout probes, and post-publish
  verification.
- Minto / communication structure: require human release notes rather than
  generated commit notes only, with narrow claims and explicit operator action.
- Raskin / operator interface: keep the upgrade path simple (`charness update`),
  state no migration, and do not invent new update commands for this patch.
- Counterweight: confirmed no additional blocker remains if notes and critique
  are committed and the helper executes successfully with post-publish
  verification.

## Findings

### Act Before Ship

- Create concise human release notes instead of relying on generated notes only.
  Status: fixed by `charness-artifacts/release/2026-07-09-v0-63-1-notes.md`.
- Use `publish_release.py`, not manual manifest edits, tag pushes, or GitHub
  release creation. Status: required next command.
- Commit this critique packet/artifact before execute so the release helper sees
  a clean intended worktree. Status: required before publish execute.
- Require helper-recorded public visibility plus distinct-channel verification
  and install refresh before calling the release complete. Status: required
  publish helper proof.

### Bundle Anyway

- Pass the release notes file to the helper through `--notes-file`.
- Pass this artifact to the helper through `--critique-artifact`.
- Keep existing adapter update instructions; they are evergreen and not stale.

### Over-Worry

- Do not manually pre-bump generated manifests; helper-owned sync is safer and
  is the release contract.
- Do not require a new migration path or new update command for this patch.
- Do not rewrite README or generated CLI docs for this release; the changed
  operator action is already covered by release notes plus `charness update`.

### Valid But Defer

- Broader argparse help debt remains outside this patch release.
- A stronger fixed release-note taxonomy can be added later.
- More release distinct-channel probe tightening is separate from this patch if
  the configured helper verification passes.

## Operator Action Required

- Before publish: commit the release critique artifacts and notes file.
- Publish: run `publish_release.py --part patch --notes-file ... --critique-artifact ... --execute`.
- After publish: require the helper to record GitHub release visibility,
  distinct-channel verification, and `charness update` install refresh.

## Upgrade Path

- No migration is required.
- Operators run `charness update`.
- Operators restart active Claude/Codex sessions if the update reports cache path
  or session staleness.
- Rollback path remains the prior published release `v0.63.0`.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: host accepted three angle reviewers and one counterweight reviewer.

## Boundary Ownership

- Producer: release helper, packaging manifest, checked-in plugin export, and
  release adapter.
- Consumer: operators installing or updating Charness from the published release.
- Owning surface: release skill and `.agents/release-adapter.yaml`.
- Verdict: owned-correctly

## Next Move

Validate and commit the critique artifacts plus release notes, then execute the
repo-owned release helper for patch release `0.63.1`.
