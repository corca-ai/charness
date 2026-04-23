# HITL State Model

Portable `hitl` should persist resumable runtime state under a repo-owned
directory, not a host-specific global location.

Recommended runtime layout:

```text
.charness/hitl/runtime/<session-id>/
  hitl-scratchpad.md
  state.yaml
  rules.yaml
  queue.json
  fix-queue.yaml
  events.log
```

Recommended state fields:

- `session_id`
- `status`
- `target`
- `origin`
- `base_ref`
- `scope`
- `last_presented_chunk_id`
- `intent_resync_required`
- `last_intent_resync_at`
- `revisit_cadence`
- `observation_points`
- `automation_candidates`

Use `origin: quality-non-automatable` when the review loop starts from a
`quality` proposal. In that case, queue entries should retain the original
`review_question`, `decision_needed`, and `must_not_auto_decide` fields so the
review does not collapse into a generic approval pass.
Queue entries should also retain the source path plus line span or excerpt used
for the last presented chunk so resumed review does not drift into summary-only
reconstruction.

After each accepted chunk:

- write an `Accepted working text` section to `hitl-scratchpad.md`
- keep decision summaries, rationale, caveats, and open questions under `Notes`
- update `state.yaml` with the latest chunk cursor, such as
  `last_presented_chunk_id`
- only then present the next chunk

If the accepted output is still unsettled, record the current working text and
name the open question instead of storing only a summary of the conversation.

Portable rule:

- keep the runtime state near the repo
- persist before every user pause
- persist accepted decisions before advancing the cursor
- keep enough cursor data to resume honestly
