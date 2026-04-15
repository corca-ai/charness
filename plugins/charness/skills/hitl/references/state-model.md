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

Portable rule:

- keep the runtime state near the repo
- persist before every user pause
- keep enough cursor data to resume honestly
