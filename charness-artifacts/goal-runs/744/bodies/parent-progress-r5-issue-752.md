## Situation

Charness currently implements its managed CLI, repository inventory, surface matching, import checks, package/export boundaries, and most quality orchestration in Python. Several validators inspect overlapping projections of the same repository topology, while the checked-in plugin export duplicates canonical scripts and skills into a second install tree.

A read-only survey on 2026-08-28 found 2,007 tracked Python files and about 494k Python lines including tests and generated plugin copies. The canonical `scripts/` tree alone contains 359 Python files and about 87k lines. Across canonical Python sources, 266 files use dynamic path loading or import machinery, 131 launch subprocesses, and 91 perform repository walks or glob scans.

The repository also carries a 1,016-line `.agents/surfaces.json` manifest with 43 surfaces, 212 source patterns, 68 derived patterns, and 83 verification commands. Some of those declarations express human policy, but others repeat package, source, generated-mirror, or command topology that could be derived mechanically.

## Experience

Maintainers and consuming repositories pay for this structure in three ways:

- repeated Python startup, parsing, filesystem traversal, and subprocess fan-out make broad checks expensive;
- native package facts and manually maintained path catalogs can drift into multiple owners;
- type annotations exist, but there is no repository-wide static type checker, and dynamic loading prevents annotations from closing many cross-module contracts.

Measured on the current checkout, `./charness --help` takes about 0.22 seconds and `catalog list` about 0.69 seconds, so CLI startup is not the first bottleneck. The full standalone-import check takes about 9.4 seconds wall time and 133–135 seconds of aggregate CPU, while the export-safe import scan takes about 2.6 seconds. The dominant opportunity is to stop rediscovering and reinterpreting repository topology in many processes.

Issue #743 shows the same ownership failure in a consumer-facing contract: a release adapter must either over-trigger on adjacent test files or copy an exact production-file catalog that can silently become stale.

## Impact

Adding another Python validator or translating each script independently would preserve the underlying duplication. Rewriting every Python script as an independent native binary would produce the same ownership graph with faster processes and a larger distribution burden. Without a single typed owner, Charness cannot reliably derive package boundaries, explain reachability, identify validator/test-only islands, or reduce its manually curated surface catalogs.

## Desired outcome

Introduce one typed Rust repository-analysis core that owns facts derivable from repository state:

- tracked and relevant untracked file inventory;
- package, skill, adapter, entrypoint, generated-mirror, test, and command-carrier identities;
- typed import, invocation, configuration, packaging, mirror, and test edges;
- strongly connected components, rootless components, validator/test-only islands, and declared boundary violations;
- deterministic changed-path projection and explanation of why a file or package is selected.

Keep semantic intent explicit rather than pretending it is derivable. Human decisions such as why a surface matters, which live proof a change requires, and which exception is intentional remain in a small declarative owner. The native graph derives the file membership and topology beneath those claims.

For TypeScript and JavaScript, Charness should ingest a package-local analyzer such as rev-dep through a versioned provider result instead of implementing another language parser. For Python, the Rust core may own static import extraction and target selection, but a bounded Python runtime smoke remains the owner of actual import side effects.

## Ownership contract

- Rust core: repository inventory, typed topology, derivable membership, reachability, and boundary algorithms.
- Small declarative manifests: non-derivable policy, named semantic surfaces, intentional exceptions, and external-proof requirements.
- External language analyzers: language-specific import edges, with absence or incompatible output reported as unestablished rather than clean.
- Python runtime probes: behavior that only an actual Python interpreter can establish.
- Compatibility wrappers: existing output and exit-code projection only; no duplicate analysis logic.

## Work sequence

1. Prove the architecture and parser/ABI choices against representative current validators and recorded performance evidence.
2. Establish the typed topology core and external-analyzer provider contract.
3. Ship a version-bound native artifact without requiring a Rust toolchain on consumer machines.
4. Migrate one complete repository-boundary family, delete absorbed Python owners, and resolve #743 from native topology rather than a copied production catalog.
5. Inventory the remaining Python responsibility and decide whether the top-level CLI should move after the core has proved its value.

Core construction and distribution preparation may proceed independently after the spike freezes their shared ABI. Owner migration waits for both the core contract and its runtime availability. CLI migration is deliberately last.

