# Efficiency A/B — prompt-mutation-handoff-refresh-pilot

Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.

## Per-arm (mean [min–max])

| metric | baseline | m-bootstrap | m-workflow | m-closeout |
| --- | --- | --- | --- | --- |
| n | 2 | 2 | 2 | 2 |
| pass_rate | 1.0 | 0.0 | 1.0 | 1.0 |
| total_tokens | 2.85361e+06 [2.80854e+06–2.89869e+06] | 5.56447e+06 [3.22834e+06–7.90059e+06] | 2.18266e+06 [1.25899e+06–3.10633e+06] | 2.72906e+06 [1.9145e+06–3.54362e+06] |
| output_tokens | 43496 [39394–47598] | 105448 [64006–146890] | 48778 [33516–64040] | 54840 [42180–67500] |
| duration_ms | 337200 [294144–380255] | 731466 [551597–911335] | 353432 [202459–504406] | 453487 [369445–537529] |
| tool_count | 37 [36–38] | 49.5 [35–64] | 29 [16–42] | 34.5 [29–40] |
| waste_smell_count | 1.5 [1–2] | 1.5 [1–2] | 1 [0–2] | 2 [2–2] |
| output_lines | 18.5 [17–20] | 47.5 [27–68] | 23.5 [18–29] | 71.5 [21–122] |

## Deltas vs `baseline` (mean %, + = spends more)

| metric | m-bootstrap | m-workflow | m-closeout |
| --- | --- | --- | --- |
| total_tokens | +95% | -23.5% | -4.4% |
| output_tokens | +142.4% | +12.1% | +26.1% |
| duration_ms | +116.9% | +4.8% | +34.5% |
| tool_count | +33.8% | -21.6% | -6.8% |
| waste_smell_count | +0% | -33.3% | +33.3% |
| output_lines | +156.8% | +27% | +286.5% |

## Outcome grade (advisory)

Per-eval discriminating assertions graded over each run's evidence bundle (separate from the matcher pass_rate above, which scores routing/coverage). Pairs the efficiency deltas with whether the work was actually done — a leaner number can just mean an arm did less.

| arm | outcome pass_rate (mean [min–max]) | runs graded | judge skipped | errors |
| --- | --- | --- | --- | --- |
| baseline | 1 [1–1] | 2 | 6 | 0 |
| m-bootstrap | 1 [1–1] | 2 | 6 | 0 |
| m-workflow | 1 [1–1] | 2 | 6 | 0 |
| m-closeout | 1 [1–1] | 2 | 6 | 0 |

- Deterministic checks grade for free; judge-kind assertions are SKIPPED unless `--judge-cmd` (ask-before-run spend) ran — a high `judge skipped` count means the live judge did not run.

## Honest caveats

- n=2 per arm — read the [min–max] range, not just the mean; small-n means overlap is common.
- output_lines is best-effort (added lines in the worktree vs the capture base ref, including any in-run commit's slice).
- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.
- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.

