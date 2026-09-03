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

The earlier charness-owned `gather-slack`/`gather-notion` runtimes and credentialed `direct-cli` routes were removed under #418; [test_provider_boundary.py](../tests/quality_gates/test_provider_boundary.py) refuses their return.

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

When a consumer needs credentialed org data, the Default Boundary above applies: the consuming runtime's own capability/connector, never gather.

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
- X/Twitter status posts: the `twitter-syndication` route's `domain-specific-route` stage fetches the exact post and never substitutes a similar source; [twitter_exact_source.py](../skills/support/web-fetch/scripts/twitter_exact_source.py) owns the identity proof and the terminal states, live fetch is an explicit opt-in (`--live-domain-route` on [acquire_public_url.py](../skills/support/web-fetch/scripts/acquire_public_url.py)), and [gather SKILL.md](../skills/public/gather/SKILL.md) owns what the answer path does with `source_resolution.terminal_state`.

## Modeling Rule Going Forward

- use `integrations/tools/*.json` for true external ownership boundaries
- keep gather public-source only; credentialed org data stays behind the
  consuming runtime's capability/connector surface
- keep provenance in references or docs instead of pretending it is the active
  runtime owner
- [test_provider_boundary.py](../tests/quality_gates/test_provider_boundary.py) keeps model-facing skill surfaces and their `plugins/` mirror free of raw-token and removed-runtime wording
