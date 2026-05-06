# Doctor Advisory Exit Debug
Date: 2026-05-06

## Problem

`python3 scripts/doctor.py --repo-root . --json --skip-release-probe` exited
with status 1 while Cautilus was intentionally disabled by the repo adapter.

## Correct Behavior

Given an integration is disabled by adapter policy, doctor should report that
tool as disabled without running it. Given another tool is missing but only has
an advisory manual-install disposition, whole-inventory doctor should still
exit 0.

## Observed Facts

- Cautilus reported `doctor_status: disabled` and
  `doctor_disposition: disabled-by-adapter`.
- `gws-cli` reported `doctor_status: missing` and
  `doctor_disposition: advisory-install-needed`.
- The prior exit-code check treated any non-`ok` `doctor_status` as blocking.
- Full doctor exited 1 before the patch and 0 after checking dispositions.

## Reproduction

Run `python3 scripts/doctor.py --repo-root . --json --skip-release-probe` in a
workspace where Cautilus is disabled and `gws` is not installed.

## Candidate Causes

- The CLI may have ignored the Cautilus disabled adapter and tried to execute it.
- The exit-code aggregation may have used status labels instead of disposition
  severity.
- The `gws-cli` integration may have been incorrectly classified as blocking.
- Generated plugin exports may have carried stale doctor behavior.

## Hypothesis

If doctor exit aggregation uses `doctor_disposition` and only fails for
blocking dispositions, then disabled Cautilus and advisory missing tools remain
visible without failing the whole doctor run.

## Verification

Focused doctor repro now exits 0 and reports Cautilus as
`disabled-by-adapter` and `gws-cli` as `advisory-install-needed`. The full
`./scripts/run-quality.sh --read-only` gate passed 51 phases.

## Root Cause

Doctor exit aggregation collapsed advisory, disabled, and blocking states into
a single non-`ok` status check. That made a missing advisory tool look like a
hard doctor failure even though Cautilus was correctly disabled.

## Seam Risk

- Interrupt ID: doctor-advisory-exit
- Risk Class: operator-visible-recovery
- Seam: integration readiness status versus process exit severity
- Disproving Observation: whole-inventory doctor exits 0 with disabled Cautilus
  and advisory missing `gws-cli`
- What Local Reasoning Cannot Prove: whether every future integration will set
  disposition severity consistently
- Generalization Pressure: monitor

## Interrupt Decision

- Premortem Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep doctor exit decisions on disposition severity, not display status. Preserve
disabled/advisory states in JSON and docs, and keep generated plugin exports
synced before validation.
