# Lane 2 brief: 745-spike-validators

Governing contract: read
`charness-artifacts/design-studies/2026-08-28-issue-745-rust-core-spike-plan.md`
(rev 2) first — especially D4 (exit classes), D5.2–D5.4 (command contracts),
D6 (parity bar and bug-for-bug lists), D8 (what the parity/bench harness must
produce). Lane 1 already landed the crate at `native/repograph/` (inventory,
panic-safe parser, `parse-corpus`); build on it. Do not spawn descendant
agents. Read the three Python owners before implementing:
`scripts/check_export_safe_imports.py`, `scripts/surfaces_lib.py`,
`scripts/check_standalone_imports.py`, plus `scripts/repo_file_listing.py`.

## Outcome

### 1. `repograph export-safe`

Reimplements `check_export_safe_imports.py` verdicts. Universe: the same four
non-recursive globs (`scripts/*.py`, `skills/public/*/scripts/*.py`,
`skills/support/*/scripts/*.py`, `skills/shared/scripts/*.py`) filtered
through the shared inventory snapshot (or `--file-list`). Detection must
replicate (read the Python for exact semantics):

- forbidden `from skills.public...` / `import skills.public...` module forms;
- `import_repo_module(script_file, "skills.public...")` calls with the
  owner's positional/keyword resolution, its exact-`ast.unparse`-equivalent
  acceptance of only `__file__` / `Path(__file__)`, and no `*args`/`**kwargs`
  handling;
- `REPO_ROOT`-rooted path expressions via `_chain_root_name`-equivalent
  unwrapping of Call/Attribute chains, both path-literal spellings
  (segmented and slash-joined), backslash normalization for matching only;
- `_probes_both_layouts` escape hatch: suppresses only the asset-path
  family, never the import checks, scoped per file.

Differences from the owner, fixed by plan D4/D6 (do not "fix" back):
report ALL violations (no fail-fast) sorted by (path, line); exit 1 on any
violation; exit 3 on zero in-scope files; exit 3 when any in-scope file has
parse status other than `parsed` (report those files in a typed
`unestablished` list — a non-parsed in-scope file must never yield exit 0).
Output one JSON document, `schema: "repograph.export_safe.v1"`, listing
violations with path, line, kind, and source text.

### 2. `repograph match-surfaces`

Reimplements `load_surfaces` + `match_surfaces` from `scripts/surfaces_lib.py`
over `.agents/surfaces.json` (path via `--surfaces <path>`, default
`.agents/surfaces.json` under `--repo-root`). Changed paths come only from
repeated `--path <p>` flags (no git-diff discovery in the spike). Replicate
exactly: Python `fnmatch.fnmatch` semantics — `*` DOES cross `/` (not glob
segment semantics: `dir/**/*.py` misses top-level `dir/file.py`), POSIX
case-sensitivity, `normalize_repo_path` including its naive `../`/`/` prefix
guard (do not add embedded-`..` rejection), matched-surface and
sync/verify-command dedup in manifest declaration order, numeric version
equality (`1.0` == 1 accepted), exact-string (not glob) generated-markdown
lookup if you expose it (optional — only `match_surfaces`/`load_surfaces`
parity is required). Exit 0 on success (matching zero surfaces is still 0),
exit 3 on unreadable/invalid manifest. Output
`schema: "repograph.match_surfaces.v1"` with matched surface ids and ordered
command lists.

### 3. `repograph standalone-targets`

The static-selection half of `check_standalone_imports.py`. Replicate its
8-pattern module enumeration (`__init__.py` excluded, globally sorted),
per-module import shapes (package-relative `import scripts.X` for top-level
`scripts/*.py`, sys-path direct `import X` otherwise — read the owner for the
exact rule), `--changed` handling with the empty-vs-omitted distinction
(explicitly-empty list exits 0 with a nothing-checked note; plan D4) and
first-occurrence-after-dedup ordering for changed output. Output
`schema: "repograph.standalone_targets.v1"`: the probe plan (module, shapes,
file path) plus top-level `claim: "static-selection-only"`. This command
never runs Python and never claims import side effects. Exit 0 unless the
inventory itself is unestablished (3).

