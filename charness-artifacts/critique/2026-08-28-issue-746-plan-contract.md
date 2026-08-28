# Critique record: 746 topology plan, contract fidelity

> Date: 2026-08-28
> Reviewer: bounded-reviewer subagent (opus, explicit model override)
> Target: the rev 1 plan; all blockers and should-fixes dispositioned in rev 2

Fresh-eye satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye critique (repo
  bounded-reviewer envelope, one assigned lens)
- Requested spawn fields: host `bounded-reviewer` subagent type
  (Read/Grep/Glob only), shared parent worktree, lens-scoped prompt;
  explicit model override `opus`
- Host exposure state: applied
- Application state: host-confirmed: the subagent transcript metadata
  records model=opus for this spawn.
- Execution mode: typed-subagent
- Delivery state: findings-received

## Boundary Ownership

- Verdict: single-surface
- Producer: the reviewed design document (one plan file in this repo).
- Consumer: the parent orchestrating session revising that plan.
- Owning surface: charness-artifacts design study; findings were
  dispositioned in the plan revision, no state moved across surfaces.

I've verified the plan's claims against the repo. Here is the full report.

---

# Fresh-eye critique: #746 topology core plan — contract correctness and model fidelity

**Fresh-eye context:** `parent-delegated`. **Envelope:** bound (no Bash/Edit/Write/Agent tools available; all findings are read-only).
**Target:** `/home/hwidong/codes/charness/charness-artifacts/design-studies/2026-08-28-issue-746-topology-core-plan.md`

## Headline

The plan is directionally right and its typed-opacity posture is the correct one, but it has **three blockers**: the role-classification rules that the entire #743 answer rests on are never specified anywhere in the document; the single-snapshot model (D4) structurally contradicts the deletion/rename fixture it promises (D8) and leaves "changed path not in the inventory" undefined; and D2's tokenizable tier as written will emit *wrong-typed* edges on real repo carriers, not merely unresolved ones. Everything else is fixable in the plan text before Lane A starts.

I found **no breaking ABI change** to the four frozen v1 commands (finding 16 is a documentation precision point, not a break).

---

## Blockers

### 1. The role-classification rule source is never specified — and it is the load-bearing input to #743

**Sections:** D1 (`file` node), D6 (`classify`), Lane C ("+ role classification rules")

D1 says a `file` node "carries derived role classification `production | test | generated | doc | config | fixture` plus `unestablished` when no rule applies (never silently defaulted)." The plan never states **what the rules are or where they are declared**. Lane C is handed "role classification rules" as a bullet with no contract, so four things get invented at implementation time: what makes a file `production` vs `config`, where per-package test patterns come from, whether the rules are hardcoded or declarative, and whether they are per-repo or universal.

This is not a detail. The plan's own cited investigation raised it as its first open question (`/home/hwidong/codes/charness/charness-artifacts/design-studies/issue-746-747/issue_743.md:32`: "How does the graph derive test-vs-production membership for languages/frameworks without a uniform naming convention... or must it require an explicit per-package test-glob declaration"), and the plan does not answer it. Worse, the only concrete grounding the plan gives is Charness-local and does not generalize: D1 defines `package` as "a skill package, the shared library, the scripts tree, the CLI, the test tree, and the plugin export," and `test` as "tests under pytest `testpaths`" (`/home/hwidong/codes/charness/pyproject.toml:2` — accurate for this repo). But #743's consuming repo is a **Go** repo whose triggers are `cli/internal/client/**/*.go` with adjacent `_test.go` files (`issue_743.md:5`). Nothing in D1–D8 reads a Go package manifest, and D5 restricts external analyzers to `imports` edges from rev-dep (JS/TS). So in the repo that filed #743, `classify` returns `unestablished` for every path — fail-loud, but not an answer, and the acceptance clause says the classification must *answer* the source-set question.

**Smallest fix:** add a decision (D1a) naming the rule source explicitly: a declarative per-package `test_globs`/`production_globs` contract with a documented built-in default set (pytest `testpaths` for Python; `*_test.go` for Go), stating that a package with no matching declaration yields `unestablished` rather than a guess. Then state in D6 that #746 ships the *mechanism* and this repo's defaults, and that a consuming repo without a declaration gets `unestablished` — which is the honest non-claim the acceptance criteria want.

### 2. D4's one snapshot contradicts D8's two-snapshot fixture, and "changed path absent from the inventory" is undefined

