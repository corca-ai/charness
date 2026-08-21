# R2 Changed-Line Proof

Date: 2026-08-21

## Receipt

- Command: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha "$(git rev-parse 495af8a20^)" --refuse-unestablished`
- Base SHA: `825b2a4198ae1342a843ccd20f57be7f4e1e0213`
- Resolved HEAD SHA: `c0738b0f33bb6e69d22eabeb2672bc8eaa96e67d`
- Status: `clean`
- Analyzed changed-pool files: `6`
- Changed files: `6`
- Blocking targets: `[]`
- Consumer return code: `0`
- Standing pytest: passed (`50.5s`)
- Raw operator log: `/tmp/r2-changed-line-proof-after-coverage-repair.out`
- Raw log SHA-256: `603bca02440b9011225a02aba4eef63d9317e4db678c04f1d034a0e58c6a18d8`

## Execution Boundary

The first run at this exact base returned `blocked` on five uncovered input
classes. Counterexample tests were then added at the adapter, packet-renderer,
and release-ledger consumer boundaries, and the same producer was rerun. This
receipt proves changed-line coverage for the stated base and HEAD only; it does
not prove runtime, installed, hosted, publication, issue-closeout, or Cautilus
truth.
