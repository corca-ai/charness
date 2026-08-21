# Current Open Surface Refresh

Captured: 2026-08-21T18:07:56+09:00
Source: `gh issue list --repo corca-ai/charness --state open --limit 100`
Each live row was then read with `issue_tool.py read --comments`; this is a
scope receipt, not a replacement for the frozen activation ledger.

## Live Issues

| Issue | Title | Current release disposition | Meaningful slice |
| --- | --- | --- | --- |
| #687 | Fresh-eye review delivery has no terminal path for interrupted subagents | `release-blocker retained`: Charness child present; host terminal event unclaimed | review-delivery reliability |
| #686 | Retro planner emits unavailable source-layout auto-trigger command | `release-blocker retained`: source/export repair present; installed proof pending | installed/source path contract |
| #685 | Retro persistence warns on the documented artifact-name stem | `release-blocker retained`: source repair present; installed proof pending | artifact persistence contract |
| #683 | Reviewer fingerprint custom snapshot output does not reveal verify --before handoff | `release-blocker retained`: supported continuation present; candidate proof pending | review-delivery reliability |
| #682 | Auto-retro prescribed command loses changed paths after slice commit | `release-blocker retained`: committed-basis repair present; candidate proof pending | evidence continuity |
| #681 | goal checker says Gate cadence is absent while returning the detected line | `already-satisfied` source requalification; tracker/install closeout pending | verdict consistency |

The already-closed #684 is intentionally excluded from this live set; its
retro-path child is represented by #686 and must be read independently.

## Historical Qualification Notes (not current admission state)

The current requalification join is recorded in
`charness-artifacts/issues/2026-08-21-current-requalification.md`. It keeps
the historical post-lock reproducer separate from current source, installed,
and host observations; it is not an issue-close or publication receipt.

The notes below preserve the original reproductions and command-boundary
signals. They do not reopen admission or override the authoritative table
above.

- #681: comments-inclusive read `681.raw.yaml` and the current goal checker
  agree on `ok: true`; the remaining claim is installed/tracker closeout.
- #682: the bare clean-tree call is intentionally `state: not-established`;
  the explicit committed-range form evaluates. The historical empty-basis
  signal is not a current repair-admission state.
- #683: the guessed `verify --snapshot` form exits 2; the declared
  `verify --before` form is the valid continuation. This is a live command-shape
  smell, while any boundary drift is a separate worktree fact.
- #685: the historical installed 6.2.0 warning is retained as public-surface
  evidence; the current source repair is present and candidate install proof
  is still pending.
- #686: the historical installed 6.2.0 source-layout path mismatch is retained
  as public-surface evidence; source/export repair is present and candidate
  install proof is still pending.
- #687: source-of-truth readback and the issue-first RCA are complete; the
  Charness child may ship with the host terminal explanation explicitly
  unclaimed.

## Current Source/Install Split

- #682/#683: source-side continuation contracts are present and their exact
  current positive controls are in the requalification packet; bare empty
  basis and guessed flags remain explicit non-verdict failures.
- #685/#686: current source passes the repaired contract, while installed
  Charness 6.2.0 still reproduces the warning/path mismatch. Do not discharge
  either release exception before a candidate install/update readback.
- #687: typed Charness non-delivery states are source-proven; the host-side
  terminal event channel is not available in this checkout.

## R1 Admission Result

The four current reproductions for #682, #683, #685, and #686, plus the
issue-first #687 delivery failure, are now appended as post-lock
`release-blocker` exceptions in
`charness-artifacts/issues/2026-08-20-next-release-ledger.json`. Their
source reads, reproduction artifacts, exact commands, nonzero assertion exits,
and release impact are bound there. #681 now also has a comments-inclusive raw
read, but remains the original ledger's `already-satisfied` row pending a fresh
consumer requalification; it was not silently promoted or duplicated.

## Historical Admission Rule

No provisional route is a qualified repair until the current reproducer,
acceptance owner, disjoint path budget, proof command, and release-content
carrier are recorded in an append-only ledger amendment. A passing current
reproducer becomes an explicit `already-satisfied` or `premise-refuted` row,
not silent omission. This rule has been applied to the rows above; it is
retained here as the reason for the durable release-blocker amendments, not as
an instruction that admission is still pending.

## #687 Boundary

The unnamed one-shot request is the established Charness mitigation for named
mailbox routing. The pinned Codex source is a separate source-level host
hypothesis; runtime episode attribution remains unproven. The release may
carry Charness refusal/diagnostic prevention while leaving the host change open.
