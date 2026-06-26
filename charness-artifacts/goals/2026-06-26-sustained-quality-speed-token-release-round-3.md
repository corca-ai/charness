# Achieve Goal: Sustained Quality Speed Token Release Round 3

Status: active
Created: 2026-06-26
Activation: `/goal @charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-3.md`
Timebox: 3h
Activation time: 2026-06-26T21:03:40+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Discuss before activation: resolved — the user explicitly requested a
three-hour quality run ending in push and release; release publication remains
the final boundary only, not a per-slice action.

## Active Operating Frame

- Current slice: active discovery for the next high-leverage quality slice.
- Current slice intent: find structural improvements that beat repeated tiny
  subprocess conversions: prioritize measured runtime, brittle bug risk, and
  token/verbosity surfaces with deterministic proof.
- Next action: run focused inventories, choose the first safe mutation slice,
  then verify with focused tests before any broad closeout.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Run a three-hour sustained quality improvement pass over charness, applying the prior-round lessons to prioritize higher-leverage structural fixes across bug risk, test speed, script runtime, token efficiency, and release readiness. Finish by pushing and publishing the next release only after final proof and critique.

## Non-Goals

- Do not publish or push before the final release boundary.
- Do not weaken local pre-push proof merely to make the run faster.
- Do not claim live/provider proof unless a real configured proof channel runs.
- Do not add new blocking floors for first-sighting waste; prefer advisory or
  existing preflight absorption unless recurrence is proven.
- Do not chase metric-only cleanup: each slice needs a behavioral or operator
  value claim.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Push and release are approved by the user's request, but only for the final
  bundle after final quality proof, release critique, and publish helper checks.
- Generated/export surfaces follow mutate -> sync -> verify -> publish.
- Cautilus remains eval-only and ask-before-run; no bare `cautilus evaluate`.
- Fresh-eye critique is required before release publication. If host tooling
  blocks it, record the concrete host signal instead of substituting same-agent
  review.

## User Acceptance

- Check the final pushed commit and release tag on GitHub.
- Re-run `./scripts/run-quality.sh --read-only` from a clean checkout.
- Inspect this goal artifact, the quality artifact, critique artifact, and
  release artifact for slice proof and non-claims.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task ... --summary`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- Focused inventories: runtime summary, skill ergonomics, standing test
  economics, boundary/duplicate/script/runtime inventories as triggered.
- Focused unit tests for each changed seam.
- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  for pre-lock bundle checks.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`
  with refresh only after mutation set is locked.
- `./scripts/run-quality.sh --read-only` through pre-push.
- Release planner and publish helper dry-run/execute path, including fresh
  checkout probes configured by the adapter.
- Distinct-channel release verification recorded in the release artifact.

### External Or Live Proof

- Git push and release publication are final-boundary proof only.
- Real-host release proof is run only when `check_real_host_proof.py` says the
  release slice triggers configured surfaces.
- No provider/live behavior proof is expected for this quality bundle unless a
  later slice deliberately touches such a surface.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Select high-leverage quality targets from current inventories | Avoid repeating low-yield subprocess micro-slices | runtime summary, ergonomics inventory, selected candidate ledger | active |
| 2 | Implement bug/runtime/token-efficiency slice(s) | Main value delivery before release | focused tests, ruff/length checks, slice log with duplicate pressure when tests change | pending |
| 3 | Bundle verification and critique | Prevent green-terminal trust before irreversible boundaries | fresh-eye critique, quality artifact, slice closeout verification lock | pending |
| 4 | Push and release | User explicitly requested final publication | pre-push full gate, release helper proof, public visibility/readback | pending |

## Operator Decision Queue

None currently — the user already approved final push/release for this goal;
new operator-only decisions discovered mid-run will be added here.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing: `find-skills` recommended `quality` and `release` for this task; no
external/trusted skill roots configured.
Gather: n/a — no external source URLs are part of the request.
Release: pending final release helper proof.
Issue closeout: n/a — no tracked GitHub issue is being resolved by this goal.

## Slice Log

### Slice 1: Prefilter repo-copy invariant scan

- Objective: Reduce standing gate runtime waste in check_test_repo_copy_invariants.py without weakening the copy-heavy release_only contract.
- Why this approach: Structural-waste inventory identified a broad parser-without-prefilter candidate, and the script measured around 1.14s before the change.
- Commits:
- What changed: Added COPY_HEAVY_TOKEN_RE text prefilter before AST parsing; added regression coverage for irrelevant invalid Python; expanded structural-waste prefilter detection to identifier segment names such as COPY_HEAVY_TOKEN_RE.
- Alternatives rejected: Did not weaken or remove the invariant; did not move it to CI because the gate is cheap and local proof remains valuable.
- Targeted verification: pytest: 22 passed for repo-copy invariants and structural-waste inventory; ruff passed; check_test_repo_copy_invariants.py runtime measured about 0.31s after the change; inventory_structural_waste.py now reports no broad_scanner_candidates.
- Test duplication pressure: Added two focused tests in existing quality gate files; no new test file; length headroom remains >590 lines for touched test files.
- Critique: Same-agent slice critique: behavior contract remains intact because regex checks still scan all files and AST release_only checks now run only when copy-heavy fixture/helper tokens are present; false-positive inventory detector was corrected with focused coverage.
- Off-goal findings: None.
- Lessons carried forward: Prefer a measured structural runtime fix plus inventory correction over another narrow subprocess conversion.
- Metrics: Runtime proxy: check_test_repo_copy_invariants.py 1.14s before, 0.31s after on this machine.

### Slice 2: Compact release-only sentinel inventory

- Objective: Reduce token overhead for advisory release-only sentinel review without removing full attribution when needed.
- Why this approach: The full --json output for inventory_release_only_sentinels.py was about 28KB and mostly per-test names; quality triage usually needs counts, samples, and findings first.
- Commits:
- What changed: Added --summary compact JSON output with counts, sample file lists, and bounded findings; preserved --json full per-test attribution; added focused CLI regression coverage.
- Alternatives rejected: Did not change the default text output or remove full JSON because detailed attribution remains useful for targeted cleanup.
- Targeted verification: pytest: 5 passed for test_release_only_sentinel_inventory.py; ruff passed; length headroom remains 178 lines for the script and 595 for the test file; full JSON 28142 bytes vs summary 4557 bytes, 83.8% reduction.
- Test duplication pressure: Added one focused test in an existing test file; no new test file.
- Critique: Same-agent slice critique: the summary is explicitly labeled triage output and points callers to --json for full attribution, so compact output cannot masquerade as complete evidence.
- Off-goal findings: The summary makes the existing advisory visible: 10 release_only files still lack obvious standing sentinels; that is not fixed in this slice.
- Lessons carried forward: Token efficiency improvements should preserve a full-detail escape hatch and label summaries as triage output.
- Metrics: Token/output proxy: release-only sentinel inventory output reduced 83.8% for summary use.

### Slice 3: Standing sentinel coverage for release-only update boundaries

- Objective: Reduce release-only blind spots by making two existing update/doctor boundaries visible to the standing-test sentinel inventory.
- Why this approach: Fresh-eye read-only review identified a low-risk rename and a small in-process predicate test that cover real release/update behavior without running the heavy managed-install flow.
- Commits:
- What changed: Renamed the missing-source doctor standing test so inventory recognizes its `without_source` sentinel role; added a fast `git_has_tracked_changes` standing test proving untracked runtime files remain allowed while tracked edits block managed checkout updates.
- Alternatives rejected: Did not duplicate the full release-only managed install path in standing tests; did not loosen release_only markers on expensive end-to-end tests.
- Targeted verification: pytest: 2 passed, 16 deselected for non-release-only tests in test_doctor_next_action.py and test_managed_install.py; ruff passed; length headroom remains 689 lines for test_doctor_next_action.py and 307 lines for test_managed_install.py; inventory_release_only_sentinels.py --summary now reports missing_standing_sentinel_file_count 8, down from 10.
- Test duplication pressure: Added one focused standing test in an existing CLI test file and renamed one existing test; no new test file.
- Critique: Same-agent slice critique: the new test asserts the exact predicate that ensure_checkout uses before managed pull, so it adds confidence without pretending to cover pull/reinstall side effects.
- Off-goal findings: Eight release_only files still lack obvious standing sentinels; remaining candidates need more design care than the two low-risk fixes here.
- Lessons carried forward: When release-only gates are intentionally expensive, standing coverage should target the smallest safety predicate rather than replay the expensive flow.
- Metrics: Coverage proxy: release-only sentinel missing file count reduced 20%, from 10 to 8.

### Slice 4: Compact dead-code advisory output

