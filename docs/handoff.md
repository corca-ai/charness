# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- The release-failure retention flake is FIXED. `persist_failure_payload`
  ([publish_release_runtime.py](../skills/public/release/scripts/publish_release_runtime.py))
  evicted records by
  filesystem `st_mtime_ns`, which ties on coarse-granularity filesystems
  (ext2/ext3, ext4 with 128-byte inodes), so eviction dropped an arbitrary record
  under a same-second burst. It now orders by the embedded `time.time_ns()` stamp
  with an mtime fallback and a `path.name` tiebreak. A deterministic
  adversarial-mtime regression test pins it on any filesystem. RCA in References.
- The `--release` mass-error flake ("12 failed + 1321 errors") is FIXED. It was a
  pytest temp-tree deletion race, not resource contention: the standing runner's
  explicit `--basetemp` was named `pytest-<ns>` under a `pytest-of-<user>` rootdir
  shared with nested pytest runs (via inherited `PYTEST_DEBUG_TEMPROOT`), and pytest
  gives explicit basetemps no cleanup lock, so a nested run's exit-time
  `make_numbered_dir_with_cleanup` deleted it (and every live xdist worker dir)
  mid-run. `default_basetemp` now emits `charness-run-<ns>`, invisible to that
  `pytest-*` cleanup glob. Proof: 10/10 clean full `--release` runs (prior base rate
  ~1-in-3 failing) plus a deterministic regression test. RCA in References.
- Durable prior context (all closed, do not reopen without regression evidence):
  v2.3.0 release and adapter-owned measurement-contract discovery, the Gajae goal,
  dead-code dynamic-entrypoint review, standing-xdist speedups, and quality's
  portable proof-path method.

## Next Session

1. Recommended next slice (no explicit task): run the workflow trigger and choose
   the smallest coherent backlog slice. The deferred discovery follow-ups (inline
   `.rglob`/`ls-files` pathspec discovery, `CODE_LANGUAGE_FAMILIES` expansion,
   zero/near-zero test-surface advisory) are candidates, not commitments.
2. For clean-start mutating workflows, enumerate owned mutations before coding and
   make every failure either restore the start state or emit a typed, resumable
   state; for irreversible operations, prove the exact consumed range (see recent
   lessons in References).
3. Keep D18 ignored unless the operator explicitly reopens it.
4. For mutation-pool changes, ask the selector before widening a producer by hand:
   direct reference, nearest recognized loader ancestor, then broad fallback.
5. When adding a new dynamic-call syntax, add wrong-path, wrong-loader,
   wrong-receiver, and disconnected-control-flow fixtures before recognizing it.
6. Tracked follow-ups (candidates, not commitments): `follow-up:mtime-recency-tiebreak`,
   `follow-up:release-failure-unlink-missing-ok`, and reaping stale `charness-run-*`
   basetemps left by failed standing runs (the seed-budget gate already bounds them).

## Discuss

- Decide an additive migration for issue closeout's terminal-sounding `verified`
  state; do not silently redefine existing artifacts.
- Persist pre-commit rollback outcomes and strengthen post-publication proof with an
  explicitly different observer identity, not only a different channel.

## References

- [retention RCA](../charness-artifacts/debug/2026-07-20-debug-review.md)
- [basetemp deletion-race RCA](../charness-artifacts/debug/2026-07-20-standing-pytest-basetemp-deletion-race.md)
- [release state](../charness-artifacts/release/latest.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
