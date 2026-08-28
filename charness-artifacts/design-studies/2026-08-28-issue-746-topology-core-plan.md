# Issue #746 plan: typed repository topology core

> Status: rev 2 (post-critique; two opus reviews applied — contract fidelity,
> scope/sequencing)
> Date: 2026-08-28
> Parent: #744; depends on the ratified #745 spike (crate `native/repograph`,
> frozen ABI v1, exit classes 0/1/2/3/70)
> Investigation records: `issue-746-747/` (topology, command carriers, #743)
> Critique records: `../critique/2026-08-28-issue-746-plan-{contract,scope}.md`

## Objective

Extend `native/repograph` into the single typed owner of derivable
repository topology: one inventory → typed nodes/edges → components,
explanations, changed-path queries, and the #743 role classification — with
external analyzers ingested through a versioned provider result and human
policy left declarative.

## Decisions

### D1. Node, edge, and root model

Node classes:

- `file` — inventory entry with `role` (D1a) and mirror/package membership.
- `package` — no installed Python package exists; package =
  skill package (`skills/public/<s>`, `skills/support/<s>`), shared library
  (`skills/shared`), scripts tree (`scripts/`), CLI (`charness` +
  `runtime_bootstrap.py`/`yaml_output.py`/`skill_runtime_bootstrap.py`
  shims), test tree (`tests/`), plugin export (`plugins/charness`), native
  crate (`native/repograph`). Membership derived from the snapshot.
- `skill` — a directory under `skills/public|support/` with `SKILL.md`
  frontmatter `name:`; candidacy excludes the exporter's own skip set
  (`generated/` and upstream-consumed support ids, single source:
  `packaging_lib.py` discovery). A candidate without valid frontmatter is a
  typed `malformed-skill` node (`skills/public/handoff` is the live case).
- `adapter` — classified by an explicit enumerated table over `.agents/*`
  (covering the naming exceptions: `markdown-preview.yaml` has no
  `-adapter` suffix; `worktree-adapter.yaml` belongs to
  `integrations/worktree`, not a skill), with a typed
  `unmodeled-declaration` fallback for unlisted entries. v1 models adapter
  identity only; adapter content is NOT parsed (no YAML dependency, D9).
- `command-carrier` / `validation-command` — D2.
- `mirror-pair` — D1b.
- `test` — role-derived (D1a); `runtime-probe` — the standalone runtime
  smoke and `integrations/tools` check commands, identity only in v1.
- `external-module` — owned by an ingested analyzer result (D5).

Edge classes (v1): `imports` (Python static + `import_repo_module`
call-form + `sys.path`-insert + pytest-`pythonpath` plain imports),
`invokes` (D2), `packages`, `mirrors`, `documents` (markdown link → file),
`tests` — defined as a VIEW: an `imports`/`invokes` edge whose source file
has role `test` (roles resolve first; no independent extraction, no
circularity). Cut from v1 (scope review): `configures` edge class,
`registry` node class, `derivable-declaration` advisories — their only
consumers are later issues.

Root classes: product/runtime entrypoints (`./charness`, `init.sh`, the
three root shims), validation entrypoints (run-quality labels, git hooks,
CI workflow steps, surfaces verify/sync commands, staged-commit gate plan),
tests, generated outputs (mirror destinations), host-discovered surfaces
(skills, `.claude/agents/*`, marketplace manifest). The `charness` CLI is
itself the operator-command root; `.agents/command-registry.json` and
`command-docs.yaml` are taxonomy files, not parsed roots in v1 (their
entries carry no file targets). "Mentioned somewhere" is not a root.

### D1a. Role classification rules (the #743-load-bearing contract)

`role ∈ production | test | generated | doc | unestablished` (`config` and
`fixture` deferred — no v1 consumer). Ordered resolution, first match wins:

1. Explicit per-package declaration: an optional `topology` block
   (test_globs / production_globs / generated_globs) readable from repo
   config; #746 ships the mechanism plus Charness defaults.
2. `generated`: mirror destinations (D1b) and declared generated surfaces.
3. Built-in language convention table: Python — under pytest `testpaths`
   (`tests/` here), `test_*.py` / `*_test.py` / `conftest.py`; Go —
   `*_test.go`, `testdata/**`; JS/TS — `*.test.*`, `*.spec.*`,
   `__tests__/**` → `test`.
4. `doc`: `*.md` and declared docs trees.
5. Remaining tracked source in a package → `production`.
6. No rule applies, or two rules conflict → `unestablished` with a typed
   detail (never a silent default; a conflict names both rules).

The #743 consumer contract is an EXCLUSION test, not a selection test:
the trigger arm keeps a hit when `role != test` (and `!= generated` for
mirror destinations). `role` is independently readable for paths belonging
to no declared surface — the raw-glob trigger arm
(`real_host_required_path_globs`, which today includes `README.md` and doc
paths) composes `matches_any(globs) AND role != test`; a doc-role trigger
path still counts as a hit (fixture-pinned, D8). A Go-shaped fixture tree
(`*_test.go` beside production `.go`) is mandatory; it needs path shapes
only, no Go toolchain.

### D1b. Mirror rules: enumerated, subtractive, and honest

The rule table is transcribed from `packaging_lib.export_plugin_tree`, not
summarized: public-segment collapse; shared verbatim; `.claude/agents/` →
`agents/` relocation; filtered support copy (skip set + upstream-consumed
ids from `integrations/tools/*.json`); `scripts/` copy MINUS
`SOURCE_ONLY_PLUGIN_SCRIPTS`; root shim injection; README rewrite; lock
surface; bootstrap dependency contract (exactly two `packaging/` files);
manifest-generated outputs with no file source (`.claude-plugin/*`,
`.codex-plugin/*`, marketplace manifests) as a distinct rule id; the two
content-transforming rewrites flagged `content-transformed` (byte
inequality expected). Derivation inputs: `packaging/charness.json` +
`integrations/tools/*.json` + the rule table constants. Anything the table
does not cover emits a typed `unmodeled-mirror-rule` entry. Ground truth:
derived destination set compared as SET EQUALITY against
`git ls-files plugins/charness`.

### D2. Invokes edges: program-position only, typed opacity elsewhere

Carrier tiers:

- Structured with file targets: `command_plan_preflight` JSON plans exist
  but have one archived instance; `{target:<id>}` resolution is deferred
  from v1 (recorded scope bound), the carrier is typed
  `structured-unparsed`.
- Tokenizable: git-hook lines, CI inline `run:` single commands,
  `package.json` scripts, simple `surfaces.json` strings,
  `integrations/tools` check commands. Rule: ONLY the resolved program
  word yields an `invokes` edge — argv[0] after skipping `env` prefixes,
  `KEY=VALUE` assignments, and interpreter flags (`python3 x.py`,
  `python3 -m pkg.mod`, `bash x.sh`, `./x`). Path-valued arguments yield a
  distinct `carrier-path-reference` record (never `invokes`; `.` and
  non-snapshot words yield nothing). A command-shaped string appearing as
  an argument to `echo`/`printf` or inside a `-c` payload is a typed
  `unresolved-carrier`, never an edge. Named negative fixtures (D8):
  `.githooks/pre-commit`'s echo-advice line and `run-quality.sh`'s
  variable-target `queue_selected` line must produce NO invokes edge.
- Opaque: multi-statement shell strings, computed bash
  (`"${...[@]}"`, `"$VAR"` targets), two-hop adapter→workflow carriers →
  typed `unresolved-carrier` with carrier identity and raw text.
- run-quality labels: extracted with the same source-regex contract
  `quality_label_universe.py` uses, bash-source part only; labels sourced
  from `quality-adapter.yaml` `startup_probes` are typed
  `unresolved (yaml)` in v1 (D9). Named non-claim: the Rust extractor is
  NOT a label source of truth — the Python reader's guarantee comes from
  run-quality's runtime assertion, which v1 does not inherit.

### D3. Determinism and ordering

Same INVENTORY + same configuration + same ordered analyzer inputs → byte
identical output. The graph builder deduplicates inventory paths; arrays
sort by (class, id) or source declaration order; no timestamps or absolute
paths in new-command output (`standalone-targets` v1's absolute-path
fields are pre-existing frozen contract, out of scope). Analyzer results
merge in argument order; overlapping declared scopes produce a typed
`scope-conflict` record. The double-build equality test pins the inventory
via `--file-list` so the claim is testable.

### D4. One snapshot, one invocation, no second truth store

One `FileInventory` per invocation (spike D3 rules). All derivations come
from that graph in-process. v1 ships no cache; the future-cache contract
(discardable projection keyed by snapshot/config/analyzer digests) is
stated so a cache can never become a second store. Digest-bearing JSON
members are named `digest`/`fingerprint`/`id` — never `key`, `token`, or
`secret` (gitleaks generic-rule precedent).

### D5. External analyzer provider contract

`repograph.analyzer_result.v1`: analyzer identity + version, source
identity (commit/digest), declared scope, typed `imports` edges,
exclusions, parse conditions, completeness (`complete | partial | failed`).
Deserialized with `deny_unknown_fields`; typed enums have no fallback
variant. Rules: edges outside declared scope are typed violations;
analyzer edges never overwrite Charness-owned skill/adapter/mirror/command
edges; missing/incompatible/zero-module/`partial` results mark claims over
the affected scope `unestablished`, never clean. rev-dep: a documented
mapping plus one fixture only — no live producer exists in this repo, and
that is a recorded non-claim; the provider mechanism is the deliverable.

### D6. Commands (additive ABI; four v1 commands stay frozen)

All new commands accept repeatable `--exclude-prefix` with default
`plugins/` AND `native/repograph/fixtures/` (the committed fixture tree
must not pollute whole-repo graphs), repeatable `--analyzer-result <file>`
(flag plumbing lands in lane A; provider parsing in lane D), and reuse the
crate's Python-faithful fnmatch matcher for ALL surface/package membership
— no second matcher, pinned by a test asserting `classify` surface
membership equals `match-surfaces` v1 output on the same paths.

- `graph` — full typed emit (nodes, edges, roots, unresolved carriers,
  unestablished entries). Pure report: exits 0/2/3. No checked-in
  whole-repo snapshot; fixture-scoped expected documents only.
- `components` — SCCs, rootless components, validator/test-only islands;
  import-boundary violations are RE-REPORTED from the same graph with
  `export-safe` v1 remaining the verdict owner (equality with export-safe
  findings is a test, preventing a second truth). Pure report: 0/2/3.
- `explain --path <p>` — roots reaching p with every traversed typed edge,
  plus a `dependents` section (reverse edges), plus nearest classified
  ancestors when no root reaches it. Pure report: 0/2/3.
- `classify --path <p>...` — per path: `role`, `presence`
  (`present | absent-from-snapshot`), owning package, per-surface
  production membership. An absent path (deleted/renamed) still resolves
  pattern-level surface membership and path-shape role rules, reported as
  `unestablished-absent` when rules cannot apply — NEVER folded to
  not-production. Exit 3 if any requested path is `unestablished`, else 0.
- `changed --path <p>...` — affected surfaces/packages/roots with per-path
  explanations; same presence semantics. Pure report: 0/2/3.

Per-command exit tables are part of each schema doc. Wiring
`check_real_host_proof.py` is #748/#743 scope; #746 proves the contract on
fixtures replicating #743's scenario. The shared top-level usage string and
its verbatim copy in `ABI.md` are updated in the same change (additive).

### D7. Human policy boundary

The graph never derives intent. Surface purpose, live-proof requirements,
intentional exceptions, operator notes stay declarative in `.agents/`.
(The declared-vs-derived comparison program is deferred to the issue that
consumes it.)

### D8. Fixtures

Extend `native/repograph/fixtures/` with: import cycles across packages,
mirror pairs (collapse rule + a subtractive rule), package entrypoints,
direct script commands, test-only closed components, unresolved carriers
(including the two named negative fixtures from D2), partial external
analysis (scope claims go unestablished), deletion/rename expressed as two
`--file-list` inventories compared by the harness, the #743 scenario
(production hit, `_test`-adjacent non-hit, doc-role trigger still a hit,
unclassifiable → unestablished), and a Go-shaped tree. Constraints:
fixture `.py` names snake_case; markdown fixtures markdownlint-clean
(repo-wide gate; dangling-link fixtures are safe — link/docs-graph gates
do not reach `native/**`); no secret-shaped strings and no `key`-named
digest members; note that fixture `.py` files enter
`check_test_production_ratio.py`'s production denominator (safe direction,
recorded so the metric drift is not misread).

