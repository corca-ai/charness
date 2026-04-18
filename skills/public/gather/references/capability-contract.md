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
- browser-mediated private SaaS fallback through `agent-browser`
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

## Browser-Mediated Private Sources

For a private SaaS URL or stable UI path, the decision ladder is:

1. existing local artifact for the same source identity
2. runtime grant or authenticated binary
3. official API, export, or CSV/report path
4. browser-mediated fallback through `agent-browser`
5. human-only bootstrap or clean stop
6. degraded partial value only when it stays honest

Escalate to browser fallback when:

- the user already named the private URL or the stable UI source
- the official API/export path is absent, blocked, or still gated behind the
  same authenticated browser state
- the request is read-oriented acquisition, not mutation-heavy workflow
- a durable local artifact can still capture what was gathered and what remains
  unconfirmed

Do not escalate to browser fallback when:

- the source owner or system of record is still unclear
- the task needs destructive or approval-sensitive actions rather than read
  acquisition
- the browser auth/bootstrap path is missing and there is no approved local
  operator step

## Auth / Bootstrap Modes

Treat these as first-class gather-compatible modes when the operator already
has them through an approved local path:

- imported auth state
- persistent profile path
- session-name persistence
- auth vault login
- origin-scoped headers
- human-only or manual bootstrap when state does not exist yet

The public skill should name the mode that was actually used, not hide it
behind a generic "authenticated" claim.

## Remote / Headless Story

Local desktop profile reuse is not equivalent to a remote Linux runner.

- Some flows can stay headless once saved auth state already exists.
- Some flows need a one-time manual or headed bootstrap before later headless
  runs become honest.
- If the host is remote/headless and no approved bootstrap path exists yet,
  `gather` should stop cleanly and name that gap instead of pretending every
  private URL is already automatable.

## Durable Artifact Shape

After browser-mediated acquisition, the gathered artifact should make these
visible:

- source identity
- freshness
- access path tried before browser fallback
- auth/access mode actually used
- what was captured
- what still needs human confirmation
