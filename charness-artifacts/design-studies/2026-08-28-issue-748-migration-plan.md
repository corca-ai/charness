# Issue #748 plan: retire the Python repository-boundary owners

> Status: rev 2 (two opus bounded reviews applied — contract fidelity;
> scope/sequencing/operability)
> Date: 2026-08-28
> Parent: #744; depends on integrated #746 (typed topology, additive
> commands) and #747 (native distribution machinery, `native_core_path()`
> sum-type; no artifact published yet — main resolves `not-distributed`).
> Also resolves #743 through the same topology owner.
> Investigation record: workflow `issue-748-investigation`
> (5-agent consumer/contract/CI/test inventory, 2026-08-28).

## Objective

Delete the duplicated Python repository-boundary algorithms whose
surfaces are charness-internal and make `native/repograph` the single
owner of export-safe boundaries, mirror-aware doc-reference resolution,
path-target reverse-reference evidence, static standalone-import
selection, and the #743 production/test role classification — typed and
fail-loud wherever the native binary is unavailable. Consumer-shipped
shared helpers (`repo_file_listing.py`, `surfaces_lib` matching) do NOT
migrate in this slice (see "Slice boundary" and "Deferred work").

## Slice boundary (the availability constraint that shapes this plan)

The contract review established that `repo_file_listing.py` (~20
exported importers, including public-skill scripts
`release_claim_surfaces.py` and `quality_skill_scope.py`) and
`surfaces_lib.match_surfaces` (8 consumers, including
`render_critique_section_changed_surfaces.py` — the critique AND retro
adapter DEFAULT command — retro's `check_auto_trigger.py`, and
`check_real_host_proof.py`'s own declared-surface arm) execute inside
consumer repositories via `plugins/charness/`. Until the first
switch-on release publishes a native artifact, every consumer resolves
`not-distributed`; making those helpers binary-dependent now would
hard-break consumer critique/retro/quality gates — and would break the
real-host script UPSTREAM of D8's degradation (its declared-surface arm
calls `match_surfaces` before the raw-glob arm runs). Therefore:

- IN this slice: D2 export-safe, D5 what-reads (narrowed), D6
  plugin-refs, D7 standalone selection, D8 real-host classification,
  D10 export/catalog sync, D11 surfaces audit. All are
  authoring-repo-scoped except real-host-proof, which degrades typed.
- OUT of this slice: `repo_file_listing.py` and `surfaces_lib` matching
  — see "Deferred work" for what is release-gated versus what is an
  open design question.

## Ground facts the design stands on (investigated or probe-verified)

- Only two family scripts are run-quality gates:
  `check-export-safe-imports` (run-quality.sh:1076) and
  `check-plugin-dir-references` (:1105); the latter is ALSO a direct CI
  step (quality-core.yml:90).
- PROBE-VERIFIED (2026-08-28): with `CHARNESS_ALLOW_DEV_NATIVE_CORE=1`
  exported and a built dev binary present, `native_core_path()` on main
  returns `not-distributed` ("native_core declaration is absent") — the
  dev-tree branch at `native_core_resolution_lib.py:148-152` sits
  BEHIND the declaration gate and is unreachable while distribution
  stays deliberately inert. Any gate resolution routed through
  `native_core_path()` alone fails on today's main.
- CI installs no Rust toolchain, but the ubuntu-latest image ships
  cargo (mutation-tests.yml runs `cargo --version` bare).
  quality-core.yml runs neither run-quality.sh nor pytest; it invokes
  gate scripts directly, and carries the
  `local-gate-subset-mirror` gate-policy marker whose honesty
  constrains what steps may be added.
- run-quality exit-3 handling is opt-in per label
  (`UNESTABLISHED_CAPABLE_LABELS`); a non-listed label exiting 3 scores
  as ordinary fail — satisfying the ABI wrapper rule (3 must block);
  exit 70 is never remapped. `.githooks/pre-push`'s docs-only label set
  contains neither migrated label, so docs-only pushes never touch the
  binary.
- `check_real_host_proof.py` never touches native-core today; its
  exported copy is self-contained under `plugins/charness/`. Its
  four-state `evaluation_scope` vocabulary, absent-`required`-key
  structure, and version-refusal guard (upstream of any fold change)
  are test-pinned contracts.
- `classify` emits its report even at exit 3, but hard-fails without a
  surfaces manifest (probe-verified). Role `generated` derives from
  surfaces-manifest `derived_paths` membership (graph_roles.rs:77-79) —
  manifest-configured, NOT purely topological; this bounds what D8 may
  exclude.
