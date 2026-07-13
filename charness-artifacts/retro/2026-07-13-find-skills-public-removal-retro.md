# Find-Skills Public Removal Session Retro
Date: 2026-07-13

## Mode

session

## Context

This session removed the public `find-skills` workflow and its free-text recommendation engine, retained the session hook as a small compatibility surface, and introduced a deterministic capability catalog for hidden support and integration inventory. The conclusion is strong: it is backed by the working-tree diff, focused tests, slice-closeout output, and a fresh-eye critique that moved from BLOCK to PASS.

## Evidence Summary

- `charness-artifacts/critique/2026-07-13-find-skills-public-removal.md` records the pre-change boundary, two remediation rounds, and final fresh-eye PASS.
- `charness-artifacts/retro/2026-07-13-020003-packet.md` maps the changed paths to their owning validation surfaces.
- The deterministic catalog, hook, setup, achieve, Cautilus-registry, and packaging test groups passed before this retro; the final verification lock remains the closeout step after persistence.

## Waste

The initial removal pass treated the public skill directory and obvious router calls as the primary boundary. Active contract references remained in bootstrap and achieve surfaces, so the fresh-eye reviewer needed two BLOCK/remediation cycles. The transferable waste was not broad exploration; it was declaring the removal matrix after mutation instead of before it.

## Critical Decisions

- Remove semantic recommendation logic entirely and let installed skill metadata plus model judgment own ordinary routing. This avoids maintaining a second, lower-quality intent classifier.
- Keep only deterministic code for inventory and exact path resolution under `charness catalog`; inventory is useful, but it must not pretend to recommend a workflow.
- Retain legacy hook filenames, adapter input, and marker cleanup as explicit compatibility boundaries, while changing the canonical intent to `session_routing`.
- Preserve release/install state as an unverified future boundary. Source and checked-in plugin export change here; the currently installed cache is not silently rewritten.

## Expert Counterfactuals

- Engelbart's system-improving lens would design the tool, language, and method together at the start: a removal matrix naming active contracts, generated exports, compatibility aliases, historical artifacts, and installed-runtime state; the deterministic catalog and its tests would be specified as the replacement control surface in that same matrix.
- A direct first-reader lens would demand one negative acceptance statement before coding: no active public skill, free-text matcher, mandatory router invocation, or generated export may remain; every surviving `find-skills` token must be classified as compatibility or history.

## Sibling Search

- same layer: active skill, doc, test, and eval references | decision: same waste, fix now | proof: repository residue scans plus fresh-eye review removed active invocations and obsolete scenarios
- abstraction up: surface registry, packaging export, current-pointer ownership, and setup-generated AGENTS text | decision: same waste, fix now | proof: dedicated `capability-catalog` surface, synced plugin mirror, and closeout validators passed
- specialization down: legacy hook filename, adapter intent input, marker cleanup, and compatibility tests | decision: intentional boundary | proof: canonical `session_routing` output is asserted while legacy inputs remain isolated and tested
- mental-model siblings: installed v0.66.4 plugin cache and historical dated artifacts | decision: intentional boundary | proof: this slice performs no release or installed-machine update and active contracts do not source those historical records

## Next Improvements

- workflow: for future public-surface removal, lock a five-bucket matrix before mutation: active contract, generated export, compatibility alias, history, and external installed state.
- capability: use `charness catalog list` only for deterministic hidden-capability availability; keep task routing in installed metadata and model judgment.
- memory: keep the critique and this retro with the slice so future removals inherit both the negative acceptance criteria and the compatibility classification.

## Packet Consumed

Packet Consumed: charness-artifacts/retro/2026-07-13-020003-packet.md

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-13-find-skills-public-removal-retro.md
