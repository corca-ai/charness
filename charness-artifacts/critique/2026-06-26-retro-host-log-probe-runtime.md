# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts six `probe_host_logs.py` subprocess
tests to in-process `main()` calls while retaining representative real CLI
coverage.

## Failure Angles

- Boundary proof: converting all calls could remove the only proof that the
  script boots correctly through `skill_runtime_bootstrap.py`.
- Argument surface: converting `--goal-path`, `--repo-root`, or
  `--claude-session-file` paths could hide argparse or path-expansion problems.
- Isolation: monkeypatched `sys.argv` and captured stdout could leak between
  tests if not pytest-scoped.
- Value: a count-only improvement would be weak if it traded away a meaningful
  external process boundary.

## Counterweight Pass

- Three real subprocess CLI smokes remain: basic `--home`, goal-window
  `--repo-root --goal-path`, and named `--claude-session-file`.
- The converted tests still exercise `parse_args()`, `build_payload()`, stdout
  JSON rendering, and return-code handling through `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.
- Fresh-eye review found no materially weakened CLI/argument proof.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_retro_host_log_probe.py | action: fix | note: duplicate subprocess calls dropped from 9 to 3 while retaining representative CLI bootstrap and option-family proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_startup_probe_measure.py | action: defer | note: timeout-focused startup probe tests depend on real process behavior and should not be collapsed in this slice

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_context=true, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: reviewer completed and returned no findings

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f0173-450d-7fc0-bc2e-9cdc55de4774`
completed through `multi_agent_v1.spawn_agent`; it found no issues and named
the three retained real subprocess CLI paths.
