# Achieve Goal: Portable skill contract quality and routing discipline

Status: complete
Created: 2026-06-04
Activation: `/goal @charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete - final closeout recorded.
- Next action: n/a - goal complete. Deferred follow-ups are tracked as #295
  (closeout test-selection cost) and #296 (bounded reviewer cost/tier
  visibility); `host_surface_reference=104` remains advisory evidence, not a
  blocking portability violation.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Make Charness public/support skills portable and easier to operate by improving
skill text quality as a first-class contract: remove repo-local history leakage
and other non-portable wording from skill packages, strengthen detection so
future full-surface quality passes catch conceptual/text-quality regressions
before humans do, and tighten `achieve` coordination so implementation/debug
work routes through the owning skills instead of being absorbed by the goal
operator.

The goal starts from the RCA in
`charness-artifacts/debug/2026-06-04-portable-skill-contract-quality-and-routing.md`:
the previous long goal mostly used `achieve` correctly as a scratchpad, but it
did not explicitly invoke `impl` for implementation slices or `debug` for the
fresh-eye blocker; the portable skill surface also still contains concrete
repo-local issue anchors and broader skill-text quality smells after recent
broad skill quality review.

## Non-Goals

- Do not resolve unrelated open product or mutation work in this goal unless a
  validator added here directly exposes the same invariant failure.
- Do not remove issue-number syntax from user-facing issue workflows where it is
  the actual domain object. Generic placeholders such as `#N` or synthetic
  fixture issue numbers are allowed when the surrounding example is portable and
  not tied to `corca-ai/charness`.
- Do not preserve historical rationale, repo-local chronology, overfull
  reference sprawl, or exact incident wording in portable skill packages merely
  because it explains how a rule originated. If history is still useful, move it
  to a repo-local artifact or convert it into invariant-first wording.
- Do not claim installed-host cleanup until the plugin/export propagation path is
  synced and verified.

## Boundaries

- Scope covers `skills/public/`, `skills/support/`, their checked-in plugin
  mirrors, skill validators, quality inventories, handoff/achieve coordination
  contracts, and durable artifacts needed to prove the change.
- Portable skill text quality covers at least: concrete repo issue anchors,
  repo-local chronology, stale incident rationale, hidden host assumptions,
  missing reference/index discoverability, duplicated workflow instructions,
  SKILL.md core overfill, exact-prose source guards, and unclear ownership
  between public skill, references, scripts, adapters, and quality gates.
- Concrete repo issue anchors are one disallowed subtype: examples include
  `#123`, `issue-123`, `issues/123`, and `corca-ai/charness#123` when they name
  real Charness history rather than a generic placeholder.
- Portable skill source may describe issue workflows, close keywords, and
  issue-number parameters, but examples must use placeholders or synthetic
  adapter fixtures that cannot be mistaken for Charness project history.
- `achieve` remains a goal operator. During pursuit it should use `find-skills`
  to decide the owning skill at real phase boundaries, not carry a hard-coded
  exhaustive skill map. Add short anchors only where this RCA proves the boundary
  is easy to miss, especially implementation -> `impl` and bug/RCA work ->
  `debug`.
- Prefer validators and inventories over prose-only policy. Any manual exception
  must be machine-readable, narrow, and reviewed during closeout.
- Preserve generated-surface discipline: mutate source, sync plugin mirrors,
  verify, then publish/commit.

## User Acceptance

- A user can run one documented quality command and see a skill text quality
  report that covers portability, issue-anchor leakage, reference
  discoverability, core overfill, repeated prose ritual, host-assumption leakage,
  and exact-prose/source-guard risk.
- That report shows zero unapproved concrete Charness issue anchors under
  portable skill packages.
- `achieve` documentation and validator output make clear that `achieve`
  coordinates `impl`/`debug`/`quality`/`issue` instead of replacing them, and a
  long goal missing required phase evidence is flagged before completion.
