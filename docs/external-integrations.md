# External Integrations Policy

`charness` should integrate external tools without pretending to own them.

## Principle

If a tool already exists as its own repo, package, or likely standalone
product, `charness` should prefer integration over vendoring.

Examples:

- `agent-browser`
- `specdown`
- `crill`
- future evaluation engine split from `workbench`

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
- how hosts should install or update it
- how a public skill should degrade when it is absent

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

Fork only when:

- the upstream skill is unavailable to the host model/runtime,
- the upstream skill is unmaintained,
- or `charness` needs a thin compatibility wrapper with a very small surface.

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
  - verify tool availability, version expectations, and skill references

## Scope Guardrails

- Do not turn `charness` into a registry for generic SaaS connectors.
- Do not add general-purpose tools only because a single host uses them.
- Do not vendor external binaries just to simplify docs.
- Do not duplicate upstream support skills unless there is a concrete host
  compatibility reason.
- Do not model secret values in adapters, presets, or public skill bodies.

## Current Exclusions

- `gws-cli` is intentionally excluded from support skill scope because it is too
  general and would force the same treatment for many unrelated connectors.
