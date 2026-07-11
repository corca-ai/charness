# Quality Review
Date: 2026-07-11

## Scope

Target boundary: the three operator-facing retro telemetry, planning, and
packet CLIs; exactly 11 `argparse_missing_help` findings.

Ambient repo findings were not repaired. The Cautilus 0.18.0 to 0.19.1 manual
update advisory remains outside this deterministic help-only slice.

## Current Gates

- `inventory_skill_ergonomics.py` reports missing `help=` strings advisory-first.
- Focused subprocess `--help` tests, Ruff, py_compile, mirror comparison, and
  existing retro behavior tests own this package's deterministic proof.

## Runtime Signals

- runtime source: timing capture is missing for this small help-only slice.
- runtime hot spots: none investigated.
- coverage gate: verification-lock standing pytest and focused mutation
  coverage producer are the final closeout boundary.
- evaluator depth: deterministic gates only because no prompt or agent-behavior
  claim changed.

## Healthy

- All 11 descriptions stay with the existing parser owners while option names,
  types, defaults, destinations, and packet-selection behavior remain unchanged.
- Public sources and packaged plugin mirrors are byte-identical.
- Option-scoped tests tolerate argparse wrapping and bind each option to a
  distinctive help fragment.

## Weak

- Repo-wide argparse missing-help debt remains 51 findings after this package;
  the advisory count is a selection prompt, not a blocking floor.

## Missing

- none for this target — all three direct entrypoints expose meaningful help
  with focused executable readback.

## Deferred

- Other skill packages wait for their own cohesive ownership slice.
- Cautilus update remains deferred because no evaluator was needed and machine
  tool installation was not authorized.

## Advisory

- structural review result: command: `inventory_skill_ergonomics.py --summary`;
  capability_needed=retro operators understand telemetry, planning, and packet
  controls from `--help`; sequencing applies as inventory -> package -> proof;
  current centers are the three parsers and their mirrors; next center is the
  release planner's single-file cluster; transformation=help strings plus
  option-scoped readback; proof_boundary=11 mappings and focused behavior tests;
  enforcement_posture=no-gate.
- prose review result: artifact:
  `charness-artifacts/critique/2026-07-11-retro-argparse-help-critique.md`;
  fresh-eye found exact mirror parity, preserved parser contracts, and faithful
  option-scoped tests with no actionable finding.
- command: `inventory_skill_ergonomics.py --summary` measured 62 findings before
  and 51 after, with retro moving 11 -> 0.

## Delegated Review

- Delegated Review: executed — a lower-power worker implemented the bounded
  package and a separate read-only child reviewer inspected source, mirrors,
  parser contracts, tests, and live help; no actionable finding remained.
- Slow-gate lenses `fixture-economics`, `parallel-critical-path`, and
  `duplicated-proof` were not re-delegated because broad-gate economics and
  runtime performance are outside this help-only slice.

## Commands Run

- Skill-ergonomics summary; all three `--help` commands; 33 focused retro tests;
  Ruff; py_compile; mirror comparison; `git diff --check`; verification-lock
  standing pytest plus focused mutation coverage.

## Recommended Next Quality Moves

- active release-help-package — capability_needed=release operators understand
  planner inputs; next_center=the eight-finding single-file release planner;
  transformation=bounded help/readback slice; proof_boundary=package inventory
  plus focused help and behavior tests; enforcement_posture=no-gate.
- passive remaining-help-debt because scattered findings still need cohesive
  owner-level triage — capability_needed=discoverable helper CLIs;
  next_center=deferred owner-level packages; transformation=none;
  proof_boundary=current inventory only; enforcement_posture=advisory.

## History

- [Archived quality review](history/2026-06-16-quality-review.md)
