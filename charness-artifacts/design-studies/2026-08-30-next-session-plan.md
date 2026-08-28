# Next-session plan: retire the native-core distribution layer, then close out

> Date: 2026-08-30 (written at the end of the 2026-08-29 session, with the
> operator, after the v8.0.0 release was deliberately HALTED).
> Supersedes `2026-08-29-next-session-plan.md`, whose keystone (ship the
> switch-on release) is withdrawn.
> Inputs: `charness-artifacts/debug/2026-08-29-native-artifact-sidecar.md`,
> `charness-artifacts/spec/native-artifact-roundtrip.md`,
> `2026-08-28-issue-748-migration-plan.md` rev 2 (Deferred work),
> `issue-753/2026-08-28-jtbd-audit-quality-gates.md`.

## Read this first

The operating lesson the 2026-08-29 session paid for, three times:

> **A verification failure is investigated by suspecting the verifier first.**
> Before satisfying a refusal, name who consumes the value it demands.

Three separate refusals that session all turned out to demand nothing:
the native-artifact sidecar (contents discarded on the next line), the
gate-side `packaging/charness.json` requirement (the gate downloads nothing),
and — a session earlier — the test-production ratio's verdict (the denominator
was wrong, not the corpus). In each case the cheap disconfirmer was one grep for
who reads the demanded value.

## Operator decision that shapes everything below (2026-08-29)

**The native-core distribution layer is to be retired, not repaired.** No
measurement study first — the decision is made. `charness` already owns an
external-tool control plane that installs missing binaries; a missing toolchain
is something to install, not something to design a parallel distribution
lifecycle around.

Do not re-open this as "should we?". Open it as "what exactly comes out, and
what replaces it?".

## Step 1 — Retire the distribution layer (the keystone)

### Why it is redundant, with the evidence already gathered

- `integrations/tools/*.json` declares 15 tools with
  `lifecycle.install.commands`, `platforms`, `degradation.when_missing`, and
  `doctor_policy`; `charness tool doctor <id>` and `charness tool install <id>`
  are the operator surface. `nose` is `doctor_policy: required` and the quality
  `doc-duplicates` phase fails closed without it — so "a required external
  binary must be installed" is already a first-class concept here.
- **Three of those tools already install through cargo**: `awiki`, `lychee`,
  and `tokei` all shell `if command -v cargo >/dev/null 2>&1; then cargo install
  ...`. The repo already depends on cargo in practice.
- `tokei` is the sharp case: `check-test-production-ratio` is now BLOCKING, and
  `--engine auto` silently falls back to `splitlines` when tokei is absent,
  where the same tree measures **1.0415 → over-max → FAIL** (0.9955 with
  tokei). The blocking gate already assumes a cargo-installed tool.
- The Rust crate **ships in git**: `git ls-files native/` → 207 files, present
  in HEAD's tree since `9d2ba2ff3 spike(745)`. The managed checkout at
  `~/.agents/src/charness` is a full (non-sparse) clone, so a consumer that runs
  `charness update` already receives the source.
- Building from the checkout you are running makes `stale`, `incompatible`, and
  `source_drift` **structurally impossible** — definitionally the same commit.
  Digest-matching a downloaded artifact only imitates that invariant after the
  fact.

### What comes out

Everything below exists solely because a prebuilt binary is downloaded instead
of built from source that is already present:

- `scripts/native_core_lib.py` — download, checksum, staging, extraction,
  atomic activation, `current` pointer, version pruning, rollback,
  `PHASE_STATUSES` (12 members).
- The acquisition half of `scripts/native_core_resolution_lib.py` — the
  `native_core` declaration read, `supported_tuples`, `artifact_declaration`,
  and the `NativeStatus` members that only describe download/activation states
  (`awaiting-artifact`, `offline`, `unsupported-tuple`, `stale`, `corrupt`).
- `scripts/build_native_artifact.py`, `scripts/check_native_release_asset.py`.
- `skills/public/release/scripts/publish_release_native_artifact.py` and the
  `release_upload` / `release_assets` ops in `publish_release_helpers.py` —
  built 2026-08-29, never used for a published release.
- `native_core` in `packaging/plugin.schema.json` (`nativeCore`,
  `nativeCoreVersion`, `nativeCoreArtifact` definitions) and the declaration in
  `packaging/charness.json`.
- The release-adapter `real_host_checklist` item 1 (native_core healthy
  readback after publish).
