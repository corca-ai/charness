# Efficiency A/B — retro pre/post the plan_retro_run.py planner (clean variant-A-vs-B)

Date: 2026-06-29

Handoff item 1(a): the clean variant-A-vs-B EFFICIENCY re-run. Compares `/charness:retro`
*before* vs *after* the planner-first extraction (commit `167cad5c` "retro: extract
plan_retro_run.py planner"; pre = `167cad5c~1` = `a7e49790`). Both arms run the identical
`/charness:retro` prompt, so find-skills auto-routing is constant — the delta is the
planner-extraction effect, not routing contamination. n=2 per arm.

## Result: the planner-first refactor made retro ~15–22% leaner, correctness held

| metric | pre-planner (n=2) | post-planner (n=2) | delta |
| --- | --- | --- | --- |
| total_tokens | 2.43M [2.31–2.55M] | 2.07M [2.04–2.09M] | **−14.9%** |
| output_tokens | 54,370 [51.8–57.0k] | 47,827 [43.6–52.1k] | −12% |
| duration_ms | 306,298 [287–326s] | 240,083 [235–245s] | **−21.6%** |
| tool_count | 25 [22–28] | 19.5 [19–20] | **−22%** |
| waste_smell_count | 0 | 0 | n/a |
| matcher pass_rate | 1.0 | 1.0 | — |

The arms are **cleanly non-overlapping** even at n=2 (post-planner's token/duration/tool
ranges sit entirely below pre-planner's), so the win is signal, not small-n noise. Both
arms held matcher `pass_rate 1.0` — the planner extraction cut ~1/5 of the tool calls and
wall-clock **without degrading claim-fidelity**. This is the highest-value charness A/B: it
proves a skill refactor's efficiency effect with n>1, isolated by holding the prompt
constant across two git refs.

## Proves the "no assertion set" outcome path

retro ships no `evals/cautilus/retro-claim-fidelity/outcome-assertions.json`, so the wired
harness graded nothing and the report carries **no Outcome-grade section** (both arms record
`eval_id: null, runs_graded: 0` in `results.json`). This is the correct skip path — the
outcome section appears only when an eval has discriminating assertions (contrast the hitl
run, which folds the section in). Adding a retro assertion set stays deferred: each new set
is a hypothesis needing its own live capture (live-capture-before-assert), best added when
the correctness sweep captures retro, not speculatively here.

## Honest non-claims

- **n=2.** Small; the ranges are reported and happen to be clean here, but two captures per
  arm is a comparison, not a distribution.
- **The delta is the whole `167cad5c` commit**, which extracted `plan_retro_run.py` and
  routed `expert-lens.md` — the A/B isolates the ref pair, not any single line within it.
- **Efficiency only.** Advisory process/size metrics; no LLM judge ran (retro has no
  assertion set). Bundles are clean — 0 binary files (the `.pyc`/binary-skip fix holds).
