# lesson score authoring proof critique
Date: 2026-08-12

## Decision Under Review

Add one locally serialized command that appends a retro-cited score to the
replayed lesson ledger without creating selection, shown-set, or graduation state.

## Diff Scope

The score authoring CLI, the ledger's pure in-memory validator seam, focused
tests, source/plugin mirrors, and the ledger surface inventory changed together.

## Failure Angles

- Cooperative writer contention could discard an uncommitted score unless the
  lock spans read through replace.
- A CLI-only blank-input check would leave direct JSON edits able to evade the
  ledger's declared event identity contract.
- A durable lock in the worktree would leave ordinary consumer worktrees dirty.

## Counterweight Pass

- The validator's shared replay path, exact source citation, and committed-prefix
  checks remain the sole score-state authority; no presentation inference belongs
  in this command.
- Crash-durability fsync and timing-sensitive contention tests are useful later
  but do not alter the bounded local atomic-replace claim.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/lesson_ledger_lib.py | action: fix | note: Persisted score events now reject whitespace-only identity, source, lesson, and anchor values rather than relying only on CLI normalization.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/record_lesson_score.py | action: fix | note: The stable lock moved to an OS-temporary path keyed by the ledger path, so ordinary writes do not pollute a repository worktree; temporary serialization files are removed after failure.
- F3 | bin: bundle-anyway | evidence: moderate | ref: .agents/surfaces.json | action: document | note: The dedicated ledger/register surface now names the authoring command and its exported mirror.
- F4 | bin: over-worry | evidence: moderate | ref: charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md | action: defer | note: Do not add shown-set, presentation, selection, archive, or score-budget behavior to a cited-retro authoring seam.
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/record_lesson_score.py | action: defer | note: Cross-process timing proof and crash-durability fsync are deferred; the tested lock protocol and atomic replacement make no stronger durability claim.

## Defect Class Cross-Link

- `charness-artifacts/retro/recent-lessons.md` Repeat Traps: proof-surface validators must enforce the same semantic contract on both direct state and convenient authoring paths.

## Reviewer Tier Evidence

- Requested tier: n/a (host inherited the parent session model).
- Requested spawn fields: task name and read-only bounded review scope sent through the host agent interface.
- Host exposure state: metadata-hidden
- Application state: the host returned no applied reviewer-tier metadata.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-014829-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-014829-packet.json
- Packet SHA256: b0492bf951e044bf442ba188d180ab6e38de51c642e7660e203cc09e04a355f3
- Identity SHA256: 643b73c80f36d680a3b8cb2490a0ee1af7dc83cfbc130894513227f051ae150f

## Boundary Ownership

- Producer: `record_lesson_score.py` creates one candidate score event; `lesson_ledger_lib.py` replays and judges it.
- Consumer: `check_lesson_ledger.py` and later selection preview read the validated materialized ledger.
- Owning surface: lesson-ledger-and-contract-register.
- Verdict: owned-correctly

## Pre-Merge Action

- Applied F1 and F2, synchronized the exported plugin mirror, and pinned their regression tests before broad validation.
