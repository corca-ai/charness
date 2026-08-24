# Issue #689 Node TAP Accounting Handoff

Date: 2026-08-24

## Contract

The Ceal requalification must distinguish a green direct Node run from the
wrapper reporter's accounting verdict. The direct fixture proves Node itself;
the wrapper mutation roundtrip proves reporter selection, summary ownership,
mutation accounting, and exact restoration. Any newly exposed reporter defect
is split into its own implementation contract rather than weakening #689's
consumer proof.

## Outcome

Ceal's real TAP suite passed 27/27 and the installed Charness wrapper killed the
selected mutation before restoring the file byte-for-byte. The sibling run-window
defect became issue #714 and is governed by
`charness-artifacts/spec/2026-08-24-issue-714-run-window.md`.

## Critique

- Interrupt Source: issue-689-node-tap-accounting-2026-08-24
- Seam Summary: runner output -> reporter -> structured payload -> consumer/adoption fork.
- Chosen Next Step: factor-first
- Impl Status: allowed
- Impl Status Reason: the direct Node control and wrapper mutation roundtrip separate the healthy consumer path from the newly factored #714 reporter defect.
- What Disproving Observation Is Resolved: the same fixture can be green under explicit Node execution while default reporter selection refuses it, so Node health alone cannot establish wrapper accounting.

## Non-Claims

This record does not close #689, #714, or any GitHub issue, and it does not prove
installed adoption beyond the recorded Ceal roundtrip.
