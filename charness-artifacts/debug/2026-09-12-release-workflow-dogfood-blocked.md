# Debug Review: release workflow dogfood blocked
Date: 2026-09-12

Historical experiment, retired on 2026-09-12. The runner had no production
publish consumers, so the observations below prove only its fixture. The
runner, dogfood, and dedicated test were removed; existing consumer checks
and outstanding production acceptance are recorded in
[the current regression contract](../../docs/release-workflow-dogfood.md).

## Problem

The release-workflow dogfood does not prove its durable resume contract. The
user-facing capability that fails is a release run that must recover safely
after a process dies at receipt creation.

## Correct Behavior

Given an intent journal in `creating` state and no receipt, when the owner dies,
the public resume command must reconstruct the identity-bound receipt, promote
the journal to `ready`, execute the canonical path once, and report `complete`.

## Observed Facts

- Focused test: `pytest -q tests/quality_gates/test_release_workflow_dogfood.py`.
- Initial result: `1 failed, 4 passed`; final dogfood status was
  `blocked-unproven`.
- The failed acceptance was `durable-release-run-resume`.
- First observation: creation-boundary control observed owner return code `1`,
  no owner boundary marker, no creating binding, and no resume calls. This was
  generated-mirror skew; synchronization made the owner return `17` and reach
  `creating`.
- Second observation: the recovery itself completed, but the acceptance still
  said `receipt_missing_before_resume=false` because that field was measured
  after resume had created the receipt. The final focused result is `5 passed`
  after replacing that scalar with explicit before/after snapshots.
- Concurrent creation, terminal-closed readback, retry-history retention, and
  executable lock-timeout command readback produced passing observations; the
  aggregate gate still correctly stayed closed.

## Reproduction

- Historical command (test now removed): the fixture launched child
  processes against `plugins/charness/shared/scripts/release_workflow_runner.py`
  while the parent implementation is edited under `skills/shared/scripts/`.
- Durable evidence: `charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked-reproduction.json`.

## Candidate Causes

- Generated plugin mirror was stale relative to the source runner: confirmed as
  the first child failure; disconfirmed as the final cause after synchronization.
- Recovery algorithm was wrong in the source runner: disconfirmed by the
  synchronized owner-death command completing all five stages and promoting
  the registry to `ready`.
- Acceptance predicate measured a transient precondition after the action under
  test: confirmed by the second run's complete recovery plus false scalar.

## Hypothesis

- If the dogfood snapshots receipt existence before invoking resume, then a
  successful owner-death recovery will remain provable after the receipt is
  created. Disconfirmer: rerun the same focused test and require both
  `before_resume.receipt_exists=false` and `after_resume.binding_state=ready`.

## Verification

- Confirmed: mirror parity plus explicit phase snapshots produced `5 passed`.
  The owner returned `17`, the creating journal existed with no receipt before
  resume, the executable resume command ran all five stages, and the registry
  ended `ready` with a complete receipt.

## Root Cause

- Two defects formed one recurring pattern. First, source and generated
  consumer state diverged because export parity was not a precondition. Second,
  the verifier treated a post-transition state as evidence of a pre-transition
  fact. Pattern of patterns: boundary tests mixed producer, action, and
  observation into one mutable timeline, so a repair could be correct while
  the verdict stayed wrong. A third proof error was treating this fixture as
  a production release consumer. Removing the unconsumed runner and its
  dogfood eliminates that false proof surface; actual publish acceptance
  remains unproven.

## Invariant Proof

- Invariant: every producer-to-final-consumer release proof must use the same
  shared runner identity and contract that the consumer executes.
- Producer Proof: source runner contains the journal recovery contract; fixture
  owner/resume controls are intended to exercise it.
- Final-Consumer Proof: synchronized plugin child exits `17` only after writing
  the creating journal; the public resume command then completes all stages.
- Interface-Shape Sibling Scan: source runner, generated plugin mirror, and
  dogfood child command are one export/runtime seam.
- Non-Claims: no release, push, issue close, or source-only recovery proof.

## Detection Gap

- Export gate | source/mirror parity was not asserted before the child boundary
  | synchronize and compare the generated shared runner before dogfood.
- Acceptance gate | a precondition was read after resume | capture named
  `before_resume` and `after_resume` snapshots before the action, and make the
  acceptance consume the former.

## Sibling Search

- Mental model: source green means consumer green, and a later state can prove
  an earlier state.
- same layer: generated runner parity and before/after dogfood observation |
  decision: same class, fix now | proof: two successive failures and `5 passed`
  after phase snapshots.
- abstraction up: all exported plugin scripts | decision: follow-up required;
  `follow-up: export-parity-release-runner` | proof: this slice names one
  shared runner seam, not every exporter.
- specialization down: lock-timeout and concurrent-creation controls use the
  generated path | decision: passing siblings; retain as guards.
- cross-file: `scripts/plugin_export/sync_root_plugin_manifests.py` owns the
  source-to-plugin carrier and must be part of the verification contract.

## Seam Risk

- Interrupt ID: release-workflow-dogfood-blocked
- Risk Class: repeated-symptom
- Seam: shared source runner to generated plugin consumer
- Disproving Observation: synchronized mirror plus phase snapshots passes the
  owner-death control with identical source/plugin behavior.
- What Local Reasoning Cannot Prove: exported consumer behavior.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-09-12-release-consumer-acceptance.md

## Prevention

Treat export parity and phase snapshots as first-class proof inputs: synchronize
before dogfood, record the state immediately before and after each irreversible
action, and never reconstruct a precondition from post-action state. Keep the
aggregate status blocked while any boundary lacks final-consumer evidence.

## Evidence Disposition

- Report Identity: probe:release-workflow-dogfood-blocked#sha256:cb16ab13401a27e1d39d4bd372f52859754d81292a07814f91ebc5e5bef27603
- Reported Findings: 1
- Dispositioned Findings: DOGFOOD-1
- Missing Findings: none
- Evidence Digest: sha256:7155efe71f654d8904f568dc62a089771e96617c37f76358349ec7dcedae0f98
- Report Source: charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked-reproduction.json
- Report Source SHA256: cb16ab13401a27e1d39d4bd372f52859754d81292a07814f91ebc5e5bef27603

## Adversarial Verification

- Finding: DOGFOOD-1 | source: focused dogfood acceptance | expected: the experimental owner-death fixture resumes | stimulus: inspect the current consumer inventory after retirement | disposition: not-applicable | observed: the fixture and unconsumed runner are removed; historical reproduction JSON remains, but is not a current consumer receipt | proof: static scan only | handoff: docs/release-workflow-dogfood.md | next move: retain production acceptance as unproven | receipt: none | receipt sha256: none
