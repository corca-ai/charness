# Command-Plan Changed-Line Proof

Date: 2026-08-21

## Receipt

- Command: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
- Base SHA: `38775dfeb8d1e5574663d7ef461d19a63e252841`
- Resolved HEAD SHA: `ea6737b30b770d454a0ec2a1d45338efdf559ce6`
- Status: `clean`
- Analyzed changed-pool files: `23`
- Changed files: `23`
- Blocking targets: `[]`
- Consumer return code: `0`
- Standing pytest: passed (`76.9s`)
- Raw operator log: `/tmp/charness-final-head-changed-line-current.log`
- Raw log SHA-256: `70aa8f42b2f9ab077ae19ea1c24800b5850fd9d86723f97ea03db987ede13536`

## Execution Boundary

The proof was rerun alone at the exact current HEAD after a concurrent
broad/changed-line attempt produced a no-verdict race. The two producers share
mutation/coverage state and are therefore serialized here. This receipt proves
changed-line coverage for the stated base and HEAD only; it does not prove
runtime, installed, hosted, publication, issue-closeout, or Cautilus truth.
