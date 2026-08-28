# Lane 1 brief: 745-spike-core

Governing contract: read
`charness-artifacts/design-studies/2026-08-28-issue-745-rust-core-spike-plan.md`
(rev 2) first; it overrides any inference you make. This lane implements plan
decisions D1, D2, D3, D5.1, and D7. Do not spawn descendant agents.

## Outcome

A building, tested, non-production Rust crate at `native/repograph/` with:

1. `Cargo.toml` — package `repograph`, one library plus one binary target
   named `repograph`. Dependencies exact-pinned: `ruff_python_parser`,
   `ruff_python_ast`, and (if needed) `ruff_text_size` / `ruff_source_file`
   all `=0.0.11`; `serde = { version = "=1.0.219", features = ["derive"] }`;
   `serde_json = "=1.0.140"`; optionally `tempfile = "3"` for tests. No
   other dependencies — the sandbox has NO network; exactly these crates
   (and their transitive deps) are pre-cached in the `CARGO_HOME` already
   exported in your environment. Arg parsing is hand-rolled. Set
   `CARGO_NET_OFFLINE=true` is already exported; add `--offline` to cargo
   invocations if any command still tries the network. Commit `Cargo.lock`.
   Add `rust-toolchain.toml` pinning `channel = "1.96.0"` (installed on
   this host; the ruff 0.0.11 crates require rustc >= 1.96). Rust edition
   2021 or 2024.
2. Inventory module (plan D3): builds a `FileInventory` from exactly one
   `git ls-files -z --cached --others --exclude-standard` execution per
   process, or from `--file-list <path>` (NUL-separated repo-relative
   paths). No other filesystem walking anywhere. If git listing fails and no
   `--file-list` was given: typed failure on stderr, exit 3. Exit classes
   (plan D4): 0 ok, 2 CLI usage error, 3 unestablished, 70 internal error
   (wrap panics at the top level; never exit 3 for a bug).
3. Parser module (plan D1): per-file parse via `ruff_python_parser` inside
   `catch_unwind`. Per-file typed status:
   `parsed | parse-error | unsupported-syntax | panicked | unreadable`
   (unreadable = cannot read or not valid UTF-8), with a one-line typed
   detail (error kind + location where available).
4. `repograph parse-corpus` subcommand: flags `--repo-root <path>` (default
   cwd), `--file-list <path>` (optional), `--exclude-prefix <prefix>`
   (repeatable; default exactly one: `plugins/`). Selects every `.py` file
   in the inventory outside excluded prefixes and parses each. Output: one
   JSON document on stdout:
   `{"schema":"repograph.parse_corpus.v1","repo_root":...,"listing":"git"|"file-list","files_total":N,"parsed":N,"failed":N,"files":[{"path":...,"status":...,"detail":...}...]}`
   — `files` contains an entry for EVERY selected file, sorted by path
   (byte-wise string sort of the repo-relative POSIX path). A selected file
   missing from `files` is a defect. Exit 0 when every file is `parsed`,
   exit 3 when any file is not (the corpus claim is then unestablished).
5. Fixture corpus at `native/repograph/fixtures/` (plan D7) as a small fake
   repo tree (NOT a git repo; consumed via `--file-list`), covering:
   ordinary imports, dynamic/path imports (`import_repo_module(__file__,
   "pkg.mod")` call shape and `sys.path.insert` + import), a
   `if __name__ == "__main__"` direct-execution script, a glob-consumer
   (a `.py` calling `glob`/`rglob` with a literal pattern), a generated
   mirror pair (same content, `plugins/`-style prefix), an import cycle
   (two modules importing each other), a test-only root (a `test_*.py`
   importing a module nothing else imports), malformed source (one syntax
   error file, one non-UTF8-bytes file, one null-byte file), an empty
   `.py`, an extensionless Python script with shebang, and symlinks (to a
   file, to a directory, dangling — create with relative targets so they
   survive checkout). Every fixture `.py` filename is snake_case (a
   repo-wide filename gate scans `**/*.py`). No high-entropy secret-shaped
   strings anywhere (gitleaks scans all tracked files).
6. Tests (`cargo test`): at minimum — parse-corpus over the fixture
   file-list asserts the malformed files each appear with their exact
   expected status and that `files` length equals the input selection
   count; inventory refuses (exit-3 path) when git is unavailable and no
   file list is given; the panic-to-`panicked` path is exercised with a
   unit test (simulate a panicking parse via a test seam if no real
   panicking input is available — do not depend on finding a real ruff
   panic input).
7. Quality: `cargo fmt` applied; `cargo clippy` warning-free (allow
   documented exceptions with a comment); `cargo build --release` succeeds.
8. Update `native/repograph/README.md` with build/run/test instructions
   (keep lines under 100 chars; a repo-wide markdown lint scans all tracked
   `.md`; keep links resolving).

## Verification to run before finishing

- `cargo test` and `cargo build --release` in `native/repograph/`.
- `target/release/repograph parse-corpus --repo-root <worktree-root>` over
  the real repo: report `files_total` (expected ~1,284 canonical files) and
  confirm exit 0 with zero non-`parsed` entries.
- `parse-corpus --file-list` over the fixture list: confirm exit 3 with the
  malformed files typed correctly.

## Hard boundaries and non-claims

- Touch only paths under `native/`. Do not modify, create, or delete
  anything outside `native/` — no root `.gitignore` edits, no scripts, no
  docs, no CI. `native/.gitignore` already ignores `target/`.
- Do not implement export-safe, match-surfaces, standalone-targets, import
  edges, or benchmarks — lane 2 owns those. Build the inventory/parser
  layers so lane 2 can consume them, but do not speculate APIs beyond what
  parse-corpus needs.
- Do not claim runtime import behavior; this is static parsing only.
- If crates.io is unreachable from the sandbox, stop and report that as the
  blocker in your result instead of vendoring or downgrading dependencies.

## Stop condition and result shape

Stop when the verification steps above pass in your worktree; commit your
work to the lane branch as one coherent commit (message prefix
`spike(745):`). Final message must state: what was built, exact commands
run with their observed results (including real-repo `files_total` and the
fixture exit-3 confirmation), the exact crate versions pinned, and any
deviation from this brief with its reason.
