# Cautilus Dogfood
Date: 2026-06-29

## Trigger

- slice: planner-first retro fix (`167cad5c`) — extract `plan_retro_run.py` so
  retro routes `references/expert-lens.md` at the point of need. Needs a
  live-behavior proof that the fix changes real run behavior.
- source: the FIRST live capture of the claim-fidelity sweep failed retro's floor
  (the run never opened expert-lens.md); this proves the fix flips it.

## Validation Goal

- goal: improve
- reason: prove the planner-first routing flips retro's claim-fidelity floor
  failed→proven and delivers the quality outcome (the briefed lens is applied),
  not only a doc-open proxy.

## Change Intent

- public prompt-surface change: new `plan_retro_run.py` planner (matching the
  debug/handoff/quality/issue/gather/release family) + planner-first SKILL.md;
  expert-lens.md is now an unconditional planner `required_read`.

## Prompt Surfaces

- subject under evaluation (read-only) at `HEAD`=167cad5c:
  `skills/public/retro/SKILL.md`, `skills/public/retro/scripts/plan_retro_run.py`,
  `skills/public/retro/references/expert-lens.md`.

## Behavior Source

- source-kind: operator-log
- source-ref: `charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/`
- note: operator-authorized retro test (one re-capture) per the decided plan
  "extract planner → re-capture → then change methodology". Two real `claude -p`
  captures (fail baseline + pass) in isolated read-only worktrees; no shared
  install clone mutated.

## Commands Run

- planner consult (verbatim, read-only): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: none`, `must_ask_before_running: true`,
  `run_mode: ask` (authorization is the operator's plan-level approval, not a green).
- `python3 scripts/run_cautilus_eval.py --mode observation --justification-log
  charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/justification.md
  -- --input .../observed.v1.json --output .../cautilus-report.json`

## Regression Proof

- `cautilus evaluate observation` (0.17.1): RE-CAPTURE `status: passed`
  (passed=1, failed=0); FIRST capture `status: failed` (the floor miss).
- behavior delta: first run `Read=1`, coverage 0/9, expert-lens.md never opened,
  counterfactual = Feathers + direct lens (missed the on-the-nose lens). Re-capture
  `Read=4`, coverage 4/9, ran `plan_retro_run.py` then opened expert-lens.md, and
  applied the briefed **Engelbart system-improving lens** + a Charity Majors lens.
- no new `.cautilus/runs/` dir: observation scores an already-observed packet.

## A/B Compare

- baseline_ref: 482352dc (retro before the planner) vs candidate 167cad5c
  (planner-first). `cautilus evaluate comparison prepare --repo-root .
  --baseline-ref 482352dc --output-dir /tmp/cautilus-compare` prepared both
  worktrees (deterministic; no paid run).
- A/B verdict via `cautilus evaluate observation` on the real captured packet at
  each ref: baseline `failed` (expert-lens.md never opened, coverage 0/9),
  candidate `passed` (expert-lens.md opened, coverage 4/9, Engelbart lens applied).
  The planner-first fix is the only delta between the two refs.

## Outcome

- recommendation: accept — the planner-first fix flips retro's floor failed→proven
  and delivers the quality outcome (right lens applied), not just a doc-open. The
  floor is now planner-anchored like the other 6 planner skills.

## Follow-ups

- methodology change (open): anchor RCF to planner `required_reads` / outcome
  assertions; refresh the retro-claim-fidelity spec `_comment` (still says "retro
  has no planner"); set `thresholds.max_duration_ms` from the 193700ms pass baseline.
- rollout (open): give a planner to `hitl` (the other planner-absent skill).
