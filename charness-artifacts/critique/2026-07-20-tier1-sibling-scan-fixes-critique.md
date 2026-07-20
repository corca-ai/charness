# Critique Review
Date: 2026-07-20

## Decision Under Review

Fixing the three Tier-1 findings from the abstracted-pattern sibling scan
(`charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md`):

- A (P2): `scripts/record_quality_runtime.py` `rotate_archives` now uses
  `oldest.unlink(missing_ok=True)` so two concurrent recorders racing on the
  same oldest archive cannot fail the losing recorder with `FileNotFoundError`.
- B (P2): `scripts/mutation_baseline_abort_lib.py`
  `delete_stale_baseline_abort_marker` drops the exists-then-unlink TOCTOU and
  uses `marker_path.unlink(missing_ok=True)`.
- C (P1): `scripts/check_mutation_score.py` `_marker_is_stale` flips `>=` to
  `>` so a same-mtime tie on a coarse-granularity filesystem keeps the abort
  marker authoritative instead of letting a persisted previous-run stats file
  mask a genuine current baseline abort.

Plugins mirrors regenerated; two new regression tests pin the race
(`test_rotate_archives_tolerates_concurrently_deleted_oldest`) and the tie
direction (`test_marker_is_stale_false_on_mtime_tie_keeps_marker_authoritative`).

One bounded fresh-eye reviewer ran over the uncommitted slice (correctness of
the tie flip, error-swallowing risk, test soundness, mirror fidelity, scope);
the rail-1 reviewer-boundary fingerprint verified clean around the pass.

## Failure Angles

- Correctness: does the `>` tie flip break any `_marker_is_stale` caller or
  consumer expectation, and is the tie direction actually the safe one given
  `sample_mutation_files.py` deletes the marker at run start?
- Robustness: could `missing_ok=True` now silently swallow a legitimate error
  state (permissions, directories, symlinks)?
- Test quality: does the `Path.glob` monkeypatch race test genuinely fail
  pre-fix, and does it introduce xdist/parallel hazards of its own?
- Mirror fidelity: do the three `plugins/charness/scripts/` mirrors byte-match
  canonical?
- Scope: anything beyond Tier 1 A/B/C plus tests and mirrors.

## Counterweight Pass (four-bin triage)

- K2 | over-worry (confirmed, no change): `_marker_is_stale` has exactly one
  caller (`check_mutation_score.py`); `check_js_mutation_score.py` reads the
  marker but never calls it, so the JS path is unaffected. With a real mtime
  gap the old-marker-ignored behavior is unchanged (pinned by
  `test_check_mutation_score_marker_ignored_when_stats_file_is_newer`); only an
  exact tie now fails safe (surfaces the possible abort) instead of failing
  open. `Path.unlink(missing_ok=True)` suppresses only `FileNotFoundError` —
  `PermissionError`/`IsADirectoryError` still raise. The race test binds
  `original_glob` before patching, invokes glob exactly once, restores via
  `monkeypatch.undo()`, and is isolated per-worker by `tmp_path`; the reviewer
  confirmed the pre-fix code raises on the test's simulated race.
- K4 | valid-but-defer (no action): dropping the `exists()` pre-check means a
  dangling symlink at the marker path is now removed instead of skipped — more
  correct, and the marker is always a tool-written regular file. The
  same-second-tie case now exits 2 (reports a possible abort) where it
  previously trusted the stats file; that is the audit's intended fail-safe
  cost, accepted.
- No K1/K3 entries: the reviewer reported zero blockers, should-fixes, or nits
  across all five angles.

## Recurrence Verdict

A and B restore consistency with their already-guarded structural siblings
(`t_events_emit_lib.py`, `publish_release_runtime.py`), shrinking the
odd-one-out surface the sibling scan flagged; C closes the last unsafe-direction
mtime tie in the mutation gate. The remaining pattern instances are recorded as
Tier 2/3 in the audit artifact with their own dispositions, so the class does
not depend on memory to resurface.

## Boundary Ownership

- Verdict: owned-correctly

The canonical `scripts/` files own the behavior; the `plugins/charness/scripts/`
mirrors are regenerated output synced via `sync_root_plugin_manifests.py`, and
the regression tests live with the owning gate suites. No producer/consumer
inversion.

## Reviewer Tier Evidence

<!-- allowed Host exposure state enums only -->
- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, typed `bounded-reviewer`
  (Read/Grep/Glob) with session-model inheritance per the repo per-host
  subagent contract; no Codex model requested on this host, so the omission is
  contract-conformant, not a degradation.
- Host exposure state: host-defaulted
- Application state: the host spawned the typed `bounded-reviewer` agent by
  name; the read-only envelope bound and the rail-1 reviewer-boundary
  fingerprint verified clean (no index/worktree drift) after the reviewer
  returned, so approvals are valid and the reviewer ran on the parent's
  session-inherited model.

## Fresh-Eye Satisfaction

parent-delegated — one high-leverage bounded reviewer over the uncommitted
slice with an in-report counterweight; rail-1 reviewer-boundary fingerprint
verified clean.