**Sections:** D4, D6 (`changed`, `classify`), D8

D4: "Graph construction consumes exactly one `FileInventory`." D8 requires a fixture for "path deletion/rename between two snapshots (changed-path determinism)," and the issue acceptance lists deletion/rename as a required fixture case. One inventory cannot express two snapshots.

The concrete consequence is not fixture bookkeeping, it is a hole in the query contract. A deleted path is not in the inventory, so it has no `file` node — but `classify --path <deleted>` and `changed --path <deleted>` must still answer, because in #743's scenario deleting a production file must still trigger host proof. The plan defines no behavior for this case in D6. Note that the frozen `match-surfaces` sidesteps it entirely because it is pure pattern matching with no inventory (`/home/hwidong/codes/charness/native/repograph/src/surfaces.rs:125-192` never touches `FileInventory`); the graph-backed commands cannot.

Renames compound it: `git ls-files` carries no rename information, so the old path is simply absent and the new path present, with no link between them.

**Smallest fix:** in D6, add an explicit `presence: present | absent-from-snapshot` field to every per-path result of `classify` and `changed`, with the rule that an absent path falls back to pattern-level surface membership and reports its role as `unestablished-absent` (never `not-production`). In D8, restate the fixture as "deletion/rename expressed as two `--file-list` inventories over the same fixture tree, compared by the harness" so it stays inside the one-snapshot-per-invocation rule rather than breaking it.

### 3. D2's tokenizable tier will emit wrong-typed edges on real repo carriers

**Section:** D2 ("shell-token split, then argv words resolved against the snapshot (exact path, then `python3 -m`/script-path forms)")

"Argv words resolved against the snapshot" does not distinguish the *invoked program* position from *path-valued arguments*, and does not distinguish command text from quoted message text. The plan's own guardrail — "wrong edges are worse than typed opacity" — is violated by four shapes that exist in the repo today:

- **A path inside an error message becomes an invocation.** `/home/hwidong/codes/charness/.githooks/pre-commit:8` is `echo "charness pre-commit: interrupted mutation recovery is REQUIRED; run python3 scripts/mutate_and_restore.py --repo-root . --check-recovery, then --recover" >&2`. The hook never runs that script; it tells a human to. D2 explicitly names "git-hook inline `python3 scripts/x.py` lines" as tokenizable, and this line matches that shape exactly. It yields a false `invokes` edge.
- **Path-valued flags become invocations.** `/home/hwidong/codes/charness/scripts/run-quality.sh:1161` passes `--adoption-path .agents/consumer-validator-adoption.yaml`; `/home/hwidong/codes/charness/.github/workflows/quality-core.yml:64` is `pip install -r packaging/bootstrap-requirements.txt`. Both are real snapshot paths in argv-word position. Both are *read/configure* relations that D1 already models as a separate `configures` edge class, so typing them as `invokes` is a wrong edge in a class the model can already express correctly.
- **`--repo-root .` resolves to the repo root.** Present in nearly every carrier in `.agents/surfaces.json` (e.g. `:27`, `:30`, `:31`). "Invokes `.`" is meaningless.
- **The invoked target itself can be the dynamic part.** `/home/hwidong/codes/charness/scripts/run-quality.sh:1172` is `queue_selected "check-provenance-contract" python3 "$PROVENANCE_CONTRACT_CHECKER" --repo-root "$REPO_ROOT"`. D2's model for run-quality is "literal prefix, argv beyond it may be `unresolved`" — here the prefix is literal, the *target* is a variable, and the tail is literal. The stated shape is backwards for this line.

**Smallest fix:** narrow D2's rule to "only the resolved program word produces an `invokes` edge — argv[0] after skipping an `env` prefix, `KEY=VALUE` assignments, and interpreter flags; a path-valued argument produces a `reads` (or `configures`) edge, never `invokes`." Add: "a command-shaped string appearing as an argument to `echo`/`printf` or inside a `-c` payload is a typed `unresolved-carrier`, never an edge." Add `.githooks/pre-commit:8` and `run-quality.sh:1172` as named negative fixtures in D8 so the false edges are asserted absent.

---

## Should-fix

### 4. The mirror rule table is materially incomplete, and its stated derivation inputs are wrong

**Section:** D1 (`mirror-pair`)

