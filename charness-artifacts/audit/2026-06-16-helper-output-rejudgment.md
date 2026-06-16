# Audit: Deterministic Helper Output Re-Judgment

Status: active slice proof for #376
Date: 2026-06-16

## Question

Which deterministic helper outputs are only inputs to agent judgment, and does
the operator-facing workflow make that judgment visible before presentation,
mutation, closeout, or next-action selection?

## Reviewed Surfaces

| Surface | Helper output | Required agent judgment | Current disposition |
| --- | --- | --- | --- |
| `handoff` chunked routing | `propose_merges.py` overlap hints and merge policy facts | Re-judge `semantic_fit`, `implementation_boundary`, `closeout_flow`, `downstream_unlock`, and `operator_value` before packages are presented | Updated in this slice: package responses now require `judgment_summary`; materialized package rationale includes that summary; docs state hints are facts, not package decisions |
| `quality` advisory inventories | Inventories such as structural waste, standing-test economics, clone families, and runtime summaries | Decide whether advisory findings represent real repo-local action or an intentional/acceptable shape | Already explicit through inference-layer `interpretation` declarations and paired consumer references; the #378 slice added `structural-waste` to the registry |
| `issue` resolution helpers | Issue selection/readback/classification and generative ordering support | Classify issue type, identify reporter JTBD, and order work based on uncertainty and unlocks rather than helper output alone | Already explicit in `issue` skill workflow: GitHub readback is source of truth, feature/deferred issues require a pre-mutation brief, and ordering remains agent judgment |
| `find-skills` recommendations | Ranked capability and skill recommendations | Decide whether the top-ranked route fits the current task and repo state | Already explicit through `recommendation_interpretation` and `discovery-order.md`; empty or ranked output is not treated as a final workflow decision |
| `critique` generated packets | Prepared packet sections and angle findings | Counterweight triage decides Act Before Ship / Bundle Anyway / Over-Worry / Valid But Defer | Already explicit in the critique workflow; generated packets are substrate for bounded reviewers, not final decisions |

## Slice Decision

The concrete gap for #376 was the handoff chunker: deterministic merge hints
were already described as facts, but the agent's semantic/package judgment was
not a required response field. This slice makes the re-judgment visible in the
packet schema, validator, materialized operator-facing package rationale, and
reference prose.

## Non-Claims

- This audit is not a complete proof that every helper in Charness has a perfect
  re-judgment surface.
- It does not make deterministic gates less authoritative when their contract is
  true pass/fail validation.
- It does not close #376 without a GitHub closeout carrier and readback.
