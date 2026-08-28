# Issue #746 evidence record

> Date: 2026-08-28
> Plan: `../2026-08-28-issue-746-topology-core-plan.md` (rev 2)
> Lanes: 746-graph-model, 746-carriers, 746-classify, 746-explain,
> 746-analyzer — all Codex (`gpt-5.6-luna`, xhigh), integrated serially by
> the parent with two manual merge reconciliations (lib.rs/ABI.md command
> unions; one GraphReport field reconciliation commit).

## What shipped (all under `native/repograph`)

Typed graph core (`graph_model`, `graph_roles`, `graph_imports`,
`graph_mirrors`, `graph_carriers`, `graph_queries`, `graph_components`,
`graph_analyzer`) and five additive commands — `graph`, `carriers`,
`classify`, `changed`, `components`, `explain` — documented in `ABI.md`
alongside the four frozen v1 commands; analyzer provider contract
(`repograph.analyzer_result.v1`, `deny_unknown_fields`) with the rev-dep
mapping documented in `ANALYZERS.md` (fixture-only; recorded non-claim).

## Parent-executed verification (integrated tree)

- Cargo battery: 56 tests green (49 unit + integration suites), fmt,
  clippy `-D warnings`, release build; docs gate PASS.
- Determinism: double-build byte-equality via pinned `--file-list`.
- Whole-repo runs: 8,144+ nodes, 9,100+ edges; invokes 174 with 28 typed
  unresolved carriers (21 tokenizable, 7 opaque) and 17 path references;
  labels 97 vs the Python reader's 98 with the single YAML
  `startup_probes` label as the typed known gap.
- Negative fixtures verified on the real repo: the pre-commit echo-advice
  line and the variable-target `queue_selected` line produce no invokes
  edge.
- Ground-truth battery:
  - frozen-ABI oracle: `export-safe` universe (713) and
    `standalone-targets` (718) fully contained in graph file nodes;
  - mirror SET equality: derived destinations = every tracked
    `plugins/charness` path plus the two root marketplace manifests;
  - validator recall: all 10 `wired: true` validator entries reachable
    from validation roots;
  - carrier recall vs `check_plugin_asset_command_carriers.py`: vacuous
    (the oracle is a green negative check) — recorded, not claimed;
  - whole-repo `classify` census (6,466 paths): production 807, test
    578, doc 3,495, generated 2, unestablished 1,584 — every
    unestablished path in a non-package tree (charness-artifacts,
    .agents, integrations, …), matching the declared package model;
  - skill set comparison: 21 skills; `skills/public/handoff` contains
    only gitignored `__pycache__` residue and is correctly invisible to
    the snapshot (the plan's malformed-skill "live case" assumption was
    wrong; the behavior is fixture-pinned instead).
- #743 contract: exclusion-based `classify` proven on fixtures
  (production hit, `_test.go` exclusion, doc-role raw-glob trigger still
  a hit, unestablished fail-loud, `absent-from-snapshot` presence for
  deleted paths). Production wiring of `check_real_host_proof.py` is
  deliberately #748/#743 scope.

## Derived findings worth keeping

Six real 2-file static import cycles in `scripts/` (e.g.
`check_doc_authoring_preflight.py` ↔ `doc_authoring_rules.py`) surfaced by
`components`; the runtime standalone smoke passes, so these are
deferred-import patterns — static-graph-vs-runtime distinction behaving
as designed. 5,544 rootless components and 1,095 validator/test-only
islands are report-only v1 numbers, not verdicts.

## Final integrated proof

`./scripts/run-quality.sh --full`: 78 passed, 0 failed (113.5s) at the
integrated head, after the standing-gate repair pass (32 regressions the
focused lane checks missed — 15 from a parent-authored multi-line adapter
entry and critique-record format, 17 repaired by a dedicated codex lane —
plus 8 full-battery gate failures triaged: 4 caused by this work and
fixed, 4 pre-existing debts fixed at the operator's direction, including
the D33 task-run module split).
