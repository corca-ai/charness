# Achieve Goal: Quality Duplication Workflow Improvement 6h

Status: active
Created: 2026-06-12
Activation: `/goal @charness-artifacts/goals/2026-06-12-quality-duplication-workflow-improvement-6h.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command. This artifact is active because the operator
created the host goal and asked the agent to continue.

## Active Operating Frame

- Current slice: Slice 9 - continue with final closeout or the next locally safe
  cleanup after recording the committed release adapter preflight helper split.
- Next action: choose between the remaining release CLI warn-band/function
  pressure and final closeout if the reserve window is reached.
- Timebox: 6h
- Activation time: 2026-06-11T21:13:55Z
- Closeout reserve: 30m
- Done-early policy: continue_next_improvement
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Continue improving Charness quality for up to six hours, prioritizing duplicated
structure and workflow/skill quality. Apply the strengthened timebox early-close
ledger rule so the run does not close with low yield: if it stops before the
reserve window, record distinct next-slice candidates and an outcome sufficiency
check.

## Non-Goals

- Do not push, release, publish, or depend on remote CI unless the operator
  explicitly asks.
- Do not treat a metric-only improvement as sufficient; each slice should
  reduce an actual duplicated structure, workflow ambiguity, gate weakness, or
  maintainability pressure.
- Do not rewrite unrelated release/#354 work just because it appears in
  `docs/handoff.md`; that drafted goal is context, not this run's scope.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Local-only quality work is preferred. Any release/install-machine proof is a
  separate lane unless it directly blocks the chosen quality slice.
- Before early closeout, `## Final Verification` must include at least two
  distinct `Next slice candidate:` ledger lines and an
  `Outcome sufficiency check:` per `achieve` lifecycle rules.

## User Acceptance

- Inspect the commits recorded in `## Final Verification` and confirm each one
  is a real quality improvement, not only artifact churn.
- Re-run the listed focused tests and broad gates.
- Confirm any early-close ledger names the next plausible slices and honestly
  explains why they were not continued inside the timebox.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `ruff check ...` and `python3 -m py_compile ...` for changed Python files.
