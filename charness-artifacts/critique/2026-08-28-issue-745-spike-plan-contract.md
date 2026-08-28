# Critique record: issue #745 spike plan (contract and parity correctness)

> Date: 2026-08-28
> Target: charness-artifacts/design-studies/2026-08-28-issue-745-rust-core-spike-plan.md (rev 1)
> Reviewer: bounded-reviewer subagent (read-only; ran on the parent model by omission —
> session policy since corrected to explicit sonnet/opus-only Claude subagents)
> Disposition: all should-fixes adopted in plan rev 2; what-reads cut adopted with
> library/fixture-level glob-consumer modeling retained

Fresh-eye satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye critique (repo
  bounded-reviewer envelope, one assigned lens)
- Requested spawn fields: host `bounded-reviewer` subagent type
  (Read/Grep/Glob only), shared parent worktree, lens-scoped prompt;
  no model override field was sent
- Host exposure state: host-defaulted
- Application state: no model field was sent, so the host applied its
  default (the parent model); recorded as the session policy correction
  to explicit sonnet/opus-only Claude subagents.
- Execution mode: typed-subagent
- Delivery state: findings-received

## Boundary Ownership

- Verdict: single-surface
- Producer: the reviewed design document (one plan file in this repo).
- Consumer: the parent orchestrating session revising that plan.
- Owning surface: charness-artifacts design study; findings were
  dispositioned in the plan revision, no state moved across surfaces.

Fresh-eye adversarial review complete (context: parent-delegated; envelope bound — no Bash/Edit/Write/Agent tools visible). I read the plan and all four Python owners plus the shared listing helper (`scripts/repo_file_listing.py`, `scripts/repo_layout.py`), the exit-code consumers (`scripts/run-quality.sh`, `scripts/staged_commit_gate_plan.py`), and `scripts/check_changed_surfaces.py`. Findings, ordered by severity.

## Should-fix findings

**1. D8 benchmark protocol is unexecutable as written, and the executable reading is unfair to Python.** The plan says all four comparisons run "on identical injected file lists" — but three of the four Python owners accept no file-list injection at all (`check_export_safe_imports.py`, `check_standalone_imports.py`, `what_reads_this.py` derive their own universe via git + glob; only `check_changed_surfaces.py` takes `--paths`). The only way to make the sentence true is to inject into repograph alone, which exempts it from the git-acquisition cost D3 says it pays in production, inflating the speedup the 3x gate depends on. Smallest fix: benchmark each side in its production acquisition mode (both run their own `git ls-files`), assert analyzed-file counts match as the identity check, and reserve `--file-list` injection for parity runs. Also add repograph build identity (release profile, rustc version) to the "exact source identity" record — D8 records only repo identity, and a debug/release ambiguity taints the 3x claim.

**2. D4's exit-code table collides with the repo's existing typed exit convention.** `scripts/run-quality.sh:384-397` already defines `UNESTABLISHED_EXIT=3` and `PARTIAL_EXIT=4`, opt-in per label via `UNESTABLISHED_CAPABLE_LABELS`, with an explicit warning that exit 3 "is not ours to redefine" because misreading it launders real failures. The plan's D4 assigns 2 = unestablished and **3 = internal error** — the exact inversion: a repograph crash exits with the byte the surrounding ecosystem reads as "unestablished, non-blocking" the moment any wrapper label joins that list under #748. The plan's premise that the Python owners merely "overload onto exit 1" is incomplete: the repo already has a frozen unestablished byte, and D4 contradicts it. Smallest fix: align repograph with the existing convention (3 = unestablished, 4 = partial, pick a non-colliding byte for internal error), or freeze into `ABI.md` a hard rule that raw repograph exit codes must never reach `run-quality.sh` without per-command remapping, with the 3-vs-3 collision named.

**3. Parse-failure verdict semantics are unpinned for `export-safe`, opening a false-green path.** Python blocks on an unparseable in-scope file: `ast.parse` raises SyntaxError, wrapped to ValidationError, exit 1 (`scripts/check_export_safe_imports.py:214, 256-259`). D1 says repograph continues past per-file parse failures as typed unestablished results. If `export-safe` then reports pass (exit 0) with the bad file merely annotated, the wrapper passes a gate Python would block — a verdict divergence D6's replicate/intentional lists never mention. Smallest fix: freeze in ABI.md that any non-parsed file inside a verdict command's scope forces a non-pass exit class, and add a malformed-source fixture asserting exactly that for `export-safe` (D7's malformed fixtures currently only bind `parse-corpus`).

**4. The membership rule plus a passing whole repo is a false-green corridor.** Whole-repo comparison on the current (green) repo proves both sides emit empty violation sets — nothing about detection. And the fail-fast rule ("Python-reported violation is a member of the repograph set") never validates repograph's *extra* violations: whenever Python fails, repograph can carry arbitrarily many false positives and stay green. Detection parity therefore rests entirely on fixtures, but D7 enumerates acceptance categories, not per-family violation-positive cases with expected-complete answer sets. Smallest fix: require, per violation family (forbidden `from`/`import` forms, `import_repo_module` form, both path-literal spellings, escape-hatch suppression), a fixture with a curated exact expected violation set compared as a set, not by membership; and on any whole-repo Python failure, have the harness re-run the Python owner with the first offender excluded to enumerate its full set (cheap, since fail-fast is per-run).

**5. The `export-safe` universe is not derivable from one git snapshot in all supported configurations.** `iter_matching_repo_files` splits patterns starting with `skills/support/` and globs them against `support_dir(repo_root)` with **no git filter** (`scripts/repo_file_listing.py:74-96, 123-128`), and `support_dir` can point outside the repo entirely — `CHARNESS_SUPPORT_DIR`, or `repo_root/support` in the exported layout (`scripts/repo_layout.py:16-23`). `check_export_safe_imports.py` includes `skills/support/*/scripts/*.py` (line 61), so its universe can contain files no `git ls-files` snapshot lists. D3's "subcommands never walk the filesystem" structurally cannot reproduce this; whole-repo parity is green on this checkout only because `skills/support` exists here. Note this routing does *not* affect `check_standalone_imports` (its `SCAN_PATTERNS` use wildcards, which don't trigger the split). Smallest fix: record the external-support configuration in the parity ledger as an explicit intentional contract change (or add a second injected list input), and add a fixture so the exclusion is chosen, not discovered.

