# Critique: #376 deterministic helper re-judgment

Status: draft; counterweight pending
Fresh-Eye Satisfaction: parent-delegated
Target: code critique
Issue: #376

## Reviewer Tier Evidence

- requested tier: default
- requested spawn fields: inherited parent model and reasoning settings
- host exposure state: host-defaulted
- application state: spawn tool accepted reviewer agent ids
  `019ece05-a84c-7b71-8469-00f3e6f7baf7`,
  `019ece05-c0ae-7cb2-9d15-f1d8bdc720c0`, and
  `019ece09-9aef-7581-9d85-e61fd58e8530`; reviewer-tier application details
  are host-hidden.

## Change

Make handoff chunked-routing deterministic merge hints visibly subordinate to
agent judgment by requiring every agentic package response to carry
`judgment_summary` fields for semantic fit, implementation boundary, closeout
flow, and operator value.

## Act Before Ship

- Authoring spec drift: `docs/handoff-chunked-routing.md` still described the
  old package schema. Fixed by adding `judgment_summary`, the four required
  fields, empty-field validation, and presentation wording.
- Packet version ambiguity: response schema changed while packet version stayed
  `1`. Fixed by bumping `CHUNK_PROPOSAL_PACKET_VERSION` to `2`.
- Operator-facing proof gap: the judgment summary was validated but not carried
  on the candidate shown downstream. Fixed by adding
  `ChunkCandidate.judgment_summary`, preserving it through materialization and
  JSON round trips, and requiring presentation docs/tests to keep it visible.

## Bundle Anyway

- Include `charness-artifacts/audit/2026-06-16-helper-output-rejudgment.md` in
  the same commit because it is the cross-skill audit evidence for #376.
- Completed: added a `prepare_ranker_packet` round-trip assertion for
  `judgment_summary` and aligned the non-clearance wording with the required
  judgment fields.

## Over-Worry

- The validator only checks presence/non-empty text for judgment fields. That
  is sufficient for this deterministic contract; semantic quality remains agent
  responsibility.
- Old filled package responses without `judgment_summary` now fail validation.
  That is intentional because filled responses are regenerated from the current
  packet schema.

## Valid But Defer

- Full coverage of every Charness helper-output surface is broader than this
  slice. The audit records non-claims and reviewed surfaces; future gaps should
  become targeted follow-ups rather than expanding this implementation unit.

## Proof

- `python3 -m pytest -q tests/test_handoff_chunker_agentic_packages.py
  tests/test_handoff_chunker_end_to_end.py
  tests/test_handoff_chunker_cli_contract.py
  tests/test_handoff_chunker_ranker_packet.py
  tests/test_handoff_chunker_auto_draft.py
  tests/quality_gates/test_goal_artifact_producers.py` -> 66 passed.
- `validate_public_skill_dogfood.py`, packaging validators, skill validators,
  doc links, markdown, Ruff, and py_compile passed in focused runs.
- Cautilus scenario registry review: `evals/cautilus/scenarios.json` maps
  `handoff` to `handoff-adapter-bootstrap`; no registry mutation was made
  because this slice changes deterministic package-synthesis schema, not
  routing/bootstrap behavior, and there is no log-backed behavior proof request.

## Non-Claims

- This critique does not close #376.
- The deterministic validator does not judge semantic quality; it only requires
  the agent judgment surface to exist and travel with the operator-facing
  package.
