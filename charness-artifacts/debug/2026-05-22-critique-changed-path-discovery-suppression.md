# Critique Changed Path Discovery Suppression Debug
Date: 2026-05-22

## Problem

`validate_critique_artifacts.py` converted failed changed-path discovery into
an empty path list, so the default validator mode could report success after
validating zero critique artifacts.

## Correct Behavior

Given the default critique artifact validator mode depends on `git diff` and
`git ls-files` to find changed artifacts, when either discovery command fails,
then validation must exit nonzero with the failed command and output. Explicit
`--paths` and `--all` validation modes must not depend on changed-path
discovery.

## Observed Facts

- `_git_paths()` returned `[]` whenever a git command exited nonzero.
- `changed_paths()` merged those empty lists and `candidate_paths()` returned
  no artifacts, allowing the command to print `Validated 0 critique artifact(s).`
- `--all` was also computing changed paths before selecting all artifacts,
  even though all-artifact validation does not need changed-path discovery.

## Reproduction

Run `validate_critique_artifacts.py --repo-root <non-git repo>` without
`--paths` or `--all`. Before the fix, git discovery failure could become an
empty changed-path set. After the fix, the command exits 1 with
`critique artifact changed-path discovery failed`.

## Candidate Causes

- The helper treated discovery failure as equivalent to no changed files.
- The default path did not carry a separate discovery health signal.
- The CLI computed default changed paths before honoring the `--all` mode.

## Hypothesis

If `_git_paths()` raises `ValidationError` on nonzero git exit, and `main()`
skips changed-path discovery when `--all` is set, then the default mode cannot
silently validate zero artifacts after discovery failure while explicit modes
stay usable in fixture repos.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_critique_skill.py` passed.
- `ruff check scripts/validate_critique_artifacts.py tests/quality_gates/test_critique_skill.py` passed.

## Root Cause

The validator collapsed “changed-path discovery failed” into the same data
shape as “no changed critique artifacts exist.”

## Detection Gap

- default discovery path | no regression for git command failure | add a
  non-git repo fixture that asserts the default mode exits 1 with the discovery
  failure message.
- explicit validation modes | `--all` unnecessarily touched git discovery |
  preserve existing `--all` fixture coverage and route `--all` around
  changed-path discovery.

## Sibling Search

- Mental model: empty changed-path input is always a valid no-op.
- fixed now: critique artifact default discovery fails closed on git command
  failure.
- checked non-blocker: explicit `--paths` and `--all` modes still validate
  fixture artifacts without git metadata.
- deferred: release previous-tag discovery and central repo file listing
  fallback remain separate residuals from the completion audit.

## Seam Risk

- Interrupt ID: critique-changed-path-discovery-suppression
- Risk Class: contract-freeze-risk
- Seam: git changed-path discovery -> critique artifact validator -> quality
  closeout status
- Disproving Observation: a non-git repo fixture now exits 1 in default mode
  instead of validating zero artifacts.
- What Local Reasoning Cannot Prove: whether any historical closeout relied on
  a failed git discovery command before this guard existed.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Keep discovery health distinct from empty discovery results. A validator may
no-op only after a successful discovery command proves that no in-scope files
exist.

## Related Prior Incidents

- `2026-05-22-mutation-sample-manifest-suppression.md`: missing proof input
  was collapsed into an empty clean result.
- `2026-05-22-shell-file-listing-suppression.md`: git file discovery failure
  could previously fall back to a broader shell scan.
