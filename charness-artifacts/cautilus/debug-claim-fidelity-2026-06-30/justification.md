# Operator Log — debug claim-fidelity capture (correctness sweep resume)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this session: "코틸러스 허용"
  (Cautilus allowed) + "스킬 평가 재개" (resume skill evaluation), 2026-06-29/30.
  This is the next capture in the capture-driven correctness sweep
  (`docs/handoff.md` Next Session), taken one at a time after quality.

## Why this run

- `debug` is a planner-backed public skill whose claim-fidelity floor
  `requiredCommandFragments: ["five-steps.md", "debug-memory.md",
  "five-whys-causal-chain.md"]` has never been exercised by a live run — a
  HYPOTHESIS until this capture. It is the most demanding floor captured so far
  (THREE required references, no runtime threshold → pure correctness).
- The claim under test: does a real `/charness:debug` run honor its central
  routing — open the 5-step workflow (`five-steps.md`), the prior-incident memory
  (`debug-memory.md`), and the five-whys causal chain (`five-whys-causal-chain.md`)
  — driven by the canonical planner, rather than improvising an ad hoc fix?
- DOUBLE DUTY (this slice's regression proof): debug's planner `plan_debug_run.py`
  was just refactored to call `ENVELOPE.adapter_echo(adapter)` (fae23 extraction,
  commit f827594c). Its `--json` output was proven byte-identical, but a live
  capture is the ultimate behavior-safety proof. This run also exercises the
  empty-hooks capture-sandbox fix (commit b97b9436).
- Planner consult (read-only, verbatim): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: "none"`, `must_ask_before_running: true`,
  `run_mode: "ask"`. Authorization is the operator's explicit request above; this
  log is the `--justification-log` override the wrapper requires.

## Subject under evaluation (read-only)

- `skills/public/debug/SKILL.md` + `skills/public/debug/references/{five-steps.md,
  debug-memory.md,five-whys-causal-chain.md}` (+ other declared references) at ref
  `HEAD` (f827594c), via an isolated installed-plugin worktree capture. No shared
  install clone mutated (#258 hazard).

## Honest reading guard

- PASS = the run opens all three floor references (the planner emits them as
  required reads and the run honors them). A MISS on any one is a real skill-shape
  signal of the SAME class as retro's first capture (re-pin / planner required-read
  / re-classify) — NEVER soften the matcher. The debug prompt is a TEMPLATE bug
  CLASS (a non-gitignore-aware file scanner failing only in CI); a faithful run
  investigates it as a real RCA, so flailing at reproduction is itself signal.
