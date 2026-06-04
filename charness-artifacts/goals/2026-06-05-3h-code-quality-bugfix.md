# Achieve Goal: 3h Code Quality Bugfix And Skill Health

Status: active
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-3h-code-quality-bugfix.md`
Timebox: 3h
Activation time: 2026-06-05T07:41:49+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 5 complete; mutation score summary helper extraction is
  verified.
- Next action: decide whether the remaining time should address the final
  measured length warning or enter final closeout based on the timebox reserve.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Run a three-hour Charness improvement goal focused on code quality, bug fixes,
and skill health. Start from current repository quality signals, identify the
highest-value reproducible defect or quality weakness, implement focused fixes,
and preserve portable skill behavior across public/support/plugin surfaces.

Discuss before activation: RESOLVED by the user's Before-phase request and this
draft's explicit boundaries. The goal is an implementation-continuation run only
after `/goal` activation. No live, provider, release, publication, or tracked
GitHub issue closeout is assumed. If a tracked issue becomes the selected bug,
the run must route through `issue` and `debug` before claiming closeout.

## Non-Goals

- Do not publish a release, bump versions, edit install manifests, or claim
  installed-host behavior unless the user separately asks for release work.
- Do not chase cosmetic refactors, length warnings, or duplicate advisories
  unless they remove real risk, reduce proof cost, or improve skill
  maintainability.
- Do not change public skill contracts, support-skill boundaries, or generated
  exports without syncing all owning surfaces and running focused validation.
- Do not close or split a tracked GitHub issue opportunistically; issue closeout
  needs an explicit selected issue, root-cause/debug evidence for bug-class
  work, and issue closeout proof.
- Do not substitute live or provider proof with local deterministic checks; name
  skipped proof levels explicitly at final closeout.

## Boundaries

- Timebox active improvement work to three hours from activation, protecting a
  20-minute closeout reserve for proof, artifact updates, critique, commit, and
  user closeout. If closeout starts inside the reserve, finish the closeout even
  if it crosses the wall.
- If the first selected issue finishes early and safe time remains, continue to
  the next quality or skill-health improvement under the same boundaries.
- Prefer bugs or quality gaps with reproducible evidence: failing/fragile tests,
  quality inventory findings, skill ergonomics findings, stale generated
  surfaces, routing drift, or clear helper-level defects.
- Skill health includes public skill metadata, trigger clarity, support skill
  portability, generated plugin exports, routing/coordination cues, and
  validators that protect those contracts.
- Keep edits scoped to the chosen slice. For skill or export changes, follow the
  repo's sync-before-verify discipline and avoid host-specific behavior outside
  adapters, presets, and integration manifests.
- Every meaningful slice should end with focused checks, a slice-log update,
  and a commit before broadening to another improvement.
- Use fresh-eye critique for non-trivial bug fixes, public/support skill
  contract changes, validator changes, generated export changes, or test
  deletion/demotion.

## User Acceptance

- Review the final commits and see at least one concrete code-quality, bug-fix,
  or skill-health improvement with focused evidence.
- Inspect the slice log and see why each selected target beat alternatives on
  risk reduction, confidence, or proof-cost savings.
- Re-run the listed focused tests and final broad/substitute checks.
- Confirm skill-health changes, if any, include synced public/support/plugin
  surfaces and validators or tests that protect the intended behavior.
- Confirm skipped release, live, provider, or issue-closeout proof is stated as
  a non-claim.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch` before selecting targets and before each commit.
- `find-skills` recommendation for the active phase or validation boundary, with
  routing evidence recorded in `## Coordination Cues`.
- Current quality inventory refresh through `quality` before selecting the
  first target.
- Focused `pytest` for touched helpers, validators, scripts, or skill-surface
  tests.
- `python3 scripts/check_python_lengths.py --paths <touched python files>` for
  Python edits, plus repo-native lint/format checks where available.
- For skill changes, run the narrow skill metadata/ergonomics/public-spec gates
  that own the touched surface.

### High-Confidence Checks

- `python3 scripts/check_changed_surfaces.py --repo-root .` before committing
  meaningful repo work.