- Open follow-ups that evaporate with the layer: archive reproducibility (the
  gzip mtime in `_write_archive`), the `artifact.json` asset-name collision
  across tuples, and `host_tuple()`'s non-Rust triples
  (`arm64-unknown-darwin` vs the real `aarch64-apple-darwin`).

### What replaces it

A `repograph` entry in the tool control plane, built from the managed
checkout's own `native/repograph/`. Design decisions to settle in `spec`
before implementing:

1. **Tool identity**: is the declared tool `repograph` (built from source, with
   cargo as a prerequisite) or `cargo`/`rustup` (with repograph built by a
   charness command)? The former keeps one doctor line for the thing gates
   actually need.
2. **Where the built binary lands and how it is found.** `native_gate_lib`'s
   resolution order is the surviving consumer; it currently looks at
   `repo_root/native/repograph/target/release/repograph`, which is wrong for a
   consumer repo (that is the SUBJECT repo, not the provider). Resolution must
   key off the managed checkout.
3. **Staleness**: rebuild when the crate source is newer than the built binary.
   This replaces the entire skew-detection vocabulary with one mtime/hash
   comparison against source that is present.
4. **Degradation** when cargo is absent and cannot be installed (offline,
   restricted host): `degradation.when_missing` in the manifest, matching how
   `nose` already declares it. The typed-degradation contract from #748 D8
   stays; only its cause changes.
5. **First-build cost** is real (toolchain install plus a release build). Decide
   whether the build is lazy-on-first-gate-use or eager in `charness update`,
   and say so in the manifest notes.

### Issues to file/update

- New issue: retire the native-core distribution layer in favour of the tool
  control plane. Link this plan, the debug artifact, and the tokei/awiki/lychee
  precedent.
- **#747 must be re-opened or superseded.** It is CLOSED, and its acceptance
  claims installation/update/rollback/checksum/doctor readback are "proven on
  the repository's actual supported host matrix". That was proven with
  consumer-derived fixtures; the 2026-08-29 roundtrip work re-proved the eight
  scenarios honestly, but the layer they prove is the one being retired. Say
  that plainly rather than leaving a closed issue asserting a shipped capability.
- #744 umbrella: its step 3 ("Ship a version-bound native artifact without
  requiring a Rust toolchain") is the premise being reversed. Record the
  reversal on the umbrella.

## Step 2 — The halted release

State as of `2026-08-29`, all committed, tree clean, full battery **78/0**:

- The attach step, the sidecar fix, the roundtrip gate, and the eight-scenario
  replay are all integrated and green. **Keep them until step 1 decides what
  goes** — they are the accurate inventory of what the layer does.
- `packaging/charness.json` carries a `native_core` declaration for
  `8.0.0` / `x86_64-unknown-linux-gnu`, sha256
  `19f6be7f913fccaf07c4ffe4ce3eb7be342505b4e6e9a69d4b5100873842f70e`, matching
  an archive built at `runtime_root(repo)/native-artifacts/`. **Nothing was
  published**: no `v8.0.0` tag, no GitHub release, `origin/main` is ~85 commits
  behind local `main`.
- `charness-artifacts/release/latest.md` is an ABANDONMENT record for the
  2026-08-28 prepare, carrying `- target version: 8.0.0` (the
  current-pointer-freshness gate requires the claim) and no prepared marker, so
  a fresh release run is unblocked whenever one is wanted.

Decide early in the session: does a release ship BEFORE step 1 lands (with the
declaration removed, i.e. a plain release with `native_core` absent and every
readback reporting the typed not-distributed state), or after? Publishing with
the declaration present would freeze the asset-name rule, tuple key space, and
manifest schema of a layer that is being retired.

## Step 3 — #748 slice 2: `match_surfaces` → native projection

Release-gated in the original plan; that gate is now moot in its original form,
so re-derive the trigger. The three deferred audit obligations were verified at
line level on 2026-08-29:

- `staged_commit_gate_plan.py:230-235` catches `SurfaceError` and returns `[]`,
  an empty fast-gate set — a silent pre-commit disarm. Binary-unavailability
  must therefore raise a type **not** derived from `SurfaceError`.
- `boundary_probe_lib.py:132` calls `match_surfaces` with no handler and
  deliberately propagates — a distinct type propagates correctly there.
