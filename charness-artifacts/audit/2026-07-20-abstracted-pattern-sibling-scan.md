# Abstracted-Pattern Sibling Scan — Flaky-Suite Root Causes
Date: 2026-07-20
Status: findings recorded for a future fix session (no code changed by this scan)

## Why this exists

After v2.3.1 fixed two flaky-suite root causes, a 5-Whys pass abstracted them into
two defect patterns, and three read-only subagents scanned the codebase for
siblings. This file records every finding (including low-severity) so a future
session can fix them without re-deriving the scan. The scan itself changed no code.

## The two abstract patterns

- **P1 — lossy ambient key.** Ordering / selecting ("newest/oldest wins") /
  deduping / freshness / identity keyed on an *ambient, environment-derived, lossy*
  attribute (filesystem `st_mtime`/`ctime`, wall-clock `time.time()`, readdir/glob
  order, `set`/`dict` iteration, `hash()`/`id()`) instead of an *intrinsic
  authoritative* key the data already carries. Collides / goes nondeterministic
  when the ambient attribute's resolution ties or its order is unspecified.
  Exemplar (fixed): retention evicted by `st_mtime_ns`, tied on a 1s-granularity FS.
- **P2 — shared-namespace contract violation.** Placing resources in a namespace a
  *different process/tool/worktree* owns or reaps, without that space's protection
  protocol (lock / `O_EXCL` / atomic `os.replace` / private per-run subpath) or by
  matching a naming convention an external reaper keys on; or concurrent-writer
  TOCTOU on a shared path. Exemplar (fixed): lock-less `pytest-*` basetemp deleted
  mid-run by nested pytest cleanup.

## Headline

