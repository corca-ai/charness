# Quality Review
Date: 2026-07-14
Title: Open Issue Resolution Proof

## Scope

Target boundary: issue-resolution validation for #433, #436, and #437; current
mutation is test-only and production behavior for #433/#436 landed earlier.

Ambient repo findings: skill-ergonomics inventory reports host-surface lexical
heuristics across 16 skills; no skill package changed, so those findings are
ambient and not remediation candidates for this slice.

## Current Gates

- GitHub source reads included every issue comment before classification.
- Five focused existing behavior tests cover the #433 carrier consumer and
  #436 dirty-sync, clean-sync, and sync-failure paths.
- Twenty-six focused tests cover #437's custom-HOME and parser/mutation seams.
- The repo mutation coverage producer, not a naive coverage run, reaches every
  changed-line target named in #437.
- A targeted Cosmic Ray session over `scripts/capability_catalog.py` kills all
  five `required=True` mutants and one reported dispatch comparison.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: release quality 72.1s latest / 73.7s median; read-only quality 55.5s / 60.5s; pytest 35.7s / 48.1s.
- coverage gate: focused producer passed; final repo closeout remains pending at artifact author time.
- evaluator depth: deterministic gates only; Cautilus is neither needed for these executable seams nor authorized on demand.

## Healthy

- Existing release and verification-lock floors remain unchanged.
- The #437 fix adds narrow non-release proof instead of moving slow release-only
  fixtures into the standing command or weakening mutation thresholds.
- Reviewer-boundary snapshots verified clean after two angles and one separate
  counterweight pass.

## Weak

- No fresh scheduled/provider mutation run exists for the patch. Targeted
  outcomes prove the reported survivor delta, not future sample selection.

## Missing

- None within the issue acceptance boundaries after final closeout runs.

## Deferred

- A real Claude custom-HOME host roundtrip remains unclaimed; fake-CLI and
  final-consumer proof are the local contract for this test-only slice.
- The next scheduled mutation run remains monitoring evidence, not a blocker.

## Advisory

- structural review result: capability needed is early, consumer-reachable proof; current centers are issue-owned carrier validation, sync-phase stopping, mutation coverage, and focused tests; the next center is the issue-specific carrier; use existing gates with no new floor. Evidence artifact: `charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-critique.md`.
- prose review result: no public skill prose changed; trigger boundaries and progressive disclosure are out of target, while helper ownership remains with production and proof ownership with tests. Evidence command: `git diff --name-only`.
- skill ergonomics advisory: `inventory_skill_ergonomics.py --summary` found only ambient host-surface lexical heuristics for this slice.

## Delegated Review

- Delegated Review: executed — `problem-framing-and-legibility`, `diagnostic-boundary-and-operations`, and separate `counterweight` lenses; verdict requires issue-specific proof mapping and no production expansion.
- Slow-gate lenses: `fixture-economics`, `parallel-critical-path`, and `duplicated-proof` were not re-delegated because no slow-gate scope change or runtime recommendation is proposed; #436 reuses its existing executor behavior proof.

## Commands Run

- `issue_tool.py read` for #433, #436, and #437.
- focused pytest for five existing #433/#436 cases and 26 #437 cases.
- `mutation_sampling_lib.run_test_coverage` with the non-release focused command.
- targeted Cosmic Ray baseline/init/exec/dump for `scripts/capability_catalog.py`.
- quality runtime summary and skill-ergonomics summary inventories.
- reviewer-boundary snapshot/verify around every delegated reviewer.

## Recommended Next Quality Moves

- active carrier mapping — capability_needed=issue readers can distinguish landed behavior from current proof; next_center=issue-specific closeout carriers; transformation=record JTBD, exact proof, critique, and non-claims; proof_boundary=`validate-closeout-draft` plus post-push `verify-closeout`; enforcement_posture=existing-gate-reuse.
- passive scheduled observation — capability_needed=future sample monitoring; next_center=scheduled mutation workflow; transformation=observe the next automatic run without delaying this focused fix; proof_boundary=provider run artifact; enforcement_posture=no-gate because current targeted proof already settles the reported fixed sample.

## History

- [pytest suite test-value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
