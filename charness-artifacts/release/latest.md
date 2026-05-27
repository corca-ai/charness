# Release Surface Check
Date: 2026-05-27

## Scope

Advanced `charness` toward release `0.9.0` (tag `v0.9.0`). This minor release
ships the first public version of the `achieve` goal-lifecycle skill, the #223
quality/achieve duplicate-test-pressure contract, test-regression fixes for the
unpushed find-skills/achieve stack, and a new `local-linux-aarch64-4cpu`
runtime budget profile.

## Current Version

- previous version: `0.8.0`
- target version: `0.9.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `current_release.py` reported no version drift across packaging and generated
  install surfaces (packaging manifest, claude plugin, codex plugin, claude
  marketplace all `0.9.0`; codex marketplace path-pinned).
- The release content's own changed-surface gates pass: `validate_skills`,
  `validate_public_skill_dogfood`, `validate_public_skill_validation`,
  `validate_packaging`/`validate_packaging_committed`, `check_doc_links`,
  `check_command_docs`, `check-markdown`, `check-secrets`,
  `validate_cautilus_proof`, `check_skill_ownership_overlap`,
  `validate_critique_artifacts`, `ruff`, and `test_goal_artifact_lib` (10
  passed). `check-runtime-budget` passes with the new aarch64 profile.
- The standing `./scripts/run-quality.sh --release` gate was NOT used as the
  publish gate on this host: its `pytest` phase fails for environment-only
  reasons (pytest-xdist parallel test-isolation flakiness — the affected tests
  pass in isolation — plus a cautilus `0.14.2` version mismatch), confirmed
  identical on an `origin/main` worktree in this environment and filed as #225.
  The release was published with `git push --no-verify` per explicit operator
  authorization; the env-only failures are not code regressions in this release.

## Release State

- local release mutation: complete
- branch/tag push: complete (pushed with `--no-verify`; pre-push standing gate
  bypassed for the documented #225 environment-only failures)
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.9.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend (`gh release view v0.9.0`).

## Review Proof

- Review proof: `charness-artifacts/critique/2026-05-27-release-0-9-0.md` (release-surface critique, bounded fresh-eye subagent).

## Open Risks

- #225 (pre-push quality gate non-deterministic under xdist + cautilus version
  drift) remains open; it is environment/test-hygiene, not a defect in this
  release's shipped surface.
- Real-host/fresh-checkout proof: the release adapter declares no
  fresh-checkout probes and no real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
