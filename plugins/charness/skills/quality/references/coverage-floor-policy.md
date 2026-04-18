# Coverage Floor Policy

Use `coverage_floor_policy` when a repo already keeps per-file coverage floors
or is clearly drifting toward them.

The adapter should own the thresholds and discovery paths. The public skill
should own the discipline:

- enumerate the current source inventory before reading the prior artifact
- cross-check that inventory against declared floors and exemptions
- keep a warn band visible so high-coverage unfloored files do not silently
  drift downward
- detect contradictions such as a file being both floored and exempted
- detect operational drift between discovered quality-gate scripts and what
  lefthook / CI actually run

Portable defaults:

- `min_statements_threshold: 30`
- `fail_below_pct: 80.0`
- `warn_ceiling_pct: 95.0`
- `floor_drift_lock_pp: 1.0`
- `exemption_list_path: scripts/coverage-floor-exemptions.txt`
- `gate_script_pattern: "*-quality-gate.sh"`
- `lefthook_path: lefthook.yml`
- `ci_workflow_glob: .github/workflows/*.yml`

Interpretation:

- `min_statements_threshold` is lower than a large-file heuristic on purpose;
  boundary modules often sit in the 30-100 statement band.
- `fail_below_pct` catches unfloored files that are already weak enough to need
  action now.
- `warn_ceiling_pct` keeps very healthy but unfloored files visible as
  promotion candidates.
- `floor_drift_lock_pp` is a promotion hint, not proof by itself. Use it to
  recommend raising stale floors after real improvements land.

Reference implementations live next to this document:

- [coverage-floor-inventory.py](./coverage-floor-inventory.py)
- [coverage-floor-exemptions.txt](./coverage-floor-exemptions.txt)
- [validate-spec-pytest-references.py](./validate-spec-pytest-references.py)
