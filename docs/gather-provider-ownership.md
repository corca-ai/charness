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
  - `defuddle`
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

When using a reference implementation, separate:

- `Core Practice`: the invariant that creates the useful behavior and should be
  preserved in the local design
- `Peripheral Practice`: host, packaging, credential, adapter, or UI details
  that should be adapted to `charness` instead of copied

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
  Google gather should instead flow through a host-mediated capability,
  operator-provided export, or browser-mediated private-source path

## Consumer Contract

When a consumer wants provider-backed gather:

- Slack:
  - provide the approved grant or env fallback
  - do not reimplement Slack API helper scripts in the consumer repo
- Notion:
  - provide the approved publication or access path
  - do not reimplement Notion export helpers in the consumer repo
- Google:
  - prefer a host-mediated capability when one exists
  - otherwise ask for an operator-provided export or use the browser-mediated
    private-source ladder when appropriate
- browser-mediated private SaaS:
  - let `gather` own the official-path-first and degradation policy
  - let `agent-browser` stay the external browser runtime boundary
  - do not push each consumer repo to reinvent profile/auth/bootstrap wording
- public article/document pages:
  - use `defuddle` as an external reader-extraction binary when direct fetch
    returns cluttered or weak HTML
  - preserve the source URL and extraction confidence because cleaned markdown
    is derived content
  - preserve attempted, skipped, unavailable, terminal, and selected fallback
    stages in the durable acquisition trace instead of relying on handoff notes
    or chat context for proof of degraded acquisition
- X/Twitter status posts (exact-source identity):
  - the `twitter-syndication` route's `domain-specific-route` stage fetches the
    EXACT post through identity-keyed endpoints (Syndication CDN by status id,
    then oEmbed) and treats a result as the original ONLY when the returned
    status id matches the requested one — the proof lives in the trace as
    `identity_proof.matched`
  - never substitute a merely-similar public source as if it were the original:
    a mismatch is `invalid-proof`, an all-blocked outcome is honest. The
    acquisition exposes `source_identity` ∈ `exact-fetched` / `exact-blocked` /
    `exact-unavailable` / `not-applicable` so the answer path can distinguish a
    fetched exact post from a blocked one; `gather` never emits `similar-source`
  - live X fetching is operator-authorized, not autonomous: the exact-source
    stage runs against seeded/granted responses by default, and live network
    fetch is an explicit opt-in (`--live-domain-route`)
  - `source_resolution.terminal_state` names the terminal operator boundary:
    `exact-post-acquired`, `exact-post-blocked-by-x`,
    `authenticated-browser-required`, or `unsupported-route`;
    `authenticated-browser-required` includes the default non-live policy where
    exact endpoints were not attempted until an operator-approved live X route,
    authenticated browser/profile, or exact-source provider is available
  - the Syndication endpoint is keyed on the post-body status id (genuine
    existence proof) and is tried first; oEmbed echoes the requested URL, so it
    proves *requested-id match* only and is accepted as the original solely when
    it also returns a rendered body (`html`/`author_name`) — a bare URL echo for
    a deleted/nonexistent post is rejected rather than treated as existence

## Modeling Rule Going Forward

- use `integrations/tools/*.json` for true external ownership boundaries
- use `skills/support/<skill-id>/capability.json` plus repo-owned helper
  scripts for `charness`-owned provider runtime
- keep provenance in references or docs instead of pretending it is the active
  runtime owner

## Near-Term Follow-Up

1. Keep Google on a host/export/browser-mediated path until a concrete runtime
   contract is stable enough to consume.
2. Treat Slack and Notion as `charness`-owned provider runtime, not external
   plugin dependencies.
3. Keep capability metadata honest while the support/runtime home lands under
   `skills/support/`.
