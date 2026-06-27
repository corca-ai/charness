# Charness v0.56.7

## Scope

This patch release tightens proof-scope honesty and speeds up validation startup
without changing the normal update path.

- Release planning now evaluates real-host proof from the intended release delta
  when a target version is selected, and the plain planner output calls out when
  real-host proof is required.
- Slice closeout now fails if a recorded or reused broad pytest proof is narrower
  than the closeout payload it claims to verify.
- The standing pytest runner no longer starts pytest subprocesses just to detect
  pytest and xdist availability; it keeps the runner interpreter aligned with
  the pytest module and falls back to serial mode when xdist is disabled.
- Focused mutation coverage suggestion output is clearer about recommended,
  partial, missing, and noop states.

## Verification

The release bundle is verified through the repo-owned release helper. The helper
runs the version bump, generated surface sync, quality gate, fresh-checkout
probes, tag and branch push, public release creation, distinct-channel
verification, and maintainer install refresh.

## Upgrade

Run `charness update`, then restart existing Codex or Claude sessions that
should load the refreshed plugin surface. No migration or rollback step is
required beyond the normal update path.
