# Debug Review
Date: 2026-07-20

## Problem

`test_failure_record_retention_removes_oldest_record` flakes under xdist/`--release`
load: it passes in isolation and on retry but intermittently fails asserting that
the oldest release-failure record (`v0-*`) was evicted. Capability at risk: the
release helper's promise to retain the N most-recent failure records and drop the
oldest.

## Correct Behavior

Given `FAILURE_RECORD_RETENTION + 1` records written oldest→newest, when
`persist_failure_payload` prunes, then it keeps exactly the newest N and removes
the single oldest by true creation order — deterministically, on any filesystem.

## Observed Facts

- `persist_failure_payload` (skills/public/release/scripts/publish_release_runtime.py)
  pruned via `sorted(record_dir.glob("*.yaml"), key=st_mtime_ns, reverse=True)`
  then unlinked `records[FAILURE_RECORD_RETENTION:]`.
- The pytest temp root (`~/.cache/charness/pytest-tmp/...`) reports filesystem
  `ext2/ext3` with 1-second mtime granularity.
- Direct probe: a 21-file burst yields 1–2 distinct `st_mtime_ns` values / 21; the
  mtime-sorted eviction removed a non-`v0` record in 19/20 trials.
- Real test, isolated, 8 repeats: 2 failed / 6 passed (naturally flaky).
- Assertion that failed: `assert not any(path.name.startswith("v0-") ...)` → v0 survived.

## Reproduction

- `for i in $(seq 1 8); do python3 -m pytest
  tests/quality_gates/test_release_failure_record.py::test_failure_record_retention_removes_oldest_record
  -q -p no:randomly; done` → intermittent failures (2/8) on a 1s-granularity temp FS.

## Candidate Causes

- Filesystem mtime granularity: same-second writes share `st_mtime_ns`, so the
  eviction sort key ties across the burst (control-flow/env). ✅ confirmed.
- Cross-worker shared state (git common dir `charness-release-failures`, real
  worktrees off one repo). ❌ tests use isolated `tmp_path` repos; no site writes
  to the real repo common dir.
- `time.time_ns()` filename collisions. ❌ O_EXCL makes stamps unique; not the tie.

## Hypothesis

- Falsifiable claim: eviction order depends on `st_mtime_ns`, which ties on
  coarse-granularity filesystems, so among tied records the evicted one is
  readdir-order arbitrary rather than the oldest. | disconfirmer: probe whether a
  21-file burst produces <21 distinct `st_mtime_ns` and mis-evicts.

## Verification

- result: confirmed — the burst probe showed 1–2 distinct mtimes/21 and wrong
  eviction in 19/20 trials; an adversarial-mtime test (oldest record given the
  newest mtime) evicts `v20` on the old code and `v0` on the fixed code.

## Root Cause

`persist_failure_payload` used filesystem `st_mtime_ns` as the record ordering key
for retention. mtime is a lossy proxy for creation order: coarse-granularity
filesystems (ext2/ext3, ext4 with 128-byte inodes) collapse same-second writes to
one identical value, so the sort ties and eviction removes a readdir-order-arbitrary
record. Fix: order by the monotonic `time.time_ns()` stamp embedded in each
filename (`-(\d+)\.yaml$`), with mtime fallback for foreign files and a `path.name`
tiebreak for full determinism.

## Invariant Proof

- Invariant: n/a - not a workflow-boundary propagation bug
- Producer Proof: n/a
- Final-Consumer Proof: n/a
- Interface-Shape Sibling Scan: n/a
- Non-Claims: the one-time `--release` "12 failed + 1321 errors" is a SEPARATE bug
  from this retention flake. It was initially not reproduced from the two named files
  alone (30 passed x 3 at `-n 16`), but under the FULL `--release` suite it reproduced
  (11 failed, 1439 errors) and was root-caused + fixed as a pytest temp-tree deletion
  race — NOT the seed-cache contention first guessed here. See
  `charness-artifacts/debug/2026-07-20-standing-pytest-basetemp-deletion-race.md`.

## Detection Gap

- surface: standing pytest gate | what did not fire: the test encoded the invariant
  but only reproduced the defect on a coarse-mtime FS and only intermittently, so a
  nanosecond-granularity CI could stay green over the bug | smallest change to fire
  it: an adversarial-mtime regression test that stamps mtime opposite to creation
  order (added) — deterministically red on the old code, green on the fixed code.

## Sibling Search

- Mental model: "filesystem mtime is a reliable, high-resolution ordering/creation
  key." False on coarse-granularity filesystems.
- eviction/retention axis: publish_release_runtime.persist_failure_payload | decision:
  fix (correctness invariant) | proof: reproduced + adversarial test.
- most-recent-selection axis: codex_session_jsonl_audit.py:38, host_log_probe_lib.py
  {36,40,193}, capability_catalog_resolver.py:19 (mtime as secondary key) | decision:
  low-impact pick-one-of-equally-recent, out of scope | proof: read-only, `follow-up:mtime-recency-tiebreak`.
- cross-file: recent_lessons_lib.py:45 and debug/plan_debug_run.py:157 ALREADY use a
  `(mtime, …, name)` deterministic tiebreak — the repo convention existed and release
  retention simply missed it.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: none
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Retention/eviction ordering must key on an intrinsic monotonic creation stamp (the
embedded `time.time_ns()`), never on filesystem mtime, whose granularity is
filesystem-dependent. Regression tests for ordering must make mtime adversarial to
creation order so they are deterministic regardless of the host filesystem.
Follow-up `follow-up:mtime-recency-tiebreak`: audit the low-impact `max(key=st_mtime)`
recency selectors if same-second ties ever matter. Follow-up
`follow-up:release-failure-unlink-missing-ok`: `stale_record.unlink()` lacks
`missing_ok=True`, so a concurrent same-file eviction (two release runs sharing one
git common dir) could flip the return to `failed` after the record actually
persisted — pre-existing, out of this slice's ordering scope.
