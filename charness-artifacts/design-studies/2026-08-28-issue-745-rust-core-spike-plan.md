# Issue #745 spike plan: Rust repository-analysis core

> Status: rev 2 (post-critique; contract-angle and scope-angle reviews applied)
> Date: 2026-08-28
> Parent: #744 umbrella; this plan governs only the #745 spike
> Base: 533f24dad (main)
> Critique records: `../critique/2026-08-28-issue-745-spike-plan-contract.md`,
> `../critique/2026-08-28-issue-745-spike-plan-scope.md`

## Objective

Prove or refute, with recorded evidence, that one typed Rust crate can own the
repository inventory and enough typed edges to replace the representative
Python validators at verdict parity and >=3x static-family speedup, and (on a
go verdict) freeze the per-command JSON ABI the #746/#747 children need. A
no-go or redesign verdict is an acceptable, complete outcome.

## Decisions

### D1. Parser: `ruff_python_parser` + `ruff_python_ast`, exact-pinned

Survey evidence (2026-08-28): actively maintained (0.0.11), MIT, error-recovery
model returns best-effort AST plus typed `Vec<ParseError>` /
`UnsupportedSyntaxError` — matching the acceptance rule that parse errors are
typed unestablished results, never silent node loss. Production users: ruff,
Pyrefly, ty. Risks and mitigations:

- 0.0.x unstable API → exact `=0.0.x` pins in `Cargo.toml`, `Cargo.lock`
  committed. The pin is convention-enforced (no repo gate reads Cargo
  manifests; the supply-chain gate knows only JS/Python surfaces) — acceptable
  for a non-production spike.
- Confirmed panic class in the wild (Pyrefly #1559) → every per-file parse
  runs inside `catch_unwind`; a panic becomes a typed
  `parse-status: panicked` result for that file and the run continues.
- Comments are token-level, not AST → the spike does not claim comment
  attachment; no representative validator needs it.

Rejected: `rustpython-parser` (stale, upstream says superseded), `tree-sitter`
(syntax errors never surface as `Result::Err`; silent-clean-parse hazard),
`libcst` native (no error recovery; whole-file abort granularity),
PyO3/CPython wrappers (defeats the point). Corpus fit confirmed by Appendix A
(language floor 3.10; ruff parses a superset grammar).

### D2. Crate placement: `native/repograph/`, one crate, non-production

One crate: library modules plus one machine-facing binary `repograph`
(JSON out). Placement under a new top-level `native/` keeps it out of every
glob-scoped gate; verified: standalone/export-safe patterns, ruff path list,
py-compile globs, pytest `testpaths`, vulture, shell checks, and every
`.agents/surfaces.json` pattern cannot match `native/**`. Three repo-wide
tracked-file scans still bind native content and are constraints, not
blockers: `check_python_filenames.py` (all `**/*.py` names must be
snake_case), markdown/link checks (crate `README.md` and any `.md` must be
lint-clean with resolving links), and gitleaks (no secret-shaped fixture
strings). Non-production markers: crate README states spike status; no gate,
hook, skill, or export references it. `native/.gitignore` containing
`target/` is committed **before** the first `cargo build` anywhere (an
unignored `target/` is instantly visible to the secrets tar sweep and
changed-path collectors); the root `.gitignore` is deliberately untouched (it
is a `repo-python` surface source path whose edit triggers that surface's
full verify battery). `native/` is not ignored wholesale — evidence documents
cite tracked files in it. Promotion or deletion is a #746 decision.

### D3. File universe: one snapshot, injected or acquired once

The library consumes a `FileInventory` built from exactly one
`git ls-files -z --cached --others --exclude-standard` execution per process
(or from `--file-list <path>` NUL-separated input for tests/parity injection).
Subcommands never walk the filesystem independently. There is no silent
filesystem-walk fallback: if git listing fails and no `--file-list` was
given, the result is a typed unestablished failure (exit 3). This replaces
two distinct Python fallback behaviors, recorded in the disposition ledger as
one intentional contract change: `iter_matching_repo_files` falls back to an
unfiltered pattern glob (gitignore-blind, unreported), and `what_reads_this`
falls back to `rglob` but does report `listing: "filesystem-walk"`.

Known non-derivable exception, recorded as an intentional contract change:
when `CHARNESS_SUPPORT_DIR` (or the exported layout) relocates
`skills/support` outside the repo, `check_export_safe_imports.py`'s
`skills/support/*/scripts/*.py` pattern globs that external directory with no
git filter, so its universe is not derivable from any one repo snapshot. The
spike does not reproduce external-support relocation; a fixture pins that
this exclusion is chosen, not discovered.

### D4. ABI: per-command JSON, versioned, no universal envelope

Each subcommand owns its input flags, its output JSON schema, and its exit
semantics. Shared conventions only: UTF-8 JSON on stdout, one document per
run; diagnostics on stderr; `schema` field naming the per-command schema id
and version (e.g. `repograph.export_safe.v1`). Exit classes align with the
repo's existing typed convention (`run-quality.sh` freezes
`3 = unestablished`, `4 = partial`; those bytes are not ours to redefine):