- Broader `./scripts/run-quality.sh --read-only` or a documented substitute at
  final closeout when standing quality, skill contracts, generated exports, or
  validators changed.
- Fresh-eye critique for non-trivial bug fixes, skill contract changes, support
  skill changes, generated export changes, validation behavior changes, or test
  proof demotion.
- If tests are added or expanded, include a cheap duplicate/test-pressure sample
  in the slice log.

### External Or Live Proof

- No external, provider, live, release, or installed-host proof is planned for
  this goal. If a selected fix requires one of those proof levels, stop, record
  the proof gap, and ask before proceeding.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Refresh current quality, bug, and skill-health posture. | The target should come from current repo evidence, not stale memory. | quality routing, current gate/inventory summary, selected target rationale. | completed |
| 2 | Fix the highest-value reproducible bug or quality weakness. | Bug fixes need root cause and focused proof before broader refactoring. | root cause, focused tests before/after or equivalent proof, changed-surface check. | completed |
| 3 | Improve one skill-health surface if current evidence supports it. | The user explicitly included skill health; it should be considered as a first-class target. | skill metadata/ergonomics/public-spec/export proof, synced surfaces if touched. | completed |
| 4 | Use remaining time for the next safe quality improvement. | The timebox should keep producing value when earlier slices close cleanly. | focused tests, critique if non-trivial, committed diff. | completed |
| 5 | Trim mutation score helper length pressure. | After Slice 4, this was the remaining near-limit production script with focused tests. | mutation tests, workflow validators, plugin sync, fresh-eye review. | completed |
| 6 | Finalize and close out. | The goal needs honest proof, complete artifact evidence, retro dispositions, and commits. | final broad/substitute proof, complete goal artifact, retro/disposition evidence, clean tree or explicit non-claim. | planned |

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

Routing: find-skills session bootstrap completed in read-only mode; no support
route auto-matched the prose request. The named lifecycle route is `achieve`;
activation should ask `quality` for the current gate and skill-health posture
before selecting the first target.
Gather: n/a — no external URLs, Slack, Notion, Docs, Drive, or other external
source is being used as working context.
Release: n/a — this goal must not bump versions, publish, or edit install
manifests unless the user changes scope.
Issue closeout: #299 selected as feature/deferred quality work; carrier is
direct-commit with `Close #299`; `issue_tool.py validate-closeout-draft` passed
for `charness-artifacts/issue/2026-06-05-issue-299-closeout-commit-message.md`.
Final `verify-closeout --expect-state CLOSED` is post-push and not claimed in
this local goal slice.

## Slice Log

Activation: started at 2026-06-05T07:41:49+09:00 after `--pursue-ready`
reported shaped and activation-ready. Initial routing: `find-skills`
recommended `quality` for the current gate and skill-health posture.

### Slice 1: Refresh and improve handoff skill health

