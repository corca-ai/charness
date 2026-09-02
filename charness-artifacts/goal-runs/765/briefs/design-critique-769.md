# #769 design critique, before the lanes land (2026-09-02)

Two bounded read-only reviewers read the lane briefs and maps with disjoint
angles (runner and universes; export boundary). Findings are recorded here
with the parent's disposition; the formal distinct-observer critique artifact
for the boundary is produced on the landed tree (issue #769, Owned scope,
fifth bullet). Reviewer replies are truncated by the host near 4k
characters; the runner reviewer's findings 9 onward and its `NOT READ` line
were lost.

## Runner and universes angle

1. Mirror preamble under `--read-only` mutates tracked files:
   `sync_root_plugin_manifests.py:78-83` rewrites `.claude-plugin/marketplace.json`
   and `.agents/plugins/marketplace.json` and unlinks a stale `plugin.json`;
   `.gitignore:35` ignores only `/plugins/`; `.githooks/pre-push:112` runs
   `--full --read-only`. Disposition: ACCEPTED. R2b: under `--read-only` the
   preamble validates (export to a tempdir and compare, the
   `validate_packaging.py --validate-export` shape) and refuses with the
   regenerate command when stale; it writes only in the writing modes.
2. Preamble on a consumer tree is destructive: `scripts/` ships wholesale, so
   a consumer has the sync script; the guard "when `plugins/` exists" plus
   `shutil.rmtree(plugin_root)` at `:74-75` would delete a consumer's own
   `plugins/`. Disposition: ACCEPTED. Guard on `packaging/charness.json`
   present AND the resolved plugin root gitignored; never on the bare
   directory. R2b also moves the nine mirror-comparing tests (map-769-runner
   section 6) onto a session-scoped fixture that exports to a tempdir, so the
   standing pytest no longer depends on the on-disk mirror at all.
3. The extractor cannot emit lanes, phases, or conditions from the label
   regexes (`quality_label_universe.py:143-179` extracts labels only).
   Disposition: ACCEPTED in part. `--check` proves label+command parity;
   lane, condition, and phase are hand-authored with a parity test against
   the shell `if` sites map section 7b lists. Verified at R1 integration.
4. Label-set parity leaves command drift unchecked in the R1 to R2b window.
   Disposition: ACCEPTED. The standing parity test compares (label, argv)
   pairs. Verified at R1 integration; R2b brief updated.
5. `condition` needs disjunction and runtime state (`run-quality.sh:1179`
   is release OR full OR predicate; `:1324-1339` needs release AND prior
   phases green AND no non-claim AND a base sha). Disposition: ACCEPTED.
   R2b adds `any_of:`, `release: true`, `prior_phases_green: true`,
   `non_claim_absent: <name>` verbs (or phase metadata) and pins each with a
   test.
6. `env` needs a non-empty form (`:1276`, `:1306` test `-n`). Disposition:
   ACCEPTED. `env: {VAR: nonempty}`.
7. `opt-in` rows bypass the allowlist and only count a match when named
   (`:1001-1005`, `:650-662`). Disposition: ACCEPTED. `opt-in` = env OR
   explicit name, ignoring `label_is_selected`; the match-counter rule is
   pinned by a test.
8. `runner_variables` in the R2a brief is incomplete (`PYTEST_FLAGS`,
   `python_files` with its empty refusal, `seed_budget_args`,
   `PROVENANCE_CONTRACT_CHECKER`, and more, truncated). Disposition:
   ACCEPTED. R2b enumerates every `$`-token in the emitted rows and refuses
   an undeclared one at load time.

## Export boundary angle

(appended when the reviewer reports)
