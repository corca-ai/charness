# Markdown Preview Readiness Criterion Debug
Date: 2026-05-06

## Problem

Pre-push failed in `check-cli-skill-surface` because
`python3 scripts/doctor.py --repo-root . --json --skip-release-probe` exited 1.

## Correct Behavior

Given the markdown-preview `glow` readiness command renders a sample and exits
0, doctor should accept the readiness check using supported success criteria.
The command can encode non-empty rendered output through its own exit status.

## Observed Facts

- Pre-push reported `FAIL check-cli-skill-surface`.
- Direct reproduction showed `markdown-preview-glow-backend` command exited 0.
- The same check still failed with
  `unsupported success criterion non_empty_rendered_sample`.
- Existing doctor readiness criteria accept `exit_code:0`, not ad hoc semantic
  labels.

## Reproduction

Run `python3 scripts/doctor.py --repo-root . --json --skip-release-probe` after
adding `non_empty_rendered_sample` to
`skills/support/markdown-preview/capability.json` readiness success criteria.

## Candidate Causes

- The new helper command may have returned non-zero.
- The support capability command may have been path-bound to the wrong tree.
- The doctor success-criteria parser may not understand the new semantic label.
- The checked-in plugin export may have been stale after source edits.

## Hypothesis

If the unsupported success criterion is removed and the helper command remains
the source of the non-empty sample check, then doctor will accept
markdown-preview readiness when the command exits 0.

## Verification

After removing `non_empty_rendered_sample` and syncing the plugin export:

- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe` exits 0
- `python3 scripts/validate_packaging_committed.py --repo-root .` passes
- `python3 scripts/validate_integrations.py --repo-root .` passes
- focused markdown-preview and packaging support tests pass

## Root Cause

The patch introduced a new success criterion string without extending the
doctor readiness evaluator. The helper command already made the semantic check,
so the extra criterion duplicated that assertion at an unsupported layer.

## Seam Risk

- Interrupt ID: markdown-preview-readiness-criterion
- Risk Class: operator-visible-recovery
- Seam: capability manifest success criteria versus helper-owned runtime checks
- Disproving Observation: doctor exits 0 after relying on `exit_code:0`
- What Local Reasoning Cannot Prove: whether future capability authors will add
  unsupported criteria without validator coverage
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep semantic readiness checks inside helper commands unless the doctor
success-criteria schema explicitly supports the label. Preserve plugin export
path-rewrite tests for support capability commands.
