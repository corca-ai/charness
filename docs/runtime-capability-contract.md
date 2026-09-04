# Runtime Capability Contract

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

This document defines how `charness` should reason about external access when
it runs inside both ordinary local coding environments and isolated agent
runtimes.

## Core Assumption

Assume an isolated agent runtime with no arbitrary local-secret-file read; the grant > authenticated binary > env preference is owned by [external-integrations.md](./external-integrations.md#runtime-access-principle). Public skills, support skills, and manifests must not present a raw env-variable fallback (`SLACK_BOT_TOKEN`, `GH_TOKEN`, ...) as the normal agent-consumable path; env fallbacks exist only for operator CLIs outside agent-controlled runtimes.

Repo-local capability config keeps secret-name choices repo-scoped:

- repo-local profiles and bindings live at
  `<repo-root>/.charness/local/capability.json` (gitignored)
- the committed shape lives at `<repo-root>/.charness/capability.example.json`
- machine-local install and doctor snapshots stay in the XDG state layer and
  remain unrelated to capability resolution

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

They may also record ordered host-neutral `config_layers` such as:

1. `grant`
2. `authenticated-binary`
3. `env`
4. `operator-step`
5. `public-fallback`

This is about precedence and fallback shape, not about host-specific file
paths or secret-file transport.

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

## Local Resolution Layer

Repo-local capability config models `logical capability id -> repo-local profile -> provider id` and records env-name aliases only, never secret values or machine-global state; [capability-resolution.md](./capability-resolution.md) owns the file, the CLI, and the shape.

## Gather As Exemplar

`gather` is one public concept (durable knowledge acquisition) over many providers; provider, access mode, and onboarding stay below the skill surface. [gather-provider-ownership.md](./gather-provider-ownership.md) owns the provider boundary.

## Onboarding Rule

Order: grant, authenticated binary, env fallback ([external-integrations.md](./external-integrations.md#runtime-access-principle)); then offer install only when it is safe and deterministic, otherwise stop with an explicit missing-capability explanation.

## Implication For Profiles

Profiles never carry secret transport or access control; capability availability is modeled by manifests, adapters, and host grants. Execution uses flattened bundles; `extends` is authoring metadata only ([profile.schema.json](../profiles/profile.schema.json)).
