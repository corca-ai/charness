# Harness eval-contract re-verification on cautilus 0.17.1 (2026-06-22)

The claim-fidelity harness was authored and first run against cautilus **0.15.4**.
This note records re-verification after upgrading the binary to **0.17.1** (the
latest release), so the harness is not silently trusting a contract that moved.

## Why

`charness tool update` left cautilus at 0.15.4 while 0.17.1 had shipped (the
silent-staleness defect this session also fixed with a behind-latest advisory).
Upgrading the scorer can shift its eval surface across minors, so the contract
the harness depends on (`evaluate observation` + the `skill_evaluation_*.v1`
schemas) had to be re-checked on 0.17.1.

## What was checked (no new capture — re-scored the existing packet)

Input reused verbatim: `observed.v1.json` (`cautilus.skill_evaluation_inputs.v1`).

1. `cautilus evaluate observation` still exists on 0.17.1 (`--input`/`--output`).
2. `cautilus doctor packet inspect` recognizes the packet as
   `inputSchemaVersion: cautilus.skill_evaluation_inputs.v1`.
3. Gated re-score via `scripts/run_cautilus_eval.py --mode observation`
   (operator-authorized this session; operator-log justification) produced
   `reverify-0.17.1-summary.v1.json`:
   - `schemaVersion: cautilus.skill_evaluation_summary.v1` (output schema holds)
   - `recommendation: reject` — reproduces the original 0.15.4 verdict
   - `evaluationCounts: execution 1, failed 1, passed 0` (parity)

## Verdict

The harness eval contract holds across 0.15.4 -> 0.17.1: same input schema
accepted, same output schema emitted, same verdict reproduced. The claim-fidelity
harness is compatible with cautilus 0.17.1; no harness change was required.
