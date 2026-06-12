# Critique Review
Date: 2026-06-12

## Decision Under Review

Ship slice 3 of `charness-artifacts/goals/2026-06-12-quality-cadence-duplicate-followup.md`: use the `nose` advisory to select one extractable duplicate family, then replace repo-owned adapter scalar helpers with the shared `scripts.adapter_lib.optional_string` / `optional_string_list` helpers while leaving portable skill-local copies alone.

## Failure Angles

- API and coverage compatibility (`019eb95a-c0aa-73f0-82b5-11c6cebddb0e`): no Act Before Ship findings; requested two cheap direct assertions for changed scalar rejection paths.
- Duplicate evidence and export integrity (`019eb95a-ed83-7d81-b3b5-6504c1e31327`): no Act Before Ship findings; requested recording live `nose` numbers and describing the remaining reported family as scalar helper-shaped, not purely `_string`.

## Counterweight Pass

- The two angle reviewers agreed that refactoring portable skill-local adapter copies is out of scope because those scripts are intentionally self-contained package code.
- Export drift concern was cleared: `sync_root_plugin_manifests.py` regenerated the plugin mirrors, and the touched plugin files import the exported shared helper through `plugins/charness/scripts/adapter_lib.py`.
- The focused cleanup reduced the advisory signal from 524 to 523 total ranked families and from 3073 to 3045 duplicated lines in the top report. The selected scalar helper-shaped family moved from 15 files / 112 duplicated lines to 11 files / 84 duplicated lines.
- Counterweight reviewer `019eb95d-f2b2-78a3-abaa-cdedf6f9c1f3` found no Act Before Ship findings after the folded tests; its only Bundle Anyway correction was the stale test line reference fixed below.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_proof_semantics_adapter.py:198 | action: fix | note: direct verifier-ref scalar rejection now pins the changed `optional_string` call in `proof_semantics_adapter_lib`
- F2 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_quality_bootstrap.py:182 | action: fix | note: direct `validate_simple_adapter_data` non-string scalar rejection now pins the shared simple adapter helper path
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/inventory_nose_clones.py | action: document | note: goal closeout records live nose after-cleanup numbers: 523 total families and 3045 duplicated lines in the top report
- F4 | bin: over-worry | evidence: strong | ref: skills/public/debug/scripts/resolve_adapter.py:40 | action: defer | note: remaining skill-local scalar helpers are portable package boilerplate and are not part of this repo-owned helper cleanup
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/adapter_lib.py:264 | action: defer | note: a future table-driven scalar contract across adapter libraries could help later duplicate cleanup slices

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: host returned agent IDs `019eb95a-c0aa-73f0-82b5-11c6cebddb0e`, `019eb95a-ed83-7d81-b3b5-6504c1e31327`, and `019eb95d-f2b2-78a3-abaa-cdedf6f9c1f3`; no provider-side application confirmation exposed.

## Fresh-Eye Satisfaction

parent-delegated — two bounded angle reviewers and one separate counterweight reviewer completed through the `multi_agent_v1.spawn_agent` / `wait_agent` host tool path. No remaining Act Before Ship findings were reported after the folded tests and wording corrections.
