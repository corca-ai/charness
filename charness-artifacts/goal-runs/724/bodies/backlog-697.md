<!-- charness-work-item-key: backlog-697 -->
# Existing Work Item #697 — Distinct mutation coverage producers

## Purpose and premise

Specify separate producer paths/markers for mutation sampling and changed-line
coverage. Re-read the current report path and freshness checks first.

## Owned change and acceptance

A freshness marker identifies its producer; the changed-line producer remains
authoritative and the sampler cannot satisfy its proof merely by writing the
same report path.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_changed_line_mutation_coverage.py`, then changed-line proof. No expensive evaluator or release mutation is claimed.
