# Test Isolation Critique
Date: 2026-07-18

## Decision Under Review

Extend the existing repo-copy invariant into a finite AST ratchet for direct
pathlib writes derived from the real checkout, isolate the remaining offending
test, and add process-level seed-cache contract tests.

Packet Consumed: `charness-artifacts/critique/2026-07-18-055909-packet.md`.

## Failure Angles

- Problem framing: the first draft claimed categorical checkout immutability
  while only recognizing a few method spellings.
- Implementation integrity: class methods, `Path(ROOT)`, write-mode
  `Path.open`, and false taint from `ROOT = Path('/tmp')` escaped the first
  detector draft.
- Operational cost: a full static sandbox or copy-heavy fixture would weaken
  the standing fast path and create a misleading guarantee.

## Counterweight Pass

- Act before ship: recognize real-root provenance, class test methods,
  `Path(ROOT)`, and write-mode `Path.open`; add positive and negative fixtures.
- Bundle anyway: synchronize the checked-in plugin export after source edits.
- Over-worry: do not interpret arbitrary `os`, `shutil`, shell, third-party, or
  subprocess behavior as if an AST ratchet were a process sandbox.
- Valid but defer: failed-builder seed-cache recovery is useful extra proof but
  is not required to close the reproduced shared-checkout mutation class.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_test_repo_copy_invariants.py | action: fix | note: recurse into class test methods and preserve function-scoped diagnostics
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_test_repo_copy_invariants.py | action: fix | note: recognize Path(ROOT), write-mode Path.open, imported root aliases, and real __file__ provenance
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_repo_copy_invariants.py | action: fix | note: accept a non-checkout variable named ROOT so the blocking gate stays low-noise
- F4 | bin: bundle-anyway | evidence: strong | ref: plugins/charness | action: fix | note: run the owning source-to-plugin sync before validation
- F5 | bin: over-worry | evidence: moderate | ref: n/a | action: document | note: arbitrary subprocess and library mutation modeling is outside this finite direct-Path ratchet
- F6 | bin: valid-but-defer | evidence: moderate | ref: tests/seed_cache.py | action: defer | note: failed-builder recovery can be added when a failure or recurrence makes it the next proof boundary

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: metadata-hidden
- Application state: requested fields were sent; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — two distinct angle reviewers and one separate counterweight
completed read-only reviews; each parent fingerprint verification reported no
worktree, index, or HEAD drift.

## Boundary Ownership

- Producer: standing test authors create filesystem setup and mutation calls.
- Consumer: parallel standing pytest and snapshot-based repo commands observe checkout state.
- Owning surface: existing repo-copy/test-isolation invariant plus the portable quality testability reference.
- Verdict: owned-correctly

## Deliberately Not Doing

- No new standalone gate, subprocess tracer, or full Python side-effect model.
- No copy-heavy repo fixture in standing pytest.

## Next Move

Land the finite detector, focused concurrency/recovery proof, portable doctrine,
generated plugin mirror, and full locked closeout as one slice.
