# Issue 617 Durable Lesson Session Bundle

Status: released
Date: 2026-08-14
Refreshed: 2026-08-20 (release-train Slice 0) — interrupt carry-forward remains
explicit and the contract below is unchanged; no #617 decision was reopened.
Source: https://github.com/corca-ai/charness/issues/617

## Delivery Status

Built and consumed on the current tree. Measured 2026-08-15, not transcribed:

- `lesson_evaluation_continuity_lib.bundle_path` and `write_bundle` landed in
  `311844e23` (`git log -S "def bundle_path"`), an ancestor of `eae80f660`. The
  release-scope contract cites `eae80f660` for this capability; that commit
  contains it but is not where it shipped, and this line is the accurate one.
- `open_lesson_session.py:33-34,53` writes the bundle and names its path;
  `lesson_evaluation_records_lib.py:325` is the production consumer that reads it
  back through `load_session_bundle`, inside `_bundle_lesson_texts`.
- ALL EIGHT receipts on disk re-digest to their bundles exactly, each matching
  its own `stdout_sha256` and `stdout_byte_count` (re-digested with `hashlib`, not
  read off the field). Seven are committed at HEAD; the eighth,
  `2026-08-15-s3`, is this slice's own and still untracked — round 2 caught the
  earlier "checked-in" doing work it had not earned: `2026-08-13-issue-614` (3,122
  bytes), `2026-08-14-closeout-618-628` (2,260), `2026-08-14-json-removal`
  (2,260), `2026-08-14-lesson-loop-625-627-626` (2,396),
  `2026-08-15-release-design` (2,594), `2026-08-15-s1-release-tooling` (3,321),
  `2026-08-15-s2` (3,145), `2026-08-15-s3` (3,145). An earlier draft cited "both
  checked-in receipts" and named two of the eight; a bounded reviewer caught a
  sample presented as the population, in the artifact whose whole point is that
  the bundle set is complete. `collect_receipts` validates every `.json` in that
  directory, so the other six are load-bearing, not context.
- `tests/test_lesson_session_emission.py`,
  `tests/test_lesson_evaluation_continuity.py`, and
  `tests/test_lesson_evaluation_contract_boundaries.py` pass — 80 tests.
- `skills/public/retro/references/lesson-evaluation.md:10-13` binds retro to the
  explicit-session-ID lookup and refuses the newest-file guess.

Released, and the evidence is named so a later reader re-runs it rather than
trusting this line: `git log -S "def bundle_path" -- scripts/lesson_evaluation_continuity_lib.py`
resolves to `311844e23`, `git tag --contains 311844e23` lists `v6.0.0`,
`git show v6.0.0:plugins/charness/scripts/lesson_evaluation_continuity_lib.py`
carries `bundle_path` (so the CONSUMER copy has it, not only `scripts/`), and
`gh release view v6.0.0` reports it published `2026-08-16T06:07:24Z`, not a draft.
This line previously read `delivered-unreleased` with "it still reproduces for
its reporter until S7 publishes"; S7 published, and the status was never
refreshed — a bounded reviewer caught it during the #617 closeout, where a stale
status on the issue's own living contract would have contradicted the closure.

Not claimed: nothing here proves human readback, agent use, or lesson effect —
the bundle proves only which lessons the session-start action issued, which is
the non-claim the contract fixed below.

Also not claimed: a consumer repo that opened lesson sessions on a PRE-bundle
charness now gets `invalid-receipt` for each old receipt, permanently. That is
the deliberate consequence of the one-contract rule below, not an unrequested
regression, and it is stated here rather than left for a consumer to discover.

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
  frozen. **Resolved by delivery, not by argument (2026-08-15):** the host no
  longer disproves the local record, because the local record now holds the
  bytes — a checked-in bundle written by the current code path, re-digested
  against its receipt, and read back by a production consumer. The debug
  artifact's `Resolution` is `resolved` as of this refresh.
- Interrupt Carry-Forward: the `host-disproves-local` risk class is FORCED and
  therefore never stops being required; what changes is that the disproving
  observation is discharged. The residual is the standing one this contract
  already states: a bundle proves issued content only. If a future session again
  finds the host contradicting a `presentation-unproven` disposition, that is a
  NEW interrupt, not this one reopening.
- Contract critique: two producer/first-use angles and a separate counterweight
  accepted the bundle owner, rejected host-log lookup and v1 runtime
  compatibility, and required only an exact derived path, durable work citation,
  and fail-closed orphan semantics before implementation.
- Current-slice carry-forward: this resolved handoff is refreshed for the
  release-train investigation that also crosses installed-versus-repo-owned
  seams. That is a new issue contract, not a reopening of #617; the current
  slice must keep its own producer, consumer, and host non-claims explicit.

## Canonical Artifact

This file is the living implementation contract for #617. The debug artifact
owns the historical evidence; implementation tests will own future behavior.

## First Implementation Slice

Write the rendered preview bytes once to the deterministic Markdown companion,
emit those same bytes, require the file for every accepted receipt, and teach
retro to load the bundle by explicit session ID. Add only the tests
named above, synchronize mirrors, and stop.
