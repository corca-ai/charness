# Resolution Critique: #273 + #261 Mutation Gate Recovery

Date: 2026-06-01
Target: `charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md`
Reviewer: Mill (`019e826b-ba36-77e3-8bc0-d3f558b0549c`)
Fresh-Eye Satisfaction: parent-delegated

## Act Before Ship

- The carrier was not closeout-valid until it carried a real `Critique:` line
  pointing at this persisted critique artifact.
- The debug artifact header needed validator-compatible shape: `Date:` belongs
  immediately after the H1.
- Because the debug artifact is closeout evidence, the debug seam-risk index
  must be regenerated before final validation.
- The goal must not be marked complete until final validation, issue draft
  validation, and critique evidence are recorded.

## Bundle Anyway

- #273 proof is adequate for the named regression after the paperwork fixes:
  it targets the latest failing scheduled range, shows `blocking: []`, covers
  the exact `host_log_probe_lib.py` changed-line targets, and removes the
  sampled `portable_artifact_lib.py` survivor shapes.
- #261 should receive a leave-open comment after publication, framed as a
  scope/status comment rather than a closeout.

## Over-Worry

- Re-running the full coordination-cues survivor campaign before this push
  would be waste. The prior `765f5d4` hardening is already on `HEAD` and
  `origin/main`, and prior critique classifies remaining survivors as
  equivalent/low-value policy residue.
- Chasing every sibling helper named by causal review would expand this beyond
  the live #273 regression.

## Valid but Defer

- #261 still needs a policy decision for equivalent/low-value survivor
  treatment. Leaving it open is honest and matches the issue body.
- Remote CI remains unproven until after push; final verification should keep
  that as a non-claim unless observed.