- Objective: Reduce token overhead for the quality skill's vulture-backed dead-code advisory without removing full attribution.
- Why this approach: `run_dead_code_advisory.py --json` emitted about 95KB in this repo, mostly a massive vulture command and full findings; triage usually needs counts, classification buckets, and a small candidate sample first.
- Commits:
- What changed: Added `--summary` output to the public quality script and checked-in plugin mirror; summary omits the full command and full findings, keeps counts/classification buckets/review-candidate samples, and points users to `--json` for complete attribution. Updated quality dogfood evidence for the public skill contract.
- Alternatives rejected: Did not make compact output the default text mode, and did not remove the full `--json` escape hatch because detailed dead-code review still needs complete attribution.
- Targeted verification: pytest: 8 passed for test_quality_dead_code_advisory.py; ruff passed; check_python_lengths headroom remains 163 lines for run_dead_code_advisory.py and 611 lines for test_quality_dead_code_advisory.py; validate_public_skill_dogfood.py passed; public script and plugin mirror compare equal.
- Test duplication pressure: Added one focused CLI contract test in the existing dead-code advisory test file; no new test file.
- Critique: Same-agent slice critique: compact output is explicitly labeled triage output and preserves full `--json`, so downstream callers cannot mistake the summary for full evidence.
- Off-goal findings: Dead-code advisory still reports many review candidates; this slice improves review efficiency rather than deciding each candidate.
- Lessons carried forward: Large advisory JSON should have a bounded first-read mode before humans or agents spend context on full attribution.
- Metrics: Token/output proxy: dead-code advisory output reduced from 95468 bytes to 5176 bytes with `--summary`, a 94.6% reduction.

### Slice 5: Compact lint-ignore inventory output

- Objective: Reduce token overhead for lint-suppression review while preserving the full detailed inventory.
- Why this approach: `inventory_lint_ignores.py --json` emitted about 90KB in this repo; the payload already had useful counts, but callers had to ingest full findings to get them.
- Commits:
- What changed: Added `--summary` output to the public quality script and checked-in plugin mirror; summary keeps counts, interpretation, adapter diagnostics, review prompts, and a bounded priority findings sample while omitting full findings. Updated quality dogfood evidence.
- Alternatives rejected: Did not change the plain text output or remove full `--json`; detailed suppression cleanup still needs snippets and per-finding data.
- Targeted verification: pytest: 6 passed for test_quality_lint_ignores.py; ruff passed; check_python_lengths headroom remains 289 lines for inventory_lint_ignores.py and 614 lines for test_quality_lint_ignores.py.
- Test duplication pressure: Added one focused summary contract test in the existing lint-ignore inventory test file; no new test file.
- Critique: Same-agent slice critique: the summary samples likely-priority suppressions first but remains explicitly triage-only, so it cannot silently hide the full debt list.
- Off-goal findings: The lint-ignore inventory still reports existing suppression debt; this slice makes first-pass review cheaper rather than deciding those findings.
- Lessons carried forward: Advisory inventories that already compute counts should expose them without forcing full finding ingestion.
- Metrics: Token/output proxy: lint-ignore inventory output reduced from 89662 bytes to 6140 bytes with `--summary`, a 93.2% reduction.

### Slice 6: Convert managed-install sync proof to in-process execution

- Objective: Remove a boundary-bypass advisory and reduce one release-only test's extra Python process hop without weakening install-surface proof.
- Why this approach: Slice closeout repeatedly flagged `test_managed_install.py -> scripts/sync_root_plugin_manifests.py` as an import-safe script subprocess from a changed test file; the script has a callable `main()` and the test only needs the mutation result.
- Commits:
- What changed: Added an in-process helper that loads `sync_root_plugin_manifests.py`, patches its argv/cwd, captures stdout, and returns the JSON payload; replaced the subprocess call in the embedded managed-checkout test.
- Alternatives rejected: Did not add a boundary-bypass exemption because the subprocess boundary was not needed for the assertion under test.
- Targeted verification: pytest: 1 passed for test_embedded_cli_bootstraps_managed_checkout_from_configured_repo_url; check_boundary_bypass_ratchet.py passed; ruff passed; check_python_lengths headroom remains 293 lines for test_managed_install.py; run_slice_closeout.py completed with no boundary-bypass advisory.
- Test duplication pressure: Added a local helper in the existing test file; no new test file and no duplicated release-only flow.
- Critique: Same-agent slice critique: the test still mutates a cloned upstream repo and commits the refreshed install surface, so the managed-checkout behavior remains covered while avoiding a redundant process boundary.
- Off-goal findings: Other baseline sync_root_plugin_manifests subprocess call sites remain, including test_update_propagation.py and packaging validation; they need separate fidelity review.
- Lessons carried forward: When closeout flags a changed test file for import-safe script subprocess, prefer an in-process helper unless the test asserts CLI exit/stderr semantics.
- Metrics: Quality proxy: boundary-bypass closeout advisory for test_managed_install.py eliminated.

### Slice 7: Reuse in-process sync proof for update propagation

- Objective: Remove another redundant sync_root_plugin_manifests subprocess boundary from release-only update propagation coverage.
- Why this approach: test_update_propagation.py used the same import-safe sync script boundary as slice 6 before committing a modified source repo; the new helper preserves the mutation and JSON assertion without spawning a second Python process.
- Commits:
- What changed: Reused `sync_root_plugin_manifests_inprocess` from test_managed_install.py and replaced the subprocess call in test_update_propagation.py.
- Alternatives rejected: Did not weaken the installed CLI update subprocess itself because that is the behavior boundary the test is meant to prove.
- Targeted verification: pytest: 1 passed for test_installed_cli_update_propagates_new_skill_into_exported_plugin_root; check_boundary_bypass_ratchet.py passed and candidate count dropped from 71 before slice 6 to 70 after this slice; ruff passed; check_python_lengths headroom remains 680 lines for test_update_propagation.py.
- Test duplication pressure: Reused an existing helper instead of duplicating loader/cwd/argv plumbing in a second test file.
- Critique: Same-agent slice critique: only the setup sync step moved in-process; the release/update propagation proof still invokes the installed CLI and validates the exported host-visible plugin root.
- Off-goal findings: Some sync_root_plugin_manifests subprocess uses remain in packaging validation where CLI semantics may be the intended boundary.
- Lessons carried forward: Shared in-process helpers are preferable when multiple release-only tests need the same setup mutation before proving a different external behavior.
- Metrics: Quality/runtime proxy: boundary-bypass inventory candidate count reduced by one additional import-safe script subprocess.

### Slice 8: Compact ubiquitous-language inventory output

- Objective: Reduce token overhead for terminology-contract review while preserving full per-file counts.
- Why this approach: `inventory_ubiquitous_language.py --json` emitted about 78KB in this repo because each term carries full per-file count rows; first-pass review needs status, totals, and a small sample.
- Commits:
- What changed: Added `--summary` output to the public quality script and checked-in plugin mirror; summary keeps status, term totals, finding count, and bounded deprecated/alias-only samples while omitting full `files_with_terms`. Updated quality dogfood evidence.
- Alternatives rejected: Did not alter failure exit semantics for deprecated terminology and did not remove full `--json`, because detailed cleanup still needs per-file count rows.
- Targeted verification: pytest: 6 passed for test_quality_ubiquitous_language.py; ruff passed; check_python_lengths headroom remains 129 lines for inventory_ubiquitous_language.py and 612 lines for test_quality_ubiquitous_language.py; public script and plugin mirror compare equal.
- Test duplication pressure: Added one focused summary contract test in the existing ubiquitous-language test file.
- Critique: Same-agent slice critique: summary preserves failing status and findings samples, so it reduces context load without hiding terminology regressions.
- Off-goal findings: The current repo terminology contract remains ok; this slice improves review ergonomics for future failures.
- Lessons carried forward: Inventories that fail on low-noise findings should keep summary exit codes identical to full JSON.
- Metrics: Token/output proxy: ubiquitous-language inventory output reduced from 77814 bytes to 3325 bytes with `--summary`, a 95.7% reduction.

### Slice 9: Compact entrypoint-docs ergonomics output

- Objective: Reduce token overhead for entrypoint documentation ergonomics review while preserving full document attribution.
- Why this approach: `inventory_entrypoint_docs_ergonomics.py --json` emitted about 43KB in this repo, partly because every document row repeated the same review prompts.
- Commits:
- What changed: Added `--summary` output to the public quality script and checked-in plugin mirror; summary reports document counts, heuristic counts, bounded heuristic-document samples, and a single review prompt list while omitting full inbound link lists and per-row prompt repetition. Updated quality dogfood evidence.
- Alternatives rejected: Did not remove full `--json` because detailed docs cleanup still needs per-document attribution and inbound link lists.
- Targeted verification: pytest: 4 passed for test_quality_entrypoint_docs_ergonomics.py; ruff passed; check_python_lengths headroom remains 137 lines for inventory_entrypoint_docs_ergonomics.py and 660 lines for test_quality_entrypoint_docs_ergonomics.py; public script and plugin mirror compare equal.
- Test duplication pressure: Added one focused summary contract test in the existing entrypoint-docs ergonomics test file.
- Critique: Same-agent slice critique: summary focuses on documents with heuristics and keeps prompt context once, so it is useful for triage without hiding full document rows from `--json`.
- Off-goal findings: Current entrypoint-doc heuristic findings remain advisory; this slice reduces first-read cost rather than deciding each documentation concern.
- Lessons carried forward: Repeated prompt metadata belongs once in a compact summary, not duplicated across every row.
- Metrics: Token/output proxy: entrypoint-docs ergonomics output reduced from 43255 bytes to 9786 bytes with `--summary`, a 77.4% reduction.

