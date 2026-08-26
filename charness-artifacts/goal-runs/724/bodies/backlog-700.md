<!-- charness-work-item-key: backlog-700 -->
# Existing Work Item #700 — Grant transition readback

## Purpose and premise

Choose the exact grant-transition producer and narrative consumer. Re-read the
pre/post grant fixtures and make stale prose refusal explicit.

## Owned change and acceptance

The producer records the transition identity and the consumer re-reads it before
claiming a release-time grant. A pre-grant narrative cannot authorize a
post-grant action without the required readback.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_release_narrative_gate.py`, then changed-line proof. This child does not grant release or publish anything.
