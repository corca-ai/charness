# Standing-Pytest Basetemp Deletion Race Debug
Date: 2026-07-20

## Problem

The standing pytest suite intermittently emits a large burst of errors under full
`--release` xdist load (once "12 failed + 1321 errors"; reproduced here as
"11 failed, 3612 passed, 1439 errors"), concentrated in whichever tests happen to
allocate a `tmp_path` at the wrong moment. It passes clean in isolation and on
retry. Capability at risk: a deterministic, trustworthy standing-quality gate.

## Correct Behavior

Given the full standing suite running under xdist with nested pytest/quality
subprocess tests, when any worker allocates a `tmp_path`, then its per-worker
basetemp (`.../popen-gwN`) still exists for the whole session, so no worker errors
on `tmp_path` setup.

## Observed Facts

- The error is `FileNotFoundError` in pytest's `tmp_path` -> `make_numbered_dir` ->
  `os.scandir(<basetemp>/popen-gwN)`; the worker's own basetemp dir was deleted
  mid-run, across many workers (gw1,2,5,6,7,10,12,14,15) at once.
- `run_standing_pytest` passed an explicit `--basetemp` of
  `PYTEST_DEBUG_TEMPROOT/pytest-of-<user>/pytest-<time_ns>`; run-quality.sh exports
  `PYTEST_DEBUG_TEMPROOT` and nested runs inherit it.
- pytest `getbasetemp` explicit-`--basetemp` branch does `rm_rf` + `mkdir` only — it
  creates NO cleanup `.lock` file (unlike the default numbered-dir branch).
- pytest `cleanup_numbered_dir`/`ensure_deletable`: an unlocked `pytest-*` dir is
  always deletable; `make_numbered_dir_with_cleanup(keep=3)` registers this cleanup
  at `atexit`, so it runs when each nested pytest subprocess exits.
- Reproduced only under the FULL suite; the two named files alone pass 30x3 at `-n 16`.

## Reproduction

- Full suite: `python3 scripts/run_standing_pytest.py --repo-root . --mode full
  --include-release-only` in a loop — ~1 in 3 runs hit the error burst.
- Deterministic unit repro: create a lock-less `pytest-<n>/popen-gw0` under a shared
  `pytest-of-<user>`, run `make_numbered_dir_with_cleanup(prefix="pytest-", keep=3)`
  several times, then `cleanup_numbered_dir(...)` — the lock-less dir is renamed to
  `garbage-*` and removed.

## Candidate Causes

- Nested pytest cleanup deletes the outer run's lock-less explicit basetemp (shared
  rootdir via inherited `PYTEST_DEBUG_TEMPROOT`). ✅ confirmed (pytest source + probe).
- Resource exhaustion / worker OOM under `-n 16` load. ❌ signal is a clean
  `FileNotFoundError` on a deleted dir, not an allocation/kill error.
- Cross-worker seed-cache race (`tests/seed_cache.py::get_or_build`). ❌ that surface
  is `filelock`-serialized and self-healing; not the deleter.

## Hypothesis

- Falsifiable claim: the outer run's explicit `--basetemp` is a lock-less `pytest-*`
  dir sharing `pytest-of-<user>` with nested runs, so a nested run's exit-time
  `make_numbered_dir_with_cleanup` deletes it mid-run. | disconfirmer: recreate the
  lock-less `pytest-*/popen-gwN` + run the cleanup functions directly and see it die.

## Verification

- result: confirmed — the direct probe deleted the lock-less `pytest-*` basetemp and
  its `popen-gw0`; renaming the leaf to a non-`pytest-*` prefix (`charness-run-*`) left
  it untouched across 6 nested cleanups. Full-suite proof: 10/10 clean `--release`
  runs post-fix (prior base rate ~1-in-3 failing).

## Root Cause

`default_basetemp` named the explicit basetemp `pytest-<time_ns>`. Because it lives
under the shared `PYTEST_DEBUG_TEMPROOT/pytest-of-<user>` rootdir that nested pytest
runs also use, and pytest's explicit-`--basetemp` branch never writes a cleanup lock,
the outer basetemp is an unlocked deletion candidate for any nested run's
`make_numbered_dir_with_cleanup(prefix="pytest-", keep=3)` at process exit. Fix: name
the leaf `charness-run-<time_ns>` so it is invisible to pytest's `pytest-*` cleanup
glob while staying in the intended external cache root.

## Invariant Proof

- Invariant: a per-run explicit basetemp shared with nested pytest cleanup must not be
  a `pytest-*` name (the only cleanup target), since pytest gives explicit basetemps
  no protective lock.
- Producer Proof: `default_basetemp` now emits `charness-run-<ns>` (unit-pinned).
- Final-Consumer Proof: nested-cleanup simulation leaves `charness-run-*` intact; full
  `--release` suite 10/10 clean.
- Interface-Shape Sibling Scan: two tests asserted the old `pytest-*` leaf
  (`test_standing_pytest_default_basetemp_uses_user_and_time`, `test_quality_runner`)
  — both updated to the new invariant.
- Non-Claims: none outstanding.

## Detection Gap

- surface: standing pytest gate itself | what did not fire: the failure is load- and
  timing-dependent and self-heals on retry, so a single green run hid it | smallest
  change to fire it: a deterministic unit regression that drives pytest's own cleanup
  against a lock-less basetemp and asserts survival (added,
  `test_default_basetemp_survives_nested_pytest_cleanup`).

## Sibling Search

- Mental model: "an explicit pytest `--basetemp` is private and safe from cleanup."
  False when it shares `pytest-of-<user>` with nested runs and carries no lock.
- naming axis: `default_basetemp` leaf | decision: fix | proof: probe + full-suite.
- assertion-sibling axis: two tests hardcoded the `pytest-` leaf | decision: update to
  the new invariant | proof: both red on old name, green on fix.
- cross-file: `run_standing_pytest` also `shutil.rmtree`s only its own basetemp; nested
  bare-pytest runs self-protect via locks — no other lock-less shared `pytest-*` writer.
- name-consumer sibling (found in critique): `standing_test_economics_lib.py`
  `PYTEST_SESSION_RE` keyed session discovery on `^pytest-\d+$`; the new leaf would drop
  from the drill-down footprint (enforcement seed-budget gate uses whole-root `du`, so
  it stayed correct). Broadened to `^(?:pytest|charness-run)-\d+$` + a pinning test.

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

Any per-run explicit pytest `--basetemp` placed under a rootdir shared with nested
pytest invocations must avoid the `pytest-*` name so pytest's numbered-dir cleanup
cannot target it; explicit basetemps get no protective lock. Before renaming a widely
referenced constant, grep for tests asserting its exact shape (two assertions here were
only caught by the full-suite run) — batch those updates with the change.
