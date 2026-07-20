# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.3.0 plugin.

## Current State

- v2.3.0 is published and installed-host readback is recorded (distinct-channel
  release-URL fetch + `charness update`/`version`/`doctor`). It makes
  measurement-contract file discovery adapter-owned: a consumer repo declares
  its real test surface via `test_file_discovery` (fixing the `.mjs` undercount,
  issue #447) and its non-default linter directive syntax via
  `lint_ignore_discovery`, instead of the portable body re-deriving and diverging.
- New advisory inventory `inventory_hardcoded_discovery` is a tripwire for that
  class: it flags portable constants hardcoding a polyglot (2+ code-family)
  discovery list unless adapter-owned or marked `# discovery-boundary:`. The broad
  lexical version was noise (71 sites); narrow polyglot-only reads 0 unmarked.
- Deferred discovery follow-ups (recorded, not blocking): inline
  `.rglob`/`ls-files` pathspec discovery, `CODE_LANGUAGE_FAMILIES` expansion, and
  a zero/near-zero test-surface advisory.
- Durable prior context (all closed, do not reopen without regression evidence):
  the Gajae goal, dead-code dynamic-entrypoint review, standing-xdist speedups,
  and quality's portable proof-path method (define the current consumer envelope
  before boundary replacement; prove requires representative input consumption).
- OPEN SMELL — flaky/nondeterministic suite under parallel load. `run-quality.sh
  --release` once emitted 12 failed + 1321 errors in
  `tests/charness_cli/{test_worktree_doctor,test_yaml_output_branch_coverage}.py`,
  and `test_failure_record_retention_removes_oldest_record` flakes under xdist —
  all pass clean in isolation and on retry. Lead: shared state across parallel
  workers/worktrees — `publish_release_runtime.persist_failure_payload` writes to
  the git COMMON dir (`charness-release-failures`), and worktree tests make real
  worktrees off one repo.

## Next Session

1. Recommended next slice (no explicit task): fix the OPEN SMELL above — isolate
   per-worker/per-worktree shared state so the suite is deterministic under
   parallel/`--release` load, and improve test quality and runtime. Otherwise run
   the workflow trigger and choose the smallest coherent backlog slice.
2. For clean-start mutating workflows, enumerate owned mutations before coding
   and make every failure either restore the start state or emit a typed,
   resumable state. For irreversible operations, prove the exact consumed range.
   The checklist is in [recent lessons](../charness-artifacts/retro/recent-lessons.md).
3. Keep D18 ignored unless the operator explicitly reopens it.
4. For mutation-pool changes, ask the selector before widening a producer by
   hand: direct reference, nearest recognized loader ancestor, then broad
   fallback; keep its canonical parallel-runner command.
5. When adding a new dynamic-call syntax, add wrong-path, wrong-loader,
   wrong-receiver, and disconnected-control-flow fixtures before recognizing it.
   Finish critique packets before taking reviewer boundary fingerprints, and run
   the focused duplication ratchet before broad validation for large AST helpers.
6. Treat the v2.3.0 release and adapter-owned-discovery work as closed; the
   deferred discovery follow-ups are candidates, not commitments.

## Discuss

- Decide an additive migration for issue closeout's terminal-sounding
  `verified` state; do not silently redefine existing artifacts.
- Persist pre-commit rollback outcomes and strengthen post-publication proof
  with an explicitly different observer identity, not only a different channel.

## References

- [release state](../charness-artifacts/release/latest.md)
- [portable proof/release critique](../charness-artifacts/critique/2026-07-19-portable-proof-path-and-release-identity-critique.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