- Objective: Refresh current quality, bug, and skill-health posture, then implement the first evidence-backed skill-health improvement.
- Why this approach: Broad read-only quality passed, so no failing bug was available as the first target. The actionable current weakness was handoff chunked_routing_agentic.py entering the length advisory band at 345/360 lines while mixing packet/materialization code with proposal validation.
- Commits: local commit subject `Extract handoff agentic validation`.
- What changed: Extracted agentic chunk proposal validation into skills/public/handoff/scripts/chunked_routing_agentic_validation.py and synced the plugin mirror under plugins/charness/skills/handoff/scripts/. chunked_routing_agentic.py now re-exports validate_chunk_proposal_response from the sibling module and keeps packet/materialization responsibilities local.
- Alternatives rejected: Rejected chasing skill ergonomics portable-package host-surface heuristics because inventory labels them advisory and prose-review-dependent. Rejected standing test pruning because this slice had a narrower skill-health improvement with direct headroom proof. Rejected tracked issue closeout because no issue was selected for root-cause/debug handling.
- Targeted verification: find-skills routed current validation posture to quality; ./scripts/run-quality.sh --read-only passed 71/71 in 42.8s; runtime summary showed check-coverage 44.7s latest / 42.3s median under 45.0s and pytest 17.3s latest / 27.7s median under 140.0s; standing test economics reported 244 test files and 107 nested CLI files; inventory_skill_ergonomics reported heuristic findings with prose review still required; pytest -q tests/test_handoff_chunker_agentic_packages.py passed 14 in 2.40s; ruff touched files passed; py_compile touched source/plugin files and all public/support skill scripts passed; check_python_lengths headroom improved chunked_routing_agentic.py from 345/360 to 157/360 and new validation module is 210/360; validate_packaging, validate_packaging_committed, validate_skills, check_skill_ownership_overlap, validate_public_skill_validation, validate_public_skill_dogfood, check_doc_links, check_command_docs, check-markdown, and check-secrets passed. Cautilus planner reported required=false, next_action=none, changed_public_skills=handoff; `suggest_public_skill_dogfood.py --skill-id handoff --json` showed the current handoff consumer contract is already frozen in docs/public-skill-dogfood.json; evals/cautilus/scenarios.json lists `handoff-adapter-bootstrap` for handoff, and this extraction did not change routing/bootstrap or prompt semantics, so no scenario mutation or Cautilus run is claimed. `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest --ack-cautilus-skill-review` passed after running plugin sync, packaging, doc, command-doc, markdown, secrets, skill validation, compile, ownership, public-skill validation/dogfood, and agent-browser runtime guard checks.
- Test duplication pressure: no tests were added or expanded; no duplicate-pressure sample required.
- Critique: Fresh-eye reviewer Kierkegaard reported no blocking findings. It confirmed chunked_routing_lib still re-exports the public API, validation flow and merge_policy_facts did not drift, materialization still works, plugin mirror files are byte-identical, and the extraction genuinely improves script health. Non-blocking note to sync the goal artifact was applied by this slice log.
- Off-goal findings: No tracked issue selected or closed. Nose inventory in run-quality skipped because nose was not on PATH for the standing gate; this is not treated as a bug in this slice.
- Lessons carried forward: For skill-health goals, prefer measured headroom and focused behavior tests over heuristic-only prose findings. Keep broad pytest for closeout or changed broad surfaces, not every pre-lock slice.
- Metrics: Activation 2026-06-05T07:41:49+09:00; first broad read-only gate 42.8s; focused handoff agentic package pytest 2.40s; no tests added, so no duplicate-pressure sample required.

### Slice 2: Issue 299 release-only sentinel inventory

- Objective: Resolve #299 by adding an advisory quality inventory for release-only test sentinel coverage.
- Why this approach: #299 is the only current open quality/test-economics issue and directly follows the first slice's quality evidence. It is feature/deferred-work class, not a bug, so a resolution brief and critique are the right issue flow.
- Commits: local commit subject `Report release-only sentinel coverage`.
- What changed: Added skills/public/quality/scripts/inventory_release_only_sentinels.py, focused tests in tests/quality_gates/test_release_only_sentinel_inventory.py, inventory-dispatch discoverability, quality dogfood evidence, plugin mirror sync, critique artifact, and a verified direct-commit closeout draft for #299.
- Alternatives rejected: Rejected making the inventory a blocking gate because the signal is intentionally advisory and default all-test scanning can be noisy. Rejected live Cautilus because the planner returned required=false and next_action=none. Rejected leaving marker/async robustness as deferred after reviewers raised them because structural marker parsing and async test counting were cheap to apply.
- Targeted verification: find-skills routed #299 resolution to issue and quality; issue_tool preflight selected gh and resolve-invocation targeted corca-ai/charness#299; feature resolution brief had no open decisions. Focused pytest for test_release_only_sentinel_inventory.py passed 4 in 2.38s; selected inventory output for test_release_publish.py and test_release_publish_real_host_delta.py reported release_only=19, standing=8, standing sentinels=8, findings=[]; ruff, py_compile, check_python_lengths, validate_cautilus_proof, validate_packaging, validate_packaging_committed, validate_skills, check_skill_ownership_overlap, validate_public_skill_validation, validate_public_skill_dogfood, check_doc_links, check_command_docs, check-markdown, check-secrets, validate_attention_state_visibility, and run_slice_closeout --skip-broad-pytest --ack-cautilus-skill-review passed. issue_tool validate-closeout-draft passed for direct-commit Close #299 with classification feature and critique binding.
- Test duplication pressure: Added four focused tests in one new quality_gates module; no broad duplicate-pressure gate was run for this pre-lock slice. Final broad closeout should classify any suite pressure separately.
- Critique: Fresh-eye critique artifact: charness-artifacts/critique/2026-06-05-issue-299-release-only-sentinel-inventory.md. Two angle reviewers and one counterweight found no Act Before Ship issues. Bundle items applied: selected-file closeout output, Cautilus non-run proof, --path dispatch warning. Valid-defer robustness items were applied before commit: structural marker parsing and AsyncFunctionDef support.
- Off-goal findings: No external source or release proof. #299 will be carried by direct commit with Close #299; final GitHub CLOSED verification is post-push and is not claimed locally.
- Lessons carried forward: Advisory inventories should make selected-file mode explicit when default broad scans are intentionally noisy. Cheap robustness concerns from critique should be applied before commit when they reduce future gate-promotion risk without expanding scope.
- Metrics: Focused pytest 2.38s; selected inventory command returned immediately; slice closeout rehearsal 14.6s.

