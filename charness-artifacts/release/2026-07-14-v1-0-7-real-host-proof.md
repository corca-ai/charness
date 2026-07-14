# v1.0.7 Real-Host Proof

- Release: v1.0.7
- Date: 2026-07-14
- Proof mode: maintainer-machine pre-publish tool checks, with post-publish
  `charness update` and installed reviewer-boundary readback reserved for the
  release helper boundary.

## Trigger

The v1.0.7 release delta changes `docs/host-packaging.md`, which matches the
release adapter's `real_host_required_path_globs`. The release-time checker
therefore reports `required: true`.

## Nose Initial And Detected State

`nose --version` and `charness tool doctor nose --json --no-write-locks` ran on
this maintainer machine. `nose` was already installed, so the missing-binary
branch was not recreated destructively.

- doctor status: `ok`
- doctor disposition: `ready`
- observed version: `0.18.0` (satisfies `>=0.17.0`)
- resolved binary: `/home/hwidong/.cargo/bin/nose`
- latest upstream release discovered by doctor: `v0.19.0`

## Install Route And Support Sync

`charness tool install nose --dry-run --json` reported the manifest-supported
upstream installer and current upstream metadata; no reinstall was needed for
the already-ready binary.

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/corca-ai/nose/releases/latest/download/nose-cli-installer.sh | sh
```

`charness tool sync-support nose --json` reported `skipped` because `nose` is
integration-only and has no materialized support-skill source.

## Quality Inventory

`python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`
completed with `status: clean`, `tool_version: 0.18.0`, and
`total_dup_lines: 0`. Its findings remain advisory refactoring candidates.

## Reviewer-Boundary Post-Publish Proof

Before the tag, the committed consumer test proves the exported package carries
the Claude envelope and resolves the fingerprint helper from the active skill
directory. After public visibility, the release helper must run `charness
update`; the final release artifact must then record installed version/readback
and preserve the distinction between Claude's packaged envelope and Codex's
native `explorer` path. It must not claim live Claude envelope binding or Codex
reviewer-tier application without a separate host signal.

## Result

All pre-publish maintainer-machine checks applicable to this release passed.
The only pending evidence is post-publish install refresh and installed-surface
readback, which require v1.0.7 to exist first.