- In a real consumer tree, production files classify `unestablished`
  and only rule-3 path shapes (`*_test.go`, `test_*.py`, `testdata/**`)
  or the consumer's own `topology` declaration yield `test` — the
  exclusion contract survives because unestablished keeps the hit.
- Every family script is `consumer_facing: false, decision: exclude` in
  the consumer-validator catalog and absent from the adoption manifest.
- Parity-ledger intentional deltas (exit classes, report-all, no silent
  filesystem fallback, no `CHARNESS_SUPPORT_DIR` relocation in
  export-safe, zero-scope = 3) are ratified contract changes.
- Issue #672 (open) concerns `what_reads_this.py`'s SYMBOL-mode kind
  grouping; D5 retires that mode — reconciled explicitly, not silently
  (see D5).

## Decisions

### D1. Native-binary availability policy (the #747/CI seam)

- One shared resolver shim, `scripts/native_gate_lib.py`, with its OWN
  resolution order (probe-verified necessity above):
  1. `CHARNESS_NATIVE_CORE` override (the test seam);
  2. a healthy MANAGED result from `native_core_path()`;
  3. the dev-tree build `native/repograph/target/release/repograph`
     whenever the crate SOURCE tree exists (authoring checkouts) —
     first-class `dev-tree` provenance, independent of the distribution
     declaration, with no env-var gate for gate execution;
  4. otherwise a loud exit 1 whose remediation is context-typed: crate
     source present → "cargo build --release in native/repograph";
     no `native/` tree (exported/consumer checkout) → "this checkout
     has no native core and no source to build one; the native
     artifact is not yet distributed — run `charness update` once it
     is".
  The PRODUCT resolver `native_core_path()` and its
  `CHARNESS_ALLOW_DEV_NATIVE_CORE` contract are unchanged — doctor and
  install semantics stay exactly as #747 ratified them; the shim is a
  gate-execution policy layered on top, and says so in its docstring.
- Exit codes of the invoked repograph command pass through unchanged;
  exit 70 is never remapped.
- `run-quality.sh` gains a single preflight that resolves the binary
  once and fails fast with the same context-typed message when any
  queued label needs it — one actionable line, not N gate logs; in the
  exported runner (no `native/` tree) the message is the
  not-yet-distributed variant, never a cargo instruction.
- Charness CI (`quality-core.yml`): add a cache-backed PROVISIONING
  step (`cargo build --release --locked` in `native/repograph`; cache
  `~/.cargo` + `native/repograph/target` keyed on `Cargo.lock` +
  `rust-toolchain.toml`). Provisioning is `setup`-bucket work and keeps
  the `local-gate-subset-mirror` marker honest. `cargo test --release`
  does NOT enter quality-core (no run-quality label runs it; adding it
  would falsify the marker) — it runs in `mutation-tests.yml`
  (`scheduled-deeper-check` policy home) and in the parent's local
  battery at every lane integration.
- Consumer repositories: the only migrated surface executing there in
  this slice is real-host-proof (typed degradation, D8). The
  release-adapter checklist already carries the post-publish
  `native_core: healthy` readback obligation.

### D2. Export-safe gate migration

Delete `scripts/check_export_safe_imports.py`. The
`check-export-safe-imports` label invokes `repograph export-safe`
through the D1 shim. The label stays OFF the unestablished-capable
list: exits 1 and 3 both block. Behavioral deltas (report-all,
zero-scope exit 3, non-parsed exit 3) are the parity-ledger-ratified
contract; tests pinning first-violation/exit-1 behavior are rewritten
or deleted, not preserved. The `CHARNESS_SUPPORT_DIR` relocation is not
reproduced (ledger item 9; recorded non-claim).
`tests/quality_gates/support.py` stub entries and
`test_empty_scope_refusals.py` membership follow the new command.
AST-helper unit tests die with the algorithm; detection behavior is
owned by the crate's committed fixture families.

### D5. Path-target reverse-reference owner: additive `repograph what-reads` (narrowed)

New additive command `repograph what-reads --path P [--include-mirrors]
[--detail]` (`repograph.what_reads.v1`) owning exactly the evidence the
#748 acceptance names — literal, glob, and COMMAND evidence for a path
target — plus the typed explanations only the graph can add:

- text-suffix allowlist, fixed exclusion dirs, `plugins/` opt-in;
- path evidence kinds: `literal-path`, `glob-consumption`,
  `basename-glob`, `basename-reference` (path-semantics glob
  compilation preserved);