### Slice 10: Route quality inventory review summary-first

- Objective: Make the compact inventory modes reachable through the public quality workflow instead of leaving them as hidden CLI flags.
- Why this approach: Adding `--summary` flags saves little if the dispatch reference still teaches first-pass users to run full payloads.
- Commits:
- What changed: Updated `references/inventory-dispatch.md` in the public quality skill and checked-in plugin mirror to use `--summary` for compact-supported inventories and to state that summaries are triage, not complete evidence.
- Alternatives rejected: Did not replace full `--json` guidance everywhere; detailed disposition still needs full attribution when a summary sample earns follow-up.
- Targeted verification: pytest: 22 passed for test_quality_skill_docs.py; validate_skills.py passed; check_doc_links.py passed; public reference and plugin mirror compare equal.
- Test duplication pressure: No new tests; existing skill-doc coverage verifies the reference remains reachable.
- Critique: Same-agent slice critique: summary-first routing changes review ergonomics, not evidence semantics, because the reference explicitly requires `--json` for full attribution/disposition.
- Off-goal findings: None.
- Lessons carried forward: A token-efficiency feature should update the operator path that causes token spend, not only the script flag.
- Metrics: Adoption proxy: seven inventory dispatch bullets now point at `--summary` for first-read review.

### Slice 11: Run entrypoint-docs inventory tests in-process

- Objective: Reduce focused test startup cost for the entrypoint-docs ergonomics inventory after adding its summary mode.
- Why this approach: The tests were spawning the inventory script for every assertion even though the entrypoint is import-safe and already follows the in-process pattern used by neighboring quality inventory tests.
- Commits:
- What changed: Loaded `inventory_entrypoint_docs_ergonomics.py` once with `import_repo_module`, added an in-process runner that patches argv and captures stdout/stderr, and converted four tests away from `run_script` subprocess calls.
- Alternatives rejected: Did not change the inventory implementation or assertions; the tests still exercise the public `main()` path.
- Targeted verification: pytest: 4 passed for test_quality_entrypoint_docs_ergonomics.py; ruff passed; run_slice_closeout.py passed; boundary-bypass inventory summary reports candidate_count 76 after this conversion.
- Test duplication pressure: Reused the established in-process entrypoint pattern from adjacent tests; no new test file.
- Critique: Same-agent slice critique: in-process execution still drives argparse/main output, so it improves startup cost without bypassing the CLI entrypoint contract these tests assert.
- Off-goal findings: Boundary-bypass inventory still has many candidates; larger conversion should be planned by cluster to avoid low-value churn.
- Lessons carried forward: After adding a new CLI mode, make its test proof cheap enough to stay in the standing loop.
- Metrics: Runtime proxy: focused entrypoint-docs ergonomics test file observed at 0.61s before conversion and 0.38s after conversion in this session.

### Slice 12: Run dead-code advisory CLI tests in-process

- Objective: Reduce focused test startup cost for the dead-code advisory after adding its summary mode.
- Why this approach: Two tests spawned a fresh Python process only to exercise the script main with a fake `vulture` on PATH; the same contract can be tested by calling `main()` with patched argv/PATH and captured stdout.
- Commits:
- What changed: Added an in-process helper for run_dead_code_advisory.py and converted the full JSON and summary CLI contract tests away from subprocess.run.
- Alternatives rejected: Did not bypass the fake vulture subprocess itself because the advisory's behavior depends on invoking the external detector.
- Targeted verification: pytest: 8 passed for test_quality_dead_code_advisory.py; ruff passed; check_python_lengths headroom remains 614 lines; run_slice_closeout.py passed.
- Test duplication pressure: Added one local helper and kept existing assertions; no new test file.
- Critique: Same-agent slice critique: the tests still exercise argparse/main JSON output and fake-vulture invocation, so the only removed boundary is the redundant Python wrapper process.
- Off-goal findings: Broader boundary-bypass conversion remains available but should be batched by repeated helper patterns.
- Lessons carried forward: When a test needs a fake external binary, keep that external boundary and remove only the redundant script process.
- Metrics: Runtime proxy: focused dead-code advisory test file observed at 0.64s before conversion and 0.53s after conversion in this session.

### Slice 13: Exclude artifacts from coverage and seeded repo copies

- Objective: Reduce avoidable fixture-copy work in coverage and seeded test repos by excluding repo-owned artifacts that scenarios do not consume.
- Why this approach: `charness-artifacts` is about 16MB locally, while check_coverage.py and tests/repo_copy.py already exclude volatile roots such as `.charness`, caches, reports, and node_modules.
- Commits:
- What changed: Added `charness-artifacts` to check_coverage.py COPY_IGNORE_NAMES, plugin mirror, tests/repo_copy.py REPO_COPY_EXCLUDE_NAMES, and the repo-copy invariant required exclude set.
- Alternatives rejected: Did not narrow coverage's source copy beyond existing ignore roots because scenario behavior still expects a realistic source checkout.
- Targeted verification: pytest: 12 passed for test_repo_copy_invariants.py; check_test_repo_copy_invariants.py passed; check_coverage.py JSON output stayed byte-equivalent as structured data to the before snapshot (coverage 0.9212, 1075/1167); ruff passed; check_python_lengths passed; run_slice_closeout.py passed.
- Test duplication pressure: Updated the existing invariant set instead of adding another copy-specific test.
- Critique: Same-agent slice critique: excluding artifacts is safe because coverage scenarios and seeded repo copies exercise source/control-plane behavior, not historical goal/quality artifacts.
- Off-goal findings: Single-run coverage wall time is noisy; observed samples ranged from 4.64s to 4.84s after the change, so the durable claim is reduced copied payload rather than a precise wall-clock win.
- Lessons carried forward: Fixture copy helpers should exclude durable artifacts unless a test explicitly opts into artifact behavior.
- Metrics: Copy-size proxy: avoid copying the local 16MB `charness-artifacts` tree in coverage and seeded repo copies.

### Slice 14: Compact public-spec quality inventory output

- Objective: Reduce token overhead for public-spec quality review while preserving full spec attribution.
- Why this approach: `inventory_public_spec_quality.py --json` emitted about 10KB; small compared with earlier inventories, but the wrapper was simple and public-spec first-read review now follows the summary-first policy.
- Commits:
- What changed: Added `--summary` output to the public quality script and checked-in plugin mirror; summary keeps rollup counts, layering recommendations/prompts, and bounded flagged-spec samples. Updated inventory dispatch to use summary-first for public-spec review and refreshed quality dogfood evidence.
- Alternatives rejected: Did not remove full public_specs rows from `--json`; detailed spec cleanup still needs command examples, proof blocks, and per-spec attribution.
- Targeted verification: pytest: 36 passed for test_quality_public_spec_quality.py and test_quality_skill_docs.py; ruff passed; check_python_lengths headroom remains 302 lines for inventory_public_spec_quality.py and 199 lines for test_quality_public_spec_quality.py; script and reference mirrors compare equal.
- Test duplication pressure: Added one focused summary contract test in the existing public-spec quality test file.
- Critique: Same-agent slice critique: summary keeps layering recommendations and flagged-spec heuristics, so first-pass review remains actionable while full rows stay available for disposition.
- Off-goal findings: None.
- Lessons carried forward: Once summary-first routing exists, smaller inventories should still participate when the wrapper cost is low.
- Metrics: Token/output proxy: public-spec quality inventory output reduced from 10220 bytes to 2389 bytes with `--summary`, a 76.6% reduction.

### Slice 15: Standing sentinel for Codex cache selection

- Objective: Reduce release-only blind spots around Codex cache primary selection without adding another expensive installed-host flow.
- Why this approach: test_doctor_cache_selection.py had a release-only E2E proof but no standing sentinel; the core selection behavior is a pure function.
- Commits:
- What changed: Narrowed the release_only marker from module-level to the existing E2E test and added a standing unit test for `codex_primary_cache_entry` selecting the enabled cache whose manifest version matches the source version.
- Alternatives rejected: Did not duplicate the full doctor/cache fixture setup in standing tests; retained the release-only E2E coverage for host-visible payload behavior.
- Targeted verification: pytest: standing test passed in 0.31s; release-only test passed in 5.98s; ruff passed; check_python_lengths headroom remains 735 lines; run_slice_closeout.py passed; inventory_release_only_sentinels.py --summary reports missing_standing_sentinel_file_count 7, down from 8 after slice 3.
- Test duplication pressure: Added one focused unit test inside the existing cache-selection test file.
- Critique: Same-agent slice critique: the standing test proves the algorithmic selection rule but does not claim to cover config parsing or doctor payload assembly; the release-only test still owns that broader boundary.
- Off-goal findings: Seven release-only files still lack obvious standing sentinels.
- Lessons carried forward: Convert module-level release_only markers to function-level when the same file can host a cheap standing predicate.
- Metrics: Coverage proxy: release-only sentinel missing file count reduced from 8 to 7.

