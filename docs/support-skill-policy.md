# Support Skill Policy

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

This document defines when `charness` should ship a support skill, when it
should consume an upstream one, and when a capability should stay an external
integration only.

## Purpose

Support skills are not public workflow concepts.

They exist to teach the harness how to use specialized tools consistently
without turning those tools into the product's philosophy.

They are also where host/runtime-specific capability usage guidance can live
without forcing secret-handling details into a public skill body.

Terminology:

- `support skill`: agent-readable instructions for using a tool capability.
- `support capability`: Charness-owned runtime or provider metadata that can
  select or explain a support skill.
- `integration manifest`: external tool lifecycle, install, doctor, and update
  metadata.

## Classification Rule

Ask this first:

- is the user asking for a workflow concept?
- or is the harness missing tool-use knowledge?

If it is a workflow concept, it belongs in `skills/public/`.

If it is tool-use knowledge, it may belong in `skills/support/` or an external
integration.

If the missing knowledge is only "this public skill benefits from this binary,
and here is how to install, doctor, update, and degrade around it," keep it as a
support binary in an integration manifest. Do not create a support skill just to
name a CLI that has no additional agent operating contract.

Examples:

- `tokei` for `quality` SLOC inventory and test-ratio probes
- `ruff` for Python lint validation
- `gitleaks` for fast secret scanning
- `vulture` for Python dead-code and dead-file advisory review

## Keep A Support Skill In `charness` When

- the harness needs local instructions that are not well expressed by a plain
  manifest
- multiple public skills benefit from the same tool-usage guidance
- the capability is still repo-agnostic and does not become host philosophy

Examples:

- `web-fetch`
- a thin wrapper skill that teaches how to use an external engine safely
- `markdown-preview`

## Prefer Upstream Consumption When

- the external tool already ships a usable support skill
- the upstream skill is maintained and compatible
- `charness` only needs sync/update/doctor plus a small usage policy layer

Examples:

- `agent-browser`
- `specdown`

## Fork Only When

- the upstream skill is unavailable or incompatible
- the upstream surface is unmaintained
- `charness` needs a very thin compatibility wrapper with a small local seam

Forking should be exceptional, not the default.

Support-state identity lives in [lock.schema.json](../integrations/locks/lock.schema.json) and [control-plane.md](./control-plane.md). Do not recopy the enum here.

## Capability Catalog Interaction

The read-only capability catalog inventories these layers in order:

- local public skills first
- local support skills and local integration manifests next
- adapter-configured trusted skill roots after that
- generic external ecosystems only when the host explicitly allows them

That keeps hidden availability facts honest without turning inventory into
semantic workflow routing. Installed skill metadata and model judgment own the
ordinary route decision.

Required contract fields live in the lock/manifest schemas. Private-access capabilities follow [runtime-capability-contract.md](./runtime-capability-contract.md).

## Consumable Locally

Support skills are always materialized into the installed plugin under
`support/<tool-id>/`; [control-plane.md](./control-plane.md) owns the sync,
update, doctor, and lock/provenance contract.
