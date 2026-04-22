# Spec — Agent-Facing CLI Startup Probes
Date: 2026-04-22

## Problem

`quality` already has a standing runtime-budget pattern, but installable or
agent-facing CLIs still lack a reusable contract for startup latency seams.
That leaves repo owners without a standard answer to:

- which cheap startup commands should exist
- which of those should be standing-gated
- which measurements are release-time proof only
- how startup timing should connect back to the existing runtime-signal and
  runtime-budget surface

## Decision

Add adapter-owned `startup_probes` that describe cheap startup commands and
their semantics:

- `label`
- `command`
- `class` (`standing` or `release`)
- `startup_mode` (`warm`, `cold`, or `first-launch`)
- `surface` (`direct`, `install-like`, or another explicit launcher surface)
- `samples`

`startup_probes` define what to measure. Existing `runtime_budgets` continue to
define the standing latency budget for labels that should fail the quality run.

This keeps semantics and budgets separate:

- `startup_probes` answers "what startup seam are we measuring?"
- `runtime_budgets` answers "which measured seams have a standing hard limit?"

## Current Slice

1. Add `startup_probes` to the quality adapter contract and bootstrap defaults.
2. Ship a reusable `measure_startup_probes.py` helper through the public
   `quality` skill.
3. Teach `quality` and `create-cli` to require at least one cheap read-only
   startup probe for agent-facing CLIs.
4. Teach `release` to surface startup proof when install or launcher seams
   move.
5. Dogfood the standing path in this repo with a `charness --version` startup
   probe and a runtime budget keyed by the same label.

## Non-Goals

- making every CLI cold-start measurement a standing gate
- hardcoding one packaging tool such as PyInstaller into the public contract
- requiring identical budgets across repos
- treating release-time launcher proof as equivalent to repo-local standing
  gates

## Success Criteria

1. `quality` adapters can declare startup probes with standing vs release
   classification.
2. a repo-owned helper can execute those probes and optionally record runtime
   signals for the measured labels.
3. standing probes can reuse `runtime_budgets` by sharing the same label.
4. `create-cli` documents cheap startup probes as part of the operator and
   agent-facing contract.
5. `release` can point at startup proof explicitly when launcher or install
   seams changed.