### Slice 16: Standing sentinel for Codex cache staleness no-op

- Objective: Reduce release-only blind spots around Codex cache refresh/session-staleness behavior without adding another full update flow to standing tests.
- Why this approach: test_codex_cache_refresh.py had module-level release_only tests, but `session_staleness_payload` has a cheap no-diff branch that can be exercised as a standing predicate.
- Commits:
- What changed: Narrowed release_only markers to the four copy-heavy update tests and added a standing unit test proving `session_staleness_payload` returns None when there are no rotated or removed cache entries.
- Alternatives rejected: Did not move the existing update/refresh tests into standing because they clone managed homes and exercise fake Codex integration.
- Targeted verification: pytest: standing test passed in 0.34s; full file including release_only tests passed (5 passed) in 24.20s; check_test_repo_copy_invariants.py passed; ruff passed; check_python_lengths headroom remains 688 lines; run_slice_closeout.py passed.
- Test duplication pressure: Added one focused unit test in the existing cache refresh test file.
- Critique: Same-agent slice critique: the standing test only covers the no-op staleness predicate; the release-only tests still own cache rotation and update payload behavior.
- Off-goal findings: A failed attempt to unmark test_managed_home_clone.py correctly hit the copy-heavy invariant; that marker was restored and not committed.
- Lessons carried forward: Copy-heavy invariant is the right guardrail; use function-level markers plus cheap predicates instead of demoting copy-heavy tests.
- Metrics: Coverage proxy: release-only sentinel missing file count currently 6 after this slice.

### Slice 17: Standing sentinels for tool lifecycle helpers

- Objective: Reduce release-only blind spots in tool lifecycle coverage and remove one avoidable subprocess boundary from that test file.
- Why this approach: `test_tool_lifecycle.py` had module-level `release_only`, but two update-advisory helpers and the repair next-step predicate are pure/cheap enough for standing pytest. The file also contained a best-effort cleanup helper that spawned `python3 scripts/agent_browser_runtime_guard.py`; loading the guard in-process keeps the same behavior without a nested Python process.
- Commits:
- What changed: Replaced the module-level marker with function-level `release_only` markers on copy-heavy CLI tests, renamed two pure tests so the standing sentinel inventory recognizes their guard role, and changed `cleanup_agent_browser_orphans()` to call `agent_browser_runtime_guard.main()` in-process with captured output.
- Alternatives rejected: Did not demote managed-home or repo-copy lifecycle tests; the copy-heavy invariant still owns that boundary. Did not assert cleanup return codes because the previous subprocess helper was explicitly best-effort.
- Targeted verification: pytest: standing subset `3 passed, 13 deselected` in 0.42s; release-only subset `13 passed, 3 deselected` in 33.81s; `check_test_repo_copy_invariants.py` passed; `check_boundary_bypass_ratchet.py` passed with 68 candidates, 31 clean-convertible, 31 internally-spawning, 23 likely keep-boundary; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new assertions; moved three existing cheap predicates into standing coverage.
- Critique: Same-agent slice critique: this improves standing coverage and removes an internal subprocess, but it does not claim tool lifecycle E2E flows are cheap; those remain release-only because they copy repos/managed homes.
- Off-goal findings: Release-only sentinel inventory still reports 5 files without obvious standing sentinels.
- Lessons carried forward: Module-level `release_only` can hide already-fast tests; split markers only when the repo-copy invariant agrees.
- Metrics: Coverage proxy: missing standing-sentinel file count reduced from 6 to 5; boundary-bypass candidate count reduced from 76 after earlier conversions to 68.

### Slice 18: Standing sentinel for release-state degradation

- Objective: Reduce another release-only blind spot without adding duplicate release probe setup.
- Why this approach: `test_managed_install_release_checks.py` had module-level `release_only`, but the unwritable state-cache degradation check uses only a temp home and the repo CLI; it is cheap enough to stay in standing pytest while the managed-home release probe cases remain release-only.
- Commits:
- What changed: Split the module-level marker into function-level `release_only` decorators for the managed-home release-check tests and renamed the unwritable-state test so the release-only sentinel inventory recognizes it as a standing guard.
- Alternatives rejected: Did not demote release probe tests that clone seeded managed homes; those still prove installed CLI/version state behavior across the release fixture boundary.
- Targeted verification: pytest: standing subset `1 passed, 5 deselected` in 0.44s; release-only subset `5 passed, 1 deselected` in 7.76s; `check_test_repo_copy_invariants.py` passed; `check_boundary_bypass_ratchet.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new assertions; moved one existing cheap degradation test into standing coverage.
- Critique: Same-agent slice critique: the standing test covers degradation when the state path is unwritable, not remote release probing; release-probe behavior remains in release-only tests.
- Off-goal findings: Release-only sentinel inventory still reports 4 files without obvious standing sentinels.
- Lessons carried forward: A standing sentinel can be an existing cheap error-path test when its name makes the guarded failure mode obvious.
- Metrics: Coverage proxy: missing standing-sentinel file count reduced from 5 to 4; release-only test count reduced from 75 to 74 and standing count increased from 116 to 117.

### Slice 19: Standing sentinel for Codex cache drift guidance

- Objective: Reduce Codex managed-install release-only blind spots without duplicating official app-server or managed-home setup.
- Why this approach: The E2E doctor test proves host-visible payloads, but the core stale-cache guidance is produced by a pure function. A standing unit keeps the `needs-refresh`/manual-action contract covered on every standing run.
- Commits:
- What changed: Added a standing unit test in `test_codex_managed_install.py` for `build_codex_host_guidance` when an enabled `charness@local` cache manifest version differs from the source manifest version.
- Alternatives rejected: Did not demote the official app-server install or managed-home doctor drift tests; they still cross host/cache boundaries and remain release-only.
- Targeted verification: pytest: standing subset `1 passed, 2 deselected` in 0.31s; release-only subset `2 passed, 1 deselected` in 11.12s; `check_test_repo_copy_invariants.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: Added one focused unit test that covers the small pure branch the E2E asserts through the full doctor payload.
- Critique: Same-agent slice critique: this is a contract sentinel for guidance text/status, not a replacement for app-server install proof.
- Off-goal findings: Release-only sentinel inventory still reports 3 files without obvious standing sentinels.
- Lessons carried forward: When a release-only E2E asserts a pure helper's branch, add a direct standing sentinel instead of trying to shrink the E2E.
- Metrics: Coverage proxy: missing standing-sentinel file count reduced from 4 to 3; standing test count increased from 117 to 118.

### Slice 20: Compact boundary-bypass inventory output

- Objective: Reduce token overhead for boundary-bypass quality review while preserving full candidate attribution on demand.
- Why this approach: `scripts/inventory_boundary_bypass.py --json` emitted every candidate row; most review loops first need counts plus a few samples. Adding `--summary` matches the summary-first pattern already applied to other quality inventories.
- Commits:
- What changed: Added `summarize_payload()` to the boundary-bypass inventory lib, wired `--summary` into the root and plugin-mirror CLIs, and added an in-process CLI test proving summary output omits full `candidates` while retaining counts and clean-convertible samples.
- Alternatives rejected: Did not change default text output or the full `--json` payload; ratchets and detailed cleanups still need exact candidate attribution.
- Targeted verification: pytest: `tests/test_boundary_bypass_inventory.py` and `tests/test_boundary_bypass_ratchet.py` `13 passed` in 0.37s; root/plugin mirror scripts and libs compare equal; `python3 -m json.tool` accepted summary output; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: Added one CLI summary contract test using in-process `main()` rather than spawning a subprocess.
- Critique: Same-agent slice critique: summary samples are triage-only and can hide unsampled candidates, so the output explicitly points reviewers to `--json` for full attribution.
- Off-goal findings: None.
- Lessons carried forward: Inventory scripts with full row payloads should offer compact machine-readable summaries, not just human text.
- Metrics: Token/output proxy: boundary-bypass full JSON was 35165 bytes and summary JSON was 6443 bytes, an 81.7% reduction.

### Slice 21: Standing sentinel for update human summary

