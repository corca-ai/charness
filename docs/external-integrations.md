# External Integrations Policy

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

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
- whether a separate healthcheck is meaningful, and if so how to probe the
  smallest read-only consumer contract
- runtime hygiene for long-lived helper processes or daemons that `charness`
  may start, reuse, or depend on
- how hosts should install or update it
- how a public skill should degrade when it is absent
- the scripted recovery path when a recurring integration failure mode is known

### `gather` is public-source only

`gather` is public-source only. Credentialed organizational data — Slack,
Notion, private Google Workspace, Drive, or similar — is not a gather source and
`charness` does not own a credentialed provider runtime for it. Acquiring that
data is the consuming runtime's responsibility, through its own first-class
capability/connector surface, so `charness` never holds Slack/Google/Notion
tokens or ships a token-backed export runtime in a portable skill bundle.

That means:

- Slack / Notion / private Google Workspace / Drive access is reached through the
  consuming runtime's own capability/connector, not a `charness` gather provider
- Google Workspace public content is modeled through a host-mediated capability,
  operator-provided export, or browser-mediated path
- `gh` remains an external integration for public GitHub content (standard dev
  tooling), not a credentialed gather provider

The earlier `charness`-owned credentialed gather runtimes (`gather-slack`,
`gather-notion`) have been removed. See
[gather-provider-ownership.md](./gather-provider-ownership.md).

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

Some external binaries are support binaries: they do not need a support skill,
but they do support a public workflow through a manifest-backed install,
doctor, update, and recommendation path.

Use that lighter path when the tool has no agent-readable operating surface to
sync, and the public skill only needs to discover, install, verify, or degrade
around the binary. Examples include `tokei`, `ruff`, `gitleaks`, and `vulture`
for `quality`.

When an external tool repo already ships a support skill:

1. Prefer that upstream skill.
2. Do not fork it into `charness` by default.
3. Track it through an integration manifest.
4. Provide sync/update/doctor flows from `charness`.

When `support_skill_source` is present, `charness` should materialize a real
local skill surface instead of leaving only a pointer:

- upstream-owned skills should be fetched into the user cache and exposed
  through the installed Charness plugin under `support/<tool-id>/`
- charness-owned wrappers should be rendered into the user cache and exposed
  through the same installed plugin support layout

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
  - optional command and expected signal; omit it when `detect`, readiness, or a
    public-skill consumer probe is the honest boundary
  - prefer repo-owned probes or machine-readable read-only consumer commands
    over help prose or fragile descriptive strings
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

## User-Repo Discovery

When support or integration availability is unclear, run
`charness catalog list --repo-root <repo>` as read-only inventory before
assuming a tool is absent.

User repos that consume `charness` as a plugin do not need to copy every
manifest. Discovery surfaces (quality `list_tool_recommendations`, narrative
`list_tool_recommendations`, and `charness catalog list`) merge plugin-
shipped manifests as a fallback so a user repo without an
`integrations/tools/` of its own still sees the full charness-owned tool
set. When a user repo ships a manifest with the same `tool_id`, the user
copy wins; this is the override path for `install` commands, version
constraints, or recommendation roles a specific repo wants to pin.

Strict workflows (`install_tools`, `sync_support`, `update_tools`,
`validate_integrations`) honor the same merge through `load_manifests` so
`charness tool install <tool>` works in user repos without requiring local
manifests. Tests opt out of the fallback through
`CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS=1`.

User repos that want their tool dependencies visible in git (and in PR
diffs) can declare them explicitly:

```text
integrations/tools/dependencies.json
```

Schema (validated by [`validate_integrations.py`](../tools/validate_integrations.py)):

```json
{
  "schema_version": 1,
  "tool_dependencies": ["tokei", "ruff"]
}
```

Effects:

- `tool_recommendation` payloads gain `staged: true|false`. `null` when no
  [`dependencies.json`](../integrations/tools/dependencies.json) is declared.
- `validate_integrations` rejects unknown `tool_id`s in the list so the
  declaration cannot drift away from the available manifest set.
- Discovery and recommendation behavior is otherwise unchanged.

This file is optional and informational; absence means "no explicit staging
policy" and every plugin-fallback recommendation surfaces as `staged: null`.

## Command Surface

The current external-tool command surface is nested under `charness tool`:

- `charness tool sync-support`
  - sync upstream support skills and manifests into the local harness view
- `charness tool update`
  - update integrated external tools where safe
  - for a `manual`/`advisory` tool it cannot auto-bump, it still
    prints a behind-latest `ADVISORY:` line (and an `update_advisory` field in
    the payload) by comparing the detected version against the probed latest release,
    so a manual tool does not lag unnoticed
- `charness tool doctor`
  - verify tool availability, version expectations, and support-skill materialization
  - emits the same behind-latest `update_advisory` signal (output only; not
    persisted to the strict lock)

## Scope Guardrails

- Do not turn `charness` into a registry for generic SaaS connectors.
- Do not add general-purpose tools only because a single host uses them.
- Do not vendor external binaries just to simplify docs.
- Do not duplicate upstream support skills unless there is a concrete host
  compatibility reason.
- Do not model secret values in adapters, presets, or public skill bodies.

## Current Exclusions

- Google Workspace is intentionally excluded from support skill scope until the
  repo owns a concrete runtime. Do not add a support skill wrapper around an
  untracked local CLI.
- a reference implementation repo is not, by itself, an integration contract.
