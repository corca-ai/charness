# Agent Production Runtime Quality Critique

- Date: 2026-05-17
- Target: `quality` lens and reference for production LLM/agent runtime review
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: n/a (bounded source/diff review)

## Change

Add a provider-neutral `quality` review lens for production LLM and agent
runtimes. The lens reviews cache/cost economics, overload fallback, retry
idempotency, streaming stall recovery, model routing economics, and telemetry as
evidence questions. It does not add a public skill, provider wrapper, runtime
library, static detector, adapter surface, or behavior-test runner.

## Design Angles

- Design reviewer A checked concept boundary, provider neutrality, trigger
  evidence, deterministic-vs-behavior proof split, and overfitting risk.
- Design reviewer B checked production-runtime trigger precision, proof
  vocabulary reuse, inapplicability handling, naming, dogfood, and test
  brittleness.
- Counterweight reviewer separated the hard requirements from deferred
  detection infrastructure.

## Design Counterweight Triage

### Act Before Ship

- Keep the change inside `quality`; do not create a new public skill, provider
  wrapper, retry library, or behavior-test runner.
- Trigger only from production runtime evidence such as serving-path model
  clients, model routing/fallback config, streaming endpoints, tool/action
  queues, user-facing agent product docs, or runtime telemetry.
- Exclude eval fixtures, skill docs, prompt examples, harness-only agent
  orchestration, and offline benchmark scaffolding by themselves.
- Reuse existing `behavior-testing` and external capability proof ladder
  vocabulary instead of inventing a separate proof taxonomy.
- Treat cache, fallback, idempotency, streaming, and model routing as review
  questions with proof or explicit non-applicability, not mandatory
  architecture.

### Bundle Anyway

- Add a concise `SKILL.md` anchor plus a separate inventory-dispatch section.
- Add dogfood evidence because the reviewed `quality` consumer contract changed.
- Pin boundary and trigger anchors in deterministic tests without adding a
  brittle static detector.

### Over-Worry

- Blocking on a full taxonomy of all provider/runtime signs.
- Treating every review question as mandatory for every runtime.
- Requiring broad provider coverage or live provider tests in routine quality
  review.

### Valid But Defer

- Static detector or inventory script.
- Adapter fields for provider/runtime profiles.
- Cautilus scenarios without a named behavior log or prompt regression.
- Provider-specific appendices.

## Implementation Critique

### Act Before Ship

- Include the new source and plugin reference files in the commit:
  `skills/public/quality/references/agent-production-runtime.md` and
  `plugins/charness/skills/quality/references/agent-production-runtime.md`.

### Bundle Anyway

- The implemented diff keeps the reference provider-neutral and routes from
  `quality` without adding a new skill or runner.
- Trigger gating appears in both the new reference and inventory dispatch.
- The behavior-testing reference links production runtime behavior only where
  deterministic tests cannot prove quality of fallback, partial-output recovery,
  cheap-first routing, or escalation.
- The plugin export was synced.

### Over-Worry

- The Anthropic wording is a negative boundary, not provider coupling.
- Phrase-based tests are acceptable here because they pin routing anchors and
  section presence while the repo still uses migration-time prose guards.

### Valid But Defer

- A future dogfood scenario can test undertrigger/overtrigger behavior against
  concrete consumer repos.
- A structural export-sync validator for newly added reference files can wait
  unless this untracked-file hazard recurs.

## Scenario Review

`run_slice_closeout.py` required public-skill scenario review because this slice
changes `quality`. The reviewed dogfood scaffold for `quality` remains the
current slow-gate/runtime-economics consumer prompt from
`docs/public-skill-dogfood.json`; `python3 scripts/suggest_public_skill_dogfood.py
--repo-root . --skill-id quality --json` still matches that route,
`expected_skill`, `expected_artifact`, validation tier, and acceptance evidence.

Decision: keep the existing reviewed consumer prompt and add observed evidence
for the new agent-production-runtime lens. This slice changes `quality` review
coverage, not the top-level routing prompt shape. The repo adapter reported
`run_mode: ask`, `next_action: none`, and `quality` as `hitl-recommended`, so no
live Cautilus run or maintained evaluator scenario is required without a
log-backed behavior proof request.

## Proof

- `pytest -q tests/quality_gates/test_quality_skill_docs.py tests/quality_gates/test_docs_and_misc.py::test_quality_skill_discloses_advisory_and_prompt_asset_root_boundary tests/quality_gates/test_docs_and_misc.py::test_cautilus_guidance_does_not_use_generic_review_triggers`: 17 passed.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`: passed.
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`: reviewed scaffold unchanged; dogfood observed evidence updated.
- `python3 scripts/validate_skills.py --repo-root .`: passed after fixing
  relative shared-reference paths and keeping `quality/SKILL.md` at 200 lines.
- Broader pytest surface:
  `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`:
  996 passed, 4 skipped.

## Next Move

Run the remaining slice closeout commands, commit the source skill, synced
plugin export, dogfood evidence, tests, and this critique artifact together.
