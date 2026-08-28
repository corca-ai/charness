# Issue #748 evidence record (slice 1)

> Date: 2026-08-28
> Plan: `../2026-08-28-issue-748-migration-plan.md` (rev 2; two opus
> bounded reviews applied — contract fidelity, scope/operability)
> Lanes: RA `748-classify-optional`, S1 `748-seam-export-safe`,
> RB `748-plugin-refs`, RC `748-what-reads`, P3 `748-standalone-probe`,
> P5 `748-real-host-classify`, P4 `748-native-rewire-cleanup` — all
> Codex (`gpt-5.6-luna`, xhigh), integrated serially by the parent with
> a full `run-quality.sh --full` battery immediately after every
> production-surface integration (retro improvement honored; it caught
> real defects each time — see "Integration catches").

## What shipped

- `scripts/native_gate_lib.py` — the single gate-side resolver/runner
  for the repograph binary (override → managed-healthy → dev-tree when
  crate source exists; context-typed loud failure; exit passthrough,
  70 never remapped). run-quality gained a fail-fast preflight over
  `NATIVE_GATE_LABELS`; quality-core.yml gained a cache-backed
  provisioning build; `cargo test --release` runs in mutation-tests.yml
  (scheduled-deeper-check home) so the `local-gate-subset-mirror`
  marker stays honest.
- DELETED Python owners: `check_export_safe_imports.py` (gate →
  `repograph export-safe`), `check_plugin_dir_references.py` (gate +
  CI step + commit-time plan → `repograph plugin-refs`),
  `what_reads_this.py` + `what_reads_this_fallback.py` (owner →
  `repograph what-reads`, path-target contract), and
  `check_standalone_imports.py`'s discovery/selection half (selection →
  `repograph standalone-targets`; the Python runtime probe remains the
  runtime-import owner and records its selection provenance).
- Additive native commands: `plugin-refs` (doc-placeholder resolution
  over the mirror rule table), `what-reads` (literal/glob/basename
  evidence + NEW `command-carrier` evidence kind + typed graph
  dependents/roots; `--symbol`/`--config-key` retired per plan D5),
  `classify --surfaces-optional` (absence-tolerant, opt-in, invalid
  manifests still hard-fail).
- #743 resolved and CLOSED (verified backend readback): real-host
  raw-glob hits are classified via
  `classify --surfaces-optional`; only role `test` is excluded;
  `excluded_path_hits` + `test_exclusion` payload evidence; typed
  positive-only degradation when no binary resolves.

## Parent-executed verification (integrated tree)

- Cargo battery at every Rust integration (fmt, clippy `-D warnings`,
  tests, release build): final state 60+ tests green across suites.
- Full standing battery `78 passed, 0 failed` after S1, P3, P5, P4 and
  the ratio-surface lane (five separate full runs).
- Real-repo cross-checks (fake-vs-real binary discipline, D9):
  - export-safe: gate label smoke end-to-end through the shim;
  - plugin-refs: native vs Python owner on the real tree — identical
    clean verdicts; native reports 65 references (41 resolved,
    4 templated, 20 authoring-only, 0 findings) where the Python owner
    silently dropped two `<plugin-dir>/...` ellipsis targets (typed
    improvement, recorded);
  - what-reads: `--path scripts/surfaces_lib.py` — reference_kinds
    byte-equal to the Python owner (153 hits: 75 literal-path,
    69 glob-consumption, 4 basename-glob, 5 basename-reference) plus
    the new graph section (11 dependents, 3 root paths) and a
    fixture-proven `command-carrier` hit;
  - standalone probe: full real run — 726 modules, verdict ok,
    `selection: repograph standalone-targets v1`;
  - real-host (#743, D8 proof b): consumer-shaped repo with the real
    binary — test-only changeset `required: false` with the test-role
    exclusion listed; mixed changeset `required: true` driven by the
    production file; no-binary checkout typed
    `test_exclusion: unavailable`.

## Integration catches (defects found by the parent battery/review, fixed in-tree)

1. S1: boundary-bypass ratchet caught the shim's ad hoc
   `sys.path.insert` fallback and a new test→script subprocess
   boundary; fixed with the sanctioned `import_repo_module` route and
   in-process `main()` tests.
2. RB: the lane masked inline backtick code (following an ambiguous
   brief sentence), emptying the gate's subject set on the real repo
   (0 references vs the Python owner's dozens). Contract corrected
   from the Python source: only fences/HTML comments are skipped;
   inline code IS scanned.
3. P5: the classify invocation passed one `--path` flag followed by
   bare paths — a usage error (exit 2) on every multi-path changeset
   that silently degraded the exclusion. Caught by the parent's live
   multi-path proof; fixed to one flag per path and pinned by a
   strict-argv fake binary.
4. P4 follow-through: deleting the Python owner silently dropped the
   commit-time `check-plugin-dir-references` gate from
   `staged_commit_gate_plan.py` (a consumer the plan had not named);
   rewired to the canonical shim command, restoring the planned-label
   contract.

## D11 audit: `.agents/surfaces.json` derivable membership

All 42 surfaces carry notes and at least one sync/verify command; none
is a pure catalog. The manifest's path declarations are change-routing
policy (which command runs when these paths change), not derivable
membership lists — file DISCOVERY lives inside gates, not in the
manifest. The one derivable-looking class (mirror `derived_paths` such
as `plugins/charness/**`) is load-bearing routing for export-sync
gates; consolidating it onto classify-derived roles belongs to the
deferred matcher slice. Disposition: no removals in this slice; the
acceptance bullet's target class ("path sets that exist only to make a
gate discover files") has no members in the current manifest.

## Deferred work and reconciliations (recorded, not silent)

- `repo_file_listing.py` and `surfaces_lib` matching stay Python:
  consumer blast radius until the first artifact-bearing release
  (matcher: release-gated) and the `CHARNESS_SUPPORT_DIR`
  external-splice design question (inventory). Details and audit
  obligations: plan rev 2 "Deferred work".
- Issue #672 targets the retired `--symbol` mode's kind grouping; it
  needs operator disposition (close as retired-subject or re-scope to
  the native command).
- The consumer-live managed-artifact readback stays the #747 release
  checklist obligation; until the first switch-on release, consumers
  see typed degradation only in real-host-proof (the sole
  consumer-executing migrated surface in this slice).

## Non-claims

- Static selection/classification is not runtime proof; the Python
  standalone probe and the release checklist own their runtime claims.
- The #748 acceptance bullet on inventory/matcher native consumption is
  NOT met by this slice; the issue stays open on that recorded boundary
  unless the umbrella owner accepts the split.
- No tombstone tests were added for retired filenames; recurrence is
  prevented by the native commands being the only reachable owners.
