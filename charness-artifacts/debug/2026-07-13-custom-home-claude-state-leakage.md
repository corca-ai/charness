# Custom Home Claude State Leakage Debug
Date: 2026-07-13

## Problem

`charness doctor --home-root <custom>` reads Claude JSON files from the custom
home but asks `claude plugins list` about the process `HOME`. When those homes
differ, doctor can report an installed custom-home plugin as missing.

## Correct Behavior

Given an explicit home root, all file and subprocess observations used for one
Claude host verdict must address that same home. Default invocations keep the
inherited environment unchanged.

## Observed Facts

- All filesystem paths in `build_doctor_payload` derive from `home_root`.
- `claude_enabled_status(repo_root)` accepts no home and runs the CLI with an
  inherited environment.
- With a seeded custom home and an empty process home, the payload reports
  `present=false`, drops the installed entry, and recommends reinstalling.
- Aligning process `HOME` to the same custom root reports `present=true`, retains
  the installed entry, and returns `status=installed`.

## Reproduction

- Seed the repo marketplace and plugin with the fake Claude CLI under custom
  HOME, then run doctor with process HOME pointed at a different empty directory
  and `--home-root` still pointed at custom. The two runs differ only in process
  HOME and produce `needs-install` versus `installed`.

## Candidate Causes

- `claude_enabled_status` omits `home_root` and therefore cannot bind CLI state.
- The fake CLI behaves differently from real Claude and exposes a test-only gap.
- `--home-root` intentionally scopes only Charness files, not host CLIs.

## Hypothesis

- Falsifiable claim: Claude subprocesses participating in a custom-home workflow
  inherit the unrelated process HOME; explicitly binding only those subprocesses
  to `home_root` will make doctor file and CLI evidence agree while preserving
  default-home behavior. | disconfirmer: find a documented split-scope contract
  or a subprocess helper already binding HOME for every Claude call.

## Verification

- resolved — the two-home fake-CLI experiment changed the final doctor verdict
  solely with process HOME. Every Claude plugin subprocess now crosses one
  home-binding seam. Public two-home doctor, init, and reset regressions passed
  in 6.57s, proving observation, addition, and removal target only the selected
  home. Ruff, raw-call search, and bounded code critique passed.

## Root Cause

The workflow passes `home_root` through path producers but drops it at the
Claude subprocess boundary. The final verdict then combines state produced by
two different homes as if it described one host installation.

## Invariant Proof

- Invariant: one doctor/install/update/uninstall workflow must not mix custom-home
  files with a different home selected implicitly by its host subprocess.
- Producer Proof: custom-home known/installed JSON and empty process-home CLI
  listing disagree in the minimal reproduction.
- Final-Consumer Proof: public doctor reports the selected home; public init
  creates only selected-home Claude state; public reset removes selected-home
  state and leaves the unrelated process home without a `.claude` tree.
- Interface-Shape Sibling Scan: inspect every Claude CLI call and distinguish
  observational, mutating, and default-home-only paths before choosing the seam.
- Non-Claims: no claim that PATH, credentials, XDG roots, or arbitrary child
  processes should be replaced; only Claude's HOME-owned plugin state is in scope.

## Detection Gap

- managed-home CLI tests | test env always sets `HOME == --home-root`, hiding
  the split | add a two-home process regression that asserts the custom home is
  observed and the unrelated process home remains untouched.

## Sibling Search

- Mental model: an explicit path parameter was treated as complete authority in
  file code but not propagated through the subprocess seam.
- same layer: doctor `plugins list` | decision: fix now | proof: two-home repro.
- abstraction up: a Claude-command environment helper | decision: probe | proof:
  enumerate all Claude calls before deciding helper scope.
- specialization down: init/update/uninstall Claude mutations | decision: probe |
  proof: confirm whether each mutation promises the explicit home boundary.
- cross-file: managed-install fixtures always align process/custom HOME and
  therefore cannot exhibit the leak.

## Seam Risk

- Interrupt ID: custom-home-claude-subprocess-state
- Risk Class: none
- Seam: explicit Charness home root to Claude plugin subprocess environment
- Disproving Observation: the same custom-home files yield opposite final
  verdicts when only unrelated process HOME changes.
- What Local Reasoning Cannot Prove: whether real Claude also consults XDG state
  beyond HOME; the repo fake owns the current deterministic contract.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Bind Claude plugin subprocesses to the workflow home at one owned seam and add
a public two-home regression; do not globally replace process environment.
