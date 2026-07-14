# Skill Directory Shell Bootstrap Critique
Date: 2026-07-14

## Decision Under Review

Correct the shared `SKILL_DIR` bootstrap contract, add a canonical-reference
validator, and preserve honest source/plugin/installed boundaries after the
reported consuming-repo shell failure.

Packet Consumed:
`charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md`.
The review scope was the shared reference, validator and tests, synchronized
plugin copies, debug/spec records, handoff, and the locked-suite isolation
repair; unrelated lifecycle design had already completed its own critique.

## Failure Angles

- Customer/first-reader: the first revision said relative source paths worked
  from the Charness root while the spec promised execution from an unrelated
  consuming repo. That contradiction could replace `/scripts/...` with a
  different wrong relative path.
- Operational shell lifetime: export-before-use is insufficient if an agent
  exports in one ephemeral tool invocation and expands in another.
- Implementation integrity: the validator owns positive canonical shell
  examples and plugin sync owns the derived copy; parsing every prompt style or
  making the installed plugin validate a consumer repo would expand the owner.
- Delivery honesty: the local source/plugin fix must not imply released v1.0.5
  caches are fixed.

## Counterweight Pass

- The cwd and shell-lifetime findings are real blockers because both reproduce
  the same first-use capability failure. The reference now conditions relative
  paths on the source root, shows an absolute path elsewhere, and groups export
  plus invocation in one persistent shell block.
- Console-prompt fence parsing, all shell dialects, a permanent installed
  integration gate, and plugin-runtime self-validation are over-worry for a
  canonical author-repo contract whose positive examples are `bash` fences.
- Publication/readback is valid but deferred: the user authorized this source
  fix, not another irreversible release.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/bootstrap-resolution.md | action: fix | note: condition source-relative paths on the Charness root and show an absolute source path from consuming repos; applied
- F2 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/bootstrap-resolution.md | action: fix | note: keep export and dependent expansion in the same persistent shell/tool invocation; applied
- F3 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md | action: document | note: bound the durable review to bootstrap, validator, plugin sync, and test-isolation repair; applied here
- F4 | bin: over-worry | evidence: moderate | ref: scripts/check_skill_bootstrap_vars.py | action: defer | note: do not broaden the canonical validator to every console prompt, fence label, or shell assignment dialect without an observed escape
- F5 | bin: valid-but-defer | evidence: strong | ref: docs/handoff.md#next-session | action: defer | note: released-cache publication and installed readback require a later authorized release boundary

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: metadata-hidden
- Application state: requested fields were sent; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated. Two distinct bounded angles and one separate counterweight
completed read-only. Parent-side worktree/index fingerprints verified no drift
for all three accepted reviews. An earlier lifecycle-test reviewer approval was
quarantined after parent-created ledger drift and is not used as evidence here.

## Boundary Ownership

- Producer: host metadata, catalog resolution, or operator discovery produces a resolved skill path.
- Consumer: the command shell expands `$SKILL_DIR` and the selected helper is the final executable consumer.
- Owning surface: the shared bootstrap reference owns path-to-shell transport, the bootstrap-variable validator owns regression detection, and plugin sync owns derived copies.
- Verdict: owned-correctly
