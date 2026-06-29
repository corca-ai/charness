# Efficiency A/B — hitl-outcome-wired

Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.

## Per-arm (mean [min–max])

| metric | hitl |
| --- | --- |
| n | 1 |
| pass_rate | 0.0 |
| total_tokens | 423392 [423392–423392] |
| output_tokens | 13523 [13523–13523] |
| duration_ms | 66033 [66033–66033] |
| tool_count | 5 [5–5] |
| waste_smell_count | 0 [0–0] |
| output_lines | 0 [0–0] |

## Outcome grade (advisory)

Per-eval discriminating assertions graded over each run's evidence bundle (separate from the matcher pass_rate above, which scores routing/coverage). Pairs the efficiency deltas with whether the work was actually done — a leaner number can just mean an arm did less.

| arm | outcome pass_rate (mean [min–max]) | runs graded | judge skipped | errors |
| --- | --- | --- | --- | --- |
| hitl | 0.778 [0.778–0.778] | 1 | 0 | 0 |

- Deterministic checks grade for free; judge-kind assertions are SKIPPED unless `--judge-cmd` (ask-before-run spend) ran — a high `judge skipped` count means the live judge did not run.

## Honest caveats

- n=1 per arm — read the [min–max] range, not just the mean; small-n means overlap is common.
- output_lines is best-effort (added lines in the worktree vs the ref; excludes any in-run commits).
- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.
- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.

