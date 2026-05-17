# Critique: Usage Episodes Skill Contract Patch

Date: 2026-05-17

## Execution

- Fresh-Eye Satisfaction: parent-delegated.
- Packet Consumed: `charness-artifacts/critique/2026-05-17-095323-packet.md`.
- Target: `code-critique`.

## Change

The patch changes the user-facing contract for usage episodes after v0.6.0:

- `setup` frames `.agents/usage-episodes-adapter.yaml` seeding as setup skill behavior.
- `setup` keeps `seed_usage_episodes_adapter.py` as implementation detail, not user-facing API.
- `quality` runs the Charness package-root `validate_usage_episodes.py` validator when the adapter exists.
- `quality` treats `no_adapter` and `disabled` as skipped states, not failures.
- ownership overlap is explicit: setup is seed-only; quality is read-only gate.

## Angles

- Problem framing and humane interface: confirmed the patch moves the primary UI from script execution to skill execution. Suggested naming the validator resolution rule so downstream agents can execute without asking humans to translate the contract.
- Diagnostic and operational checklist: initially flagged the test as too prose-only and setup wording as still too helper-forward. Parent patch tightened both: setup now starts with the skill-owned action, and quality names package-root validator resolution.
- Counterweight: no remaining blocker after the parent patch. Exact-prose coverage is acceptable as a bridge because this slice changes skill-contract wording, not runtime capture.

## Counterweight Triage

### Act Before Ship

None.

### Bundle Anyway

None remaining after the validator-resolution and setup-wording edits.

### Over-Worry

- Do not remove the helper name entirely from `setup`; nearby setup bullets name seed helpers, and maintainers still need the implementation breadcrumb.
- Do not expand this patch into Ceal/Crill runtime hooks or usage-episode analytics.

### Valid But Defer

- A full consumer fixture proving `setup` seed -> `quality` gate -> validator execution would be stronger than the current string/contract guard, but it is larger than this patch and should wait for an adoption slice.

## Scenario Review

- `quality` is `hitl-recommended`; the updated `docs/public-skill-dogfood.json`
  evidence is the maintained consumer contract for this slice.
- `setup` is `evaluator-required`, but existing maintained scenarios cover
  adapter bootstrap, inspect states, and compact skill-routing discoverability.
  This patch changes an optional integration seeding contract, so no maintained
  scenario registry mutation is bundled here.
- Mutating `evals/cautilus/scenarios.json` remains ask-before-mutate per repo
  policy.

## Next Move

Ship after deterministic gates remain green.
