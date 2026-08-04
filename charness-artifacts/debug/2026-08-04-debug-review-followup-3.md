# Retro Persistence Goal Binding Debug
Date: 2026-08-04

## Problem

An achieve closeout can persist a valid-looking session retro without passing
the owning goal identity to the write boundary, so the final goal validator may
reject the evidence only after artifact and summary state have changed.

## Correct Behavior

Given an opt-in owning goal path, persistence must require exactly one matching
`Goal:` metadata field before it writes any retro, summary, lesson index, event,
or newly-created output directory. Given no goal path, ordinary session retro
persistence must retain its current behavior.

## Observed Facts

- Issue #504 identifies `skills/public/retro/scripts/persist_retro_artifact.py`
  and `scripts/retro_persistence_lib.py` as the persistence boundary.
- Before this repair, the library wrote the retro before emitting t-events or
  refreshing the summary/index; the pre-fix API accepted only artifact name and
  markdown text.
- Before this repair, the achieve closeout consumer derived goal tokens and
  bound cited evidence later, while the release caller invoked the same library
  directly without a goal. Making the input universally required would have
  broken session/release mode.
- Source and `plugins/charness` copies are synchronized surfaces.

## Reproduction

- Minimal pre-fix reproduction: invoke the persistence CLI with a markdown body
  whose `Goal:` names a different goal and an output directory containing no
  prior artifacts. The current boundary has no goal argument and writes before
  any goal identity comparison; the later closeout binding gate rejects the
  resulting artifact.

## Candidate Causes

- Boundary cause: goal identity is checked only by the later achieve evidence
  consumer, after persistence has already mutated state.
- API cause: the shared library has no optional goal-aware mode, so callers
  cannot request identity validation without changing legacy callers.
- Grammar cause: loose body-token matching could accept incidental prose or
  multiple/malformed `Goal:` fields instead of one exact metadata field.

## Hypothesis

- If validation is added at the library boundary before `_write_text`, then a
  matching exact `Goal:` field succeeds, while missing/malformed/different
  identity returns before creating or changing any target state; the omitted
  goal argument continues to take the legacy path. Disconfirmer: inspect and
  test every write path, then compare a complete filesystem/event snapshot for
  mismatch and legacy cases.

## Verification

- confirmed and repaired — 112 focused tests pass, including direct-library and
  CLI matching/mismatch/legacy cases; the mismatch fixtures compare the complete
  output and enabled event trees byte-for-byte before and after refusal. Relative
  paths resolve from the repository root, the first H1 title is permitted while
  later ATX headings with 0-3-space indentation terminate exact metadata
  parsing, slug input is canonicalized to the repo-relative path, and
  source/plugin parity is clean, and a maintained achieve/retro caller-contract
  regression test proves the required opt-in instructions remain present. Two
  delegated repair-reads found and drove
  these heading/output-contract repairs; the final repair-read found no
  concrete blocker. The locked aggregate closeout and final goal-bound retro
  remain pending.

## Root Cause

The persistence API owns the first irreversible local writes but has no
goal-aware contract. Achieve can therefore validate only the artifact it later
reads, after the wrong-owner artifact and derived state may already exist.

## Invariant Proof

- Invariant: when the achieve producer emits an owning goal identity, the
  persistence boundary must refuse a non-matching retro before the artifact,
  summary/index, event, or output-directory consumer can claim success.
- Producer Proof: the repaired library/CLI signatures carry an optional goal
  path to the shared write boundary, where exact identity validation runs before
  artifact, event, summary, index, or output-directory writes.
- Final-Consumer Proof: `goal_artifact_closeout_evidence.py` preserves the
  final binding defense and now recognizes the numeric-only canonical goal
  filename token; focused tests cover the producer and final-consumer seams.
- Interface-Shape Sibling Scan: shared library, retro CLI, release caller, and
  achieve closeout parser were inspected as producer/transport/final-consumer
  siblings; the library is the shared write owner.
- Non-Claims: no provider/live/release proof or arbitrary dynamic caller is
  claimed; host-installed behavior and remote issue state remain unverified.

## Detection Gap

- Existing achieve evidence binding | catches the wrong owner only after
  persistence | pass the goal identity into the write boundary and add direct
  library/CLI no-write tests.

## Sibling Search

- Mental model: a late final-consumer identity check is mistaken for a
  producer-boundary write guard.
- same interface shape: release-trigger persistence omits a goal by design |
  decision: preserve it as legacy mode while adding explicit goal-aware input |
  proof: caller inventory plus compatibility test.
- abstraction up: achieve closeout evidence binding | decision: keep final
  binding as defense-in-depth, not the first write guard | proof: consumer read.
- cross-file: `plugins/charness/scripts/retro_persistence_lib.py` and mirrored
  CLI | decision: synchronize both exported surfaces | proof: parity gate.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: local persistence helper to generated plugin and t-events adapter
- Disproving Observation: none yet
- What Local Reasoning Cannot Prove: host-installed plugin behavior beyond the
  checked-in source/export parity and local subprocess tests
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this dated debug record

## Prevention

Keep identity validation at the shared write boundary, use an exact metadata
field grammar, snapshot all derived outputs in mismatch tests, and preserve the
omitted-goal legacy path. If another persistence caller needs goal binding,
route it through the same API rather than duplicating a late token check.
