# Host Packaging Contract

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

This document defines the first host-packaging contract for exporting the
host-neutral `charness` repo into Claude-compatible, Codex-compatible, and
minimal Grok Build plugin layouts.

## Goals

- keep `charness` as the only source of truth for shared skills, profiles,
  presets, and integrations
- prevent Claude, Codex, and Grok plugin trees from becoming hand-maintained forks
- make host-specific manifests and marketplaces generated artifacts rather than
  policy surfaces
- give future sessions a stable target for export scripts and packaging tests

## Source Of Truth

- source policy: [packaging/charness.json](../packaging/charness.json)
- source schema: [packaging/plugin.schema.json](../packaging/plugin.schema.json)
- bootstrap runtime contract: [packaging/bootstrap-python.json](../packaging/bootstrap-python.json)
- bootstrap runtime requirements: [packaging/bootstrap-requirements.txt](../packaging/bootstrap-requirements.txt)
- validation entrypoint: [scripts/validate_packaging.py](../scripts/validate_packaging.py)
- export entrypoint: [scripts/export_plugin.py](../scripts/export_plugin.py)

The shared packaging manifest is authoritative for:

- package identity and summary
- which repo directories are shared bundle inputs
- which host exports exist
- which manifest paths and marketplace paths generators must produce

## The `repograph` binary is built, not distributed

This packaging contract deliberately declares NO native artifact. `repograph`
is built from the [`native/repograph`](../native/repograph) crate that ships in
this checkout, and installed through the external-tool control plane:

```bash
charness tool doctor repograph      # required tool; blocking when missing
charness tool install repograph     # cargo install --path native/repograph
```

The manifest is [integrations/tools/repograph.json](../integrations/tools/repograph.json)
and the gate-side resolver is
[scripts/native_gate_lib.py](../scripts/native_gate_lib.py), which prefers, in
order, a `CHARNESS_NATIVE_CORE` override, this checkout's own
`native/repograph/target/release/repograph` (rebuilding it, with an announcement
on stderr, when the crate source is newer), then the installed binary.

A prebuilt-artifact distribution layer used to live here: a `native_core`
declaration in the packaging manifest bound a per-version, per-tuple archive
name and sha256, and a lifecycle downloaded, checksummed, staged, extracted,
atomically activated, pruned, and rolled it back, projecting twelve phase
statuses into `charness doctor`. It was retired on 2026-08-30 because the crate
source ships in the same repository that consumes it: building from the checkout
you are running makes `stale`, `incompatible`, and `source_drift` structurally
impossible rather than detectable after the fact, and `charness` already owned a
control plane that installs missing binaries — three of its tools (`awiki`,
`lychee`, `tokei`) already install through `cargo`. See
[the spec](../charness-artifacts/spec/repograph-tool-control-plane.md).

Consequently a charness release publishes no native asset, and the released
version does not determine which `repograph` a consumer has; the checkout does.

Generated host layouts are not authoritative. If an exported manifest drifts
from the shared packaging manifest, regenerate the export instead of editing the
host file by hand.

## Shared Bundle Inputs

The first contract keeps these repo directories host-neutral:

- `skills/`
- `profiles/`
- `presets/`
- `integrations/tools/`
- [`README.md`](../README.md) — operator quick start, install path, and skill map

That means the export script can materialize a host plugin layout without
needing a second skill taxonomy or a second profile catalog.

The repo also materializes a generated plugin tree on demand so hosts get one
stable install path. That tree is NOT in git:
[`scripts/sync_root_plugin_manifests.py`](../scripts/sync_root_plugin_manifests.py)
writes it, `charness init` and `charness update` run that producer, and a bare
clone has no `plugins/` at all until something does. Run the producer before the
next two links resolve:

- [`plugins/charness/.claude-plugin/plugin.json`](../plugins/charness/.claude-plugin/plugin.json) — Claude plugin identity: name, version, author, repository
- [`plugins/charness/.codex-plugin/plugin.json`](../plugins/charness/.codex-plugin/plugin.json) — Codex plugin identity plus skills path and interface metadata

The two marketplace files that point AT that tree are tracked, so they resolve
in a bare clone:

- [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) — Claude marketplace entry pointing at the generated plugin root
- [`.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json) — Codex repo marketplace with the local plugin source and install policy

These files are generated from the shared packaging manifest and validated
against it. They are still derived artifacts, not the source of truth.

## Host Mapping

### Codex

The Codex export must map the shared bundle into:

- `.codex-plugin/plugin.json`
- `skills/` with flat public skill directories
- `support/` for non-discoverable support assets
- optional future `.mcp.json`, `.app.json`, and `assets/`
- optional repo marketplace at [`.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json)

Codex does not discover Claude-style markdown files from a plugin-root
`agents/` directory. Bounded fresh-eye reviewers therefore use Codex's native
`explorer` agent with the bounded review packet. Reviewer-tier spawn fields are
passed when exposed; this is not the Claude tool envelope. Use an isolated
reviewer or, when sharing the parent is unavoidable, the parent-side fingerprint
fallback.

The current contract fixes the Codex repo-marketplace path because the official
Codex plugin docs use that location for repo-scoped plugin catalogs.

### Claude

The Claude export must map the shared bundle into:

- `.claude-plugin/plugin.json`
- `skills/` with flat public skill directories
- `support/` for non-discoverable support assets
- optional future `.mcp.json`
- plugin-native `agents/` with the bounded reviewer envelope
- optional future `commands/`

