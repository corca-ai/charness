# Remote CI Changed-Line Reconciliation Contract

Date: 2026-08-09
Source: [remote CI debug record](../debug/2026-08-09-remote-ci-changed-line-reconciliation-debug.md)

## Problem

The local focused changed-line lane and the remote broad mirror disagree over
the same eligible files. The local selector cannot resolve an existing dynamic
loader dependency, so deliberate mapper policy renders the files `UNPROVEN` and
non-blocking. GitHub's broad coverage sees the files and correctly blocks eight
uncovered changed lines. Main is red after a local green aggregate.

## Capability Contract

For an eligible changed file, the focused selector owns test reachability, the
selected test owns executable observation, and the changed-line consumer owns
the verdict. When a supported loader call contains a literal naming the changed
file, the selector must map the standing test. The consumer may pass only after
that test's coverage observes the changed lines; selector absence and executable
coverage absence remain different states.

## Current Slice

Reconcile the exact `ec67291e...18a9a439` failure range before the active goal
continues to slice 5: recognize the existing dynamic-loader call shape in the
shared selector, prove the mapper turns the two files from unmapped to mapped,
observe the local focused lane fail on the eight real gaps, then add direct
in-process branch tests and prove the same lane passes.

## Fixed Decisions

- Preserve the recorded policy that a genuinely unmapped file is non-blocking;
  this slice repairs false absence rather than converting every selector blind
  spot into a push refusal.
- Keep one reachability owner in `suggest_mutation_coverage_command.py` so
  `prepush_focused_changed_line_coverage.py` and
  `subprocess_only_coverage_advisory.py` inherit the repair.
- Recognize string constants only inside the loader families the selector
  already supports; compare full path, filename, and stem tokens. A decoy token
  outside a loader call must remain unmapped.
- Exercise `check_regenerable_facts.py` in-process in its owning test module;
  subprocess CLI tests remain for delivery behavior but cannot carry line
  coverage across the process boundary.
- Do not weaken the CI mirror, shrink its range, add an exemption, widen a
  timeout, or add a new gate.
- Sync the generated plugin projection only after all source and review repairs.

## Probe Questions

- Does loader-token recognition map both the entry script and its sibling
  library through existing loader ancestry without mapping an unrelated decoy?
  Signal: focused selector fixture plus the live `--detail` payload. If false,
  refine the reachability model before adding coverage tests.
- Once mapped but before branch tests, does the local focused lane block the
  same eight lines? Signal: the exact old base-range run. If it does not, the
  local/remote consumer contract is still different and implementation returns
  to debug.

## Deferred Decisions

- General AST data-flow resolution for arbitrary path aliases is deferred; the
  current supported loader boundary and a negative decoy fixture bound this
  repair.
- Remote CI confirmation is deferred until an explicit push approval. Local
  proof cannot claim a green hosted run.

## Non-Goals

- Reversing mapper policy for truly unknown test dependencies.
- Reworking broad mutation coverage production or GitHub workflow topology.
- Advancing the active goal's planned deletion slice or the unrelated #518 awiki
  contract.

## Deliberately Not Doing

- No coverage exclusion, pragma, exemption, or changed-line scope reduction.
- No direct edit to the shipped regenerable-facts behavior; only its testability
  and the shared selector are repaired.
- No push, release, tag, version bump, issue close, or Cautilus evaluation.

## Constraints

- The mapper's safe error direction is extra focused runtime or a local false
  stop, never a false pass. The negative fixture must show the repair stays
  bounded to a loader call.
- The old failure range is the acceptance fixture; checking only the new diff
  would not prove the original red main is repaired.
- Because the selector renders verdict scope for other code, this is proof-
  surface verdict logic and owes two bounded review rounds. The second reads any
  round-1 repair; two is the cap.
- Existing user changes and the two local handoff commits remain intact.

## Success Criteria

- The live selector maps both regenerable-facts files to
  `tests/quality_gates/test_regenerable_facts.py` over the original base range
  and no longer lists either as unmapped.
- A negative fixture proves an identical filename/stem outside a supported
  loader call does not create a mapping.