- `quality` reports this as a portable-skill text quality concern with explicit
  human-review status, not as a hidden human-only judgment or a misleading "no
  issues" summary when heuristics are merely incomplete.
- `skills/public/achieve/SKILL.md` links to a discoverable reference/index path
  without dropping important references due to line-budget pressure.
- Existing issue, handoff, release, and quality tests still pass after examples
  are generalized.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch` and `git log --oneline origin/main..HEAD`.
- `find-skills --recommend-for-task` before each phase boundary.
- Baseline inventories: issue-anchor scan, `inventory_skill_ergonomics.py
  --json`, skill-surface preflight on overfull skills, reference-link inventory,
  and any existing brittle-source/prose-guard inventory.
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --path <changed-skill-surface> --preview-delta <planned-lines>` before public skill prose edits.
- Focused tests for any new inventory/validator plus touched skill helper tests.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after each mutation.

### High-Confidence Checks

- Add or extend a portable skill text-quality inventory/gate with subchecks for
  issue anchors, repo-local chronology/history leakage, reference
  discoverability, SKILL.md overfill, duplicated prose ritual, host assumptions,
  and exact-prose/source-guard risk.
- Add quality-consumption coverage proving each text-quality subcheck is surfaced
  when skills are in scope and cannot be summarized away as "no issue."
- Add achieve goal-artifact validation coverage for routing-cue binding so
  easy-to-miss implementation/debug slices cannot silently remain
  `achieve`-only, without turning the artifact into an exhaustive phase-to-skill
  map.
- Add focused regression tests for `achieve` references/index discoverability and
  SKILL.md headroom behavior if the solution changes reference structure.
- Run `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  at slice boundaries and the locked broad gate before final closeout.

### External Or Live Proof

- No external source gathering is expected unless the next session consults live
  GitHub issue bodies for historical migration decisions; if it does, route that
  through `gather`.
- No release proof is expected unless the change modifies release surfaces.
- Installed-host proof is optional; if skipped, record it as a non-claim and
  rely on plugin mirror/package validators for local closeout.

Discuss before activation: resolved by the user's 2026-06-04 instruction that
all Charness skills must be portable and real issue-number anchors must not
appear in portable skills. The remaining discretion is implementation shape:
whether the first shipped gate is advisory or blocking may be decided during
Slice 2 after baseline counts and false-positive review.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Baseline RCA and skill text-quality inventory | Avoid cleaning only `achieve` or only issue anchors while sibling text-quality smells remain | Debug artifact, issue-anchor counts, ergonomics payload, candidate taxonomy, routing proof | complete |
| 2 | Define and implement the portable skill text-quality detector | Prevention needs a validator bundle, not another prose warning | Inventory/gate script, subcheck schema, allowlist/exception model, tests, quality consumption | complete |
| 3 | Generalize portable skill packages away from repo-local/history-coupled prose | Remove current violations and reduce historical/text-quality coupling | Updated skill docs/scripts/examples, plugin mirror sync, doc/link tests | complete |
| 4 | Tighten `achieve` routing and phase-evidence contract | Stop `achieve` from absorbing `impl`/`debug` responsibilities without hard-coding every skill | Goal validator/docs/tests proving routing evidence or explicit opt-out | complete |
| 5 | Skill discoverability/readability cleanup for `achieve` | Fix missing-link/headroom/reference-index quality at the root surface | Reference/index structure, SKILL.md headroom, link validation, focused tests | complete |
| 6 | Broad verify, critique, retro, and handoff closeout | Prove the new prevention/response loop and leave non-claims clear | Locked broad gate, fresh-eye critique, retro dispositions, handoff update | complete |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) - never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** - ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** - when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a - <reason>` when no external context
  applies.
- **Release step** - when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a - <reason>`.
- **Issue closeout step** - when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a - <reason>`.

