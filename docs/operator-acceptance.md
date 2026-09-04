# Operator Acceptance

> Status: conditional (operator takeover path)
> Source of truth: functional checks, the active Goal Run parent/cursor, and the active plan
> Last verified: 2026-09-04

This document translates active work into operator-owned acceptance runs. The
plan of record is the active Goal Run parent ([goal lifecycle](./goal-lifecycle.md)).
Use this page when you want to take over one item directly instead of asking an
agent to rediscover the whole repo state. A consumer may add an optional
roadmap surface when active ordered work requires it.
Each item names the ownership seam, read-first surfaces, and acceptance bar. Restate that material in your own prompt instead of copying another embedded prompt block into chat.

## Shared Start

Start from a clean tree and the small quality lane
([verification and export](./development.md#verification-and-export)). If the
work touches integrations or packaging, read
[control plane](./control-plane.md) and
[public skill validation](./public-skill-validation.md).

## Progressive Operator Path

See [docs/operator-progressive-path.md](./operator-progressive-path.md) for the per-horizon operator capability map (Day 1, Week 8, Month 6).

## Remaining Items

The items closed with their Goal Run are recorded in
[operator-acceptance checklists](../charness-artifacts/goal-runs/765/2026-09-03-operator-acceptance-checklists.md).

### Run Managed CLI Install Experiments

Focus: confirm that the managed install/update path changes the host-visible payload, not only the source checkout.

Read first:

- [README.md](../README.md) — product framing, managed install quick start, and everyday CLI commands.
- [docs/host-packaging.md](./host-packaging.md) — export contract for host plugin layouts and its source-of-truth surfaces.
- [packaging/charness.json](../packaging/charness.json) — shared packaging manifest: identity, version, bundle inputs, host export paths.

Useful local commands (the runners refresh the generated mirror themselves:
[generated surfaces](./operating-contract.md#generated-surfaces)):

```bash
python3 scripts/plugin_export/validate_packaging.py --repo-root .
python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
charness doctor
charness update all
charness tool update agent-browser
```

Suggested operator runs:

- bootstrap or reuse the managed checkout under `~/.agents/src/charness` with
  `charness init`; use [`./init.sh`](../init.sh) only when the binary is not already
  available on PATH
- make an explicit upstream payload change that should be visible in a loaded
  skill or plugin manifest
- run `charness update`
- run `charness update all` when the acceptance run also needs tracked external
  binaries and bundled support skill surfaces refreshed
- verify Claude by checking that the changed payload is reflected in the
  installed host copy after the documented restart/reload step
- if you need to rerun the update-propagation experiment locally, prefer
  `pytest -q tests/charness_cli/test_update_propagation.py` plus a human host
  spot-check instead of turning it back into a default every-session task
- if you want the full local install/update regression suite before or after
  host testing, run [`./scripts/self-validate-install-update.sh`](../scripts/self-validate-install-update.sh)

Acceptance is the install/update/doctor contract on
[host packaging](./host-packaging.md), [cli-reference](./cli-reference.md), and
[control plane](./control-plane.md). Run the commands above; do not recopy
those semantics here.

## Closeout Rule

[Implementation discipline](./implementation-discipline.md) and
[goal lifecycle](./goal-lifecycle.md) own mutate/verify/publish and cursor
advance.
