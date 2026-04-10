# Supply-Chain Checklist: pnpm

Use this when a repo declares `packageManager: "pnpm@..."` or keeps
`pnpm-lock.yaml`.

## Offline Gate

- keep `pnpm-lock.yaml` checked in when the repo depends on pnpm-managed
  packages
- do not leave a stale `packageManager` field pointing at pnpm while only an
  npm lockfile is committed
- keep one JavaScript lockfile surface per repo root unless the repo has an
  explicit multi-root packaging contract

`scripts/check-supply-chain.py` enforces the root-level alignment piece. It is
not a substitute for pnpm's live audit tooling.

## Manual Or Networked Follow-Up

- run pnpm's audit flow only where the team is prepared to triage advisory
  output
- review new registries, overrides, or workspace-wide patching rules with human
  judgment because those choices are trust-boundary changes, not only syntax
