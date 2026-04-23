# Auto Retro Missing Surfaces Debug
Date: 2026-04-23

## Problem

`skills/public/retro/scripts/check_auto_trigger.py` raised
`scripts.surfaces_lib.SurfaceError: missing surfaces manifest` in consumer
repos that had `.agents/retro-adapter.yaml` but no `.agents/surfaces.json`.

## Correct Behavior

Given a consumer repo with a retro adapter and no configured auto-retro trigger
surfaces or path globs, when `check_auto_trigger.py --repo-root .` runs, then
it should return `triggered: false` without requiring `.agents/surfaces.json`.

Given auto-retro trigger config is present but `.agents/surfaces.json` is
missing or invalid, when the helper runs, then it should fail without a Python
traceback and include a clear bootstrap or adapter-remediation path.

## Observed Facts

- GitHub issue #63 reported the failure after ordinary closeout in `crill`.
- The observed command was
  `python3 .../skills/retro/scripts/check_auto_trigger.py --repo-root .`.
- Local reproduction with a temp repo containing only
  `.agents/retro-adapter.yaml` produced
  `scripts.surfaces_lib.SurfaceError: missing surfaces manifest`.
- `resolve_adapter.py` defaults both `auto_session_trigger_surfaces` and
  `auto_session_trigger_path_globs` to empty lists when they are absent.
- `check_auto_trigger.py` loaded `.agents/surfaces.json` before checking
  whether either auto-trigger list was configured.

## Reproduction

Create a temp repo with `.agents/retro-adapter.yaml` and no
`.agents/surfaces.json`, then run:

```bash
python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root "$tmp"
```

Before the fix, the command exited with a traceback ending in
`SurfaceError: missing surfaces manifest`.

## Candidate Causes

- The helper loaded the surfaces manifest unconditionally before knowing if
  configured surface matching was needed.
- The adapter default layer made absent trigger fields look like explicit empty
  lists, but the evaluation order did not exploit that safe default.
- The script had no top-level `SurfaceError` handler, unlike adjacent
  surface-driven helpers that convert those errors to operator-readable output.

## Hypothesis

If `check_auto_trigger.py` exits early when both trigger lists are empty, then
consumer repos without `.agents/surfaces.json` can complete closeout normally.
If a `SurfaceError` is caught after trigger config is detected, then configured
repos still fail loudly but with remediation instead of a traceback.

## Verification

- Added a regression test for a consumer repo with retro adapter but no
  surfaces manifest and no auto-trigger config.
- Added a regression test for configured auto-trigger surfaces with a missing
  surfaces manifest, asserting no traceback and an explicit remediation path.
- Reproduced the original failure before patching and confirmed the new tests
  cover that shape.
- Reviewed the `retro` public-skill dogfood scaffold; the prompt-routing
  contract is unchanged because this slice only changes auto-trigger helper
  fallback behavior.

## Root Cause

`check_auto_trigger.py` treated surface matching as mandatory setup even when
the adapter had no surface or glob triggers configured. The safe adapter
defaults existed, but they were read only after the helper had already required
`.agents/surfaces.json`.

## Seam Risk

- Interrupt ID: auto-retro-missing-surfaces
- Risk Class: operator-visible-recovery
- Seam: consumer repo closeout using installed charness retro helper
- Disproving Observation: regression tests cover missing manifest with and without trigger config
- What Local Reasoning Cannot Prove: every downstream caller's nonzero-output handling for configured missing-manifest repos
- Generalization Pressure: monitor

## Interrupt Decision

- Premortem Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

- Keep no-trigger auto-retro evaluation independent from git diff and surfaces
  manifest loading.
- Keep configured missing-manifest failures structured and remediation-oriented.
- Preserve consumer-repo regression tests for retro adapter presence without a
  committed surfaces manifest.
