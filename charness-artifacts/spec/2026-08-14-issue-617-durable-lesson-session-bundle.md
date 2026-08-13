# Issue 617 Durable Lesson Session Bundle

Status: in-progress
Date: 2026-08-14
Source: https://github.com/corca-ai/charness/issues/617

## Problem

`open_lesson_session.py` freezes selected IDs and a hash of its rendered stdout,
but not the exact human-readable lesson content. Active conversation context was
therefore the only place an agent could reread the opened lessons. Compaction
removed that context and retro later rendered a false `presentation-unproven`.

## Capability Contract

Opening a lesson session persists the exact rendered lesson list as a
human-readable, session-specific bundle before affected work. The command emits
the same bytes to stdout, and its receipt binds the bundle by digest and byte
count. Work and retro refer to the bundle by the declared `session_id`; after
compaction the agent rereads the bundle instead of inspecting a host transcript.

## Current Slice

Extend the existing lesson-session open/receipt path with one durable Markdown
companion, validate its byte identity, and route the existing retro lesson
evaluation through that bundle. Do not build session-log lookup.

## Fixed Decisions

- The exact bytes already rendered by `open_lesson_session.py` are the bundle;
  no second renderer or reconstruction path is introduced.
- The bundle uses a deterministic same-stem Markdown path under the existing
  `charness-artifacts/retro/lesson-session-receipts/` directory. The JSON file is
  integrity metadata; the Markdown file is the content an agent reads.
- `bundle_path(output_dir, session_id)` is exactly
  `receipt_directory(output_dir) / f"{session_id}.md"`. The receipt reuses
  `stdout_sha256` and `stdout_byte_count` as the bundle commitment because bundle
  and stdout are byte-identical; it adds no duplicate digest, count, or path.
- A valid new session requires a ledger event, bundle, completed stdout
  emission receipt, and exact agreement among the receipt digest/byte count and
  bundle bytes.
- The receipt has one current contract. Every accepted receipt requires its
  deterministic companion bundle; there is no old-format reader, version
  bridge, migration command, or compatibility branch.
- The one checked-in #614 receipt is updated in place by adding the exact bundle
  whose bytes already match its `stdout_sha256` and `stdout_byte_count`.
- A valid bundle proves exactly which lessons the session-start action issued.
  It does not prove human readback, agent use, or positive effect; retro judges
  those separately and scores only observed effects.
- Retro resolves the bundle from an explicit `session_id`. It does not scan
  unrelated sessions, choose the newest file, or read Codex rollout logs.
- Immediately after open, the affected work's canonical durable artifact cites
  the `session_id` and derived bundle path. A continuation or retro recovers the
  citation from that task/issue/goal artifact rather than from active context or
  a global current-session pointer.
- The #614 historical score is not backfilled. Its exact reconstruction and
  user/log readback remain incident evidence, not a retroactive score event.

## Probe Questions

- Resolved: `lesson_evaluation_continuity_lib.py` owns a write-once atomic bundle
  helper beside its existing fsync-and-replace receipt writer. The bundle is not
  a rolling pointer, so the rolling-pointer writer is not reused.
- Resolved: there is no receipt migration surface. The repository carries one
  current receipt/bundle shape and rejects incomplete state.

## Deferred Decisions

- Reopen an active-session pointer only if explicit `session_id` lookup proves
  insufficient in a real compaction continuation; do not add a global `latest`
  pointer preemptively because concurrent work can make it lie.
- Broader persistence for approvals, announcements, or arbitrary conversation
  actions reopens only after a separate confirmed failure.
- Cross-host lesson injection remains outside this repo-owned evaluator until a
  consumer defines an equivalent durable lesson-session boundary.

## Non-Goals

- Do not ingest, index, or search host transcripts in the normal workflow.
- Do not store a complete conversation or create generic agent memory.
- Do not infer a person read the bundle merely because it exists.
- Do not change lesson selection policy, lifecycle, or graduation behavior.

## Deliberately Not Doing

- No exact-message parser, timestamp cutoff policy, host session resolver, or
  Codex-specific fallback. Those were artifacts of putting the fix in the
  forensic evidence channel rather than the lesson-session owner.
