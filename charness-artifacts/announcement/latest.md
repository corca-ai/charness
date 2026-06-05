# charness 0.21.0 — release announcement (draft)

Date: 2026-06-05
Scope: release-note style summary for `charness` 0.21.0 (`v0.20.0..HEAD`, 12 commits).
Audience: charness maintainers and operators. Delivery: draft-only (adapter `delivery_kind: none`).

## Highlights

- **The clone-family advisory works again under nose 0.5.** nose 0.5 changed its
  `--format json` output (top-level array → object) and made `--mode` *replace*
  the default channels. The quality clone inventory was silently reading the new
  schema as zero families; it now parses both the 0.5 object and the 0.4 array,
  reports the live nose version, and surfaces real refactoring candidates again
  (a live scan finds ~20 extractable families across the skill scripts).
- **More of the quality gate is testable in-process.** Five more `inventory_*`
  quality-gate tests stopped spawning their entrypoint as a subprocess and now
  drive it in-process, so coverage/type/mutation tooling can finally see across
  what used to be a process boundary. The repo-local boundary-bypass ratchet
  dropped from 94 to 90 candidate test files (55 → 51 convertible) — a real
  reduction, not an exemption.

## Changes

- `integrations/tools/nose.json` now prefers **nose 0.5.0 or newer**; the
  clone-family baseline was refreshed from a live 0.5 scan.
- Two quality inventory scripts (`inventory_public_spec_quality`,
  `inventory_cli_side_effect_probes`) gained the sibling-library import bootstrap
  their peers already had, so they are genuinely importable in-process.
- Portable quality-artifact scaffolding and the boundary-bypass testability
  ratchet from the test-quality initiative are part of this release.

## Fixes

- The nose advisory no longer under-reports `0 families` on a healthy scan.
- Per-file test path-bootstraps and several `E402` suppressions were removed
  earlier in the cycle; this release keeps tests free of path hacks while the
  fix lives in the production scripts.

## Operator update

- `charness update` refreshes the managed install to 0.21.0; Claude and Codex
  pick up the regenerated plugin manifests after the update.
- nose is advisory: install/upgrade to nose 0.5 (`~/.cargo/bin` or the upstream
  installer) to get clone-family findings; the gate still passes without it.
