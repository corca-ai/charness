# Release local-failure recovery critique
Date: 2026-07-18

## Execution

- Two independent angle reviewers and a separate counterweight reviewer inspected the release state machine read-only in the shared worktree.
- The correctness reviewer repeated its pass after each repair; the final pass returned `SHIP-READY`.
- Parent fingerprints verified no worktree, index, or HEAD drift around the final review.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

- `charness-artifacts/critique/2026-07-18-115559-packet.md`

## Decision Under Review

Make a failed local release attempt either restore the clean starting commit or leave an explicitly resumable post-commit state, without broadening the helper into a generic transaction framework.

## Capability at Stake

An operator must be able to retry a reversible release failure without manually reconstructing which version, generated, artifact, staged, renamed, or newly created paths the helper changed.

## Failure Angles

- Git semantics: staged renames, untracked paths, partial restore, and partial quarantine must not be reported as fully recovered.
- State-machine ownership: failures before and after the release commit need distinct transitions; rollback must never rewrite a commit that already exists.
- Operator evidence: non-`SystemExit` failures must still return structured recovery evidence.
- Publish boundary: a missing local tag after a successful local commit must be resumable only while remote tag and public release are absent.

## Counterweight Pass

- Act before ship: use `--no-renames` for HEAD-backed restoration; include preparation and artifact commit in the rollback boundary; report only completed restore/quarantine work; expose recovery on every caught failure; resume an exact untagged release commit after remote/public absence checks. All were fixed and re-reviewed.
- Bundle anyway: add an explicit assertion that pre-commit failure never reaches release creation; done.
- Act before ship: add a direct integration test for an ambiguous remote-tag state on the missing-local-tag branch. It exposed that general plan construction ran before resume validation and could change tag evidence; resume now freezes that state first.
- Over-worry: sweeping ignored files or building a repo-wide transaction framework would widen ownership without observed evidence. The helper deliberately owns only tracked and non-ignored paths created by its release attempt.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: publish_release_rollback.py | action: fix | note: rename-aware diff output could restore only the destination; `--no-renames` now enumerates both HEAD path identities and the integration test proves the old path returns.
- F2 | bin: act-before-ship | evidence: strong | ref: publish_release_execute.py | action: fix | note: rollback originally covered preparation but not later local artifact/commit failure; one owner now encloses the complete pre-commit mutation phase.
- F3 | bin: act-before-ship | evidence: strong | ref: test_release_publish_rollback.py | action: fix | note: restore and quarantine reports now contain completed operations only; injected later failures prove partial evidence remains truthful.
- F4 | bin: act-before-ship | evidence: strong | ref: publish_release_resume.py | action: fix | note: a release commit created before local tag failure was stranded; resume now revalidates and tags the exact saved commit only when remote tag and public release are absent.
- F5 | bin: act-before-ship | evidence: strong | ref: test_release_publish_resilience.py | action: fix | note: resume preflight now rejects a missing local tag plus remote publication evidence before plan construction can fetch or reinterpret that tag; dry-run and execute carry the same frozen state.
- F6 | bin: over-worry | evidence: moderate | ref: publication-boundary.md | action: defer | note: ignored-file sweeping and a generic transaction abstraction exceed the release helper's known mutation set and would weaken the boundary.

## Deliberately Not Doing

- No version bump, tag, push, or release publish; the operator explicitly excluded push and release.
- No Cautilus evaluation; the Git transitions and payloads are deterministically observable.
- No new blocking gate; focused state-machine tests exercise the owning helper.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested spawn fields; provider-side application metadata was not exposed.

## Boundary Ownership

- Producer: release preparation and rollback helpers produce local state transitions and structured recovery evidence.
- Consumer: the failed-release operator and `--resume --publish-current` path consume that evidence and state.
- Owning surface: public release skill source plus exact plugin mirror.
- Verdict: owned-correctly

## Verdict

SHIP-READY for local commit. Keep push and release out of this slice.
