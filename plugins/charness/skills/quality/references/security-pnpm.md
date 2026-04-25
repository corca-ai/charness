# Supply-Chain Checklist: pnpm

This reference covers the pnpm lockfile and audit moves that matter to
`quality`.

## Offline Gate

- keep `pnpm-lock.yaml` checked in when the repo depends on pnpm-managed
  packages
- do not leave a stale `packageManager` field pointing at pnpm while only an
  npm lockfile is committed
- keep one JavaScript lockfile surface per repo root unless the repo has an
  explicit multi-root packaging contract

`<repo-root>/scripts/check_supply_chain.py` enforces the root-level alignment piece. It is
not a substitute for pnpm's live audit tooling.

## Manual Or Networked Follow-Up

- run pnpm's audit flow only where the team is prepared to triage advisory
  output; `<repo-root>/scripts/check_supply_chain_online.py` now wraps that path
  explicitly with `pnpm audit --json`
- review new registries, overrides, or workspace-wide patching rules with human
  judgment because those choices are trust-boundary changes, not only syntax
