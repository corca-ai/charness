# Live-Capture Proof — retro claim-fidelity RE-CAPTURE (floor flipped failed→proven)
Date: 2026-06-29

Second live capture, against the planner-first fix (`167cad5c`). The first
capture (`../retro-claim-fidelity-2026-06-29/`) failed retro's floor; this one
proves the fix flips it.

## Behavior Source

- source-kind: operator-log
- source-ref: `charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/justification.md`
- note: operator authorized the retro test as part of the decided plan
  ("extract planner → re-capture → then change methodology").

## Commands Run

- capture (one real isolated headless run at ref `HEAD`=167cad5c):
  `bash scripts/agent-runtime/capture-skill-run.sh --ref HEAD --invocation
  "<retro spec prompt>" --out-dir /tmp/charness-retro-recapture` → exit 0,
  193700ms wall, 1.80M total tokens.
- build observed packet: `node scripts/agent-runtime/build-skill-execution-observation.mjs
  --spec evals/cautilus/retro-claim-fidelity/spec.json` → `outcome=passed |
  coverage=4/9 | tools: Bash=15 Read=4 Write=1`.
- score: `python3 scripts/run_cautilus_eval.py --mode observation
  --justification-log justification.md -- --input observed.v1.json` →
  `cautilus evaluate observation`: `status: passed`, passed=1 failed=0.

## Regression Proof (the floor now survives live capture)

- Asserted floor `requiredCommandFragments: ["expert-lens.md"]`: MET. The run
  executed `plan_retro_run.py` (planner-first Bootstrap), then opened
  `references/expert-lens.md` via the Read tool BEFORE writing — the deterministic
  routing the planner adds. Tool sequence: git context → run plan_retro_run.py →
  Read expert-lens.md (+3 other refs) → scaffold → write → persist → validate.
- Behavior delta vs first capture:
  - first: `Read=1`, coverage 0/9, expert-lens.md never opened, counterfactual =
    Feathers + direct lens (general knowledge), MISSED the Engelbart lens.
  - now: `Read=4`, coverage 4/9, expert-lens.md opened, counterfactual = **Engelbart
    system-improving lens (the briefed lens) + Charity Majors observability lens**.
- Quality outcome (not just doc-open): the run applied the briefed Engelbart
  `system-improving-itself` (H+LAM+T) lens and correctly diagnosed the root cause
  ("evolved the tooling without co-evolving the method; the planner did not exist;
  froze the gap"), converging on "live-capture-before-assert" — the exact insight
  the first capture could not reach without the doc. See `captured-retro-artifact.md`.
  Its Sibling Search independently named `hitl` as the other planner-absent skill.

## Outcome

- recommendation: accept — the planner-first fix flips retro's claim-fidelity floor
  failed→proven, and delivers the quality outcome (right lens applied), not just a
  doc-open. expert-lens.md is now planner-anchored, like the other 6 planner skills.

## Follow-ups

- thresholds.max_duration_ms: set from this passing baseline (193700ms) during the
  fixture reshape (methodology change), with headroom — not pinned here.
- methodology: anchor RCF to planner required_reads + outcome assertions; refresh
  the retro-claim-fidelity spec `_comment` (still says "retro has no planner").
- rollout: give a planner to `hitl` (the other planner-absent skill) and re-evaluate.
