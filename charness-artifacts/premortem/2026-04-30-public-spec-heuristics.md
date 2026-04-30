# Public Spec Heuristics Premortem

## Decision

Ship the #84 public-spec quality heuristic fix as one complete slice:
section-aware exemptions, implementation-reference density, pointer-spec
recognition, adapter configuration, bootstrap support, tests, and plugin export.

## Fresh-Eye Satisfaction

parent-delegated

## Angles

- Correctness and completeness: initial review found unexempt headings were
  accidentally skipped; fixed with heading-scan regression coverage. Re-review
  reported no blockers or advisories.
- Adapter/bootstrap/export compatibility: found that inventory should fail on
  invalid quality adapters instead of silently using defaults; fixed with a
  non-zero invalid-adapter path and regression coverage.
- Counterweight: Cautilus validation is over-worry for this deterministic
  quality heuristic change; local validators and focused tests are sufficient.

## Counterweight Triage

- Act Before Ship: fixed before closeout.
- Bundle Anyway: source changes, adapter docs/defaults, tests, and synced
  plugin export belong in the same commit.
- Over-Worry: Cautilus proof/eval validation for this issue.
- Valid But Defer: future calibration of the default density floor or extra
  default exempt headings remains adapter-tunable.

## Verification

- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 scripts/validate_adapters.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
