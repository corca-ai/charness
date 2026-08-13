# Compaction Lesson Presentation Miss Retro
Date: 2026-08-14

## Context

The user corrected the claim that #614's lesson presentation was unproven. The
correction exposed a released workflow defect: the lesson opener stored IDs and
an output hash but left the readable lesson content in compactable context.

## Evidence Summary

- Rollout `019ffaeb-56af-72d2-b03c-bf034ea4aa4d` contains the exact ten-ID
  assistant presentation at `2026-08-13T11:44:04.923Z`.
- The first of five compactions followed at `12:06:33.015Z`.
- The #614 receipt and ledger snapshot match the presented list exactly.
- Reconstructing the rendered list yields the receipt's exact 3,122 bytes and
  `stdout_sha256`, confirming that the opener already possessed the content it
  should have frozen.
- The user directly confirmed seeing the list.
- [#617](https://github.com/corca-ai/charness/issues/617) preserves the bug and
  durable lesson-session bundle boundary; its body readback is byte-identical.

## Waste

The system made the user repair an agent memory error even though the lesson
opening command had held every byte needed for durable recovery. A green
continuity report then made the false negative look deliberate. Two proposed
repairs repeated the ownership mistake: first inventing a new presentation
receipt, then making the host session log the normal lookup path. The user
redirected the fix to saving and referring to the received lessons themselves.

## Critical Decisions

- Correct the factual diagnosis without backfilling a score after the work.
- Treat the session log as forensic evidence for the historical incident only.
- Persist future opened lessons as a human-readable, receipt-bound session file
  and make work/retro refer to it by explicit session ID.
- File #617 as an off-goal bug rather than silently expanding the active goal.

## North Star Alignment

P4/P5 were initially violated: an internally consistent continuity green was
treated as support for a wrong content claim. The distinct observer and channel
that caught it were the user plus the Codex rollout. The repair moves the teeth
to the lesson-session producer: freeze the content it already renders, without a
generic transcript gate.

## Expert Counterfactuals

- Engelbart's H+LAM+T lens would join the lesson-opening action, the content the
  agent must reuse, and the durable work environment. The missing move was to
  save the received lessons where the agent can reread them after compaction.
- A producer-ownership lens would ask why the command writes a digest of exact
  content it then discards. Writing those same bytes once is smaller and more
  portable than teaching retro to parse host transcripts.

## Sibling Search

- same layer: lesson-session renderer, receipt, and continuity reporter |
  decision: valid follow-up outside the slice | proof: the renderer creates exact
  bytes while durable state retains only IDs/hash | follow-up:
  https://github.com/corca-ai/charness/issues/617
- abstraction up: proof-bearing conversation actions lost from active context |
  decision: same class, diagnostic-only for this slice | proof: static scan only;
  #617 owns the bounded sibling review.

## Lesson Evaluation

Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}

This correction session opened no declared lesson session. The prior #614 score
is not backfilled; #617 must define any historical correction semantics.

## Next Improvements

- **workflow**: after opening a lesson session, retain its bundle path and reread
  that file after compaction and before retro.
- **capability**: write the exact rendered lesson bytes to a session-specific
  Markdown companion and bind them with the existing receipt integrity fields.
- **memory**: keep the exact reproduction and causal boundary in the debug
  artifact and #617 so another compaction cannot reset the diagnosis.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-14-compaction-lesson-presentation-miss-retro.md
