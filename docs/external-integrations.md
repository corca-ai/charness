# External Integrations Policy

`charness` should integrate external tools without pretending to own them.

This also applies to provider-specific capability surfaces that sit below one
public workflow concept. For example, `gather` stays one public skill even
when it uses separate provider paths such as `gh`, Slack, Google Workspace, or
published Notion gathering.

## Principle

If a tool already exists as its own repo, package, or likely standalone
product, `charness` should prefer integration over vendoring.

Examples:

- `agent-browser`
- `specdown`
- `gws-cli`
- `cautilus`

## Ownership Model

### Upstream owns

- binary implementation
- binary release cadence
- binary versioning
- tool-specific deep documentation
- upstream support skill if the tool ships one

### charness owns

- when the tool should be used in harness workflows
- how to detect whether it is available
- which access modes are supported (`grant`, `binary`, `env`, `public`,
  `human-only`, `degraded`)
- which version range is expected
- how to health-check it
- runtime hygiene for long-lived helper processes or daemons that `charness`
  may start, reuse, or depend on
- how hosts should install or update it
- how a public skill should degrade when it is absent
- the scripted recovery path when a recurring integration failure mode is known

### `gather` provider exception

Some `gather` providers are not true upstream runtime dependencies even when
their first implementation was inspired by another repo.

If `charness gather` is supposed to work in consumer repos without asking those
repos to install a second plugin or reimplement helper scripts, then
`charness` owns that provider runtime.

That means:

- Slack gather helper logic belongs in `charness`
- published Notion gather helper logic belongs in `charness`
- Google Workspace access should be modeled through a real external runtime
  such as `gws-cli`, not through a borrowed public-export implementation

Current `charness` support homes:

- `skills/support/gather-slack/`
- `skills/support/gather-notion/`

See [gather-provider-ownership.md](./gather-provider-ownership.md).
The machine-readable metadata for these `charness`-owned gather providers now
lives next to the support skill itself under:

- [`skills/support/gather-slack/capability.json`](../skills/support/gather-slack/capability.json)
- [`skills/support/gather-notion/capability.json`](../skills/support/gather-notion/capability.json)

## Runtime Access Principle

`charness` should assume it may run inside an isolated runtime where the agent
cannot read arbitrary local secret files directly.

So external integrations should prefer:

1. runtime capability grants
2. already authenticated local binaries
3. environment-variable fallback only when the host lacks a stronger grant
   path

The integration layer may record env var names or permission scope names, but
should not require checked-in secret values or adapter-level secret transport.

## Support Skill Reuse Rule

When an external tool repo already ships a support skill:

1. Prefer that upstream skill.
2. Do not fork it into `charness` by default.
3. Track it through an integration manifest.
4. Provide sync/update/doctor flows from `charness`.

When `support_skill_source` is present, `charness` should materialize a real
local skill surface instead of leaving only a pointer:

- upstream-owned skills should be fetched into the user cache and exposed
  through a repo-local symlink
- charness-owned wrappers should be rendered into the user cache and exposed
  through the same repo-local symlink pattern

Fork only when:

- the upstream skill is unavailable to the host model/runtime,
- the upstream skill is unmaintained,
- or `charness` needs a thin compatibility wrapper with a very small surface.

Do not apply this rule to a provider that `charness` actually intends to own as
part of its shipped runtime surface. Provenance is not the same as runtime
ownership.

## Integration Manifest Contract

Each external tool should eventually get one manifest file under:

```text
integrations/tools/<tool-id>.json
```

Expected fields:

- `tool_id`
- `kind`
  - `external_binary`
  - `external_skill`
  - `external_binary_with_skill`
- `upstream_repo`
- `homepage`
- `install`
  - command or documented method
- `update`
  - command or documented method
- `detect`
  - command and success criteria
- `healthcheck`
  - command and expected signal
- `access_modes`
  - ordered supported access modes such as `grant`, `binary`, `env`, or
    `public`
- `capability_requirements`
  - non-secret grant ids, env var names, or permission scopes needed to use
    those access modes
- `readiness_checks`
  - optional setup-readiness probes that can fail closed before runtime use
- `config_layers`
  - ordered host-neutral precedence such as `grant` ->
    `authenticated-binary` -> `env` -> `operator-step` -> `public-fallback`
- `version_expectation`
- `support_skill_source`
  - absent when no upstream skill exists
- `host_notes`
  - optional host-specific install wrinkles

## Desired Commands

These do not need implementation in session 1, but the plan assumes them.

- `charness sync-support`
  - sync upstream support skills and manifests into the local harness view
- `charness update-tools`
  - update integrated external tools where safe
- `charness doctor`
  - verify tool availability, version expectations, and support-skill materialization

## Scope Guardrails

- Do not turn `charness` into a registry for generic SaaS connectors.
- Do not add general-purpose tools only because a single host uses them.
- Do not vendor external binaries just to simplify docs.
- Do not duplicate upstream support skills unless there is a concrete host
  compatibility reason.
- Do not model secret values in adapters, presets, or public skill bodies.

## Current Exclusions

- `gws-cli` is intentionally excluded from support skill scope because it is an
  external binary boundary, not a `charness` support skill. It now belongs in
  the external integration surface via
  [`integrations/tools/gws-cli.json`](../integrations/tools/gws-cli.json).
- a reference implementation repo is not, by itself, an integration contract.
