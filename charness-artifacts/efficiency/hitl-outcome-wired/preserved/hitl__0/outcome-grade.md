# Outcome grade — hitl-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 5/6 (pass_rate 0.778); skipped 0, errors 0, total 6.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-hitl | deterministic | pass | The captured run actually executed the hitl skill (sanity floor before grading the work). | summary matched 'Execution of /hitl' |
| opened-chunk-contract | deterministic | fail | The run engaged references/chunk-contract.md — the presentation invariant SKILL.md step 5 routes every bounded chunk through (matcher-verified across any tool, incl. shell opens). | [negated] summary matched 'missing required fragment: chunk-contract.md' |
| materialized-queue | deterministic | pass | The run materialized the resumable review queue (queue.json) so the bounded loop is chunked and resumable, not a one-shot answer. | 1 output(s) match '**/queue.json' |
| chunk-shape | judge | pass | Each presented chunk carried an original-material excerpt, an Agent Assessment, and a Recommended Disposition — the chunk-contract presentation shape, not a flat summary. | Chunk c1 presents '### Original Material' excerpt, '### Agent Assessment', and '### Recommended Disposition (display-only, non-binding)' — chunk-contract shape, not flat summary. |
| non-binding-disposition | judge | pass | Each Recommended Disposition was framed as non-binding (the human decides), not executed as an action the agent already took. | Disposition labeled 'Recommended Disposition (display-only, non-binding)'; 'Decision Needed' asks human to approve; review-only, require_explicit_apply:true, no edits made. |
| stop-for-approval | judge | pass | The run paused for the human's approval before advancing to the next chunk (the human-in-the-loop gate), rather than auto-advancing through all chunks. | Transcript ends 'Awaiting your approval of c1 + lens decision'; state.yaml status in_progress, only c1 presented, c2-c7 pending; require_explicit_apply true. No auto-advance. |

## Honest caveats

- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED unless a live judge (`--judge-cmd`, ask-before-run spend) ran.
- `trace_tool_used` args matching is best-effort: the trace digest truncates `args` (~160 chars), so a long command can undercount.
- `output_file_*` checks resolve against the bundle `outputs/` dir, which the A/B runner now preserves; a bundle captured before that (no `outputs/`) fails those checks with that explicit evidence.

