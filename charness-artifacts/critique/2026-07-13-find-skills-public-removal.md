# Find-Skills Public Removal Critique
Date: 2026-07-13

## Decision Under Review

Remove `find-skills` as a public semantic-routing skill and remove its free-text
recommendation proxy. Preserve deterministic inventory, path recovery, and
readiness facts behind a stable non-public catalog CLI/backend; keep the
SessionStart hook contextual rather than turning it into a classifier.

Packet Consumed: `charness-artifacts/critique/2026-07-13-005302-packet.md`.

## Failure Angles

- First-reader/discoverability review found that deletion before naming the
  replacement backend would strand hidden support/integration discovery and
  stale-path recovery behind removed paths.
- Operational migration review found live dependencies in SessionStart hook
  wording and markers, setup-generated AGENTS policy, public-skill registries,
  plugin exports, current-pointer policy, profiles, tests, and inference-surface
  registration.
- Both reviewers rejected making the hook a semantic classifier. Host skill
  metadata plus agent judgment should choose public workflows; deterministic
  code should expose only catalog, path, and readiness facts.

## Counterweight Pass

- Act before ship: establish one stable catalog command/backend, move stale-path
  recovery, remove public registry/export entries, update hook/setup owners, and
  preserve focused proof for installed and fallback paths.
- Bundle anyway: rename user-facing hook concepts and active operator docs while
  retaining narrow legacy-marker cleanup.
- Over-worry: do not rewrite historical artifacts, add a replacement semantic
  classifier, or require every internal compatibility token to disappear.
- Valid but defer: richer catalog CLI ergonomics and unrelated historical
  coordination prose can follow after the stable removal seam lands.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/find-skills/scripts | action: fix | note: move deterministic inventory and stale-path recovery to a stable non-public catalog owner before deleting the skill
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/session_start_find_skills.py | action: fix | note: remove public-skill invocation and keep the hook as routing context only
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/setup/scripts/render_skill_routing.py | action: fix | note: shrink generated AGENTS routing and remove the public find-skills dependency
- F4 | bin: act-before-ship | evidence: strong | ref: docs/public-skill-validation.json | action: fix | note: synchronize public registries, plugin exports, profiles, artifacts, and focused tests with the removed skill
- F5 | bin: bundle-anyway | evidence: moderate | ref: scripts/host_hook_find_skills.py | action: fix | note: rename live hook concepts while retaining legacy marker cleanup
- F6 | bin: over-worry | evidence: strong | ref: charness-artifacts | action: document | note: historical records may keep find-skills lineage and should not be rewritten
- F7 | bin: valid-but-defer | evidence: moderate | ref: docs | action: defer | note: broader historical coordination prose cleanup is outside the first stable removal slice

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model `gpt-5.5`, reasoning effort `medium`, service tier `priority`.
- Host exposure state: metadata-hidden
- Application state: parent sent the adapter-requested fields; host returned no applied-tier metadata.

## Fresh-Eye Satisfaction

parent-delegated. Two distinct angle reviewers and one separate counterweight
reviewer completed read-only passes; parent-side fingerprint verification
reported `ok: true` and no drift after every review.

Post-change review initially returned `BLOCK` for active public-skill routing
contracts, the usage-episodes adapter schema, host-hook registry tests, and the
shared stale-path resolver reference. A second pass found deeper `achieve`
lifecycle/coordination references with the same removed ownership assumption.
Both remediation rounds moved semantic selection to installed metadata/model
judgment, retained catalog use only for hidden availability facts, synchronized
plugin mirrors, and passed their focused validators. The same bounded reviewer
then returned `PASS` with no remaining Act Before Ship findings; fingerprint
verification again reported no drift.

## Scenario Review

- Removed the retired public skill from the maintained evaluator-required skill
  registry, claim-fidelity registry/spec, and chatbot proposal inputs.
- Updated the whole-repo routing fixture so ordinary `impl`, `spec`, and
  `quality` selection remains unchanged while `bootstrapHelper` becomes `none`;
  compact instruction content now uses installed metadata/model judgment and
  reserves the catalog for hidden availability facts.
- Retained the maintained `achieve`, `handoff`, `impl`, `quality`, and `setup`
  consumer cases because their owner-workflow outcomes remain current; their
  active routing prose and dogfood contracts were updated where they had
  assigned semantic ownership to the removed skill.
- Deterministic fixture, registry, claim-fidelity, public-validation, and
  dogfood tests passed. No live Cautilus evaluation ran because the planner
  returned `next_action: none` under the ask-before-run policy.

## Boundary Ownership

- Producer: installed skill/plugin metadata and integration manifests produce capability inventory and readiness facts; the handoff produces pickup workflow state.
- Consumer: the host agent consumes installed public-skill metadata for semantic choice and consults deterministic catalog facts only when discovery is needed.
- Owning surface: stable Charness catalog CLI/backend for deterministic facts; SessionStart hook for contextual routing; setup for the hook-absent AGENTS fallback.
- Verdict: moved-to-owner
