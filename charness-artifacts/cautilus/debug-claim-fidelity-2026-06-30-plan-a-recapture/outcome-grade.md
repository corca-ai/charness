# Outcome grade — debug-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 6/6 (pass_rate 1.0); skipped 0, errors 0, total 6.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-debug | deterministic | pass | The captured run actually executed the debug skill (sanity floor before grading the work). | summary matched 'Execution of /debug' |
| wrote-debug-artifact | deterministic | pass | The run materialized a durable debug artifact (the debug-memory surface every run must leave behind), not just an in-chat answer. | 2 output(s) match '**/debug/*.md' |
| falsifiable-hypothesis-before-fix | judge | pass | The run stated a falsifiable root-cause hypothesis and tested it (a reproduction or the cheapest disconfirming check) BEFORE applying any fix — the debug discipline of not jumping to a fix before the cause is proven, whether or not five-steps.md was opened. | Trace shows 'REPRODUCTION: helper fallback in non-git context' Bash run + DISCONFIRMER grep during investigation; artifact has falsifiable Hypothesis w/ explicit disconfirmer, confirmed Reproduction. No code fix applied (RCA-only). |
| detection-gap-substance | judge | pass | The run's Detection Gap names a SPECIFIC existing gate or detection surface that failed to catch the bug and WHY it failed (concrete: the gate exists but does not cover this case, with evidence), not a generic 'add a test' — or an explicit, justified 'n/a — trivial fix' only when the bug is genuinely single-site trivial. | Detection Gap names specific gate '--require-git-file-listing' strict knob, why it failed (action=store_true, default off, quality-core.yml invokes validators without it), not generic 'add a test'. |
| sibling-search-substance | judge | pass | The run abstracted the bug's mental model and searched for sibling occurrences across the codebase, recording a per-sibling decision (fix / skip-with-reason / follow-up), rather than fixing only the one reported site. | Artifact has 'Interface-Shape Sibling Scan' + 'Sibling Search' section; trace greps all rglob/os.walk scanners repo-wide, recording per-site decisions: check_current_pointer_writes (narrower), validate_packaging (same shape), 3 raw walkers. |
| prevention-substance | judge | pass | The run proposed a concrete smallest-change prevention move tied to the named detection gap (a gate, test, or invariant that would have caught this class of bug), not a vague exhortation to be careful. | Detection Gap section names the gap (--require-git-file-listing knob, default off, never armed in CI) and gives concrete smallest change: arm flag in CI or default require_git=True so non-git scan fails loud. |

## Honest caveats

- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED unless a live judge (`--judge-cmd`, ask-before-run spend) ran.
- `trace_tool_used` args matching is best-effort: the trace digest truncates `args` (~160 chars), so a long command can undercount.
- `output_file_*` checks resolve against the bundle `outputs/` dir, which the A/B runner now preserves; a bundle captured before that (no `outputs/`) fails those checks with that explicit evidence.

