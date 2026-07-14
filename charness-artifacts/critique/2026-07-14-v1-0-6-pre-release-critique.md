# v1.0.6 Pre-Release Critique
Date: 2026-07-14

## Decision Under Review

Whether the post-v1.0.5 lifecycle-truthfulness and `SKILL_DIR` bootstrap slice
needs further product or guard work before the v1.0.6 patch release.

## Release Scope

- Target: `1.0.6` / tag `v1.0.6`.
- Consumer change: record objective issue/release follow-through without
  misreporting satisfaction, and prevent the observed command-scoped
  `SKILL_DIR` expansion failure in installed skill bootstrap instructions.

## Surface-Lock Inventory

- Shared bootstrap reference and its checked-in plugin export.
- Bootstrap-variable validator and public/support `SKILL.md` Bootstrap blocks.
- Issue/release lifecycle capture, report classification, and release artifact.
- Release notes, `charness update`, stale-session restart guidance, and the
  post-publish installed-cache readback.

## Failure Angles

- Operator/readability: an operator who hit `/scripts/...` needs the exact bug,
  update command, and restart caveat in the release notes, not an internal
  validator summary.
- Guard propagation: `check_file()` previously accepted the exact unsafe
  environment-prefix pattern when an individual skill cited the canonical
  reference; the canonical-reference-only detector did not cover that sibling
  authoring seam.
- Ownership: release-linked issue capture would add another producer for
  `closed_issue`, risking double counting and widening this patch despite no
  linked open issue in the release.

## Counterweight Pass

- Act before ship: reuse the existing exact-pattern detector for individual
  Bootstrap sections and add one unsafe plus one safe characterization test.
- Act during release: state the exact bug and lifecycle non-claim, then run an
  unrelated-repo installed-cache bootstrap smoke after `charness update`.
- Over-worry: do not add broad shell parsing, a permanent cross-repo gate,
  line-count refactors, or release-linked per-issue lifecycle writes now.
- Valid but defer: revisit unified carrier-owned issue capture only when a real
  release with linked issues exposes missing product evidence.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_skill_bootstrap_vars.py:93 | action: fix | note: propagate the exact unsafe SKILL_DIR assignment guard into each skill Bootstrap section
- F2 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/bootstrap-resolution.md:71 | action: document | note: release notes and closeout must name update, restart, lifecycle non-claim, and unrelated-repo installed-cache proof
- F3 | bin: over-worry | evidence: contested | ref: skills/public/release/scripts/publish_release_common.py:168 | action: defer | note: release-linked per-issue lifecycle capture widens ownership and may double count without a current linked issue
- F4 | bin: over-worry | evidence: moderate | ref: docs/handoff.md | action: defer | note: line-count refactors, broad shell parsing, and a permanent cross-repo gate add release churn without closing the observed escape

## Operator Action Required

- Release notes must say that v1.0.6 fixes the command-scoped `SKILL_DIR`
  expansion failure, that users should run `charness update`, and that active
  Claude/Codex sessions may need restart before the refreshed cache is visible.
- State that `closed_issue` and `released` are objective lifecycle signals, not
  human approval or general satisfaction.
- After publication and update, execute the documented export-before-use form
  from an unrelated consuming-repo directory against the installed cache and
  record the result in release closeout evidence.

## Upgrade Path

Run `charness update`, restart sessions that retain stale injected cache paths,
then rerun the bootstrap command with export and dependent expansion in the
same shell/tool invocation. Rollback remains the prior published v1.0.5 tag,
with its documented export-before-use workaround.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: metadata-hidden
- Application state: spawn accepted the requested fields; provider application was not exposed.

## Fresh-Eye Satisfaction

parent-delegated. Packet Consumed:
`charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.md`.
Two clean-fingerprint angle reviews and one clean-fingerprint no-tool
counterweight supplied the accepted findings.

Reviews that mutated the shared tree or recursively delegated despite their
read-only envelope were quarantined and not used. Parent restoration returned
the reviewer-boundary fingerprint to a clean state before the accepted retries.

## Boundary Ownership

- Producer: shared bootstrap guidance and skill Bootstrap examples produce the
  shell invocation contract; issue/release workflows produce objective outcome
  evidence.
- Consumer: consuming-repo shells expand the command, while usage reporting and
  release readers interpret lifecycle evidence.
- Owning surface: existing bootstrap validator for the exact shell hazard;
  release closeout for installed proof and communication.
- Verdict: owned-correctly

## Deliberately Not Doing

- No new blocking floor: this extends an existing validator over its sibling
  skill surface and adds no new authored field or gate.
- No console-prompt parser, arbitrary-doc scan, shell-dialect parser, permanent
  installed integration gate, or line-count-only refactor.
- No release-linked per-issue lifecycle capture in v1.0.6.

## Next Move

Sync the plugin export, run focused and locked closeout proof, commit the
pre-release improvement, then publish v1.0.6 with the operator actions above.
