# Critique: Release Adapter Preflight Durability Closeout

Date: 2026-06-02
Fresh-Eye Satisfaction: parent-delegated
Target: release / workflow preflight durability

## Scope

Closeout critique for the structural follow-up after commit `323a5733`:

- make release adapter focused preflight proof durable in the release artifact;
- surface changed-adapter non-required states as explicit artifact-visible
  non-claims instead of quiet helper return values;
- avoid re-running broad pytest as discovery while the slice is still moving.

## Consumed Fresh-Eye Findings

The parent-delegated subagent critique found two Act Before Ship concerns:

- `release_adapter_preflight` was present only in the transient publish payload,
  not in `charness-artifacts/release/latest.md`.
- `not_evaluable` and `not_configured` could proceed without focused commands;
  counterweight accepted that hard-blocking those states is a policy choice, but
  said the non-claim must be release-artifact visible.

## Counterweight Triage

### Act Before Ship

- Fixed: `publish_release_artifact.py` now writes a `Release Adapter Preflight`
  section that records status, reason, previous ref, adapter paths, changed
  fields, and focused commands, or says no focused commands were executed.
- Fixed: `publish_release_cli.py` now passes
  `payload["release_adapter_preflight"]` into every release artifact write path.
- Fixed: `validate_attention_state_visibility.py` now treats `not_evaluable` as
  an attention state, and the release preflight declaration includes
  `not_configured` and `not_evaluable` as artifact-visible non-claims.

### Bundle Anyway

- Added focused tests for direct artifact rendering of `not_evaluable`.
- Added publish-path coverage proving a successful changed-adapter preflight is
  recorded in `charness-artifacts/release/latest.md`.
- Updated the release dogfood evidence so the public skill contract describes
  durable adapter-preflight recording, not just pre-mutation execution.

### Valid But Defer

- Hard-blocking `not_evaluable` or `not_configured` remains a release policy
  decision. This slice records those states visibly instead of silently
  treating them as proof.
- `publish_release_cli.py` remains in the advisory length band. This slice
  added one forwarding argument; future release-helper growth should extract
  another module instead of appending to the CLI.

### Over-Worry

- No additional broad pytest was needed to discover the fix. Focused release
  tests and pre-lock closeout own the pre-stability proof; broad closeout should
  only run after the mutation set is locked.

## Result

No remaining Act Before Ship finding for this structural durability gap.
