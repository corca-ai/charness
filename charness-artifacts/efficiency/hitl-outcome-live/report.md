# Efficiency A/B — hitl-outcome-live

Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.

## Per-arm (mean [min–max])

| metric | hitl |
| --- | --- |
| n | 1 |
| pass_rate | 1.0 |
| total_tokens | 1.07248e+06 [1.07248e+06–1.07248e+06] |
| output_tokens | 19172 [19172–19172] |
| duration_ms | 109824 [109824–109824] |
| tool_count | 13 [13–13] |
| waste_smell_count | 0 [0–0] |
| output_lines | 0 [0–0] |

## Honest caveats

- n=1 per arm — read the [min–max] range, not just the mean; small-n means overlap is common.
- output_lines is best-effort (added lines in the worktree vs the ref; excludes any in-run commits).
- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.
- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.