- command evidence: hits that are carrier path references join the
  crate's `carrier-path-reference`/carrier records as a distinct
  `command-carrier` evidence kind — a capability the Python owner
  never had (it filed these as bare `literal-path`);
- a typed `graph` section: direct dependents and up to three root
  paths (the `explain` projection);
- `unscanned_surfaces` and `zero_result_caveat` preserved.

The `--symbol` and `--config-key` modes are RETIRED with the Python
owner (scope review: zero production consumers; a verbatim taxonomy
port reproduces Python-era blind spots at the largest cost in the
plan). This is a recorded capability reduction, not an omission: open
issue #672 targets the retired symbol-mode grouping and is reconciled
at closeout — its false-zero half was already fixed under #599; its
grouping half now names a retired mode, and the operator decides
whether #672 closes as retired-subject or is re-scoped to the native
command. Delete `what_reads_this.py`, `what_reads_this_fallback.py`,
and their test files; no Python wrapper remains. Docs referencing the
tool update to the native invocation (the doc sweep is P4's named
scope).

### D6. Doc-reference owner: additive `repograph plugin-refs`

New additive command `repograph plugin-refs` (`repograph.plugin_refs.v1`)
porting `check_plugin_dir_references.py`: scan the same doc-glob set for
`<plugin-dir>/TARGET` outside fences/inline code (reusing the crate's
markdown scanning), classify resolved/templated/escapes-package-root/
missing against inventory paths under `plugins/<pkg>/`, plus the
`<authoring-repo>/TARGET` shipped-but-marked-authoring-only check using
the flatten rules already encoded in the D1b mirror table. Exits: 0
validated, 1 findings, 2 usage, 3 unestablished, 70 internal. The
no-plugins-package tree keeps the typed "nothing was validated" exit-0
note, with the reason recorded in ABI.md: a tree without a
`plugins/<pkg>` package is a legitimate consumer-tree shape, unlike
export-safe's zero-scope, where a collapsed selection universe is a
defect. Delete the Python owner; rewire the run-quality label and the
direct quality-core.yml step through the D1 shim. TWO LIVE DOC
REFERENCES to the deleted script must be edited in the same lane
(scope review, the exact scope-omission class the retro paid for):
`skills/shared/references/bootstrap-resolution.md:133` and
`docs/deferred-decisions.md:704` — otherwise the new gate blocks
itself on its own `missing` finding.

### D7. Standalone-import probe: native selection, Python runtime

`check_standalone_imports.py` keeps only what Python alone can prove:
subprocess-executing probe shapes and classifying cycle/import-error/
timeout. Its discovery patterns, module derivation, shape construction,
and `--changed` selection are deleted; it consumes
`repograph standalone-targets` JSON (via the D1 shim) and executes the
emitted `shapes[].command` strings. Payload keys, verdict semantics,
and scope notes stay; the payload records the selection provenance.
The two enumeration-completeness tests
(`test_every_tracked_module_is_either_discovered_or_deliberately_excluded`,
`test_the_exported_mirror_enumerates_its_own_modules`) CANNOT run
against a canned document without losing their point; they move to the
D9 real-binary carve-out (run against the resolved real binary,
failing loud — never skipping — when it is unavailable).
`targets[].path` is inventory-relative, so the mirror comparison
remains content-valid.

### D8. #743: role-based exclusion in real-host proof

- Additive `classify` flag `--surfaces-optional`: when supplied and the
  surfaces manifest (default or explicit) does not exist,
  classification proceeds with an empty surface set and a typed
  top-level `surfaces: "absent"` marker. WITHOUT the flag, behavior is
  unchanged (manifest failure stays a hard exit-3 diagnostic for every
  existing caller — absence-tolerance is opt-in, requested by the
  real-host fold only). ABI.md updated in the same change.
- `check_real_host_proof.py` fold change (raw-glob arm only; the
  declared-surface arm is untouched semantic policy and keeps calling
  the Python `match_surfaces`, which this slice does not migrate):
  candidate hits from `matches_any(globs)` are classified via
  `repograph classify --surfaces-optional --path ...` on the consumer's
  `--repo-root`, resolved through the D1 shim; a hit is EXCLUDED only
  when its role is `test` — role `test` ONLY, not `generated`: the
  contract review established `generated` is surfaces-manifest-
  configured, so excluding it would let a manifest edit silently drop a
  release-relevant generated-mirror hit (permissive inversion on a
  publish gate). `production`, `doc`, `generated`, `unestablished`, and
  `unestablished-absent` (deleted paths) all keep the hit — fail-safe
  toward requiring proof.
