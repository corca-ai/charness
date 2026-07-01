# Operator Log — setup normalization claim-fidelity capture (reference-compaction Slice 7)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this Cautilus capture on 2026-07-01
  ("@docs/handoff.md sweep 시작. 코틸려스 실행 허용" + "continue" + "Continue full
  sweep"). `plan_cautilus_proof.py --json` returns `next_action: none`,
  `must_ask_before_running: true`, `run_mode: ask` (setup captured read-only at
  HEAD), so this operator-log is the override.

## Basis under test (Slice 7 setup normalization)

- reference-compaction Slice 7 (#410) scoped setup as: normalization.spec.json
  RCF→RSF (in-repo capturable), with greenfield DEFERRED (not in-repo capturable)
  and greenfield-flow.md + default-surfaces.md flagged to STAY RCF-pinned
  (default-surfaces.md is "a faithful multi-surface proxy"). normalization.spec.json
  RCF = [normalization-flow.md, agent-docs-policy.md, default-surfaces.md]. This
  capture OBSERVES which docs a representative in-repo normalization run opens, then
  decides per the observed evidence (clean move / refuted / keep), same discipline
  as the rest of the sweep. HYPOTHESIS floor (no prior capture).

## Honest reading guard

- A MISS or 0-coverage is a skill-shape signal (re-classify / keep), never a reason
  to soften the matcher or pin a trivial token. default-surfaces.md STAYS pinned per
  #410 unless the capture proves otherwise.
- setup's first live claim-fidelity capture.
