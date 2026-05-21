# Release Real-Host Config Suppression Debug
Date: 2026-05-22

## Problem

Release publish treated broken real-host proof configuration as no proof
required, so a release could continue after the proof helper reported
`configuration_status: "broken"`.

## Correct Behavior

Given a release adapter declares real-host proof triggers, when the trigger
configuration is broken or the proof builder cannot run, then dry-run and
execute publish must fail before JSON output, version bumps, artifacts, quality
proof, commits, tags, pushes, or release creation.

## Observed Facts

- The standalone `check_real_host_proof.py` already exits nonzero for unresolved
  `real_host_required_surfaces`.
- `safe_real_host_payload()` caught broad exceptions and returned
  `required: False`.
- `check_real_host_proof.build_payload()` can return `configuration_status:
  "broken"` without raising.
- Publish computed real-host payload only after the version bump, and dry-run did
  not compute it before printing JSON.
- New failing tests reproduced both execute-mode release completion and dry-run
  JSON output with a broken trigger surface.

## Reproduction

Configure `.agents/release-adapter.yaml` with
`real_host_required_surfaces: [missing-release-surface]` while
`.agents/surfaces.json` declares only `operator-docs`, commit that config, then
run `publish_release.py --part patch` or `--part patch --execute`.

## Candidate Causes

- The safe wrapper collapsed real-host proof failures into a false non-match.
- The publish flow did not reject `configuration_status: "broken"` payloads.
- Dry-run output was built before proving that release proof configuration was
  readable.

## Hypothesis

If the real-host proof builder supports no-trigger repos without a surfaces
manifest, but fails closed for configured broken surface triggers and builder
exceptions before dry-run output or execute mutation, then broken proof config
cannot masquerade as no proof required.

## Verification

- Failing regression first proved execute mode completed and dry-run emitted
  JSON with broken real-host config.
- Focused pytest passed for broken-config publish regressions, proof-builder
  exception fail-closed behavior, no-trigger dry-run compatibility without a
  surfaces manifest, and existing real-host proof tests.
- `ruff check` passed for the changed release scripts and tests.
- `python3 scripts/check_python_lengths.py --repo-root .` passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`
  passed after fresh-eye critique follow-ups.

## Root Cause

The publish wrapper encoded unknown real-host proof state as a normal
`required: False` payload, and the publish path had no pre-mutation proof-config
check.

## Detection Gap

- publish real-host proof | standalone helper tested broken config, publish did
  not | add execute and dry-run broken-config publish regressions.
- wrapper semantics | broad exception fallback produced a non-match payload |
  make proof-builder failure fatal in publish.
- trigger compatibility | surfaces manifest was loaded before checking whether
  surface triggers were configured | allow no-surface no-trigger repos while
  keeping configured surface triggers strict.

## Sibling Search

- Mental model: an unavailable proof helper can be represented as no trigger.
- fixed now: broken real-host trigger config and proof-builder exceptions in
  publish fail closed.
- still open: `_release_base_ref()` can fall back to branch diff when a known
  previous release tag fetch fails.
- still open: mutation changed-file discovery can turn `git diff` failure into
  no changed files.
- still open: post-create public release verification records `not_checked`
  after mutation and needs separate recovery design.

## Seam Risk

- Interrupt ID: release-real-host-config-suppression
- Risk Class: contract-freeze-risk
- Seam: release adapter triggers -> surfaces manifest -> publish proof gate
- Disproving Observation: broken trigger config now exits before dry-run JSON or
  execute-mode mutation.
- What Local Reasoning Cannot Prove: whether post-create verification failure
  should block after external mutation.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Do not represent proof-builder failures as non-matches. Regression tests for
release proof gates must cover both dry-run visibility and execute-mode
mutation boundaries.

## Related Prior Incidents

- `2026-05-22-release-diff-failure-suppression.md`: git diff failure also
  collapsed unknown proof input into an empty release delta.
- `2026-05-17-empty-policy-silent-pass.md`: empty or unavailable policy state
  must stay distinguishable from explicit success.