- Focused pytest for changed behavior.
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`

### High-Confidence Checks

- Surface-recommended validators for touched docs, skills, generated exports,
  and artifacts.
- Fresh-eye critique for substantial slices before commit.
- Broad pytest at bundle/final boundary:
  `pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py`.

### External Or Live Proof

- Not planned. No push/release/remote-CI proof is claimed unless explicitly run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Pick and land one structural quality cleanup from current duplication/workflow pressure. | The user explicitly objected to low-yield goal execution; the next move must produce a concrete quality delta. | Committed code/test/doc change plus focused and surface-recommended gates. | committed (`25201777`) |
| 2 | Continue to the next distinct safe cleanup if time remains. | Done-early policy requires continuation rather than stopping after one small win. | Another committed cleanup or a valid early-close ledger with distinct candidates and sufficiency check. | committed (`6287bb27`) |
| 3 | Remove the next hard-limit pressure point without changing behavior assertions. | `test_surface_obligations.py` was 798/800 code lines, leaving only two lines of hard-limit headroom. | Split test module, regenerated boundary-bypass baseline, fresh-eye critique, focused and surface-recommended gates. | committed (`c863bac9`) |
| 4 | Remove the next test warn-band pressure point without overgeneralizing coverage behavior. | `test_quality_mutation_sampling.py` was 763/800 code lines; coverage collection tests formed a coherent cluster. | Split coverage collection test module, fresh-eye critique, focused and surface-recommended gates. | committed (`1f50ab7f`) |
| 5 | Remove the next production helper warn-band pressure point. | `quality_bootstrap_lib.py` was 441/480 code lines, close to its hard limit. | Split bootstrap output/rendered-diff helper module, plugin sync, fresh-eye critique, focused and surface-recommended gates. | committed (`5c5ffa1e`) |
| 6 | Reduce repeated temporary surface-manifest fixture setup in the closeout-runner tests. | Slice 3 intentionally deferred the fixture duplication after splitting the hard-limit test file. | Local fixture helper, fresh-eye critique, focused ruff and pytest. | committed (`9fdc07e8`) |
| 7 | Remove the next support helper warn-band pressure point. | `acquire_public_url.py` had 12 lines of headroom before the hard limit, and fallback/direct-attempt policy was a coherent boundary. | Policy helper split, plugin sync, fresh-eye critique, focused web-fetch/youtube tests, and surface-recommended gates. | committed (`c4b28eab`) |
| 8 | Remove the next release helper warn-band pressure point. | `publish_release_preflight.py` was close to its hard limit, and release adapter focused-preflight logic was a coherent sub-boundary. | Adapter preflight helper split, plugin sync, fresh-eye critique, focused release tests, and surface-recommended gates. | committed (`e6796431`) |
| 9 | Final closeout or continue to another distinct safe cleanup if time remains. | The goal must prove honest completion, non-claims, and residual work without stopping early while clear candidates remain. | Complete goal artifact passing `check_goal_artifact.py`, or another committed cleanup before final closeout. | planned |

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

Routing: find-skills task recommendation (2026-06-12) selected `quality` for
the active quality-improvement workflow; `achieve` owns the long-running goal
artifact and `impl` will own code/config/test mutations when a slice is chosen.
Gather: n/a — no external source is needed for the first local quality slice.
Release: n/a — no version, release, or install-manifest surface is in scope.
Issue closeout: n/a — no tracked issue is being resolved by default in this
general quality-improvement goal.

## Slice Log

### Slice 1: Slice 1 - issue skill loader/probe split

- Objective: Reduce a concrete issue-skill duplication and length-pressure point without changing issue CLI behavior.
- Why this approach: The issue loader duplication was local, repeated across several sibling scripts, and issue_tool.py was at 358/360 code lines. Moving the sibling loader into issue_local_import.py and backend probe construction into issue_backend.py removes a real source-file pressure point while staying inside the issue skill boundary.
- Commits: `25201777`
- What changed: Added issue_local_import.py; converted issue_tool.py, issue_read.py, issue_close.py, issue_create.py, issue_verify_closeout.py, and describe_closeout_draft_shape.py to use it; moved preflight probe/payload helpers into issue_backend.py; synced plugins/charness issue export; added a focused non-JSON preflight config-error test.
- Alternatives rejected: Rejected broad init_adapter/resolve_adapter cleanup for this first slice because it spans many public skills and generated surfaces. Rejected a broader import framework because the remaining runpy one-liner is smaller than the duplicated spec loader bodies and avoids package-layout assumptions.
- Targeted verification: ruff changed issue files/tests; focused pytest 110 passed; broad pytest before the final cheap test was 2806 passed, 4 skipped, 26 deselected; changed-surface validators for packaging, skills, public-skill policy/dogfood, markdown/docs/secrets, py_compile, attention-state, gitignore scan hygiene, boundary ratchet passed.
- Test duplication pressure: issue_tool.py left the Python length warn band (358 -> 291 code lines). tests/quality_gates/test_issue_skill.py grew from 736 -> 761 and remains warn-band; this is an honest next-slice pressure, not hidden success.
- Critique: Fresh-eye critique: charness-artifacts/critique/2026-06-12-issue-skill-loader-probe-split.md. Counterweight found no code diff required before commit after the cheap preflight test; remaining Act Before Ship item is inclusion/staging of new helper and durable artifacts.
- Off-goal findings: nose total_dup_lines was not a clean win (baseline 3063 -> 3073 after helper/relocation), so this slice must not claim total clone-line reduction. Nose family count improved 525 -> 523 and the issue loader family disappeared from the top findings.
- Lessons carried forward: Metric-only claims are fragile; pair clone inventory with file-level pressure and reviewer triage. Next cleanup should avoid improving one source file by pushing unchecked pressure into a test file.
- Metrics: issue_tool.py 358 -> 291 code lines; Python length warn-band files 8 -> 7 before the added test, then 7 with test_issue_skill.py still warned; nose total_families 525 -> 523; nose total_dup_lines 3063 -> 3073.

### Slice 2: Slice 2 - issue preflight test split

- Objective: Reduce the test-side length pressure introduced/exposed by Slice 1 without hiding behavior assertions outside test files.
- Why this approach: test_issue_skill.py was in the test-file warn band after the previous slice. Its preflight/backend-resolution tests formed a coherent sub-surface, and the duplicated issue adapter YAML writer also appeared in test_issue_closeout_verifier.py.
- Commits: `6287bb27`
- What changed: Added tests/quality_gates/test_issue_preflight.py for preflight/backend-resolution assertions; added write_issue_adapter_with_backend to tests/quality_gates/support.py; removed duplicate adapter writer from test_issue_skill.py and test_issue_closeout_verifier.py; updated callers.
- Alternatives rejected: Rejected a broader generic adapter-fixture DSL because remaining inline adapter writes are shape-specific. Rejected moving behavior assertions into support helpers; only mechanical YAML setup moved.
- Targeted verification: ruff changed files and repo-wide ruff passed; focused issue tests passed 60; full length gate passed and warn-band count dropped 7 -> 6; check_test_repo_copy_invariants, boundary-bypass ratchet, attention-state visibility passed; critique artifacts validator passed; broad pytest passed 2807, 4 skipped, 26 deselected.
- Test duplication pressure: test_issue_skill.py moved from 761/800 code lines and warn-band to 585/800; test_issue_preflight.py is 151/800; support.py is 332/800; test_issue_closeout_verifier.py dropped from 614/800 to 583/800.
- Critique: Fresh-eye critique: charness-artifacts/critique/2026-06-12-issue-preflight-test-split.md. Counterweight required no further code edits; remaining Act Before Ship item is inclusion/staging of the new test file.
- Off-goal findings: Nose production clone inventory was unchanged; this was a test-pressure cleanup, not a production clone-line reduction.
- Lessons carried forward: A test split is only a quality improvement when behavior assertions remain in test files and only mechanical scaffolding moves to support. Next candidate: fake ceal binary setup repetition or another warn-band file.
- Metrics: Python length warn-band files 7 -> 6; test_issue_skill.py 761 -> 585 code lines; test_issue_closeout_verifier.py 614 -> 583; broad pytest 2807 passed.

### Slice 3: Slice 3 - surface-obligations closeout test split

- Objective: Remove the immediate hard-limit pressure from `test_surface_obligations.py` without deleting or hiding closeout-runner behavior assertions.
- Why this approach: `tests/quality_gates/test_surface_obligations.py` was at 798/800 code lines. The `run_slice_closeout` tests formed a coherent runner-behavior cluster distinct from changed-surface selection and surfaces-manifest validation.
- Commits: `c863bac9`
- What changed: Added `tests/quality_gates/test_run_slice_closeout_surface_obligations.py` for closeout runner tests; removed the moved tests and unused imports from `test_surface_obligations.py`; regenerated `scripts/boundary-bypass-baseline.json` for the test-file key migration and synced `plugins/charness/scripts/boundary-bypass-baseline.json`.
- Alternatives rejected: Rejected extracting all repeated temporary `.agents/surfaces.json` setup in the same slice because that would broaden a length/cohesion split into a fixture-refactor slice. Rejected hand-editing stale baseline keys back into the regenerated baseline just to keep the diff narrower.
- Targeted verification: focused pytest for the two split files passed 36; changed-file ruff passed; full repo ruff passed; full Python length gate passed with warn-band files 6 -> 5; validate_attention_state_visibility passed; check_test_repo_copy_invariants passed; check_boundary_bypass_ratchet passed after canonical baseline regeneration; packaging, packaging-committed, integrations, sync_support dry-run, and update_tools dry-run passed; broad pytest passed 2807, 4 skipped, 26 deselected.
- Test duplication pressure: `test_surface_obligations.py` moved from 798/800 to 347/800 code lines; the new closeout test file is 455/800. Remaining repeated temporary surface-manifest setup is acknowledged as a future fixture cleanup candidate, not claimed solved here.
- Critique: Fresh-eye critique: `charness-artifacts/critique/2026-06-12-surface-obligation-closeout-test-split.md`. Counterweight required no additional implementation; Act Before Ship items are staging the new test file and critique packet artifacts.
- Off-goal findings: Boundary-bypass baseline regeneration also removed two stale scaffold/export keys (`tests/test_critique_scaffold.py::scripts/export_plugin.py` and `tests/test_handoff_scaffold.py::scripts/export_plugin.py`). Reviewers treated this as canonical baseline cleanup because current inventory and root/plugin baselines match.
- Lessons carried forward: A file split can honestly fix hard-limit pressure and cohesion without fixing every local duplication. Next slice should choose between the remaining warn-band files and the repeated temporary surface-manifest fixture setup.
- Metrics: Python length warn-band files 6 -> 5; `test_surface_obligations.py` 798 -> 347 code lines; new `test_run_slice_closeout_surface_obligations.py` 455 code lines; broad pytest 2807 passed.

### Slice 4: Slice 4 - mutation coverage collection test split

- Objective: Remove the next test warn-band pressure point without deleting coverage regression assertions or overclaiming a broad mutation-test cleanup.
- Why this approach: `tests/quality_gates/test_quality_mutation_sampling.py` was 763/800 code lines. Its coverage collection tests (`coverage_run_command`, subprocess coverage capture, stale coverage shard cleanup) form a coherent cluster distinct from sampling selection, changed-line filtering, and manifest assertions.
- Commits: `1f50ab7f`
- What changed: Added `tests/quality_gates/test_quality_mutation_coverage.py` for coverage collection regression tests; removed the moved tests and coverage-collection-only imports from `test_quality_mutation_sampling.py`; removed an unused `ROOT` constant from the new file after fresh-eye review.
- Alternatives rejected: Rejected a broader mutation-test taxonomy rewrite because remaining coverage filtering/context/manifest tests still belong with sampling behavior. Rejected moving behavior assertions into support helpers; this is a file-boundary split only.
- Targeted verification: focused ruff passed; focused pytest for the split files passed 29 both before and after the tiny unused-constant cleanup; headroom check showed `test_quality_mutation_sampling.py` 763/800 -> 676/800 and new `test_quality_mutation_coverage.py` 96/800; full repo ruff passed; full Python length gate passed with warn-band files 5 -> 4; validate_attention_state_visibility passed; check_test_repo_copy_invariants passed; check_boundary_bypass_ratchet passed; final broad pytest passed 2807, 4 skipped, 26 deselected.
- Test duplication pressure: `test_quality_mutation_sampling.py` left the warn band. This is a coverage collection split only; sampling still owns coverage filtering, coverage context/nodeid, and manifest coverage assertions.
- Critique: Fresh-eye critique: `charness-artifacts/critique/2026-06-12-quality-mutation-coverage-test-split.md`. Counterweight required no additional implementation beyond staging the new test file and keeping wording scoped to coverage collection.
- Off-goal findings: none.
- Lessons carried forward: Splits should name the behavior cluster they actually move. Do not claim all coverage-related mutation behavior moved when the original sampling file still owns coverage filtering and manifest coverage assertions.
- Metrics: Python length warn-band files 5 -> 4; `test_quality_mutation_sampling.py` 763 -> 676 code lines; new `test_quality_mutation_coverage.py` 96 code lines; final broad pytest 2807 passed.

### Slice 5: quality bootstrap output/rendered-diff split

- Objective: Remove the next production helper warn-band pressure point while preserving quality bootstrap behavior and public import compatibility.
- Why this approach: `scripts/quality_bootstrap_lib.py` was 441/480 code lines. Its YAML output rendering and rendered-output defaulted-only diff check formed a coherent helper boundary separate from adapter detection/state/write orchestration.
- Commits: `5c5ffa1e`
- What changed: Added `scripts/quality_bootstrap_render.py`; moved `render_bootstrap_adapter` and the defaulted-only rendered diff helper there; kept `quality_bootstrap_lib.render_bootstrap_adapter` available by importing it from the new module; aliased `diff_is_defaulted_only` back to `_diff_is_defaulted_only` for the existing write path; regenerated `plugins/charness/scripts/quality_bootstrap_lib.py` and added `plugins/charness/scripts/quality_bootstrap_render.py`.
- Alternatives rejected: Rejected calling this a render-only boundary because the moved diff helper is write-suppression policy coupled to rendered output. Rejected direct private-helper tests because the focused bootstrap tests already cover rendering and defaulted-only short-circuit behavior through the public bootstrap path.
- Targeted verification: focused ruff passed; `pytest -q tests/quality_gates/test_quality_bootstrap.py` passed 16; headroom check showed `quality_bootstrap_lib.py` 441/480 -> 369/480 and new `quality_bootstrap_render.py` 81/480; packaging and validate_packaging_committed passed; validate_integrations, sync_support dry-run, and update_tools dry-run passed; full repo ruff passed; full Python length gate passed with warn-band files 4 -> 3; validate_attention_state_visibility passed; check_test_repo_copy_invariants passed; check_boundary_bypass_ratchet passed; gitignore scan hygiene passed; broad pytest passed 2807, 4 skipped, 26 deselected.
- Production pressure: `quality_bootstrap_lib.py` left the warn band. Remaining warn-band files are release/web-fetch scripts, plus a near-limit `publish_release_cli.execute_publish_plan` function.
- Critique: Fresh-eye critique: `charness-artifacts/critique/2026-06-12-quality-bootstrap-output-rendered-diff-split.md`. Counterweight required no code or test change beyond staging the new source/plugin render modules and keeping wording scoped to output/rendered-diff logic.
- Off-goal findings: none.
- Lessons carried forward: When splitting a production helper, preserve the old import surface unless the slice explicitly owns an API migration. Name the boundary by the behavior moved, not by a cleaner-sounding partial label.
- Metrics: Python length warn-band files 4 -> 3; `quality_bootstrap_lib.py` 441 -> 369 code lines; new `quality_bootstrap_render.py` 81 code lines; broad pytest 2807 passed.

### Slice 6: surface-manifest fixture helper

- Objective: Reduce repeated temporary surface-manifest fixture setup in the closeout-runner tests without hiding behavior assertions.
- Why this approach: Slice 3 moved closeout-runner behavior into `test_run_slice_closeout_surface_obligations.py` but deliberately left repeated inline `.agents/surfaces.json` setup for a later fixture cleanup. The repeated schema boilerplate made each test longer while the behavior-specific fields were a small subset of each manifest.
- Commits: `9fdc07e8`
- What changed: Added local `demo_surface()` and `write_surface_manifest()` helpers in `tests/quality_gates/test_run_slice_closeout_surface_obligations.py`; converted repeated inline manifest JSON setup to helper calls; preserved explicit behavior-specific fields at call sites; used explicit `is not None` defaults so future tests can intentionally pass empty lists.
- Alternatives rejected: Rejected a shared support helper because this fixture shape is currently local to the closeout-runner tests. Rejected hiding script body setup or assertions behind helpers; only manifest boilerplate moved.
- Targeted verification: focused ruff passed; `git diff --check` passed; `pytest -q tests/quality_gates/test_run_slice_closeout_surface_obligations.py` passed 11; Python length gate still passed with the same 3 warn-band files.
- Test duplication pressure: The file changed by 50 additions and 108 deletions, reducing repeated inline manifest setup by 58 net lines while keeping behavior assertions in test bodies.
- Critique: Fresh-eye critique: `charness-artifacts/critique/2026-06-12-surface-manifest-fixture-helper.md`. Counterweight required no additional code/test changes after the optional-list default fix.
- Off-goal findings: none.
- Lessons carried forward: A local test helper is worthwhile when it removes repeated fixture schema while leaving the fields that express each test's behavior visible at the call site.
- Metrics: `test_run_slice_closeout_surface_obligations.py` 498 -> 440 total lines and 455 -> 395 nonblank/noncomment lines; net diff 50 insertions and 108 deletions; focused pytest 11 passed.

### Slice 7: web-fetch acquire policy helper split

- Objective: Remove the next support helper warn-band pressure point without changing public acquisition behavior.
- Why this approach: `skills/support/web-fetch/scripts/acquire_public_url.py` had only 12 lines of hard-limit headroom. Its defuddle/browser/YouTube fallback decisions and direct-attempt sufficiency guard form policy logic separate from URL acquisition orchestration, payload rendering, and CLI parsing.
- Commits: `c4b28eab`
- What changed: Added `skills/support/web-fetch/scripts/acquire_public_url_policy.py`; moved fallback/direct-attempt policy helpers there; preserved old private aliases in `acquire_public_url.py` for existing tests and callers; regenerated `plugins/charness/support/web-fetch/scripts/acquire_public_url.py` and added `plugins/charness/support/web-fetch/scripts/acquire_public_url_policy.py`.
- Alternatives rejected: Rejected changing tests to import the new helper directly because the old private import surface is already used by tests and compatibility costs almost nothing. Rejected standalone direct-import support for the new helper because sibling script modules in this skill already rely on script-directory path setup through entrypoints.
- Targeted verification: focused ruff passed; `pytest -q tests/test_web_fetch_support.py tests/test_web_fetch_cleanup.py tests/test_youtube_source.py` passed 63; Python length gate passed with warn-band files 3 -> 2; packaging and validate_packaging_committed passed; validate_skills and skill py_compile passed; check_skill_ownership_overlap and validate_skill_ergonomics passed; gitignore scan hygiene passed; staged mirror drift check passed before staging.
- Support pressure: `acquire_public_url.py` left the warn band, moving from 348/360 code lines to 296/360; the new policy helper is 67/360 code lines. Remaining warn-band files are the release helper scripts.
- Critique: Fresh-eye critique: `charness-artifacts/critique/2026-06-12-web-fetch-acquire-policy-helper-split.md`. Counterweight required no further code/test change beyond including the new source/plugin helper files and recording the surface validations.
- Off-goal findings: none.
- Lessons carried forward: Preserve compatibility aliases when moving private helpers that tests already exercise. Split by behavior boundary, not by moving arbitrary lines.
- Metrics: Python length warn-band files 3 -> 2; `acquire_public_url.py` 348 -> 296 code lines; new `acquire_public_url_policy.py` 67 code lines; focused pytest 63 passed.

### Slice 8: release adapter preflight helper split

- Objective: Remove the next release helper warn-band pressure point without changing release adapter focused-preflight behavior.
- Why this approach: `skills/public/release/scripts/publish_release_preflight.py` was 334/360 code lines. The release-adapter focused-preflight logic had a coherent boundary around adapter candidate paths, field diffing, focused command payload construction, and command execution, distinct from critique, update-instructions, and real-host preflight checks.
- Commits: `e6796431`
- What changed: Added `skills/public/release/scripts/publish_release_adapter_preflight.py`; moved adapter-diff and focused command logic there; kept `publish_release_preflight.release_adapter_preflight_payload` and `publish_release_preflight.run_release_adapter_preflight` as wrapper functions; loaded the helper by sibling path so direct `spec_from_file_location` tests keep working; moved attention-state visibility declaration for `not_configured`/`not_evaluable` to the new helper; regenerated `plugins/charness/skills/release/scripts/publish_release_preflight.py` and added its plugin helper mirror.
- Alternatives rejected: Rejected converting release scripts to normal package imports because existing tests and skill runtime paths load release scripts by file location. Rejected preserving old private helper symbols on `publish_release_preflight.py` because no current callers use them.
- Targeted verification: focused ruff passed; `pytest -q tests/quality_gates/test_release_backend.py tests/quality_gates/test_release_publish.py::test_publish_release_runs_adapter_preflight_before_bump tests/quality_gates/test_release_publish.py::test_publish_release_records_adapter_preflight_in_release_artifact` passed 16; direct `spec_from_file_location` import smoke passed; Python length gate passed with warn-band files 2 -> 1; packaging and validate_packaging_committed passed; validate_skills and skill py_compile passed; check_skill_ownership_overlap and validate_skill_ergonomics passed; validate_public_skill_validation and validate_public_skill_dogfood passed; validate_attention_state_visibility passed after declaration ownership moved with the helper; validate_cautilus_proof passed; gitignore scan hygiene passed; staged mirror drift check passed before staging.
- Release pressure: `publish_release_preflight.py` left the warn band, moving from 334/360 code lines to 215/360; the new adapter helper is 153/360 code lines. Remaining warn-band/function pressure is `publish_release_cli.py` and `execute_publish_plan()`.
- Critique: Fresh-eye critique: `charness-artifacts/critique/2026-06-12-release-adapter-preflight-helper-split.md`. Counterweight required no further code/test changes beyond including the new source/plugin helper files and recording validation evidence.
- Off-goal findings: none.
- Lessons carried forward: For release scripts loaded by path, preserve wrapper surfaces and use sibling-path loading unless a slice explicitly owns the broader import contract migration.
- Metrics: Python length warn-band files 2 -> 1; `publish_release_preflight.py` 334 -> 215 code lines; new `publish_release_adapter_preflight.py` 153 code lines; focused pytest 16 passed.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request in this thread: continue up to six hours of Charness quality
  improvement, prioritizing duplicated structure and workflow/skill quality.
- `docs/handoff.md` for current repo context and stale/active adjacent lanes.
- `charness-artifacts/retro/recent-lessons.md` for repeat traps.
- Previous goal:
  `charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`.
- Achieve early-close gate commit:
  `9b7c3de5 Strengthen achieve timebox early close gate`.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Goal mode: continue implementation now rather than draft-only activation,
  because the operator already created the host goal and asked for continuation.
- Scope priority: duplicated structure and workflow/skill quality over release
  proof or issue-specific work, because the user's complaint was low-yield
  quality progress.
- Timebox: 6h from the new host-goal continuation point with 30m closeout
  reserve; early close before reserve requires candidate ledger and sufficiency
  check.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Initial self-critique: do not spend this turn only on artifacts; the first
  implementation slice must change repo quality posture measurably or reduce a
  real workflow/testability pressure.
- Counterweight: the artifact is still needed because the host goal alone is not
  durable repo state and cannot carry slice evidence across compaction.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