### 4. Library: glob-consumer edges (small)

A library module (no CLI) that extracts glob/rglob literal-pattern consumer
edges from parsed Python (the `fixtures/glob_consumer.py` shape), with one
unit test. This pins the acceptance's glob-consumer category at edge level;
nothing more.

### 5. Violation-positive fixtures with exact expected sets (plan D6)

Extend `native/repograph/fixtures/` with an `expected/` scheme: for each
export-safe violation family above, a fixture file plus a checked-in JSON
expected-violation set; for match-surfaces, a small fixture manifest plus
path cases pinning: `*`-crosses-`/`, the #331 top-level-file miss under
`dir/**/*.py`, case sensitivity, declaration-order dedup, version `1.0`;
for standalone-targets, fixture trees pinning the 8-pattern selection
boundary, `__init__.py` exclusion, and `--changed` ordering. Every fixture
`.py` name snake_case; no secret-shaped strings.

### 6. Parity and bench harness: `native/repograph/parity/`

Python (stdlib only, run with `python3`), NOT wired into any repo gate:

- `run_parity.py` — runs fixture cases through both implementations where a
  Python owner can accept the same scope, and whole-repo comparisons for all
  three commands (each side in its production acquisition mode; compare
  verdict, exit class, and load-bearing fields per plan D6; for export-safe
  detection on multi-violation fixtures, enumerate the fail-fast owner's
  full set by re-running with each reported offender excluded, then compare
  as set equality). Emits one JSON difference report to stdout; every
  difference carries the fields needed for a ledger disposition (command,
  case, python result, rust result).
- `run_bench.py` — implements plan D8: per comparison 3 cold + 3 warm runs
  of both sides in production mode, capturing wall time, user+sys CPU, peak
  RSS via `/usr/bin/time -v`, analyzed-file count, plus repo identity (HEAD
  SHA, porcelain hash), host identity (`uname -a`, CPU model), and build
  identity (rustc version, release profile). Benchmarks invoke the release
  binary. Emits one JSON report. Python sides: `check_export_safe_imports.py`
  (direct), `check_standalone_imports.py` full sweep (NOTE: this owner runs
  live import subprocesses — benchmark only its selection phase if it can be
  isolated without modifying the script; otherwise benchmark
  `--changed`-scoped selection and record that bound honestly in the
  report), and for surfaces use `scripts/check_changed_surfaces.py --paths
  <sampled paths>` vs `match-surfaces --path ...` on the same path sample.
  Do NOT modify any file outside `native/`.

The harness must be runnable by the parent as:
`python3 native/repograph/parity/run_parity.py --repo-root .` and
`python3 native/repograph/parity/run_bench.py --repo-root .` from the repo
root, each printing its JSON report. Keep runs bounded (bench sample sizes
chosen so one full harness run stays under ~10 minutes).

## Verification to run before finishing

- `cargo test --offline`, `cargo fmt -- --check`,
  `cargo clippy --offline --all-targets -- -D warnings`,
  `cargo build --release --offline` — all green.
- `run_parity.py` full run: report the difference count and include the
  differences verbatim in your final message (do NOT disposition them —
  the parent owns dispositions).
- `run_bench.py` once: include the summary numbers.

## Hard boundaries and non-claims

- Touch only `native/**`. Never modify the Python owners, `scripts/`,
  `.agents/`, docs, or gates.
- Network may be available; if you need a new crate dependency, justify it
  in one line in the result and exact-pin it. Prefer none.
- Do not claim runtime import proof, do not add an ABI.md (parent decision,
  go-verdict only), do not touch `what_reads_this.py` parity.
- If a Python owner behavior is ambiguous after reading the source, pick
  the reading the source supports, add a fixture pinning it, and flag it in
  the result — do not silently guess.

## Stop condition and result shape

Stop when the verification steps pass in your worktree; one coherent commit,
message prefix `spike(745):`. Final message: what was built, exact commands
with observed results, the full parity difference list, bench summary, any
new dependency pins, and any deviation from this brief with its reason.
