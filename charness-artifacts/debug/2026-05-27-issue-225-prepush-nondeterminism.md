# Issue 225 Pre-push Gate Non-determinism Debug
Date: 2026-05-27
Source: GitHub issue #225

## Problem

On this 4-CPU `aarch64` host the pre-push quality gate
(`./scripts/run-quality.sh --read-only`, run by `.githooks/pre-push`) reports the
`pytest` phase as failed even on otherwise-green work, forcing `--no-verify`
pushes. Issue #225 frames it as (1) pytest-xdist isolation flakiness across ~16
"fail-closed outside git" / strict-listing tests and (2) cautilus eval tests
hard-failing on a cautilus version/surface mismatch instead of skipping.

## Correct Behavior

The pre-push gate is the maintainer-local enforcement boundary, so its result
must reflect code correctness. Optional external capabilities that are absent or
drifted (cautilus, the `coverage` package) must cause the affected tests to
**skip**, and the standing pytest run must be deterministic under `-n auto` on a
multi-CPU host regardless of where the repo lives in the filesystem.
<!-- reproduction-source -->

## Observed Facts

- `cautilus --version` -> `0.14.2`; its surface is `cautilus claim discover` /
  `cautilus eval test` / `cautilus scenario propose`. `scripts/eval_cautilus_chatbot_proposals.py:65`
  invokes `cautilus discover scenarios propose` and `scripts/eval_cautilus_chatbot_compare.py:235`
  invokes `cautilus evaluate comparison prepare`; neither exists on 0.14.2.
- `tests/test_cautilus_chatbot_compare.py:12` and `tests/test_cautilus_scenarios.py:14`
  gate on `shutil.which("cautilus")` (binary presence) only, not surface.
- `python3 -c "import coverage"` -> `ModuleNotFoundError`; `coverage` is not a
  declared dependency. `scripts/mutation_sampling_lib.py:72 run_test_coverage`
  spawns `python3 -m coverage run`, so the three tests that call it hard-fail.
- `run-quality.sh` computed `PYTEST_TEMPROOT="${XDG_CACHE_HOME:-${HOME:-/tmp/.cache}}/charness/pytest-tmp/..."`.
  With `XDG_CACHE_HOME` unset this expands to `${HOME}/charness/pytest-tmp` =
  `/home/ubuntu/charness/pytest-tmp` — i.e. **inside the repo**, because this
  host's repo is `$HOME/charness` and the fallback drops the `.cache` segment.
  A stray `pytest-tmp/<key>/pytest-of-ubuntu/...` tree was left in the repo root
  after each run, and the `test_portable_json_artifacts` failure value was the
  repo-relative `pytest-tmp/.../external-worktree`.

## Reproduction

- cautilus / coverage hard-fails reproduce deterministically:
  `pytest -p no:xdist <the 5 nodes>` -> 5 failed (cautilus Usage error /
  `No module named 'coverage'`).
- `run-quality.sh --read-only` failed only the `pytest` phase on
  `test_portable_json_artifacts::...external_worktree_paths` and
  `test_check_coverage_inventory::...ignores_ambient_orphans`. The same suite run
  with an explicit `--basetemp` under `$HOME/.cache/...` (outside the repo)
  passed across repeated `-n auto` runs — isolating the in-repo basetemp as the
  trigger, not parallelism per se.

## Candidate Causes

- cautilus/coverage tests gate on the wrong (or no) usability signal for an
  optional external capability, so absence/drift becomes a hard failure.
- `run-quality.sh` places the pytest basetemp inside the repo, so fixtures that
  assume a temp tree outside the repo misbehave.
- Genuine cross-xdist-worker state sharing in the named tests (ruled out: the
  tests pass under an out-of-repo basetemp at the same `-n auto` parallelism).

## Hypothesis

