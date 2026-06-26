# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts static `check_cli_skill_surface.py`
subprocess tests to in-process `main()` calls while retaining real probe
execution tests.

## Failure Angles

- Boundary proof: converting all calls would erase proof that the script boots
  and parses its CLI.
- Probe execution: `--run-probes` launches external commands and must keep real
  process proof.
- Timeout behavior: probe timeout handling depends on subprocess timeout
  semantics and should not be collapsed into a direct helper call.
- Argument surface: `--changed-path` behavior should still be exercised through
  `main()` if converted.

## Counterweight Pass

- Real subprocess checks remain for basic JSON invocation, run-probe success,
  and run-probe timeout.
- Converted tests still exercise argparse, JSON stdout, and return-code behavior
  through `main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.
- The converted cases are static adapter-rule payload checks, not unique
  external probe boundaries.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_cli_skill_surface.py | action: fix | note: static-rule subprocess calls dropped from 9 to 3 while retaining probe execution and timeout smokes
- F2 | bin: valid-but-defer | evidence: strong | ref: tests/quality_gates/test_cli_skill_surface.py | action: defer | note: keep remaining --run-probes subprocess tests because they prove external command execution and timeout behavior

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_context=true, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: reviewer completed and returned no blocking findings

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f017d-a9c5-7f11-96a1-1d3e2f1ab86c`
completed through `multi_agent_v1.spawn_agent`; it found no blocking issue and
confirmed retained subprocess proof for bootstrap, `--run-probes` success, and
timeout probe execution.
