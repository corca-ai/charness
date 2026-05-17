# Critique: Issue #171 H-LAM/T Usage Episodes Implementation

## Execution

completed

## Fresh-Eye Satisfaction

parent-delegated

## Target

code critique

## Change

The implementation added the `usage-episodes` integration surface, JSON
schemas, adapter example, validator, setup seed helper, plugin export, and
focused tests for H-LAM/T product usage episodes.

## Angles

- schema and validator correctness against the updated spec
- privacy, retention, and source-boundary risk
- repo integration, packaging, and compatibility with `t-events`
- counterweight triage over implementation findings

## Counterweight Triage

### Act Before Ship

- Fix `t_link` semantics so non-`none` `t_status` may omit `t_link`, while
  `t_status: none` rejects `t_link`.
- Enforce `raw_prompt: false` and `raw_transcript: false` in the adapter schema.
- Reject absolute paths and parent traversal in adapter `storage_path` and
  opaque reference `path`.
- Add `.charness/usage-episodes/` to `.gitignore`.

### Bundle Anyway

- Add negative tests for the above boundaries.
- Add bounded structural limits on opaque refs: max length and no control or
  newline characters.
- Prefer repo-relative validator paths in JSON output.
- Add a focused checked-in plugin export assertion for `usage-episodes`.

### Over-Worry

- Do not require the adapter `privacy` block whenever `enabled: true`.
- Do not have the seed helper mutate consumer `.gitignore` in this slice.
- Do not ban all URL-like refs categorically.

### Valid But Defer

- Timestamp `format` enforcement with a `FormatChecker`.
- Rotation enforcement in the validator.
- Operator-facing docs mention for `validate_usage_episodes.py`.
- H-LAM/T inventory consumption and Ceal/Crill runtime hooks.

## Resolution

The act-before-ship and cheap bundle items were implemented:

- `episode.schema.json` now allows non-`none` `t_status` without `t_link` and
  still rejects `t_link` when `t_status` is `none`.
- `manifest.schema.json` uses `const: false` for raw prompt/transcript flags.
- `storage_path` and reference `path` reject absolute and traversal paths.
- opaque refs have a bounded length and reject control/newline characters.
- validator JSON output uses repo-relative paths when possible.
- `.gitignore` ignores `.charness/usage-episodes/`.
- tests cover schema, validator, seed helper, boundary negatives, and checked-in
  plugin export parity.

## Scenario Review

`python3 scripts/plan_cautilus_proof.py --repo-root . --json` returned
`next_action: none` with `scenario_registry_review_required: true` for the
`setup` skill core change. The representative maintained setup scenario is
still the partial-normalization contract in `evals/cautilus/scenarios.json`;
that scenario does not need to learn the new product-episode seed path because
this slice only adds optional setup guidance for product repos and does not
change setup routing, repo-mode detection, or normalization behavior.

The current `setup` consumer contract was instead frozen in
`docs/public-skill-dogfood.json` by adding observed evidence for
`seed_usage_episodes_adapter.py`. No maintained Cautilus scenario registry
mutation is needed for this slice.

## Next Move

Run closeout gates, then commit the complete #171 slice.
