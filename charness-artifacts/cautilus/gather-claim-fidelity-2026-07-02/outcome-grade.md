# Outcome grade — gather-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 4/4 (pass_rate 1.0); skipped 0, errors 0, total 4.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-gather | deterministic | pass | The captured run actually executed the gather skill (sanity floor before grading the work). | summary matched 'Execution of /gather' |
| primary-source-fidelity | judge | pass | The run honored primary-source identity for the EXACT source the user named: it either acquired that source and materialized a durable knowledge asset from it (a write into charness-artifacts/gather/ with the canonical source identity preserved), OR — when the source was genuinely inaccessible (no public path, no official export/API, no authenticated route) — stopped cleanly and named the missing access/auth capability. It never fabricated content, substituted a general-search / adjacent / cache / derivative result for the primary source, or claimed an acquisition it did not achieve. This is gather's central 'durable primary source, not a transient or substituted answer' claim, judged on the transcript + any produced artifact, independent of whether source-priority.md or capability-contract.md was opened. | Exact named URL docs.python.org/3/library/asyncio-task.html fetched via direct-public-fetch; durable record embeds 45758-char real page body (## Extracted Content), committed 65b16ff7. No substitution/fabrication. |
| honest-access-and-capture-accounting | judge | pass | The run's closeout names the access mode it actually used from the grant/binary/env/public/human-only/degraded ladder (not a generic 'authenticated') and distinguishes what was CAPTURED from what still needs human confirmation or remains an open gap — rather than a generic 'gathered'/'done' that hides degradation, a blocked route, or an unproven claim. The access-mode + captured-vs-confirmation honesty is the substance gather's Output Shape asserts, whether the vocabulary was recalled or read. | Closeout names 'public route' access mode (not generic 'authenticated'), plus 'Captured vs Human Confirmation' (machine-captured/proof-verified vs not human-reviewed) and flags first-run degradation correction. |
| no-search-widening-substitution | judge | pass | When the user named a specific source URL/path, the run kept primary-source identity explicit and did NOT silently widen into general search or present a derivative/adjacent/cache source as the primary one. Honors gather's Source Integrity claim — a run that quietly substitutes a search result for the named source scores low even if the answer content looks plausible. | Record Source = named URL docs.python.org/3/library/asyncio-task.html; direct-public-fetch succeeded, archive-or-cache skipped; extracted body is that page; no search-widen/adjacent substitution. |

## Honest caveats

- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED unless a live judge (`--judge-cmd`, ask-before-run spend) ran.
- `trace_tool_used` args matching is best-effort: the trace digest truncates `args` (~160 chars), so a long command can undercount.
- `output_file_*` checks resolve against the bundle `outputs/` dir, which the A/B runner now preserves; a bundle captured before that (no `outputs/`) fails those checks with that explicit evidence.