- No reconstruction of future bundles from mutable lesson sources. The content
  is frozen when the session opens.
- No mandatory pointer to whichever session was opened most recently.

## Constraints

- The companion write is atomic; partial bundle bytes must never validate.
- The bundle and receipt stay inside the repo-owned lesson-session artifact
  boundary and use a path derived from the already validated `session_id`.
- Missing, unreadable, changed, or size-mismatched sessions are refused and
  never permit lesson scoring.
- A ledger event or complete bundle left orphaned by a later stdout/receipt
  failure is invalid without the final receipt. It is not rolled back or
  auto-deleted in this slice and can never enable scoring.
- Source and checked-in plugin mirrors remain synchronized.
- Because this changes a proof surface's presentation verdict, implementation
  closeout owes the repo's bounded two-round rule when round 1 causes repairs.

## Success Criteria

- Opening a new lesson session writes a Markdown bundle byte-identical to the
  rendered stdout and returns/names its path.
- The new receipt validates only when bundle hash and byte count match; missing,
  changed, truncated, or wrong-path bundles fail conservatively.
- After simulated context loss, retro recovers the explicit session ID and
  bundle path from the affected work's durable artifact, loads the frozen lesson
  list, and avoids a false `presentation-unproven` without host log access.
- The checked-in #614 receipt validates against its newly checked-in exact
  bundle; no historical receipt conversion capability is shipped.
- No host-log parser, transcript artifact, global active-session pointer, or
  historical score event is added.

## Acceptance Checks

- Verification type: unit — `open_lesson_session` writes exact Markdown bytes,
  exposes the deterministic path, and leaves no validating partial artifact on
  file-write or stdout failure.
- Verification type: unit — receipt validation covers current exact match,
  missing bundle, content mutation, byte-count mismatch, and path escape.
- Verification type: integration — open a synthetic session, record its ID/path
  citation in the affected work artifact, discard command/chat context, then
  recover that citation and prove retro receives the same ordered IDs and lesson
  text from the bundle.
- Verification type: unit — bundle-write, stdout/flush, and receipt-replace
  failures never leave a validating receipt; any earlier ledger event or atomic
  bundle remains a non-validating orphan, and no partial temporary bundle remains.
- Verification type: integration — the valid current bundle permits lesson
  effect evaluation, while missing/changed bundles are refused.
- Verification type: specdown — verify source/export parity and assert the diff
  adds no Codex-session reader, transcript store, active `latest` pointer, or
  historical score event.

## Boundary Ownership

`open_lesson_session.py` owns producing one byte sequence and writing it to both
the durable bundle and stdout. The lesson evaluation continuity library owns
receipt-to-bundle integrity and strict schema acceptance. The retro workflow owns
loading the explicit session bundle before authoring its disposition; host-log
audit code owns only historical incident diagnosis.

## Critique

- Interrupt Source: lesson-presentation-compaction-2026-08-14
- Seam Summary: lesson-session rendered output to repo-owned retro verdict
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the user corrected the owning boundary from host-log
  lookup to durable lesson-session content, then rejected compatibility and
  migration branches. Bounded review accepted the producer-owned bundle; the
  implementation now carries one strict current contract.
- What Disproving Observation Is Resolved: the #614 selected output reconstructs
  to 3,122 bytes whose SHA-256 exactly matches the existing receipt, proving the
  lesson-session owner already possessed the content that should have been
  frozen.
- Contract critique: two producer/first-use angles and a separate counterweight
  accepted the bundle owner, rejected host-log lookup and v1 runtime
  compatibility, and required only an exact derived path, durable work citation,
  and fail-closed orphan semantics before implementation.

## Canonical Artifact

This file is the living implementation contract for #617. The debug artifact
owns the historical evidence; implementation tests will own future behavior.

## First Implementation Slice

Write the rendered preview bytes once to the deterministic Markdown companion,
emit those same bytes, require the file for every accepted receipt, and teach
retro to load the bundle by explicit session ID. Add only the tests
named above, synchronize mirrors, and stop.
