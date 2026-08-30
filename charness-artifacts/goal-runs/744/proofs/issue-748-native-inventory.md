# Issue #748 Native Inventory Readback

Date: 2026-08-30
Provider source: `ad17d9ef3c4f86a3221a93169096ff37ccdccefc` (native tree unchanged through `e7a7d2f25b2839b3c392789fb44d3fad2d2c2fcf`)

Command:

```text
native/repograph/target/release/repograph inventory --repo-root . --regular-files-only
```

Bound summary:

```json
{
  "schema": "repograph.inventory.v1",
  "status": "established",
  "regular_files_only": true,
  "path_count": 6880,
  "paths_listed": 6882,
  "dropped_by_stat": 2,
  "listing": "git",
  "unestablished": null
}
```

The executed binary SHA-256 was `bd7175eea6d1a662b69f62808eba74ebd20abf4de888b3eff115a6b336a0d2ea`. The published parity and owner-removal evidence remains `charness-artifacts/design-studies/issue-748/evidence-748.md`.

The local default Rust compiler was 1.93 while the crate declares 1.96, so rebuilding through unqualified local `cargo` was unavailable. This readback executes the repository's existing release binary; Quality Core had already provisioned and tested the native crate at exact provider main. It does not claim a fresh local rebuild, release artifact, consumer export, submodule behavior, or complete migration of the two explicitly deferred Python owners.
