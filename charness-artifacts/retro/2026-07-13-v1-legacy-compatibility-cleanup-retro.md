# v1 Legacy Compatibility Cleanup Session Retro
Date: 2026-07-13

## Mode

session

## Context

This unit removed the remaining active `find-skills` compatibility surface before the v1.0.0 release: runtime/schema aliases, adapter paths, legacy module and script APIs, evaluator assumptions, tests, active docs, and generated plugin copies. The only retained old literals delete already-installed Charness-owned hook state.

## Evidence Summary

- `charness-artifacts/critique/2026-07-13-find-skills-legacy-removal-v1-release-critique.md` records three pre-change angles, counterweight triage, and a post-change fresh-eye PASS for the code slice.
- Verification lock passed the standing pytest suite, repository validators, plugin sync checks, agent-runtime tests, and mutation-context coverage production.
- `charness-artifacts/retro/2026-07-13-033644-packet.md` maps the slice to export, control-plane, prompt, catalog, and repo-code owners.

## Waste

The earlier removal deliberately retained compatibility aliases, which made the public skill disappear while active names and inputs still taught its old ownership. The extra pass was caused by treating “old state must be removable” and “old input remains supported” as one compatibility bucket.

## Critical Decisions

- Remove every old input and API instead of carrying a shim into v1.
- Preserve only one-way cleanup for Charness-owned installed hook entries, under canonical retired-state terminology and tests.
- Use a major bump because existing adapter keys and filenames require migration.
- Keep dated audit artifacts immutable; active source and operator surfaces alone define the current product.

## Expert Counterfactuals

- Engelbart's system-improving lens would define the migration mechanism alongside the new language from the first removal slice: canonical routing/catalog terms, rejected old inputs, and one-way state deletion as three explicit contracts.
- A direct release-operator lens would require upgrade and rollback instructions before calling a compatibility deletion complete, because code purity does not clean an already-installed host entry by itself.

## Sibling Search

- same layer: other host-hook intents and adapters | decision: diagnostic-only | proof: registry and schema scan found no second old-input fallback in the touched sibling hooks
- abstraction up: schema, CLI status, active docs, evaluator fixtures, and plugin export | decision: same waste, fix now | proof: canonical names landed together and sync/validators passed
- specialization down: retired marker and script literals in cleanup tests | decision: intentional boundary | proof: the code only deletes owned state and never accepts those names as configuration
- mental-model siblings: v1 release notes and installed-machine update | decision: same waste, fix now | proof: release critique requires migration, rollback, public readback, and post-publish refresh before publication closes

## Next Improvements

- workflow: every breaking removal plan must separate supported inputs, active internal names, historical evidence, and one-way deletion of already-owned external state before mutation.
- capability: keep cleanup-only literals mechanically confined to a canonical retired-state inventory with tests that assert deletion, never fallback acceptance.
- memory: bind this distinction into the v1 critique and release notes so future compatibility cuts do not reintroduce a shim to solve cleanup.

## Packet Consumed

Packet Consumed: charness-artifacts/retro/2026-07-13-033644-packet.md

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-13-v1-legacy-compatibility-cleanup-retro.md
