# Capability Resolution

## Problem

`charness` already models provider capability metadata for external tools and
support runtimes, but it does not yet give each repo one local place to say:

- which logical capability ids that repo's skills/scripts care about
- which provider profile resolves each id on this machine for this repo
- how skills consume that resolution without reintroducing raw secret env names
  into committed adapters or skill contracts

The missing seam is not "store secrets in `charness`." The missing seam is a
portable resolver that maps:

- a skill-facing logical capability id
- to a repo-local provider profile
- to one real provider capability already modeled by manifests or support
  capability metadata

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
- The CLI uses JSON so it stays stdlib-only.
- Backward compatibility for older machine-global capability config layouts is
  not a goal.

## Non-Goals

- secret storage or encryption
- generic cross-product credential management
- replacing `gh auth`, host grants, or existing external auth flows
- forcing every provider to use env export when authenticated binary or grant
  is the honest primary path

## Constraints

- installed `charness` CLI must remain runnable from a managed checkout without
  extra Python dependencies
- support runtimes should be able to consume resolved env aliases without
  learning the full config model themselves
- durable docs must explain the separation between the gitignored real config
  and the committed example shape

## Success Criteria

- `charness capability resolve <logical-id>` reads
  `<target-repo-root>/.charness/local/capability.json` and returns the bound
  profile and provider for that repo.
- `charness capability env <logical-id>` emits shell exports that alias runtime
  env names from machine-local source env names without printing secret values.
- `charness capability init` scaffolds the gitignored real config plus the
  committed example shape and updates the repo's `.gitignore`.
- `charness capability doctor <logical-id>` reuses provider manifest metadata
  to inspect provider readiness for the resolved profile.
- `charness capability explain <skill-id>` shows which logical capabilities
  one public skill may need and, for `announcement`, which delivery capability
  the current repo adapter configured.
- Slack gather runtime can consume the env export flow before falling back to
  any operator-only direct-env path.
- First-run failure messages point to the exact file path and shape that the
  operator should edit.

## Acceptance Checks

- run `charness capability init --target-repo-root <repo>` against a fresh
  repo and verify that `<repo>/.charness/local/capability.json`,
  `<repo>/.charness/capability.example.json`, and a `/.charness/local/`
  entry in `<repo>/.gitignore` all exist.
- write a profile with `env_bindings` and verify that
  `charness capability env slack.default` prints alias exports such as
  `export SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN_CEAL_DEV}"`.
- verify that the Slack gather export helper can consume that env export path.
- run repo validators and standing tests after syncing the checked-in plugin
  export surface.

## Canonical Artifact

- this document for the current contract
- CLI implementation in `charness`

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

`<repo-root>/.charness/local/capability.json` (gitignored, real values):

```json
{
  "version": 1,
  "bindings": {
    "slack.default": "slack.ceal-dev"
  },
  "profiles": {
    "slack.ceal-dev": {
      "provider": "gather-slack",
      "access_mode_preference": ["grant", "env"],
      "env_bindings": {
        "SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN_CEAL_DEV"
      }
    }
  }
}
```

`<repo-root>/.charness/capability.example.json` (committed) keeps the same
shape with placeholder source env names. It must not contain real source env
names that would identify another repo's secret material.
