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
- external source schema: [manifest.schema.json](../integrations/tools/manifest.schema.json)
- support capability source policy: `skills/support/*/capability.json`
- support capability schema: [capability.schema.json](../skills/support/capability.schema.json)
- generated live state: `integrations/locks/*.json`
- repo-local generated support symlinks: `skills/support/generated/`
- user-cache support payloads: `${XDG_CACHE_HOME:-~/.cache}/charness/support-skills/`

External manifests are authoritative for external ownership intent. Support
capability metadata is authoritative for `charness`-owned runtime capability
that still needs machine-readable discovery and doctor context. Lock files are
authoritative only for what was last synced or observed on one machine.

Support skills are now always materialized. `reference` is no longer a sync
strategy. If a manifest declares `support_skill_source`, `charness` should
produce a real local skill surface:

- `upstream_repo`: fetch or reuse the upstream skill root into the user cache,
  then expose it through a repo-local symlink
- `local_wrapper`: render a charness-owned wrapper skill into the user cache,
  then expose it through a repo-local symlink

Support capability state should stay explicit in doctor and lock output:

- `native-support`
- `upstream-consumed`
- `wrapped-upstream`
- `integration-only`

For this contract, `external_skill` and `external_binary_with_skill` both
materialize a local skill surface. The difference is binary lifecycle:

- `external_skill`: only the skill surface is required
- `external_binary_with_skill`: the skill surface plus install/update/detect/
  healthcheck/readiness contract

## Command Responsibilities

## Agent-Readable State

Control-plane actions should leave state that a later agent can continue from
without re-deriving machine conditions.

- command stdout should stay structured and machine-readable
- mutations should persist under `integrations/locks/*.json`, the user cache,
  and repo-local support symlinks when relevant
- manual-only steps should still record explicit upstream docs and remaining
  guidance instead of disappearing into prose
- when the manifest points at a GitHub repo, control-plane output should try to
  record the latest release metadata so manual guidance can stay current; the
  probe should prefer authenticated `gh api`, fall back to tokened HTTP via
  `GH_TOKEN` or `GITHUB_TOKEN`, and only then use public unauthenticated HTTP
- release probe output should persist structured `status`, `reason`, and
  `error` fields so `no-release`, `github-forbidden`, invalid JSON, and network
  failure remain distinguishable in lock state
- when the host install path can be inferred safely, control-plane output
  should record install provenance so later updates can route through the same
  package manager instead of guessing

### `charness tool sync-support`

Purpose:
sync upstream support skills referenced by manifests.

Reads:

- manifests with `support_skill_source`
- optional existing lock entries for last synced refs

Writes:

- lock entry under one stable per-tool shape with a `support` section
- cache-backed materialized support payload under the user cache
- repo-local symlink under `skills/support/generated/`
- explicit upstream checkout overrides may still be supplied for local
  maintainer iteration or deterministic tests, for example
  `--upstream-checkout corca-ai/claude-plugins=/abs/path/to/claude-plugins`

Rules:

- never installs or updates the external binary itself
- upstream skill sources must point at a skill root directory, not only one
  `SKILL.md` file
- remote fetch is the default path for `upstream_repo`; an explicit local
  checkout is only an override
- materialization should use immutable-ish cache directories keyed by content
  digest, then repoint the repo-local symlink instead of mutating the old
  target in place
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
- refreshed support cache/symlink state when support sync is requested
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
- if install provenance is known and the manifest declares a matching package
  manager route, update may promote `manual` into an explicit
  `package_manager` execution path
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
- declared repo-local support symlink still resolves

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
  because support materialization has not run yet

Current doctor payload also carries metadata-side capability context so setup
and onboarding layers can inspect it without re-reading the source file:

- `kind`
- `access_modes`
- `capability_requirements`
- `readiness`

For long-lived external runtimes, health is not limited to "the binary
responds". Doctor should also fail closed on known runtime-hygiene drift such
as orphaned daemon trees when `charness` has a repo-owned inspection or cleanup
surface for that tool.

## Initial Target Set

The first manifest wave should cover:

- `agent-browser`
- `specdown`
- `gws-cli`
- `cautilus`

These are now concrete manifest instances. The evaluator boundary is no longer
deferred: `cautilus` is the tracked standalone evaluation product, while
consumer-owned adapters remain local repo assets.

## Command Surface

Representative operator path:
`charness tool doctor cautilus`, `charness tool install cautilus`,
`charness tool update agent-browser`, `charness tool sync-support cautilus`.

When a tool's healthcheck detects recurring runtime drift, the follow-up should
prefer a repo-owned cleanup command over prose-only guidance.

Manual-mode install flows should persist manual install guidance, latest
observed release metadata when available, and refreshed doctor state instead of
claiming that the host was mutated.

## Non-Goals

- generic SaaS connector registry
- vendoring external binaries for convenience
- hidden forks of upstream support skills
- profile-specific install logic inside the manifest schema