Routing: Before-phase shaping used `find-skills` read-only recommendation and
selected `achieve` for the goal artifact, `debug` for RCA, `handoff` for the
next-session baton, and `quality`/`impl` as required pursuit-phase routes.
Activation routing on 2026-06-04 used `find-skills --recommend-for-task
"continue active goal ...portable-skill-contract-quality-and-routing.md"` and
selected `quality` for Slice 1 because the immediate work is a portable skill
text-quality baseline and gate-design pass. Slice 5 routing used `find-skills
--recommend-for-task "continue active goal ... Slice 5 skill
discoverability/readability cleanup for achieve"` and selected `achieve` for
goal lifecycle plus `quality` for reference-discoverability validation; the
implementation stayed repo-local and synced plugin mirrors before validators.
Routing: `find-skills` recommended `impl` for implementation-shaped mutation
work; implementation slices used repo-local source changes with generated mirror
sync before validators.
Routing: `find-skills` recommended `debug` for the RCA source that shaped this
goal; the debug artifact remained the causal source while this goal pursued the
quality/routing fixes.
Routing: `find-skills` recommended `quality` for portable skill text-quality,
validation, and final closeout proof; quality inventories and gates own the
portable skill report.
Gather: n/a - this goal was shaped from local repo artifacts and the user's
in-thread portability requirement, not an external URL.
Release: n/a - no release surface is planned.
Issue closeout: n/a - this is a repo-quality goal not currently bound to a
tracked issue closeout carrier.

## Slice Log

### Before-phase shaping: RCA and goal contract

- Objective: Turn the user's portability/routing concerns and this session's
  waste into a reviewable next-session goal.
- What changed: Created this draft goal and the RCA artifact
  `charness-artifacts/debug/2026-06-04-portable-skill-contract-quality-and-routing.md`.
- Evidence: `find-skills` recommended `achieve`, `debug`, `handoff`, `impl`,
  `issue`, and `quality` for the task. `rg` found 106 concrete issue-anchor
  candidates under `skills/public` and `skills/support`; `achieve` SKILL.md is
  at 160/160 core non-empty lines and 190/200 total lines. The user clarified
  that issue anchors are a symptom of broader skill text quality, so the goal
  scope was widened before activation.
- Non-claims: No skill package cleanup or text-quality validator has been
  implemented yet.

### Slice 1: Slice 1: portable skill text-quality detector baseline

- Objective: Establish a package-wide portable skill issue-anchor detector baseline and wire the first quality-gate surface without enabling the stricter current-corpus rule before cleanup.
- Why this approach: The prior inventory reported zero findings because it only checked public SKILL.md core; a package-level inventory gives Slice 3 concrete cleanup targets while the opt-in gate stays available for post-cleanup enforcement.
- Commits:
- What changed: Activated the goal artifact; extended inventory_skill_ergonomics.py to emit package_issue_anchor_count and line-level package_issue_anchor_findings for public/support skill packages; added valid opt-in rule portable_package_issue_anchor with explicit public/support applicability; kept the rule out of default/generated adapter rules; documented the inventory/gate field and synced plugin mirrors.
- Alternatives rejected: Rejected enabling portable_package_issue_anchor in the current repo adapter before cleanup because the corrected baseline still has 102 findings. Rejected counting generic defaults_version issue-* fields or .../issues/123 placeholders as concrete history leakage after fresh-eye review.
- Targeted verification: Focused pytest passed: tests/quality_gates/test_quality_skill_ergonomics.py, test_skill_ergonomics_gate.py, test_quality_bootstrap.py, test_profile_and_preset_validation.py (63 tests). Corrected inventory baseline: checked_skill_count=23, heuristic_finding_count=10, package_issue_anchor_count=102. validate_skill_ergonomics --json passed with existing adapter rules and no violations; package counts are visible in checked_skills. validate_inventory_consumption_declaration and check_inventory_declaration_coverage passed after stable sync. run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review completed; broad pytest intentionally skipped for slice rehearsal.
- Test duplication pressure: New coverage adds focused cases for whole-package public/support findings, defaults_version and .../issues/123 false-positive skips, runtime-install package count suppression, support-skill package rule enforcement, and public-only applicability for older rules.
- Critique: Fresh-eye parent-delegated critique executed by subagent 019e90b4-143c-7cb3-8da8-6d9bbac73a0f. Act-before-ship findings were applied: removed the new rule from defaults/example adapter, narrowed placeholder/version false positives, made rule applicability explicit, suppressed runtime-install counts, included findings in gate payloads, updated stale review prompt, and removed unsupported reviewed-exception wording. Valid-but-defer: vendor subdirectories in support skills and two-digit anchor ambiguity.
- Off-goal findings: None.
- Lessons carried forward: Do not call a baseline concrete until false-positive taxonomy is reviewed; gate valid-rule vocabulary and default-generated enforcement are separate policy surfaces.
- Metrics:

