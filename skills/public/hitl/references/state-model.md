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
- `accepted_rules`
- `active_rules_applied`
- `target_cursor_checked`
- `target_cursor_check_result`
- `last_presented_chunk_id`
- `applied_rewrite_review_status`
- `pending_rewrite_chunk_id`
- `pending_rewrite_source_anchor`
- `last_rewritten_chunk_id`
- `last_rewrite_review_result`
- `full_target_review_item_id`
- `full_target_review_status`
- `full_target_review_result`
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

When a reviewer asks for a rewrite, revision, or current-chunk change, set
`applied_rewrite_review_status: pending` after the edit is applied and before
the cursor moves. The scratchpad should record the applied excerpt, source
anchor, surrounding context, and any verification result. The next assistant
response shows that material and asks whether the rewritten chunk is accepted or
needs another revision. Only after that judgment is recorded should state update
`last_presented_chunk_id` to a later chunk. If the reviewer requests another
revision, keep the same chunk active and refresh the pending applied-rewrite
record instead of advancing.

Before editing or rewriting a chunk, copy the relevant accepted rules into
`active_rules_applied` and record `target_cursor_checked` only with a
`target_cursor_check_result` that names the target, chunk id, queue item, line
bounds, and queue epoch checked. If a rule violation or stale cursor is found
after the edit, keep the same chunk active and record the repair need in
`target_cursor_check_result` instead of advancing.
`check_review_state.py --phase pre-edit` and `--phase cursor-advance` provide a
minimal runtime gate for these transitions: they fail when accepted rules have
not been activated, target/cursor evidence is missing, or an applied rewrite is
still pending human judgment.

Bootstrap may seed `full_target_review` as a pending completion item with an
activation condition. After the target edit has been applied or staged at the
end of the chunk queue, the run must advance that item before the target can be
closed as accepted. The item asks for whole-target judgment over the full
updated document, or a clearly bounded full target-scope view when the file is
too large. Record the final judgment in both `state.yaml` and
`hitl-scratchpad.md`; use `needs_another_pass` instead of `accepted` when the
composed document has duplicated concepts, terminology drift, missing
transitions, or stale earlier prose.

Portable rule:

- keep the runtime state near the repo
- persist before every user pause
- persist accepted decisions before advancing the cursor
- keep enough cursor data to resume honestly
- before closeout or handoff, sync hidden runtime state into the checked-in
  `charness-artifacts/hitl/latest.md` checkpoint
- treat a missing or stale HITL runtime sync metadata block as a closeout
  failure, not as a cosmetic artifact drift
