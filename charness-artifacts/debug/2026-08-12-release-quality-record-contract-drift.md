# Release Quality Record Contract Drift Debug
Date: 2026-08-12

## Problem

The first 5.0.0 release-gate attempt rolled back before commit/tag/push because
the newly committed quality record made three release-only quality checks fail.

## Correct Behavior

Adding a quality record must either keep every derived measurement and cited
evidence contract current, or fail locally before release; a repaired record
must pass the same `--release` gate that refused it.

## Observed Facts

- `pytest-release` reported three failures: the mutable inventory probe was
  stale at 133 versus live 134 artifacts; a runtime citation pointed to ignored
  local state without a permitted reproduction annotation; and the ergonomics
  inventory was named without consuming its required fields.
- The release helper restored its precommit candidate state, recorded the
  failure under `.git/charness-release-failures/`, and created no `v5.0.0` tag.
- Re-running the two inventory measurement producers over the corrected record
  yields the revised shallow/recursive payloads and a floor-20 counterfactual
  of 12 citations and 46 label values.

## Reproduction

- `./scripts/run-quality.sh --release` on `516c90ee` with the new quality
  record reproduces the three failures in `/tmp/charness-release-5-0-0.log`.

## Candidate Causes

- The release-only suite is flaky or reads a different tree.
- The quality record's claims are valid but its validators overreach.
- The record changed measured corpus/citation inputs without synchronizing the
  generated probe and evidence-contract consumers.

## Hypothesis

- If the record cites ignored runtime state with the required reproduction
  marker, consumes the declared ergonomics fields, and the current measurement
  payloads plus mirror comment are synchronized, then all three named tests
  pass without changing quality policy. Disconfirmer: run their direct
  validators and the release gate after the repair.

## Verification

- confirmed — `validate_inventory_consumption.py` now accepts the record;
  `check_spec_evidence_durability.py` accepts its runtime citation; the floor
  and marker measurements match the synchronized probes. Full release-gate
  rerun remains the final consumer proof.

## Root Cause

The initial record both extended the measured quality corpus and referenced a
declared inventory, but it was committed after the earlier mutable probes were
recorded. Its local runtime path and inventory citation also failed the
separate evidence-consumer contracts. The broad read-only run preceded the
final record and therefore did not exercise this exact release candidate.

## Invariant Proof

- Invariant: when a quality record becomes a checked-in release input, its
  measurement producers and evidence-contract consumers must accept that exact
  record before the release helper can claim local readiness.
- Producer Proof: the inventory measurement scripts emit 134 artifacts and
  synchronized marker/floor payloads from the current record.
- Final-Consumer Proof: `run-quality.sh --release` invokes `pytest-release`,
  which refused the stale/citation defects and will decide the repaired state.
- Interface-Shape Sibling Scan: `validate_inventory_consumption.py`,
  `check_spec_evidence_durability.py`, and the plugin mirror consume different
  facets of a newly written quality artifact.
- Non-Claims: no hosted CI, GitHub release, tag, or public readback exists
  until the later successful publish boundary.

## Detection Gap

- quality record authoring | the pre-record broad run did not include the final
  record | run the release gate after committing record/probe synchronization.

## Sibling Search

- Mental model: generated evidence and contract consumers must be refreshed
  from the final artifact, not from an earlier nearby worktree.
- same layer: marker and floor probes | decision: synchronize together now |
  proof: their direct producers match current corpus.
- exported mirror: plugin validator comment | decision: sync now | proof:
  `sync_root_plugin_manifests.py` reports the mirror update.
- cross-file: `scripts/validate_inventory_consumption.py` and
  `scripts/check_spec_evidence_durability.py`.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: local quality artifact → release-only validators.
- Disproving Observation: a green release gate on the repaired commit.
- What Local Reasoning Cannot Prove: hosted/public release readback.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Treat a quality record as an input to its measurement and evidence consumers.
Refresh derived probes only after the record's final wording is set, then run
the release-specific gate; do not transpose a prior broad-green receipt onto a
later record.