### Slice 2: portable skill text-quality detector

- Objective: Define and ship the broader portable skill text-quality detector bundle beyond package issue anchors.
- Why this approach: The Slice 1 baseline proved the old core-only inventory missed package-level leakage; this slice moves detection into reusable subchecks while keeping noisy current-corpus rules opt-in until cleanup.
- Commits:
- What changed: Added skill_text_quality_lib.py and extended inventory_skill_ergonomics.py with package-level issue-anchor, dated-incident, host-surface-reference, and reference-discoverability subchecks; added optional validator rules and payload fields for those signals; added inventory consumer fields; documented the advisory/gate contract; synced the checked-in plugin mirror.
- Alternatives rejected: Rejected enabling the new package-level gates in generated/default adapter rules because current baseline still has 102 package issue anchors, 3 dated incidents, and 104 high-recall host-surface references. Rejected shipping the host signal as portable_package_host_assumption after fresh-eye review because many hits are legitimate host-plural seams; renamed it to portable_package_host_surface_reference.
- Targeted verification: Focused pytest passed: tests/quality_gates/test_quality_skill_ergonomics.py, test_skill_ergonomics_gate.py, test_quality_bootstrap.py, test_profile_and_preset_validation.py, test_inventory_consumption.py (77 tests). Inventory baseline after fixes: checked_skill_count=23, heuristic_finding_count=29, package_issue_anchor_count=102, subcheck_counts={core_overfill:0, mode_option_pressure:0, prose_ritual:0, path_ambiguity:0, package_issue_anchor:102, package_dated_incident:3, host_surface_reference:104, reference_discoverability:0}. validate_skill_ergonomics --json passed with existing adapter rules and 0 violations; inventory declaration and coverage validators passed; check_python_lengths passed with unrelated advisory warnings; run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review completed after final sync.
- Test duplication pressure: New tests cover package dated incidents, host-surface reference payloads, reference discoverability, __pycache__ false-positive suppression, opt-in gate failure payloads, and checked_skill field exposure for the new subchecks.
- Critique: Fresh-eye parent-delegated critique executed by subagent 019e90c3-574b-7143-8adf-e31c39c57544. Act-before-ship findings were applied: reference discoverability now ignores cache/non-text files and has a regression test; the host signal was renamed/reframed as host_surface_reference; run_slice_closeout was rerun after final sync. Bundle-anyway requests applied: package_dated_incident_count declared, review prompts updated, checked_skills includes new finding lists. Valid-but-defer: cleaning 102 issue anchors and 3 dated incidents, plus richer host-surface exception modeling.
- Off-goal findings: None.
- Lessons carried forward: High-recall text-quality heuristics need names that describe evidence, not verdicts. Local generated/cache files must be excluded from package-discoverability inventories before baselines are treated as meaningful.
- Metrics: package_issue_anchor=102; package_dated_incident=3; host_surface_reference=104; reference_discoverability=0; closeout_usage_episode=slice-closeout-abca6310dc454bba9d0cb38bd009f037

