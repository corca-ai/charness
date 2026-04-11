# Supply-Chain Checklist: npm

This reference covers the npm lockfile and audit moves that matter to
`quality`.

## Offline Gate

- keep `package-lock.json` checked in when dependencies are declared
- avoid multiple JavaScript lockfiles in the same repo root unless the repo is
  explicitly split into separate package-manager domains
- keep `packageManager: "npm@..."` aligned with the checked-in lockfile when
  the field is present

`scripts/check-supply-chain.py` owns those checks for the current `charness`
bar.

## Manual Or Networked Follow-Up

- run npm's advisory flow when dependency changes matter enough to justify a
  live registry lookup
- review new scopes or publishers before promoting them into standing runtime
  dependencies
- keep high-noise online audit commands out of the default local gate unless
  maintainers agree on when to read and act on the output
