# Resolution Critique - nose adapter helper extraction

Date: 2026-06-15
Scope: nose 0.10.0 clone slice
Reviewer: bounded fresh-eye critique subagent, read-only shared parent worktree.

## Slice under review

Reduce extractable adapter-helper duplication surfaced by nose 0.10.0 without
chasing per-skill bootstrap/import/main boilerplate that remains intentional
for portable skill execution.

Changed surfaces:

- `scripts/adapter_lib.py`
- `scripts/announcement_adapter_lib.py`
- `skills/public/achieve/scripts/achieve_adapter_policy.py`
- `skills/public/create-skill/scripts/resolve_adapter.py`
- `skills/public/debug/scripts/resolve_adapter.py`
- `skills/public/find-skills/scripts/resolve_adapter.py`
- `skills/public/gather/scripts/resolve_adapter.py`
- `skills/public/hitl/scripts/resolve_adapter.py`
- `skills/public/hotl/scripts/resolve_adapter.py`
- `skills/public/impl/scripts/resolve_adapter.py`
- `skills/public/release/scripts/resolve_adapter.py`
- `skills/public/retro/scripts/resolve_adapter.py`
- checked-in `plugins/charness/**` mirrors for those files
- `tests/test_adapter_lib.py`

## Causal Review

JTBD: remove genuine maintenance duplication where resolver helpers had
identical optional string/list/bool and list-field-state semantics, while
leaving portability boilerplate alone.

Classification confirmation: improvement/refactor, not a bug. The nose findings
are advisory refactoring candidates.

Root cause: adapter resolver scripts had grown local copies of small validation
helpers even though `scripts/adapter_lib.py` already owned adjacent YAML and
adapter helper behavior.

Invariant proof: the new helpers preserve the removed return/error shapes:
`None` remains absent, wrong types append the same field-specific message, and
list field state remains `unset` / `explicit-empty` / `configured`.

Detection gap: before this slice, direct tests did not pin the new shared helper
API. Fresh-eye critique identified that as cheap confidence to bundle.

Fresh-Eye Satisfaction: parent-delegated.

## Resolution Critique Findings

### Act Before Ship

None.

### Bundle Anyway

- Add direct tests for the new shared helper API.

Disposition: bundled. `tests/test_adapter_lib.py` covers optional string,
string-list, bool, and list-field-state behavior.

### Valid but Defer

- Broader `validate_adapter_data` framework consolidation remains real design
  work and is not this slice's quick helper extraction.
- A bare copied `achieve` skill directory without root `scripts/adapter_lib.py`
  would fail earlier because `achieve_adapter_policy.py` now loads the shared
  helper at module import time. Packaged Charness requires the shared
  `scripts/adapter_lib.py`, so this is acceptable unless standalone single-skill
  copying becomes a supported distribution boundary.
- Maintained evaluator scenario mutation is unnecessary for this slice. The
  changed public skill files are adapter helper consumers; the public routing
  prompts and artifact expectations returned by `suggest_public_skill_dogfood.py`
  remain unchanged, and `evals/cautilus/scenarios.json` already covers the
  evaluator-required changed skills with adapter/bootstrap scenarios.

### Over-Worry

- Do not chase per-skill bootstrap/import/main duplication in this slice. That
  duplicate shape is intentional portability boilerplate and remains outside the
  goal's selected nose fixes.

## Structured Findings

- bin: bundle-anyway | evidence: strong | ref: tests/test_adapter_lib.py | action: fix | note: add direct coverage for optional_bool and list_field_state
- bin: valid-but-defer | evidence: strong | ref: charness-artifacts/quality/latest.md | action: defer | note: broader validate_adapter_data consolidation is design work, not this slice
- bin: valid-but-defer | evidence: moderate | ref: skills/public/achieve/scripts/achieve_adapter_policy.py | action: defer | note: standalone single-skill copying without scripts/adapter_lib.py is not a supported packaging boundary
- bin: valid-but-defer | evidence: strong | ref: evals/cautilus/scenarios.json | action: defer | note: no evaluator scenario mutation for helper-only adapter refactor
- bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/inventory_nose_clones.py | action: defer | note: per-skill bootstrap/import/main boilerplate is intentionally left alone

## Reviewer Tier Evidence

- requested tier: default
- requested spawn fields: inherited parent model and reasoning settings
- host exposure state: host-defaulted
- application state: spawn tool accepted reviewer agent id `019ecb33-4228-7771-bf4e-c8d4228c0b98`; reviewer-tier application details are host-hidden.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. The bounded reviewer completed
read-only review; the suggested helper test was bundled before commit.

## Verification

- `pytest -q tests/test_adapter_lib.py tests/test_announcement_adapter_lib.py tests/quality_gates/test_achieve_adapter_policy.py tests/quality_gates/test_gather_provider.py tests/quality_gates/test_hotl_adapter.py tests/quality_gates/test_bootstrap_visibility.py tests/quality_gates/test_retro_memory.py tests/quality_gates/test_release_publish.py` passed.
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` reported nose 0.10.0 at 20 shown families, 551 ranked families, and 2002 duplicate lines after the slice. The before sample in this goal was 20 shown families, 559 ranked families, and 2036 duplicate lines.
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id <changed-skill> --json` was reviewed for achieve, create-skill, debug, find-skills, gather, hitl, hotl, impl, release, and retro; existing dogfood cases remain the right public contract coverage.