No NEW correctness-critical sibling at the exemplars' severity exists. The codebase
is already well-defended (intrinsic name-embedded stamps for every real
deletion/rotation, `filelock`/`O_EXCL`/atomic `os.replace` where it matters,
per-worker `tmp_path`, #225 git-ceiling confine, content-addressed seed cache).
What remains are low-severity "odd-one-out" inconsistencies and latent/conditional
flakes.

## Tier 1 — FIXED 2026-07-27 (commit `092ab996`), retained for lineage

**Do not re-plan these as work.** All three landed with the audit's own rationale
written into the comments, `plugins/` mirrors synced, and regression tests:

- **A** — `scripts/record_quality_runtime.py` `rotate_archives` carries
  `oldest.unlink(missing_ok=True)`; proved by
  `tests/quality_gates/test_quality_runtime_recorder.py::test_rotate_archives_tolerates_concurrently_deleted_oldest`.
- **B** — `scripts/mutation_baseline_abort_lib.py` dropped the exists-then-unlink
  TOCTOU; proved by `tests/quality_gates/test_mutation_baseline_abort.py`
  (missing-marker unlink must not raise).
- **C** — `scripts/check_mutation_score.py` `_marker_is_stale` compares with `>`;
  proved by
  `tests/quality_gates/test_mutation_baseline_abort.py::test_marker_is_stale_false_on_mtime_tie_keeps_marker_authoritative`.

This block is stale-state history, kept because a 2026-07-27 goal run planned a
slice against it before checking the tree, and the line numbers below no longer
resolve. Verifying a named finding against the source before treating it as debt
is the standing rule; this heading exists so the next reader does not need it.

## Tier 1 as originally recorded (line numbers no longer resolve)

- **A. `scripts/record_quality_runtime.py:102-106` (P2).** `rotate_archives` does
  `sorted(glob(...))` then `oldest.unlink()` with NO `missing_ok`. Its two structural
  siblings already carry the guard (`scripts/t_events_emit_lib.py:89`,
  `skills/public/release/scripts/publish_release_runtime.py:144`). Failure: two
  concurrent recorders (two `run-quality.sh` in one worktree, or `run-quality.sh`
  racing `measure_startup_probes.py`) both `pop(0)` the same oldest path; the second
  `unlink()` raises `FileNotFoundError` → recorder exits nonzero. Fix:
  `oldest.unlink(missing_ok=True)`. (Mirror: `plugins/charness/scripts/record_quality_runtime.py`.)
- **B. `scripts/mutation_baseline_abort_lib.py:53-55` (P2).** `if marker_path.exists(): marker_path.unlink()`
  — exists-then-unlink TOCTOU, no `missing_ok`. Concurrent mutation runs (rare, CI
  serial) → `FileNotFoundError`. Fix: `marker_path.unlink(missing_ok=True)` and drop
  the `exists()` check.
- **C. `scripts/check_mutation_score.py:280` (P1).** `_marker_is_stale` returns
  `stats_path.stat().st_mtime >= marker_path.stat().st_mtime`. On a coarse-mtime FS a
  same-second tie resolves toward "marker is stale" → a persisted previous-run stats
  file masks a genuine current baseline abort (the unsafe direction). Fix: use `>`
  (a same-second tie keeps the marker authoritative), or compare an intrinsic embedded
  run id instead of mtime. (Mirror: `plugins/charness/scripts/check_mutation_score.py`.)

## Tier 2 — real but conditional (latent); needs a little design

- **D — CLOSED (2026-07-20, commit `48b51a39`; verified 2026-08-01).** The fix
  landed the same day this scan was written and the record was never updated, so
  the handoff carried the row as open for eleven days.
  `tests/test_usage_episodes_host_hooks.py` now excludes the live-writer paths
  (`sessions/**`, `usage_episode.jsonl`) from the snapshot, with the finding id in
  the code comment, and carries three regression tests including a discriminating
  control (`..._tolerates_concurrent_live_writers`,
  `..._still_catches_state_file_mutation`, `..._still_catches_unexpected_new_file`).
  Verified independently by the parent and by two bounded reviewers. The original
  statement follows, unedited.
- **D (as written 2026-07-20). `tests/test_usage_episodes_host_hooks.py:15-53,406-469`.** Two tests snapshot
  the REAL shared `REPO_ROOT/.charness/usage-episodes/` tree, run a CLI subprocess,
  then assert the whole tree is byte-identical and "no new files appeared". If a live
  Claude/Codex **SessionStart hook** (this repo ships/installs `usage_episode_session_start.py`,
  which writes `.charness/usage-episodes/sessions/current` + `start.json`) fires while
  the suite runs, or a concurrent `run-quality.sh` writes there, the `after - before`
  delta is non-empty → false-positive failure unrelated to the SUT. Latent under a
  clean isolated run (nothing in-suite writes the live tree). Fix: scope the assertion
  to the specific session-id/paths the test could have created (PID/mtime-fenced
  delta), or run the guard against a copied/redirected tree instead of the live one.

## Tier 3 — low severity; defer or fold in opportunistically

- **E. `scripts/hitl_review_artifact_lib.py:300` (+`:47`) (P1).** `artifact.st_mtime + 0.5 < runtime_updated_ts`
  — the 0.5s slack is below 1s mtime granularity; same-second post-sync drift is not
  flagged (false negative). Secondary check (content-metadata compare at :294-299 is
  primary). Fix: compare an embedded sync token / content hash.
- **F. `scripts/narrative_adapter_lib.py:266` (P1).** `min(same_name, key=len)` over
  `rglob("*")` order; equal-length same-basename candidates → filesystem-order-arbitrary
  suggestion (advisory string only). Fix: `key=lambda p: (len(p), p)`.
- **G. `scripts/t_events_emit_lib.py:74-76` (P1).** Rotation filename is a 1s wall-clock
  stamp; two rotations within one second produce an identical name and the `rename`
  clobbers the earlier file. Practically negligible (needs two size-threshold crossings
  in one second). Fix: append `time.time_ns()`/a counter to the rotation stamp.
- **H. `scripts/record_quality_runtime.py:140-159,194-218` (P2).** `update_summary`/
  `update_smoothing` read-modify-write shared `runtime-signals.json`/`runtime-smoothing.json`
  via plain `write_text` (not atomic, no lock). Concurrent cross-process recorders →
  lost update / torn read. Repo-local, advisory data. Fix: atomic temp+`os.replace`
  (reuse `scripts/current_pointer_writer_lib.py`).
- **I. `scripts/host_hook_install_lib.py:116-155` / `scripts/host_hook_codex_toml_lib.py:71-75` (P2).**
  Machine-shared `~/.claude/settings.json` / `~/.codex/config.toml`. Temp write is SAFE
  (per-PID `.tmp.{pid}` + atomic `os.replace`); only residual is a lost-update if two
  repos install hooks at the same instant — self-heals on next install/doctor. Mostly
  safe; note only.
- **J. Test timing budgets (low).** `tests/charness_cli/test_codex_cache_refresh.py:179-201`
  (`assert elapsed < 0.15` — 90ms headroom, could flake on a CPU-starved 16-worker box;
  raise ceiling or drop the upper bound); `tests/test_usage_feedback.py:174` (sleep 0.75,
  generous); `tests/test_web_fetch_cleanup.py:342-346` (10s monotonic deadline, generous).

## Confirmed SAFE (already-defended — do NOT re-audit)

- Exemplars fixed: `run_standing_pytest.py` (`charness-run-*` leaf), `publish_release_runtime.py`
  (`O_EXCL`+`time_ns`+atomic replace+`missing_ok` retention; embedded-stamp eviction).
- Guarded P1 selectors: `capability_catalog_resolver.py:19`, `host_log_probe_lib.py:{36,40,193}`,
  `codex_session_jsonl_audit.py:40`, `hitl_review_artifact_lib.py:35`, `recent_lessons_lib.py:45`,
  `debug/plan_debug_run.py:157` — all `(…mtime, name)` / intrinsic-key tiebroken.
- Protected P2 sites: `record_usage_feedback.py` (`flock`), `current_pointer_writer_lib.py`
  (per-PID temp + atomic replace), `publish_release_rollback.py` (per-worktree unique subdir),
  `seed_cache.py` (content-addressed + `filelock`), single-run generated-surface `rmtree`s.
- Test isolation: per-worker `tmp_path` pervasive; `conftest.py` #225 git-ceiling; worktree
  tests use tmp `git init`; mtime tests use explicit `os.utime`; seed cache filelock+content-hash;
  agent-browser guard uses faked `ps`.

## Scan coverage

- P1 (scripts/skills): `st_mtime|st_ctime|st_atime|getmtime|getctime|st_mtime_ns`, enumeration-as-order
  (`glob|iterdir|listdir|scandir`), `time.time()|datetime.now()|monotonic`, `hash(|id(`, selection
  primitives (`max|min|sorted[...][0]|next(iter`), deletion sites (`unlink|rmtree|rename|os.replace`).
- P2 (scripts/skills): temp roots (`gettempdir|mkdtemp|mkstemp|TMPDIR|PYTEST_DEBUG_TEMPROOT|XDG_CACHE_HOME|/tmp`),
  git-common/worktree (`--git-common-dir|--git-path|.git|worktree`), reapers (`rmtree|unlink|os.remove|rm -rf`),
  coordination (`filelock|flock|O_EXCL|os.replace|missing_ok|exist_ok`).
- Test flake (tests/, 445 files): `os.environ[...]=`, `chdir`, `sleep|time()|monotonic|perf_counter`,
  `git worktree add`, `ROOT|REPO_ROOT` writes, `iterdir|glob|listdir` ordering, `st_mtime|os.utime`,
  `filelock|flock`, fixed `/tmp|gettempdir|mkdtemp`, `Path.home|expanduser`, `HOME|XDG|TMPDIR`, session fixtures.
- Excluded by scope: `plugins/` (generated mirror), `mutants/`, `.mjs` runtime tests.
- Not exhaustively read: every `cwd=ROOT` validator subprocess test (sampled, cleared); a follow-up grep
  for those writing ROOT-relative outputs would close it, but none surfaced.

## Next-session pickup

Tier 1 (A, B, C) is **done** — see the Tier 1 heading above; do not re-plan it.
Tier 2 (D) is **done too**, and was already done when this line was written —
closed on 2026-07-20 in `48b51a39`, confirmed 2026-08-01. Do not re-plan it.
Tier 3 is opportunistic / boy-scout only.

The eleven days this row spent on the handoff as open work is the lesson worth
keeping: a record that is not updated when its fix lands is a backlog entry that
costs a future session a reproduction attempt.
