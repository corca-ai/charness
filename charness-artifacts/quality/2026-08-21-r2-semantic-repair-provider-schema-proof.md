# R2 Semantic Repair Provider-Schema Proof

Date: 2026-08-21

## Receipt

- Command: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha 825b2a4198ae1342a843ccd20f57be7f4e1e0213 --refuse-unestablished`
- Base SHA: `825b2a4198ae1342a843ccd20f57be7f4e1e0213`
- Resolved HEAD SHA: `2a8b479cb32a01e1e04289276cbcba3d321bc9f9`
- Status: `clean`
- Analyzed changed-pool files: `7`
- Changed files: `7`
- Blocking targets: `[]`
- Consumer return code: `0`
- Standing pytest: passed (`62.7s`)
- Raw operator log: `charness-artifacts/quality/2026-08-21-r2-semantic-repair-changed-line-proof-provider-schema.raw.log`
- Raw log SHA-256: `da11bccbbdd255fdda4dfe8c3d465bacdec7512cacaf853fbb2d214879ae483a`

## Execution Boundary

The prior candidate packet was invalidated after the first round-2 worker
fan-out exposed a provider rejection: Codex requires `additionalProperties:
false` on nested response-schema objects. The source/plugin schema was closed
recursively and a focused regression was added before this proof.

This receipt proves changed-line coverage for the stated base and HEAD only.
It does not prove reviewer delivery, fresh-eye approval, installed or hosted
behavior, publication, issue closeout, or Cautilus evaluation. The semantic
packet must bind this exact candidate before the next fresh-eye round.