## Completion criteria

- One native inventory and graph is the canonical owner for every migrated derivable fact.
- Existing user-facing verdicts, exit semantics, and failure scope remain compatible or change through an explicit contract decision.
- Each migrated slice deletes the absorbed Python algorithm and its generated copy; a thin compatibility wrapper may remain only when a current consumer requires the old command.
- Every remaining manual path set states the non-derivable policy it owns; no package/source catalog exists only to make a gate discover files.
- JS/TS graph support uses a package-local analyzer provider and does not make rev-dep a mandatory dependency of Charness itself.
- Runtime Python import smoke is narrowed by static reachability where honest, but is not reported as statically proven.
- Native artifact installation, version binding, update, rollback, checksum verification, and `doctor` readback are proven on the repository's actual supported host matrix.
- Retained Python has a defined role and a practical type-checking boundary without a broad ignore baseline.

## Non-claims

- This is not a wholesale Rust rewrite of public skill prose, assets, or every orchestration script.
- Rust does not statically prove Python import side effects, provider behavior, or live host behavior.
- Charness does not reimplement rev-dep or claim one parser can understand every language.
- This work does not expand the supported host matrix merely to justify a release artifact table.
- A new native core is not completion while duplicate Python owners remain active.
- This umbrella is independent of the nearly complete friction-removal Goal Run #736 and must not widen its final closeout child #742.

## Linked sub-issues and dependency order

1. #745 proves the Rust parser, graph, ABI, parity, and performance decision without changing production gates.
2. #746 builds the typed topology and external-analyzer provider contract after #745 freezes the shared model.
3. #747 establishes version-bound native distribution after #745 freezes the executable and ABI. It may proceed in parallel with #746 except where they share that frozen contract.
4. #748 migrates and deletes one complete Python repository-boundary owner family after #746 and #747 are usable.
5. #749 reduces and type-checks the retained Python/CLI layer after at least one complete migration provides real evidence.
6. #743 remains the existing consumer-facing production/test catalog problem. The #746/#748 path must resolve it from the same topology owner; do not close it merely because the new graph exists.
7. #753 prunes the test corpus with graph and mutation evidence once #746's derivations are usable (they are, as of 2026-08-28). It is independent of #748/#749, feeds #749's retained-Python role definition, and must not weaken the behavioral proof floor the migrations rely on.

## Weak direction

Start with one Rust crate containing a library and a small machine-facing binary. Split crates or replace the human-facing CLI only after distinct consumers make those boundaries real.

<!-- charness-goal-run:v1
{
  "binding_path": "charness-artifacts/goals/2026-08-30-close-current-open-issues-goal-run.binding.json",
  "binding_schema": "charness.goal-binding/v1",
  "binding_sha256": "2b5ac12a3722897bc5a11e88a881b45784adcbaab5e84840629ccd1d57421eb8",
  "bootstrap_verification": "verified-target-roundtrip",
  "current_membership_sha256": "8c7d8a81f9fcb8d66977cca5ee569a8d8bbdd4632508f06fe980dd92a8f312b8",
  "draft_path": "charness-artifacts/goals/2026-08-30-close-current-open-issues-goal-run.md",
  "draft_sha256": "eec33587771e5f6abf0e06eb32b1291f475b5b549860c96f73f89218fda44e20",
  "initial_graph_sha256": "e6be1f983d6c3851a1f4810ec45b4980c027a7d49fccb5be724d3e261e9da475",
  "parent_identity": {
    "number": 744,
    "repo": "corca-ai/charness",
    "url": "https://github.com/corca-ai/charness/issues/744"
  },
  "progress": {
    "completed": 8,
    "membership_sha256": "8c7d8a81f9fcb8d66977cca5ee569a8d8bbdd4632508f06fe980dd92a8f312b8",
    "next": {
      "key": "issue-752-worktree-readiness",
      "number": 752,
      "repo": "corca-ai/charness",
      "state": "OPEN",
      "url": "https://github.com/corca-ai/charness/issues/752"
    },
    "open": 9,
    "revision": 5,
    "schema": "charness.goal-progress/v1",
    "total": 17
  }
}
-->
