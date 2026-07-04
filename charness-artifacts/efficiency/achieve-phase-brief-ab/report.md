# Efficiency A/B — achieve-phase-brief-ab

Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.

## Per-arm (mean [min–max])

| metric | pre-demote | post-demote |
| --- | --- | --- |
| n | 3 | 3 |
| pass_rate | 1.0 | 1.0 |
| total_tokens | 4.31127e+06 [3.67098e+06–4.66486e+06] | 4.82202e+06 [3.8957e+06–6.2238e+06] |
| output_tokens | 87606 [71127–114341] | 77895.7 [64253–86644] |
| duration_ms | 696391 [626416–736602] | 623165 [545436–731790] |
| tool_count | 48 [40–55] | 50.7 [42–66] |
| waste_smell_count | 2 [2–2] | 2 [2–2] |
| output_lines | 367.7 [323–391] | 348.3 [320–370] |

## Deltas vs `pre-demote` (mean %, + = spends more)

| metric | post-demote |
| --- | --- |
| total_tokens | +11.8% |
| output_tokens | -11.1% |
| duration_ms | -10.5% |
| tool_count | +5.6% |
| waste_smell_count | +0% |
| output_lines | -5.3% |

## Outcome grade (advisory)

Per-eval discriminating assertions graded over each run's evidence bundle (separate from the matcher pass_rate above, which scores routing/coverage). Pairs the efficiency deltas with whether the work was actually done — a leaner number can just mean an arm did less.

| arm | outcome pass_rate (mean [min–max]) | runs graded | judge skipped | errors |
| --- | --- | --- | --- | --- |
| pre-demote | 1 [1–1] | 3 | 0 | 0 |
| post-demote | 1 [1–1] | 3 | 0 | 0 |

- Deterministic checks grade for free; judge-kind assertions are SKIPPED unless `--judge-cmd` (ask-before-run spend) ran — a high `judge skipped` count means the live judge did not run.

## Honest caveats

- n=3 per arm — read the [min–max] range, not just the mean; small-n means overlap is common.
- output_lines is best-effort (added lines in the worktree vs the capture base ref, including any in-run commit's slice).
- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.
- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.

