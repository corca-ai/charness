# Cautilus Dogfood
Date: 2026-07-02

## Trigger

- slice: correctness sweep (#411) — VERIFY the redesigned gather public-URL
  claim-fidelity floor. The old doc-open RCF (`source-priority.md`,
  `capability-contract.md`) was refuted by the 2026-07-01 slice-7 capture (0/8);
  this session shipped the artifact/substance replacement
  (`evals/cautilus/gather-claim-fidelity/outcome-assertions.json`, `3b650cb6`)
  and this capture proves it grades a real run.
- source: operator authorized this session ("캡처 시작", 2026-07-02).

## Validation Goal

- goal: preserve
- reason: prove the substance floor grades a genuine `/charness:gather` public-URL
  run correctly (durable primary-source asset, honest access/capture accounting, no
  search-widening) and confirm the doc-open RCF is refuted on a fresh run. Result:
  substance floor PROVEN 4/4; doc-open RCF refuted 0/8.

## Change Intent

- intent: `truth_surface_change`. The eval-instrument change (add
  `outcome-assertions.json`) shipped `3b650cb6`; gather was captured READ-ONLY at
  `HEAD`=22dba8c8, so the planner reports `prompt_affecting_paths: []`,
  `intent_tags: []`, `goal: preserve`. The enum-inline + RCF-flip that would close
  the public-URL default are the DEFERRED capture-gated MOVE, blocked on a design
  decision (substance-floor-only spec support), not this proof.

## Prompt Surfaces

- subject under evaluation (read-only) at `HEAD`=22dba8c8:
  `skills/public/gather/SKILL.md` + its declared references, via the isolated
  installed-plugin worktree capture. No shared install clone mutated (#258).

## Behavior Source

- source-kind: issue-log
- source-ref: `charness-artifacts/cautilus/gather-claim-fidelity-2026-07-02-justification.md`
- note: operator (bae.hwidong@corca.ai) authorized this capture explicitly
  ("캡처 시작", 2026-07-02). One real `claude -p` capture in an isolated read-only
  worktree; no shared install clone mutated.

## Commands Run

- planner consult (read-only): `python3 scripts/plan_cautilus_proof.py --repo-root
  . --json` → `next_action: none`, `must_ask_before_running: true`, `run_mode: ask`
  (authorization is the operator's explicit request via `--justification-log`).
- capture: `bash scripts/agent-runtime/capture-skill-run.sh --ref HEAD --invocation
  "/charness:gather https://docs.python.org/3/library/asyncio-task.html ..."
  --out-dir ~/.cache/charness-captures/gather-2026-07-02 --timeout-sec 900` → exit
  0, 119209ms, 1.18M tokens.
- build packet (phase B): `node
  scripts/agent-runtime/build-skill-execution-observation.mjs --session-tree <tree>
  --spec evals/cautilus/gather-claim-fidelity/spec.json --stream <stream.jsonl>
  --output <bundle>/observed.v1.json`.
- score (phase B): `python3 scripts/run_cautilus_eval.py --mode observation
  --justification-log <bundle>-justification.md -- --input <bundle>/observed.v1.json`
  → `cautilus evaluate observation` status failed, 0/8 (doc-open RCF refuted).
- grade (phase C): `python3 scripts/grade_skill_outcome.py --grade <bundle>
  --assertions evals/cautilus/gather-claim-fidelity/outcome-assertions.json
  --judge-cmd "python3 scripts/outcome_judge_cmd.py"`.

## Regression Proof

- phase B — `outcome=failed | coverage=0/8`: the fresh run opened ZERO reference
  docs (both RCF floors `source-priority.md` + `capability-contract.md` missing),
  reproducing the slice-7 refutation. The doc-open floor is a refuted HYPOTHESIS
  (census INLINE), NOT matcher softening.
- phase C — substance floor PROVEN: eval result 4/4 passed, 0 failed (pass_rate
  1.0, 0 skipped, 0 errors) via `grade_skill_outcome.py` + live independent judge.
  All three judge assertions PASS plus the deterministic sanity. The judge graded
  the
  asset the run COMMITTED (`65b16ff7`), validating the committing-run-aware design
  (transcript-reading judge + base..HEAD output extraction, not a naive
  `output_glob` that would false-fail a committing run).
- bundle: `charness-artifacts/cautilus/gather-claim-fidelity-2026-07-02/`.

## Scenario Review

- spec `evals/cautilus/gather-claim-fidelity/spec.json` (public-URL default): the
  doc-open RCF is refuted (0/8, census INLINE confirmed); the honest floor is the
  substance set, now PROVEN. The RCF flip is NOT applied — `claim_fidelity_lib`
  requires RCF-or-RSF non-empty and public-URL has no honest token, so the flip
  needs substance-floor-only spec support (deferred, affects setup #413 too). The
  `private-saas.spec.json` sibling (RCF browser-mediated-private-sources.md) is
  unaffected.

## Outcome

- recommendation: accept — gather's public-URL substance floor is live-capture
  PROVEN (4/4), and the doc-open RCF refutation is reconfirmed on a fresh run. This
  is the honest #411 replacement floor, verified before any pin (capture-before-pin).
  #411 stays OPEN pending the RCF flip, which is gated on the substance-floor-only
  spec-support design decision, not on further proof.

## Follow-ups

- DECIDE + implement substance-floor-only spec support in `claim_fidelity_lib`
  (allow empty RCF+RSF when a sibling `outcome-assertions.json` exists); then flip
  gather public-URL RCF and inline the Access-Modes enum into SKILL.md (handling the
  `mode_option_pressure_terms` ergonomics gate). Same unblock serves setup #413.
- remaining untested HYPOTHESIS floors (announcement/ideation/narrative/create-skill/
  release/spec/find-skills) per `untested-hypothesis-floor-sweep.md` — one batched
  ask-before-run capture session each, capture-before-pin.
