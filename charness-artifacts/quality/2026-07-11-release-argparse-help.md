# Quality Review
Date: 2026-07-11

## Scope

Target boundary: the single operator-facing release run planner; exactly eight
`argparse_missing_help` findings. No release mutation or publication is in scope.

Ambient repo findings were not repaired. The manual Cautilus update advisory
remains outside this deterministic help-only slice.

## Current Gates

- `inventory_skill_ergonomics.py` reports missing `help=` strings advisory-first.
- Focused planner tests, live `--help`, Ruff, py_compile, mirror comparison, and
  existing release planner behavior tests own deterministic proof.

## Runtime Signals

- runtime source: timing capture is missing for this help-only slice.
- runtime hot spots: none investigated.
- coverage gate: verification-lock standing pytest and focused mutation
  coverage producer are the final closeout boundary.
- evaluator depth: deterministic gates only because no prompt or agent-behavior
  contract changed.

## Healthy

- All eight descriptions stay with the existing parser owner while required
  state, defaults, choices, mutual exclusion, plan schema, and behavior remain
  unchanged.
- Help explicitly distinguishes read-only planning from irreversible publish.
- Public source and packaged plugin mirror are byte-identical; option-scoped
  tests tolerate argparse wrapping.

## Weak

- Repo-wide argparse missing-help debt remains 43 findings after this package;
  the advisory count is a selection prompt, not a blocking floor.

## Missing

- none for this target — the planner now explains every option with focused
  executable readback.

## Deferred

- Other skill packages wait for cohesive owner-level slices.
- Cautilus stays unrun because deterministic help proof is sufficient and repo
  policy requires asking before evaluator execution.

## Advisory

- structural review result: command: `inventory_skill_ergonomics.py --summary`;
  capability_needed=release operators understand planner inputs without
  confusing planning with publication; sequencing applies as inventory ->
  single-file package -> proof; current center is `plan_release_run.py` and its
  mirror; next center is gather's single-file four-option planner;
  transformation=help strings plus option-scoped readback; proof_boundary=eight
  mappings and the release planner suite; enforcement_posture=no-gate.
- prose review result: artifact:
  `charness-artifacts/critique/2026-07-11-release-argparse-help-critique.md`;
  fresh-eye corrected four overstatements at the irreversible boundary and
  approved the revised wording.
- command: `inventory_skill_ergonomics.py --summary` measured 51 findings before
  and 43 after, with release moving 8 -> 0.

## Delegated Review

- Delegated Review: executed — a lower-power worker implemented the package;
  an independent read-only reviewer caught boundary wording and approved the
  corrected delta with zero worktree/index drift.
- Slow-gate lenses `fixture-economics`, `parallel-critical-path`, and
  `duplicated-proof` were not re-delegated because broad-gate economics and
  runtime performance are outside this help-only slice.

## Commands Run

- Skill-ergonomics JSON/summary; planner `--help`; 22 focused planner tests;
  Ruff; py_compile; mirror comparison; `git diff --check`; final locked
  standing pytest and focused mutation coverage.

## Recommended Next Quality Moves

- active gather-help-package — capability_needed=gather operators understand
  one planner's four inputs; next_center=`gather_plan.py`;
  transformation=bounded help/readback slice; proof_boundary=package inventory
  plus focused help and behavior tests; enforcement_posture=no-gate.
- passive scattered-quality-help because its 23 findings span ten files —
  capability_needed=discoverable quality helper CLIs; next_center=deferred
  owner-level clusters; transformation=none; proof_boundary=current inventory;
  enforcement_posture=advisory.

## History

- [Archived quality review](history/2026-06-16-quality-review.md)