D1 lists six rules ("public-segment collapse, verbatim replace, filtered support copy, shim injection, README rewrite, lock surface") and says pairs are "derived mechanically from `packaging/charness.json` + the rule table." Reading `export_plugin_tree` (`/home/hwidong/codes/charness/scripts/packaging_lib.py:227-320`), at least six behaviors are missing or misattributed:

- `.claude/agents/**` → `plugins/charness/agents/**` (`packaging_lib.py:261-262`), a real pair on disk (`.claude/agents/bounded-reviewer.md` → `plugins/charness/agents/bounded-reviewer.md`) and a declared surface (`.agents/surfaces.json:106-120`). Absent from the rule table, so it becomes an unexplained generated output.
- `SOURCE_ONLY_PLUGIN_SCRIPTS` subtraction (`packaging_lib.py:42-46`, `301-302`): three `scripts/*.py` files are deliberately deleted from the export. A collapse rule that predicts a mirror for every `scripts/*.py` reports three false missing mirrors.
- `export_bootstrap_dependency_contract` (`packaging_lib.py:205-224`): exactly two `packaging/` files travel, while `./packaging/` is otherwise source-only (`packaging_lib.py:31-40`).
- Manifest-generated outputs with no file source: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` (`packaging_lib.py:319-320`), plus `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` (`packaging_lib.py:370-382`). These are derived from `packaging/charness.json` *content*, not from a source file, so they need a distinct rule id.
- Two content-mutating rewrites that a byte-equality mirror check would flag as drift: `rewrite_exported_consumer_validator_catalog` (`packaging_lib.py:172-194`) and `rewrite_support_capability_path` (`packaging_lib.py:154-169`).
- The support filter is data-dependent on a third input: `upstream_consumed_support_ids` comes from `load_manifests_for_discovery` over `integrations/tools/*.json` (`packaging_lib.py:269-275`; `integrations/tools/agent-browser.json:120`, `integrations/tools/specdown.json:91`). So the derivation inputs are `packaging/charness.json` **+ `integrations/tools/*.json` + hardcoded constants in `packaging_lib.py`**, not the two the plan names.

This directly threatens the plan's own verification step ("a final adversarial pass comparing derived facts against known ground truth (e.g. `plugins/` mirrors)"), which would be comparing against an incomplete model.

**Smallest fix:** replace D1's prose rule list with an explicit enumerated rule-id table transcribed from `export_plugin_tree`, including the four subtractive/generative rules above, and correct the derivation-input sentence.

### 5. The crate has no YAML parser, and several D1/D2 inputs are YAML — under a pinned offline build

**Sections:** D1 (adapter/registry nodes, skill frontmatter), D2 (`command-docs.yaml`), Lane B (label parity)

`native/repograph/Cargo.toml:16-21` declares exactly four dependencies: three `ruff_*` crates, `serde`, `serde_json`. There is no YAML crate, the versions are `=`-pinned, `rust-toolchain.toml` pins 1.96.0, and the documented build is `cargo build --release --offline` (`native/repograph/README.md:8-13`).

The plan requires reading: `.agents/<skill>-adapter.yaml` (D1 adapter nodes and `configures` edges "from declared `source_paths`"), `.agents/command-docs.yaml` (D2 tier structured), `.agents/consumer-validator-adoption.yaml` (D1 registry), SKILL.md YAML frontmatter (D1 skill identity), and — for Lane B's parity claim — `.agents/quality-adapter.yaml` `startup_probes`, since that is one of the three sources `quality_label_universe.py` reads (`scripts/quality_label_universe.py:56-57`, `78`, `198-254`, which additionally documents a column-0 formatting footgun that only a real YAML parser handles).

**Smallest fix:** add one line to the execution shape naming the YAML strategy and its cost — either a vetted pinned crate with a `Cargo.lock` update and a populated offline registry cache (and a note that `check_supply_chain` sees it), or an explicit v1 restriction to JSON plus a documented frontmatter-subset reader, with YAML-only carriers typed as unresolved.

### 6. "Schemas reject unknown required variants" has no enforcement point in the crate

**Sections:** Acceptance traceability ("serde deny-unknown on required variants"), D1/D5

Two problems. First, the parenthetical is a category error: `#[serde(deny_unknown_fields)]` rejects unknown *fields*, while unknown *enum variants* already fail by default unless `#[serde(other)]` is present. Second and more important, there is currently nothing to deny on: the crate has **zero** `Deserialize` implementations and zero `deny_unknown_fields` — every serde use is `Serialize` for output (verified across `src/*.rs`; `surfaces.rs:84` parses into `serde_json::Value` and validates by hand). Node and edge schemas are output-only, so nothing ever deserializes them.

That means the acceptance clause can only be satisfied at the crate's genuine *input* boundaries: the D5 analyzer result, any new config the graph reads, and the existing hand-validated `surfaces.json`.

**Smallest fix:** rewrite the traceability line to name the input surfaces where strictness is enforced (analyzer result and graph config, deserialized with `deny_unknown_fields` and no `#[serde(other)]` fallbacks on typed enums), and state that node/edge variant strictness is proven by round-trip fixtures rather than by an output type.

### 7. The fixture tree pollutes every whole-repo run, and the new commands have no exclusion flag

**Sections:** D6, D8, Execution shape (verification)

`native/repograph/fixtures/` is committed and deliberately malformed; the crate README already documents that a clean whole-repo scan must pass `--exclude-prefix native/repograph/fixtures/` in addition to `plugins/` (`native/repograph/README.md:30-37`). D8 adds import cycles, generated mirror pairs, test-only closed components, and unresolved carriers to that same tree. Meanwhile D6 specifies no `--exclude-prefix` for `graph`, `components`, `explain`, `classify`, or `changed`; only `parse-corpus` has one (`native/repograph/ABI.md:71`).

So the plan's own verification step — "whole-repo `graph`/`components`/`explain` sanity runs" and "comparing derived facts against known ground truth" — would run against a graph containing synthetic cycles and synthetic islands reported as real ones.

(I checked the adjacent worry and it is fine: `native/.gitignore:1` is `target/`, so the Rust build tree stays out of the inventory.)

**Smallest fix:** give every new command the same repeatable `--exclude-prefix` with the same replace-the-default semantics, defaulting to `plugins/` **and** `native/repograph/fixtures/`, and state the default in D6.

### 8. D3's determinism claim has three inputs it does not account for

**Section:** D3

"Same repository bytes + same configuration + same analyzer inputs → byte identical output" is not true of the inventory as implemented:

- `git ls-files -z --cached --others --exclude-standard` (`native/repograph/src/inventory.rs:154-167`) honors `--exclude-standard`, which reads `core.excludesFile` and `.git/info/exclude` — user and per-clone state, not repository bytes. It also includes untracked files, so a stray local file changes the graph. And `--others` output is not globally sorted with `--cached`.
- `FileInventory` neither sorts nor deduplicates (`inventory.rs:183-197`); each existing command does its own sort/dedupe, and the ABI states duplicates in an injected file list survive (`ABI.md:78`). A `--file-list` with a duplicate path would produce duplicate nodes unless the graph builder dedupes.
- D5 makes `--analyzer-result` repeatable but never defines merge/conflict resolution between two results with overlapping declared scope, so "same analyzer inputs" is under-determined.

**Smallest fix:** scope the D3 sentence to "same *inventory* + same configuration + same ordered analyzer inputs," state that the graph builder deduplicates inventory paths by path, define analyzer-result merging as ordered with a typed conflict record on scope overlap, and require the double-build test to pin the inventory via `--file-list` so the claim is actually testable.

### 9. The `.agents/` adapter/registry taxonomy covers 12 of 22 entries and has two naming exceptions

**Section:** D1 (`adapter`)

D1 asserts two subclasses: `.agents/<skill>-adapter.yaml` per-skill policy adapters, and five named registry files. Against the actual directory:

- `.agents/markdown-preview.yaml` is a support-skill adapter **without** the `-adapter` suffix — the naming rule as stated misses it.
- `.agents/worktree-adapter.yaml` matches the `<skill>-adapter.yaml` pattern but there is no `skills/*/worktree` skill; it belongs to `integrations/worktree`. A rule that derives "adapter → skill" from the filename produces a dangling reference.
- Unmodeled entirely: `.agents/command-dominance.yaml`, `.agents/inference-interpretation-surfaces.json`, `.agents/surfaces.json`, `.agents/codex-host.md`. The first two are precisely "hand-maintained shadows of derivable facts" by the plan's own definition of a `registry` node, so their omission undercuts the "later issues can compare declared vs derived and shrink them" purpose.

**Smallest fix:** define the adapter/registry classification by an explicit enumerated table over `.agents/*` with a typed `unmodeled-declaration` fallback, rather than by a filename pattern plus a five-item list.

### 10. `skills/support/generated/` becomes a false `malformed-skill` node

**Section:** D1 (`skill`)

D1: "A skill directory without valid frontmatter is a typed `malformed-skill` node, not skipped." `skills/support/generated/` exists (holding only `.gitkeep`), is gitignored except that keepfile (`/home/hwidong/codes/charness/.gitignore:41-42`), and is explicitly skipped by the exporter as a non-skill (`scripts/packaging_lib.py:275`). Typing it `malformed-skill` reports a defect where the repo has a deliberate convention.

**Smallest fix:** state in D1 that skill-directory candidacy excludes the exporter's own skip set (`generated` and `upstream_consumed_support_ids`), citing `packaging_lib.py:269-275` as the single source for that rule.

### 11. Per-command exit semantics are unspecified — and that *is* the #743 fail-loud contract

**Section:** D6 ("each with `repograph.<cmd>.v1` schema and spike exit classes")

Naming the class set 0/1/2/3/70 does not determine, for `classify`, whether one `unestablished` path exits 0 with a typed field or exits 3. That choice is the entire fail-loud requirement, because the ABI's wrapper rule makes exit 3 blocking by default (`native/repograph/ABI.md:589-595`) and `run-quality.sh` only tolerates it for labels in the opt-in `UNESTABLISHED_CAPABLE_LABELS` list. It also has to compose with the consumer's existing four-state vocabulary in `check_real_host_proof.py`, which deliberately has no state for "the classifier could not decide" (`skills/public/release/scripts/check_real_host_proof.py:104-135`, `191-227`) — and whose own comments record that a permissive default here *inverted* a release gate's verdict.

**Smallest fix:** add a per-command exit table to D6, minimally: `classify` exits 3 if any requested path is `unestablished`, 0 otherwise; `components` exits 1 on findings and 3 on unestablished scope; `graph`/`explain`/`changed` are pure-report commands (0/2/3). State that an unestablished classification must never be reported as "not production."

### 12. "Declared boundary violations" names no declaration source and risks a second truth

**Section:** D6 (`components`)

"Declared boundary violations" is undefined. In this repo "boundary" means `boundary_cross_surface_globs` / `boundary_cross_surface_surfaces` — a *changed-path* policy read from adapters (`scripts/boundary_probe_lib.py:37-38`, `66-67`), which is a different question from a graph edge-direction rule. The other candidate reading is the export-safe rule (no `skills.public` imports from exported scripts), and that already has a frozen v1 command with its own violation taxonomy (`native/repograph/ABI.md:207-216`). If `components` re-derives that, the repo gets two implementations that can disagree — the same two-truth failure D4 is written to prevent for caches.

**Smallest fix:** name the declaration source in D6 and state the ownership rule: `export-safe` v1 remains the verdict owner for import-boundary violations and `components` only re-reports its findings, or the boundary declaration is a new explicit input whose format D6 specifies.

### 13. Tier "structured" is misclassified: two of its three members carry no file target

**Section:** D2 (Tier structured)

- `.agents/command-registry.json` contains no paths and no command strings — entries are `{"path": ["worktree", "create"], "group": "worktrees"}` (`.agents/command-registry.json:2-37`). It is a subcommand taxonomy of the `charness` binary, exactly as the plan's own investigation classified it (`command_carriers.md:75`, carrier shape 5). Producing an `invokes` edge from a registry entry requires parsing the `charness` script's argparse dispatch, which no lane covers. D1 nonetheless makes all 37 entries root nodes.
- `.agents/command-docs.yaml` `help_command` values are all `./charness <sub> --help` (`.agents/command-docs.yaml:4,28,39,52,...`), so ~30 entries collapse to one identical edge to a single file.
- The `{target:<id>}` grammar has exactly one real instance in the repo: `charness-artifacts/critique/command-plans/2026-08-21-goal-fanout.json` (verified by grepping `owner_target`; the other hits are the tool, its test, and docs). Reimplementing that resolution algorithm in Rust — which the investigation warns must match `command_plan_preflight.py`'s exact exact→basename→fnmatch and ambiguous/not-found refusal semantics (`command_carriers.md:79`) — buys typed edges for one archived artifact.

**Smallest fix:** split D2's tier structured into "structured with a file target" (`command_plan_preflight` plans) and "structured taxonomy, no file target" (`command-registry.json`, `command-docs.yaml`), and move `{target:<id>}` resolution out of #746 scope unless a live consumer appears, since deferring it costs one artifact's edges and avoids a second resolution implementation.

### 14. Pattern matching must reuse the crate's Python-faithful `fnmatch`, not a glob crate

**Sections:** D6 (`classify` per-surface membership, `changed`), D1 (`package` membership)

Surface membership in this repo uses `fnmatch` where `*` **crosses `/`** — a footgun the repo has already been burned by and documents at length (`.agents/surfaces.json:102` records #331; `scripts/surfaces_lib.py:14-22`; `native/repograph/ABI.md:336-338`). The spike already ships a Python-faithful implementation (`native/repograph/src/surfaces.rs:396-500`, with `surfaces.rs:610-614` pinning that `dir/**/*.py` misses `dir/file.py`). The plan never mentions pattern semantics. A lane reaching for the `glob` crate's default (where `*` does not cross `/`) silently changes which files are a surface's production sources — a wrong classification in the exact path #743 depends on, with no test failure to reveal it.

**Smallest fix:** one sentence in D6: all surface and package membership matching reuses `surfaces::fnmatch` / `path_matches_patterns`; no second matcher is introduced.

---

## Notes

### 15. #743's raw-glob arm is the one that actually filed the issue

D6 frames the `classify` answer as `production-source-of: [surface ids]`, and D7 leaves raw path sets to human policy. But the trigger that produced #743 is `real_host_required_path_globs`, evaluated separately from surfaces as a flat positive fold (`check_real_host_proof.py:189-190`), precisely because the consuming repo's Go package is not a declared Charness surface. The per-path `role` field does answer it (the sketch in `issue_743.md:28` composes `matches_any(...) and role == "production"`), so this works — but only if finding 1 is fixed. Worth stating explicitly in D6 that the raw-glob arm is served by the role field, not by surface membership.

### 16. ABI: no breaking change, but "untouched" is imprecise

The four frozen commands' inputs, schemas, ordering, and exit contracts are unaffected; adding dispatch arms in `native/repograph/src/lib.rs:55-64` is additive. Two precision points: the shared top-level usage string `native/repograph/src/lib.rs:209` is printed by `--help` and by every usage error of the frozen commands, and it is transcribed verbatim into `native/repograph/ABI.md:29`, so it must be updated in the same change (no test pins it). And D3's "no absolute paths in output" is a new-command rule only — `standalone-targets` v1 emits absolute `sys.path.insert` literals by contract (`ABI.md:486`, `550`), so its output is legitimately not machine-portable and the double-build determinism test must scope around it.

### 17. Lane B's label parity test inherits a claim without inheriting its guarantee

`quality_label_universe.py` is trusted only because `run-quality.sh` asserts at queue time that every label it queues was found by the reader (`command_carriers.md:35`) — the static parse is load-bearing *because* a runtime check makes a miss loud. A Rust reimplementation compared only against the Python one has no such backstop; a shared blind spot in both regexes passes parity silently. Since #746 wires no production consumer this is acceptable for now, but D2 should record it as a named non-claim so a later issue does not promote the Rust extractor to source of truth without adding the runtime assertion.

### 18. Schema-id naming

Existing ids snake_case the command name (`repograph.match_surfaces.v1`, `native/repograph/src/surfaces.rs:185`). All five new commands are single words, so `repograph.<cmd>.v1` is consistent — no action, just do not introduce a hyphenated id.

---

## Verdict

**Sound to execute after should-fixes: yes — but only after the three blockers are resolved in the plan text, not deferred to lane implementation.**

Blockers 1 and 2 are specification gaps in the contracts the issue is *about* (the #743 classification rule and the changed-path/deletion contract); handing either to a lane means the lane invents the acceptance criterion it is being measured against. Blocker 3 is a correctness rule that must be settled before Lane B writes its first extractor, because retrofitting the invoked-program-position distinction after the edge set exists means re-litigating every fixture.

The should-fixes are all plan-text edits of a paragraph or less, and none of them changes the four-lane shape. Findings 4, 5, and 7 have the most execution risk attached: an incomplete mirror table and a polluted whole-repo graph would both surface as confusing lane failures rather than as clear specification bugs, and the missing YAML dependency is the kind of thing that stalls a lane mid-flight under an offline pinned build.
