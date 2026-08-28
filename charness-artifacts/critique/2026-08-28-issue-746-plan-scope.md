# Critique record: 746 topology plan, scope/sequencing

> Date: 2026-08-28
> Reviewer: bounded-reviewer subagent (opus, explicit model override)
> Target: the rev 1 plan; all blockers and should-fixes dispositioned in rev 2

## Fresh-eye review — issue #746 topology core plan (scope/sequencing/containment angle)

Fresh-eye context: `parent-delegated`. Envelope bound (Read/Grep/Glob only; no Bash, Edit, Write, or Agent tools were offered).

One evidence caveat up front: I could not read the #746 issue body itself (no shell). My reading of its acceptance comes from the plan's own traceability section (lines 199-202) plus the acceptance sentence quoted verbatim in `/home/hwidong/codes/charness/charness-artifacts/design-studies/issue-746-747/issue_743.md:14`. If the issue text carries acceptance items beyond those, findings 4, 5, and 15 need re-checking against it.

---

### 1. The `classify` contract drifted from #743's actual contract: it is an exclusion test, not a selection test (blocker)

Plan D6, lines 137-141. The plan defines `classify` as returning "per-surface production membership (`production-source-of: [surface ids]`)". The investigation record states the query contract differently: "given a changed path P, is P a current production source belonging to package/surface S ... **and NOT classified as a test node**" (`issue_743.md:18`).

That difference is load-bearing, because the consumer's other half is a raw glob list. `check_real_host_proof.py:190` computes `required = bool(surface_hits or path_hits)`, where `path_hits` comes from `matches_any(path, trigger_globs)` against `.agents/release-adapter.yaml:52-63` — a list that today includes `README.md`, `docs/host-packaging.md`, `charness`, and `scripts/install_machine_local.py`. If #748 rewrites that fold as "keep only paths whose role is `production`", the README and docs triggers stop firing, because their derived role will be `doc`. That is a silent coverage loss on the gate whose entire purpose is to stop a publish that skipped host proof.

Smallest fix: restate D6's `classify` contract as an exclusion (`role != test`, and `!= generated` for mirror destinations), state that `role` is independently readable for paths belonging to no declared surface, and add a D8 fixture where a doc-role trigger path still counts as a hit.

### 2. The role classification rules are never written, and the one repo they must serve is a Go repo (blocker)

Plan D1 line 26 names the vocabulary; the execution shape (line 185) assigns "role classification rules" to lane C as a deliverable. The plan never states a single rule. The lane will invent them, and it will invent them from what it can see: Charness, whose tests live under pytest `testpaths = tests/`.

But #743 is filed against a consuming repo with Go sources: the choice it describes is between the glob `cli/internal/client/**/*.go` and an enumerated file list, with `_test.go` files as the thing to exclude (`issue_743.md:5`). A classifier derived from pytest configuration answers nothing there, and the D8 "#743 scenario" fixture (plan lines 167-169) would be authored in the same Charness idiom, so no test in the lane would catch it. The investigation's open question 1 (`issue_743.md:32`) asks exactly this and the plan does not answer it.

Smallest fix: write the rule table into D1 before launch — an ordered resolution of (a) per-package declaration, (b) a language convention table (Go `*_test.go` and `testdata/`; Python `test_*.py`/`*_test.py` plus pytest `testpaths`; JS `*.test.*` and `__tests__/`), (c) `unestablished` — with the tie-break stated when two rules disagree; and make a Go-shaped fixture tree mandatory in D8. It needs no Go toolchain, only path shapes.

### 3. The `tests` edge definition is circular with the test role (blocker, cheap fix)

Plan D1 line 60 defines `tests` as "test file → imported/invoked production file" while line 26 says the file role is derived. If the role is derived from being the source of a `tests` edge, and the edge is defined as originating from a test file, a lane has two incompatible readings to choose from.

Smallest fix: state the order — the role is derived first from the rules in finding 2, and `tests` is then a *view* over existing `imports`/`invokes` edges whose source carries role `test`. This also removes an independent extraction pass from lane A.

