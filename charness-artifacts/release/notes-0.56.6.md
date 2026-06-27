# Charness 0.56.6

This patch release adds a focused changed-line mutation coverage producer helper
and repairs broad pytest proof scoping for `run_slice_closeout.py --base`.

## Operator Impact

- When changed-line mutation coverage is stale, run:
  `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --json`
- If the payload returns `status: "recommended"` or `status: "partial"`, pass
  the emitted `command` to `run_slice_closeout.py --mutation-coverage-command`.
- If the payload is `missing` or lists unmapped changed files, use the broad
  mutation coverage producer fallback.

## Verification

- Full pre-push quality passed: `79 passed, 0 failed`.
- Changed-line coverage consumer passed for `origin/main..0c462fea`.
- Focused coverage producer for the final commit range ran 169 tests in 31.1s,
  instead of instrumenting the full standing pytest suite.
- Fresh-checkout probes passed: `./charness --help`, `./charness goal check --help`,
  and `python3 scripts/doctor.py --repo-root . --json --skip-release-probe`.

## Update

Run `charness update` to install the latest published Charness release.
