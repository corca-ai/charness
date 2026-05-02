# HITL Adaptive Decision Queue

## Problem

`hitl` report mode currently preserves packet item order. That makes the review
mechanically source-ordered even when one early human decision could establish a
rule, unblock later judgments, or make the remaining queue stale.

The current slice changes report mode into an adaptive decision queue: present
the highest-leverage decision first, re-order remaining cards after explicit
human input, and recommend stopping the current queue when accepted feedback
means the target should be fixed before further review.

## Current Slice

- Add deterministic report-mode ordering from explicit item metadata.
- Let structured review input reprioritize remaining unreviewed items.
- Let structured review input recommend queue restart/invalidation without
  treating that recommendation as human approval.
- Keep the public `SKILL.md` core thin and put concrete schema in
  `references/report-mode.md` plus helper tests.

## Fixed Decisions

- Adaptive report packets require stable explicit item IDs. Generated
  `item-N` fallback IDs remain valid only for non-adaptive packets.
- Ordering is deterministic and helper-owned. Inputs include `priority`,
  `depends_on`, `blocks`, `tags`, `source_order`, and review-input
  `queue_effects`.
- Existing reviewed items are not reordered or re-presented when review input
  is supplied. Only remaining unreviewed items are candidates for the next
  queue order.
- Stop/restart is a meta-decision card, not an automatic target edit and not an
  approval of remaining cards.
- Queue effects come from structured `review-input`; this slice does not parse
  free-form human comments.
- Public skill wording names the behavior only. Schema, tie-breakers, and
  examples live below the public core.

## Probe Questions

- Whether the current browser save UI should expose queue effects directly.
  Signal: real HITL use shows repeated manual construction of structured
  review-input effects. Current slice keeps browser save compact.

## Deferred Decisions

- Cross-session priority learning, analytics, and global tuning.
- Concurrent multi-operator queue locking.
- A richer support-layer review product beyond portable report-mode HTML and
  JSON.

## Non-Goals

- No natural-language inference from comments.
- No evaluator requirement for ordinary HITL adaptive ordering.
- No target-file edits during report review.
- No generic queue framework outside `hitl`.

## Deliberately Not Doing

- Do not add a public mode enum for adaptive ordering. Adaptive ordering is the
  report-mode default when metadata is present, with source order as a
  deterministic fallback.
- Do not mark superseded or stale items as approved. They remain unreviewed with
  a structured reason.
- Do not persist agent restart recommendations as accepted human decisions
  unless the review input explicitly records the queue action.

## Constraints

- Stable item identity must survive reordering.
- Suggested item decisions and queue recommendations are display-only unless
  human input explicitly records them.
- Reprioritization state must be portable JSON and repo-relative.
- Ties must be deterministic: priority score first, then `source_order`, then
  `id`.

## Success Criteria

- A packet ordered `a,b,c` can render `b` first when explicit metadata says it
  is the highest-leverage decision.
- After a human decision on `b`, structured queue effects can rerender the
  remaining cards as `c,a` without re-presenting `b`.
- When a human answer makes the remaining queue stale, the next review surface
  shows a restart recommendation meta-card before ordinary cards.
- Restart recommendations and superseded items stay display-only/unreviewed
  unless explicit human queue action is submitted.
- Existing report-mode guarantees still hold: suggestions do not become
  approvals, untouched cards are dropped from saved decisions, duplicate IDs are
  rejected, and unsafe HTML is sanitized.

## Acceptance Checks

- Unit/helper test: adaptive priority metadata renders `b,c,a` from source
  order `a,b,c`.
- Unit/helper test: review input for `b` with a `boost_tag` queue effect renders
  remaining items as `c,a` and decisions JSON includes only explicit `b`.
- Unit/helper test: review input with `recommend_restart` emits a queue
  recommendation/meta-card, records superseded unreviewed IDs, and does not
  approve those IDs.
- Unit/helper negative test: adaptive metadata without explicit item IDs is
  rejected.
- Existing `tests/quality_gates/test_portable_json_artifacts.py` report-mode
  tests still pass.

## Premortem

Fresh-Eye Satisfaction: parent-delegated.

Act Before Ship:

- Require stable explicit IDs for adaptive queues.
- Define deterministic ordering inputs and tie-breakers.
- Model queue invalidation/restart as structured state, not prose-only
  `agent_next_step`.
- Keep stop/restart human-owned and display-only until explicit queue action.

Bundle Anyway:

- Extend schema version/summary fields enough that adaptive report outputs are
  distinguishable.
- Record queue-effect reasoning in decisions output so later agents can resume
  without chat memory.

Over-Worry:

- Full UI redesign, global queue uniqueness, cryptographic audit logs, and
  evaluator-required validation are not needed for this slice.

Valid But Defer:

- Cross-session learning, global priority tuning, concurrent queue locking, and
  broader non-HITL queue infrastructure.

## Post-Implementation Premortem

Fresh-Eye Satisfaction: parent-delegated.

Act Before Ship:

- Blank adaptive item IDs must not fall back to generated `item-N` IDs. Fixed
  by making explicit adaptive IDs mean nonblank IDs and adding a negative test.
- Queue effects must not act on an otherwise untouched card. Fixed by requiring
  an explicit decision or comment when `queue_effects` are present.
- Full slice closeout must run because this slice spans plugin export,
  markdown, prompt proof, public skill dogfood, integrations, and repo Python.
  Completed with `python3 scripts/run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review`.

Bundle Anyway:

- `schema_version: 2` is an intentional additive output-shape marker for
  queue state and effects; no current repo consumer is pinned to report-mode
  decisions schema v1.

Valid But Defer:

- Multiple simultaneous `recommend_restart` effects, richer dependency gates
  that distinguish reviewed from resolved, and nonadaptive queue-state wording.

## Canonical Artifact

`charness-artifacts/spec/hitl-adaptive-decision-queue.md`

## First Implementation Slice

Update `scripts/hitl_report_mode_lib.py`, `scripts/hitl_adaptive_queue_lib.py`,
`skills/public/hitl/references/report-mode.md`,
`skills/public/hitl/SKILL.md`, and focused report-mode tests.