**6. The go condition "design demonstrably permits deletion of existing owners" has no defined meaning for two of the four owners.** `check_standalone_imports.py` keeps its Python runtime probe half (D5.4 says so), and `what_reads_this.py` keeps symbol/config-key (D5.5). Neither file can actually be deleted on the strength of the spike design; "deletion" for them means splitting, and the plan never says which half surviving still counts as go. Judged at verdict time against an undefined bar, this clause can be satisfied by assertion. Smallest fix: one sentence per owner in D8 stating what deletability concretely means (e.g. "standalone: static discovery half deleted, probe loop rehosted behind the repograph plan; what-reads: path lane deleted, symbol/config-key lanes explicitly retained in Python").

## Notes

**7. The `--symbol`/`--config-key` exclusion does not undermine path-consumer coverage (question 5 answered: defensible).** Command carriers name paths literally, and the literal-path arm scans doc/config surfaces (`scripts/what_reads_this.py:374-377`), so both implementations catch them identically; dotted-module consumers (`scripts.x`) are invisible to the *Python* path lane too, so the exclusion is parity-neutral. The plan's "no automated consumers" claim checks out — only tests and catalog inventory reference the tool. Tie this note to finding 6: the exclusion is honest only because the Python tool survives.

**8. D3's "silent rglob fallback" characterization is imprecise.** `what_reads_this` does fall back to `rglob` but reports it (`listing: "filesystem-walk"` plus an unscanned-surfaces entry, lines 459, 465-466); `iter_matching_repo_files`'s fallback is a pattern glob, not an rglob. The intentional change (refuse instead of walk) remains defensible; the ledger entry should describe the behavior it actually replaces, or the disposition record misstates the contract it changed.

**9. D5.2's replication list underspecifies the AST semantics that carry the verdict.** The precise items: `_chain_root_name` unwrapping of Call/Attribute chains so `REPO_ROOT.resolve().parent / ...` is caught (`check_export_safe_imports.py:80-95`); `_is_supported_script_file` accepting exactly `__file__` / `Path(__file__)` via `ast.unparse` (line 192-193); and — most important — `_probes_both_layouts` suppresses **only** the asset-path family, never the import checks (`validate_asset_paths` early-returns at line 170; `validate_imports` continues). "Whole-file escape hatch scoping" as written permits an over-broad implementation whose false negatives only a fixture will catch; name the asset-only scope in the plan or ABI.

**10. Zero-scope semantics differ per owner and D4's blanket clause could regress the commit gate.** `check_export_safe_imports` refuses zero scope with exit 1 (lines 246-254); `check_standalone_imports` exits **0** on an empty `--changed` match with a "NOTHING WAS CHECKED" scope note (lines 284, 331). `staged_commit_gate_plan.py:447-453` runs the latter with `--changed` at every commit; a wrapper that maps repograph's zero-scope exit 2 to a blocking code would newly block commits touching non-module Python. D4's "where the Python owner refuses" is the right instinct — make it per-command and explicit in ABI.md.

Verified accurate (no finding): the 8-pattern count and `__init__.py` exclusion for standalone; fnmatch `*`-crosses-`/` and POSIX case sensitivity; declaration-order command dedup; numeric version equality (`1.0` passes); `--changed` empty-vs-omitted distinction; the `--paths` falsy-vs-None inconsistency living in `check_changed_surfaces.py:32`; D1's tree-sitter/rustpython rejection rationale; D2's isolation claims.

## Verdict

**Yes — sound to execute after the should-fixes.** None of findings 1-6 requires redesign; each is a bounded amendment (benchmark acquisition mode, exit-byte alignment, three ABI/fixture pins, one ledger disposition, one definitional sentence). But findings 2 and 4 should land before Lane 1 starts, because the exit-code table and the fixture expected-set discipline are inputs to every lane's scope, not post-hoc patches.
