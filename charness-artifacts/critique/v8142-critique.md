# Release Critique — charness v8.14.2 (patch)

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.14.2-release (current: 8.14.1, tag `v8.14.1`)
- **Scope**: `v8.14.1..HEAD` — behavior delta is one fix commit:
  `ee6420943` prompt-evidence scope preflight is advisory, never a launch
  block (#880). The v8.14.1 receipt-refresh commit in between carries no
  behavior change.
- **Reviewers**: two fresh-eye reviewers in parallel (read-only shared
  checkout, no repo mutation), safety angle plus correctness angle, with a
  synthesis counterweight pass; verdicts below are the reviewers' own.
- **Lane evidence**: release lane green, 90 passed, 0 failed
  (`./scripts/run-quality.sh --full --read-only --release`), including
  release-changed-line-coverage on the release HEAD.

Fresh-eye satisfaction: parent-delegated angle reviewers, findings received.

## Reviewer Tier Evidence

- **Requested tier**: (none requested — two parallel angle reviewers, safety
  plus correctness, with a synthesis counterweight pass)
- **Requested spawn fields**: read-only shared checkout, verdict-plus-findings
  report, no repo mutation
- **Host exposure state**: `host-defaulted`
- **Application state**: findings received as subagent result text
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`
- **Lane evidence**: release lane green, 90 passed, 0 failed
  (`./scripts/run-quality.sh --full --read-only --release`)

## Boundary Ownership

- **Producer**: fresh-eye release critique reviewers (verdict plus findings)
- **Consumer**: release publisher (`publish_release.py --execute`) and operators
  reading the release notes
- **Owning surface**: `charness-artifacts/critique/v8142-critique.md` (this
  record)
- **Verdict**: `owned-correctly`

## Verdict

SHIP. No Act Before Ship items.

## Bump Honesty

Patch is correct. One `fix(task-run)` commit, no new flags, no schema
additions, no intended breaking change. One deliberate contract change,
carried into the release notes: prompts naming out-of-scope paths now exit
0 / status `pass` on `--dry-run` instead of the old `premise-blocked`
refusal; automation that probed scope via dry-run exit codes must read the
advisory `would_touch_outside_declared` findings instead.

## Safety / Contract Risks (reviewed, none blocking)

- The executor now launches even when the prompt names out-of-scope paths;
  genuinely mismatched prompts spend a full run and fail at completion
  instead of failing fast. Accepted: the false-positive rate (any slash
  prose or backtick path triggered the old block) outweighs the saved spend,
  and completion-friction logging makes a spike observable.
- Scope enforcement on real writes is untouched: `_scope_result` still
  FAILs candidates with changed paths outside the declared scope, and
  completion blockers still append the scope reason. Report-only lanes never
  failed completion on prompt text before either, so no defense-in-depth is
  lost.
- `brief_critique` premise-failure and acceptance-skeleton blockers still
  block in `run_prelaunch_gates`; only the text-heuristic gate was removed.

## Reason Not To Release

None on contract. Follow-ups are deferred, not blocking: the evidence
parser still records slash prose as advisory findings (receipt and
launch-warning noise, no block); watch scope-fail-at-completion friction
for a spike before considering any fail-fast return.
