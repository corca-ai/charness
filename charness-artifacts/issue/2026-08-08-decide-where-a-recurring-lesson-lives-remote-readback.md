# Remote issue closeout readback

Date: 2026-08-04

Goal: `2026-08-08-decide-where-a-recurring-lesson-lives`

Carrier: `4a2170da0a02d8dad066af9eed20beb8c9a40ceb`, the previously published
closeout carrier for issues #497, #500, and #501.

Observer and channel: authenticated `gh issue view` readback through the
GitHub backend, distinct from local carrier validation and the local behavior
tests.

Observed at: `2026-08-04T05:18:54Z`.

Command:

```text
for n in 497 500 501; do
  gh issue view "$n" --repo corca-ai/charness --json number,state,title,closedAt,url
done
```

Readback:

```json
{"closedAt":"2026-08-04T03:10:55Z","number":497,"state":"CLOSED","title":"validate_adapters.py cannot be imported in the exported plugin: hardcoded skills.public path the export flattens away","url":"https://github.com/corca-ai/charness/issues/497"}
{"closedAt":"2026-08-04T03:10:55Z","number":500,"state":"CLOSED","title":"The second goal-artifact creator is unguarded: draft_goal_from_chunk.py does not get upsert_goal.py's value guards","url":"https://github.com/corca-ai/charness/issues/500"}
{"closedAt":"2026-08-04T03:10:56Z","number":501,"state":"CLOSED","title":"check_export_safe_imports scans import statements only, so a module path passed as a string slips through (this is how #497 shipped)","url":"https://github.com/corca-ai/charness/issues/501"}
```

This records remote tracker state only; it does not replace the carrier's
per-issue behavior verdicts or the local resolution critique.
