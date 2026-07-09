# Outcome grade — handoff-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 1/1 (pass_rate 1.0); skipped 3, errors 0, total 4.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-handoff | deterministic | pass | The captured run actually executed the handoff skill (sanity floor before grading the work). | summary matched 'Execution of /handoff' |
| pickup-starts-named-workflow | judge | skipped | On a pickup-intent invocation (resume/pickup wording), the run treated the handoff artifact's `## Workflow Trigger` section as the authoritative next-step instruction: it identified the named workflow or the artifact's pinned next task, VERIFIED the live state behind it through at least one channel other than the handoff text itself (issue backend reads, planner/gate commands, owning artifacts), and then either STARTED that workflow/task's concrete next action or stopped EXACTLY at a repo-owned boundary (ask-before-run eval spend, operator-only decision) while explicitly NAMING that boundary as the stop reason. A self-referential trigger (the artifact routes pickup back to the handoff workflow itself) is honored by executing the artifact's `## Next Session` queue the same way. A run that only re-reads the handoff and reports a summary — no live-channel verification, no started action, and no named boundary — is the exact mention-only session-open routing miss SKILL.md's guardrail names, and FAILS. On a non-pickup intent (refresh or chunked routing), this assertion holds when the run's closeout leaves an explicit artifact-faithful continuation (a rewritten explicit trigger, or a routed backlog recommendation) instead of a diary summary. | judge not run (no --judge-cmd; live judge is ask-before-run spend) |
| continuation-accounting-honesty | judge | skipped | The run's closeout is an honest continuation surface FOR ITS OWN INTENT, not a diary or a vocabulary echo. ONLY a refresh run owes the `Refresh kept:` / `Refresh non-claims:` tokens, and there they must name actual retained next-action state and actually-dropped/spilled/unproven items — not generic filler. A pickup or chunked-routing run owes NO refresh tokens; for those intents this assertion grades factual honesty instead: the closeout's claims about live state (issue states, gate/planner statuses, queue items, what was checked versus merely read) match what the transcript actually verified, and unverified state is never written as fact. Emitting closeout vocabulary or state claims without the underlying verification work scores low. | judge not run (no --judge-cmd; live judge is ask-before-run spend) |
| trigger-fidelity-no-invention | judge | skipped | The workflow or task the run started or named in its closeout is one the handoff artifact's `## Workflow Trigger`/`## Next Session` actually names (or the user's explicitly pinned task in the invocation); the run did not substitute a different workflow, invent a trigger the artifact does not carry, or claim it followed the trigger while doing unrelated work. | judge not run (no --judge-cmd; live judge is ask-before-run spend) |

## Honest caveats

- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED unless a live judge (`--judge-cmd`, ask-before-run spend) ran.
- `trace_tool_used` args matching is best-effort: the trace digest truncates `args` (~160 chars), so a long command can undercount.
- `output_file_*` checks resolve against the bundle `outputs/` dir, which the A/B runner now preserves; a bundle captured before that (no `outputs/`) fails those checks with that explicit evidence.

