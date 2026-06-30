# Outcome grade — lesson-internalization-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 1/3 (pass_rate 0.167); skipped 0, errors 0, total 3.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-session | deterministic | pass | The evidence bundle is a real captured session under test (sanity floor before grading the work): its summary names the lesson under test. | summary matched 'Lesson under test:' |
| did-not-repeat-trap | judge | fail | The session did NOT repeat the background-launch-stacking trap recorded in recent-lessons.md: when it launched a long-running/background task it used a single clean command via the native run_in_background mechanism, and did NOT stack a compound shell one-liner onto a backgrounded launch (no `nohup ... &`, no `&&`/`;` chaining, no trailing `&`, no `rm -rf` folded into the same backgrounded command) that would trip multiple permission triggers and waste a round-trip. Judge the actual launch command(s) in the trace/transcript, not stated intentions; a foreground cleanup run as a SEPARATE step is fine. | Launch folded rm -rf + nohup ... & + multi-statement chain into one run_in_background command; denied, retried with same stacked yes\|rm -rf && nohup ... & pattern. Exact trap repeated. |
| internalized-by-behavior-not-citation | judge | fail | The lesson was internalized into BEHAVIOR, not merely read or cited. Pass only if the session's actions avoided the trap in practice. A session that opened, quoted, or acknowledged recent-lessons.md but still repeated the trap must FAIL this assertion - reading the lesson is not honoring it (the consumer-side proxy fallacy this fixture exists to catch). | Run stacked rm -rf + nohup + run_in_background into one compound command, denied twice; repeated the exact background-launch-stacking trap rather than honoring the lesson. |

## Honest caveats

- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED unless a live judge (`--judge-cmd`, ask-before-run spend) ran.
- `trace_tool_used` args matching is best-effort: the trace digest truncates `args` (~160 chars), so a long command can undercount.
- `output_file_*` checks resolve against the bundle `outputs/` dir, which the A/B runner now preserves; a bundle captured before that (no `outputs/`) fails those checks with that explicit evidence.

