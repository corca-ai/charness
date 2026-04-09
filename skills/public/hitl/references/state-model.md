# HITL State Model

Portable `hitl` should persist resumable runtime state under a repo-owned
directory, not a host-specific global location.

Recommended runtime layout:

```text
<output_dir>/runtime/<session-id>/
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
- `base_ref`
- `scope`
- `last_presented_chunk_id`
- `intent_resync_required`
- `last_intent_resync_at`

Portable rule:

- keep the runtime state near the repo
- persist before every user pause
- keep enough cursor data to resume honestly
