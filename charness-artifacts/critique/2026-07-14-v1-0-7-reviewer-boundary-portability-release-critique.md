# v1.0.7 Reviewer-Boundary Portability Release Critique
Date: 2026-07-14

## Decision Under Review

Publish the committed reviewer-boundary portability repair as Charness v1.0.7:
package Claude's bounded-reviewer asset, resolve the fingerprint helper from
the active skill directory, and state Codex's native `explorer` path without
claiming it loads Claude's envelope.

## Release Scope

`1.0.6` → `1.0.7` patch. Consumers receive a repair for a documented command
that previously looked for Charness source files in their own repositories.

## Surface-Lock Inventory

- Package export: `scripts/packaging_lib.py` and generated
  `plugins/charness/agents/bounded-reviewer.md`.
- Consumer command and host contract:
  `skills/shared/references/fresh-eye-subagent-review.md` and
  `docs/host-packaging.md`.
- Claude reviewer envelope: `.claude/agents/bounded-reviewer.md`.
- Consumer recurrence proof:
  `tests/quality_gates/test_reviewer_boundary_portability.py`.
- Release, critique, retro, and handoff artifacts that record package and
  publication boundaries.

## Failure Angles

- Operational: a correct source change could reach neither generated manifest
  nor installed consumer; fresh-checkout and post-publish update/readback are
  the release evidence boundaries.
- Communication: release notes could falsely say Codex loads Claude's markdown
  envelope, or omit the operator update needed to leave v1.0.6.
- First use: a path replacement could still fail from a clean consumer repo,
  leaving the original missing-file error unaddressed.

## Counterweight Pass

- Act before ship: track the consumed packet and critique, supply notes that
  distinguish Claude from Codex, and run the release helper's fresh-checkout
  proof before the tag.
- Bundle anyway: ship helper resolution, Claude asset export, and Codex native
  mapping as one patch; splitting them leaves one consumer second-class.
- Over-worry: do not generate a Codex custom-agent TOML or require a live
  Claude envelope bind before tagging this compatibility repair.
- Valid but defer: post-publish maintainer update/readback proves installed
  state; live Claude binding and Codex reviewer-tier application remain
  host-specific claims rather than release assertions.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-07-14-064853-packet.md | action: fix | note: track the consumed critique packet and use the release helper to run configured fresh-checkout proof before tag creation
- F2 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-07-14-v1-0-7-public-notes.md | action: document | note: release notes distinguish packaged Claude envelope asset from Codex native explorer mapping and name the update action
- F3 | bin: over-worry | evidence: moderate | ref: docs/host-packaging.md | action: defer | note: do not add a project-local Codex custom-agent file or claim the Claude envelope binds on Codex
- F4 | bin: valid-but-defer | evidence: strong | ref: .agents/release-adapter.yaml | action: defer | note: execute maintainer update and installed readback only after public release visibility, recording no early completion claim

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; the spawn surface accepted requested
  fields but did not expose provider-application metadata.

## Fresh-Eye Satisfaction

parent-delegated

Three independent `explorer` angles reviewed operational readiness,
communication, and first-use behavior. A separate `explorer` counterweight
triaged their concerns. All consumed
`charness-artifacts/critique/2026-07-14-064853-packet.md`; parent-side
fingerprints verified no worktree or index drift after each result.

## Boundary Ownership

- Producer: the packaging exporter creates installed plugin assets; the shared
  reference creates the helper command and host-specific reviewer contract.
- Consumer: Claude plugin installs, Codex native `explorer` reviewers, and
  clean consumer shells that run the fingerprint helper.
- Owning surface: checked-in-plugin-export owns installed assets; the shared
  reviewer-boundary reference owns portable command and host-contract wording;
  the release helper owns version, publication, and install-readback evidence.
- Verdict: owned-correctly

## Operator Action Required

Run `charness update` after v1.0.7 is public, then restart active Claude Code
and Codex sessions. The release artifact must record the installed package
readback; it must not claim a live host envelope bind without that distinct
host proof.

## Deliberately Not Doing

This patch does not create a Codex custom-agent TOML, prove every host's tool
binding, or expand into a cross-host packaging matrix.
