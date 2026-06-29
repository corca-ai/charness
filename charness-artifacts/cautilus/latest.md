# Cautilus Dogfood
Date: 2026-06-29

## Trigger

- slice: correctness sweep (skill-planner-uniformity rollout) — capture the next
  hypothesis-floor skill, `quality`, one at a time per `docs/handoff.md` Next
  Session item 1. quality's floor had no valid PASSING capture under the current
  measurement instrument (the prior 2026-06-23 passing capture predates the
  item-1 matcher fix + item-2 envelope and was matcher-only, not cautilus-scored).
- source: operator authorized this session ("정확성 증명 시작. 코틸러스 허용",
  2026-06-29).

## Validation Goal

- goal: preserve
- reason: prove (or refute) that a real `/charness:quality` run honors its central
  claim — open `references/quality-lenses.md` during the bounded primer/lens phase,
  driven by the canonical planner — and (if passing) re-derive the provisional
  `max_duration_ms`. Result: floor PROVEN; the capture also surfaced a matcher
  false-negative on the for-loop batch-read idiom, fixed this slice.

## Change Intent

- intent: `truth_surface_change` + measurement-instrument accuracy fix. No
  prompt-affecting SKILL surface changed (quality captured read-only at HEAD); the
  planner reports `prompt_affecting_paths: []`, `intent_tags: []`, `goal: preserve`.
  The code change is to the eval instrument
  (`scripts/agent-runtime/build-skill-execution-observation.mjs`:
  `expandForLoopReadCommands`, wired into the floor + coverage) plus its tests,
  this proof bundle, and a critique artifact. The matcher fix is false-negative
  correction (a genuine for-loop read the static command log could not see),
  verified SOUND by fresh-eye review + a 3-angle + counterweight critique.

## Prompt Surfaces

- subject under evaluation (read-only) at `HEAD`=7d40044a:
  `skills/public/quality/SKILL.md`, `skills/public/quality/references/quality-lenses.md`
  (+ the other declared references), via the isolated installed-plugin worktree
  capture. No shared install clone mutated (#258).

## Behavior Source

- source-kind: operator-log
- source-ref: `charness-artifacts/cautilus/quality-claim-fidelity-2026-06-29/justification.md`
- note: operator (bae.hwidong@corca.ai) authorized this capture explicitly
  ("정확성 증명 시작. 코틸러스 허용", 2026-06-29). Two real `claude -p` captures in
  isolated read-only worktrees; no shared install clone mutated.

## Commands Run

- planner consult (verbatim, read-only): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: none`, `must_ask_before_running: true`,
  `run_mode: ask` (authorization is the operator's explicit request via
  `--justification-log`, not a green).
- capture 1: `bash scripts/agent-runtime/capture-skill-run.sh --ref HEAD
  --invocation "/charness:quality" --out-dir /tmp/charness-quality-capture-20260629
  --timeout-sec 900` → exit 124 (hit cap), 899315ms, 9.66M tokens.
- capture 2 (re-capture): same with `--timeout-sec 1200` → exit 124, 1199362ms,
  14.4M tokens.
- score (canonical packet, fixed matcher): `python3 scripts/run_cautilus_eval.py
  --mode observation --justification-log .../justification.md -- --input
  .../observed.v1.json --output .../cautilus-report.json`.

## Regression Proof

- `cautilus evaluate observation` (0.17.1): skill_task_fidelity passed (0 failed),
  `status: degraded` only on `runtime_budget_respect` (`duration_ms` 899315 >
  600000). The correctness floor `quality-lenses.md` is met, coverage 10/39.
- floor PROVEN n=2: capture 1 read all 9 planner primers via a `for f in ...; do
  cat "references/$f.md"; done` loop (27,552-byte tool result of real
  `quality-lenses.md` content); capture 2 read `quality-lenses.md` via the Read
  tool. The matcher previously false-negatived capture 1 (the literal
  `quality-lenses.md` never appears contiguously when assembled from a loop var);
  `expandForLoopReadCommands` corrects it — re-scoring capture 1's same tree flips
  `failed → passed`, coverage `1/39 → 10/39`.
- no new `.cautilus/runs/` dir: observation scores an already-captured packet.

## Scenario Review

- spec `evals/cautilus/quality-claim-fidelity/spec.json` reviewed against the live
  runs: the single RCF floor (`quality-lenses.md`, engage-always primer) is met by
  both captures; the canonical planner emits it as required-read #1 and the runs
  honored it. `max_duration_ms` is NOT re-derived — both captures hit the timeout
  cap (no natural completion) and the overrun is dominated by a genuine red
  `dup-ratchet` gate investigation + capture-sandbox git-hook friction, not
  reference-routing cost (the 2026-06-23 capture completed in 154968ms). The
  provisional 600000 stays. No floor, prompt, or engagement-map change.

## Outcome

- recommendation: accept — quality's claim-fidelity floor is live-capture PROVEN
  (n=2). Quality is the 3rd correctness-proven skill (after retro, hitl). The proof
  required and landed a measurement-instrument fix (the for-loop read false-
  negative); this is sharpening, not softening, and is NOT a skill change (the
  planner already routes correctly and the runs honored it). Runtime budget stays a
  known degrade for quality, `max_duration_ms` unchanged at the provisional 600000.

## Follow-ups

- n=2 caveat: both captures cut off at the cap; a future natural-completion capture
  would let `max_duration_ms` be re-derived honestly (deferred, not blocking).
- capture-sandbox git-hook friction recurred in both runs; a quieter hooks posture
  in `capture-skill-run.sh` is a deferred efficiency follow-up.
- rollout (open): ~16 uncaptured public skills still carry HYPOTHESIS floors; each
  needs one live capture. Next skill per the capture-driven sweep, ask-before-run.