If the basetemp resolves outside the repo (`$HOME/.cache/...`) and optional
capabilities skip on absence/drift, then external-worktree path classification,
fail-closed-outside-git listing, and `copytree(ROOT)` probes all behave correctly
and the pre-push `pytest` phase is deterministic.

## Verification

- `run-quality.sh --read-only` `pytest` phase now PASSES (1545 passed, 11
  skipped) after the basetemp fix; the 5 cautilus/coverage tests skip.
- Repeated full `-n auto` runs (out-of-repo basetemp) stayed green.
- `validate_packaging.py` passes after re-syncing the `plugins/charness` mirror
  of `run-quality.sh`.

## Root Cause

Two independent root causes:

1. **Optional-capability hard-fail.** cautilus eval tests gate on binary
   presence (`shutil.which`) not surface/version; mutation-coverage tests have no
   guard for the optional `coverage` package. Both should skip.
2. **`run-quality.sh` places the pytest basetemp inside the repo.** Its
   `PYTEST_TEMPROOT` fallback used bare `$HOME` (not `$HOME/.cache`) when
   `XDG_CACHE_HOME` is unset; on a host whose repo is `$HOME/charness` that is
   `<repo>/pytest-tmp/...`. An in-repo basetemp breaks every fixture that assumes
   its temp tree is outside the repo: external-worktree classification,
   fail-closed-outside-git listing, and `copytree(ROOT)` probes that then copy
   the live, concurrently-written basetemp. This is deterministic per host
   layout, which is why it looked like random xdist flakiness across hosts.

## Detection Gap

- cautilus eval tests: gate only on binary presence — add a subcommand-surface
  probe (`cautilus ... --help`) and skip when absent.
- mutation-coverage tests: no optional-dependency guard — add
  `pytest.importorskip("coverage")`, matching the repo's `importorskip` pattern.
- basetemp location: nothing asserted `PYTEST_TEMPROOT` resolves outside the
  repo; the bare-`$HOME` fallback silently produced an in-repo basetemp.

## Sibling Search

Mental model: a test (or runner) trusts an ambient signal — "the capability is
nominally present" or "the temp tree is outside the repo" — without making the
assumption explicit, so a drifted host quietly violates it.

Scanned sibling patterns:

- other `@requires_cautilus`-gated tests and other `run_test_coverage` consumers
  share the same gate/lib; fixed at the shared helper / call sites now.
- fail-closed-outside-git fixtures share the in-repo-basetemp assumption; hardened
  defensively with a `GIT_CEILING_DIRECTORIES` ceiling at the temp root.
- prior artifact `2026-05-22-repo-file-listing-strict-mode.md` owns the
  strict-listing feature; its tests are the structural sibling hardened here.

## Seam Risk

- Interrupt ID: issue-225-prepush-basetemp-and-optional-capability-gating
- Risk Class: operator-visible-recovery
- Seam: `run-quality.sh` temp-root expansion interacts with the operator's repo
  location and `XDG_CACHE_HOME`; cautilus surface depends on the installed binary.
- Disproving Observation: `run-quality.sh --read-only` pytest phase passes with
  the `.cache` fallback, and the stray in-repo `pytest-tmp` no longer appears.
- What Local Reasoning Cannot Prove: behavior on hosts with an unusual
  `XDG_CACHE_HOME` pointing inside the repo, or a cautilus version that does
  expose the exercised surfaces.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this file

## Prevention

Gate optional-capability tests on actual usability (surface/version for
binaries, `importorskip` for packages); never let a cache-root fallback resolve
to the repo itself; and keep filesystem/git fixture assumptions explicit rather
than dependent on basetemp location or ambient ancestor state. Resolution
critique bundled two cheap guards that implement the detection gap above:
`run-quality.sh` now hard-fails if `PYTEST_TEMPROOT` resolves inside the repo
(covers a regressed fallback or an in-repo `XDG_CACHE_HOME`/`PYTEST_DEBUG_TEMPROOT`),
and `pytest-tmp/` is gitignored so a recurrence cannot be committed.
