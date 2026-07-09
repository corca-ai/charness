# Efficiency A/B — prompt-mutation-handoff-step7-slim

Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.

## Per-arm (mean [min–max])

| metric | baseline | step7_slim |
| --- | --- | --- |
| n | 2 | 2 |
| pass_rate | 1.0 | 1.0 |
| total_tokens | 1.91407e+06 [1.31951e+06–2.50863e+06] | 2.36925e+06 [2.17798e+06–2.56053e+06] |
| output_tokens | 61585.5 [47482–75689] | 55312 [54498–56126] |
| duration_ms | 371989 [305167–438811] | 465806 [430096–501517] |
| tool_count | 23.5 [17–30] | 38 [37–39] |
| waste_smell_count | 2.5 [2–3] | 2.5 [2–3] |
| output_lines | 31 [28–34] | 24 [20–28] |

## Deltas vs `baseline` (mean %, + = spends more)

| metric | step7_slim |
| --- | --- |
| total_tokens | +23.8% |
| output_tokens | -10.2% |
| duration_ms | +25.2% |
| tool_count | +61.7% |
| waste_smell_count | +0% |
| output_lines | -22.6% |

## Outcome grade (advisory)

Per-eval discriminating assertions graded over each run's evidence bundle (separate from the matcher pass_rate above, which scores routing/coverage). Pairs the efficiency deltas with whether the work was actually done — a leaner number can just mean an arm did less.

| arm | outcome pass_rate (mean [min–max]) | runs graded | judge skipped | errors |
| --- | --- | --- | --- | --- |
| baseline | 1 [1–1] | 2 | 6 | 0 |
| step7_slim | 1 [1–1] | 2 | 6 | 0 |

- Deterministic checks grade for free; judge-kind assertions are SKIPPED unless `--judge-cmd` (ask-before-run spend) ran — a high `judge skipped` count means the live judge did not run.

## Honest caveats

- n=2 per arm — read the [min–max] range, not just the mean; small-n means overlap is common.
- output_lines is best-effort (added lines in the worktree vs the capture base ref, including any in-run commit's slice).
- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.
- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.

