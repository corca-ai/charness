# Quality Review
Date: 2026-08-06
Title: Mutation producer discovery for the post-push proof slice

## Scope

Target boundary: changed-line mutation-coverage producer selection for the
current post-push goal range, plus the manifest test fixture needed by the
selected target set.

Ambient repo findings: broad pytest, locked coverage stamping, remote CI,
installed-consumer behavior, provider state, and Cautilus are outside this
focused producer-selection packet.

## Current Gates

The existing changed-line mutation floor and `run_slice_closeout.py` producer
contract remain unchanged. The helper must identify every eligible Python file
in the merge-base-to-worktree pool before a focused producer is accepted.

## Runtime Signals

- runtime source: structured command output captured in `/tmp/slice5-mutation-suggestion-after-fix.yaml` and `/tmp/slice5-focused-producer-proof-after-fix.txt`.
- runtime hot spots: no timing measurement; this slice measures target completeness and focused test success only.
- coverage gate: the focused target command passed; the locked coverage stamp remains a final-bundle obligation.
- evaluator depth: deterministic-gates-only; no Cautilus evaluation was requested.

## Healthy

- `suggest_mutation_coverage_command.py --detail` resolved merge-base `e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5`.
- The eligible mutation pool contains 7 changed Python files: `check_premise_preflight.py`, `final_bundle_preflight.py`, `final_bundle_preflight_evidence.py`, `final_bundle_preflight_lib.py`, `premise_preflight_lib.py`, `slice_manifest_lib.py`, and `validate_slice_manifest.py`.
- All 7 eligible files map to 3 standing targets, with `unmapped_changed_pool_files: []`.
- The eighth changed `scripts/` path, `boundary-bypass-exemptions.txt`, is non-Python and correctly outside the mutation pool.
- The selected standing command passed 58 tests: `test_final_bundle_preflight.py`, `test_premise_preflight.py`, and `test_slice_manifest.py`.
- The disposable manifest fixture now recomputes reader-root and parity hashes against its clone; the frozen captured manifest remains unchanged. The focused manifest suite passed 24 tests, and the producer/mapping plus manifest suites passed 54 tests.

## Weak

- The helper proves producer-target mapping through imports, loader references, and standing-target reachability; it does not itself prove changed-line coverage.
- The focused run was an uninstrumented target proof. It did not write the freshness marker consumed by the changed-line mutation gate.

## Missing

- A verification-locked closeout that instruments the selected command and writes fresh coverage for the final committed range.
- The final broad pytest and integrated closeout after the remaining ledger and handoff slices.

## Deferred

- Keep the existing mutation floor and run the selected command through `--produce-mutation-coverage` only after the final semantic inputs and bounded reviews are frozen.
- Do not add manual targets or treat the non-Python boundary exemption as a mutation-pool file.

## Advisory

- structural review result: command: `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --detail`; the complete eligible set was mapped without a broad fallback.
- focused proof result: command: `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_final_bundle_preflight.py --pytest-target tests/quality_gates/test_premise_preflight.py --pytest-target tests/quality_gates/test_slice_manifest.py`; 58 passed.
- fixture repair result: the initial target run exposed a stale captured reader-root hash after Slice 3 changed `.agents/surfaces.json`; the disposable fixture was refreshed, while stale-reader and parity-refusal assertions remain active.

## Delegated Review

- Delegated Review: executed — an unnamed bounded fresh-eye reviewer independently confirmed the 7-file pool, 3-target command, zero unmapped eligible files, and fixture semantics; it returned clean. Parent boundary fingerprint `slice5-producer-review-2` verified clean with no drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not re-delegated; this slice selected an existing focused producer and changed only a test fixture.

## Commands Run

- `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --detail` — recommended; 7 eligible files, 3 targets, no unmapped files.
- Focused standing producer-target command — 58 passed.
- `pytest -q tests/quality_gates/test_slice_manifest.py` — 24 passed after the fixture repair.
- `pytest -q tests/quality_gates/test_suggest_mutation_coverage_command.py tests/quality_gates/test_slice_manifest.py` — 54 passed.
- `ruff check tests/quality_gates/test_slice_manifest.py` — passed.
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing` — passed with existing advisory warn-band findings.
- `python3 scripts/check_changed_surfaces.py --repo-root .` — matched the repo-python surface; no sync command required.
- Reviewer boundary snapshot/verify — clean; no reviewer-attributed worktree or index drift.
- `python3 scripts/run_slice_closeout.py --repo-root . --base 922bd448 --skip-broad-pytest` — completed; structural and deterministic pre-lock checks passed, while broad pytest and locked mutation coverage remain final-bundle obligations.

## Recommended Next Quality Moves

- active — capability_needed=locked mutation proof; next_center=final bundled closeout; transformation=instrument the selected 3-target command and retain broad proof; proof_boundary=verification-locked closeout; enforcement_posture=existing-gate-reuse.
- active — capability_needed=integrated publish-state proof; next_center=immutable ledger and handoff; transformation=reconcile the final committed state before any publish boundary; proof_boundary=distinct observer readback; enforcement_posture=existing-gate-reuse.

## History

- [Prior runtime phase-isolation review](history/2026-07-19-portable-proof-path-learning-review.md)
