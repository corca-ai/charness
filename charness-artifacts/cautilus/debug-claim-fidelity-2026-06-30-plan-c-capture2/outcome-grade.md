# Outcome grade — debug-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 6/6 (pass_rate 1.0); skipped 0, errors 0, total 6.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-debug | deterministic | pass | The captured run actually executed the debug skill (sanity floor before grading the work). | summary matched 'Execution of /debug' |
| wrote-debug-artifact | deterministic | pass | The run materialized a durable debug artifact (the debug-memory surface every run must leave behind), not just an in-chat answer. | 2 output(s) match '**/debug/*.md' |
| falsifiable-hypothesis-before-fix | judge | pass | The run stated a falsifiable root-cause hypothesis and tested it (a reproduction or the cheapest disconfirming check) BEFORE applying any fix — the debug discipline of not jumping to a fix before the cause is proven, whether or not five-steps.md was opened. | Trace shows FALSIFIER 1/2 Bash checks run before any edit; artifact has falsifiable Hypothesis + Verification (real-scanner repro, exit 1) confirming cause; no source fix applied (debug-only). |
| detection-gap-substance | judge | pass | The run's Detection Gap names a SPECIFIC existing gate or detection surface that failed to catch the bug and WHY it failed (concrete: the gate exists but does not cover this case, with evidence), not a generic 'add a test' — or an explicit, justified 'n/a — trivial fix' only when the bug is genuinely single-site trivial. | Detection Gap names inventory_gitignore_scan_hygiene.py DEFAULT_PATH_GLOBS + _is_repo_wide_glob, with WHY each didn't fire (scanners match no glob; receiver-name-only check) verified via --json []. |
| sibling-search-substance | judge | pass | The run abstracted the bug's mental model and searched for sibling occurrences across the codebase, recording a per-sibling decision (fix / skip-with-reason / follow-up), rather than fixing only the one reported site. | Output has 'Sibling Search' section: explicit mental model, per-sibling decisions (same bug/runtime repro, follow-up deferred docs/handoff.md, same-class diagnostic-only), abstraction-up/down scan. |
| prevention-substance | judge | pass | The run proposed a concrete smallest-change prevention move tied to the named detection gap (a gate, test, or invariant that would have caught this class of bug), not a vague exhortation to be careful. | Detection Gap section: 'fix: broaden to scripts/*.py' for inventory_gitignore_scan_hygiene gate, and 'fix: flag any rglob/os.walk outside git-aware context' for _is_repo_wide_glob — concrete gate-scope changes. |

## Honest caveats

- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED unless a live judge (`--judge-cmd`, ask-before-run spend) ran.
- `trace_tool_used` args matching is best-effort: the trace digest truncates `args` (~160 chars), so a long command can undercount.
- `output_file_*` checks resolve against the bundle `outputs/` dir, which the A/B runner now preserves; a bundle captured before that (no `outputs/`) fails those checks with that explicit evidence.

