# Current Open Surface Refresh

Captured: 2026-08-21T07:07:16+09:00
Source: `gh issue list --repo corca-ai/charness --state open --limit 100`
Each live row was then read with `issue_tool.py read --comments`; this is a
scope receipt, not a replacement for the frozen activation ledger.

## Live Issues

| Issue | Title | Provisional release route | Meaningful slice |
| --- | --- | --- | --- |
| #687 | Fresh-eye review delivery has no terminal path for interrupted subagents | qualified Charness child + host dependency | review-delivery reliability |
| #686 | Retro planner emits unavailable source-layout auto-trigger command | qualify as installed-layout repair | installed/source path contract |
| #685 | Retro persistence warns on the documented artifact-name stem | qualify as CLI contract repair | artifact persistence contract |
| #683 | Reviewer fingerprint custom snapshot output does not reveal verify --before handoff | qualify as handoff contract repair | review-delivery reliability |
| #682 | Auto-retro prescribed command loses changed paths after slice commit | qualify as commit-boundary repair | evidence continuity |
| #681 | goal checker says Gate cadence is absent while returning the detected line | requalify current source; likely already-satisfied or regression | verdict consistency |

The already-closed #684 is intentionally excluded from this live set; its
retro-path child is represented by #686 and must be read independently.

## Qualification Checkpoints

- #681: current source search finds the cadence-owner parser and related tests;
  re-run the canonical goal checker on a current consumer fixture before
  changing code. Existing ledger route is `already-satisfied`, not a closure
  claim for the live tracker.
- #682: current `check_auto_trigger.py --base-ref HEAD^ --head-ref HEAD` uses
  the explicit commit-range input and evaluates. The clean-after-commit
  no-basis failure still needs a deterministic fixture before admission.
- #683: the guessed `verify --snapshot` form exits 2; the declared
  `verify --before` form is the valid continuation. This is a live command-shape
  smell, while any boundary drift is a separate worktree fact.
- #685: current help still documents `--artifact-name` as a stem without an
  extension; the warning-producing persistence invocation remains to be run in
  an isolated fixture before admission.
- #686: installed 6.2.0 `plan_retro_run.py --repo-root /tmp
  --changed-paths scripts/example.ts` emits the source-layout
  `skills/public/retro/.../check_auto_trigger.py` path as unavailable while the
  plan envelope is `ok: true`. This is an installed-layout current reproducer.
- #687: source-of-truth readback and the issue-first RCA are complete; the
  Charness child remains contingent on R1 admission fields, and the host
  terminal explanation remains a runtime non-claim.

## R1 Admission Result

The four current reproductions for #682, #683, #685, and #686, plus the
issue-first #687 delivery failure, are now appended as post-lock
`release-blocker` exceptions in
`charness-artifacts/issues/2026-08-20-next-release-ledger.json`. Their
source reads, reproduction artifacts, exact commands, nonzero assertion exits,
and release impact are bound there. #681 remains the original ledger's
`already-satisfied` row pending a fresh consumer requalification; it was not
silently promoted or duplicated.

## Admission Rule

No provisional route is a qualified repair until the current reproducer,
acceptance owner, disjoint path budget, proof command, and release-content
carrier are recorded in an append-only ledger amendment. A passing current
reproducer becomes an explicit `already-satisfied` or `premise-refuted` row,
not silent omission.

## #687 Boundary

The unnamed one-shot request is the established Charness mitigation for named
mailbox routing. The pinned Codex source is a separate source-level host
hypothesis; runtime episode attribution remains unproven. The release may
carry Charness refusal/diagnostic prevention while leaving the host change open.