- `0` — analysis completed, verdict pass (or pure-report command completed)
- `1` — analysis completed, verdict fail (violations found)
- `2` — CLI usage error (matches argparse convention)
- `3` — could not be established (git listing unavailable, unreadable
  manifest, zero-file scope where the Python owner refuses)
- `70` — internal repograph error (EX_SOFTWARE; never 3, so a crash can
  never be laundered into a non-blocking unestablished reading)

Frozen rules for verdict commands:

- Any in-scope file that did not parse (parse-error/panicked/unreadable)
  forces a non-pass exit: the command reports the typed per-file failures and
  exits 3. The Python owners exit 1 here; the difference is a ledger-recorded
  intentional contract change, and the ABI states that compatibility wrappers
  must map 3 to a blocking code unless their gate label is explicitly
  unestablished-capable.
- Zero-scope semantics are per-command and mirror the owner: `export-safe`
  with zero files is non-pass (exit 3; Python refuses with 1);
  `standalone-targets` with an explicitly-empty `--changed` list exits 0 with
  a nothing-checked scope note (Python exits 0; a blocking mapping here would
  regress the commit gate).

`ABI.md` (exact input flags, output schemas with examples, exit mapping per
command, for the four D5 commands) is written only on a go verdict; on no-go
the parity fixtures remain the de facto schema record and nothing is frozen.

### D5. Representative command scope (four commands)

1. `repograph parse-corpus` — parse every `.py` in the universe (default
   excludes the `plugins/` mirror prefix; flag-overridable); report per-file
   `parsed | parse-error | unsupported-syntax | panicked | unreadable` with
   typed detail. A file missing from the output is a spike failure.
2. `repograph export-safe` — reimplements `check_export_safe_imports.py`
   verdicts: the forbidden `skills.public` import forms, the
   `import_repo_module` call form (positional/keyword resolution, exact
   `__file__` / `Path(__file__)` `ast.unparse`-equivalent matching, no
   `*args`/`**kwargs` handling), `REPO_ROOT` path expressions with
   `_chain_root_name`-equivalent unwrapping of Call/Attribute chains, both
   path-literal spellings with backslash normalization for matching only, the
   four-glob non-recursive universe, and the `_probes_both_layouts` escape
   hatch that suppresses **only the asset-path family, never the import
   checks**, scoped per file.
3. `repograph match-surfaces` — reimplements `surfaces_lib.match_surfaces` +
   `load_surfaces` over `.agents/surfaces.json`: fnmatch-exact semantics
   (`*` crosses `/`, case-sensitive POSIX), manifest-declaration-order dedup,
   numeric-equality version check, changed paths injected via `--paths`.
4. `repograph standalone-targets` — static selection half of
   `check_standalone_imports.py`: enumerate modules from the 8-pattern list
   (`__init__.py` excluded), compute import shapes, emit the probe plan with
   `claim: "static-selection-only"`. The runtime probe stays Python; the
   spike narrows it and never claims static proof of import side effects.
   `--changed` empty-vs-omitted distinction preserved; `--changed` ordering
   follows first-occurrence insertion order after dedup.

