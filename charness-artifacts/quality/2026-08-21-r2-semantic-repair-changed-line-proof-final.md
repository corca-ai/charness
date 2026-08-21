# R2 Semantic Repair Changed-Line Proof

Date: 2026-08-21

## Receipt

- Command: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha 825b2a4198ae1342a843ccd20f57be7f4e1e0213 --refuse-unestablished`
- Base SHA: `825b2a4198ae1342a843ccd20f57be7f4e1e0213`
- Resolved HEAD SHA: `7d15f1aef1dabd948ed1f71806294050348219e9`
- Status: `clean`
- Analyzed changed-pool files: `7`
- Changed files: `7`
- Blocking targets: `[]`
- Consumer return code: `0`
- Standing pytest: passed (`52.4s`)
- Raw operator log: `charness-artifacts/quality/2026-08-21-r2-semantic-repair-changed-line-proof-final.raw.log`
- Raw log SHA-256: `4948fb901ae6d4fc56182f9be9b4722937a923ff00728006f239124e1dc7930f`

## Execution Boundary

The first run at this exact base had no verdict because a load-bearing
`rail-1 snapshot/verify` contract pin was missing. After that wording was
restored, the next run passed standing pytest but exposed three uncovered
worker-delivery evidence branches. Direct counterexample tests were added and
this same producer was rerun clean.

This receipt proves changed-line coverage for the stated base and HEAD only.
It does not prove runtime, installed, hosted, publication, issue-closeout,
Cautilus, or fresh-eye approval. The semantic packet and round-2 review must
bind this exact candidate and its receipt.