`commands/` remains a future host-specific output and should only appear when
a future export iteration has a clear shared source or a clearly bounded host
adapter.

### Grok Build

Grok consumes the same exported plugin tree. There is no Grok marketplace in
this contract.

The operator install path is:

- copy the exported tree to `~/.grok/plugins/charness` (auto-trusted)
- list `charness` in `~/.grok/config.toml` `[plugins].enabled`
- or point `[plugins].paths` at a plugin directory that already contains
  `charness/`

`charness init` / `charness update` materialize that user plugin directory.
They do not add a Grok marketplace source.

Charness does not install Grok-native hooks or depend on hook stdout. Host
behavior is explicit and adapter-owned; the exported plugin tree is otherwise
read-only.

## Current Export Scope

The export flow writes host layouts into an operator-chosen output root, and the
same producer materializes a generated (untracked) install tree under
`plugins/charness/`.

What it materializes today:

- [`README.md`](../README.md) — repo overview covering workflow routes, core concepts, and support integrations
- flat public `skills/`
- Charness-owned `support/` assets only
- `profiles/`
- `presets/`
- `integrations/tools/`
- both host plugin manifests inside one generated plugin root
- Claude's typed bounded-reviewer envelope under plugin-native `agents/`
- an optional Codex repo marketplace file

Upstream-consumed support skills such as `agent-browser` and `specdown` are
intentionally absent from the generated plugin tree. Install
and update commands materialize those skill bodies into the machine-local
installed plugin from `support_skill_source` metadata.

What it intentionally does not materialize yet:

- generated Codex `commands/` or custom-agent TOML files (those are project
  surfaces owned by the Codex host, not plugin assets)
- richer install-surface metadata for published plugin catalogs
- release-time overrides beyond version stamping

## Release-Time Version Override

The shared packaging manifest keeps the default version and remains the source
of truth.

When a release workflow needs a stamped export without mutating
[`packaging/charness.json`](../packaging/charness.json), the export entrypoint may override the emitted
version:

```bash
python3 scripts/export_plugin.py \
  --repo-root . \
  --host codex \
  --output-root /tmp/charness-export \
  --version-override 1.2.3 \
  --with-marketplace
```

Guardrails:

- the override only changes emitted release metadata
- it must not change shared bundle membership or other policy fields
- the checked-in shared manifest remains the canonical default version

## Repo-Root Install Surface

The repo-root install surface exists for a different reason than temporary
export trees.

- temporary export trees prove that shared source artifacts can be materialized
  into a host layout under another root
- the repo-root plugin tree gives hosts one stable install PATH with the correct
  flat skill layout — the path is stable, the tree is regenerated, not stored

This means the source repo taxonomy and the host-facing plugin taxonomy are now
explicitly different on purpose.

Operationally this means:

- the official operator install path is a thin `charness` CLI rooted at the
  managed checkout `~/.agents/src/charness`
- refreshing the maintainer/authoring machine's own managed checkout is a
  required release-closeout step: after publish, run `charness update` here so
  the installed plugin surface stays `== repo`. This closes the installed-vs-repo
  version-skew class (a scaffold or check that cites the installed plugin can
  otherwise diverge from the repo gate). The `release` skill owns the contract;
  see [install refresh](../skills/public/release/references/install-refresh.md)
- operators do not need to clone `charness` manually before first install when
  they already have a usable `charness` binary; `charness init` may materialize
  that managed checkout internally from its configured repo URL
- that CLI manages one machine-local exported plugin surface under
  `~/.codex/plugins/charness`
- Claude should prefer host-native marketplace and plugin installation driven by
  `charness init` and `charness update`; `claude-charness` remains an optional
  local wrapper for proof or fallback use
- Codex personal installs may point `~/.agents/plugins/marketplace.json` at
  `./.codex/plugins/charness` while keeping the marketplace file itself under
  `~/.agents`
- Codex local development should load [`./plugins/charness`](../plugins/charness/)
  through the tracked repo marketplace file, after the producer has written it
- tracked marketplace files remain generated compatibility artifacts rather
  than the primary operator-facing install contract
- public GitHub install remains a testable hypothesis, not an already-proven
  guarantee, until a pushed-repo experiment confirms it on both hosts

## Thin Startup Advisory

`charness` does not use a thick runtime preamble like `gstack`.

Instead, hosts may render a thin startup advisory from:

- [scripts/plugin_preamble.py](../scripts/plugin_preamble.py) — builds the advisory payload from the packaging manifest, capability locks, and copy checks

Current v1 output is intentionally read-only:

- package version
- root install-surface drift status
- explicit update hints for Claude, Codex, and Grok installs, including the best-effort Codex cache refresh path
- lock-based readiness summary for known integrations
- vendored-copy warnings for consumer repos that still carry a local
  non-symlink `charness` copy

This keeps startup guidance centralized without turning skill execution into a
networked self-update loop.

## Charness host hooks

Charness does not install SessionStart, Codex, or startup-context hooks. It does
not inject lessons or routing text into every session. The only retained
optional host hook is the Claude PostToolUse skill-anchor guard when an adapter
explicitly enables it. Plugin export itself remains read-only.

## Non-Goals

- inventing a second metadata system for host-specific skill behavior
- treating host manifests as the canonical place for bundle membership
- solving downstream host packaging in the shared repo

## Deferred Decisions

- whether future Codex exports should always ship repo-marketplace metadata or
  only when explicitly requested by an operator
- whether Claude-specific `commands/` or `agents/` should be generated from
  neutral metadata or kept as separate optional adapter-owned artifacts
