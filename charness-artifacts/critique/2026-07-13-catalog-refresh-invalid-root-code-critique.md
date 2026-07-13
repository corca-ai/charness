# Catalog Refresh Invalid Root Code Critique
Date: 2026-07-13

## Decision Under Review

Reject missing and non-directory catalog refresh roots in the artifact-producing
backend, then render the typed error consistently in the direct and public CLI.

## Failure Angles

- Root-cause and ownership: a caller-only guard could leave imported backend
  consumers able to create typo roots, while a shared `_repo_root` guard would
  incorrectly narrow read-only list and cache-recovery semantics.
- Operator boundary: in-process handler tests could miss parser, dispatcher,
  process exit, and stdout/stderr regressions at the actual `./charness` entrypoint.

## Counterweight Pass

- The backend guard and consumer translation are correctly owned and scoped.
- The real-process regression was required before ship and added; it covers one
  JSON missing-root case and one plain-text file-root case without duplicating
  the full backend matrix.
- Permission, symlink, Git-checkout, list, and resolve matrices are over-worry or
  valid deferrals absent new operator evidence.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/charness_cli/test_codex_cache_refresh.py | action: fix | note: add a durable real-process regression for rc, channels, JSON shape, traceback absence, and no-write behavior; fixed and verified.
- F2 | bin: bundle-anyway | evidence: moderate | ref: tests/charness_cli/test_codex_cache_refresh.py | action: fix | note: assert canonical `repo_root` and clean stdout/stderr separation in the real-process test; bundled into F1.
- F3 | bin: over-worry | evidence: strong | ref: charness-artifacts/debug/2026-07-13-debug-review-followup-3.md | action: defer | note: do not broaden the guard to read-only list/resolve or require a Git checkout.
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/capability_catalog.py | action: defer | note: permission and symlink edge matrices require future operator evidence before expanding this focused slice.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: metadata-hidden
- Application state: requested fields were accepted by the host spawn surface; provider application was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — two distinct code angles and a separate counterweight ran
read-only; fingerprint verification reported zero drift after each review window.

## Boundary Ownership

- Producer: `scripts.capability_catalog.refresh_catalog` produces catalog current-pointer artifacts.
- Consumer: direct script `main` and public `charness catalog refresh`.
- Owning surface: capability-catalog refresh backend owns destination validity; each final CLI owns error rendering.
- Verdict: moved-to-owner