### Slice 4: Extract setup fresh-eye policy detection

- Objective: Reduce setup inspection helper length pressure while preserving the
  AGENTS.md fresh-eye/subagent delegation policy detector.
- Why this approach: `scripts/setup_agent_docs_lib.py` was in the advisory length
  band at 435 lines and carried a cohesive fresh-eye policy subdomain alongside
  agent-doc, retro-memory, artifact-policy, skill-routing, and adapter
  normalization. Extracting that subdomain improves skill-health maintainability
  without changing the public inspect payload shape.
- Commits: local slice subject `Extract setup fresh-eye policy detection`.
- What changed: Added `scripts/setup_agent_docs_fresh_eye_lib.py` for fresh-eye
  constants, compact contract detection, policy gap calculation, and
  normalization findings. `scripts/setup_agent_docs_lib.py` now imports that
  helper and still owns the overall `detect_agent_docs` payload. Synced plugin
  mirror files under `plugins/charness/scripts/`. While running the required
  markdown surface gate for this goal artifact update, also converted three
  existing backticked script references in
  `docs/conventions/implementation-discipline.md` to markdown links so
  `check_doc_links.py` can pass.
- Alternatives rejected: Rejected trimming `scripts/check_mutation_score.py`
  first because setup policy tests directly cover the selected behavior and the
  fresh-eye detector is a clearer cohesive extraction. Rejected changing
  AGENTS.md policy wording because this slice is a behavior-preserving refactor,
  not a policy change.
- Targeted verification: `pytest -q tests/quality_gates/test_setup_inspect_policy.py`
  passed 31 tests; the broader setup inspect trio
  `tests/quality_gates/test_setup_inspect_policy.py
  tests/quality_gates/test_setup_inspect_adapters.py
  tests/quality_gates/test_setup_source_guard_scan.py` passed 44 tests. `ruff
  check` passed for touched setup files, then full `ruff check charness scripts
  tests skills/public/*/scripts skills/support/*/scripts` passed. `python3 -m
  py_compile scripts/*.py plugins/charness/scripts/*.py` passed.
  `check_python_lengths --paths` passed for the old and new files, and full
  `check_python_lengths --require-git-file-listing` now leaves only two advisory
  warnings (`scripts/check_mutation_score.py` and
  `tests/quality_gates/test_release_publish.py`), so the previous
  `setup_agent_docs_lib.py` warning is resolved. `check_changed_surfaces` routed
  the change through plugin export plus integrations/control-plane checks;
  `sync_root_plugin_manifests`, `validate_packaging`,
  `validate_packaging_committed`, `validate_integrations`, `sync_support --json`,
  `update_tools --json`, `check_export_safe_imports`, `check_plugin_import_smoke`,
  `check_doc_links`, `check_command_docs`, `check-markdown`, `git diff --check`,
  and `run_slice_closeout --skip-broad-pytest --ack-cautilus-skill-review`
  passed. Cautilus planner reported
  required=false, next_action=none, and must_ask_before_running=true; no
  evaluator run is claimed.
