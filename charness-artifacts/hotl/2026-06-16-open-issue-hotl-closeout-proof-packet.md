# HOTL Proof Packet: Open issue HOTL closeout

Status: draft
Created: 2026-06-16
Goal: `charness-artifacts/goals/2026-06-16-open-issue-hotl-closeout.md`

## Loop Inventory

- Surface class: mixed local guard / repo artifact / GitHub issue state /
  external runtime lifecycle.
- Related issues: #378, #377, #376, #375, #371.
- Applied/live state at shaping: no active-run mutation has been executed.
- Adapter state: no HOTL adapter is present; live proof commands are
  undeclared.

## Success Criteria

- Every shaped issue (#378, #377, #376, #375, #371) is verified `CLOSED`
  through GitHub readback after the implementation carrier lands.
- Any GitHub issue closure carries before/after provider readback.
- #371 closeout is acceptable from the Charness side if local mitigation and
  ownership transfer are proven, upstream lifecycle ownership is linked, and the
  closeout explicitly does not claim invocation-bound teardown was fixed.
- #371 upstream lifecycle proof is verified only if invocation-end process-tree
  teardown and `agent-browser-chrome-*` profile-dir cleanup are proven for
  normal completion, cancellation, provider failure, and timeout.

## Pre-Roundtrip Failure Checks

- Confirm `issue_tool.py preflight --repo-root . --json` selects an
  authenticated GitHub backend.
- Refresh `gh issue list --repo corca-ai/charness --state open --limit 50`.
- Read each issue with comments before design.
- Run `hotl` adapter resolution. If no adapter declares live proof commands,
  record any live-provider proof need as a residual disposition unless the
  active run first adds a repo-owned proof command and tests it.
- Validate issue closeout carrier drafts before publishing close keywords.

## Feasibility

- #378: feasible through local quality advisory implementation plus tests and
  GitHub closeout readback.
- #377: feasible through repo-wide artifact/current-pointer audit, resolver or
  instruction changes, validators where justified, and GitHub closeout readback.
- #376: feasible through skill-contract updates plus at least one cross-skill
  audit and tests/validators that prove the visible re-judgment surface.
- #375: feasible through `achieve` adapter/scaffold changes and tests proving
  idempotent draft-frame customization.
- #371: feasible as Charness-local closeout if the active run records verified
  mitigation/readback plus residual upstream issue disposition. The local issue
  can close without upstream lifecycle verification, as long as the closeout
  explicitly does not claim that upstream teardown was fixed.

## Human Intervention

- Before any push, release, or manual issue close, name the phase-scoped carrier
  and obtain or record the operator-approved path.
- If #371 proof depends on a real provider cancellation/failure/timeout event,
  record the exact action packet and readback target before executing it.

## Non-Claims

- Local deterministic tests do not prove live provider lifecycle behavior for
  #371.
- A direct cleanup command or doctor result proves post-hoc mitigation only, not
  invocation-bound teardown.
- Closing #371 locally does not prove upstream `agent-browser` has fixed its
  daemon/profile lifecycle.
- A closed GitHub issue proves tracker state only; it does not by itself prove
  release availability or consumer update.

## Ledger Draft

| Issue | Initial HOTL status | Required proof or disposition |
| --- | --- | --- |
| #378 | planned | Local advisory implementation proof plus GitHub before/after closeout readback |
| #377 | planned | Audit/change proof plus GitHub before/after closeout readback |
| #376 | planned | Re-judgment contract proof plus GitHub before/after closeout readback |
| #375 | planned | Adapter-controlled scaffold proof plus GitHub before/after closeout readback |
| #371 | planned close | Verify Charness mitigation/ownership closeout; disposition upstream lifecycle residual as `issue` with upstream tracker and non-claim; verify local GitHub issue closed |