### Slice 3: portable skill package cleanup and blocking rules

- Objective: Generalize portable public/support skill packages away from concrete issue anchors and dated incident wording, then promote the clean package issue/date checks to blocking enforcement.
- Why this approach: Slice 2 proved the package-level detector and showed the current issue/date baseline was finite and objective. Cleaning those findings now lets future quality runs fail on the same leakage instead of treating it as advisory prose review.
- Commits:
- What changed: Removed concrete issue-number anchors, issue URLs, and dated incident wording from public/support skill references, script comments, docstrings, diagnostic strings, and examples while preserving stable behavioral contracts; promoted portable_package_issue_anchor and portable_package_dated_incident into DEFAULT_SKILL_ERGONOMICS_GATE_RULES and .agents/quality-adapter.yaml; updated the quality adapter example and adapter contract to separate default blocking rules from valid opt-in review rules; synced plugin mirrors.
- Alternatives rejected: Rejected enabling portable_package_host_surface_reference as blocking because the remaining 104 findings are mostly legitimate host-surface seams and need a narrower exception/modeling slice. Rejected mutating evals/cautilus/scenarios.json because plan_cautilus_proof reported next_action=none and the slice is a preserve/provenance cleanup, not a routing or behavior-improvement claim.
- Targeted verification: Inventory after cleanup: checked_skill_count=23, subcheck_counts={package_issue_anchor:0, package_dated_incident:0, host_surface_reference:104, reference_discoverability:0, core_overfill:0, mode_option_pressure:0, prose_ritual:0, path_ambiguity:0}. validate_skill_ergonomics passed with portable_package_dated_incident and portable_package_issue_anchor active and 0 violations. Focused tests passed: quality/bootstrap/ergonomics set 77 before promotion and 66 after reviewer fixes; achieve goal helper set 74 after heading guard repair; handoff chunker set 61; quality mutation testing passed in slice closeout. validate_adapters, check_github_actions, inventory declaration/coverage, py_compile, ruff, check_python_lengths, git diff --check, plugin mirror scan, and run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review all passed after final sync. run_slice_closeout final usage episode: slice-closeout-bce1af8df512436cb5ba5761ccbec2cf.
- Test duplication pressure: No new tests were needed for the prose cleanup because existing exact-heading, handoff, goal-artifact, adapter, and skill-ergonomics tests covered the affected semantics. One test failure caught accidental heading-case drift and was fixed by preserving the expected heading phrases without numeric anchors.
- Critique: Fresh-eye parent-delegated critique executed by subagent 019e90d2-efbf-7c32-b8b8-2d8c09827474. Act-before-ship findings were applied: quality adapter example now includes the promoted package rules; adapter-contract now separates default blocking rules from valid opt-in review rules. Bundle-anyway indentation cleanups in handoff scripts were applied. Valid-but-defer: host_surface_reference remains a real follow-up but not a blocker for this issue/date cleanup.
- Off-goal findings: None.
- Lessons carried forward: Do not stop at a clean source inventory when shipped examples and adapter docs still describe the pre-promotion contract. Preserve exact behavior-test phrases while removing numeric provenance anchors.
- Metrics: package_issue_anchor=0; package_dated_incident=0; host_surface_reference=104; reference_discoverability=0; active_blocking_rules+=portable_package_issue_anchor,portable_package_dated_incident; Cautilus scenario review=preserve/no scenario registry mutation

### Slice 4: phase-routing closeout floor

