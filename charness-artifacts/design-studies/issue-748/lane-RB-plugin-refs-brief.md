# Lane brief: 748-plugin-refs (lane RB)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
(rev 2), decision D6 (normative), and the Python owner being ported:
`scripts/check_plugin_dir_references.py` (read it in full; its behavior
is the contract except where D6 states a delta). A sibling Rust lane
(`748-what-reads`) runs concurrently in its own worktree on the same
crate — keep changes additive: new module(s), one dispatch arm in
`lib.rs`, fixtures under `native/repograph/fixtures/plugin_refs/`,
minimal edits elsewhere; the parent reconciles `lib.rs`/`ABI.md`
unions. Do not spawn descendant agents.

## Outcome

1. New additive command `repograph plugin-refs [--repo-root PATH]
   [--file-list PATH]` emitting `repograph.plugin_refs.v1`:
   - Discover `plugins/<pkg>/` package roots from the inventory (no
     hardcoded package name).
   - Scan the same doc-glob set as the Python owner
     (`README.md`, `AGENTS.md`, `docs/**/*.md`, `presets/**/*.md`,
     `profiles/**/*.md`, `skills/**/*.md`) for `<plugin-dir>/TARGET`
     references OUTSIDE fenced code blocks and inline code, matching
     the Python `markdown_doc_scan.iter_doc_lines` skipping semantics
     (read that module and transcribe its rules — fences, comment
     lines; pin them with fixtures).
   - Classify each reference: resolved (exists under some
     `plugins/<pkg>/TARGET` in the inventory), `templated` (`<`, `>`,
     or ellipsis in TARGET — counted, not a finding),
     `escapes-package-root` (absolute or `..`), `missing`.
   - Port the `<authoring-repo>/TARGET` shipped-but-marked-
     authoring-only check over `skills/**/*.md`: a reference that
     resolves under the installed spellings
     (`skills/public/<s>/` → `skills/<s>/`, `skills/support/<s>/` →
     `skills/<s>/`) inside a shipped package is a finding. Reuse the
     crate's existing mirror-rule constants where they already encode
     the flatten; do not invent a second rule table.
   - Report: typed findings with path, line, reference text, and
     classification; counts per class; the package set validated.
   - Exits: 0 validated (including the typed
     "no plugins package; nothing was validated" note — ABI.md must
     record WHY this zero-scope is exit 0 unlike export-safe's: a tree
     without a plugins package is a legitimate consumer-tree shape,
     not a collapsed selection universe), 1 findings, 2 usage, 3
     inventory/unestablished, 70 internal.
2. Fixtures: a doc tree with resolved/templated/escaping/missing
   `<plugin-dir>/` references (including fenced/inline-code negatives
   that must NOT match), an `<authoring-repo>/` shipped-file finding
   plus a legitimately authoring-only reference (non-finding), and a
   no-plugins-package tree. Expected JSON documents committed.
3. `ABI.md` gains the `plugin-refs` section (input, schema, exit
   table, the zero-scope rationale); usage string updated if the
   dispatch list line changes.

## Boundaries

Only `native/repograph/**`. Frozen v1 ABIs unchanged. No Python
deletion or rewiring in this lane (a later Python lane owns that).
Markdown fixtures markdownlint-clean; no `key`/`token`/`secret` member
names.

## Verification

Run in `native/repograph`: `cargo fmt --check`,
`cargo clippy -- -D warnings`, `cargo test`,
`cargo build --release`. ALSO run the built binary once against the
real repository root and compare the verdict direction with
`python3 scripts/check_plugin_dir_references.py --repo-root .`
(both should validate today's tree; report both outputs verbatim —
this is evidence for the parent, not a committed test).

## Stop condition and result shape

One coherent commit, prefix `topo(748):`. Final message: what was
built, commands run with observed results including the real-repo
comparison, and every deviation from this brief with its reason.
