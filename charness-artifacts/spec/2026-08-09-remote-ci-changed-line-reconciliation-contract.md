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
- GitHub `Quality Core` readback on the repaired SHA — e2e, pending explicit push approval.

## Tripwires

- The selector still says `partial` or names either target as unmapped.
- The fail-before focused run does not name the old targets.
- Tests pass while focused coverage omits the entry script or either fallback.
- A review repair changes policy (a), CI scope, or a generated file before source
  sync.

## Implementation Evidence

- Mapper-only fail-before: the old-range final consumer exited 1 with
  `status: blocked` and named exactly entry lines 20, 63, 102, 106, 107, 122 and
  library lines 183, 184.
- Post-test focused coverage: the coverage JSON recorded all eight target lines
  as executed.
- Post-test final wrapper: exit 3, `status: unestablished`, `blocking: []`, and
  `changed_line_proof: unverified-dirty-worktree`; this is not a local aggregate
  pass. Post-commit wrapper proof remains pending.

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

## Canonical Artifact

- `charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md`

## First Implementation Slice

Add the bounded loader-token recognizer and its positive/negative selector
fixtures. Run the exact old range to capture the local blocker. Then import the
regenerable-facts entry script in-process, drive the six entry branches and two
git-fallback lines, and rerun the same selector and focused final consumer.
