# Runtime Capability Contract

This document defines how `charness` should reason about external access when
it runs inside both ordinary local coding environments and isolated agent
runtimes.

## Core Assumption

`charness` should assume that it may run inside an isolated agent runtime where
the agent cannot read arbitrary local secret files directly.

That means public skills should not treat raw `.env` access as the primary
integration model.

The preferred model is:

1. host grants a capability for one run or one session
2. support and integration layers resolve how to consume that capability
3. `.env` or process environment fallback exists for ordinary local operator
   setups when no stronger runtime grant surface exists

## Access Modes

External integrations should describe which access modes they can consume.
When a manifest lists more than one, it should keep them in preferred runtime
order.

- `grant`: runtime-provided capability or connector grant with no raw secret
  material persisted in repo artifacts
- `binary`: authenticated local CLI or binary already available on the machine
- `env`: environment-variable fallback such as `.env`, shell exports, or host
  process environment
- `public`: unauthenticated public fetch path
- `human-only`: user must intervene or supply the material outside the agent
- `degraded`: the skill still provides partial value without the capability

`grant` should be preferred over `env` whenever the host runtime can provide
it.

## Secrets Rule

`charness` should never require public skills or adapters to carry secret
values.

Allowed:

- env var names
- capability ids
- permission scope names
- install and grant instructions

So manifests may record non-secret capability requirements such as:

- `grant_ids`
- `env_vars`
- `permission_scopes`

Not allowed:

- checked-in API keys or tokens
- adapter fields that embed token material
- gathered artifacts containing copied credentials
- presets used as secret transport

## Skill Boundary

Public skills should talk about user intent and capability requirements, not
about secret plumbing details.

Good public-skill phrasing:

- requires GitHub access
- can use a granted Slack capability when available
- falls back to a public web path when private access is unavailable

Bad public-skill phrasing:

- export `SLACK_BOT_TOKEN`
- open `.env`
- paste the credential into chat

Raw credential mechanics belong in support skills, integration manifests, host
setup, or adapter references.

## Gather As Exemplar

`gather` is the clearest example because one user-facing concept may consume
many capability providers.

Example provider classes:

- GitHub via `grant` or authenticated `gh`
- Google Workspace via `grant`, `gws`-style binary, or explicit env-backed
  wrapper
- Slack via granted connector access or bot-token-backed integration
- Notion via granted connector access, token-backed fetcher, or published-page
  fallback
- generic web via public fetch

The public skill remains one concept: durable knowledge acquisition.

The provider, access mode, and onboarding path stay below the public-skill
surface.

## Onboarding Rule

When a public skill depends on an external capability, onboarding should follow
this order:

1. reuse an already granted runtime capability
2. reuse an already installed/authenticated local binary
3. use env/process fallback only when the host does not provide a better grant
   path
4. if installation is safe and deterministic, offer to install it
5. otherwise stop cleanly with an explicit missing-capability explanation

## Implication For Profiles

Profiles may still group workflow emphasis, but they are not the authority for
secret transport or runtime access control.

Capability availability should be modeled through integrations, support usage
guidance, adapters, and host runtime grants rather than through profile
inheritance.
