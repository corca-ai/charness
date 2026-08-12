# Cautilus Dogfood
Date: 2026-08-12

## Trigger

- slice: operator ruling 5 — evaluate the ready route-undetermined
  `handoff/judge-intent` scenario once.
- source: the operator explicitly approved one Cautilus evaluation in this
  session; the durable operator log is named below.

## Validation Goal

- goal: preserve
- reason: verify that the safety-net branch is exercised without inventing a
  pickup, refresh, or chunked-routing route before its required reads.

## Change Intent

- intent: truth_surface_change — this artifact records the approved evaluation
  result. The scenario itself had already been committed at `056afc75`; the run
  evaluates that fixed local surface and makes no hosted claim.

## Prompt Surfaces

- subject: `skills/public/handoff/SKILL.md` and
  `evals/cautilus/handoff-claim-fidelity/judge-intent.spec.json`, captured from
  isolated `HEAD` `056afc75` via `/charness:handoff`.

## Behavior Source

- source-kind: operator-log
- source-ref: `charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/justification.md`
- note: the log records this session's single-run approval and the specific
  route-undetermined behavior; it does not claim a pre-existing failure.

## Commands Run

- planner: `python3 scripts/plan_cautilus_proof.py --repo-root . --detail` →
  `next_action: none`, `must_ask_before_running: true`; the named operator log
  and explicit approval satisfy the ask-before-run override.
- capture: `scripts/agent-runtime/capture-skill-run.sh --ref HEAD --invocation
  "/charness:handoff … --intent auto …" --out-dir /tmp/handoff-judge-intent-2026-08-12`
  → exit 0.
- packet: `node scripts/agent-runtime/build-skill-execution-observation.mjs
  --spec evals/cautilus/handoff-claim-fidelity/judge-intent.spec.json`.
- score: `python3 scripts/run_cautilus_eval.py --mode observation
  --justification-log charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/justification.md
  -- --input …/observed.v1.json --output …/summary.json`.

## Regression Proof

- deterministic packet: `outcome=passed`, 20 tool calls, `Read=8`, and no waste
  smells; its required `workflow-trigger.md` and `state-selection.md` reads were
  satisfied by actual read events.
- `cautilus evaluate observation`: 1 execution, 1 passed, 0 failed, stable
  consensus; `duration_ms=177666` remains below the 660000-ms scenario limit.
- durable bundle: `charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/`
  contains the authorization, observed packet, summary, and trace digest.

## Scenario Review

- `judge-intent.spec.json` deliberately leaves route choice unresolved. Its two
  engage-always references are the planner safety-net reads; `adapter-contract.md`
  and `spill-targets.md` remain conditionally irrelevant to this healthy run.

## Outcome

- recommendation: accept-now
- ruling 5's one approved local evaluation completed successfully. This is local
  evaluator evidence only, not a push, release, hosted readback, or consumer claim.

## Follow-ups

- Proceed to operator ruling 6 / `#585`: re-key boundary-bypass identity on
  normalized call-site content while preserving membership and multiplicity.
