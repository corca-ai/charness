# Retired Hook Ledger Cleanup Contract
Date: 2026-07-13

## Problem

v1.0.0 removes the `find-skills` runtime/configuration surface, but an
already-installed pre-v1 hook-state key can survive in the local host-state
ledger. Settings become canonical while aggregate status remains red. <!-- reproduction-source -->

## Capability Contract

An operator upgrading from a pre-v1 install can reconcile hooks once and obtain canonical settings plus an `in_sync` state ledger, without re-enabling or accepting any retired configuration.

## Current Slice

Delete the two pre-v1 ledger-key shapes during the existing session-routing install and uninstall lifecycles, preserve all canonical and foreign state, mirror the change into the plugin export, and publish the correction as v1.0.1.

## Fixed Decisions

- Retired names exist only in one-way deletion inventory and tests.
- Cleanup runs for Claude and Codex on both install and uninstall.
- Settings cleanup and ledger cleanup share the existing `retired_state_cleanup` result channel.

## Probe Questions

- None; the maintainer install reproduced the state-only residue and the local patch removed it.

## Deferred Decisions

- None for this retirement. A future hook rename must add its own settings+ledger deletion inventory.

## Non-Goals

- Accepting `find_skills_routing` as adapter input, schema, CLI, or status API.
- Rewriting arbitrary foreign state entries.
- Changing canonical session-routing intent or hook commands.

## Deliberately Not Doing

Manual host-state JSON edits are rejected because they repair one machine without restoring the lifecycle invariant for upgrades.

## Constraints

- Preserve canonical and foreign ledger keys byte-for-value.
- Keep source and plugin mirror identical.
- Treat live maintainer state as external-seam proof, not a universal frequency claim.

## Success Criteria

- State-only retired keys are removed under both hosts and operations.
- Canonical/foreign state survives.
- Installed status after cleanup reports `in_sync: true`, `drift: []`, and no dangling retired script.
- v1.0.1 public release and install refresh read back successfully.

## Acceptance Checks

- unit: four state-seeded host/operation regressions plus focused lifecycle/registry tests.
- integration: apply the local deletion helper to the managed checkout, then run installed `charness session-capture status --json`.
- manual: inspect the plugin mirror and release/readback payloads.

## Boundary Ownership

moved-to-owner — session-routing lifecycle code owns retirement of both settings and its ledger state; aggregate status remains the final consumer.

## Critique

- Interrupt Source: retired-hook-ledger-survives-reconcile
- Seam Summary: installed host settings and Charness host-state ledger
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the root cause and live disconfirmer are confirmed; the patch is deletion-only and regression-covered.
- What Disproving Observation Is Resolved: canonical settings no longer imply a clean ledger; the final status consumer must also pass.

## Canonical Artifact

This file is the patch contract; the debug artifact retains the RCA and live proof.

## First Implementation Slice

Add `_cleanup_retired_state_entry`, call it from install/uninstall for both hosts, seed state-only tests, sync the plugin mirror, then verify the installed final consumer.
