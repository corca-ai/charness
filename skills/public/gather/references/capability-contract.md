# Gather Capability Contract

`gather` is the public concept for durable knowledge acquisition.

It may consume many providers, but those providers should stay below the
public-skill surface.

## Provider Classes

Common examples:

- local repo files
- public web fetch
- GitHub
- Google Workspace
- Slack
- Notion
- future repo-specific document or connector surfaces

## Access Modes

Preferred order:

1. `grant`
2. `binary`
3. `env`
4. `public`
5. `human-only`
6. `degraded`

Interpretation:

- `grant`: host runtime already granted access for this provider
- `binary`: authenticated CLI or external tool already available
- `env`: ordinary local environment-variable fallback
- `public`: unauthenticated public path
- `human-only`: the user must intervene outside the agent
- `degraded`: partial value remains even without the provider

## Public Skill Rule

The public skill should say:

- what capability class is needed
- whether a public fallback exists
- what durable artifact is produced

It should not say:

- open `.env`
- paste the token
- store the credential in the adapter

Those details belong in support usage guidance and integration manifests.

## Onboarding Rule

When a capability is missing:

- offer safe installation when the toolchain is deterministic and appropriate
- otherwise ask whether the operator wants to install or grant the capability
- if neither path is available, stop cleanly and preserve what was still
  gathered
