# Quality Review
Date: 2026-07-14
Title: v1.0.5 Advisory Disposition and Release Readiness

## Scope

Target boundary: advisories surfaced while closing issues #433, #436, and #437,
plus Cautilus 0.19.3 compatibility discovered by the release gate.

Ambient repo findings: nine Python length warnings remain advisory after a
cohesion/risk review; no public command, skill trigger, or release API changes.

## Current Gates

- Focused split-module and Cautilus suite: 138 passed; Ruff and the boundary
  ratchet pass.
- Full read-only quality passed 81/81 gates and 4,587 tests after sync.
- Release critique passed; release-gate proof and a distinct post-publish
  observation remain mandatory.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: release quality 72.1s latest / 73.7s median; read-only
  quality 55.5s / 60.5s; pytest 35.7s / 48.1s.
- coverage gate: focused coverage and boundary checks pass; full read-only
  quality passed 81/81 gates and 4,587 tests.
- evaluator depth: deterministic gates and installed Cautilus final consumers;
  no Cautilus evaluation was run because the change is a CLI wire-contract fix.

## Healthy

- Cautilus stdout parsers now select JSON explicitly, and command-shape tests
  guard both live consumers.
- Three large test matrices were split without changing production behavior or
  assertions, reducing Python length warnings from 12 to 9.
- New file-qualified boundary keys have reasoned, revisit-bounded exemptions;
  the candidate count remains neutral.
- A real installed Claude CLI honored an isolated custom HOME during doctor.

## Weak

- The manually dispatched mutation workflow passed at 89.0% Python and 93.0%
  JavaScript, but proves commit `c6a1e828`, not the unreleased cleanup HEAD; it
  remains provider evidence for #437 rather than a release-HEAD claim.

## Missing

- None within the patch-release acceptance boundary once the release gate and
  public post-create verification pass.

## Deferred

- `check_skill_surface_preflight.py` and `validate_critique_artifacts.py` show
  genuine production accretion, but refactoring 479/480-line contract validators
  during a release would create more risk than the advisory removes.
- Seven other warned modules remain cohesive command/planner/test-support units;
  splitting them would add shallow coordination surfaces without behavioral gain.

## Advisory

- structural review result: inventory `inventory_skill_ergonomics.py` reported
  `scope_status=scanned`, `checked_skill_count=21`,
  `heuristic_finding_count=16`, and `host_surface_reference_count=74`; all 74
  references are adapter/integration contexts (37 compatibility, 4 mapping, 6
  detector, 25 named-host integration, 2 policy fixture). No core is overfilled.
- prose review result: evidence from manual judgment after
  `prose_review_status=required`; trigger boundaries, progressive disclosure, helper
  ownership, path clarity, issue anchors, dated incidents, and reference
  discoverability produced no actionable finding; host names remain on their
  owning portable adapter/integration surfaces.
- Python length advisory: command: `check_python_lengths.py`; nine warnings
  remain by deliberate disposition; three
  low-risk test matrices were split, while seven cohesive modules and two
  high-risk validators were not churned for line-count compliance alone.
- mutation advisory: evidence: provider run 29289933683 passed against
  `c6a1e828` (Python 89.0%, 118/118 executed; JavaScript 93.0%, 86 reachable);
  it is an evidence-channel observation, not a substitute for committed-HEAD gates.

## Delegated Review

- Delegated Review: executed — distinct operational sequencing and operator-
  communication reviewers plus a separate counterweight passed; all three
  reviewer-boundary fingerprint verifies reported no drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  not re-delegated because no gate topology or runtime recommendation changes.

## Commands Run

- `inventory_skill_ergonomics.py --summary` and Python length inventory/review.
- focused pytest for split matrices and both installed Cautilus consumers.
- `check_boundary_bypass_ratchet.py`, Ruff, debug/spec validators, and sync tools.
- isolated-home `charness doctor` through the installed Claude CLI.
- GitHub Actions mutation workflow run 29289933683 and its score summary.

## Recommended Next Quality Moves

- active release proof — capability_needed=public patch confidence;
  next_center=full gate plus release critique; transformation=sync, verify,
  publish, and read back through a distinct channel; proof_boundary=public tag
  and release artifact; enforcement_posture=existing-gate-reuse.
- passive validator decomposition because line count alone does not justify
  release-slice churn — capability_needed=safer cohesive validators;
  next_center=the two near-limit production validators; transformation=refactor
  only alongside behavior work with characterization tests; proof_boundary=full
  quality plus mutation proof; enforcement_posture=no-gate because line count
  alone does not justify release-slice churn.

## History

- [Open issue resolution proof](history/2026-07-14-open-issue-resolution-proof.md)
- [pytest suite test-value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
