# Charness v0.56.7

## Scope

This release ships two threads of work that landed on `main` since `v0.56.6`:

1. A **capability-first skill surface rollout** that sharpens how skills name the
   capability at stake, and
2. **Proof-scope honesty and validation-startup** improvements in the release and
   quality tooling.

No migration or rollback step is required beyond the normal `charness update`
path; the update surface is unchanged.

## Skill Surface Changes

- Public skill **contracts** now name the capability at stake — refined workflow
  steps and Output-Shape field names across 17 skills: `achieve`, `announcement`,
  `create-cli`, `create-skill`, `critique`, `debug`, `gather`, `handoff`, `hitl`,
  `hotl`, `ideation`, `impl`, `issue`, `narrative`, `quality`, `setup`, and
  `spec`. These edits are in the skill bodies; the skill-picker `description:`
  text is unchanged except `quality`, whose description now proposes "quality
  moves" rather than "next gates".
- The rollout is bounded and advisory: it refines skill prose and contracts. It
  does **not** add a new capability-language validator or blocking gate, and it
  does **not** claim every public skill is fully migrated — the explicit
  non-claims for unmigrated skills live in the rollout's goal and quality
  artifacts, not in the shipped skill prose.

## Validation & Release Tooling

- Release planning now evaluates real-host proof from the intended release delta
  when a target version is selected, and the plain planner output calls out when
  real-host proof is required.
- Slice closeout now fails if a recorded or reused broad pytest proof is narrower
  than the closeout payload it claims to verify.
- The standing pytest runner no longer starts pytest subprocesses just to detect
  pytest and xdist availability; it keeps the runner interpreter aligned with the
  pytest module and falls back to serial mode when xdist is disabled.
- Focused mutation coverage suggestion output is clearer about recommended,
  partial, missing, and noop states.
- The release planner's target-version and next-action resolution was factored
  into shared helpers, and the dup-ratchet / advisory clone baselines were
  re-seeded in lockstep after the tooling edits rotated clone family ids without
  introducing new duplication.

## Verification

The release bundle is verified through the repo-owned release helper. The helper
runs the version bump, generated surface sync, quality gate, fresh-checkout
probes, tag and branch push, public release creation, distinct-channel
verification, and maintainer install refresh.

## Upgrade

Run `charness update`, then restart existing Codex or Claude sessions that should
load the refreshed plugin surface. No migration or rollback step is required
beyond the normal update path.
