# Spec: Issue #171 - H-LAM/T Usage Episodes

Source: https://github.com/corca-ai/charness/issues/171

## Problem

The c-families projects need a shared way to reason about habit and usage
context in products that have real users, especially Ceal and Crill. The goal
is not to add analytics to Charness itself. The goal is to let user-facing
products record privacy-bounded usage episodes that can later become H-LAM/T
evidence.

For this slice, an episode means:

```text
H: an actor in a bounded product context
LAM: the agent/tool action and first value produced
T: the feedback or durable improvement link that can change future behavior
```

Raw usage and retention are insufficient. The important signal is whether a
similar context repeatedly leads to a valuable action, whether the product can
route the next action with less re-explanation, and whether repeated use feeds
back into memory, specs, skills, evaluation, or product workflow changes.

## Current Slice

Define a portable usage episode contract that consumer products can opt into:

- a new `integrations/usage-episodes/` integration surface
- a JSON schema for `usage_episode` records
- an adapter example for consumer repos
- a validator for episode JSONL files
- a `setup` seed helper for repos that want this capture surface

This is a schema and workflow substrate only. Ceal, Crill, Cautilus, and other
products keep ownership of their runtime capture points and product-specific
core actions.

## Fixed Decisions

- Charness will not become a product analytics backend for #171.
- Charness will provide a shared vocabulary and validation surface for
  user-facing product usage episodes.
- `usage-episodes` is separate from `t-events`.
  - `t-events` records Charness skill/T-loop lifecycle evidence.
  - `usage-episodes` records product runtime episodes from Ceal, Crill, or
    similar consumer products.
- The shared schema stores product-safe references, not raw transcripts.
- User identity stays host/product-owned. The shared schema uses privacy-safe
  actor and context buckets by default.
- Episode ids and references must be opaque and non-PII. They must not be
  derived from user identity, raw message body, email address, or source text.
- Automaticity is not inferred from behavior logs in this slice. It may only be
  represented later through explicit host/product-owned prompts or survey
  results.
- Each consumer product must define its own `core_action` and `first_value_ref`.
  Charness only validates the cross-product envelope.

## Product Vocabulary

The v1 episode envelope should include:

- `product_id`: product emitting the episode, for example `ceal` or `crill`
- `episode_id`: product-owned opaque stable id for this episode; non-PII and
  not user-identity-derived
- `actor_kind`: coarse actor category such as `human`, `operator`,
  `developer`, `agent`, or `agent_on_behalf`; closed v1 enum
- `context_bucket`: privacy-safe context class, for example `slack_thread`,
  `github_issue`, `repo_task`, `review`, or `incident`; product-owned string
- `context_ref`: optional privacy-safe stable reference for recognizing repeated
  use in the same product context without carrying raw source or user identity
- `entry_point`: how the episode started, for example `mention`, `command`,
  `ui`, `scheduled`, `delegated`, or `api`; product-owned string
- `trigger_type`: why the episode started, for example `explicit_request`,
  `correction`, `failure`, `review_request`, or `follow_up`; product-owned
  string
- `selected_job`: privacy-safe human/job intent bucket, not a raw user prompt
- `core_action`: product-specific valuable behavior
- `agent_action`: the LAM move that produced value; required object with
  `surface` and optional `capability_ref`
- `first_value_ref`: opaque product-owned reference to the first valuable
  output
- `outcome_status`: `delivered`, `abandoned`, `corrected`, `escalated`, or
  `failed`; closed v1 enum
- `feedback_signal`: optional product-owned signal such as `accepted`,
  `edited`, `ignored`, `retried`, `follow_up_requested`, or
  `human_confirmed`
- `t_status`: required T lifecycle state: `none`, `candidate`, `promoted`, or
  `rejected`
- `t_link`: optional link to a durable T-loop artifact such as a spec, lesson,
  eval case, routing change, memory update, or issue; only meaningful when
  `t_status` is not `none`

Reference objects such as `first_value_ref` and `t_link` use a minimal shape:

- `kind`: product-owned reference class
- `ref`: opaque product-owned identifier or locator
- `path`: optional repo-root-relative path when the reference points into a
  repo artifact

Reference objects must not embed prompt text, transcript excerpts, source body,
message body, author identity, raw user identity, or copied source content.

The consumer adapter path is `.agents/usage-episodes-adapter.yaml`. Its v1
shape mirrors `t-events` where useful:

- `version: 1`
- `enabled: true|false`
- `storage_path`, default `.charness/usage-episodes`
- `events`, default `["usage_episode"]`
- optional `rotation.max_files` and `rotation.max_size_mb`
- optional `privacy.policy_ref` naming the product-owned privacy/retention
  policy when raw source material is retained outside the shared schema

When the adapter is absent, Charness validators report `no_adapter` rather than
failing by default. When the adapter is present with `enabled: false`,
validators report `disabled`. Emitted JSONL records are generated local state
and should not be committed except as intentionally curated test fixtures.

## Probe Questions

- Should `same_context_repeat_rate` be computed by each product, or should
  Charness provide an offline summarizer over JSONL records?
- Should `automaticity` remain survey-only forever, or should a future schema
  add a separately named product-owned explicit score?