- `path_matches_patterns` survives at `surfaces_lib.py:105,109` inside
  `_validate_surface`'s generated-markdown validation. That is manifest
  self-consistency checking, a different job from classifying real changed
  paths. Slice 2 cannot claim single-matcher ownership; record it.

## Step 4 — `repo_file_listing.py` decision

Investigation completed 2026-08-29; the answer is now evidence-backed:

- `CHARNESS_SUPPORT_DIR` has exactly one production read site,
  `scripts/repo_layout.py:17`, and one live operator-facing doc,
  `skills/shared/references/bootstrap-resolution.md:222-246` (cited by 18
  SKILL.md bootstrap sections). **No adapter, hook, CI step, skill script, or
  `run-quality.sh` path ever sets it.** Every non-doc reference is a test
  fixture.
- When set, `skills/support/` patterns are globbed directly against the external
  tree with **no git filter** (`repo_file_listing.py:123-128`) — untracked and
  ignored files included, and the tree may sit outside the repo entirely.
- 24 exported importers; by the consumer-validator catalog's own fields all 19
  catalogued ones are `consumer_facing: false, decision: exclude`. The other 6
  are uncatalogued (basenames lack `check_`/`validate_`) and belong to the
  `quality` and `release` public skills — those DO execute in consumer repos.

Choose: absorb the external-support splice into the native owner, keep Python
with the reason recorded, or deprecate the splice (one doc, zero real setters).

## Step 5 — #753 closeout

Targets are the JTBD artifact's "Deletion/conversion candidates" section:

- convert-pin (2): `test_narrative_adapter.py`,
  `test_quality_tool_recommendations.py`
- trim-partial (8): `test_critique_skill.py`,
  `test_issue_closeout_discipline.py`, `test_narrative_scenario_blocks.py`,
  `test_quality_bootstrap.py`, `test_quality_skill_docs.py`,
  `test_retro_memory.py`, `test_skill_docs_contracts.py`,
  `test_source_bound_records_guidance.py`

Each candidate carries per-file line ranges and evidence in the artifact. Cite
those ranges in the lane brief; do not paraphrase them.

## Accumulated follow-ups (small, each with a named owner)

- `follow-up: release-machinery-jtbd-audit` — `_publish_and_finalize`
  (`publish_release_execute.py:225`) is unreachable in production with three
  test-only callers. More broadly: 52 release skill scripts / 12,599 lines plus
  36 test files / 15,336 lines to bump a version, tag, push, create a release.
  Apply #753's JTBD method to it.
- `follow-up: seam-fake-real-argv-audit` — every repo fake standing in for an
  external binary (`gh`, `repograph`, `nose`).
- **`charness task run` receipts do not carry the lane's final message.** Two
  lanes in a row returned a ~27-line receipt with no verification narrative, so
  the parent had to reconstruct the required scenario table from the tests. Same
  family as #754 (the runner discarding the state the improvement loop needs);
  add it there.
- `publish_release_helpers.py` sits at **359/360** tokei code lines (hard cap,
  blocking at `run-quality.sh:1070`); `test_release_resume_edge_coverage.py` at
  798/800.
- `check-test-production-ratio` passes or blocks purely on whether `tokei` is on
  PATH (see step 1). Either make the engine requirement explicit or accept the
  splitlines number.
- `build_native_artifact.py:91-94` catches `OSError` but `runtime_root` raises
  `RuntimeEnvironmentError` (a `RuntimeError`) — pre-existing, and moot if the
  builder is deleted.
- `corrupt` is an imprecise status token for `state-write-skipped` and
  `activation-failed` (nothing is corrupt; a write failed). The true status is
  preserved in `reason` and the message is honest, so this was accepted rather
  than adding a `NativeStatus` member. Moot if the layer is retired.

## Working shape

Unchanged from the 2026-08-29 session and it worked: investigation via dynamic
workflow (sonnet); design critique via opus reviewers with an EXPLICIT model
override, delivered through the workflow channel (in-process bounded-reviewer
subagents went idle without delivering twice); implementation via
`charness task run` Codex lanes at xhigh. The parent owns design, adversarial
verification, integration, and final proof.

Two lane-brief rules this session added to `.agents/lane-brief-template.md`,
both earned: cite the owning source rather than paraphrasing a scan/skip set,
and seam fakes must reject malformed argv. Add the third from the sidecar RCA:
**a double's accepted shape must be derived from the real producer, never from
the consumer's expectation.**