### 4. The declared-versus-derived program is a later issue's work, done early (should-fix)

Three places: `registry` nodes exist, by the plan's own words, "so later issues can compare declared vs derived and shrink them" (D1, lines 40-42); `configures` edges are derived partly "from declared `source_paths`/single-owner comments" (line 57-58), i.e. a regex over prose comments; and `derivable-declaration` advisories are described as "a follow-up inventory" (D7, lines 156-158). No acceptance item names any of them, and each produces output the parent must then triage during integration.

Smallest cut: model those five `.agents` files as ordinary `file` nodes with role `config`; drop the `registry` node class, the `configures` edge class, and the advisory inventory from #746 entirely. The comparison work lands in the issue that consumes it.

### 5. The role vocabulary is larger than #746 consumes (should-fix)

D1 line 26 lists six roles plus `unestablished`. `config` and `fixture` have no consumer in `components`, `explain`, `classify`, or `changed`, and `fixture` is genuinely ambiguous in this repo — `native/repograph/fixtures/*.py` are fixtures that `check_test_production_ratio.py` counts as production Python (its exclusion set at lines 20-31 covers `tests`, `plugins`, `evals`, not `native`). Every extra role is another rule family a lane can get wrong, and finding 1 shows a wrong role can do downstream harm rather than just be noise.

Smallest cut: `production | test | generated | doc | unestablished` in v1. Keep `doc` (finding 1 needs it to explain the README trigger); drop `config` and `fixture`.

### 6. `classify` must reuse the frozen surfaces matcher, and the plan does not say so (should-fix)

`native/repograph/src/surfaces.rs` is 631 lines of parity-frozen fnmatch semantics, including the documented `*`-crosses-`/` behavior and the #331 top-level-file miss (recorded in `.agents/surfaces.json:102`). Lane C, writing surface membership for `classify` without that instruction, will plausibly write a second matcher — and then one binary ships two different answers to "does path P belong to surface S", one of them ABI-frozen.

Smallest fix: one sentence in D6 requiring `classify` and `changed` to call the existing matcher, and one test asserting `classify`'s surface membership equals `match-surfaces` v1 output on the same paths.

### 7. Paths absent from the snapshot are unspecified for `classify` (should-fix)