- Which product should dogfood first: Ceal because it has Slack/GitHub action
  surfaces, or Crill because it may have a more direct end-user workflow?
- Should H-LAM/T inventory consume `usage-episodes` directly, or should
  products first promote selected episodes into `t-events`/retro/spec evidence?

## Deferred Decisions

- Cross-repo aggregation of usage episodes.
- Any remote analytics storage, dashboards, or background daemons.
- Raw transcript retention/redaction policy.
- User-level identity joins across products.
- Product-specific emit hooks inside Ceal or Crill.
- Automaticity survey wording and scoring.

Cross-repo aggregation, identity joins, or raw source retention may only reopen
after a separate privacy review and product-owned consent/policy design exist.

## Non-Goals

- Adding a new public `usage-context` skill.
- Changing Ceal or Crill runtime behavior in this Charness slice.
- Inferring habits from private messages or raw prompt history.
- Replacing `t-events` or the Skill-T mechanism inventory.
- Making every Charness consumer repo emit usage episodes by default.

## Deliberately Not Doing

- Do not fold `usage_episode` into `integrations/t-events/event.schema.json`.
  The current t-events contract is skill-lifecycle oriented; mixing product
  runtime episodes into it would blur ownership and make consumer privacy
  policy harder to reason about.
- Do not add raw `user_id`, raw prompt, raw transcript, or source body fields
  to the shared v1 schema. Products may keep those under their own retention
  policy, but the shared substrate should remain portable and low-risk.
- Do not add automaticity scoring in v1. A weak behavior-log proxy would look
  more scientific than it is.

## Constraints

- Keep Charness portable: consumer runtimes own emission and storage decisions.
- Keep capture opt-in through an adapter file.
- Store generated/high-churn episode records under `.charness/` by default.
- Keep schema validation deterministic and runnable without network access.
- Use repo-root-relative paths for product-owned references when a reference
  points into a repo.
- Preserve current `t-events` semantics and validators.

## Success Criteria

- A consumer repo can opt into usage episode validation with one adapter file.
- A consumer product can write JSONL `usage_episode` records without importing
  Charness as a runtime analytics service.
- The validator distinguishes absent opt-in, disabled opt-in, invalid records,
  and valid records.
- The v1 schema can represent at least one Ceal-shaped Slack/GitHub episode and
  one Crill-shaped product episode without raw transcript or user identity.
- The first implementation slice leaves the next Ceal/Crill adoption point
  obvious.

## Acceptance Checks

- `python3 scripts/validate_usage_episodes.py --repo-root . --adapter-path <fixture>`
  validates a good fixture and rejects a malformed fixture.
- Tests cover `no_adapter`, `enabled: false`, malformed record, valid record,
  one Ceal-shaped Slack/GitHub delegated episode, and one Crill-shaped direct
  product workflow episode.
- The Ceal and Crill fixtures each demonstrate H, LAM, first value, feedback,
  and `t_status` without raw transcript or user identity.
- `python3 -m json.tool integrations/usage-episodes/episode.schema.json` passes.
- `python3 -m json.tool integrations/usage-episodes/manifest.schema.json` passes.
- `python3 skills/public/setup/scripts/seed_usage_episodes_adapter.py --dry-run`
  prints a valid adapter template.
- The seed helper supports `--repo-root`, `--force`, refuses to overwrite by
  default, and its dry-run template validates against the manifest schema.
- Existing `t-events` tests and Skill-T inventory validation still pass.

## Critique

Canonical critique ran with parent-delegated bounded reviewers after the user
explicitly delegated subagents. The critique target was a spec critique over
this artifact, with special attention to:

- whether `usage-episodes` should be separate from `t-events`
- whether the schema is too analytics-shaped and not H-LAM/T-shaped enough
- whether privacy and raw-source boundaries are explicit enough
- whether the first implementation slice is small enough

Act-before-ship items now reflected in this contract:

- add required `agent_action` for the LAM move
- add required `t_status` for T lifecycle state
- add optional `context_ref` for repeated same-context analysis
- keep `first_value_ref` and `t_link` as opaque product-owned references
- specify `.agents/usage-episodes-adapter.yaml` and absent/disabled semantics
- keep emitted JSONL as generated local state by default
- require Ceal/Crill fixtures that prove H, LAM, first value, feedback, and T

Deliberately not changed after counterweight:

- keep `usage-episodes` separate from `t-events`
- do not require H-LAM/T inventory consumption in this slice
- do not ban all URL-like references; ban raw/source-rich/user-identifying
  embedded content

## Canonical Artifact

- This document:
  `charness-artifacts/spec/issue-171-hlam-usage-episodes.md`

## First Implementation Slice

1. Add `integrations/usage-episodes/episode.schema.json`.
2. Add `integrations/usage-episodes/manifest.schema.json`.
3. Add `integrations/usage-episodes/adapter.example.yaml`.
4. Add `scripts/validate_usage_episodes.py` and focused tests.
5. Add `skills/public/setup/scripts/seed_usage_episodes_adapter.py`.
6. Update `setup` guidance to mention the opt-in seed helper.
7. Verify the new slice with targeted tests and unchanged t-events validation.