- Objective: Reduce release-only blind spots around `charness update all` human output without duplicating the full installed CLI flow.
- Why this approach: The existing E2E still proves progress lines and installed-tool integration, but the `VERSION: None` and tool-summary formatting contract is produced by `print_update_human_summary()` and can be checked in-process.
- Commits:
- What changed: Split `test_update_output.py` from module-level release-only to function-level release-only on the full installed update flow, then added a standing unit for `print_update_human_summary()` covering omitted `None` versions, scope, and sorted tool status output.
- Alternatives rejected: Did not demote the full `update all` test; it clones a repo, installs a managed home, and exercises fake external tools.
- Targeted verification: pytest: standing subset `1 passed, 1 deselected` in 0.28s; release-only subset `1 passed, 1 deselected` in 12.27s; `check_test_repo_copy_invariants.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: Added one focused unit test that preserves the E2E's user-visible summary invariant without its fixture cost.
- Critique: Same-agent slice critique: this sentinel proves formatting only; it does not prove external tool update behavior or progress sequencing, which remain in the release-only E2E.
- Off-goal findings: Release-only sentinel inventory still reports 2 files without obvious standing sentinels.
- Lessons carried forward: Human output regressions often have a pure formatter underneath; cover that in standing tests and leave one E2E for wiring.
- Metrics: Coverage proxy: missing standing-sentinel file count reduced from 3 to 2; standing test count increased from 118 to 119.

### Slice 22: Compact standing-gate verbosity inventory output

- Objective: Reduce token overhead and operator error for standing-gate verbosity review.
- Why this approach: The script already produced useful full JSON, but lacked the `--summary` mode now standard across quality inventories. The full payload includes surfaces/snippets; first-pass review usually needs only axis statuses and a bounded finding sample.
- Commits:
- What changed: Added `summarize_payload()` to standing-gate verbosity lib, wired `--summary` into root and plugin-mirror CLIs, updated quality inventory dispatch to use summary-first, and added an in-process CLI summary test.
- Alternatives rejected: Did not remove default text output or full `--json`; detailed verbosity review still needs full surface/snippet attribution.
- Targeted verification: pytest: `tests/quality_gates/test_quality_standing_gate_verbosity.py` and `test_quality_skill_docs.py` `30 passed` in 0.39s; root/plugin mirror scripts/libs/docs compare equal; summary JSON validates with `python3 -m json.tool`; ruff passed; skill-surface preflight passed; public-skill dogfood suggestion inspected; `plan_cautilus_proof.py` reported `next_action: none`; `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review` passed.
- Test duplication pressure: Added one focused CLI summary contract test without subprocess.
- Critique: Same-agent slice critique: summary is only triage; it intentionally omits full snippets and tells the reviewer to use `--json` for attribution.
- Off-goal findings: `measure_startup_probes.py` has no `--summary`, but its full JSON is currently only 660 bytes, so adding summary there is low leverage.
- Lessons carried forward: Summary-first inventory dispatch should be mechanically consistent so agents do not waste attempts on unsupported flags.
- Metrics: Token/output proxy: standing-gate verbosity full JSON was 7870 bytes and summary JSON was 2993 bytes, a 62.0% reduction.
- Public-skill/Cautilus disposition: `quality` dogfood suggestion was reviewed; the existing `docs/public-skill-dogfood.json` contract remains the maintained consumer contract for this summary-first dispatch change. Cautilus live proof was skipped because planner `next_action` was `none` and deterministic validation owned closeout.

### Slice 23: Run metric-window CLI tests in process

- Objective: Reduce avoidable subprocess cost and boundary-bypass noise in metric-window tests.
- Why this approach: `test_record_metric_window.py` already had an in-process helper for the same script, but three CLI/error-path tests still used `run_script`. Catching argparse `SystemExit` in the helper preserves error-path assertions without spawning Python.
- Commits:
- What changed: Removed `run_script` usage from metric-window tests, made the in-process helper capture `SystemExit`, and routed update / mutually-exclusive / missing-session-source tests through that helper.
- Alternatives rejected: Did not change the script implementation; the behavior surface was already import-safe and covered.
- Targeted verification: pytest: `tests/quality_gates/test_record_metric_window.py` `13 passed` in 0.39s; `inventory_boundary_bypass.py` dropped from 75 to 74 candidates and from 36 to 35 clean-convertible; `check_boundary_bypass_ratchet.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted existing subprocess tests to the already-present in-process helper.
- Critique: Same-agent slice critique: this keeps CLI argparse behavior covered but no longer proves process startup for this script; that is acceptable because the repo keeps broader script startup/mirror gates elsewhere.
- Off-goal findings: Boundary-bypass inventory still reports 74 advisory candidates.
- Lessons carried forward: Before adding a new helper, check whether the test file already has an in-process runner that only needs `SystemExit` support.
- Metrics: Speed/testability proxy: removed three nested Python script invocations from the focused metric-window test file and reduced ratchet clean-convertible count by one.

### Slice 24: Run retro host-log probe tests in process

- Objective: Reduce nested process cost and boundary-bypass noise in retro host-log probe tests.
- Why this approach: `test_retro_host_log_probe.py` already loaded `probe_host_logs.py` and used an in-process helper for most cases; three tests still spawned the same script through `run_script`.
- Commits:
- What changed: Removed `run_script` from the retro host-log probe test file and routed host availability, goal-window, and named-Claude-session tests through the in-process helper.
- Alternatives rejected: Did not alter `probe_host_logs.py`; the behavior already had an import-safe `main()` and the test file had sufficient fixture coverage.
- Targeted verification: pytest: `tests/quality_gates/test_retro_host_log_probe.py` `17 passed` in 0.40s; `inventory_boundary_bypass.py` dropped from 74 to 73 candidates and from 35 to 34 clean-convertible; `check_boundary_bypass_ratchet.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted existing subprocess invocations to the existing helper.
- Critique: Same-agent slice critique: this no longer proves process startup for the retro probe, but the tests were behavior-heavy and the repo has separate script/package validation for startup and import safety.
- Off-goal findings: Boundary-bypass inventory still reports 73 advisory candidates.
- Lessons carried forward: Mixed in-process/subprocess files usually have leftover conversions; search within the same file before scanning globally.
- Metrics: Speed/testability proxy: removed three nested Python script invocations from retro host-log probe tests and reduced ratchet clean-convertible count by one.

### Slice 25: Run gather advice CLI smokes in process

- Objective: Reduce nested process cost in gather advice tests while keeping CLI JSON smoke coverage.
- Why this approach: `test_gather_google_workspace.py` already imports both gather advice scripts and validates their payload helpers directly. The two remaining subprocess calls only exercised `main()` JSON emission.
- Commits:
- What changed: Replaced subprocess-based Google Workspace and Slack advice CLI tests with an in-process `run_script_main()` helper that patches `sys.argv` and captures stdout/stderr.
- Alternatives rejected: Did not remove CLI smoke assertions; they still prove `main()` emits JSON.
- Targeted verification: pytest: `tests/test_gather_google_workspace.py` `11 passed` in 0.36s; `inventory_boundary_bypass.py` dropped from 73 to 72 candidates and from 34 to 33 clean-convertible; `check_boundary_bypass_ratchet.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted two existing subprocess tests.
- Critique: Same-agent slice critique: in-process CLI smoke no longer proves interpreter startup for the gather advice scripts, but helper payload and script package validation already cover importability.
- Off-goal findings: Boundary-bypass ratchet summary stayed at 66 candidates because baseline/exemption filtering differs from raw inventory.
- Lessons carried forward: CLI JSON smokes can often call `main()` directly when startup is not the behavior under test.
- Metrics: Speed/testability proxy: removed two nested Python script invocations and reduced raw clean-convertible count by one.

### Slice 26: Run markdown preview CLI smokes in process

- Objective: Reduce nested process cost in markdown preview support tests while preserving CLI behavior assertions.
- Why this approach: The file already had an in-process `render_markdown_preview.py` runner for most cases; the remaining success/config/error tests could use it once it restored `SystemExit` messages to stderr.
- Commits:
- What changed: Removed the subprocess render helper, converted the success/config/unsupported-backend tests to the in-process helper, and taught that helper to capture `SystemExit` return codes and messages.
- Alternatives rejected: Kept subprocess use for local git repository setup in the changed-only test because that is fixture preparation, not a script-under-test boundary.
- Targeted verification: pytest: `tests/test_markdown_preview_support.py` `11 passed` in 1.49s; raw `inventory_boundary_bypass.py` after conversion reports 71 candidates and 32 clean-convertible; `check_boundary_bypass_ratchet.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted existing CLI smokes.
- Critique: Same-agent slice critique: in-process calls still prove parser/main behavior and stderr message content, but not separate interpreter startup; repo-level script validation covers startup/importability.
- Off-goal findings: Fixture setup still uses git subprocesses intentionally.
- Lessons carried forward: When replacing process-boundary error tests, preserve non-integer `SystemExit` messages on stderr or the test loses the user-visible contract.
- Metrics: Speed/testability proxy: removed render script subprocess helper usage from the markdown preview support suite and reduced raw clean-convertible count by one.

### Slice 27: Run public-skill dogfood CLI smoke in process

- Objective: Reduce one more nested process from public-skill dogfood tests.
- Why this approach: The file already exercises the dogfood library directly; the remaining subprocess was only a JSON-emission smoke for `suggest_public_skill_dogfood.py`.
- Commits:
- What changed: Imported `suggest_public_skill_dogfood.py` through `runtime_bootstrap`, added a small in-process runner, and converted the CLI JSON smoke to call `main()` directly.
- Alternatives rejected: Did not remove the CLI smoke; it still proves the script's `main()` and `--json` output shape.
- Targeted verification: pytest: `tests/test_public_skill_dogfood.py` `5 passed` in 0.42s; raw `inventory_boundary_bypass.py` dropped from 71 to 70 candidates and from 32 to 31 clean-convertible; `check_boundary_bypass_ratchet.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted the existing smoke.
- Critique: Same-agent slice critique: this keeps parser/main/output coverage but not separate interpreter startup; package validation and other CLI startup checks cover that class.
- Off-goal findings: Boundary-bypass ratchet filtered count stayed unchanged while raw inventory improved.
- Lessons carried forward: Public-skill support scripts should be tested through direct `main()` calls unless startup itself is the asserted behavior.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced raw clean-convertible count by one.