- Payload contract, per `evaluation_scope` state:
  - `evaluated`: `path_hits` KEEPS its published meaning as the hits
    that drive the verdict — the post-exclusion list, preserving
    `required == bool(surface_hits or path_hits)`;
    `excluded_path_hits: [{path, role}]` lists what the exclusion
    removed; `test_exclusion: {status: applied | unavailable,
    native_core: <typed status>}` is ALWAYS present in `evaluated`
    payloads, so "unavailable" is distinguishable from "never
    attempted".
  - `empty`, `not-configured`, `not-established`/broken: byte-for-byte
    unchanged — no new keys; the absent-`required`-key structure and
    exit table (0/1/3) are untouched. The fold can never affect
    whether `required` is present.
- Degradation: when the D1 shim resolves non-healthy the fold runs
  positive-only (today's behavior) with
  `test_exclusion: {status: unavailable, native_core: ...}` —
  over-triggering, never false-negative, never silent.
- No new release-adapter keys. Ownership statement: the exclusion is
  owned by the topology layer — the built-in language convention table
  plus the consumer's own optional `topology` declaration — not by
  release-adapter negative syntax. The release adapter keeps owning
  only "these triggers require host proof".
- Proof: (a) a consumer-shaped fixture repo (Go tree: production `.go`
  hit kept, `_test.go` excluded, `testdata/` excluded, `README.md`
  doc-role trigger still a hit, deleted production path keeps the hit,
  generated-mirror path keeps the hit, no `.agents/surfaces.json`)
  driven through the real fold with `CHARNESS_NATIVE_CORE` pointing at
  a fake binary emitting canned `classify.v1` documents; (b) the same
  scenario against the REAL dev-tree binary executed once by the
  parent and recorded in evidence; (c) the degradation state pinned
  with the resolver returning non-healthy. Close #743 on (a)+(b); the
  consumer-live managed-artifact readback stays #747's
  release-checklist obligation (typed non-claim).
- `skills/public/release/references/real-host-proof.md` and
  `adapter-contract.md` document the derived exclusion and the
  degradation state.

### D9. Test seam policy

Python-side wrapper/fold tests never require a compiled binary: they
inject fake binaries emitting canned v1 schema documents (the schema IS
the seam), via `CHARNESS_NATIVE_CORE` or shim injection. Native
behavior is owned by cargo tests over committed fixtures. EXPLICIT
real-binary carve-out: the D7 enumeration-completeness pair (and any
test whose value is comparing native output against the real tree)
resolves the real binary through the D1 shim and fails loud with the
D1 remediation when unavailable — never a skip. The integrated tree is
proven by the parent running the full battery plus `cargo test` with
the real dev-tree binary, and by CI provisioning the same binary (D1).

### D10. Export, catalog, and dependency consequences

Deleted scripts leave the plugin export through the canonical exporter
(parent runs the sync; no hand edits). Consumer-validator-catalog
entries for deleted paths are removed (all are `decision: exclude`; no
consumer contract changes). `staged_commit_gate_plan.py`'s literal
`check_standalone_imports.py` reference follows D7. Deleted scripts
take their `--require-git-file-listing` flags with them; the flag
remains meaningful on the unmigrated `repo_file_listing` consumers.
Bootstrap/mutation requirement files are checked for dependencies made
unreachable (expected: none — the family is stdlib-only).

### D11. Derivable-membership audit of `.agents/surfaces.json`

After the migrations land, a parent-owned audit walks every surface:
source/derived patterns that only repeat derivable membership (now
owned by `classify`) are removed; every surviving raw path declaration
must carry a note naming the policy it alone owns. The audit's
per-surface disposition table goes in the #748 evidence record. This is
an audit of declarations, not a manifest-schema redesign.

## Deferred work (recorded, not scheduled in this slice)

- `surfaces_lib.match_surfaces` → native projection: RELEASE-GATED
  (consumer blast radius; must wait until consumers resolve `healthy`).
  Carried audit obligations from review: binary-unavailability must
  raise a type distinct from `SurfaceError`
  (`staged_commit_gate_plan.py:230-236` swallows `SurfaceError` into an
  empty fast-gate set — a silent pre-commit disarm — and
  `boundary_probe_lib.py:132` deliberately propagates); and
  `path_matches_patterns` survives inside `load_surfaces`'s own
  generated-markdown validation path, not only in `boundary_probe_lib`.
- `repo_file_listing.py` → native projection: OPEN DESIGN QUESTION,
  not merely release-gated. The scope review showed a port cannot
  single-own matching while the `CHARNESS_SUPPORT_DIR` external-support
  splice globs a tree outside the git inventory, the module's API
  (including the re-exported `support_dir`) is REQUIRED by the
  gitignore-scan-hygiene repo rule, and the split-layout tests exercise
  non-git roots. Absorbing the external-support policy is a design
  decision that precedes any port; until then no `repograph list`
  command is added (a port now would leave two matchers with a policy
  seam — the exact #744 disease).
- Until then the Python fnmatch fold and repograph's matcher coexist;
  the drift guard is the repograph-side equality pinning (classify
  surface membership == match-surfaces v1) plus #746 parity evidence.
  A recorded, bounded exception to the umbrella's no-duplicate-owner
  rule — not an open-ended shadow mode.

## Execution shape

Codex lanes (`gpt-5.6-luna`, xhigh), briefs from
`.agents/lane-brief-template.md`; parent integrates serially and runs
`./scripts/run-quality.sh --full` IMMEDIATELY after integrating each
production-surface lane. Seam-first sequencing (scope review):

1. Lane RA `748-classify-optional` (Rust, small, lands first):
   D8 `--surfaces-optional` + ABI.md. Concurrent with S1 (disjoint
   trees).
2. Lane S1 `748-seam-export-safe` (Python): D1 shim with the
   dev-tree-first-class resolver + run-quality preflight + CI
   provisioning step (+ cargo-test relocation to mutation-tests.yml) +
   D2 rewire/deletion/tests. Proves the seam on exactly one gate;
   everything downstream inherits it. Parent full battery immediately
   after.
3. Lanes RB `748-plugin-refs` and RC `748-what-reads` (Rust,
   sibling-concurrent after RA; parent reconciles lib.rs/ABI unions).
4. Lane P5 `748-real-host-classify` (Python, after RA + S1): D8 fold +
   fixtures + docs (fake-binary seam for tests; parent runs the
   real-binary proof).
5. Lane P3 `748-standalone-probe` (Python, after S1): D7 + D9
   carve-out.
6. Lane P4 `748-native-rewire-cleanup` (Python, after RB/RC): D6
   rewire/deletion including the two NAMED doc edits, what-reads
   Python deletion + doc sweep, catalog updates.
7. Parent: serial integration, export syncs, D11 audit, evidence
   record, #743 then #748-slice closeout (deferred work recorded on
   the issue, #672 reconciliation surfaced to the operator).

run-quality.sh and tests/quality_gates/support.py are each edited by at
most one lane at a time (S1 then P4, serialized) — the review's two
same-file merge traps are removed by sequencing, not hope.

## Acceptance traceability

Export-safe native ownership → D2; what-reads literal/glob/command
evidence + typed root/edge explanations → D5 (narrowed to the
path-target contract the acceptance names; symbol/config-key retirement
recorded); standalone static selection + Python runtime probe → D7;
#743 via native topology without a file catalog → D8; absorbed
algorithms deleted in-slice with projection-only wrappers →
D2/D5/D6/D7; generated copies via canonical exporter → D10; behavioral
fixtures over tombstones → D2/D5/D6/D9; surfaces.json derivable
membership → D11; one canonical command per capability → D1 shim +
per-command ownership; whole-repo parity + consumer fixture → D8 proof
+ parent battery; dependency cleanup → D10. The
inventory/matcher-consumption acceptance bullet is NOT met by this
slice — deferred work is recorded on the issue rather than closed
silently; #748 closes only when the umbrella owner accepts that
recorded boundary or the deferred slice lands.

## Non-claims

- Static selection is not runtime import proof; D7's probe remains the
  runtime owner and says so in its payload.
- No consumer-live managed-artifact proof before the first switch-on
  release; real-host exclusion in consumer repos stays
  typed-unavailable until then.
- This slice does not migrate `repo_file_listing.py` or `surfaces_lib`
  matching; that duplication survives, bounded and recorded, with the
  release gate (matcher) and an open design question (inventory) as its
  expiry conditions.
- `--symbol`/`--config-key` reverse-reference queries are retired, not
  ported; #672 is reconciled at closeout, not silently absorbed.
- `load_surfaces` validation, changed-path git acquisition,
  `path_matches_patterns`, and the `CHARNESS_SUPPORT_DIR` splice remain
  Python, each with a recorded reason; #749 owns the remaining-Python
  inventory.
- No old internal module paths are preserved without a current
  consumer; no "must not exist" tombstone tests are added for retired
  filenames.
- The remaining Python test corpus is #753's scope, not this plan's.
