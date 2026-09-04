# Host Packaging Contract

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

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
- validation entrypoint: [scripts/plugin_export/validate_packaging.py](../scripts/plugin_export/validate_packaging.py)
- export entrypoint: [scripts/plugin_export/export_plugin.py](../scripts/plugin_export/export_plugin.py)

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

Consequently a charness release publishes no native asset, and the released
version does not determine which `repograph` a consumer has; the checkout does
(the retired prebuilt layer and why:
[spec](../charness-artifacts/spec/repograph-tool-control-plane.md)).

Generated host layouts are not authoritative. If an exported manifest drifts
from the shared packaging manifest, regenerate the export instead of editing the
host file by hand.

## Shared Bundle Inputs

Host-neutral inputs and generated plugin/marketplace paths live in
[`packaging/charness.json`](../packaging/charness.json).
[`sync_root_plugin_manifests.py`](../scripts/plugin_export/sync_root_plugin_manifests.py)
writes the untracked `plugins/` tree; marketplace files that point at it are
tracked. Do not recopy those path inventories here.

## Host Mapping

Codex and Claude export layouts are the packaging manifest's host mapping.
Codex does not discover Claude-style markdown from a plugin-root `agents/`
directory; bounded reviewers use Codex's native `explorer` agent. Claude ships
plugin-native `agents/` with the bounded reviewer envelope.

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
python3 scripts/plugin_export/export_plugin.py \
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

Temporary export trees prove a host layout can be materialized under any root;
the repo-root `plugins/charness/` tree is the one stable install path,
regenerated rather than stored (see
[Shared Bundle Inputs](#shared-bundle-inputs)).

Operationally this means:

- after publish the maintainer's managed checkout is refreshed as a
  release-closeout step (`charness update` here); the `release` skill owns it,
  see [install refresh](../skills/public/release/references/install-refresh.md)
- the CLI manages one machine-local exported plugin surface under
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

- [scripts/plugin_export/plugin_preamble.py](../scripts/plugin_export/plugin_preamble.py) — builds the advisory payload from the packaging manifest, capability locks, and copy checks

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
