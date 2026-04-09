# Support Skill Policy

This document defines when `charness` should ship a support skill, when it
should consume an upstream one, and when a capability should stay an external
integration only.

## Purpose

Support skills are not public workflow concepts.

They exist to teach the harness how to use specialized tools consistently
without turning those tools into the product's philosophy.

## Classification Rule

Ask this first:

- is the user asking for a workflow concept?
- or is the harness missing tool-use knowledge?

If it is a workflow concept, it belongs in `skills/public/`.

If it is tool-use knowledge, it may belong in `skills/support/` or an external
integration.

## Keep A Support Skill In `charness` When

- the harness needs local instructions that are not well expressed by a plain
  manifest
- multiple public skills benefit from the same tool-usage guidance
- the capability is still repo-agnostic and does not become host philosophy

Examples:

- `web-fetch`
- a thin wrapper skill that teaches how to use an external engine safely

## Prefer Upstream Consumption When

- the external tool already ships a usable support skill
- the upstream skill is maintained and compatible
- `charness` only needs sync/update/doctor plus a small usage policy layer

Examples:

- `agent-browser`
- `specdown`
- future evaluation engine extracted from `workbench`

## Fork Only When

- the upstream skill is unavailable or incompatible
- the upstream surface is unmaintained
- `charness` needs a very thin compatibility wrapper with a small local seam

Forking should be exceptional, not the default.

## States

Support capability states should stay explicit:

- `native-support`
- `upstream-consumed`
- `wrapped-upstream`
- `forked-local`
- `integration-only`

These labels matter for later sync/update/doctor behavior.

## `find-skills` Interaction

`find-skills` should use this policy in order:

- local public skills first
- local support skills and local integration manifests next
- adapter-configured official skill roots after that
- generic external ecosystems only when the host explicitly allows them

That keeps discovery honest without hiding host-official capability packs such
as Ceal's own skill surface.

## Required Contracts

Any support capability that is not purely native should eventually have:

- an integration manifest
- install/update guidance
- detect/healthcheck commands
- version expectation
- degradation rules when absent

## Session 12 Hook

This policy is the bridge into control-plane work.

Session 12 should turn these rules into:

- sync policy
- update policy
- doctor checks
- manifest instances for real tools

For the current v1 seam, `reference` is the preferred default sync strategy:

- keep the upstream support surface visible
- generate a local reference artifact when needed
- avoid copying or forking until a manifest explicitly asks for it
