# Control Plane Contract

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

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

Manifests, capability files, and locks are the identity. Pointers:

- external policy: `integrations/tools/*.json` and [manifest.schema.json](../integrations/tools/manifest.schema.json)
- support capability: `skills/support/*/capability.json` and [capability.schema.json](../skills/support/capability.schema.json)
- live machine state: `integrations/locks/*.json`
- materialization and support-state identity: [`support_state_for_manifest`](../scripts/support_sync_lib.py), [`doctor_lib.py`](../scripts/setup/doctor_lib.py), [`control_plane_lifecycle_lib.py`](../scripts/adapters/control_plane_lifecycle_lib.py)

Do not recopy support-state enums, kind/lifecycle matrices, or per-command reads/writes/exits here. [`docs/cli-reference.md`](./cli-reference.md) is generated from `--help`.

## Agent-Readable State

Control-plane actions leave structured YAML a later agent can continue from: compact status, transition, and next-action on stdout; full evidence in the lock or `--detail`. Mutations persist under locks, the user cache, and installed plugin support paths. Manual-only steps still record upstream docs. Install provenance, when inferred safely, routes a later update through the same package manager.

## Command Surface

```bash
charness tool doctor agent-browser
charness tool install --recommendation-role validation --next-skill-id quality
charness tool install agent-browser
charness tool update agent-browser
charness tool sync-support specdown
```

Repair is preview by default (`--execute` to mutate). Recurring healthcheck drift should prefer a repo-owned cleanup command over prose. Manual-mode install should persist manual install guidance and doctor state; it does not claim the host was mutated.

When a manifest points at a GitHub repo, the release probe prefers authenticated `gh api`, then tokened HTTP via `GH_TOKEN` or `GITHUB_TOKEN`, then public unauthenticated HTTP. Probe output keeps structured `status`, `reason`, and `error` so `github-forbidden` stays distinguishable. Identity: [`control_plane_lifecycle_lib.py`](../scripts/adapters/control_plane_lifecycle_lib.py).

## Non-Goals

- generic SaaS connector registry
- vendoring external binaries for convenience
- hidden forks of upstream support skills
- profile-specific install logic inside the manifest schema
- evaluator-specific products and consumer-owned behavior evaluators
