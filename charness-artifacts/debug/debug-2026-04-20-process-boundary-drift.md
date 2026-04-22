# Process Boundary Drift Debug
Date: 2026-04-20

## Problem

Two April 20, 2026 issues exposed the same class of failure:

- `#41`: unbounded subprocess calls around `resolve_adapter.py` and `run-evals`
- `#42`: unowned `agent-browser` daemon lifecycles that can outlive the session

The concrete symptoms differ, but both come from `charness` crossing a process
boundary without enough ownership over time, health, and recovery.

## Correct Behavior

Given a repo-owned CLI, helper script, or support runtime seam,
when `charness` starts or depends on an external process,
then the process boundary should be:

- bounded by timeout or explicit lifecycle ownership
- diagnosable through repo-owned doctor or helper commands
- recoverable through scripted cleanup, not prose-only instructions

## Observed Facts

- `scripts/run_evals.py` called `subprocess.run(...)` without `timeout=`.
- public `resolve_adapter.py` helpers are invoked directly from SKILL bootstrap
  shell snippets, so a hung child process can outlive the caller.
- `agent-browser` integration only checked binary existence / `--help` health,
  not runtime hygiene such as orphaned daemon accumulation.
- the reported `agent-browser` failure mode is not a classic zombie (`Z`) but
  long-lived orphan daemon trees adopted by PID 1.

## Reproduction

Issue reports documented two concrete failure paths:

- `#41`: `resolve_adapter.py` and `run-evals` subprocess seams can hang without
  timeout and accumulate runaway processes.
- `#42`: `agent-browser` daemon trees can survive session exit as orphaned
  long-lived runtimes.

## Candidate Causes

- Missing timeout defaults for repo-owned subprocess seams.
- External runtime health was modeled as "binary responds" rather than
  "runtime is hygienic and recoverable".
- Support skills and integrations lacked a repo-owned cleanup / diagnosis path
  for long-lived runtime drift.

## Hypothesis

If `charness` moves these seams onto explicit bounded-process and runtime-health
helpers, then:

- hangs fail closed instead of accumulating silently
- `tool doctor` can surface orphan runtime drift before users rediscover it
- operators get a scripted cleanup path that future skill and CLI authors can reuse

## Verification

- add a shared subprocess guard with default timeouts
- route `run-evals` through that guard
- arm CLI timeouts for public `resolve_adapter.py` entrypoints
- add repo-owned `agent-browser` runtime inspection / cleanup helper
- make `agent-browser` doctor health fail on orphan daemon drift

## Root Cause

`charness` had no explicit policy that every external process seam must be
bounded, ownable, diagnosable, and recoverable. Individual commands worked when
the happy path held, but long-lived failure modes were under-specified.

## Prevention

- treat timeout-free subprocess execution as policy drift
- treat long-lived runtime health as more than binary presence
- require scripted recovery for recurring runtime failures
- encode the rule in repo-owned helpers and doctor surfaces so future skill/CLI
  authors inherit the safer path by default
