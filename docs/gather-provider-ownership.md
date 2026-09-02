# Gather Provider Ownership

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

This document defines the ownership boundary for the public `gather` skill.

## Default Boundary: gather is public-source only

Plain `gather` targets public URLs, local files, published/exported documents,
public GitHub content, and other sources that need no organizational credential.

Credentialed organizational data — Slack, Notion, private Google Workspace,
Drive, or similar — is **not** a gather source. Reaching that data is the
**consuming runtime's** responsibility, through its own first-class
capability/connector surface. `charness` gather does not hold Slack/Google/Notion
tokens, ship provider-specific credentialed export runtimes, or advertise a
provider-CLI route to reach private org data. When a gather request names such a
source, gather hands it off to the runtime capability or stops with a
missing-capability explanation.

This is a deliberate narrowing. An earlier design shipped charness-owned
credentialed provider runtimes (`gather-slack`, `gather-notion`) and a
`direct-cli` provider mode so a maintainer who owned the grant could pull private
org data through gather. That surface was dangerous (raw tokens such as
`SLACK_BOT_TOKEN` on a portable, materialized skill bundle) and became
pointless once consuming runtimes (e.g. Ceal) moved credentialed access to their
own connector/integration layer. Those support skills and the credentialed
`direct-cli` routes have been removed; the token boundary now lives entirely with
the consuming runtime.

## Correct Ownership Split

### `charness` owns

- public `gather` behavior (public-source only)
- capability requirements and degradation rules for public routes
- the public-URL / reader-extraction / browser-mediated-public source ladder
- provenance notes when another repo informed the implementation

### the consuming runtime owns

- credentialed organizational data access (Slack, Notion, private Google
  Workspace, Drive, and similar) through its own capability/connector surface
- the grants, tokens, and audit boundary for that access

### external integrations own

- standalone binaries and CLIs with their own release boundary
- their install/update/detect/healthcheck lifecycle
- deep runtime behavior outside `charness`

Examples:

- external binary integrations:
  - `agent-browser`
  - `specdown`
  - `gh` (public GitHub content is standard dev tooling)
  - `defuddle`

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

## Consumer Contract

When a consumer needs credentialed org data:

- Slack / Notion / private Google Workspace / Drive:
  - reach them through the consuming runtime's own capability/connector surface
  - do not expect charness gather to hold the token or ship the export runtime;
    gather is public-source only
- Google (public/published content):
  - prefer a host-mediated capability when one exists
  - otherwise ask for an operator-provided export or use the browser-mediated
    public-source ladder when appropriate
- browser-mediated public SaaS:
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
- keep gather public-source only; credentialed org data stays behind the
  consuming runtime's capability/connector surface
- keep provenance in references or docs instead of pretending it is the active
  runtime owner
- a Charness-side provider-boundary gate keeps model-facing skill surfaces (and
  their `plugins/` mirror) free of direct provider-CLI / raw-token wording so the
  public-only boundary does not silently regress
