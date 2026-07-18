# Release Quality Contract Gap Debug
Date: 2026-07-19

## Problem

The v2.1.5 publish helper stopped before commit/tag/push because release quality
found one malformed debug artifact and twelve duplicate families absent from the
accepted ratchet reference. Earlier slice closeout had passed.

## Correct Behavior

Release-only gates should be exercised before publication execution, and every
new duplicate family should be removed, explicitly classified, or scoped into
the accepted reference with reviewed rationale.

## Observed Facts

- The helper restored all tracked release mutations and quarantined its generated
  auto-retro; no tag, push, or public release occurred.
- The critique-scaffold debug record lacked `## Reproduction` and
  `## Candidate Causes`, which the release validator requires.
- The duplicate ratchet reported twelve cumulative families and two membership
  reductions; none was a worktree-only surprise.
- A trial shared packet-argument helper increased live new families from twelve
  to fourteen, so it was reverted before commit.

## Reproduction

Run the release helper for v2.1.5 with `--execute` from clean commit `d9b0d99f`.
Its `./scripts/run-quality.sh --release` phase reports 80 pass / 2 fail, naming
`validate-debug-artifact` and `dup-ratchet`, then emits a restored rollback
payload with empty remaining status.

## Candidate Causes

- The release helper failed to restore its pre-commit mutations.
- Slice closeout and release quality intentionally own different gate sets.
- The duplicate baseline was stale due a scanner-version mismatch.
- New cumulative families had never received their required disposition.

## Hypothesis

The campaign closed each code slice but did not run the release-only debug-shape
and duplicate-reference consumers before entering publish execution.
Disconfirmer: release quality still fails after the missing sections, exact
family dispositions, and scoped reference rotations are applied.

## Verification

- confirmed — the helper rollback returned to `d9b0d99f` with an empty worktree.
- confirmed — the repaired debug artifact passes the full debug validator.
- confirmed — the duplicate ratchet reports clean with zero new fixable-eligible
  families after exact review; no broad path/glob exemption was added.

## Root Cause

The pre-publication rehearsal used slice closeout, whose surface plan does not
include every release-only quality consumer. The missing debug sections and
unreviewed cumulative clone identities therefore remained latent until the
helper's release gate.

## Invariant Proof

- Invariant: task-completing release critique is necessary but not a substitute
  for the helper's exact release-quality consumer.
- Producer Proof: debug artifacts now satisfy the full release validator; clone
  review names each fingerprint and rationale.
- Final-Consumer Proof: `check_dup_ratchet.py --summary` reports clean and the
  next publish attempt must rerun `run-quality.sh --release` before mutation.
- Interface-Shape Sibling Scan: the release helper already owns rollback and
  the exact consumer; no second publish path or duplicate gate was added.
- Non-Claims: exact intentional classifications do not claim the families are
  free of duplication; they claim extraction would worsen ownership or hide a
  distinct contract.

## Detection Gap

- release candidate rehearsal | slice closeout omitted release-only consumers |
  retry uses the helper's unchanged quality boundary and records this mismatch

## Sibling Search

- debug artifact shapes | repaired the only invalid current artifact | proof:
  full debug validator passes
- new code clone families | reviewed all twelve plus two reductions | proof:
  ratchet hard arm reports zero new fixable-eligible families
- shared packet parser | attempted then rejected | proof: live family count rose
  from twelve to fourteen

## Seam Risk

- Interrupt ID: release-quality-contract-gap
- Risk Class: contract-freeze-risk
- Seam: slice closeout proof -> release-only quality consumer
- Disproving Observation: a clean release rehearsal reaches mutation with an
  invalid debug artifact or undispositioned duplicate family
- What Local Reasoning Cannot Prove: future surface routing will include every
  gate later added to release quality
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep the release helper as the final consumer and run its dry-run plus exact
quality rehearsal early enough to repair local-only findings before publication.
