# Implementation Contract: Issue #697

Date: 2026-08-27

## Current Slice

Close the Charness-owned producer boundary between mutation sampling and
changed-line coverage. The changed-line producer remains the only producer
whose report can satisfy the changed-line freshness check.

## Fixed Decisions

- The changed-line report remains `reports/mutation/test-coverage.json`.
- The sampler's default coverage report is
  `reports/mutation/sample-coverage.json`.
- The changed-line freshness marker is the producer-qualified sibling
  `test-coverage.json.changed-line.fingerprint`; legacy/foreign marker content
  is not fresh for this consumer.
- An explicit sampler override of a changed-line report invalidates the
  changed-line marker before replacing the report.
- Cosmic Ray's sampler filter reads the sampler report by default.
- No hosted enforcement, evaluator run, release, push, installed-host claim,
  issue closure, or consumer-repository migration is included.
- Per user direction, no forced fresh-eye review, handoff update, or micro-slice
  ceremony is claimed.

## Acceptance Checks

1. A sampler-shaped report plus a matching legacy content-only marker is
   skipped as unverified by the changed-line consumer.
2. A marker with a foreign producer is skipped as unverified.
3. A changed-line producer marker is accepted only when its content fingerprint
   matches the current changed pool.
4. The sampler, Cosmic Ray runner, and Cosmic Ray filter share the distinct
   sampler default; runtime files and retention cover both report paths.
5. Root scripts and the checked-in plugin mirror are identical for every
   changed mirrored script.

## Owned Paths

- `scripts/mutation_sampling_lib.py`
- `scripts/mutation_changed_files_lib.py`
- `scripts/check_changed_line_mutation_coverage.py`
- `scripts/mutation_coverage_producer.py`
- `scripts/sample_mutation_files.py`
- `scripts/run_cosmic_ray_mutation.py`
- `scripts/filter_cosmic_ray_mutants.py`
- `scripts/manage_mutation_reports.py`
- related CLI/help/spec/reference surfaces and focused tests
- corresponding `plugins/charness/` mirrors

## Verification Ledger

- Reproduction receipt:
  `charness-artifacts/debug/receipts/issue-697-producer-collision.json`
- Direct producer-boundary regression suite:
  `python3 -m pytest -q tests/quality_gates/test_distinct_mutation_coverage.py` —
  5 passed.
- Affected focused test set selected by the mutation-coverage suggester — passed
  in the canonical read-only standing runner.
- Changed-line proof worktree: `/tmp/charness-697-proof2-20260827`.
- Changed-line proof base SHA:
  `6b42f7d9b8ec106bcfe575cc149198624753c477`.
- Changed-line proof target SHA:
  `94180891ee5dd99f64187b406443ebde0d215416`.
- Changed-line proof path scope: all changed scripts under
  `scripts/` that belong to the mutation-coverage pool; 11 analyzed, 0
  unmapped, 0 blocking, consumer exit 0.
- Changed-line proof command:
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .
  --base-sha 6b42f7d9b8ec106bcfe575cc149198624753c477
  --refuse-unestablished`, with `PYTHONPYCACHEPREFIX` directed outside the
  worktree.
- Root/plugin mirror parity and targeted Ruff/pre-commit checks: passed.
- This artifact records implementation proof only; issue closeout and Goal Run
  advancement remain separate operations pending the closeout readback.
