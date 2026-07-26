# xdist scheduling session retro
Date: 2026-07-26

## Context

One session under the standing operator direction (bug fixes, friction/rework, test/code
speed), taking the handoff's item 2 — the clause the previous session recorded as
untouched. Profiled the standing pytest suite, found the bottleneck was xdist's
scheduler rather than the tests, re-derived the four runtime bars the speedup
invalidated, and published `v2.11.1`.

## Evidence Summary

- Timeline instrumentation (per-worker start/stop over 16 workers) showed 14 of 16
  workers idle from t=23s while one ran alone to t=109s; 78s of a 110s wall sat at one
  or two concurrent tests, 4.2x effective parallelism.
- Cause read from installed `xdist/scheduler/load.py:289-292`: each worker gets a
  CONSECUTIVE chunk of `len(collection)//nworkers//4` before any timing feedback, and
  this suite's slow tests are adjacent (`tests/charness_cli/` sorts first).
- `--maxschedchunk 1`: standing gate 45.5s -> 26.9s (11.3x effective);
  `run-quality --read-only` 54.5s -> 37.8s; 4-core `taskset -c 0-3` 64.8s -> 64.5s.
- Four bars re-derived, all verified against 20/20 post-change windows for the three
  36cpu labels: `pytest` 73000 -> 58500, `run-quality-read-only` 76500 -> 58500,
  `run-quality-full` 100000 -> 62000, `pytest-release` 87000 -> 105000 (a raise).
- Three bounded fresh-eye reviews, all boundary-verified clean; 11 + 9 findings acted on.

## Waste

- **Four failed publish attempts** (~20 min) to one root cause: I ran the release helper
  from the INSTALLED plugin (`~/.agents/src/charness/plugins/...`) instead of the repo's
  own `skills/public/release/scripts/`. Installed charness was 2.11.0, whose
  `recent_lessons_lib` predates this repo's `independent_source_count` change, so the
  helper wrote an old-schema lesson index that the repo's own gate then rejected as
  stale. `bootstrap-resolution.md` already says to use the repo copy inside the source
  tree; I did not read it before reaching for a path I already had.
- Diagnosing it cost three of those attempts because the gate's message —
  "index is stale; run `--write`" — points at a fix that CANNOT work here: `--write`
  emits the new schema, and the next publish overwrites it with the old one again.
- Two rounds of budget-bar rewriting: I sized bars from the post-change slice, then
  learned from review that enforcement reads the full-window median, then had to run the
  windows to convergence and rewrite every number and comment a second time.
- Wrote a version floor (`MIN_XDIST_FOR_SCHED_CHUNK = (2, 3)`) from inference and
  shipped it into a commit before checking; the real answer is 3.2.0.

## Critical Decisions

- Instrumenting the per-worker timeline instead of reading `--durations`. The durations
  list showed a 16.7s slowest test and a 478s total — both consistent with a healthy
  suite. Only the timeline showed the idle 78s, which is where the win was.
- Verifying the mechanism against installed xdist source rather than shipping the
  docstring I had already written. "Round-robin `len(collection)//4`" was wrong in the
  way that mattered: CONSECUTIVE chunking is precisely why adjacency made it bite.
- Taking the reviewer's PATCH argument over the MINOR I had planned, and rewording the
  handoff precedent that would have produced the same wrong bump next time.
- Reproducing the publish failure deterministically before re-running it. The first
  instinct — "it passed on re-run, ship it" — would have shipped an unexplained red.

## Expert Counterfactuals

- **Brendan Gregg / USE method:** ask for UTILIZATION before latency. "5.5 of 36 cores
  busy" was visible in the very first `time` output (552% CPU) and named the bottleneck
  class — idle workers, not slow tests — an hour before the timeline plugin did.
- **A release engineer's "which binary am I running":** the first question on any
  self-hosting tool failure is whether the tool under test is the tool doing the
  testing. Asked at attempt one, it would have saved three.

## Sibling Search

- axis: helper-writes-artifact-that-repo-gate-validates | decision: valid follow-up outside the slice | proof: `publish_release_retro.py` is one of several installed-helper paths that write through repo libs (`persist_retro_artifact`, `write_current_artifact`, `build_debug_seam_risk_index`); any of them can drift the same way | follow-up: deferred handoff-1
- axis: bars-sized-from-slice-but-enforced-on-window | decision: valid follow-up outside the slice | proof: `runtime_budget_sizing_lib.suggest_budgets` reads `max_recent_elapsed_ms` (whole window) while a regime-change retune reasons about a slice; `--suggest-budgets` cannot reproduce three of the four committed bars | follow-up: deferred handoff-3

## Next Improvements

- workflow: when the repo IS the tool, resolve `$SKILL_DIR` to the repo copy before the
  first command, not after the first failure. `bootstrap-resolution.md` is the contract
  and it is one read.
- capability: the installed helper should refuse, or loudly warn, when `--repo-root`
  resolves to the charness source tree and the installed version differs from the repo's
  — the gate caught this, but its message misdirects toward a fix that cannot work.
- memory: a version floor, an upstream mechanism, and a precedent's scope are all CLAIMS
  ABOUT THE WORLD. Check each against its source in the same edit that writes it; this
  session shipped one of each from inference and a reviewer caught all three.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md
