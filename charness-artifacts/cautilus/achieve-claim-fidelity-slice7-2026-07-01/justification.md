# Operator Log — achieve claim-fidelity capture (reference-compaction Slice 7)

- source-kind: operator-log

## Approval
- Operator authorized 2026-07-01 ("sweep 시작. 코틸려스 실행 허용" + "Continue full sweep").
  plan_cautilus_proof.py: next_action:none, must_ask:true, run_mode:ask (read-only at HEAD);
  this operator-log is the override.

## Basis
- #410 scoped achieve CONDITIONALLY: goal-artifact.md/lifecycle.md RCF→RSF ONLY IF a capture
  confirms the shaping prompt forces a goal-artifact token; else KEEP in RCF and record the
  finding. achieve has NO substance judge. This capture OBSERVES whether a goal-shaping run opens
  lifecycle.md/goal-artifact.md and emits a goal-artifact token. HYPOTHESIS floor.

## Honest reading guard
- A MISS/0-coverage is a skill-shape signal, never a reason to soften the matcher. Per #410, if the
  capture does NOT force a goal-artifact token, KEEP the RCF and record the finding.
