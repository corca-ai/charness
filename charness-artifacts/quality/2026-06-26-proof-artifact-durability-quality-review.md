# Quality Review
Date: 2026-06-26

## Scope

Target artifact: `charness-artifacts/quality/2026-06-26-public-skill-dogfood-resolver-speed-quality-review.md`.

Ambient repo findings: broad non-release pytest found one proof-durability
failure caused by the runtime-source marker living on the continuation line
after a gitignored `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
citation.

## Current Gates

- Focused durability test passed after the marker placement repair.
- Full durability script passed across the current repo docs.
- The repaired quality artifact validated.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`, plus broad pytest duration output
  from the failing `test_real_repo_passes` run before this repair.
- runtime hot spots: broad non-release pytest reported the durability test at
  2.00s and exposed the proof bug before final closeout.
- coverage gate: focused durability pytest, full durability script, and quality
  artifact validation passed.
- evaluator depth: deterministic proof contract only; no evaluator-backed
  behavior was in scope.
- runtime interpretation: this is a correctness repair for a proof artifact,
  not a script-speed improvement.

## Healthy

- The gitignored runtime metrics citation is now explicitly marked as a
  reproduction source on the same line.
- `check_spec_evidence_durability.py` accepts the repaired artifact.

## Weak

- The earlier quality artifact validator did not catch same-line marker
  placement for gitignored citations; the broader durability gate caught it.

## Missing

- Missing before this slice: proof artifact durability was not rechecked after
  writing the dogfood resolver-speed quality artifact.

## Deferred

- Consider adding a targeted post-artifact closeout check for durability when
  quality artifacts cite `.charness/` runtime files.

## Advisory

- failure command: broad non-release pytest failed at
  `tests/quality_gates/test_check_spec_evidence_durability.py::test_real_repo_passes`
  because `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  was cited without a same-line marker.
- repair command: `python3 scripts/check_spec_evidence_durability.py --repo-root .`
  passed across 223 docs after the marker move.

## Delegated Review

- Delegated Review: not_applicable — proof-artifact marker placement repair with
  direct failing gate reproduction.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through the broad failure and focused durability
  rerun.

## Commands Run

- `pytest -q tests/quality_gates/test_check_spec_evidence_durability.py::test_real_repo_passes`
- `python3 scripts/check_spec_evidence_durability.py --repo-root .`
- `python3 - <<'PY' ... validate_quality_artifact(...) ... PY`

## Recommended Next Gates

- active none because the failing durability path now passes.
- passive because this was found by broad pytest: keep final closeout broad
  non-release/read-only proof before push or release.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
