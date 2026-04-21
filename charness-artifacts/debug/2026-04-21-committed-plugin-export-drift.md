# Committed Plugin Export Drift Debug
Date: 2026-04-21

## Problem

`charness update` failed on another machine during install-surface refresh with
`scripts/validate-packaging.py ... checked-in plugin tree does not match the
generated install surface`, even though the source checkout that fed the update
looked locally "fixed" because regenerated plugin-export files were still
present in the working tree.

## Correct Behavior

Given a repo where source-owned packaging inputs changed,
when only the source files are committed and the regenerated plugin-export files
remain uncommitted in the working tree,
then repo-owned quality gates should reject that committed snapshot before
another checkout can consume it.

## Observed Facts

- Another machine failed at
  `plugins/charness/skills/create-cli/SKILL.md` packaging drift during
  `charness update`.
- In the current repo, `python3 scripts/validate-packaging.py --repo-root .`
  passed because the working tree already contained regenerated
  `plugins/charness/**` files.
- Comparing `HEAD` files directly showed source/plugin mismatch for
  `skills/public/create-cli/SKILL.md` and its exported plugin counterpart.
- The managed checkout on this machine pulls from a local-path `origin`
  pointing at `/home/ubuntu/charness`, so that flow bypasses the checked-in
  pre-push hook.

## Reproduction

- Start from a clean git clone of the repo.
- Edit `skills/public/create-cli/SKILL.md`.
- Run `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- Commit only `skills/public/create-cli/SKILL.md`.
- Leave the regenerated `plugins/charness/**` changes uncommitted.
- `python3 scripts/validate-packaging.py --repo-root .` passes on the working
  tree, but the committed snapshot fails packaging validation and another
  checkout pulling that commit fails during `charness update`.

## Candidate Causes

- Packaging validation only checked the current working tree, not the committed
  snapshot another machine would consume.
- Maintainer workflow relied on hooks or manual discipline instead of a
  repo-owned committed-snapshot validator in the standing gate.
- The repo had no explicit regression test for the partial-commit case where
  source files are committed but regenerated plugin-export files remain only in
  the working tree.

## Hypothesis

If the repo validates the committed snapshot separately from the working tree,
then partial commits with uncommitted plugin-export drift will be blocked
before they break downstream `charness update` runs.

## Verification

- Added `scripts/validate-packaging-committed.py` to validate a git ref snapshot
  via `git archive`.
- Added the new validator to `run-quality.sh` and to the checked-in-plugin
  surface obligations.
- Added a packaging regression test that proves the working-tree validator can
  pass while the committed snapshot validator fails.
- Re-ran focused packaging, surface-obligation, and managed-install tests.

## Root Cause

The repo had a workflow gap between "working tree is consistent" and "committed
snapshot is consistent". The downstream machine only sees the committed
snapshot, but the standing packaging check validated the current working tree.

## Prevention

- Keep `validate-packaging-committed.py` in the standing quality runner so
  partial commits cannot hide behind a locally regenerated working tree.
- Keep the regression test for partial-commit drift.
