# Release Critique — charness v8.14.1 (patch)

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.14.1-release (current: 8.14.0, tag `v8.14.0` at `1c5e38dd8`)
- **Scope**: `1c5e38dd8..HEAD` — behavior delta is two fix commits:
  `4e2a03b95` input validation before executor PATH probing (#825) and
  `acb7056f7` standalone payload retry plus lane-owned scope attribution
  (#875, #876) with the PATH-independence gate. Commits between the tag and
  the fixes are v8.14.0 release-process residue (claims re-bind, artifact,
  receipt refreshes) with no behavior change.
- **Reviewers**: one fresh-eye reviewer (read-only shared checkout, no repo
  mutation), delegated by the parent; verdict below is the reviewer's own.
- **Lane evidence**: release lane green, 90 passed, 0 failed
  (`./scripts/run-quality.sh --full --read-only --release`), including the
  new path-independence gate and changed-line coverage on the release HEAD.

Fresh-eye satisfaction: parent-delegated angle reviewer, findings received.

## Reviewer Tier Evidence

- **Requested tier**: (none requested — single general-purpose reviewer)
- **Requested spawn fields**: read-only shared checkout, verdict-plus-findings
  report, no repo mutation
- **Host exposure state**: `host-defaulted`
- **Application state**: findings received as subagent result text
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`
- **Lane evidence**: release lane green, 90 passed, 0 failed
  (`./scripts/run-quality.sh --full --read-only --release`)

## Boundary Ownership

- **Producer**: fresh-eye release critique reviewer (verdict plus findings)
- **Consumer**: release publisher (`publish_release.py --execute`) and operators
  reading the release notes
- **Owning surface**: `charness-artifacts/critique/v8141-critique.md` (this
  record)
- **Verdict**: `owned-correctly`

## Verdict

GO, conditional on the release battery showing the new path-independence
phase green (met: 90 passed, 0 failed on the release HEAD, gate included).

## Bump Honesty

Patch is correct. Both commits are `fix(task-run)` with no new flags, no
schema additions, and no intended breaking change. Operator-visible behavior
changes, all fix-shaped (carried into the release notes): bad
`--timeout-seconds`/`--no-progress-seconds`/grant-executor flags now report
themselves instead of "not on PATH" when executors are missing
(`scripts/task_run/task_run_plan.py`); merge-lane receipts get narrower
(lane-owned attribution); the standalone entry now reaches task run payloads.

## Safety / Contract Risks (reviewed, none blocking)

- The `sys.path` retry in the standalone entry is single-process only.
- Receipt shrink can break strict receipt parsers — by design, narrower is
  the fix.
- The carrier move (`task_run_carrier.py`) breaks private importers of the
  old module path.
- Error-precedence change is pinned by tests.
- The gate hardcodes a minimal PATH, fragile on off-standard images.
- Octopus merges stay conservative under the new attribution.
- The no-cover line trusts its mutant test (verified: removing the insert
  kills `test_standalone_copy_reaches_task_run_payload`).

## Reason Not To Release

None on contract. No blocking finding.
