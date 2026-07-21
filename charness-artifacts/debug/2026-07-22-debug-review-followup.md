# Debug Review
Date: 2026-07-22

## Problem

The v2.4.2 release helper first rolled back because release-only quality
rejected the current quality artifact's inventory-consumption record, then a
second replay exposed a release-only test that rejected a valid idempotent
Specdown update result.

## Correct Behavior

Given a quality artifact cites `inventory_standing_test_economics.py`, when the
release gate validates inventory consumption, then the artifact explicitly
engages with at least two declared non-headline fields and the release can move
past its quality phase without changing tracked Specdown evidence.

## Observed Facts

- The first v2.4.2 publish attempt recorded `quality_command: 68.48s` and
  restored every precommit release mutation; no branch, tag, or release exists.
- `./scripts/run-quality.sh --release` reproduced exactly one failure:
  `validate-inventory-consumption` found zero declared fields in the quality
  artifact body although the command log cites the economics inventory.
- The current inventory reports `test_file_count=415`,
  `nested_cli_file_count=181`, and `nested_cli_standing_file_count=163`.
- The existing Deferred sentence used prose counts but did not include the
  validator's exact field keys.
- After that repair, the release suite had one failure: the Specdown
  provenance test expected `updated`, while the seeded lock and fake binary
  both report `0.47.2`, so `update_tools.py` correctly returned `refreshed`.

## Reproduction

- Run `./scripts/run-quality.sh --release` from clean commit `05d427fb`; the
  first replay fails `validate-inventory-consumption`. After its repair, the
  same gate fails `test_tool_update_routes_go_provenance_for_specdown` because
  it asserts `updated` against the valid idempotent `refreshed` result.

## Candidate Causes

- The release helper failed to preserve its original clean worktree.
- The quality artifact cited an inventory it had not actually consumed.
- The artifact consumed the inventory but omitted the consumer contract's exact
  non-headline field keys.
- A provenance-routing test confused a successful package-manager invocation
  with a mandatory version transition.

## Hypothesis

- The inventory validator matches declared field names literally, and the
  provenance test must accept both successful transition states; adding the
  measured field keys and allowing `updated` or `refreshed` will make the
  release gate pass | disconfirmer: run the inventory validator and the focused
  Specdown provenance test.

## Verification

- result: confirmed — the release gate names the cited inventory and reports
  zero engaged declared fields; the revised observation names three measured
  keys. The focused failure shows `refreshed` with matching seeded and detected
  versions, which is the success branch in `update_tools.py`.

## Root Cause

The quality artifact was written before the inventory-consumer contract was
enforced. Its human-readable summary retained the counts but not the declared
field identifiers the release validator uses to prove actual consumption. The
release-only provenance test separately overfit the prior version-change state
instead of the stable package-manager routing contract it owns.

## Invariant Proof

- Invariant: an artifact that cites a declared quality inventory exposes enough
  named evidence for its consumer contract to verify real use, and an update
  provenance test accepts either successful transition state.
- Producer Proof: the economics inventory emits the three named fields.
- Final-Consumer Proof: `validate_inventory_consumption.py` accepts the
  quality artifact only when at least two declared field names occur outside
  `## Commands Run`; the Specdown test accepts `updated` or `refreshed` while
  still asserting the Go package-manager provenance.
- Interface-Shape Sibling Scan: other inventory citations use their declared
  fields or avoid a citation when no durable consumer conclusion exists.
- Non-Claims: the fields measure fan-out, not that a test consolidation is safe.

## Detection Gap

- Five-pass read-only closeout | did not run the release-only inventory consumer
  or its release-only provenance test | rerun the exact `--release` gate before
  publishing.

## Sibling Search

- Mental model: prose summaries are not evidence when the consumer contract
  defines machine-checkable field names, and successful idempotence is not a
  failed update.
- release-only validation: `scripts/validate_inventory_consumption.py` |
  decision: retain literal field evidence in the artifact | proof: focused gate.
- package-manager provenance: `tests/charness_cli/test_tool_lifecycle.py` |
  decision: accept both successful transition states | proof: focused test.
- cross-file: `skills/public/quality/references/inventory-consumer-fields.json`
  owns the declared field vocabulary.

## Seam Risk

- Interrupt ID: release-quality-contract-gap
- Risk Class: contract-freeze-risk
- Seam: quality artifact authoring to release-only inventory consumer.
- Disproving Observation: the focused consumer passes without named field keys.
- What Local Reasoning Cannot Prove: future inventory declarations will remain
  aligned without their declaration gate.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep the release helper's exact quality command as the final release consumer;
when a quality artifact cites an inventory, record the measured declared fields
in the judgment section rather than only a prose paraphrase. Keep provenance
tests focused on routing and accept the documented idempotent update result. A
scoped follow-up fresh-eye spawn was attempted but blocked by host signal
`agent thread limit reached`; the existing v2.4.2 release critique remains the
release-boundary review evidence.
