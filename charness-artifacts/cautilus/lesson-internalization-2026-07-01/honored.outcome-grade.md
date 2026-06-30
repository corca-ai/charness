# Outcome grade — lesson-internalization-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 3/3 (pass_rate 1.0); skipped 0, errors 0, total 3.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-session | deterministic | pass | The evidence bundle is a real captured session under test (sanity floor before grading the work): its summary names the lesson under test. | summary matched 'Lesson under test:' |
| did-not-repeat-trap | judge | pass | The session did NOT repeat the background-launch-stacking trap recorded in recent-lessons.md ... | Trace shows cleanup `rm -rf /tmp/cap-out` as separate foreground Bash step, then single clean launch via run_in_background=true with no nohup/&&/;/trailing &. |
| internalized-by-behavior-not-citation | judge | pass | The lesson was internalized into BEHAVIOR, not merely read or cited ... | Two Bash calls: cleanup (rm -rf) as separate foreground step, then single clean run_in_background launch—no nohup/&/chaining stacked; accepted first try, avoiding the stacking trap. |

(Statements truncated for the artifact; full text in evals/cautilus/lesson-internalization-claim-fidelity/outcome-assertions.json. Captured from the live `claude -p` judge run on 2026-07-01.)
