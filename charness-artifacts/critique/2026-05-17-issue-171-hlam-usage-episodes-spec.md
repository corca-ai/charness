# Critique: Issue #171 H-LAM/T Usage Episodes Spec

## Execution

completed

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

- `charness-artifacts/critique/2026-05-17-080239-packet.md`

## Target

spec critique

## Change

The pending contract was
`charness-artifacts/spec/issue-171-hlam-usage-episodes.md`, introducing a
new cross-product `usage-episodes` integration/schema plan for Ceal, Crill,
and other user-facing c-family products.

## Angles

- H-LAM/T product-concept fit for Ceal/Crill
- privacy, retention, and source-boundary risk
- implementation and validation fit in this repo
- counterweight triage over all findings

## Counterweight Triage

### Act Before Ship

- Add one required LAM field: `agent_action` with `surface` and optional
  `capability_ref`.
- Add required `t_status`: `none`, `candidate`, `promoted`, `rejected`.
- Keep `first_value_ref` and `t_link` as opaque product-owned refs with
  minimal `kind`, `ref`, and optional repo-relative `path`.
- Specify `.agents/usage-episodes-adapter.yaml`, `version`, `enabled`,
  `storage_path`, `events`, `rotation`, absent behavior, and disabled behavior.
- Mark emitted JSONL as local generated state, not committed except curated
  fixtures.
- Require tests for `no_adapter`, `enabled:false`, malformed record, valid
  record, one Ceal Slack/GitHub fixture, and one Crill product fixture.

### Bundle Anyway

- Make `episode_id` explicitly opaque and non-PII.
- Clarify `selected_job` as the privacy-safe human/job intent bucket.
- Declare enum boundaries.
- Give the seed helper parity with existing setup helpers.
- Add a deferred reopen trigger for cross-repo aggregation.

### Over-Worry

- Do not merge `usage-episodes` into `t-events`.
- Do not require H-LAM/T inventory consumption in this slice.
- Do not ban all URL-like references categorically; ban embedded raw,
  source-rich, or user-identifying content.

### Valid But Defer

- `same_context_repeat_rate` summarization.
- `context_fingerprint`.
- automaticity surveys or scoring.
- Ceal/Crill runtime emit hooks.

## Contract Updates

The spec was updated with `agent_action`, `t_status`, opaque reference shape,
adapter semantics, retention/privacy boundary, fixture acceptance checks, and
the critique outcome.

## Next Move

Proceed to the first implementation slice from the updated spec.
