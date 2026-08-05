# Issue #505 resolution critique — focused coverage export

Date: 2026-08-06
Scope: `scripts/prepush_focused_changed_line_coverage.py`,
`scripts/mutation_coverage_producer.py`, `scripts/mutation_sampling_lib.py`,
their plugin mirrors, and focused regression tests.

## Resolution question

Does narrowing only the coverage JSON export to mapped changed mutation-pool paths
make the local focused proof actionable without changing test selection, changed-line
verdict semantics, freshness trust, unmapped-file policy, or broad closeout coverage?

## Fresh-eye review

- Round 1, named lens `coverage-scope-integrity`: parent-delegated Codex reviewer
  `019fd43e-7a6a-7841-916c-889d5c2673b9` found one blocker. Repeating
  `coverage json --include` retains only the last path under the installed
  coverage.py CLI, so a multi-file change could falsely block earlier covered files.
  Boundary window `issue505-quality-export-r1` verified clean.
- Repair: use one comma-separated `--include` argument and add a regression that
  asserts both paths survive in the final coverage argv.
- Round 2, named lens `coverage-argv-compatibility`: parent-delegated Codex reviewer
  `019fd442-5bb6-7932-aaa5-4b51d0f9afa5` reviewed the repaired surface and returned
  clean. It confirmed empty/one/multiple paths, mapped/unmapped semantics, freshness,
  broad unfiltered callers, source/plugin parity, and `57 passed`. Boundary window
  `issue505-quality-export-r2` verified clean.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`, `reasoning_effort=medium`,
  `service_tier=priority`, `fork_context=false`.
- Host exposure state: `requested_fields_sent`
- Application state: not exposed; no applied claim is made.
- Delivery state: findings-received for both rounds.

## Verdict

Resolution accepted. The focused pytest workload and consumer verdict path remain
unchanged. Only JSON serialization is filtered to the mapped changed files; the
freshness fingerprint still covers the full changed mutation pool, unmapped files
remain explicit partial/unproven results, and broad closeout callers do not pass a
filter.

Measured same-data export evidence: full JSON `9.54s` / `6,746,080` bytes versus
four-path filtered JSON `0.31s` / `34,158` bytes. The clean focused lane returned
`0` with `4/4` changed pool files analyzed.

## Boundary Ownership

- Producer: `prepush_focused_changed_line_coverage.py` selects mapped files and
  passes them to the export producer; `mutation_sampling_lib.py` owns coverage
  serialization.
- Consumer: `check_changed_line_mutation_coverage.py` owns the changed-line verdict
  and still receives the same mapped-file limits and freshness marker.
- Owning surface: the local pre-push mutation proof boundary owns this optimization;
  broad closeout remains with the unfiltered producer.
- Verdict: owned-correctly.

## Boundary and non-claims

- Local deterministic proof only; no remote CI, installed plugin, provider, public
  behavior, release tag, or Cautilus claim is made here.
- This does not weaken changed-line coverage, mutate selection, broad closeout
  coverage, or the final `run-quality.sh --read-only` gate.
- Existing `CoverageWarning` output about the sitecustomize file remains an advisory
  runtime signal; it did not alter the consumer verdict.

## Reviewer satisfaction

Fresh-eye satisfaction: parent-delegated. Both returned results were read by the
parent and immediately followed by clean boundary verification; no same-agent
substitute was used.
