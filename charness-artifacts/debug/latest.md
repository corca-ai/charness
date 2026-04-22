# Managed Checkout Divergence Debug
Date: 2026-04-21

## Problem

`charness update` failed during source refresh with the raw git error
`fatal: Not possible to fast-forward, aborting.` instead of explaining that the
managed checkout had diverged from its upstream branch.

## Correct Behavior

Given a managed checkout used by the installed CLI,
when that checkout is both ahead of and behind its upstream branch,
then `charness update` should fail with an explicit divergence message and an
actionable recovery path instead of only surfacing raw `git pull --ff-only`
stderr.

## Observed Facts

- Installed `charness` resolved to `/home/ubuntu/.local/bin/charness`.
- `charness doctor --json` reported the managed checkout at
  `/home/ubuntu/.agents/src/charness`.
- Running `charness update` stopped at `STEP: refreshing source checkout`.
- The failing command output was:
  `fatal: Not possible to fast-forward, aborting.`
- `git -C /home/ubuntu/.agents/src/charness status -sb` showed
  `## main...origin/main [ahead 1, behind 2]`.
- The managed checkout also had an untracked `.agents/charness-discovery/`
  directory, but untracked files are already allowed by the update path.

## Reproduction

- Create a managed checkout from a seeded repo.
- Commit one local change in the managed checkout.
- Commit one different upstream change in the remote source repo.
- Run the installed CLI with
  `charness update --home-root <seeded-home> --skip-codex-cache-refresh`.
- Before the fix, the command failed with only the raw `git pull --ff-only`
  stderr.

## Candidate Causes

- A prior dogfood or manual edit created a local commit in the managed checkout.
- The upstream repo advanced after that local commit, leaving the branch
  diverged.
- The update path delegated directly to `git pull --ff-only` and treated every
  failure as generic command stderr instead of classifying the common divergence
  case.

## Hypothesis

If `charness update` inspects upstream ahead/behind counts after a failed
`git pull --ff-only`, then the managed-checkout divergence case can be reported
as a first-class operator error with a precise recovery path.

## Verification

- Added upstream divergence helpers to `charness` and converted the failed
  managed-checkout pull path into a targeted `CharnessError` when the checkout
  is both ahead of and behind its upstream branch.
- Added `test_installed_cli_update_reports_diverged_managed_checkout` to
  reproduce the branch divergence and assert the new guidance text.
- Re-ran the focused managed-install tests and the debug artifact validator.

## Root Cause

The managed update flow encoded only one special-case preflight:
tracked worktree edits. Once `git pull --ff-only` failed because the managed
checkout had diverged from `origin/main`, the CLI surfaced raw git stderr
without telling the operator that the checkout needed rebase/reset or that a
proof-only `--no-pull` flow existed for intentional dogfood commits.

## Seam Risk

- Interrupt ID: managed-checkout-divergence
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: none
- Generalization Pressure: none

## Interrupt Decision

- Premortem Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

- Keep a regression test for diverged managed checkouts so update guidance stays
  operator-readable.
- Treat intentional local managed-checkout commits as a proof-only flow and use
  `charness update --repo-root . --no-pull --skip-cli-install` instead of
  expecting the default managed fast-forward path to reconcile them.
- Preserve explicit checkout-state classification near the update entrypoint so
  future git-command refactors do not collapse back to raw stderr.
