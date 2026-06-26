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