- Objective: Add an achieve closeout guard so recorded implementation/debug/quality/issue phase work cannot remain achieve-only without routing evidence.
- Why this approach: The RCA showed long goals can use achieve as a scratchpad while skipping the owning implementation/debug skills; a presence-only closeout floor gives the cue deterministic teeth without hard-coding a phase-to-skill router.
- Commits:
- What changed: Added goal_artifact_phase_routing.py and wired it into achieve complete-evidence checks; updated achieve template, lifecycle, coordination reference, SKILL.md checklist, prescribed closeout contract, plugin mirror, and public-skill dogfood scenario review; adjusted stale tests that still asserted deleted issue anchors or live handoff backlog state.
- Alternatives rejected: Rejected semantic route-quality classification and an exhaustive phase-to-skill map. Rejected using bare 'regression' as a debug cue after fresh-eye review showed quality-only 'regression suite passed' false positives.
- Targeted verification: Focused tests passed: goal/artifact and routing set 116 tests before review; post-review focused set 63 tests. Broad pytest passed: 2153 passed, 4 skipped. run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review passed after dogfood review. Required validators passed: validate_skills, packaging, packaging_committed, doc links, command docs, markdown, secrets, cautilus proof policy, py_compile, ownership, public skill validation/dogfood, ruff, python lengths, attention visibility, browser runtime guard.
- Test duplication pressure: New coverage adds phase-route trigger tests, missing-route refusal, find-skills route satisfaction, opt-out satisfaction, recorded-work-only scoping, and regression-suite-not-debug false-positive coverage. Broad suite initially exposed stale issue-anchor assertions and a live-handoff fixture dependency; both were narrowed to stable contract assertions.
- Critique: Fresh-eye parent-delegated critique executed by subagent 019e90e9-7fd7-7862-a2e5-20119c79f777. Act-before-ship findings were applied: authoritative closeout docs now mention Routing; bare regression no longer triggers debug routing; the new phase-routing files will be staged with source and plugin mirror.
- Off-goal findings: The closeout wrapper repeated the generic achieve dogfood scenario-review follow-up; resolved in this slice by updating docs/public-skill-dogfood.json for the additive phase-routing floor.
- Lessons carried forward: Presence-only floors still need authoritative closeout docs, not only template/reference prose. Tests should assert durable contracts rather than deleted issue-number anchors or live handoff backlog contents.
- Metrics: phase_routing_rule_date=2026-06-04; closeout_usage_episode=slice-closeout-c799a010c49e4b6981fab4a726656397; broad_pytest=2153_passed_4_skipped; package_issue_anchor=0; package_dated_incident=0; host_surface_reference=104

### Slice 5: achieve reference index and headroom cleanup

- Objective: Make the `achieve` root skill surface easier to scan by replacing
  a long reference list with a discoverable reference index while preserving
  reference-discoverability validation and creating SKILL.md core headroom.
- Why this approach: Slice 3/4 left `achieve` near the core line ceiling; an
  index keeps root selection prose concise without hiding important references
  from validators or operators.
- Commits:
- What changed: Added `skills/public/achieve/references/index.md`; changed
  `skills/public/achieve/SKILL.md` to list that index and trimmed small root
  wording blocks; updated `validate_skills.py` and the quality ergonomics
  inventory so `references/index.md` list items count as discoverable reference
  listings; froze reviewed dogfood evidence for `achieve` and `quality`; synced
  plugin mirrors; added focused reference-index tests.
- Alternatives rejected: Rejected dropping important `achieve` references from
  the root without an index because that would satisfy line pressure by hiding
  operator lookup paths. Rejected broad whole-body regex matching after
  fresh-eye review showed incidental prose could mask missing list entries.
- Targeted verification: Current-diff focused tests passed:
  `tests/quality_gates/test_skill_reference_index.py` (`5 passed`) and the
  quality ergonomics/skill validation bundle (`51 passed`). Achieve preflight:
  SKILL.md total 183/200, core nonempty 156/160. Achieve inventory:
  `reference_discoverability=0`, `package_issue_anchor=0`,
  `package_dated_incident=0`, `host_surface_reference=9` (deferred
  host-surface modeling). Current-diff deterministic validators passed:
  packaging, packaging_committed, doc links, command docs, markdown, secrets,
  Cautilus proof policy, `validate_skills`, py_compile, ownership overlap,
  public skill validation/dogfood, integrations, Ruff, Python lengths, attention
  visibility, public dogfood JSON validation, and `git diff --check`. Slice
  closeout wrapper passed with broad pytest skipped. A broader selected pytest
  run before the reviewer parser tightening passed `2157 passed, 4 skipped in
  291.31s`; it was not repeated after the focused parser fix.