- After the mapper repair but before coverage repair, the local focused consumer
  exits 1 and names the original uncovered targets. After the tests, focused
  coverage observes every target and the consumer reports no blocking lines,
  while the final wrapper remains `unestablished`/exit 3 on the dirty mapper
  worktree. The wrapper passes the same range only after the repair is committed
  and its analyzed tree matches its measured tree.
- Focused coverage records all eight remote CI target lines as executed.
- Targeted tests, generated projection parity, changed-surface checks, locked
  closeout, and the repo quality gate pass without lowering a floor.
- The durable debug record changes to `Resolution: resolved` and preserves the
  remote-CI non-claim until hosted CI is read back after an approved push.

## Acceptance Checks

- `python3 -m pytest -q tests/quality_gates/test_suggest_mutation_coverage_command.py tests/quality_gates/test_regenerable_facts.py` — unit: loader mapping, decoy, and branch behavior.
- `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --base-sha ec67291e88c76c45e5604882152bc021a915458b --detail` — integration: live old-range reachability.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha ec67291e88c76c45e5604882152bc021a915458b --json` — integration: mapper-only fail-before (exit 1), post-test no-blocking but dirty-tree refusal (exit 3), and post-commit final local-consumer pass.
- Focused `coverage` JSON readback for lines 20, 63, 102, 106, 107, 122, 183, and 184 — integration, reproduction-only local output.
- `python3 scripts/check_changed_surfaces.py --repo-root .` and `python3 scripts/check_staged_mirror_drift.py --repo-root .` — integration: owning/generated surfaces.
- `bash scripts/run-quality.sh` redirected to a file — integration: local aggregate.
- A redirected slow selected gate records `START` and `WAIT` before the selected
  process finishes, while the final stdout summary remains the verdict.
- GitHub `Quality Core` readback on the repaired SHA — e2e, pending explicit push approval.

## Tripwires

- The selector still says `partial` or names either target as unmapped.
- The fail-before focused run does not name the old targets.
- Tests pass while focused coverage omits the entry script or either fallback.
- A review repair changes policy (a), CI scope, or a generated file before source
  sync.

## Implementation Evidence

- Mapper-only fail-before: the old-range final consumer returned 1 with
  `status: blocked` and named exactly entry lines 20, 63, 102, 106, 107, 122 and
  library lines 183, 184.
- Post-test focused coverage: the coverage JSON recorded all eight target lines
  as executed.
- Post-test final consumer: return 3, `status: unestablished`, `blocking: []`, and
  `changed_line_proof: unverified-dirty-worktree`; this is not a local aggregate
  pass.
- First clean-tree wrapper: the original eight targets were covered, and the
  final consumer exposed one new uncovered branch in the mapper repair itself
  (`scripts/suggest_mutation_coverage_command.py:152`). A test-only negative
  case exercised the unsupported callable shape.
- Final clean-tree proof: at `7cd421c4`, the exact old-range record shows its
  inner consumer returned 0: `consumer_returncode: 0`, `status: clean`,
  `blocking: []`, and no unmapped files. No separate shell-wrapper exit receipt
  is claimed. The branch verification lock also passed broad standing pytest
  and a fresh changed-line consumer over `origin/main..HEAD`.
- Hosted CI readback remains pending explicit push approval.
- Closeout operability follow-up: combined-stream gate logs previously remained
  empty until the first concurrent batch completed. The runner now reports the
  requested scope immediately and the queued check count/first/last labels
  before waiting. Its focused summary/runtime suites pass 66 tests; an
  independent read-only review found no blocker and its three evidence/test
  hardenings were applied.

## Follow-up Slice Carry-Forward

### 2026-08-12 continuation review

The local repair remains resolved: the current changed-line consumer maps and
covers every eligible changed file it can identify. The active lesson-ledger
slice ran that consumer twice; its final broad gate reported `blocking: []` and
`changed_line_proof: partial` solely because
`scripts/render_lesson_selection_preview.py` still has no standing-test mapping.
That is an explicit local coverage-scope gap, not evidence of a remote CI
regression. No push has been authorized, so this review neither refreshes nor
claims hosted CI readback. The next ordinary local slice may proceed while
preserving the remote-readback non-claim.

- User-directed follow-up: resolve `#577`, `#578`, and `#579`, which were found while
  measuring the repaired quality runner's code and test economics.
