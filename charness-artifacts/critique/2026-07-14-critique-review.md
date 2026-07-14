# Reviewer-Boundary Consumer Portability Critique
Date: 2026-07-14

## Decision Under Review

Resolve the fingerprint helper from the active installed skill, export Claude's
typed reviewer envelope in its plugin-native location, and give Codex a
truthful native-reviewer mapping instead of treating a Claude markdown file as
a cross-host custom agent.

## Failure Angles

- Consumer-path ownership: the policy could still name a Charness checkout path
  even while the plugin contains the helper, leaving an ordinary consumer
  repository unable to run the documented command.
- Host-boundary truthfulness: exporting Claude's envelope could be misread as
  proof that Codex loads it, or a Codex configuration could be generated without
  the authorized project-setup boundary it requires.
- Recurrence proof: a textual path replacement could pass source checks without
  executing the exact documented shell command from an unrelated consumer repo.

## Counterweight Pass

- Real blockers were the consumer-root helper path, absent exported Claude
  envelope, stale source-path wording in that envelope, and an ambiguous Codex
  branch. The implementation and its focused consumer test address them.
- Bundle the helper, Claude asset, and Codex mapping: leaving any one of them
  behind would still make one host a second-class consumer.
- Do not overreach by generating a project-local Codex custom agent or claiming
  a live Claude envelope bind without a host-session probe.
- Valid deferral: live host binding/tier-application evidence and installed
  release-cache readback belong to the authorized publication boundary.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md | action: fix | note: resolve the fingerprint from the active skill package so consumer repositories never manufacture a Charness source tree
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/packaging_lib.py | action: fix | note: export Claude's typed bounded-reviewer envelope and remove its source-checkout dependency
- F3 | bin: bundle-anyway | evidence: strong | ref: docs/host-packaging.md | action: document | note: map Codex to its native explorer reviewer and state that the Claude envelope rail is unsupported there
- F4 | bin: over-worry | evidence: moderate | ref: charness-artifacts/spec/2026-07-14-skill-directory-shell-bootstrap.md | action: defer | note: do not generate a Codex custom-agent TOML or claim live host envelope binding before the authorized release proof

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; the spawn surface accepted the requested fields but did not expose provider-application metadata.

## Fresh-Eye Satisfaction

parent-delegated

Two independent `explorer` reviewers covered host portability and consumer
proof, and a separate `explorer` counterweight reviewed their disposition. All
three consumed `charness-artifacts/critique/2026-07-14-052432-packet.md`.
Parent-side reviewer-boundary fingerprints verified no worktree or index drift
after each returned result.

## Boundary Ownership

- Producer: the packaging exporter produces installed Claude assets; the shared fresh-eye reference produces the helper invocation and host mapping.
- Consumer: Claude installed-plugin reviewers, Codex native `explorer` reviewers, and the consumer shell that invokes the fingerprint helper.
- Owning surface: checked-in-plugin-export for packaged assets; shared reviewer-boundary reference for command and host-contract truthfulness.
- Verdict: owned-correctly
