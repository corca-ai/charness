# Capability Resolution

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

Capability resolution maps a skill-facing logical capability id to a repo-local provider profile, and that to a provider `charness` already models, without storing secrets in committed files.

## Current Slice

Capability resolution is **repo-local**, not machine-global. Each repo carries
its own capability surface so the same machine can host two repos that use
different Slack workspaces, different GitHub identities, or different Workspace
auth without one repo's choice silently affecting another.

This slice covers:

- one repo-local capability config file at
  `<repo-root>/.charness/local/capability.json` (gitignored)
- one repo-committed example shape at
  `<repo-root>/.charness/capability.example.json`
- CLI commands to scaffold, resolve, inspect, explain, and emit env alias
  exports against that repo-local config
- Slack gather runtime reuse through `charness capability env`

This slice does not add:

- a secret vault
- host-specific grant orchestration
- machine-global capability state shared across repos
- automatic migration helpers for repos that previously used the retired
  machine-local config layout (operators move bindings into the new repo-local
  file by hand)

## Fixed Decisions

- Capability config is repo-local. The real values live at
  `<repo-root>/.charness/local/capability.json` and are gitignored. The
  committed example lives at `<repo-root>/.charness/capability.example.json`.
- Public skills, repo adapters, and committed capability example files do not
  store raw secret values or copied secret-file paths.
- Shared credential reuse for one repo is modeled as
  `logical capability -> profile -> provider`, not as duplicated per-skill
  secret settings.
- Profiles may reference env var names, but not env values.
- Bindings are repo-local. One repo binds one logical capability id to one
  named profile per logical capability.
- The CLI emits YAML using the packaged PyYAML runtime dependency.
- Backward compatibility for older machine-global capability config layouts is
  not a goal.

## Command Surface

```bash
charness capability init
charness capability resolve slack.default
charness capability doctor slack.default
charness capability env slack.default
charness capability explain gather
```

All subcommands accept `--target-repo-root <path>` (defaults to the current
working directory) and `--repo-root <charness-checkout>` to override which
charness checkout supplies provider manifests.

## File Shape

Shape identity is the committed example
`<repo-root>/.charness/capability.example.json` and `charness capability init`.
Do not recopy the JSON here. `charness capability env <id>` prints `export`
lines of alias names, never secret values. The `provider` must be a provider
`charness` already models. Credentialed org connectors bind against the
consuming runtime's own provider, not a `charness`-owned one.
