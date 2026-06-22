# Cautilus Dogfood
Date: 2026-06-22

## Trigger

- slice: cautilus skill-experiment usage-validation harness — the one real
  baseline-vs-variant proof run (goal
  `charness-artifacts/goals/2026-06-22-cautilus-skill-usage-validation-harness.md`).
- source: operator-approved single eval-only run proving the capture → extract →
  score chain emits a real verdict from real `claude -p` transcripts.

## Validation Goal

- goal: preserve
- reason: confirm the chain emits a real, honest verdict; this single-capture
  run is deliberately not a power-bearing A/B (the verdict is the chain working,
  not a promotion claim).

## Change Intent

- harness/eval-tooling change: new stream-json transcript capture + extractor +
  obligations spec; no public prompt surface semantics changed.
- the quality-ref disposition `5ded9f3a` (variant) vs `b01cee6b` (baseline) is
  the subject under evaluation, not a change landed by this run.

## Prompt Surfaces

- subject under evaluation (read-only): `skills/public/quality/SKILL.md` and its
  `references/**` at variant `5ded9f3a` vs baseline `b01cee6b`.
- planner reported zero prompt-affecting changed paths for this run; the harness
  files are eval tooling, not prompt surfaces.

## Behavior Source

- source-kind: transcript
- source-ref: `charness-artifacts/cautilus/skill-experiment-2026-06-22/`
- note: two real haiku-4.5 `claude -p` quality-task transcripts captured in
  isolated read-only worktrees (baseline.transcript.jsonl + variant.transcript.jsonl),
  extracted to input.v1.json; no shared install clone was mutated.

## Commands Run

- planner consult (verbatim, read-only): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: none`, `must_ask_before_running: true`,
  `run_mode: ask`, `goal: preserve` (hardcoded; authorization is the operator's
  explicit one-run approval + the transcript justification-log, not a planner green).
- `python3 scripts/run_cautilus_eval.py --mode skill-experiment --justification-log
  charness-artifacts/cautilus/skill-experiment-2026-06-22/justification.md --
  --input .../input.v1.json --output .../report.json`

## Regression Proof

- cautilus evaluate skill-experiment: both arms passed (variant_ran: true,
  baseline_comparable: true); 0 failed runs.
- promotion_recommendation: `discard` — `source_coverage_delta.gained: []` and
  `lost: []` (baselineCovered 6 == variantCovered 6 of 7 obligations); rubric
  status `pass`; finding severity `note` ("no declared coverage or rubric delta
  requires promotion").
- report: `charness-artifacts/cautilus/skill-experiment-2026-06-22/report.json`
  (schema `cautilus.skill_clone_experiment_report.v1`).

## Outcome

- recommendation: accept the proof as a chain demonstration, not a promotion
  signal. The chain (capture → extract → cautilus scorer) emitted a real
  `discard` verdict from real transcripts.
- honest reading: `discard` reflects zero source-coverage delta — both arms read
  the same six references. This disposition improved pointer-*directness*
  (reach-via-pointer, measured 7/7 by the prior routing blind A/B), which the
  source-coverage lens does not measure; it is not a "bad disposition" signal.

## Follow-ups

- The full multi-scenario baseline-vs-variant sweep stays an operator decision
  (one paid run authorized; a second run re-enters the operator queue).
- If a future eval wants source-coverage to discriminate this class of
  disposition, design a no-name-hint task so pointer-following is the only path
  to the refs (a name-hinted task lets a capable agent reach refs by filename).