### Slice 28: Run public-skill validation CLI smokes in process

- Objective: Reduce nested process cost in public-skill validation tests while preserving CLI guidance behavior.
- Why this approach: The tests already imported validation/suggestion modules directly; two CLI smokes still spawned Python. The validation script handles `ValidationError` in its `__main__` guard, so the in-process helper reproduces that stderr guidance explicitly.
- Commits:
- What changed: Added an in-process module `main()` runner, converted validation and suggestion CLI smokes, and preserved the `suggest_public_skill_validation.py` guidance stderr contract.
- Alternatives rejected: Did not bypass `main()` with lower-level helper calls for these two tests, because the CLI guidance/output shape is the behavior under test.
- Targeted verification: pytest: `tests/test_public_skill_validation.py` `8 passed` in 0.33s; raw `inventory_boundary_bypass.py` dropped from 70 to 69 candidates and from 31 to 30 clean-convertible; `check_boundary_bypass_ratchet.py` passed; ruff passed; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted existing CLI smokes.
- Critique: Same-agent slice critique: reproducing the `__main__` guard in the helper is slightly coupled to the script, but it keeps the user-facing guidance contract without a process boundary.
- Off-goal findings: None.
- Lessons carried forward: For scripts whose exception handling lives under `if __name__ == "__main__"`, in-process tests must either call that wrapper or reproduce the wrapper contract deliberately.
- Metrics: Speed/testability proxy: removed two nested Python script invocations and reduced raw clean-convertible count by one.

### Slice 29: Run setup acceptance synth smoke in process

- Objective: Remove another nested Python script invocation from script behavior tests without weakening the setup acceptance JSON contract.
- Why this approach: The test already validates `synthesize_operator_acceptance()` directly, and the remaining subprocess only checked `synthesize_operator_acceptance.py --json`; calling the loaded script module's `main()` preserves the parser/output assertion.
- Commits:
- What changed: Loaded `skills/public/setup/scripts/synthesize_operator_acceptance.py` through the test script loader, converted the CLI JSON smoke to an in-process `main()` call, and removed the last `run_script` dependency from `test_script_inprocess_behaviors.py`.
- Alternatives rejected: Did not remove the CLI smoke entirely because the JSON output shape and argument parsing remain user-facing behavior.
- Targeted verification: pytest: `tests/quality_gates/test_script_inprocess_behaviors.py` `5 passed` in 0.51s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 68 candidates and 29 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 65 candidates and 28 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted one existing smoke.
- Critique: Same-agent slice critique: this no longer proves a separate interpreter start for that script, but script validation and direct module loading cover importability while this test keeps `main()` and JSON behavior covered.
- Off-goal findings: None.
- Lessons carried forward: If a script has no special subprocess-only side effect, prefer a loaded-module `main()` call so CLI smoke coverage does not pay process startup cost.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced raw clean-convertible boundary inventory by one.

### Slice 30: Run narrative adapter smoke in process

- Objective: Remove the process boundary from a pure narrative adapter JSON smoke.
- Why this approach: The test only needs `resolve_adapter.py --repo-root <repo>` output for the current repo; direct `main()` execution matches the existing in-process adapter runner pattern used by neighboring narrative tests.
- Commits:
- What changed: Imported `skills/public/narrative/scripts/resolve_adapter.py` via `runtime_bootstrap.import_repo_module`, added a tiny runner that sets `sys.argv`, and replaced `run_script()` in `test_narrative_adapter.py`.
- Alternatives rejected: Did not broaden the test to temp-repo fallback behavior because that coverage already exists in `test_bootstrap_visibility.py`; this slice stays scoped to speed/testability.
- Targeted verification: pytest: `tests/quality_gates/test_narrative_adapter.py` `1 passed` in 0.34s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 67 candidates and 28 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 64 candidates and 27 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted one existing smoke.
- Critique: Same-agent slice critique: this test no longer proves a separate Python interpreter can start the adapter, but the behavior under test is adapter resolution JSON and remains covered through `main()`.
- Off-goal findings: None.
- Lessons carried forward: For adapter resolver smokes, prefer a reusable in-process runner and reserve subprocesses for packaging/export/startup assertions.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced both raw and ratcheted clean-convertible boundary counts by one.

### Slice 31: Run narrative bootstrap fallback smoke in process

- Objective: Remove the remaining narrative `resolve_adapter.py` subprocess from bootstrap visibility tests.
- Why this approach: `test_bootstrap_visibility.py` already has a generic in-process resolver runner for find-skills and announcement; adding narrative to that table keeps the file internally consistent.
- Commits:
- What changed: Loaded the narrative resolver module, routed the fallback-rich-docs test through `run_resolve_adapter()`, and removed the now-unused `run_script` import.
- Alternatives rejected: Did not consolidate with `test_narrative_adapter.py` because the two tests cover different fixtures and assertions; only the runner pattern is shared.
- Targeted verification: pytest: `tests/quality_gates/test_bootstrap_visibility.py` `3 passed` in 0.32s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 66 candidates and 27 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 63 candidates and 26 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted one existing smoke.
- Critique: Same-agent slice critique: as with the previous narrative resolver slice, this trades process startup proof for faster `main()` behavior proof; startup remains covered by script-surface validators.
- Off-goal findings: None.
- Lessons carried forward: When a test file already has an in-process CLI runner, extend that runner rather than adding another file-local pattern.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced both raw and ratcheted clean-convertible boundary counts by one.

### Slice 32: Run narrative init smoke in process

- Objective: Remove the process boundary from the narrative adapter initialization smoke.
- Why this approach: `test_narrative_scenario_blocks.py` already imports narrative resolver/reviewer modules and has file-local in-process runners; adding `init_adapter.py` keeps the adapter-script coverage in one pattern.
- Commits:
- What changed: Imported the narrative init adapter module, added `run_narrative_init_adapter()`, and converted the default-source test to call `main()` in process.
- Alternatives rejected: Left the review-adapter subprocess in the same file untouched because it was not classified as a clean in-process candidate in the boundary inventory.
- Targeted verification: pytest: `tests/quality_gates/test_narrative_scenario_blocks.py` `6 passed` in 0.44s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 65 candidates and 26 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 62 candidates and 25 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted one existing smoke.
- Critique: Same-agent slice critique: file creation is still verified against the temp repo, while only the interpreter boundary is removed.
- Off-goal findings: None.
- Lessons carried forward: Boundary inventory classification is useful for stopping scope creep inside a nearby file; convert the clean candidate and leave non-clean subprocesses alone.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced both raw and ratcheted clean-convertible boundary counts by one.

### Slice 33: Batch portable JSON smokes in process

- Objective: Remove several nested process invocations from portable artifact tests while keeping path-sanitization assertions intact.
- Why this approach: `test_portable_json_artifacts.py` had many pure `main()` JSON/stdout smokes and one internal-boundary HITL bootstrap dependency. A shared in-process runner converts the clean targets without weakening bootstrap setup proof.
- Commits:
- What changed: Loaded announcement, find-skills, HITL sync/check, retro persistence, and markdown preview scripts as modules; added `run_loaded_script()` with `SystemExit` handling; converted six clean script targets while leaving HITL bootstrap subprocesses in place.
- Alternatives rejected: Did not convert `bootstrap_review.py` because the boundary inventory classifies it as internal-boundary and the test uses it to create runtime state for later checks.
- Targeted verification: pytest: `tests/quality_gates/test_portable_json_artifacts.py` `9 passed` in 0.89s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 65 candidates, 102 candidate keys, and 25 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 62 candidates and 24 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted existing smokes through one helper.
- Critique: Same-agent slice critique: the test file remains in the boundary inventory because `bootstrap_review.py` still correctly spans an internal process boundary, but candidate-key pressure dropped by six and the pure JSON contracts remain covered through `main()`.
- Off-goal findings: None.
- Lessons carried forward: Track candidate-key deltas for files that intentionally remain candidates; file-count-only metrics hide partial cleanup wins.
- Metrics: Speed/testability proxy: removed six nested Python script invocations and reduced raw boundary candidate keys from 108 to 102.

