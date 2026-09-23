# Release Critique — charness v8.11.1 (patch): task-run repair 834/835/836

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.11.1-release (task-run repair bundle for #834, #835, #836)
- **Scope**: `task run` lane repairs for #834 (post-edit scope-mismatch
  self-revert), #835 (`--no-progress-seconds` flag), #836 (zero-match glob
  warn-only). Touched: `scripts/task_run/` (scope, plan, progress, attempts,
  lane_runner, completion, task_run), root `charness` CLI parser, generated
  `docs/cli-reference.md`, focused tests
  (`test_task_run_scope.py`, `test_task_run_scope_closure_831.py`,
  `test_task_run_implementation_lane.py`).
- **Reviewers**: two fresh-eye parallel reviewers (contract/behavior,
  operability/deletion-safety) + parent synthesis; read-only, no repo mutation.
- **Lane evidence**: `./scripts/run-quality.sh --full --read-only` green on the
  staged tree (84 passed, 0 failed); focused suites 94 passed
  (35 scope + 53 implementation-lane + 6 scope-closure-831); ruff clean.

Fresh-eye satisfaction: parent-delegated two angle reviewers plus synthesis.

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `read-only shared checkout; structured concerns`
- **Host exposure state**: `host-defaulted`
- **Host exposure note**: spawn surface exposes no model field; default
  routing used and recorded
- **Application state**: `two angle reports delivered with concerns triage`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`

## Release Scope

#836 turns a zero-match `--scope` glob from a preflight refusal into a
warning-only creation seam (`unmatched-glob-scope` beside #831's
`unmatched-literal-scope`), admitting lane-created matching paths on refresh
while frozen `directory_matches` still never widen automatically. #835 puts the
no-progress budget on the `task run` surface as `--no-progress-seconds`
(`0` turns the stop off; finite `>= 0` required), overriding
`CHARNESS_TASK_RUN_NO_PROGRESS_SECONDS` and recorded as `budget_source`
(flag/env/default) in `progress_guard`. #834 splits the scope-mismatch
directive into pre-edit (`BLOCKED: premise/scope mismatch`, do not edit) and
post-edit (never restore/reset scoped files; keep the candidate; emit the typed
`BLOCKED: scope mismatch - real owner <path> is outside declared scope`
request), and adds a carrier backstop: EDITING/TESTING + BLOCKED + unchanged
worktree records `candidate-self-reverted` with the guard's first-scoped-diff
snapshot riding as a recovery pointer
(`recovered_scoped_snapshot.diff_ref`), not a second diff copy.

## Boundary Ownership

- **Producer**: release critique reviewers (angle findings plus synthesis)
- **Consumer**: release publisher (`publish_release.py --execute`) and
  operators reading the release notes
- **Owning surface**: `charness-artifacts/critique/task-run-834-836-release-critique.md`
  (this record); scope-mismatch directive and backstop owned by
  `scripts/task_run/task_run_lane_runner.py` and
  `scripts/task_run/task_run_completion.py`, guard snapshot owned by
  `scripts/task_run/task_run_progress.py`, budget flag owned by
  `scripts/task_run/task_run_plan.py` and the root `charness` task-run parser,
  glob warn-only owned by `scripts/task_run/task_run_scope.py`
- **Verdict**: `owned-correctly`

## Surface-Lock Inventory

No public skill, adapter, or install surface moves except one additive,
backwards-compatible CLI flag (`--no-progress-seconds`, default preserves env
behavior). `docs/cli-reference.md` regenerated from the parser.

## Findings Disposition (parent synthesis)

- **Act Before Ship**: reviewer B's four nits applied before staging —
  single-copy diff text (`diff_ref` pointer), `candidate_self_reverted` key set
  only on `True`, top-level `math` import, `budget_source` through the
  constructor; reviewer A's one defer item applied — `truncated` also covers
  the 50-path diff cap. Re-verified after each edit (ruff + 94 focused tests).
- **Bundle Anyway**: none.
- **Over-Worry (checked, not problems)**: 64 KiB once-only guard snapshot is
  proportionate (require-change lanes only, path cap, byte cap, explicit flags);
  typo'd globs spending a full lane is #836's stated intent with dry-run
  warning + require-change gate as mitigation; prompt growth (~8 lines) is the
  minimal post-EDITING mechanism; `_poll` double refresh is harmless at 15 s
  cadence; #836 admission is exact (probed: non-matching paths stay out);
  brace empty-arm refusal unchanged (#790); #835 boundaries hold
  (`0` disables, negative/NaN/inf refused, flag > env > default).
- **Valid but Defer**: `--dry-run` on a dirty tree never reaches scope
  resolution, so `scope_warnings` are unreachable mid-work (pre-existing
  ordering; follow-up candidate).

## Counterweight

The riskiest alternative — leaving the post-edit directive unconditional and
relying on parents to re-extend scope after a self-revert — was rejected:
it destroys tested work by default and the relaunch costs ~20 minutes per
occurrence. The chosen backstop only labels the shape; it never blocks a lane
that did not edit. The flag addition was preferred over guard-heuristic changes
(reading-aware budgets, READING markers) because it is a visible, recorded
per-lane choice with no behavior change at default.