- Preserved interrupt: the remote changed-line seam remains locally resolved
  and hosted CI readback remains pending explicit push approval. This follow-up
  does not alter mapper policy, changed-line verdict logic, CI topology, or the
  remote non-claim.
- Current capability: timeout/drain behavior tests must prove containment
  without retaining escaped processes or paying production-scale deadlines;
  synthetic inventory tests must observe only their declared pytest temp root.
  Generated SLOC inventory must not measure its mutable runtime state or its
  own output, and must not exclude a different versioned file by glob suffix.
- Acceptance: the focused CLI-surface tests leave no owned escapee process and
  complete under injected test deadlines; the economics suite produces the
  same payloads against a fixture-owned temp root and no longer scans ambient
  retained sessions. Broad standing proof and issue closeout remain separate
  final gates.
- Result: the CLI module passes in 6.35s serial; every retry-owned holder is
  registered by its parent, ordinary group cleanup leaves no identity-matched
  running process, escaped holders acknowledge test-owned stop signals, and
  five repeated race runs leave no holder. Economics/discovery focus passes in
  2.00s under xdist against the fixture root. Critique round 2 caught the late
  PID-registration race; its repair is accepted-unreviewed under the two-round
  cap and remains covered by the repeated execution above.
  Clean-closeout rehearsal then reproduced SLOC self-contamination. Six focused
  tests now prove exact output identity, same-suffix preservation, literal
  metacharacters, and byte stability; its round-2 repair is accepted-unreviewed.
- Non-goals: pruning tests from counts alone, removing portability bootstrap
  shims, weakening local/CI mirror proof, changing runtime budgets, or claiming
  the still-unpushed hosted CI repair is green.

## Release-Stabilization Carry-Forward

- Operator direction: finish the release-blocker and P2 backlog selected in the
  active goal, then push and publish `v4.1.0` as one final bundle. This replaces
  the earlier sequence that released before the consumer-facing backlog.
- Preserved interrupt: the exact old-range selector and changed-line consumer
  remain a locked regression seam. Later slices may change other proof surfaces,
  but they must not alter mapper policy, shrink changed-line scope, or describe
  the hosted repair as green before GitHub reads the final pushed SHA.
- Recheck trigger: if a stabilization slice touches the selector, its readers,
  regenerable-facts entry/library coverage, or CI mirror topology, rerun the
  original-range mapper and final-consumer checks before ordinary closeout. If
  none of those surfaces changes, retain the committed `7cd421c4` local proof
  and keep hosted CI as the explicit final-release non-claim.
- Publication boundary: the user granted the final push and release for this
  bundle. Local implementation still precedes sync, verification, critique,
  version mutation, push, hosted-CI readback, and public/install readback in
  that order; an earlier local or push exit cannot satisfy a later boundary.

## Boundary Ownership

- `preserve`: the selector produces reachability evidence; it does not produce a
  coverage verdict.
- `preserve`: the tests produce executable observations; subprocess delivery
  checks and in-process branch checks have distinct proof roles.
- `preserve`: local and remote consumers own verdicts over their stated coverage
  inputs; neither may infer coverage from test-file existence.

## Critique

- Interrupt Source: remote-ci-changed-line-reconciliation
- Seam Summary: local focused test selection and coverage -> local aggregate -> GitHub broad changed-line mirror.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the original range, exact missing lines, selector blind
  spot, final-consumer disagreement, and fail-before tripwire are all bound.
- What Disproving Observation Is Resolved: a passing standing test is not proof
  that the selector can discover it or that coverage observes its subprocess.
- Fresh-Eye Review: two bounded rounds before final coverage production.
- Carry-forward refresh (2026-08-12): the lesson-ledger/graduation-state slice
  is allowed to proceed because it does not touch the selector, its readers,
  regenerable-facts coverage, or CI topology. The hosted-CI readback remains a
  pending external proof and is not claimed by that local slice.

## Canonical Artifact

- `charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md`

## First Implementation Slice

Add the bounded loader-token recognizer and its positive/negative selector
fixtures. Run the exact old range to capture the local blocker. Then import the
regenerable-facts entry script in-process, drive the six entry branches and two
git-fallback lines, and rerun the same selector and focused final consumer.
