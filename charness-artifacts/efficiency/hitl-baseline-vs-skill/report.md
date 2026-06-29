# Efficiency A/B — hitl-baseline-vs-skill

Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.

## Per-arm (mean [min–max])

| metric | baseline | skill |
| --- | --- | --- |
| n | 3 | 3 |
| pass_rate | 0.0 | 0.667 |
| total_tokens | 818555 [716805–895914] | 848768 [613395–1.03736e+06] |
| output_tokens | 13303.3 [10849–15367] | 18551.3 [13488–24851] |
| duration_ms | 90403.3 [85022–93296] | 111189 [95612–125962] |
| tool_count | 9.3 [8–11] | 9.3 [7–11] |
| waste_smell_count | 0 [0–0] | 0 [0–0] |
| output_lines | 0 [0–0] | 0 [0–0] |

## Deltas vs `baseline` (mean %, + = spends more)

| metric | skill |
| --- | --- |
| total_tokens | +3.7% |
| output_tokens | +39.4% |
| duration_ms | +23% |
| tool_count | +0% |
| waste_smell_count | n/a |
| output_lines | n/a |

## Honest caveats

- n=3 per arm — read the [min–max] range, not just the mean; small-n means overlap is common.
- output_lines is best-effort (added lines in the worktree vs the ref; excludes any in-run commits).
- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.
- Arms are isolated per-ref worktrees; a delta is the ref difference, not cross-contamination.

