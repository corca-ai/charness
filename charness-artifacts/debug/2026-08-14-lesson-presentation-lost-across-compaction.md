# Lesson Presentation Lost Across Compaction Debug
Date: 2026-08-14

## Problem

The #614 retro recorded `presentation-unproven` although the assistant had
presented the exact selected lesson list before work. The continuity check
accepted the false disposition.

## Correct Behavior

Opening a lesson session freezes the exact human-readable selected lessons in a
session-specific file. Work and retro refer to that file by explicit session ID,
so compaction cannot erase the lesson context or force host-transcript recovery.

## Observed Facts

- The session receipt was emitted at `2026-08-13T11:43:58.931747Z` for
  `2026-08-13-issue-614` and snapshot `4e1234f5...`.
- The full Codex rollout contains the exact ten-lesson assistant presentation at
  `11:44:04.923Z`; the user independently confirmed seeing it.
- The first of five compactions followed at `12:06:33.015Z`. Retro later called
  presentation uncertain and persisted `presentation-unproven`; continuity was
  green.
- `open_lesson_session.py` retains selected IDs in the ledger and only a digest
  and byte count of its rendered stdout in the receipt. It does not retain the
  exact rendered lesson text as a readable session artifact.
- Reconstructing the #614 output from its ordered IDs and current selection index
  yields 3,122 bytes and SHA-256
  `6b464865a125c87ec81a14121d66d602f09f08c87de1e3b33c2178af97a26c6c`,
  exactly matching the existing receipt. This proves what was lost from the
  durable session surface; future correctness must not rely on later
  reconstruction from mutable sources.

## Reproduction

- Read lesson session `2026-08-13-issue-614`: its snapshot stores ten ordered
  IDs but no lesson text.
- Read its receipt: it stores `stdout_sha256` and `stdout_byte_count` but no
  readable content path.
- Discard active command/chat output, as compaction did: no repo-owned file can
  supply the exact opened lesson bundle.
- Run `check_lesson_evaluation_continuity.py`: it accepts the retro-authored
  `presentation-unproven` because the session content is not an input.

## Candidate Causes

- The list was never presented: disconfirmed by user readback and the rollout.
- Compaction destroyed all evidence: disconfirmed; the rollout retained forensic
  evidence and the receipt retained its hash.
- Retro needed a transcript parser: rejected as the future owner; the lesson
  command already possessed the exact bytes before compaction.
- The lesson-session boundary persisted identity/integrity but not readable
  content: confirmed by the ledger, receipt, and exact reconstruction.

## Hypothesis

- If readable session content is the missing boundary, the current ledger and
  receipt will identify and hash the selected output while providing no file an
  agent can reread. Confirmed.
- disconfirmer: locate a repo-owned, session-specific file containing the exact
  #614 rendered lessons and bound by its receipt; no such file exists.

## Verification

- Confirmed timeline: session open -> assistant presentation -> compaction ->
  false retro disposition.
- Confirmed storage shape: ordered IDs plus output hash/size, no exact content.
- Confirmed reconstruction matches the receipt byte-for-byte.
- Issue [#617](https://github.com/corca-ai/charness/issues/617) was corrected to
  durable lesson-session bundle ownership and read back byte-identically.

## Root Cause

The workflow made active conversation presentation the durable lesson-content
surface while its repo-owned session artifacts preserved only IDs and an output
digest. That split was invisible until compaction: the integrity metadata
survived, but the content an agent needed to reread did not. Continuity then
validated the authored disposition instead of exposing the missing content.

## Invariant Proof

- Invariant: a declared lesson session used for later evaluation must retain the
  exact human-readable lessons independently of active model context.
- Producer Proof: `open_lesson_session.py` creates the exact bytes once and the
  receipt already hashes them.
- Final-Consumer Proof: retro could see the declaration/receipt but not reread
  those bytes, and rendered the false non-proof.
- Interface-Shape Sibling Scan: ledger snapshot, emission receipt, stdout
  renderer, retro disposition, and host-log forensic path were inspected.
- Non-Claims: a saved bundle proves issued content, not human readback, agent
  use, or lesson effect.

## Detection Gap

- `open_lesson_session.py` | hashes rendered stdout but does not retain the
  readable bytes | write a receipt-bound Markdown companion.
- `skills/public/retro/references/lesson-evaluation.md` | makes conversation
  presentation authoritative and offers no compaction recovery path | load the
  explicit session bundle and keep use/effect as separate judgments.
- `check_lesson_evaluation_continuity.py` | validates receipt/disposition
  consistency without exact session content | validate new bundle integrity
  while preserving legacy receipt non-claims.

## Sibling Search

- same layer: lesson ledger snapshot and emission receipt | decision: same bug,
  fix under #617 | proof: IDs/hash survive but readable content does not.
- abstraction up: arbitrary conversation memory | decision: over-worry | proof:
  no second reported consumer; generic transcript storage is out of scope.
- specialization down: Codex rollout lookup | decision: diagnostic-only | proof:
  it reconstructed this incident but is the wrong future owner.
- cross-file: public retro lesson evaluation, continuity library, source/plugin
  mirrors, and focused tests.

## Seam Risk

- Interrupt ID: lesson-presentation-compaction-2026-08-14
- Risk Class: host-disproves-local
- Seam: lesson-session rendered output to repo-owned retro verdict
- Disproving Observation: the user and host rollout contradicted the accepted
  `presentation-unproven` disposition.
- What Local Reasoning Cannot Prove: whether the exact session output survived
  outside active context; current repo artifacts prove only its hash.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-14-issue-617-durable-lesson-session-bundle.md

Resolved 2026-08-15 (S3). The prevention below is built and consumed:
`lesson_evaluation_continuity_lib.bundle_path`/`write_bundle` landed in
`311844e23`, `open_lesson_session.py` writes the bundle before emitting the same
bytes, and `lesson_evaluation_records_lib.py` reads it back through
`load_session_bundle`. All eight checked-in receipts re-digest to their bundles,
including the original `2026-08-13-issue-614` at 3,122 bytes. The spec
handoff carries the resolution forward; this pointer stops hijacking a fresh bug.

## Prevention

Persist the rendered lesson preview once, beside the existing receipt, and make
the command output and readable bundle byte-identical. Require explicit session
ID lookup after compaction and at retro. Keep host logs forensic-only, carry one
current receipt contract rather than a legacy-compatibility branch (the spec
overturned the compatibility line this section originally carried), and add no
generic conversation store.