Descoped, recorded in the ledger and the #745 closeout as an intentional
scope bound (not silent truncation): `what_reads_this.py` CLI parity in all
three target modes. Rationale: the tool has no automated consumers (only its
own pinning tests), so its parity informs neither the 3x gate nor
deletability; no deletion of it is claimed by the spike. Glob-consumer and
literal-path consumer **edges** are still modeled in the library and
exercised by the D7 fixture categories the acceptance names; the
explanation-command surface is #746+ scope.

### D6. Parity bar: parsed-structure equivalence, not byte equality

The automated consumers of the owners parse output or read exit codes; none
diff raw text. Parity compares: verdict, exit-code class, and the
semantically load-bearing fields (violation file/line sets, matched surface
ids, command lists in manifest order, target/shape lists). YAML formatting,
key order, and stderr prose are out of scope. Bug-for-bug resolution:

- Replicate: fnmatch `*`-crosses-`/`; declaration-order dedup; `--changed`
  empty-vs-omitted; four-glob non-recursive universe; asset-family-only
  escape hatch; exact-`ast.unparse` argument matching.
- Do not replicate, ledger as intentional contract change: silent/reported
  filesystem fallbacks (D3); external-support universe (D3); fail-fast
  single-violation reporting (repograph reports all violations); overloaded
  exit-1 (D4); parse-failure exit class (D4); traceback-vs-clean-message
  stderr shapes.
- Out of scope (lives in surviving Python CLI wrappers): the `--paths`
  falsy-vs-None inconsistency in `check_changed_surfaces.py` /
  `select_verifiers.py`; PyYAML formatting.

Detection parity is fixture-carried, not membership-carried: for every
violation family (each forbidden import form, the `import_repo_module` form,
both path-literal spellings, escape-hatch suppression and its import-check
non-suppression), a violation-positive fixture carries a curated exact
expected violation set, compared as a **set equality** on both sides — the
Python side enumerated by re-running the fail-fast owner with each reported
offender excluded until it passes. Whole-repo comparison (currently green on
both sides) proves universe agreement, not detection; the ledger says so.
Every fixture and whole-repo verdict difference is recorded in
`charness-artifacts/design-studies/issue-745/parity-ledger.md` with a
disposition: `equivalent | intentional-contract-change | blocker`.

### D7. Fixture corpus

`native/repograph/fixtures/` checked in, covering (per acceptance): ordinary
imports, dynamic/path imports (`import_repo_module`, `sys.path` insert),
direct execution, glob consumers, generated mirrors, import cycles, test-only
roots, malformed source (syntax error, non-UTF8 bytes, null bytes), symlinks
(to file, to dir, dangling), empty files, extensionless scripts, and the
violation-positive families of D6. Constraints from repo-wide scans: every
fixture `.py` filename is snake_case (`check_python_filenames.py` scans
`**/*.py` repo-wide; name-shape traps use non-`.py` extensions passed via
`--file-list`); no high-entropy secret-shaped strings (gitleaks). Malformed
fixtures must appear in `parse-corpus` output as typed non-parsed entries,
**and** a malformed in-scope file must force `export-safe` to non-pass —
both asserted by tests. The repo itself contains no malformed `.py`
(Appendix A), so these synthetic fixtures are the only exercise of the typed
failure path: mandatory, not optional.

### D8. Benchmark protocol and go/no-go

Both implementations run in their production acquisition mode — each performs
its own `git ls-files` (no injected list on either side), so repograph pays
the acquisition cost D3 assigns it. Identity checks instead of injection:
analyzed-file counts must match, plus recorded repo identity (HEAD SHA +
`git status --porcelain` hash), host identity (`uname -a`, CPU model), and
build identity (rustc version, cargo release profile — benchmarks run the
release binary only). Comparisons: `check_export_safe_imports.py` vs
`export-safe`; surfaces matching via its thinnest CLI consumer vs
`match-surfaces`; static selection vs `standalone-targets`. Per comparison:
3 cold + 3 warm runs, wall time, CPU time (user+sys), peak RSS
(`/usr/bin/time -v`), analyzed-file count.