- Test duplication pressure: New coverage lives in
  `test_skill_reference_index.py` rather than adding more weight to already
  large quality-gate files. It covers positive index listing plus negative
  cases for references mentioned only in SKILL.md prose or index prose.
- Critique: Fresh-eye parent-delegated critique executed by subagent
  019e90fd-d5cf-71f3-a44f-36844d63fcf0. Act-before-ship findings were applied:
  only `## References` list items and index bullet list items now count as
  listings; incidental prose no longer satisfies reference inventory.
- Off-goal findings: The selected broad pytest gate costs about five minutes on
  this machine; Slice 5 treated that as evidence and left test-cost improvement
  for retro/quality follow-up rather than widening this implementation slice.
  Subagent model/cost selection was not controlled by the spawn call; the host
  surfaced a higher-cost reviewer than expected.
- Lessons carried forward: Reference-index semantics need validator and
  inventory agreement, and list-item parsing must avoid whole-document regex
  shortcuts. Small slices should prefer targeted current-diff proof and reserve
  broad pytest for final closeout or riskier semantic changes.
- Metrics: package_issue_anchor=0; package_dated_incident=0;
  host_surface_reference=9; reference_discoverability=0;
  achieve_core_nonempty=156/160; broad_pytest_pre_fix=2157_passed_4_skipped;
  current_diff_quality_gate=51_passed;
  closeout_usage_episode=slice-closeout-52ea5085e7d146aa83023b0d2f2bb2d7

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User instruction, 2026-06-04: all Charness skills must be portable; real issue
  numbers should not appear in portable skills; issue numbers are a symptom of a
  broader skill text quality problem.
- `charness-artifacts/debug/2026-06-04-portable-skill-contract-quality-and-routing.md`
- `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`
- `charness-artifacts/quality/2026-06-02-workflow-review-sibling-pattern-audit.md`
- `charness-artifacts/quality/latest.md`
- `skills/public/achieve/SKILL.md`
- `skills/public/achieve/references/lifecycle.md`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Scope: chose portable skill package-wide text quality plus `achieve` routing
  discipline. Rejected `achieve`-only cleanup because the baseline scan found
  sibling symptoms outside `achieve`, and the user clarified that issue anchors
  are not the whole problem.
- Portability rule: chose "no concrete repo-local history leakage in portable
  skill packages, with issue anchors as one blocked subtype." Rejected keeping
  issue-number history in references because the user identified it as
  non-portable coupling, not just readability debt.
- Gate posture: leave advisory-vs-blocking implementation to Slice 2 after
  false-positive review. Rejected deciding it in Before-phase because some
  checks are objective enough to block while others may need reviewed advisory
  status.
- Execution posture: next session should activate this goal, then let
  `find-skills` drive the owning skill at phase boundaries. Rejected a hard-coded
  phase-to-skill table; accepted short anchors for boundaries the prior run
  missed, especially implementation -> `impl` and bug/RCA work -> `debug`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Blocker folded: a simple issue-anchor hard gate would falsely catch generic
  issue workflow examples and still miss non-anchor text-quality problems.
  Boundary now treats issue anchors as one subtype inside a broader
  text-quality inventory.
- Blocker folded: focusing only on `achieve` would miss sibling surfaces and
  focusing only on issue anchors would miss the user's actual concern; the slice
  plan starts with a package-wide text-quality taxonomy.
- Risk folded: SKILL.md line budget is already exhausted, so adding more prose
  to `achieve` is likely the wrong repair. The plan includes reference/index
  restructuring instead.
