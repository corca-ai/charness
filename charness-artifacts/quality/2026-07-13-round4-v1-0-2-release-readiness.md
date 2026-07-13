# Quality Review
Date: 2026-07-13
Title: Round 4 v1.0.2 Release Readiness

## Scope

Target boundary: `v1.0.1..HEAD` before the release mutation: issue-plan local
misuse ordering, aggregate runtime-test economics, Codex cache update-test
economics, and the lifecycle evidence that binds those slices.

Ambient repo findings: Python warn bands, broad nested-CLI counts, stale timing
labels, and skill host-reference heuristics were reviewed as advisories. They
are not regressions introduced by this delta.

## Current Gates

- The final-head `./scripts/run-quality.sh --read-only` run passed every emitted
  phase; secrets, supply-chain, packaging, skill, mirror, and artifact checks
  were green.
- Focused behavior passed: 48 issue tests in 3.49s; aggregate recorder tests 6
  in 5.81-5.92s; Codex cache tests 6 in 14.02s on the parent confirmation run.
- Maintainer-Local Enforcement: healthy — `.githooks/pre-push` owns the
  repo-quality gate and `validate_maintainer_setup.py` confirmed this clone.

## Runtime Signals

- runtime source: structured metrics from
  `.charness/quality/runtime-signals.json`, <!-- reproduction-source --> rendered by
  `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 144.2s latest / 61.9s median
  against 90s; `pytest` 106.4s / 52.4s against 140s; full-release 77.4s /
  75.6s unbudgeted. The 144.2s latest sample is the instrumented diagnostic
  run, not evidence of a standing regression; the median remains the decision
  signal.
- coverage gate: the read-only quality run passed; exact clean-HEAD mutation
  and broad coverage remain owned by the final verification lock.
- evaluator depth: deterministic gates only. Cautilus was not run because repo
  policy is ask-before-run; the issue ordering change has direct no-call proof
  and no routing, causal-review, or feature-brief contract change.

## Healthy

- Concept: invalid local `issue resolve --target` usage is rejected by the
  argument owner after adapter-shape validation and before provider readiness.
- Behavior: exact rc/error and three no-call sentinels prove the issue fix;
  invalid-adapter precedence and valid paths remain covered.
- Testability: aggregate tests keep direct recorder coverage while replacing repeated process launches with a contract-shaped spy.
- Testability: the Codex cache file retains real update wiring, official
  app-server refresh, and actual rotation/staleness assertions in one smoke;
  only stable/diff transformations moved to pure helpers.
- Security/portability: secrets and manifest-only supply-chain checks passed;
  public issue source and installed plugin mirror are byte-identical.

## Weak

- Twelve ambient Python files remain in advisory length bands. No touched
  production file entered a band; the signal does not establish incohesion.
- The economics inventory reports `test_file_count=387`,
  `nested_cli_file_count=164`, and
  `nested_cli_standing_or_mixed_file_count=163` (150 standing plus 13 mixed;
  one all-release-only file). Two measured duplicate-cost families were
  repaired, but the counts alone cannot identify which remaining smokes fail
  to earn their isolation cost.
- The structured latest read-only aggregate is an instrumented 144.2s outlier
  above its 90s budget. Its 61.9s recent median and subsequent passing direct
  run do not justify a new gate or budget change; keep observing.

## Missing

- none for the local release candidate. Public release visibility,
  fresh-checkout behavior, unauthenticated content readback, and maintainer
  install refresh remain provisional until the publication boundary executes.

## Deferred

- Managed-install serial scenarios remain a measured test-economics candidate;
  changing them safely needs a separate boundary map, not this release lock.
- Issues #433 and #436 remain open and untouched by explicit goal boundary.
- Six stale component timing labels remain outside the release decision; their
  standing owners should refresh them when those components next change.

## Advisory

- structural review result: command: `plan_quality_run.py` — the weak capability
  was fast, local, behavior-bearing feedback. Existing argument owners and pure
  helpers were the right centers; the move was interface narrowing/test-layer
  relocation with focused proof, `enforcement_posture=existing-gate-reuse`.
- prose review result: command: `inventory_skill_ergonomics.py --summary`
  reported `scope_status=scanned`, `finding_status=heuristics_present`, and
  `prose_review_status=required`; this paragraph supplies the required prose
  judgment. It checked `checked_skill_count=21` and found
  `heuristic_finding_count=16`, with `host_surface_reference_count=74` but zero
  core overfill, option pressure, ritual, path ambiguity, incident/date,
  reference-discoverability, or argparse-help findings. The references are
  intentional adapter/integration/host-policy vocabulary; no trigger or
  progressive-disclosure defect was observed in the changed `issue` package.
- command: `inventory_structural_waste.py --summary` inspected
  `python_source_count=299` across `command_snippet_count=12`, with
  `broad_scanner_candidates=[]` and `duplicate_discovery_candidates=[]`. No
  additional cleanup is admitted from that lens.

## Delegated Review

- Delegated Review: executed — lower-power workers implemented bounded coding
  slices; fresh-eye reviewers approved the frozen diffs. Reviewer-boundary
  fingerprints proved zero drift for accepted reviews; one overlapping Codex
  cache review was quarantined and contributes no approval.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): executed — measured runtime/process fan-out admitted two
  cheaper-layer moves and deferred managed-install work where boundary proof
  was not yet narrow enough.

## Commands Run

- `./scripts/run-quality.sh --read-only`; `./scripts/check-secrets.sh`;
  `python3 scripts/check_supply_chain.py --repo-root .`.
- Focused issue, runtime-aggregate, direct-recorder, and Codex cache pytest
  commands with same-command before/after timings recorded in the goal.
- `render_runtime_summary.py --json`, `inventory_skill_ergonomics.py --summary`,
  `inventory_standing_test_economics.py --json`,
  `inventory_structural_waste.py --summary`, and
  `validate_maintainer_setup.py --repo-root .`.

## Recommended Next Quality Moves

- active bind confidence to the exact release bytes — capability_needed=honest
  publication confidence; next_center=verification/release boundary;
  transformation=gate-reuse; proof_boundary=clean HEAD mutation coverage,
  broad pytest, fresh checkout, public HTTPS readback, and installed doctor;
  enforcement_posture=existing-gate-reuse.
- passive review the next measured managed-install duplicate boundary because
  current counts do not identify a safe deletion — capability_needed=faster
  local feedback; next_center=one measured scenario family;
  transformation=defer-watch; proof_boundary=same-command timing plus retained
  real install/update smoke; enforcement_posture=no-gate because no additional
  candidate is yet causally established.

## History

- [pytest suite test-value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
