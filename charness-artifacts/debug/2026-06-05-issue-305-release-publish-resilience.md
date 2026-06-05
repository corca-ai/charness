# Debug #305 — release publish-flow resilience (3 gaps from the v0.21.0 publish)
Date: 2026-06-05
Issue: #305 (bug-class; mechanisms documented from the live v0.21.0 publish)
Surface: `skills/public/release/scripts/publish_release_cli.py`,
`publish_release_plan.py`, `publish_release_preflight.py`,
`publish_release_retro.py`, new `publish_release_resume.py`.

## Problem

The release publish flow had three independent resilience gaps, all confirmed
from the live v0.21.0 publish: it was not resumable after a mid-publish failure,
it could not run from the installed plugin cache, and it could ship stale
operator `update_instructions` undetected.

## Correct Behavior

A publish that fails after the local commit + tag but before push should be
resumable idempotently; the publish helper should run from the exported plugin
cache as well as the repo; and a release whose `update_instructions` still
describe the previous version should be blocked before publishing.

## Observed Facts

- v0.21.0: a flaked pre-push gate left commit + tag local, nothing on origin, no
  GitHub release. Re-running was not idempotent (`git commit` → "nothing to
  commit", `git tag` → "tag exists", `ensure_release_target_available` blocked on
  the local tag). Recovery was manual.
- From `plugins/charness`, `publish_release_retro.py` raised
  `ModuleNotFoundError: No module named 'skills.public'`; the exported tree has
  `skills/retro/scripts/check_auto_trigger.py`, no `skills/public/`.
- `release_adapter_preflight_payload` only ran when a release-adapter FILE
  changed in the delta; v0.21.0 shipped stale 0.20.0 operator steps in the
  generated record.

## Reproduction

The v0.21.0 publish itself reproduced all three: a real failed-push partial
state requiring manual recovery; an exported-cache `publish_release.py --help`
raising the import error; and a generated record carrying 0.20.0 update steps
while the file the preflight watches was untouched.

## Candidate Causes

- Publish steps (commit → tag → push) had no resume entry point and no
  idempotent re-validation, so a partial state could not be continued (Gap 1).
- The retro auto-trigger import assumed the `skills.public.<x>` repo layout and
  did not tolerate the flattened `skills.<x>` exported layout (Gap 2).
- The adapter preflight was gated on a changed adapter FILE rather than running
  unconditionally against the version delta (Gap 3).

## Hypothesis

A `--resume` path that re-validates the flake-prone gates and only performs the
not-yet-done push/release/verify steps fixes Gap 1; a layout-tolerant public
skill import fixes Gap 2; and an unconditional version-string staleness check on
`update_instructions` fixes Gap 3.

## Verification

Test-level only; no real `git push` / `gh release create` (resume proven with a
simulated failed-push partial state + fake git/gh; explicit non-claim).
`tests/quality_gates/test_release_publish_resilience.py` (staleness logic +
integration block; exported-layout import; resume idempotent continue; resume
refuses with no partial state; resume requires `--publish-current`) plus the full
release suite = 63+ green; deterministic closeout aggregate completed (incl.
public-skill validation/dogfood gates after recording the release dogfood
evidence). Mirrors byte-identical.

## Root Cause

The publish flow modeled only the happy path: no resume entry point for partial
state, a repo-layout-only import in the retro trigger, and a file-change-gated
adapter preflight that could not see stale `update_instructions` whose file was
untouched.

## Prevention

- Gap 1: new `--resume` flag (requires `--publish-current`). `resume_publish`
  validates the partial state (HEAD is the release commit; tag local + points at
  HEAD; refuses if already fully published or no consistent partial state),
  re-validates the flake-prone pre-push gates (issue preflight, requested review,
  CLI-skill-surface, quality command, fresh-checkout probes, narrative audit),
  refreshes the release artifact, pushes only if the tag is not already on the
  remote, creates the release only if absent, verifies, finalizes, closes issues,
  and commits the verified record. `build_publish_plan` skips
  `ensure_release_target_available` under `resume`.
- Gap 2: `_load_public_skill_module` tries `skills.public.<x>` then `skills.<x>`,
  tolerating only the `skills(.public)` layout miss and re-raising a genuine
  missing dependency inside the target module. Exported `publish_release.py
  --help` now exits 0.
- Gap 3: unconditional `update_instructions_version_blocker(update_instructions,
  target_version, previous_version)` wired into `build_publish_plan`. It flags
  when the instructions still describe the previous version but not the target,
  using plain substring containment of the concrete version strings (no general
  semver scan), so it does not false-positive on dotted dates / version-agnostic
  prose and matches `v`-prefixed forms transparently.
