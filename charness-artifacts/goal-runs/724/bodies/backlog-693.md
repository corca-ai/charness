<!-- charness-work-item-key: backlog-693 -->
# Existing Work Item #693 — Distinct-context critique provenance

## Purpose and premise

Re-read whether same-context provenance is enforced. If it is not, define the
same/distinct-context fixtures and exact identity fields before any verdict
change.

## Owned change and acceptance

The reviewer and reviewed input identities are explicit; same-context
substitution is refused, distinct context is accepted only when bound, and any
verdict-logic change receives two review rounds.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/test_critique_round_findings.py`, then changed-line proof. No fresh-eye result is inferred from this addendum.
