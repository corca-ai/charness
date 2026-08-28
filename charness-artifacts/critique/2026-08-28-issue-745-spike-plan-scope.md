# Critique record: issue #745 spike plan (simplification, operability, containment)

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

Fresh-eye context: parent-delegated. Envelope check: my live tool inventory is Read/Grep/Glob only — no Bash, Edit, Write, or Agent — so the bounded-reviewer envelope bound for this spawn. Findings below; lens was simplification/operability/containment, not parity-semantics correctness.

## Findings

**1. (should-fix, over-build) D5.5 `what-reads --path` doesn't inform the go/no-go and should be cut from the spike.**
The plan itself supplies the argument (`2026-08-28-issue-745-rust-core-spike-plan.md:98-104`): the tool "has no automated consumers", and the symbol half is already cut for exactly that reason. The same reasoning eliminates the path half. Cutting it removes: one of five command ABIs, the bug-for-bug "custom glob-to-regex rules of `what_reads_this`" replication item in D6, its fixture parity tests, its benchmark comparison in D8, and roughly half of lane 3. The go/no-go rests on parse-corpus + export-safe + match-surfaces + standalone-targets; a consumer-less explanation tool proves nothing extra about deletability. Smallest cut: delete D5.5, the D6 bullet, and the D8 what-reads row; note it as #746 scope if that rewrite ever happens.

**2. (should-fix, over-build / doing #746's job early) Full ABI freeze at spike end is wasted work on a no-go, and D4 freezes a command D5 never specifies.**
D4 (`:77-79`) promises `ABI.md` with "exact input flags, output schemas with examples, and exit mapping per command" for "the four representative commands plus `inventory` and `parse-corpus`" — but `inventory` appears nowhere in D5's command list, so the plan freezes an unspecified surface. Also, if the verdict is no-go (an explicitly acceptable outcome), the freeze document is dead weight. Smallest fix: make ABI.md freezing conditional on a go verdict (the parity harness's expected-output fixtures already document the schemas de facto during the spike), and either specify `inventory` in D5 or drop it from the freeze list.

**3. (should-fix, execution shape) Four serialized Codex lanes is heavier than the decision needs.**
`match-surfaces` is fnmatch over a file list plus JSON loading — it needs none of the AST/import-edge machinery, so lane 3 exists mostly to carry `what-reads` (finding 1). With `what-reads` cut, fold `match-surfaces` into lane 2 (or even lane 1). Lane 4's benchmark runner is a small script the parent could own outright, since the plan already assigns benchmark *execution* and whole-repo parity runs to the parent (`:187-188`); splitting authorship of a ~50-line harness into its own reviewed-and-integrated xhigh lane is process cost without a correctness payoff. Result: 2 lanes (core+fixtures, validators+parity tests) plus parent-owned harness/bench, versus 4 serialized review-integrate cycles.

**4. (should-fix, containment) Fixture `.py` filenames are gated repo-wide by `check_python_filenames.py` — the corpus must stay snake_case or the standing gate goes red.**
Evidence: `/home/hwidong/codes/charness/scripts/check_python_filenames.py:15,22` scans `("**/*.py",)` over the whole repo (skip dirs are only `.charness/.git/.venv/.pytest_cache/__pycache__/node_modules` plus `vendor` path parts) and enforces `^(?:__init__|[a-z][a-z0-9_]*)\.py$`; it runs in the standing battery (`scripts/run-quality.sh:1055`). A fixture corpus naturally tempted to include name-shape traps (`Bad-Name.py`, `UPPER.py`) would fail this gate. Content is safe (the check is name-only), so malformed-source fixtures are fine as long as their *names* are snake_case, or carry a `vendor` path segment, or use a non-`.py` extension with the harness passing them via `--file-list`. D7 should state this constraint explicitly so a lane doesn't discover it via a red gate.

**5. (should-fix, operability) The `target/` gitignore must exist before the first `cargo build` anywhere, and a nested `native/.gitignore` is strictly cheaper than editing the root file.**
Every scanner here is deliberately gitignore-aware via `git ls-files --cached --others --exclude-standard`, so an *unignored* `target/` is visible everywhere at once: the secrets gate tars up every untracked file for gitleaks (`scripts/check-secrets.sh:83-95` — copying a multi-GB target dir), and the changed-path collector reports it as unowned changed paths, turning closeout preflights red (the root `.gitignore:53-61` comment documents exactly this failure shape for `.claude/worktrees/`). Additionally, the root `.gitignore` is itself a source path of the `repo-python` surface (`/home/hwidong/codes/charness/.agents/surfaces.json:852`), so lane 1's one-line append triggers that surface's full verify battery (ruff, lengths, shell, standing pytest — `:867-875`) at closeout. Smallest fix: put `target/` in a new `native/.gitignore` instead; that file matches no surface (unmatched paths are only an advisory note, `scripts/select_verifiers.py:57-60`), shrinking lane 1's scope to `native/**` alone and removing the shared-root-file merge concern entirely.

