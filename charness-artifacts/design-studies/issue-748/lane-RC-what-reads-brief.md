# Lane brief: 748-what-reads (lane RC)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
(rev 2), decision D5 (normative, NARROWED: path-target only — the
`--symbol`/`--config-key` modes are deliberately retired and must NOT
be ported), and the Python owner `scripts/what_reads_this.py` (read in
full; its `--path` behavior is the contract except where D5 adds or
changes). A sibling Rust lane (`748-plugin-refs`) runs concurrently in
its own worktree on the same crate — keep changes additive: new
module(s), one dispatch arm in `lib.rs`, fixtures under
`native/repograph/fixtures/what_reads/`; the parent reconciles
`lib.rs`/`ABI.md` unions. Do not spawn descendant agents.

## Outcome

1. New additive command `repograph what-reads --path P
   [--repo-root PATH] [--file-list PATH] [--include-mirrors]
   [--detail]` emitting `repograph.what_reads.v1`:
   - Inventory: the common one-snapshot rules; scan universe filtered
     by the Python owner's text-suffix allowlist and fixed exclusion
     dirs (`.git`, `__pycache__`, `.pytest_cache`, `node_modules`,
     `mutants`, `.charness`); `plugins/**` excluded unless
     `--include-mirrors` (transcribe the exact lists from
     `what_reads_this.py:56-109`).
   - Path evidence kinds, preserving the Python taxonomy and
     semantics: `literal-path` (literal substring), `glob-consumption`
     (anchored quoted glob containing `/`, compiled with PATH
     semantics — `*` does not cross `/`), `basename-glob` (unanchored
     basename-only glob, with the too-generic filter), and
     `basename-reference` (weak fallback). Glob scanning restricted to
     source/config/test surfaces as the owner does.
   - NEW `command-carrier` evidence kind: a hit whose file+line
     corresponds to a `carrier-path-reference` record (or a resolved
     `invokes` edge target equal to P) from the crate's carrier
     extraction is reported as `command-carrier` instead of bare
     `literal-path` — the capability the Python owner lacked.
   - NEW typed `graph` section: direct dependents of P (reverse
     `imports`/`invokes` edges) and up to three shortest root paths —
     reuse the existing `explain` projection code; do not fork it.
   - `unscanned_surfaces` (port the caveat list including the mirror
     note, git-history/external/runtime-composed/binary/extension
     caveats, extension-only and prose-glob notes) and
     `zero_result_caveat` preserved. `--detail` adds per-file hit
     lists with line and source.
   - Output is one JSON document (contract change from YAML is
     ratified; no automated consumers exist). Exits: 0 report emitted
     (zero hits is still 0, carrying the caveat), 2 usage, 3
     inventory/unestablished, 70 internal.
2. Fixtures: literal/glob/basename hits across `.py`, `.sh`, `.md`,
   `.yaml`, `.json`; a PATH-semantics negative (a glob that would
   match only if `*` crossed `/` must not match); a too-generic-glob
   negative; a command-carrier hit (path referenced in a git-hook-like
   carrier) classified `command-carrier`; a mirror-exclusion case
   flipped by `--include-mirrors`; a zero-hit query pinning
   `zero_result_caveat` and `unscanned_surfaces`; a graph-section case
   (a file imported by another and reached from a root).
3. `ABI.md` gains the `what-reads` section (input, schema with every
   evidence kind, exit table, and a NON-CLAIM line: this command is
   lexical/graph evidence, not proof of runtime consumption; retired
   symbol/config-key modes are named as deliberately not ported).

## Boundaries

Only `native/repograph/**`. Frozen v1 ABIs unchanged. Do NOT port
`--symbol`/`--config-key`, the AST-context symbol classifier, or the
lexical fallback module — they are retired with the Python owner, not
migrated. No Python deletion in this lane (a later Python lane owns
that). Markdown fixtures markdownlint-clean; no `key`/`token`/`secret`
member names.

## Verification

Run in `native/repograph`: `cargo fmt --check`,
`cargo clippy -- -D warnings`, `cargo test`, `cargo build --release`.
ALSO run the built binary once on the real repository for one known
path (`--path scripts/surfaces_lib.py`) and report the output verbatim
next to `python3 scripts/what_reads_this.py --path
scripts/surfaces_lib.py` — evidence for the parent's evidence-
preservation check, not a committed test.

## Stop condition and result shape

One coherent commit, prefix `topo(748):`. Final message: what was
built, commands run with observed results including the real-repo
comparison, and every deviation from this brief with its reason.
