# Outcome grader — WIRED into the A/B harness (live end-to-end)

Date: 2026-06-29

First live run of the OUTCOME layer **auto-graded inside the A/B harness** (commit
`08c15fbf`), not as a separate `grade_skill_outcome.py` call. Proves handoff item 1(4):
a fresh `/charness:hitl` capture at HEAD is captured, graded, and the per-arm outcome is
**folded into `report.md`** in one `run_skill_efficiency_ab.py --run` invocation, with the
live `claude -p` judge (`--judge-cmd`) and `--keep-untracked-outputs`.

## What ran

- `python3 scripts/run_skill_efficiency_ab.py --run config.json --judge-cmd "python3 scripts/outcome_judge_cmd.py" --keep-untracked-outputs`
- One isolated `/charness:hitl` capture @HEAD (n=1). Both self-tests gated automatically
  (extractor + grader). See `report.md` (efficiency + folded outcome section),
  `results.json` (carries `outcome`), `preserved/hitl__0/` (bundle + `outcome-grade.md`).

## This is the methodology working: a leaner number that did LESS

The single most useful result is the pairing the outcome layer exists to surface:

- **Efficiency: 423,392 total tokens, 66.0s, 5 tool calls** — markedly *leaner* than the
  prior 3-live hitl capture (1.47M tokens, 13 calls).
- **But it did LESS**: the claim matcher scored `pass_rate 0.0` and the outcome grade's
  deterministic `opened-chunk-contract` **FAILED** — this run never engaged
  `references/chunk-contract.md` (the SKILL.md step-5 presentation invariant). The leaner
  token number is lean *because the run skipped a floor*, not because it was better.

Read alone, "423K tokens, 0 waste smells" looks great. Folded next to the outcome grade
(0.778, with the floor miss cited), it reads honestly. That is the entire point of wiring
the outcome grade into the efficiency report.

## Outcome grade: 5/6, pass_rate 0.778, errors 0 — the live judge worked

- **Deterministic**: `ran-hitl` PASS; `materialized-queue` **PASS** — `--keep-untracked-outputs`
  preserved the gitignored `.charness/hitl/runtime/<sess>/queue.json`, so the assertion the
  prior 3-live finding had to record as a FAIL now passes for real; `opened-chunk-contract`
  **FAIL** (honest floor miss, above).
- **Judge (live `claude -p`, 3 calls)**: `chunk-shape` PASS, `non-binding-disposition` PASS,
  `stop-for-approval` PASS — each with cited transcript evidence (the `### Recommended
  Disposition (display-only, non-binding)` shape, `require_explicit_apply:true` / no edits,
  `Awaiting your approval of c1 ... c2-c7 pending`). The deterministic and judge layers
  complement: the run presented a faithful chunk *shape* (judge) yet missed the
  chunk-contract *reference* (matcher) — two independent signals, both visible.

## Bug found and fixed by this run (live-capture-before-assert doing its job)

The FIRST wired run errored all 3 judge-kind assertions with `embedded null byte`:
`--keep-untracked-outputs` swept gitignored `__pycache__/*.pyc` (binary) into the bundle,
whose NUL bytes flowed through `judge_context` → the JSON payload → back to a raw NUL in
`outcome_judge_cmd.py`'s `claude -p` ARG, which `fork_exec` rejects. Fixed in `08c15fbf`
(binary-skip in `preserve_outputs` + NUL-safe `judge_context`). This **vindicated critique
concern C3** (the file-count/junk sweep the counterweight had dropped as "no consumer" —
the consumer is universal: every captured run emits `.pyc`). This clean re-run has **0
`.pyc` in the bundle (9 binary files omitted), judge errors 0**.

## Honest non-claims

- **n=1.** One capture; the grade describes this run, not a distribution. `opened-chunk-contract`
  FAIL is this run's real floor miss, not a grader defect and not (on one sample) a proven
  hitl regression — it is a claim-fidelity signal the correctness sweep would chase per skill.
- **The LLM judge is non-deterministic.** Well-cited here, but a re-run could vary; this is
  why the outcome layer is ADVISORY, paired with the deterministic layer + offline self-test.
- **Token cost** is dominated by the capture; the 3 judge calls are small. Ask-before-run was
  honored (user-authorized live run).