- Test duplication pressure: no tests were added or expanded; no
  duplicate-pressure sample required.
- Critique: Fresh-eye reviewer Leibniz reported no blocking findings. It checked
  behavior preservation for fresh-eye/subagent delegation detection and
  policy-source recommendations, plugin mirror consistency, and validator
  coverage. Residual risk was only that both new helper files must be included in
  the commit.
- Off-goal findings: No release, live, provider, or GitHub closed-state proof was
  attempted. #299 remains locally carrier-verified only until the branch is
  pushed.
- Lessons carried forward: Cohesive policy detector extraction is a good
  skill-health slice when it removes length pressure and is protected by
  payload-level tests. Parent-run import smoke is worth adding after plugin mirror
  refactors even when packaging validation passes.
- Metrics: setup policy pytest 5.11s; broader setup inspect trio 6.35s; slice
  closeout 8.9s.

### Slice 5: Extract mutation score summary rendering

- Objective: Reduce production mutation score script length pressure while
  preserving mutation metrics, partial-run blocking labels, survived-mutant
  detail rendering, and CLI summary output behavior.
- Why this approach: After Slice 4, `scripts/check_mutation_score.py` was the
  only remaining production script in the advisory length band at 438 lines. Its
  summary rendering and survived-mutant detail logic formed a cohesive helper
  domain with direct focused tests.
- Commits: local slice subject `Extract mutation score summary rendering`.
- What changed: Added `scripts/check_mutation_score_summary_lib.py` for survived
  mutant details, blocking label rendering, and summary line construction.
  `scripts/check_mutation_score.py` keeps parsing, metrics, config, timeout, and
  CLI orchestration, and assigns the moved helper names back onto the original
  module so existing direct imports and star-import behavior remain compatible.
  Updated the quality attention-state visibility declaration because the
  `Skipped:` summary evidence moved into the new helper. Synced plugin mirror
  files under `plugins/charness/scripts/` and
  `plugins/charness/skills/quality/references/`.
- Alternatives rejected: Rejected editing the large release publish test first
  because it is a test-only file with broader release-fixture coupling, while the
  mutation score script had focused tests and production workflow validators.
  Rejected adding `__all__` as the re-export mechanism after fresh-eye review
  noted it would narrow `from scripts.check_mutation_score import *`; replaced it
  with explicit module-name assignments.
- Targeted verification: `pytest -q
  tests/quality_gates/test_check_mutation_score_partial.py
  tests/quality_gates/test_quality_mutation_score_validity.py
  tests/quality_gates/test_quality_mutation_testing.py` passed 69 tests. `python3
  -m pytest -q tests/quality_gates/test_quality_mutation_testing.py` passed 39
  tests for the changed-surface workflow gate. `ruff check` passed for touched
  mutation files and focused tests, then full `ruff check charness scripts tests
  skills/public/*/scripts skills/support/*/scripts` passed. `python3 -m
  py_compile` passed for root/plugin mutation files. `check_python_lengths
  --paths` passed for the old and new files; full `check_python_lengths
  --require-git-file-listing` now leaves only the release publish test advisory
  warning. `check_changed_surfaces` routed the change through plugin export,
  mutation-testing workflow, skill package/public-skill policy, attention-state
  visibility, and integrations/control-plane checks;
  `sync_root_plugin_manifests`, `validate_packaging`,
  `validate_packaging_committed`, `check_github_actions`, `validate_adapters`,
  `validate_attention_state_visibility`, `validate_skills`,
  `check_skill_ownership_overlap`, `validate_public_skill_validation`,
  `validate_public_skill_dogfood`, `validate_integrations`, `sync_support
  --json`, `update_tools --json`, `check_export_safe_imports`,
  `check_plugin_import_smoke`, `check_doc_links`, `check_command_docs`,
  `check-markdown`, `check-secrets`, and `run_slice_closeout
  --skip-broad-pytest --ack-cautilus-skill-review` passed. After the pre-commit
  attention-state gate caught the moved `Skipped:` evidence, the manifest was
  updated and revalidated sequentially post-sync.
  `suggest_public_skill_dogfood.py --skill-id quality --json` showed the current
  quality consumer contract remains hitl-recommended and already covered by the
  checked-in dogfood registry.