### Slice 34: Run current-pointer HITL sync smoke in process

- Objective: Remove the clean HITL sync subprocess from current-pointer symlink protection tests.
- Why this approach: The test intentionally keeps `bootstrap_review.py` as setup, then only needs `sync_review_artifact.py main()` to write the latest artifact; direct module execution preserves the symlink assertion.
- Commits:
- What changed: Loaded `sync_review_artifact.py` as a module, added a file-local in-process runner, and converted the symlinked latest HITL sync test.
- Alternatives rejected: Did not convert `bootstrap_review.py` because it remains an internal-boundary setup command in the inventory.
- Targeted verification: pytest: `tests/quality_gates/test_current_pointer_writes.py` `20 passed` in 0.87s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 65 candidates, 101 candidate keys, and 24 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 62 candidates and 23 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted one existing smoke.
- Critique: Same-agent slice critique: symlink behavior remains asserted after the write, and the only removed boundary is Python process startup for a clean script target.
- Off-goal findings: None.
- Lessons carried forward: For mixed boundary tests, leave setup processes alone when they model runtime state creation and convert only the follow-up clean target.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced raw candidate keys by one.

### Slice 35: Run quality bootstrap smokes in process

- Objective: Remove repeated nested process startup from quality bootstrap/init/resolve tests.
- Why this approach: `test_quality_bootstrap.py` already had in-process resolver helpers; adding bootstrap/init helpers converts many repeated CLI calls while preserving the CLI's validation-error stderr contract.
- Commits:
- What changed: Loaded `bootstrap_adapter.py` and `init_adapter.py` as modules, added `_run_quality_bootstrap_adapter()` and `_run_quality_init_adapter()`, converted all remaining quality bootstrap/init/resolve `run_script()` calls, and removed the unused `run_script` import.
- Alternatives rejected: Did not split the large test file in this slice because that would be a broader refactor; closeout now warns the file is 749/800 code lines, so future work should avoid adding more to this file or extract helpers first.
- Targeted verification: pytest: `tests/quality_gates/test_quality_bootstrap.py` `17 passed` in 0.57s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 64 candidates, 98 candidate keys, and 23 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 61 candidates and 22 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed with the length warning noted above.
- Test duplication pressure: No new tests; converted existing smokes through two helpers.
- Critique: Same-agent slice critique: validation-error handling had to mirror the script's `__main__` guard, but the test explicitly checks the same stderr and returncode behavior.
- Off-goal findings: `tests/quality_gates/test_quality_bootstrap.py` is close to the repo's 800-line code limit after this helper addition.
- Lessons carried forward: For high-call-count test files, runtime wins can be larger than inventory key count suggests; record actual repeated-call conversion and heed file-length pressure before adding more helpers.
- Metrics: Speed/testability proxy: removed repeated quality bootstrap/init subprocess calls, reduced raw candidate keys from 101 to 98, and removed `test_quality_bootstrap.py` from the clean-convertible file list.

### Slice 36: Run retro resolver smoke in process

- Objective: Remove a pure retro resolver subprocess from retro memory tests.
- Why this approach: The test only checks `resolve_adapter.py` JSON for the current repo; a direct `main()` call preserves that behavior and avoids startup cost.
- Commits:
- What changed: Loaded the retro resolver script as a module, added a small runner, and converted the recent-lessons summary path smoke.
- Alternatives rejected: Did not change the prose-only AGENTS/handoff/skill assertions in the same file because they do not involve process startup.
- Targeted verification: pytest: `tests/quality_gates/test_retro_memory.py` `4 passed` in 0.41s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 63 candidates, 97 candidate keys, and 22 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 60 candidates and 21 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted one existing smoke.
- Critique: Same-agent slice critique: this no longer proves standalone interpreter startup for the retro resolver, but the adapter JSON contract remains covered.
- Off-goal findings: None.
- Lessons carried forward: Continue choosing small resolver smokes when they completely remove a file from the clean-convertible set.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced raw and ratcheted clean-convertible counts by one.

### Slice 37: Run goal artifact CLI smokes in process

- Objective: Remove remaining `check_goal_artifact.py` subprocess calls from goal freshness tests.
- Why this approach: The file already had `run_check_goal_artifact()` for most CLI cases; converting the two leftover subprocess tests makes the whole check-goal-artifact suite use one in-process path.
- Commits:
- What changed: Routed the head-freshness failure and missing-goal-path usage-error tests through the existing runner and removed the now-unused `run_script` import.
- Alternatives rejected: Kept git subprocess fixture setup in `_init_git()` because it creates repository state rather than invoking the script under test.
- Targeted verification: pytest: `tests/quality_gates/test_goal_head_freshness.py` `15 passed` in 0.48s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 62 candidates, 96 candidate keys, and 21 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 59 candidates and 20 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted two existing smokes.
- Critique: Same-agent slice critique: the usage-error test still verifies returncode 2 and JSON output, so the CLI behavior is preserved without process startup.
- Off-goal findings: None.
- Lessons carried forward: Existing runners are often incomplete; scan for straggler `run_script()` calls before leaving a test file.
- Metrics: Speed/testability proxy: removed two nested Python script invocations and removed `test_goal_head_freshness.py` from the clean-convertible file list.

### Slice 38: Share setup inspect in-process helper

- Objective: Remove repeated `inspect_repo.py` process startup across setup inspect policy/source-guard tests while preserving the env-isolation boundary tests.
- Why this approach: Three setup inspect files used the same helper shape; centralizing `inspect_setup_repo()` in `tests/quality_gates/support.py` avoids duplicating runners and keeps the PATH-rewritten git-missing checks as explicit subprocess boundaries.
- Commits:
- What changed: Added a shared loaded-script runner and `inspect_setup_repo()` helper, converted setup inspect adapters/policy/source-guard helpers to use it, and added a boundary exemption for the remaining PATH-rewritten git-missing inspect subprocess. Sync propagated the exemption to the checked-in plugin mirror.
- Alternatives rejected: Did not convert `_run_inspect_with_env()` because that test proves behavior under a modified process environment where `git` is unavailable but `python3` still resolves.
- Targeted verification: pytest: `tests/quality_gates/test_setup_inspect_adapters.py tests/quality_gates/test_setup_inspect_policy.py tests/quality_gates/test_setup_source_guard_scan.py` `48 passed` in 1.14s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 60 candidates, 94 candidate keys, and 19 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 56 candidates and 17 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed, including plugin-manifest sync/packaging validation after the exemption mirror update.
- Test duplication pressure: Reduced helper duplication across three test files.
- Critique: Same-agent slice critique: centralizing a loaded-script helper in test support makes future in-process conversions easier, but support helpers should stay small and not become a second command framework.
- Off-goal findings: The raw advisory inventory still lists the env-isolated inspect subprocess, but the ratchet now treats it as an intentional boundary through `scripts/boundary-bypass-exemptions.txt`.
- Lessons carried forward: When process boundaries are intentional, record them in the ratchet exemption file instead of leaving repeat advisory noise.
- Metrics: Speed/testability proxy: removed repeated inspect subprocesses from policy/source-guard tests, reduced ratcheted clean-convertible count from 20 to 17, and reduced raw candidate keys from 96 to 94.

### Slice 39: Run setup retro seed smokes in process

- Objective: Remove process startup from setup retro-memory seed tests.
- Why this approach: `seed_retro_memory.py` is a pure parser/filesystem/JSON command; the shared loaded-script runner preserves stdout and returncode behavior without a subprocess.
- Commits:
- What changed: Loaded `seed_retro_memory.py` as a module and converted the adapter/digest creation and existing-gitignore preservation tests to `run_loaded_script_main()`.
- Alternatives rejected: Did not add lower-level library calls because the tests intentionally cover the script's CLI output shape.
- Targeted verification: pytest: `tests/quality_gates/test_setup_retro_memory.py` `3 passed` in 0.33s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 59 candidates, 93 candidate keys, and 18 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 55 candidates and 16 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; reused the shared loaded-script helper from Slice 38.
- Critique: Same-agent slice critique: the test still asserts created files and JSON payload; only interpreter startup proof is removed.
- Off-goal findings: None.
- Lessons carried forward: The shared loaded-script runner is paying off immediately for setup script smokes.
- Metrics: Speed/testability proxy: removed two nested Python script invocations and removed `test_setup_retro_memory.py` from the clean-convertible file list.

### Slice 40: Run HITL report smokes in process

