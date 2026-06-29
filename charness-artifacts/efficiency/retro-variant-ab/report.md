# Efficiency A/B — retro-variant-ab

Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.

## Per-arm (mean [min–max])

| metric | pre-planner | post-planner |
| --- | --- | --- |
| n | 2 | 2 |
| pass_rate | 1.0 | 1.0 |
| total_tokens | 2.42799e+06 [2.30977e+06–2.54622e+06] | 2.06734e+06 [2.04406e+06–2.09061e+06] |
| output_tokens | 54369.5 [51770–56969] | 47826.5 [43564–52089] |
| duration_ms | 306298 [286587–326009] | 240083 [235442–244724] |
| tool_count | 25 [22–28] | 19.5 [19–20] |
| waste_smell_count | 0 [0–0] | 0 [0–0] |
| output_lines | 0 [0–0] | 0 [0–0] |

## Deltas vs `pre-planner` (mean %, + = spends more)

| metric | post-planner |
| --- | --- |
| total_tokens | -14.9% |
| output_tokens | -12% |
| duration_ms | -21.6% |
| tool_count | -22% |
| waste_smell_count | n/a |
| output_lines | n/a |

## Honest caveats

- n=2 per arm — read the [min–max] range, not just the mean; small-n means overlap is common.
- output_lines is best-effort (added lines in the worktree vs the ref; excludes any in-run commits).
- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.
- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.