- Test duplication pressure: no tests were added or expanded; no
  duplicate-pressure sample required.
- Critique: Fresh-eye reviewer Lagrange reported no blocking findings. It
  confirmed behavior preservation for mutation metrics, summary rendering,
  survived-mutant details, partial-run labels, public named imports, and plugin
  mirror consistency. The one compatibility concern about adding `__all__` was
  applied before commit by removing `__all__`.
- Off-goal findings: No live Cosmic Ray run, provider proof, release proof, or
  installed-host proof was attempted. This slice preserves local deterministic
  mutation summary behavior only.
- Lessons carried forward: Re-export compatibility is broader than named-import
  tests; avoid `__all__` in extraction refactors unless the original module
  already had it.
- Metrics: focused mutation pytest 4.27s; mutation workflow pytest 3.08s; slice
  closeout 13.8s.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request on 2026-06-05: `$charness:achieve` for three hours of code
  quality improvement and bug fixing, later clarified to include skill health.
- `docs/handoff.md`: recent completed work, current pickup guidance, and known
  follow-up issues (#295 and #296) are context, not automatic closeout targets.
- `charness-artifacts/quality/latest.md`: current quality posture includes
  healthy skill ergonomics from the prior review, rising standing test
  economics, and runtime hot spots around coverage/duplicate checks.
- Existing completed goal
  `charness-artifacts/goals/2026-06-05-3h-quality-test-economics.md` was read
  and not reused because it is complete and narrower than this request.
- `find-skills` read-only bootstrap and recommendation probes were run for this
  task; no canonical inventory artifact was rewritten.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode: chose implementation-continuation after explicit `/goal` activation.
  Rejected artifact-only because the user asked to spend three hours improving
  code quality and bugs, not only to draft a plan. This does not auto-execute;
  `/goal` remains the activation boundary.
- Timebox: chose three hours because the user requested it. Activation time was
  recorded at `/goal` activation so final closeout can enforce the reserve
  window.
- Closeout reserve: chose the skill default of 20 minutes. Rejected using the
  whole three hours for implementation because timeboxed goals need proof,
  artifact update, critique, commit, and user closeout.
- Scope: included skill health because the user clarified it. Rejected making
  skill health the only target because the original request also named code
  quality and bug fixing.
- Bug source: choose reproducible local evidence first. Rejected speculative bug
  hunting because fixes without reproduction cannot produce strong closeout
  proof.
- Issue closeout: no tracked issue is selected at shaping time. If activation
  selects one, closeout must route through `issue` rather than relying on prose.
- Proof level: local deterministic proof is the planned level. Rejected live,
  provider, installed-host, and release proof unless a selected slice actually
  requires it.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Same-agent Before-phase critique: a broad "quality and bugs" goal can sprawl.
  Folded into Slice 1 evidence-first target selection and stop conditions.
- Same-agent Before-phase critique: skill health can accidentally mutate public
  contracts or generated exports without sync. Folded into Boundaries and
  High-Confidence Checks.
- Same-agent Before-phase critique: bug fixing without a reproduced failure
  creates weak final proof. Folded into target selection and verification plan.
- Over-worry not folded: forcing a tracked GitHub issue target now would overfit
  the goal. The artifact keeps issue closeout pending and lets activation pick
  from current evidence.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

None yet.

## Final Verification

Not run. The goal is draft and inactive.

## User Verification Instructions

After activation and completion, inspect the final commits, rerun the focused
checks and final broad/substitute proof named here, and compare any skill-health
changes against the synced public/support/plugin surfaces.

## Auto-Retro

Not run. The goal is draft and inactive.
