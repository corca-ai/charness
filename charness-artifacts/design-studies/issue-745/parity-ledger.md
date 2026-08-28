# Issue #745 parity ledger

> Date: 2026-08-28
> Repo identity: HEAD 1a9591072 (bench/parity runs), integrated on main
> Evidence: `parity-2026-08-28.json`, `bench-2026-08-28.json` (this directory)
> Dispositions are parent-owned; lane self-reports were re-executed by the
> parent in the integrated tree before any entry below was recorded.

## Verdict differences and dispositions

Zero verdict differences were observed across every comparison executed.
Entries below record what was compared (so absence of difference is coverage,
not silence) plus every intentional contract change the spike carries.

### Equivalent (observed, no difference)

1. Export-safe fixture families — 10 expected-set cases
   (`fixtures/expected/export_safe_*.json`): forbidden `from`/`import` forms,
   `import_repo_module` form, segmented and slash-joined path literals,
   escape hatch (asset suppression), escape hatch non-suppression of import
   checks, support/shared/nested universes. Python side enumerated past its
   fail-fast by line-exclusion rerun; compared as set equality against both
   the Rust result and the checked-in expected set. 0 differences.
2. Export-safe whole repo — identical 709-file universe both sides, 0
   violations both sides, exit class agreement. (Detection parity is carried
   by the fixture families above; the whole-repo run proves universe
   agreement.)
3. Standalone-targets whole repo — full discovery comparison: 714 modules,
   module names, paths, and per-module shape lists all equal; `--changed`
   empty-vs-omitted and ordering pinned by fixture case.
4. Match-surfaces — harness fixture case plus parent-executed adversarial
   sweep: the full 7,532-path tracked list in one call produced
   byte-identical projections (changed/matched/sync/verify/unmatched), and
   300 fixed-seed random single-path calls produced 0 differences.
5. Parse corpus — 1,284/1,284 canonical files parsed (matches the
   independent CPython 3.10 census exactly); the four malformed fixtures
   appear as typed non-parsed entries and force exit 3.

### Intentional contract changes (not replicated, by plan rev 2)

6. Exit classes: repograph uses 0/1/2/3/70 (3 = unestablished per
   `run-quality.sh` convention, 70 = internal error) where Python owners
   overload exit 1. Wrappers must map 3 to blocking unless their label is
   unestablished-capable.
7. Report-all violations instead of the owner's fail-fast single-violation
   report.
8. No silent filesystem fallback when git listing fails (typed exit 3
   instead); replaces two distinct Python fallback behaviors.
9. External `CHARNESS_SUPPORT_DIR` relocation is not reproduced; the
   export-safe universe is derived from the one repo snapshot only.
10. A non-parsed in-scope file forces export-safe to exit 3 (owner: exit 1
    via SyntaxError). Same blocking direction, different byte.
11. `parse-corpus` default exclusion is `plugins/` only, so a default
    whole-repo scan now also sees the committed malformed fixtures and
    exits 3; the canonical-corpus claim uses the documented explicit
    `native/repograph/fixtures/` exclusion.

### Intentional scope bounds

12. `what_reads_this.py` parity (all modes) is descoped: no automated
    consumers, no deletion claimed. Glob-consumer edges are modeled at
    library level with a unit test.

### Evidence-fidelity notes

13. `bench-2026-08-28.json` records `rustc_version: 1.93.0`; the binary is
    actually built by the crate-pinned 1.96.0 toolchain (run_bench sampled
    `rustc --version` from the repo root, outside the `rust-toolchain.toml`
    scope). Corrected value verified by the parent: rustc 1.96.0
    (ac68faa20 2026-05-25), release profile.

### Blockers

None recorded.
