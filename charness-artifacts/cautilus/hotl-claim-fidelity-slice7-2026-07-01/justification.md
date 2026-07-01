# Operator Log — hotl claim-fidelity capture (reference-compaction Slice 7)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this Cautilus capture on 2026-07-01
  ("@docs/handoff.md sweep 시작. 코틸려스 실행 허용" + "continue" + "Continue full
  sweep"). `plan_cautilus_proof.py --json` returns `next_action: none`,
  `must_ask_before_running: true`, `run_mode: ask` (hotl captured read-only at
  HEAD), so this operator-log is the override.

## Basis under test (Slice 7 hotl floor: RCF-doc-open → emitted field tokens)

- reference-compaction Slice 7 (#410) scoped hotl as: lift ledger
  verified_against/disposition field tokens, RCF-drop proof-rules.md +
  ledger-and-dispositions.md → RSF (must rely on the relaxed RCF-or-RSF guard AND
  a captured token). hotl's floor is a HYPOTHESIS (no prior capture). Concern
  going in: hotl has NO substance judge (no outcome-assertions.json), and its spec
  rationale calls both docs unique load-bearing authority (proof-level ladder,
  completion-audit anti-proxy rule) — so dropping BOTH RCF docs to a FORM-only
  emitted-token floor risks over-relaxation. This capture OBSERVES whether a
  representative run opens the docs and which tokens it emits, then decides:
  clean move / refuted-hypothesis finding (gather-style) / contested (keep docs).

## Honest reading guard

- A floor MISS or a 0-coverage refutation is a skill-shape signal (re-classify /
  keep the doc / needs a substance judge), NEVER a reason to soften the matcher or
  pin a trivial/prompt-echoed token.
- hotl's first live claim-fidelity capture.