- Objective: Remove leftover `render_report.py` subprocess calls from HITL report-mode tests.
- Why this approach: The file already had a direct `run_render_report()` helper for most tests; extending it to catch `SystemExit` preserves argparse returncode 2 cases and lets the remaining CLI smokes run in process.
- Commits:
- What changed: Added `SystemExit` handling to `run_render_report()`, converted duplicate-id, two-space-indent, and missing-required-argument smokes, and removed the `run_script` import.
- Alternatives rejected: Did not drop the argparse-required tests because they kill existing mutation-test cases around `required=True`.
- Targeted verification: pytest: `tests/quality_gates/test_hitl_report_mode.py` `12 passed` in 0.43s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 58 candidates, 92 candidate keys, and 17 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 54 candidates and 15 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; completed an existing partial in-process migration.
- Critique: Same-agent slice critique: argparse stderr is captured through the `SystemExit` path, so the tests still distinguish usage errors from ordinary validation failures.
- Off-goal findings: None.
- Lessons carried forward: When converting CLI tests with required argparse fields, runner helpers must preserve `SystemExit` return codes or mutation-killing assertions weaken.
- Metrics: Speed/testability proxy: removed four nested Python script invocations and removed `test_hitl_report_mode.py` from the clean-convertible file list.

### Slice 41: Run skill ergonomics smokes in process

- Objective: Remove leftover `validate_skill_ergonomics.py` subprocess calls from skill ergonomics gate tests.
- Why this approach: The file already imports the validator module for direct evaluation; the remaining CLI JSON smokes can call the module's `main()` through the shared loaded-script runner.
- Commits:
- What changed: Replaced three `run_script()` wrapper calls with `run_loaded_script_main()` and removed the subprocess helper import.
- Alternatives rejected: Did not replace the CLI smokes with lower-level `evaluate()` calls because the tests intentionally assert JSON wrapper behavior and nonzero status.
- Targeted verification: pytest: `tests/quality_gates/test_skill_ergonomics_gate.py` `17 passed` in 0.44s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 57 candidates, 91 candidate keys, and 16 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 53 candidates and 14 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; reused the shared loaded-script runner.
- Critique: Same-agent slice critique: wrapper JSON behavior stays asserted, and nonzero adapter-error/no-skill status remains covered without process startup.
- Off-goal findings: None.
- Lessons carried forward: Prefer direct `main()` for validator wrapper JSON tests once importability is already covered elsewhere.
- Metrics: Speed/testability proxy: removed three nested Python script invocations and removed `test_skill_ergonomics_gate.py` from the clean-convertible file list.

### Slice 42: Run mutation score summary smoke in process

- Objective: Remove the clean `check_mutation_score.py` subprocess from mutation-testing quality tests.
- Why this approach: The test asserts summary-file contents and nonzero status for survived mutants; calling `check_mutation_score.main()` through the shared loaded-script runner preserves that contract.
- Commits:
- What changed: Imported `scripts.check_mutation_score`, routed the survivor-details summary test through `run_loaded_script_main()`, and left other mutation/propose workflow subprocesses untouched.
- Alternatives rejected: Did not convert propose/run-cosmic-ray subprocesses because they model broader workflow or command execution boundaries.
- Targeted verification: pytest: `tests/quality_gates/test_quality_mutation_testing.py` `41 passed` in 1.27s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 57 candidates, 90 candidate keys, and 15 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 53 candidates and 13 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted one existing summary smoke.
- Critique: Same-agent slice critique: summary file content and returncode 1 still prove the behavior that matters here, while process startup was incidental.
- Off-goal findings: None.
- Lessons carried forward: In mixed workflow files, target only the script classified clean and leave broader subprocess workflows alone.
- Metrics: Speed/testability proxy: removed one nested Python script invocation and reduced raw candidate keys by one.

### Slice 43: Run surface validator smokes in process

- Objective: Remove clean `validate_surfaces.py` subprocess calls from surface obligation tests.
- Why this approach: The tests only need validator stdout/stderr/returncode behavior for duplicate and accepted manifests; a file-local runner can call `main()` and preserve `SurfaceError` as CLI stderr with returncode 1.
- Commits:
- What changed: Added `run_validate_surfaces()`, converted the duplicate-id and bare-recursive-dir-glob tests, and left broader surface selection/closeout CLI tests unchanged.
- Alternatives rejected: Did not convert `check_changed_surfaces.py`, `select_verifiers.py`, or `run_slice_closeout.py` tests in this file because those prove command planner surfaces rather than the simple validator target.
- Targeted verification: pytest: `tests/quality_gates/test_surface_obligations.py` `25 passed` in 1.92s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 57 candidates, 89 candidate keys, and 14 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 53 candidates and 12 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed.
- Test duplication pressure: No new tests; converted two existing smokes.
- Critique: Same-agent slice critique: `SurfaceError` handling is mirrored from the script's `__main__` guard, but the tests still assert the same stderr and returncode contract.
- Off-goal findings: None.
- Lessons carried forward: Validator scripts with `__main__` exception wrappers need runner-specific exception handling when converted in process.
- Metrics: Speed/testability proxy: removed two nested Python script invocations and reduced raw candidate keys by one.

### Slice 44: Fix boundary inventory path-argument false positives

- Objective: Stop the boundary-bypass inventory from counting script paths that are data arguments to another spawned command.
- Why this approach: `run_script("scripts/run_slice_closeout.py", "--paths", "skills/.../inspect_repo.py")` starts `run_slice_closeout.py`; the `inspect_repo.py` string is a changed-path fixture, not a process boundary. The scanner should inspect only the spawn command argument.
- Commits:
- What changed: Narrowed `_spawn_targets()` to collect script literals only from the command position or command-like keyword (`args`/`cmd`/`command`), added a regression test for `--paths skills/.../inspect_repo.py`, and synced the checked-in plugin mirror.
- Alternatives rejected: Did not add another exemption for this case because it is an inventory bug, not an intentional boundary.
- Targeted verification: pytest: `tests/test_boundary_bypass_inventory.py` `9 passed` in 0.33s; ruff passed; raw `inventory_boundary_bypass.py --summary` reports 57 candidates, 85 candidate keys, and 14 clean-convertible; `check_boundary_bypass_ratchet.py` passed at 53 candidates and 12 clean-convertible; `run_slice_closeout.py --skip-broad-pytest` passed, including plugin sync, packaging validation, scan hygiene, and boundary ratchet.
- Test duplication pressure: Added one focused regression test because this was a scanner correctness bug.
- Critique: Same-agent slice critique: keyword detection is intentionally narrow; it still handles common `subprocess.run(args=[...])`/`command=...` forms without scanning every non-command option.
- Off-goal findings: Boundary raw inventory previously over-counted path fixtures as clean in-process targets.
- Lessons carried forward: Advisory inventories need false-positive fixes, not just exemptions, when the path is not actually spawned.
- Metrics: Token/testability proxy: reduced raw boundary candidate keys from 89 to 85 and removed misleading clean-target pressure from path-argument fixtures.

## Context Sources

- User request on 2026-06-26: repeat sustained quality improvement for 3 hours
  and finish with push/release.
- `docs/handoff.md` pickup notes; stale release-state lines checked against
  recent git log and release planner.
- `charness-artifacts/retro/recent-lessons.md`: avoid brute-force broad pytest
  fallback, record goal window before metrics, avoid many tiny subprocess-only
  slices, persist release/retro follow-up.
- `docs/design-north-star.md`: irreversible-boundary proof is provisional until
  distinct-channel evidence and fresh observer are recorded.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md`.
- `skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`.
- `skills/public/release/scripts/plan_release_run.py --repo-root . --json`.

## Interview Decisions

- Mode family: artifact-only vs implementation-continuation. Chosen:
  implementation-continuation because the user requested ongoing work and final
  publication. Rejected artifact-only as contrary to the explicit instruction.
- Timebox family: exact wall-clock continuation vs bounded meaningful slices
  with closeout reserve. Chosen: 3h timebox with 20m closeout reserve and
  continue-next-improvement policy. Rejected early release once first slice
  finishes, matching the prior-turn lesson.
- Publication family: local-only proof vs final push/release. Chosen: final
  push/release after proof because the user explicitly requested it. Rejected
  per-slice publication because approval is phase-scoped and wasteful.
- Scope family: many tiny subprocess conversions vs higher-leverage structural
  slices. Chosen: inventory-led structural fixes. Rejected repeated micro-slices
  due recent retro waste.
- Axis check: host/provider/environment are variable in adapters and release
  proof; no host-specific assumption is promoted to global contract.

## Plan Critique Findings

- Folded blocker: release/push are irreversible; final proof and fresh-eye
  critique are required before publication.
- Folded blocker: broad quality runtime must be measured, not guessed; runtime
  summary is required before making speed claims.
- Folded blocker: local gate weakening is unsafe unless CI or another channel
  repeats the proof; keep local proof by default.
- Over-worry not folded: exact three-hour wall-clock exhaustion is less useful
  than preserving closeout reserve and making every remaining slice safe; if
  no safe next slice exists, the final artifact must say why.
- Reviewer provenance: same-agent preflight critique at activation; fresh-eye
  review required before release boundary.

## Off-Goal Findings

None yet.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After closeout, verify the pushed commit and release tag named in the final
report, then run `./scripts/run-quality.sh --read-only` if local reproduction
is desired.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
