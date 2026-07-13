# v1.0.4 Release Critique
Date: 2026-07-13

## Decision Under Review

Publish v1.0.4 as a patch release for catalog invalid-root no-write behavior and
custom-home Claude plugin-state isolation, without closing any tracked issue.

## Failure Angles

- Operational lock: version, generated manifests, broad gates, fresh checkout,
  public visibility, install refresh, and doctor/cache readback can drift apart.
- Narrative/interface: notes could claim proof before execution or omit a useful
  update, restart, rollback, migration, or real-host nonclaim.

## Counterweight Pass

- Patch semver is correct: both changes repair existing behavior without a new
  command, migration, or incompatible invocation.
- Final version/sync/public/install states are expected helper steps, not reasons
  to hand-edit manifests or reject the patch before the helper runs.
- A real-Claude custom-home smoke is not required because notes explicitly limit
  that claim to deterministic fake-CLI proof; default-home post-publish update and
  doctor/cache readback still remain required.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-07-13-v1.0.4-notes.md | action: fix | note: remove the premature final-proof claim and state proof remains owned by the release workflow; fixed.
- F2 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-07-13-v1.0.4-notes.md | action: fix | note: add patch/no-migration, rollback, restart, and fake-CLI real-host nonclaim wording; fixed.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release.py | action: fix | note: use the helper for bump, sync, locked gates, tag, public verification, and install refresh; pending execution after this critique is tracked.
- F4 | bin: act-before-ship | evidence: strong | ref: docs/design-north-star.md | action: fix | note: verify public content, fresh checkout, installed version, and doctor/cache through distinct evidence; pending publication boundary.
- F5 | bin: over-worry | evidence: moderate | ref: charness-artifacts/debug/2026-07-13-custom-home-claude-state-leakage.md | action: defer | note: no permission/symlink matrices, per-slice remote CI, or real-Claude custom-home claim in this patch.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: metadata-hidden
- Application state: requested fields were accepted; provider application was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — operational and narrative/interface angles plus a separate
counterweight ran read-only; both fingerprint windows verified zero drift.

## Boundary Ownership

- Producer: repo release helper produces versioned manifests, commit/tag, release record, and proof artifact.
- Consumer: existing Charness operators updating installed Codex/Claude plugin state.
- Owning surface: release helper plus adapter-declared public/install proof channels.
- Verdict: owned-correctly

## Release Scope

- Version/tag: `1.0.4` / `v1.0.4` from `v1.0.3`.
- Consumer change: invalid catalog refresh roots refuse without writes; explicit
  custom-home Claude operations no longer observe or mutate unrelated HOME state.

## Surface-Lock Inventory

- Version/install: `packaging/charness.json`, root marketplace, Claude/Codex
  plugin manifests, checked-in plugin export, release artifact.
- Behavior: catalog refresh diagnostics and Claude doctor/init/update/reset/uninstall.
- Communication: v1.0.4 notes, update/restart/rollback/nonclaim text.
- Proof: locked release gate, fresh checkout, distinct public URL/content,
  install refresh, version and doctor/cache readback.

## Operator Action Required

- Run the repo release helper with this tracked critique and notes; pass no issue
  close flags. Hold if lock, public, install, or doctor/cache proof fails.

## Upgrade Path

- Run `charness update`, restart active sessions, and verify doctor/version/cache.
  On regression, restore v1.0.3, restart again, and repeat the readback.
