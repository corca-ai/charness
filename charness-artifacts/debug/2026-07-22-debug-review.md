# Debug Review
Date: 2026-07-22

## Problem

The full quality runner fails its `specdown` phase before executable specifications run because its command uses unsupported `-quiet` and `-no-report` flags.

## Correct Behavior

`./scripts/run-quality.sh` runs the repository's executable specifications with the installed, supported Specdown CLI and leaves the tracked `.charness/specdown/` report untouched.

## Observed Facts

- `./scripts/run-quality.sh --review` reported `flag provided but not defined: -quiet` for the `specdown` gate.
- `specdown run --help` lists `-config`, `-dry-run`, `-filter`, `-jobs`, `-out`, and `-show-bindings`; it lists neither legacy flag.
- `specdown run -dry-run -jobs 4` passes but rewrites `.charness/specdown/report.json`, so dry-run is not a safe replacement for the runner's no-report intent.
- `specdown run -jobs 4 -out <temporary-directory>` executes all four repository specs successfully and writes its report only under that temporary directory.
- The installed binary identifies itself as `dev`; `charness tool doctor specdown --detail` nevertheless reports it detected and ready.

## Reproduction

- `specdown run -quiet -no-report -jobs 4` exits nonzero with `flag provided but not defined: -quiet`.

## Candidate Causes

- The quality runner retained flags from an older Specdown CLI.
- The host resolves a different Specdown build than the runner was written for.
- The original no-report requirement was expressed as a CLI flag instead of routing generated output to the runner's existing temporary directory.

## Hypothesis

- The runner hard-codes removed/unsupported flags; replacing them with supported `-jobs 4 -out <runner-temp-dir>` will execute the same specs successfully without mutating `.charness/specdown/` | disconfirmer: run the selected quality `specdown` gate and confirm both a zero exit status and no report diff.

## Verification

- result: confirmed — direct execution with `specdown run -jobs 4 -out <temporary-directory>` passed 4 specs and 8 cases, while the legacy command failed before execution.

## Root Cause

The quality runner and executable-spec surface carried an obsolete Specdown flag contract. Their intended no-worktree-report behavior is preserved by the currently supported `-out` option, but that option was not used.

## Invariant Proof

- Invariant: no tracked `.charness/specdown/` report is written by the standing quality runner.
- Producer Proof: the runner passes its already-cleaned `$RUN_QUALITY_TMPDIR/specdown-report` as Specdown's `-out` directory.
- Final-Consumer Proof: the `specdown` phase still receives Specdown's exit status through `queue_selected`; its report directory is removed by the runner's existing exit trap.
- Interface-Shape Sibling Scan: `.agents/surfaces.json` executable-spec verification now uses the same supported `-out` contract with a shell cleanup trap.
- Non-Claims: this does not validate every historical Specdown release; it validates the supported CLI observed on this host.

## Detection Gap

- quality runner command contract | the full quality test suite did not assert the Specdown invocation | add a focused runner-source regression test that requires the temporary `-out` destination and rejects the obsolete flags.

## Sibling Search

- Mental model: a tool invocation must use the installed CLI's supported flags and preserve the repository's derived-state boundary.
- command contract: `.agents/surfaces.json` executable-specs verification | decision: update to the same temporary `-out` pattern | proof: static surface verification command uses no obsolete flags.
- cross-file: `tests/quality_gates/test_quality_runner.py` protects the runner command shape.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: runner subprocess command to external Specdown binary
- Disproving Observation: the supported command completed all executable specs with reports isolated outside the worktree
- What Local Reasoning Cannot Prove: the behavior of untested upstream versions
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep the focused command-shape regression test with the quality runner. Tool upgrades will then fail on a concrete invocation mismatch instead of leaving the broad quality gate silently stale.
