# Lane brief: 748-classify-optional (lane RA)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
(rev 2), decision D8 first bullet, and `native/repograph/ABI.md`'s
`classify` section. A sibling Python lane runs concurrently in its own
worktree but touches no `native/**` path; keep this lane additive inside
the crate anyway (no reshuffling of existing modules). Do not spawn
descendant agents.

## Outcome

1. `repograph classify` accepts a new flag `--surfaces-optional`:
   - With the flag, when the surfaces manifest does NOT exist (default
     `.agents/surfaces.json` or an explicitly supplied path),
     classification proceeds with an empty surface set and the report
     carries a typed top-level marker `surfaces: "absent"`. Per-path
     `surfaces` arrays are empty. Role classification, presence
     semantics, exits (0, or 3 for unestablished roles) are otherwise
     unchanged.
   - The flag tolerates ABSENCE only: an existing-but-invalid manifest
     (unreadable, bad JSON, failed validation) stays the current hard
     exit-3 diagnostic, flag or no flag.
   - WITHOUT the flag, behavior is byte-identical to today for every
     input (absence stays a hard exit-3 diagnostic without a report).
   - When the manifest exists and loads, reports are byte-identical
     with and without the flag (no `surfaces` marker key in that case,
     or `surfaces: "loaded"` — pick ONE, document it in ABI.md, and pin
     it; prefer omitting the key when the manifest loaded so existing
     report consumers see zero difference).
2. Fixture/test coverage in `native/repograph/tests/classify.rs` (or a
   new sibling test file):
   - absent manifest + flag → report emitted, marker present, role
     rules still applied, exit per unestablished census;
   - absent manifest, no flag → current failure pinned (no report,
     exit 3);
   - invalid manifest + flag → exit 3 diagnostic (absence-only
     tolerance pinned);
   - present manifest + flag → byte-identical to no-flag run.
3. `ABI.md` `classify` input table, output schema, and exit semantics
   updated in the same change; the top-level usage string updated only
   if it enumerates per-command flags (it does not today — verify).

## Boundaries

Only `native/repograph/**`. Frozen v1 ABIs unchanged. Do not add the
flag to `changed`, `graph`, `components`, or `explain` (no consumer;
additive later if one appears — record nothing). No new dependencies.
Digest-ish fixture values non-hex-looking; no `key`/`token`/`secret`
member names; fixture `.py`/`.md` constraints per the template.

## Verification

Run in `native/repograph`: `cargo fmt --check`,
`cargo clippy -- -D warnings`, `cargo test`,
`cargo build --release --offline || cargo build --release`. The parent
re-runs the battery and the whole-repo classify census after
integration; lane self-report is not integration proof.

## Stop condition and result shape

One coherent commit, prefix `topo(748):`. Final message: what was
built, commands run with observed results, and every deviation from
this brief with its reason. Stop at the stated outcome.
