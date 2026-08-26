<!-- charness-work-item-key: backlog-706 -->
# Existing Work Item #706 — Honest dup-ratchet withheld counts

## Purpose and premise

Preserve “not judged” in dup-ratchet summaries for adapter-invalid, inert, and
rebaseline paths. Re-read each summary producer and its consumer contract.

## Owned change and acceptance

Withheld counts and verdict fields must never be rendered as reassuring zeroes;
the summary names the reason and keeps valid measured zero distinct from absent
measurement.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_dup_ratchet.py`, then changed-line proof. No release authorization is inferred.
