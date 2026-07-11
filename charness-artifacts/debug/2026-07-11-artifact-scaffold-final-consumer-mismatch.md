# Artifact Scaffold and Final-Consumer Mismatch Debug
Date: 2026-07-11

## Problem

Two repo-owned artifact producers emit outputs that their own next action or
final gate cannot safely consume: debug fresh-investigation planning points at a
resolved prior record, and a valid critique prepare packet fails the critique
record validator unless it is manually rewritten after review.

## Correct Behavior

Given a resolved debug current pointer, when the planner selects a fresh
investigation, then its scaffold contract names a fresh record and an explicit
current-pointer transition without overwriting history. Given a valid critique
prepare packet, when repo artifact gates run, then the packet is checked by the
packet contract rather than treated as an already-completed critique record.

## Observed Facts

- `plan_debug_run.py --json` reports mode
  `fresh-investigation-with-prior-memory` and action
  `scaffold-debug-artifact`.
- The same action names the resolved #433 record as `write_artifact_path`.
- A minimal static-section `prepare_packet.py` run exits zero with `ok: true`.
- Passing its emitted `*-packet.md` to `validate_critique_artifacts.py` fails
  because pre-review evidence (`Fresh-Eye Satisfaction`) is necessarily absent.

## Reproduction

- Debug: run `python3 skills/public/debug/scripts/plan_debug_run.py --repo-root .
  --json` while `debug/latest.md` targets an artifact with
  `Resolution: resolved`; compare `mode` and `next_action.write_artifact_path`.
- Critique: in a temporary repo, configure one static critique packet section,
  run `prepare_packet.py --slug 2026-07-11-repro`, then run
  `validate_critique_artifacts.py --paths
  charness-artifacts/critique/2026-07-11-repro-packet.md`; production succeeds
  and the final gate rejects the result.

## Candidate Causes

- Shared current-pointer resolution is lifecycle-blind and always dereferences
  a symlink even when the caller has classified its target as resolved.
- The debug planner decides fresh-vs-continue only after consuming a scaffold
  payload whose write target was already fixed.
- The critique validator selects every markdown file under the critique
  directory by path prefix and does not distinguish prepare-packet envelopes
  from completed critique records.
- The prepare packet renderer may be expected to mutate after review, despite
  its documented role as reviewer input produced before reviewers run.

## Hypothesis

- Confirmed claim: lifecycle and artifact-kind facts exist, but the final
  carrier interfaces discard them. Disconfirmer: find a repo-owned field or
  validator branch that gives resolved debug targets a new record or recognizes
  `charness.critique_prepare_packet`; none appears in the reproduced paths.

## Verification

- Result: resolved — 95 composed debug/quality/critique/retro tests passed;
  debug fresh routing emits a non-conflicting durable record plus executable
  pointer refresh, and producer-marked prepare packets bypass only completed-
  record floors while renamed/mislabeled records still fail.

## Root Cause

The shared path helper models a current pointer only as a filesystem alias, so
the later debug lifecycle decision cannot request rotation. Separately, the
critique gate models directory membership as artifact kind, so a pre-review
transport packet is subjected to post-review record floors. In both cases a
real producer/consumer distinction is collapsed before the final consumer.

## Invariant Proof

- Invariant: a producer-selected lifecycle/artifact kind must survive in the
  emitted carrier until the final writer or validator acts on it.
- Producer Proof: debug plan and critique packet producer outputs reproduce the
  intended fresh-investigation and prepare-packet states.
- Final-Consumer Proof: focused regressions must show a fresh debug record path
  plus pointer transition, and packet validation that does not demand review
  completion while critique records still do.
- Interface-Shape Sibling Scan: inspect debug/quality current-pointer callers,
  critique/retro prepare packets, and artifact validators before limiting fixes.
- Non-Claims: no generic artifact framework rewrite; no weakening of completed
  critique fresh-eye or boundary-ownership floors.

## Detection Gap

- Debug scaffold tests lock the old symlink-target behavior but never compose it
  with the planner's resolved lifecycle branch.
- Critique packet tests prove producer output and critique tests prove record
  floors independently; no roundtrip test feeds producer output to the gate that
  scans committed critique-directory markdown.

## Sibling Search

- Mental model: directory/path aliasing was treated as sufficient semantic type
  information across producer and final consumer.
- lifecycle axis: debug resolved pointer | decision: confirmed mismatch | proof:
  composed planner/scaffold reproduction.
- sibling current pointer: quality | decision: producer precondition pending |
  proof: quality has no resolved/open lifecycle in the inspected payload.
- artifact-kind axis: critique prepare packet | decision: confirmed mismatch |
  proof: zero-exit producer followed by rejecting repo validator.
- sibling prepare packet: retro | decision: inspect before fixing | proof:
  prepare-packet contract exists but validator interaction is not yet mapped.
- cross-file: `scripts/scaffold_artifact_lib.py`, debug planner/scaffold, critique
  packet library, and critique validator all participate in the two seams.

## Seam Risk

- Interrupt ID: artifact-kind-carrier-collapse
- Risk Class: none
- Seam: producer lifecycle/kind to final writer/validator
- Disproving Observation: two independent repo-owned roundtrips fail without a
  host or external provider.
- What Local Reasoning Cannot Prove: whether all historical packet-shaped files
  are pure prepare packets rather than combined closeout records.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Composed roundtrip tests now cover planner plus scaffold for resolved rotation,
same-day collision refusal/fallback, executable pointer refresh, and packet
producer plus artifact gate for kind-aware validation. Strict post-review
floors remain active for true critique and retro records.
