# Gather Provider Ownership

This document corrects the ownership model for provider-specific runtime under
the public `gather` skill.

## Goal

Consumers should be able to use `charness` gather providers without
reimplementing provider scripts in each consumer repo.

That means:

- if `gather` needs provider-specific runtime to talk to Slack, Notion, or a
  similar API, `charness` should own that runtime
- consumers should only need to choose adapters, grants, env fallback, or
  approved binaries
- consumer repos should not need to recreate Slack API helpers or other
  provider scripts just because they installed `charness`

## Correct Ownership Split

### `charness` owns

- public `gather` behavior
- provider-specific support/runtime that makes `gather` actually usable
- capability requirements and degradation rules
- support skills and helper scripts that hide repeated provider bootstrap
- provenance notes when another repo informed the implementation

### external integrations own

- standalone binaries and CLIs with their own release boundary
- their install/update/detect/healthcheck lifecycle
- deep runtime behavior outside `charness`

Examples:

- external binary integrations:
  - `agent-browser`
  - `specdown`
  - `gh`
  - future `gws-cli`
  - future `defuddle`
- `charness`-owned gather provider runtime:
  - Slack thread export logic used by `gather`
  - Notion published-page gather logic used by `gather`

## Reference Implementation Rule

Another repo may inform `charness` implementation without becoming the runtime
owner.

That distinction matters:

- `reference implementation`: used to learn structure, edge cases, or output
  shaping
- `runtime dependency`: the thing the consumer must actually install or sync to
  make the feature work

`charness` must not model a reference implementation repo as the runtime owner
unless the consumer is truly expected to install or sync that repo at runtime.

## Current Correction

The earlier experimental manifests for `google-public-export`,
`slack-bot-export`, and `notion-published-export` were too easy to misread as
"`charness` depends on `claude-plugins` runtime".

That is not the intended product shape.

The corrected direction is:

- Slack and Notion gather provider logic should move toward `charness`-owned
  support/runtime
- `claude-plugins` may remain a provenance or design reference, not a required
  runtime dependency
- Google should not use a `google-public-export` helper path in `charness`;
  Google gather should instead flow through a real external binary integration
  such as `gws-cli`

## Consumer Contract

When a consumer wants provider-backed gather:

- Slack:
  - provide the approved grant or env fallback
  - do not reimplement Slack API helper scripts in the consumer repo
- Notion:
  - provide the approved publication or access path
  - do not reimplement Notion export helpers in the consumer repo
- Google:
  - install the approved external runtime such as `gws-cli`
  - let `charness` consume that binary through an integration manifest

## Modeling Rule Going Forward

- use `integrations/tools/*.json` for true external ownership boundaries
- use `skills/support/` plus repo-owned helper scripts for `charness`-owned
  provider runtime
- keep provenance in references or docs instead of pretending it is the active
  runtime owner

## Near-Term Follow-Up

1. Keep Google on the external-runtime path and add `gws-cli` when its
   contract is ready.
2. Treat Slack and Notion as `charness`-owned provider runtime, not external
   plugin dependencies.
3. Design the `charness`-owned support/runtime home for Slack and Notion gather
   helpers so consumers stop inheriting this ambiguity.