**6. (should-fix, evidence durability) Benchmark and parity evidence must be copied into `charness-artifacts/design-studies/issue-745/`, never cited from `native/**/target/` paths.**
`scripts/check_spec_evidence_durability.py:32` scans `charness-artifacts/design-studies/**/*.md` and fails any backticked/linked repo path that resolves to a gitignored target (`:207-219`). The parity ledger and verdict doc will live in that scanned scope, so a citation like `native/repograph/target/bench.json` fails the gate. Raw outputs belong in the issue-745 artifacts dir (or behind the `<!-- reproduction-source -->` marker). Corollary: keep the gitignore narrow — ignoring `native/` wholesale would break the *existing* plan document's citations of `native/repograph/ABI.md` etc.

**7. (note, containment — verified clean) The four Python owners and the main gate battery cannot reach `native/`.**
Verified: `check_standalone_imports.py:77-99` patterns and `check_export_safe_imports.py:55-65` globs go through `iter_matching_repo_files`, which uses per-component `Path.glob` (`scripts/repo_file_listing.py:109-121`), so `*.py` is root-only and nothing matches `native/**`; ruff is an explicit path list (`scripts/check-python-lint.sh:66-72`); py-compile is explicit globs (`run-quality.sh:1134-1142`); pytest is `testpaths = ["tests"]` (`pyproject.toml:2`); vulture paths are explicit (`pyproject.toml:58`); `check-shell.sh:53-59` is root/scripts/tests/.githooks only; `.agents/surfaces.json` has no pattern matching `native/**` (and the dangerous fnmatch-`*`-crosses-`/` patterns are all directory-prefixed); scan-hygiene and runtime-inheritance are scripts/skills-scoped. D2's placement reasoning holds for all glob-scoped gates.

**8. (note, containment — D2's "no gate references it" claim needs a caveat) Repo-wide *tracked-file* scans still bind native content.**
Three reach in regardless of globs: `check-markdown.sh:118` and `check-links-internal.sh:77` run over **all** tracked `*.md`, so the crate README and `ABI.md` must be markdownlint-clean with resolving links; gitleaks scans every tracked/unignored file (finding 5), so fixtures should avoid high-entropy secret-shaped strings; and `check_python_filenames` (finding 4). None is a blocker; D2 should say "no *glob-scoped* gate" and D7 should carry the two content constraints.

**9. (note, operability) No gate acquires a cargo dependency, and none verifies the pins either.**
Nothing in the quality battery invokes cargo, so other contributors are unaffected — but the supply-chain gate only knows JS and Python surfaces (`scripts/supply_chain_lib.py:20,104-166`); `Cargo.toml`/`Cargo.lock` are invisible to it. Fine for a non-production spike; worth one line in D2 so the exact-pin claim is understood as convention-enforced, not gate-enforced. Commit `Cargo.lock`.

**10. (note, benchmark protocol) D8 is slightly over-instrumented and under-specified in the one place that matters.**
Peak RSS and CPU time are recorded but appear nowhere in the go condition — harmless, keep or drop. The real gap: "representative static family >=3x wall-time" doesn't say how the (three, after finding 1) comparisons aggregate — all must clear 3x? worst-case? weighted by real gate runtime? For a decision this size, one sentence fixes it; the worst-case-comparison reading is the honest default.

**11. (note, evidence home) `charness-artifacts/design-studies/issue-745/` is consistent with actual usage.**
Precedent exists: `charness-artifacts/design-studies/issue-57/` is already an issue-scoped subdirectory, artifacts are excluded from ruff (`pyproject.toml:32`), and no naming validator constrains design-studies filenames beyond the durability scan (finding 6). No change needed.

**12. (note, deferred-decision check) Nothing deferred to #746 blocks the spike itself.**
Promotion/deletion, wrapper exit-mapping application, and comment attachment are all genuinely post-verdict. The only intra-plan dependency is Appendix A's census, which is explicitly sequenced before lane 1 and assigned to the parent.

## Biggest single simplification

Cut `what-reads --path` (finding 1). It cascades: one fewer frozen ABI, one fewer bug-for-bug replication family (the custom glob-to-regex translator), one fewer benchmark row, and — combined with folding `match-surfaces` into lane 2 — it collapses lane 3 entirely, turning a 4-lane serialized shape into 2 lanes plus a parent-owned harness.

## Proportionality verdict

The technical core (D1, D3, D6, D7 parser/snapshot/parity/fixture design) is proportionate and well-bounded for a spike whose no-go is a valid outcome. The wrapping is not: five commands where three-plus-parse-corpus decide the question, a full ABI freeze that presumes a go verdict, and four serialized review-integrate Codex cycles for what is fundamentally one crate plus one harness. Containment is genuinely sound — the repo's gates are unusually well glob-scoped — with the residual exposure being the three tracked-file-universe scans (filenames, markdown/links, secrets) and the gitignore-ordering trap, all fixable with one D7 constraint sentence and a nested `native/.gitignore`.
