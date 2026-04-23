# Debug Review
Date: 2026-04-23

## Problem

`init.sh` can fail on another machine with:

```text
bootstrap runtime `/Users/ted/.agents/src/charness/.charness/bootstrap-python/bin/python` is still missing required modules ['jsonschema', 'packaging']
```

## Correct Behavior

Given a managed checkout with an existing bootstrap runtime launcher, when
`init.sh` runs with a Python 3.10+ interpreter, then the bootstrap helper should
repair or install the repo-owned runtime so `jsonschema` and `packaging` are
available before running `charness init`.

## Observed Facts

- The error is raised by `scripts/bootstrap_runtime.py` after the final module
  probe fails.
- `init.sh` already calls `scripts/bootstrap_runtime.py` before invoking
  `./charness init`.
- The bootstrap runtime is a shell launcher under `.charness/bootstrap-python`
  that delegates to the selected base Python and prepends a target
  `site-packages` directory through `PYTHONPATH`.
- Existing tests covered fresh install and valid reuse, but not a stale existing
  launcher that points at an older or different base Python.

## Reproduction

Locally reproduced the control-flow gap with a test double:

1. Create an existing `.charness/bootstrap-python/bin/python` launcher with
   stale content.
2. Make the runtime module probe fail until the launcher is rewritten to the
   current base Python.
3. Make the current base Python module probe pass.
4. Run `ensure_bootstrap_runtime`.

Before the fix, the helper could skip rewriting the stale launcher when the
current base Python had the required modules, leaving the final runtime probe to
fail.

## Candidate Causes

- Stale launcher: the existing bootstrap runtime points at a base Python that no
  longer has the required modules.
- Dependency installation failure: `pip --target` fails or installs somewhere
  the launcher does not import.
- Missing pip: the selected Python lacks `pip`, preventing dependency install.

## Hypothesis

If a stale launcher exists and the currently selected base Python already has
the required modules, then the old logic skips dependency installation and also
does not rewrite the launcher, so the final probe still runs through stale
runtime state.

## Verification

- Added a regression test for stale launcher repair when the current base Python
  has the required modules.
- Updated the fresh-install test so module availability only flips after the
  simulated `pip install`.
- `pytest -q tests/charness_cli/test_bootstrap_runtime.py` passes.

## Root Cause

`ensure_bootstrap_runtime` only wrote the runtime launcher when the launcher was
missing or after dependency installation. It did not repair an existing launcher
that failed the module probe when the selected base Python could satisfy the
contract directly.

## Seam Risk

- Interrupt ID: bootstrap-runtime-stale-launcher
- Risk Class: operator-visible-recovery
- Seam: machine-local Python and managed checkout state
- Disproving Observation: a clean machine with no existing runtime would follow
  the fresh install path and not hit this exact stale launcher branch.
- What Local Reasoning Cannot Prove: the exact prior state of the reported
  `/Users/ted/.agents/src/charness/.charness/bootstrap-python/bin/python`
  launcher.
- Generalization Pressure: monitor

## Interrupt Decision

- Premortem Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Repair the launcher whenever the runtime probe fails, then install
requirements only if the repaired launcher still cannot import the required
modules and the base Python cannot provide them directly.

## Related Prior Incidents

- `2026-04-13-stale-init-binary.md` — another install/bootstrap issue caused by
  stale machine-local state surviving across init attempts.
