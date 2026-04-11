# Control Plane Contract

This document defines the control-plane contract for external tools,
support-owned runtime capability metadata, and upstream support-skill reuse in
`charness`.

## Goals

- keep manifest policy separate from live machine state
- let hosts verify external dependencies without vendoring them
- support upstream skill reuse without silently forking tool-specific logic
- give future sessions a stable target for `tool sync-support`,
  `tool install`, `tool update`, and `tool doctor`

## Source Of Truth

- external source policy: `integrations/tools/*.json`
- external source schema: [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json)
- support capability source policy: `skills/support/*/capability.json`
- support capability schema: [capability.schema.json](/home/ubuntu/charness/skills/support/capability.schema.json)
- generated live state: `integrations/locks/*.json`
- generated wrapper or synced support skills: `skills/support/generated/`

External manifests are authoritative for external ownership intent. Support
capability metadata is authoritative for `charness`-owned runtime capability
that still needs machine-readable discovery and doctor context. Lock files are
authoritative only for what was last synced or observed on one machine.

For v1, `sync-support` should default to `reference` as the recommended
strategy. That means `charness` records where the upstream support surface
lives and can materialize a local generated reference artifact, but does not
copy or fork the upstream content unless the manifest explicitly asks for a
stronger strategy.

Support capability state should stay explicit in doctor and lock output:

- `native-support`
- `upstream-consumed`
- `wrapped-upstream`
- `forked-local`
- `integration-only`

## Command Responsibilities

## Agent-Readable State

Control-plane actions should leave state that a later agent can continue from
without re-deriving machine conditions.

- command stdout should stay structured and machine-readable
- mutations should persist under `integrations/locks/*.json` and
  `skills/support/generated/` when relevant
- manual-only steps should still record explicit upstream docs and remaining
  guidance instead of disappearing into prose
- when the manifest points at a GitHub repo, control-plane output should try to
  record the latest release metadata so manual guidance can stay current

### `charness tool sync-support`

Purpose:
sync upstream support skills referenced by manifests.

Reads:

- manifests with `support_skill_source`
- optional existing lock entries for last synced refs

Writes:

- lock entry under one stable per-tool shape with a `support` section
- generated wrapper content under `skills/support/generated/` when
  `sync_strategy` is `generated_wrapper`
- generated reference notes under `skills/support/generated/` when
  `sync_strategy` is `reference`
- local copy or symlink material only when the manifest declares that strategy
- `copy` and `symlink` require an explicit upstream checkout mapping from the
  operator, for example
  `--upstream-checkout corca-ai/claude-plugins=/abs/path/to/claude-plugins`

Rules:

- never installs or updates the external binary itself
- never copies an upstream skill unless the manifest explicitly says `copy`
- `reference` is the default recommendation because it keeps the local taxonomy
  honest while still leaving a durable breadcrumb for operators and later host
  packaging
- shared manifests should prefer `copy` when they need executable support
  materialization; `--local-dev-symlink` is only a maintainer-local override
  for repos that want faster iteration without changing the published contract
- `copy` and `symlink` must fail closed when the requested upstream checkout is
  not mapped or the referenced upstream path does not exist
- leaves public skill taxonomy untouched
- should support `--dry-run` before any write mode exists

### `charness tool install`

Purpose:
attempt external tool installation where the manifest can execute it, otherwise
persist install guidance plus post-attempt machine state.

Reads:

- manifests for lifecycle install instructions
- existing lock entries for prior install, support, doctor, or update state

Writes:

- lock entry with an `install` section capturing status, docs, executed
  commands, and post-attempt detect/healthcheck results
- generated support references or wrappers when support sync is requested
- refreshed doctor state so later agents can see what changed

Rules:

- manual mode may still write lock state even when no binary install happened
- manual mode should preserve the operator handoff surface by recording
  explicit docs and notes
- executable modes may only run commands declared in the manifest
- install should prefer reusing doctor output over inventing separate health
  claims

### `charness tool update`

Purpose:
run the manifest-declared update flow for external binaries that `charness`
depends on.

Reads:

- manifests for lifecycle update instructions
- existing lock entries for current observed versions

Writes:

- updated lock entry with an `update` section rather than overwriting unrelated
  support or doctor state
- structured result per tool: `updated`, `noop`, `manual`, or `failed`

Rules:

- `manual` mode prints instructions and never mutates the host
- executable update modes may only run commands declared in the manifest
- every successful update must rerun detect and healthcheck before the lock is
  refreshed
- tools with `kind = external_skill` are skipped unless they also declare a
  binary lifecycle

### `charness tool doctor`

Purpose:
verify that the host matches the capability contract closely enough for harness
workflows to rely on it.

Checks:

- detect command succeeds
- observed version satisfies `version_expectation`
- healthcheck command returns the expected signal
- optional manifest-declared `readiness_checks` succeed
- declared support-skill reference exists or can be regenerated

Exit semantics:

- `0`: all checked capabilities satisfy the contract
- `1`: at least one capability is missing, unhealthy, not ready, or version-mismatched
- `2`: manifest error or control-plane misuse blocked evaluation

Rules:

- must report per-tool failures without stopping after the first problem
- should distinguish missing tool, stale version, and broken support-skill sync
- should distinguish a setup-not-ready host from a missing or unhealthy binary
- should reuse manifest degradation notes in operator-facing output
- when writing locks, should update the `doctor` section without discarding
  prior `support` or `update` sections

Current v1 drift rule:

- if a prior `tool sync-support` run recorded `materialized_paths`, `doctor` should
  verify those paths still exist and report `support-missing` when they do not
- first-run repos without a prior support lock should not fail closed only
  because generated wrapper or reference artifacts have not been materialized
  yet

Current doctor payload also carries metadata-side capability context so setup
and onboarding layers can inspect it without re-reading the source file:

- `kind`
- `access_modes`
- `capability_requirements`
- `readiness`

## Initial Target Set

The first manifest wave should cover:

- `agent-browser`
- `specdown`
- `crill`
- `gws-cli`
- `cautilus`

These are now concrete manifest instances. The evaluator boundary is no longer
deferred: `cautilus` is the tracked standalone evaluation product, while
consumer-owned adapters remain local repo assets.

## Non-Goals

- generic SaaS connector registry
- vendoring external binaries for convenience
- hidden forks of upstream support skills
- profile-specific install logic inside the manifest schema