### D9. YAML strategy (v1)

No YAML crate. SKILL.md frontmatter is read by a documented
frontmatter-subset reader (first `---` block, `name:` line). YAML-only
carriers and adapter contents are typed `unresolved (yaml)` /
identity-only. Revisit with a pinned crate only when a consumer needs
parsed YAML content.

## Execution shape

All lanes scoped `native/**`. Codex lanes (`gpt-5.6-luna`, xhigh); the
parent pre-partitions `lib.rs` dispatch arms, integrates serially, and
verifies in the integrated tree:

- Lane A `746-graph-model`: node/edge/root schemas, builder (file,
  package, skill, adapter table, mirror rule table D1b, role rules D1a),
  imports/packages/mirrors edges + tests view, `graph` command,
  `--exclude-prefix`/`--analyzer-result` plumbing with typed
  no-results path, determinism double-build test, frontmatter reader.
- Then in parallel (disjoint modules):
  - Lane B `746-carriers`: carrier tiers, invokes edges, roots,
    validation-command extraction, label parity (bash-source part) with
    the typed yaml gap, negative fixtures.
  - Lane C1 `746-classify`: `classify` + `changed`, presence semantics,
    #743 scenario + Go fixture, fnmatch-reuse equality test.
- Lane C2 `746-explain`: `components` + `explain` (needs B's roots),
  export-safe re-report equality test.
- Lane D `746-analyzer`: provider parsing, scope bounding, completeness
  semantics, rev-dep mapping doc + fixture.

Parent ground-truth battery (adversarial, after C1/C2): frozen-ABI oracle
(graph file/import model agrees with `export-safe` universe and
`standalone-targets`' 714 modules on one snapshot); mirror set equality vs
`git ls-files plugins/charness`; validator recall (every `wired: true`
entry in `consumer-validator-adoption.yaml` reachable from a validation
root); carrier recall (every `check_plugin_asset_command_carriers.py` edge
present in invokes); whole-repo `classify` census (zero `unestablished`
outside a pre-declared list); skill SET comparison including the
`malformed-skill` entry for `handoff`.

## Acceptance traceability

One snapshot/invocation → D4; input-schema strictness + identity → D5
(deny_unknown_fields at input boundaries; output variant strictness by
round-trip fixtures); determinism → D3; SCC/rootless/islands from the
graph → D6 `components`; boundary violations → D6 re-report with
export-safe as verdict owner; reverse-dependency explanation → D6
`explain` `dependents`; file explains roots/edges → `explain`; #743
classification → D1a + D6 `classify` + D8 scenario; analyzer bounding →
D5; changed-path without second store → D4/D6; per-command contracts +
non-claims → D6; fixture list → D8.

## Non-claims

- No proof of provider calls, shell command success, Python import side
  effects, or live host behavior.
- No internal parsing of every language; JS/TS via provider results only;
  no live rev-dep producer exercised.
- No removal or parsing of human policy declarations in v1.
- The Rust label extractor is not a source of truth (no runtime
  assertion backstop in v1).
- No production consumer wired (#748/#743); the four v1 ABIs unchanged.
