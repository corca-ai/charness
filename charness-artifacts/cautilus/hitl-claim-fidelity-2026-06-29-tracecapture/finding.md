# hitl claim-fidelity RE-CAPTURE — first efficiency trace (floor re-proven)
Date: 2026-06-29

Second live capture of hitl, run under the new efficiency-trace tooling. Purpose:
(a) re-prove the correctness floor, and (b) produce the FIRST durable
`trace-digest.jsonl` + exercise the deterministic waste lens on real data, then
do the intelligent review the digest enables. The first capture
(`../hitl-claim-fidelity-2026-06-29/`) proved the floor but lost its transcript
to `/tmp` cleanup — there was nothing left to review.

## What ran

- source-kind: operator-log
- source-ref: `justification.md` (operator authorized "hitl 재캡처까지 포함", 2026-06-29)
- capture: `bash scripts/agent-runtime/capture-skill-run.sh --ref HEAD --invocation
  "<hitl spec prompt>" --out-dir /tmp/charness-hitl-tracecapture` → exit 0,
  136660ms, 1476451 tokens. Isolated worktree + config; no shared install mutated.
- build: `node scripts/agent-runtime/build-skill-execution-observation.mjs
  --session-tree <tree> --spec evals/cautilus/hitl-claim-fidelity/spec.json
  --output <this-bundle>/observed.v1.json` → trace-digest.jsonl written HERE
  (durable), 20 tool calls traced.
- score: `python3 scripts/run_cautilus_eval.py --mode observation
  --justification-log justification.md -- --input observed.v1.json`.

## Verdict

- `cautilus evaluate observation` (0.17.1): `status: passed` (passed=1, failed=0).
  Floor `chunk-contract.md` MET (opened via Read, step 8). Coverage 1/5 — the same
  script-resolved/on-demand profile the engagement map predicts.
- duration 136660ms < the 240000ms ceiling; total_tokens 1476451. No degrade.

## Efficiency

This is the payoff of the durable trace: a single capture, intelligently
reviewable. Deterministic lens output (auto):

- trace: `trace-digest.jsonl` (20 tool calls)
- waste smell (repeated_edit): queue.json edited 3x (batch into one?) — CONFIRMED
  below.

Intelligent review (reading the digest — finds what the deterministic lens cannot):

- **find-flail for `agent-assessment-invariant.md` (steps 11–13, ~20s, 3 distinct
  `find` commands).** The agent searched three different roots for a reference
  whose path the SKILL.md already names (`../../shared/references/...`) instead of
  resolving it. The deterministic lens MISSED this (three distinct commands, not a
  repeat) — exactly the gap the intelligent review fills. Biggest single
  inefficiency in this run. Candidate fix: have the skill resolve shared-reference
  paths deterministically (a bootstrap helper), not by `find`.
- **runtime state/queue churn (steps 15–19): queue.json ×2 Edit + a Write + a
  re-Read (3 mutations the lens groups as the `repeated_edit` 3x flag), plus a
  state.yaml Edit.** Confirms the deterministic flag. Several round-trips on small
  runtime files; candidate fix: author the queue/state in fewer consolidated writes.
- **large reads are legitimate, not waste:** the two biggest outputs are the
  review target (step 7, 8475 chars) and `chunk-contract.md` (step 8, 3902) — the
  actual work, correctly not flagged.

## Non-Claims / Follow-ups

- **n=1 variance is large — do not over-read efficiency from one capture.** The
  FIRST hitl run (13 tool calls, 0.93M tokens, 102s) never did the find-flail;
  this run (20 calls, 1.48M, 137s) did. Same skill, same prompt, materially
  different path. The find-flail and churn are real *candidates*, but their cost
  and frequency need n>1 to be a stable claim, not a verdict.
- The waste smells are advisory; the outcome stays claim-matcher-only. None of
  this softens or alters the floor.
- follow-up (Fix 3, deferred): an agent efficiency-review pass that does this
  analysis automatically from the digest (it would have surfaced the find-flail
  the deterministic lens missed).
- the actionable skill fix (resolve `agent-assessment-invariant.md` without
  `find`; consolidate queue/state writes) is a separate `hitl` improvement slice,
  not this tooling slice.