Go condition — all of:

- every comparison in the static family is >=3x faster in wall time
  (worst-case reading, not an average), and
- the parity ledger has no undispositioned entry and no `blocker`, and
- deletability holds per owner, defined as: `check_export_safe_imports.py` —
  whole script deletable behind a thin wrapper; `surfaces_lib.py` —
  match/load engine deletable with CLI consumers repointed;
  `check_standalone_imports.py` — static discovery half deletable, runtime
  probe loop rehosted to consume the repograph probe plan;
  `what_reads_this.py` — no deletion claimed (explicitly retained in Python).

Otherwise the spike closes with a recorded no-go/redesign decision.
Peak-RSS and CPU are evidence, not gate inputs. All benchmark and parity
outputs are copied into `charness-artifacts/design-studies/issue-745/`;
evidence documents never cite gitignored `target/` paths (the spec-evidence
durability gate scans design-studies markdown and fails such citations).

### D9. Runtime-smoke honesty

`standalone-targets` output includes `claim: "static-selection-only"`; the
spike never reports a runtime import as proven. Narrowing is measured as:
statically-selected probe plan size vs the full sweep, with the remaining
runtime probe count reported as the honest residual cost.

## Execution shape

Parent (this session) owns design, integration, adversarial verification,
whole-repo parity runs, ledger dispositions, benchmark execution, and the
go/no-go verdict. Implementation goes through serialized `charness task run`
Codex lanes (model fixed `gpt-5.6-luna`, effort `xhigh`), each with an
explicit scope and prompt file; the parent reviews the retained worktree and
integrates before the next lane starts.

- Lane 1 `745-spike-core`: crate skeleton, inventory module (D3), parser
  integration with catch_unwind (D1), `parse-corpus` command, fixture corpus
  (D7), tests. Scope: `native/**` only (`native/.gitignore` is committed by
  the parent beforehand).
- Lane 2 `745-spike-validators`: `export-safe`, `match-surfaces`,
  `standalone-targets`, the import-edge extraction they share,
  fixture-level parity tests with exact expected sets, and the Python-side
  parity/bench harness under `native/repograph/parity/`. Scope: `native/**`.

Lane self-reports are not proof; every claim closes on parent-executed runs
in the integrated tree.

## Acceptance traceability

Parser coverage → `parse-corpus` over the canonical corpus (Appendix A);
single snapshot → D3; fixture corpus → D7; recorded verdict differences → D6
ledger; probe narrowing honesty → D9; benchmark evidence → D8; 3x +
deletability gate → D8 go condition; frozen ABI → D4 (go verdict only); no
production dependency → D2. Deviation from the issue's representative list:
`what_reads_this.py` comparison is descoped per D5 with its rationale
recorded for disposition at closeout.

## Non-claims

- The spike does not modify or delete any Python owner, gate, hook, skill,
  or export.
- It does not prove Python runtime imports, provider behavior, or host
  behavior.
- `what_reads_this.py` parity is not attempted; its deletion is not claimed.
- A go verdict authorizes #746/#747 to start; it completes nothing else.

## Appendix A: corpus census (2026-08-28, base 533f24dad)

- Canonical corpus = tracked `*.py` excluding `plugins/` mirrors: 1,284
  files, 336,924 lines. All 1,284 parse cleanly under CPython 3.10.12
  `ast.parse`; 0 UTF-8 decode errors, 0 BOMs, 0 null bytes, 0 encoding
  declarations.
- Language floor: Python 3.10 — one `match` statement
  (`skills/public/quality/scripts/dynamic_entrypoint_evidence.py`), PEP 604
  unions in 608 files, walrus in 42. Zero 3.11+ (`except*`) or 3.12+
  (PEP 695, relaxed f-strings) constructs; a strict 3.10 or 3.12 grammar
  rejects nothing.
- No deliberately malformed `.py` exists anywhere in the repo (fixture dirs
  included); see D7 for the consequence.
