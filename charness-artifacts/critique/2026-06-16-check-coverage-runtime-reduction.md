# Check Coverage Runtime Reduction Critique

## Execution

Fresh-eye code critique executed for the test-speed slice before final closeout.
Target reference: `code-critique`.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

charness-artifacts/critique/2026-06-15-203922-packet.md

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `requested_fields_sent`
- **Application state**: `unverified-by-host`

## Diff Scope

`scripts/check_coverage.py` narrows `trace.Trace` to repo-relevant files by
ignoring Python runtime directories and drops generated `reports/` from repo-copy
fixtures. Tests pin generated-report exclusion, tracer ignoredirs wiring,
runtime-dir collection, site API exception handling, and the repo-under-runtime
guard.

## Findings

- Michael Jackson angle: no `Act Before Ship`; the diff solves the named
  test-speed problem rather than an adjacent cleanup. `reports` exclusion in
  `tests/repo_copy.py` is adjacent but cheap and same-class.
- Gerald Weinberg angle: no `Act Before Ship`; the measured 38.2s to 16.6s drop
  plus empty coverage JSON diff supports the tracer overhead as a real cause.
  Reviewer requested a repo-under-runtime guard; implemented.
- Atul Gawande angle: no `Act Before Ship`; reviewer requested direct helper
  tests for `python_runtime_ignoredirs()` and site getter exception behavior;
  implemented.

## Counterweight Triage

- `Act Before Ship`: none.
- `Bundle Anyway`: helper tests and repo-under-runtime guard; completed before
  closeout.
- `Over-Worry`: adding a hard runtime threshold for `check-coverage`; too flaky
  for this local machine-dependent gate.
- `Valid but Defer`: centralize duplicate ignore lists later if copy-ignore
  drift recurs; handle intentional checked-in `reports/` fixtures only when such
  a fixture exists.

## Structured Findings

- runtime-helper-tests | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_check_coverage_inventory.py | action: fix | note: Direct helper tests now pin runtime dir collection, site getter exception handling, and repo-parent filtering.
- duplicate-ignore-lists | bin: valid-but-defer | evidence: moderate | ref: scripts/check_coverage.py | action: defer | note: Centralization is valid but not needed for this speed slice; revisit if copy-ignore drift recurs. | follow-up: deferred copy-ignore-centralization

## Defect Class Cross-Link

No direct repeat trap matched. The closest operational lesson is
`charness-artifacts/retro/recent-lessons.md`: keep final proof concrete when a
clean or partially synced tree changes what closeout can prove.

## Capability Gap

None.

## Pre-Merge Action

No blocker remains from critique. Keep sync-before-verify order and rerun full
read-only quality after artifacts and plugin mirror changes are locked.

## Deliberately Not Doing

No hard timing assertion is added; runtime thresholds would be noisy. The
existing runtime signal recorder remains the standing evidence path.
