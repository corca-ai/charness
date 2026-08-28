# Lane 3 brief: 745-spike-abi

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-745-rust-core-spike-plan.md`
(rev 2, D4/D5) and the ratified go verdict in
`charness-artifacts/design-studies/issue-745/verdict-2026-08-28.md`. The go
verdict authorizes exactly this: freezing the per-command ABI. Do not spawn
descendant agents.

## Outcome

One file, `native/repograph/ABI.md`, freezing the machine-facing contract
the #746/#747 children may depend on. Content, per command (`parse-corpus`,
`export-safe`, `match-surfaces`, `standalone-targets`):

1. Exact CLI input contract: every flag, argument, default, and repeatable
   flag, as implemented today.
2. Output schema: schema id (`repograph.<command>.v1`), every field with
   type and meaning, ordering guarantees (e.g. sorted-by-path file lists,
   manifest-declaration-order command dedup), and one REAL example document
   per command produced by actually running the release binary (trim long
   arrays to a few entries with an explicit `…` marker outside the JSON
   block, never inside a claimed-verbatim block — label trimmed examples as
   abridged).
3. Exit semantics table: 0/1/2/3/70 meanings per command, the per-command
   zero-scope and parse-failure rules, and the wrapper rule: compatibility
   wrappers must map exit 3 to a blocking code unless their gate label is
   explicitly unestablished-capable (`run-quality.sh` convention; never remap
   70 to 3).
4. Freeze statement: these four commands at `v1` are frozen — breaking
   changes require a new schema version; anything not documented here
   (library API, fixture layout, parity harness) is explicitly NOT frozen;
   there is no repository-wide universal verdict envelope.
5. Non-claims: no runtime-import proof; `standalone-targets` output carries
   `claim: "static-selection-only"`; the crate remains non-production until
   #746 promotes it.

Verify every documented flag and field against the actual source and real
runs — the document must describe the binary as built, not the plan. If you
find a discrepancy between plan rev 2 and the implementation, document the
implementation and flag the discrepancy in your result; do not change code.
Update the crate README to link ABI.md. Keep markdown lint-clean (repo-wide
markdown gate; ~80-col lines like the existing README, resolving links).

## Boundaries, stop condition, result shape

Touch only `native/**`. Build with `cargo build --release --offline` (cargo
cache provided via CARGO_HOME in your environment; network may also work).
No code changes; docs only. One coherent commit, prefix `spike(745):`.
Final message: confirmation that every example is a real captured output
(state the exact commands run), plus any implementation-vs-plan
discrepancies found.
