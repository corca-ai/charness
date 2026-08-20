# Command-Plan Changed-Line Proof

Date: 2026-08-21

## Receipt

- Command: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
- Base SHA: `38775dfeb8d1e5574663d7ef461d19a63e252841`
- Resolved HEAD SHA: `19e62aea829e4d40b1ede2d1e2273ea067963dd1`
- Status: `clean`
- Analyzed changed-pool files: `23`
- Changed files: `23`
- Blocking targets: `[]`
- Consumer return code: `0`
- Standing pytest: passed (`78.3s`)
- Raw operator log: `/tmp/charness-final-head-changed-line-19e62aea.log`
- Raw log SHA-256: `827b0d8242b5c28a58495a72cf16a9396e623aeb246f4c2cfe1e2587b7ff5d07`

## Execution Boundary

The proof was rerun alone at the exact current HEAD after a concurrent
broad/changed-line attempt produced a no-verdict race. The two producers share
mutation/coverage state and are therefore serialized here. This receipt proves
changed-line coverage for the stated base and HEAD only; it does not prove
runtime, installed, hosted, publication, issue-closeout, or Cautilus truth.