The real consumer feeds git-range changed paths (`check_real_host_proof.py:91-97` and `:251`), which routinely include deleted files. The snapshot is `git ls-files --cached --others` (#745 D3), which will not contain them. D8 has a deletion fixture, but only for `changed` determinism (line 167); D6's `classify` says nothing. If a deleted path resolves to `unestablished`, then under the fail-loud rule every release containing a deletion drives the #748 gate to unproven.

Smallest fix: state the rule in D6 — a path absent from the snapshot gets a typed `absent-from-snapshot` status with the role still resolved from path-shape rules where they apply, and never a silent fold to non-production.

### 8. Lane order puts the acceptance-critical work third and the cross-cutting work last (should-fix)

Two sequencing problems in the execution shape (lines 180-188).

First, `explain` is defined as "the roots reaching p" (D6, line 134), and root extraction is lane B's deliverable (line 183). So lane C's headline command cannot be baselined until B lands, while `classify` and `changed` — the acceptance-critical pair — need only lane A's file/package/mirror/role model and the surfaces matcher. As written, the #743 capability lands third of four, after the work least related to it, and any role-rule mistake (finding 2) is discovered at the latest possible moment.

Second, lane D adds `--analyzer-result` to *all* commands (D6, line 145). That is a cross-cutting edit to everything A, B, and C wrote, scheduled last — maximum conflict surface, minimum novelty.

Smallest fix: split lane C into C1 (`classify` + `changed`, depends only on A) and C2 (`components` + `explain`, depends on B), then run A, then B and C1 in parallel, then C2, then D. Have lane A define the `--analyzer-result` flag plumbing and the typed no-results path once, so lane D only supplies provider parsing and scope bounding. B and C1 are disjoint modules; the only shared edit is one dispatch arm each in `lib.rs`, which the parent can pre-partition.

### 9. Markdown fixtures are repo-linted, and D8 does not know it (should-fix, containment)

The `documents` edge (D1, line 59) can only be exercised by `.md` fixtures, and D8 (lines 160-170) never mentions markdown; its containment note covers only snake_case Python names and gitleaks.

`scripts/check-markdown.sh:117-121` builds its population from `git ls-files -- '*.md'` excluding only `charness-artifacts/**`, `.charness/**`, and `.pytest_cache/**`. So `native/repograph/fixtures/**/*.md` is linted, under `.markdownlint-cli2.jsonc` where only MD013 is disabled. The link side is safe: `check_doc_links.py:35-40` globs `docs/`, `presets/`, `profiles/`, and `skills/**`, and `check_docs_graph.py:50` scans `docs` only — so a fixture that models a dangling documentation link will not trip either, which is exactly the fixture you want.

Smallest fix: extend the D8 containment sentence — markdown fixtures must be markdownlint-clean; dangling-link fixtures are safe because the link and docs-graph gates do not reach `native/**`.

### 10. Digest-bearing JSON fields will trip gitleaks if named `key` (should-fix, containment)

This repo has already paid for this once: `.gitleaks.toml:15-17` records an allowlist entry because 16-hex content-hash values under a field named `key` trip the generic-api-key rule. #746 introduces digests in three places — stable node ids (D3), the cache key tuple "(snapshot digest, config digest, analyzer result digests)" (D4, line 106), and the analyzer's "source identity (commit/digest of analyzed tree)" (D5, line 115).

Smallest fix: forbid `key`, `token`, and `secret` as JSON member names in the new schemas and in fixture documents; use `digest`, `fingerprint`, or `id`. Prefer short, non-hex-looking digest values in fixtures.

### 11. Containment otherwise holds; two quiet bindings worth recording (note)

I re-verified the #745 D2 claim against the current gates. `native/**` is missed by `check_python_lengths.py` (its gated globs are "scripts/, tests/, and skill", per its own message at line 336), by `check_doc_links.py`, by `check_docs_graph.py`, and by every `.agents/surfaces.json` pattern (the only matches for "native" in `.agents/` are prose, at `surfaces.json:125`, `:451`, and `:465`). The repo-wide binds are the three the plan already names plus one it does not: fixture `.py` files under `native/` enter `check_test_production_ratio.py`'s *production* denominator. The direction is safe — more fixtures dilute the ratio — but it means the fixture corpus silently moves a repo-wide quality metric, and a later reader should not mistake that drift for a real change. One line in D8 is enough.

### 12. The ground-truth plan is weaker than what this repo gives away for free (should-fix)

Of the three proposed checks (line 193), mirrors and label universe are well chosen — both have an independent Python owner computing the same fact. The skill count is the weak one, and it fails precisely on the interesting case: `skills/public/handoff/SKILL.md` does not exist (a Read of it errors; the directory does contain scripts), while `skills/public/impl/SKILL.md:1-4` does. A count of 20 passes whether or not the graph handles the anomaly. Make it a set comparison and require the typed `malformed-skill` entry for `handoff` to be present.

Five sharper checks, all cheap, all with an independent owner:

- **The frozen ABI as an oracle.** `export-safe`'s four-glob universe and `standalone-targets`' 714 modules (`verdict-2026-08-28.md:16`) are already v1-frozen outputs of the same binary. The graph's file and imports model must agree with them on one snapshot. A disagreement is model drift against a contract that is already frozen — the strongest free check available, and the plan does not mention it.
- **Exact mirror set equality.** Compare the derived mirror-destination set against `git ls-files plugins/charness`. That proves the public-segment collapse and the `SOURCE_ONLY_PLUGIN_SCRIPTS` exclusions exactly, rather than by sampling.
- **Validator recall.** Every `wired: true` entry in `.agents/consumer-validator-adoption.yaml` must be reachable from a validation root. Misses are either graph gaps or genuinely stale declarations; both are worth knowing.
- **Carrier recall.** Every edge `scripts/check_plugin_asset_command_carriers.py`'s narrow regex finds must appear in the graph's invokes edges. A curated, already-passing population as a subset test for lane B.
- **A whole-repo `classify` census.** Run it over every tracked path and require zero `unestablished` outside a pre-declared list. That converts "fail loud" from a fixture claim into a census, and it is the single best adversarial test of the finding-2 rules.

### 13. `graph` full emit: keep it, but bound what gets checked in (note)

I would not cut it. The builder must exist for every other command, so the command is a serializer plus argument parsing, and it is what makes the checks in finding 12 possible at all. The thing to bound is the artifact: no checked-in whole-repo expected graph snapshot (churn, review cost, and another gitleaks surface). Fixture-scoped expected documents only, following the `expected/` scheme lane 2 of #745 established.

### 14. Per-rule mirror fidelity exceeds what #746 consumes (note)

D1 lines 43-48 model all seven-plus `export_plugin_tree` rules separately with rule ids. The investigation asks for less: a `transform_kind` discriminator so a generic edge does not misrepresent the collapse and shim behavior (`topology.md:68`), and its own open question asks whether coarse categories suffice (`topology.md:81`).

Smallest cut: derive pairs for the rules that actually produce pairs, and emit a typed `unmodeled-mirror-rule` for anything else — the same honesty stance the plan already takes for unresolved carriers. The set-equality check in finding 12 then proves coverage exactly, rather than the rule table asserting it.

### 15. The rev-dep mapping is a deliverable the parent cannot verify (note)

D5 lines 121-123 make rev-dep "the first mapped producer". No rev-dep producer exists in this repo, so the mapping can only be exercised against a fixture the same lane authors — self-certifying work. Lane D is otherwise severable and correctly placed last; it does not block #748, which needs only `classify`.

Smallest fix: keep the provider contract and scope/completeness semantics, downgrade rev-dep to a documented mapping plus one fixture, and record in the non-claims that no live producer was exercised.

### 16. "Reverse-dep" appears in acceptance traceability but has no named command (note)

Line 200 traces "SCC/rootless/islands/violations/reverse-dep from one graph" to D6, but D6 offers roots-reaching-p (`explain`) and affected-by-changed-paths (`changed`); neither is stated as "which nodes depend on p". It is probably answerable from the same graph, but the traceability currently asserts a capability no command description claims. Either name it in `explain` (a `--reverse` mode) or say explicitly that `changed --path p` is the reverse-dependency answer.

---

## The single biggest simplification

Delete from #746 everything whose only named consumer is a later issue, and spend the freed lane capacity on the one thing the acceptance names and the plan leaves blank.

Concretely, cut: `registry` nodes, the `configures` edge class, the `derivable-declaration` advisory inventory (findings 4), the `config` and `fixture` roles (finding 5), and per-rule mirror fidelity beyond what pair correctness needs (finding 14). Then write the role classification rule table with its Go-shaped fixture into D1 before any lane launches (finding 2), and restate the #743 contract as a test-exclusion rather than a production-selection (finding 1). That trade is close to work-neutral and moves the plan's effort from the parts with no consumer to the part the whole umbrella depends on.

## Proportionality verdict

Proceed, after re-weighting — not a redesign.

The plan is roughly a third larger than #746's acceptance requires, and the excess is concentrated in exactly the areas with no consumer in this issue, while the acceptance-critical derivation (role classification) is the least specified thing in the document. That is a recoverable imbalance: the cuts are clean removals rather than restructurings, and the specification gap is a table someone can write in an hour with the evidence already in `issue_743.md` and `topology.md`.

Three things should land before lane A launches: the role rule table (finding 2), the corrected `classify` contract (finding 1), and the lane re-sequencing so `classify` arrives second rather than third (finding 8). Findings 6, 7, 9, and 10 are one-sentence additions to the plan that a lane brief must carry. Everything else can be handled during integration.