- Over-worry not folded: eliminating every historical issue reference or rough
  working note from repo-local artifacts is not required. The portability/text
  quality rule applies to portable skill packages, not `charness-artifacts/`.

## Off-Goal Findings

- Current handoff still contains tracked issue pickup details for the previous
  closeout and open backlog; this goal should not silently rewrite those unless
  the next-session first move changes.

## Final Verification

- Final locked closeout: `python3 scripts/run_slice_closeout.py --repo-root .
  --verification-lock --ack-cautilus-skill-review --paths $(git diff
  --name-only origin/main..HEAD)` passed. It synced plugin mirrors and ran
  packaging, committed packaging, doc links, command docs, markdown, secrets,
  Cautilus proof policy, skill validation, py_compile, ownership overlap, public
  skill validation/dogfood, adapter validation, mutation-testing workflow test,
  GitHub Actions checks, integrations, support/tool dry-runs, Ruff, Python
  lengths, attention-state visibility, broad pytest, and browser-runtime guard.
  Broad pytest passed inside the wrapper in 297.5s. Usage episode:
  `slice-closeout-ede1ec13dda447f38e8f3412f184ea82`.
- Final skill text-quality report: `python3
  skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root .
  --json` reported `checked_skill_count=23`, `package_issue_anchor=0`,
  `package_dated_incident=0`, `reference_discoverability=0`,
  `host_surface_reference=104`, `heuristic_finding_count=17`, and
  `prose_review_status=required`. The remaining host-surface signal is advisory
  and intentionally not promoted to a blocking rule in this goal.
- Final blocking gate: `python3
  skills/public/quality/scripts/validate_skill_ergonomics.py --repo-root .
  --json` returned exit 0 with 9 configured rules and no violations.
- Cautilus: `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
  returned `next_action: none` on the clean post-commit tree; no live Cautilus
  run was performed. Scenario-review decisions are frozen in
  `docs/public-skill-dogfood.json`; deterministic tests and dogfood validation
  own this closeout.
- Retro: session retro persisted at
  `charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md`
  and refreshed `charness-artifacts/retro/recent-lessons.md`.
- Retro: charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md
- Metrics: no goal-scoped host metric window was recorded because the required
  session-file/timestamp window was unavailable. `probe_host_logs.py --repo-root
  . --format markdown` produced thread-wide pressure only: 6 compactions, 660
  function calls, 97 custom tool calls, 14 pytest invocations, and repeated
  VCS/check commands. These are not claimed as per-goal totals.
- Host log probe: skipped: host-log-not-exposed: no goal-scoped session file and timestamp window were available, so only thread-wide pressure was reported.
- Non-claims: installed-host cleanup was not run; no release surface was touched;
  no external gather source was needed; open product/mutation work (#184, #293,
  #294) remains outside this goal.

## User Verification Instructions

To verify the closeout, run:

- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py
  --repo-root . --json`
- `python3 skills/public/quality/scripts/validate_skill_ergonomics.py
  --repo-root . --json`
- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock
  --ack-cautilus-skill-review --paths $(git diff --name-only origin/main..HEAD)`

Expected current posture: zero package issue anchors, zero package dated
incidents, zero reference-discoverability gaps, no blocking skill-ergonomics
violations, and `host_surface_reference=104` as advisory/deferred evidence.

## Auto-Retro

Session retro found two workflow improvements and both have concrete
dispositions:

- issue #295: make closeout test-selection cost explicit, separating pre-lock
  slice proof from final verification-lock broad proof.
- issue #296: expose bounded reviewer cost/tier selection in closeout evidence
  when the host, not the repo, chooses it.

Retro dispositions: issues #295 and #296 filed and body-verified through the
repo-owned issue backend. No prose-only improvement remains.

Disposition review: charness-artifacts/critique/2026-06-04-portable-skill-contract-quality-final-closeout-review.md
