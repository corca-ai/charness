<!-- charness-work-item-key: backlog-704 -->
# Existing Work Item #704 — Typed `link_only_lines_slack`

## Purpose and premise

Make `link_only_lines_slack` one stable `integer|null` field. Re-read the
document graph producer and its JSON/YAML consumers before changing the shape.

## Owned change and acceptance

The value is an integer when computable, otherwise null with an explicit reason;
the first consumer rejects strings and the unavailable case cannot be mistaken
for a measured slack value.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/test_docs_graph_gate.py`, then changed-line proof. This child claims no documentation-release or hosted result.
