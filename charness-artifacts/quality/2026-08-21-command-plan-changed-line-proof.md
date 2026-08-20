# Command-Plan Changed-Line Proof

Date: 2026-08-21

## Receipt

- Command: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
- Base SHA: `38775dfeb8d1e5574663d7ef461d19a63e252841`
- Resolved HEAD SHA: `3cc29d5ea9f4e82d87cc6c5c0356c95f5569ccd6`
- Status: `clean`
- Analyzed changed-pool files: `23`
- Changed files: `23`
- Blocking targets: `[]`
- Consumer return code: `0`
- Standing pytest: passed (`77.6s`)
- Raw operator log: `/tmp/charness-final-head-changed-line-serialized.log`
- Raw log SHA-256: `8e7a2d0c7a4c5d2a1a0ddfe79c05f15ec4fb2e43b15cd4a2b82b51d726c9bee3`

## Execution Boundary

The proof was rerun alone after a concurrent broad/changed-line attempt
produced a no-verdict race. The two producers share mutation/coverage state and
are therefore serialized here. This receipt proves changed-line coverage for
the stated base and HEAD only; it does not prove runtime, installed, hosted,
publication, issue-closeout, or Cautilus truth.
