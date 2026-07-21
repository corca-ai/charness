# Debug Review
Date: 2026-07-22

## Problem

The v2.4.2 release helper rolled back before tag or push because release-only
quality rejected the current quality artifact's inventory-consumption record.

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

## Reproduction

- Run `./scripts/run-quality.sh --release` from clean commit `05d427fb`; the
  `validate-inventory-consumption` phase fails on the cited economics inventory.

## Candidate Causes

- The release helper failed to preserve its original clean worktree.
- The quality artifact cited an inventory it had not actually consumed.
- The artifact consumed the inventory but omitted the consumer contract's exact
  non-headline field keys.

## Hypothesis

- The validator matches declared field names literally; adding the measured
  field keys to the Deferred observation will make the release gate pass |
  disconfirmer: run `validate_inventory_consumption.py` against the artifact.

## Verification

- result: confirmed — the release gate names the cited inventory and reports
  zero engaged declared fields; the revised observation names three measured
  keys for the same decision.

## Root Cause

The quality artifact was written before the inventory-consumer contract was
enforced. Its human-readable summary retained the counts but not the declared
field identifiers the release validator uses to prove actual consumption.

## Invariant Proof

- Invariant: an artifact that cites a declared quality inventory exposes enough
  named evidence for its consumer contract to verify real use.
- Producer Proof: the economics inventory emits the three named fields.
- Final-Consumer Proof: `validate_inventory_consumption.py` accepts the
  quality artifact only when at least two declared field names occur outside
  `## Commands Run`.
- Interface-Shape Sibling Scan: other inventory citations use their declared
  fields or avoid a citation when no durable consumer conclusion exists.
- Non-Claims: the fields measure fan-out, not that a test consolidation is safe.

## Detection Gap

- Five-pass read-only closeout | did not run the release-only inventory consumer
  | rerun the exact `--release` gate before publishing.

## Sibling Search

- Mental model: prose summaries are not evidence when the consumer contract
  defines machine-checkable field names.
- release-only validation: `scripts/validate_inventory_consumption.py` |
  decision: retain literal field evidence in the artifact | proof: focused gate.
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
in the judgment section rather than only a prose paraphrase. A scoped follow-up
fresh-eye spawn was attempted but blocked by host signal `agent thread limit
reached`; the existing v2.4.2 release critique remains the release-boundary
review evidence.
