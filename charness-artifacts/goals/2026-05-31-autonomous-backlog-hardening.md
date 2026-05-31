# Achieve Goal: Current autonomous hardening tranche

Status: active
Created: 2026-05-31
Activation: `/goal @charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation — after explicit `/goal` activation, the
agent should continue autonomously through this closed issue tranche, stopping
only on the named stop conditions.

## Goal

Turn the current autonomous hardening tranche from the handoff chunker into an
auditable maintenance run: harden closeout proof first, then complete the scoped
portability, process, and mutation follow-ups that do not require new product
direction.

This goal deliberately narrows "all autonomous work" to this closed tranche:

| Issue | Included Work | Stop Boundary |
| --- | --- | --- |
| #268 | Achieve closeout artifact evidence floor and issue closeout draft pre-validation | Stop before direct live GitHub mutation or host-level completion bypass that lacks a checked validator path |
| #269 | Guard achieve artifacts against stale mutable-HEAD SHA wording | Stop if the fix requires changing the meaning of commit/remote proof rather than wording and validation |
| #264 | Portability guard plus cross-skill author-repo-internal cite sweep | Stop if a cited surface needs a new portability policy beyond the issue's discriminator/allowlist |
| #270 | Bind targeted mutant proof to exact gate-reported lines before mutation | Stop if the gate cannot report a precise line/source target |
| #265/#261 | Mechanical survivor enumeration and clearly real survivor kills | Stop before equivalent-mutant or mutation-standard policy decisions |

The intended autonomous sequence is:

1. #268 — close the achieve/issue closeout integrity gap before this run creates
   more closeout state.
2. #269 — remove stale mutable-HEAD wording risk before this goal's own final
   proof writes achieve artifact evidence.
3. #264 — implement the portability guard and cross-skill author-repo-internal
   citation sweep from the #250 follow-up.
4. #270 — apply exact-line proof discipline immediately before targeted
   mutation work.
5. #265 / #261 — triage the residual coordination-cues mutation survivors only
   while the work remains evidence-driven and does not require a product or gate
   policy decision from the user.

## Non-Goals

- Do not push to GitHub, merge, publish a release, or mutate live issue state
  unless a slice's owning workflow explicitly stages a closeout comment/body for
  the maintainer to apply.
- Do not decide product-success criteria, AI/ML engineering research direction,
  or product metrics (#184/#185); those require user/product judgment.
- Do not include #258, #259, #252, #243, #241, #237, or #236 in this run unless
  a slice files a separate follow-up and the next session re-ranks them.
- Do not absorb the broad "other open" backlog as a single grab bag. File or
  defer off-goal findings instead of expanding this run until it loses shape.
- Do not run an expensive full cosmic-ray campaign unless the mutation slice
  proves the targeted survivor triage cannot be resolved with cheaper
  deterministic and targeted-kill proof.
- Do not change release surfaces unless a slice discovers a direct release
  correctness blocker; if that happens, stop and re-plan the release boundary.

## Boundaries

- In scope: repo-local code, tests, docs, skills, scripts, validation helpers,
  and charness artifacts needed to close #268, #264, #269, #270, and the
  autonomous portion of #265/#261.
- In scope for #268: achieve closeout validation, issue closeout draft
  pre-validation, goal-artifact evidence floors, closeout-surface sweep
  guidance, and tests/validators that make bypasses fail before external
  mutation. This is a hard phase gate: do not stage issue-closing work for later
  slices until this slice has targeted proof.
- In scope for #264: the skill-portability library/checker, author-only
  doc/test cite discriminator, operator-surface allowlist, marker escape hatch,
  cross-skill cite sweep, portable-authoring reference sentence, and tests.
- In scope for #269/#270: achieve artifact wording that could stale against a
  mutable HEAD, and mutation proof workflow that binds targeted mutants to exact
  gate-reported lines before mutation.
- In scope for #265/#261 only after the earlier guard slices: inspect the
  residual survivors, prove the precise survivor behavior, add or adjust tests
  where the intended behavior is already clear, and stop on a real gate-design
  or semantics choice. Equivalent-mutant classification and mutation-standard
  changes are not autonomous unless the existing repo policy already decides
  them mechanically.
- Stop and ask the user if a slice requires choosing a new product metric,
  changing release/version policy, pushing or closing live GitHub issues,
  accepting lower mutation standards, or deciding behavior where the current
  repo contract is ambiguous.
- Tracked bug-class issue rule: run a `debug`/root-cause step before the fix
  slice when the issue is bug-class, and stage issue closeout through the issue
  workflow or commit close keywords; do not directly close live issues.
- Portability invariant: host-specific behavior stays in adapters, presets,
  hooks, and integration manifests; public skills and shared references must not
  bake in one host's path or provider assumptions.
- Shared-tree review invariant: any bounded reviewer inspects prior versions via
  read-only git plumbing only; no checkout/restore/reset/stash/add for
  inspection.

## User Acceptance

- The final report names which of #268, #264, #269, #270, #265, and #261 were
  completed, partially completed, or intentionally left open, with issue-ready
  closeout text or explicit non-claims for each.
- `git log --oneline origin/main..HEAD` shows small, reviewable commits whose
  subjects map to the slices; `git status --short --branch` is clean unless the
  user explicitly pauses before commit.
- `python3 scripts/check_goal_artifact.py --repo-root . --goal-path
  charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md` passes at
  closeout.
- Slice-local tests and validators pass after each meaningful slice, and the
  final broad gate or documented local substitute passes before completion.
- Any live/external proof not run is named as a non-claim, not implied.
- The goal proceeds slice-to-slice only after the expected evidence for the
  completed slice is recorded in `## Slice Log`.

## Agent Verification Plan

### Low-Cost Checks

- Before pursuing: `python3 skills/public/achieve/scripts/check_goal_artifact.py
  --repo-root . --goal-path
  charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md
  --pursue-ready`.
- Per slice: run targeted pytest/ruff/validator commands for the touched files;
  record exact commands and results in `## Slice Log`.
- When tests are added or expanded, record a cheap duplicate/length/pressure
  sample or the reason it was not applicable.
- Before any commit after code/test/doc mutation: run
  `python3 scripts/run_slice_closeout.py --repo-root .` or a narrower
  justified aggregate when the slice is docs/artifact-only.
- For mutation-work slices: bind the target to the exact gate-reported line
  before hand-mutating; record RED target-kill proof and GREEN restoration.

### High-Confidence Checks

- Final `./scripts/run-quality.sh --read-only` unless the run remains strictly
  docs/artifacts and the docs-only subset is the justified local substitute.
- `python3 scripts/check_changed_surfaces.py --repo-root .` when changed
  surfaces are unclear.
- Fresh-eye critique/review at material boundaries, with concrete host signal
  recorded if delegation is blocked.
- Final closeout evidence includes a bound retro artifact, host-log probe output
  or an explicit skip reason, a bound disposition review artifact or
  `host-blocked-subagent` skip, and gather/release coordination floor handling.
- `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root .
  --goal-path charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`
  before flipping complete.

### External Or Live Proof

- GitHub issue closure is not performed by this goal operator unless a later
  explicit user instruction says to mutate live issues. Stage closeout evidence
  locally instead.
- No push or release publication is part of this goal. If final proof depends on
  remote CI, record it as `not run` and give the maintainer the exact follow-up.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Confirm pursue-readiness and live issue context for the selected backlog | Prevent a broad autonomous instruction from running with stale or unshaped state | Goal artifact pursue-ready; current `gh issue list`/issue details reviewed; any stale handoff item recorded as off-goal | complete |
| 1 | #268 closeout integrity: make achieve closeout and issue closeout drafts fail before incomplete external or host-level completion | This run will create closeout state; harden the proof floor first | Tests/validators for goal evidence floor and issue closeout draft pre-validation; slice closeout green | complete |
| 2 | #269 stale mutable-HEAD wording guard | This proof-quality guard can affect this goal's own final artifact wording | Achieve artifact wording avoids stale mutable HEAD claims; validator/test or reference update pins the rule | complete |
| 3 | #264 portability guard and cross-skill cite sweep | Curated handoff chunk with well-scoped discriminator/allowlist; reduces portability drift before broader skill edits | Guard implemented; author-only doc/test cites blocked; operator surfaces (`docs/handoff.md`, `charness-artifacts/...`, adapter yaml) allowed; marker-qualified authoring-repo cites allowed; docs/reference updated; targeted tests green | complete |
| 4 | #270 exact-line targeted mutant proof guard, then #265/#261 mechanical survivor triage | Exact-line proof is the prerequisite for honest targeted survivor mutation; heavier survivor work should follow proof/portability guardrails | Gate-reported line/source target recorded before mutation; exact survivor behavior mapped; clearly real survivors killed with RED/GREEN proof; issue-ready residual policy decision recorded if needed | complete |
| 5 | Final closeout, critique, retro, handoff refresh, and commit discipline | Consolidate proof and leave the next operator a clean state | Final gate/substitute pass; goal artifact complete; retro improvements dispositioned; docs/handoff.md updated only at closeout; commits created | pending |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.

Initial routing:

- Routing: `find-skills` already routed bare handoff pickup to
  `charness:handoff`, and the chunker ranked the backlog before this goal was
  shaped.
- Gather: n/a — no arbitrary external URL/source is being summarized into this
  artifact; issue tracker state is used as the work queue and must be refreshed
  through the issue/handoff workflow inside the relevant slice.
- Release: n/a — no release surface is planned; stop and re-plan if one becomes
  necessary.

## Slice Log

### Slice 1: Slice 0 (activation and live issue refresh)

- Objective: Confirm pursue-readiness and current issue context before mutating.
- Why this approach: The goal is intentionally broad; slice 0 prevents stale or unshaped state from driving mutation.
- Commits: n/a — activation/context slice
- What changed: Goal status flipped from draft to active; live open issue list and #268 body refreshed; find-skills routed current boundary to achieve + issue.
- Alternatives rejected:
- Targeted verification: PASS: check_goal_artifact.py --pursue-ready; PASS: gh issue view 268; PASS: gh issue list --state open --limit 50; PASS: find-skills recommendation for #268 returned achieve + issue.
- Test duplication pressure: No tests added.
- Critique: Before-phase fresh-eye critique already folded into goal artifact; no new slice critique needed for activation-only context refresh.
- Off-goal findings: None.
- Lessons carried forward: Proceed slice-to-slice only after expected evidence is recorded in the goal log.
- Metrics: Metrics: when available.

### Slice 2: Slice 1 (#268 closeout integrity)

- Objective: Make achieve closeout and issue closeout drafts fail before incomplete host-level completion or GitHub mutation.
- Why this approach: #268 is the hard first phase gate; later slices will create issue/goal closeout state, so pre-signal and pre-mutation validation must exist first.
- Commits: b1b3e1a Harden issue closeout prevalidation
- What changed: Added issue_tool.py validate-closeout-draft via a new issue_validate_closeout_draft helper; documented draft validation before issue closeout carriers are published; documented achieve host-level completion as downstream of a checked Status: complete goal artifact; recorded public-skill dogfood/scenario review for achieve and issue; synced plugin mirrors; added regression tests for issue draft validation, issue closeout discipline, and achieve host completion ordering.
- Alternatives rejected: Did not make close-with-comment invent classification from body text; closeout classification remains explicit so the verifier applies the right ledger. Did not alter host APIs directly; repo-owned contract now requires artifact completion and check_goal_artifact before host completion signals.
- Targeted verification: PASS: pytest -q tests/quality_gates/test_issue_closeout_draft_validation.py tests/quality_gates/test_issue_closeout_verifier_critique.py tests/quality_gates/test_achieve_before_activation.py tests/quality_gates/test_issue_closeout_discipline.py (20 passed); PASS: python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py; PASS: python3 scripts/validate_skills.py --repo-root .; PASS: python3 scripts/validate_packaging.py --repo-root .; PASS: python3 scripts/validate_packaging_committed.py --repo-root .; PASS: python3 scripts/check_doc_links.py --repo-root .; PASS: python3 scripts/check_command_docs.py --repo-root .; PASS: ./scripts/check-secrets.sh; PASS: python3 scripts/validate_cautilus_proof.py --repo-root .; PASS: python3 scripts/check_skill_ownership_overlap.py --repo-root .; PASS: python3 scripts/validate_public_skill_validation.py --repo-root .; PASS: python3 scripts/validate_public_skill_dogfood.py --repo-root .; PASS: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts; PASS: python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing (advisory warnings only); PASS: python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support; PASS: ./scripts/check-markdown.sh; PASS: broad pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py (1872 passed, 4 skipped); PASS: python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review (completed; broad pytest 1872 passed, 4 skipped).
- Test duplication pressure: Added one focused 107-line test file and small assertions in existing test files; issue_tool.py is at 359/360 and must not grow further.
- Critique: Causal review fresh-eye executed (parent-delegated): classified #268 as bug; root cause is gates attached to helper surfaces rather than every externally visible completion/mutation boundary; detection gap is helper-level tests existed but close-with-comment accepted arbitrary body; sibling release manual-close risk deferred as diagnostic because this slice did not touch release closeout.
- Off-goal findings: Release manual issue closeout has a diagnostic sibling risk but is deferred unless a later slice touches release closeout.
- Lessons carried forward: Pre-mutation draft validation should reuse final verifiers without final-state checks; host completion must be downstream of durable artifact completion.
- Metrics: Metrics: when available.

### Slice 3: Slice 2 (#269 mutable HEAD freshness)

- Objective: Guard achieve goal artifacts against stale current-HEAD SHA wording.
- Why this approach: This proof-quality guard can affect this goal's own final artifact wording after later commits.
- Commits: d0a225e Guard achieve HEAD freshness
- What changed: Added goal_artifact_head_freshness.py and wired check_goal_artifact.py to emit head_freshness; documented mutable HEAD honesty in achieve skill/lifecycle; synced plugin mirror; recorded public-skill dogfood review; added helper and CLI regression tests for stale current HEAD claims, base+HEAD same-line false positives, wrapped claims, historical/proof-targeted wording, and missing-git portability.
- Alternatives rejected: Did not ban all SHAs in goal artifacts or all ..HEAD range prose; validator only checks immutable SHA tokens grammatically bound to current-HEAD wording. Did not rewrite historical artifacts; the guard validates current claims going forward.
- Targeted verification: PASS: pytest -q tests/quality_gates/test_goal_head_freshness.py tests/quality_gates/test_goal_coordination_floors.py::test_check_goal_artifact_cli_refuses_complete_goal_with_unsatisfied_gather tests/quality_gates/test_achieve_before_activation.py tests/quality_gates/test_goal_artifact_lib.py (47 passed); PASS: py_compile touched achieve scripts and plugin mirror; PASS: ruff touched achieve scripts/tests; PASS: validate_skills; PASS: validate_packaging; PASS: validate_packaging_committed; PASS: check_doc_links; PASS: check_command_docs; PASS: validate_public_skill_dogfood; PASS: check_python_lengths; PASS: python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review (completed; broad pytest 1872 passed, 4 skipped; usage episode slice-closeout-0a96f91eb11244d493fac656b86579a3).
- Test duplication pressure: Added one focused achieve validator test file; slice closeout aggregate passed the broad quality/test suite.
- Critique: Full parent-delegated code critique recorded at charness-artifacts/critique/2026-05-31-269-achieve-head-freshness-critique.md. Angle blockers fixed: line-wide exemptions, base-SHA false positives, missing-git portability, and direct historical same-line wording.
- Off-goal findings: Semantic validation for all ..HEAD ranges remains deferred; current slice is scoped to stale immutable SHA claims bound to current-HEAD wording.
- Lessons carried forward: Freshness guards should bind findings to claim grammar, not whole physical lines; remediation wording must be executable by the validator.
- Metrics: Metrics: when available.

### Slice 4: Slice 3 (#264 portability guard and sweep)

- Objective: Add a guard for author-repo-internal public-skill cites and sweep same-class references.
- Why this approach: This prevents vendored public skills from sending downstream users to source-repo-only docs/tests/skill paths while preserving operator-surface allowlists.
- Commits: 2930c46 Guard public skill authoring cites
- What changed: Extended skill_portability_lib.py and validate_skills.py to reject bare author-only docs/tests/source-tree skill cites in public skills; added validator regressions for docs contracts, tests.py nodeids, source-tree skill paths, operator surfaces, charness-artifacts, adapter yaml, marker escapes, fenced examples, and sibling skill-relative paths; swept public-skill references using marker-qualified authoring-repo-internal wording or exported-layout relative paths; updated portable-authoring guidance; synced plugin mirrors; recorded public-skill dogfood/scenario review for the affected skills.
- Alternatives rejected: Did not parse non-backticked prose or markdown link targets; issue examples and current corpus are backtick-shaped and broad prose parsing risks the reverted overreach. Did not add root scripts/... cites to this guard; that is an adjacent install-surface policy question, not #264's docs/tests/source-tree skill boundary.
- Targeted verification: PASS: pytest -q tests/quality_gates/test_skill_validation.py (28 passed); PASS: python3 scripts/validate_skills.py --repo-root .; PASS: ruff check scripts/skill_portability_lib.py scripts/validate_skills.py tests/quality_gates/test_skill_validation.py; PASS: python3 scripts/check_doc_links.py --repo-root .; PASS: validate_packaging and validate_packaging_committed earlier in slice; PASS: python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review (completed; broad pytest 1872 passed, 4 skipped; usage episode slice-closeout-8479d7c542444ae8ace5e853bf406ce8).
- Test duplication pressure: Expanded existing skill validation tests rather than adding a new test file; slice closeout aggregate passed the broad quality/test suite.
- Critique: Full parent-delegated code critique recorded at charness-artifacts/critique/2026-05-31-264-portability-guard-critique.md. Blockers fixed: nodeid detection, extensionless skill paths, sibling-skill relative paths, remaining retro sibling refs, and missing allowlist tests.
- Off-goal findings: Root script cite portability remains deferred as a separate policy/install-surface question if needed.
- Lessons carried forward: Portability guards must distinguish source-tree author-only paths from same-plugin vendored sibling paths; allowlists need exact regression coverage to avoid repeating the reverted over-broad guard.
- Metrics: Metrics: when available.

### Slice 5: Slice 4 (#270 exact-line targeted mutant proof guard)

- Objective: Make targeted mutant proof bind to the exact changed-line gate target before manual mutation.
- Why this approach: #270 is the prerequisite guard before #265/#261 survivor triage; without exact target binding, hand-mutant RED/GREEN proof can hit the wrong nearby return or branch.
- Commits: f8c7a2f Bind mutation proof to exact lines
- What changed: Added changed-line proof targets with source text from the gate head revision; exposed blocking_targets and a targeted-mutant proof contract from the local helper; carried exact targets into sample manifests and mutation score summaries; made score closeout fail closed when changed-line blockers lack exact targets; documented the manual proof contract in the quality mutation reference; synced plugin mirrors; recorded quality dogfood and critique evidence.
- Alternatives rejected: Did not build a patch-by-line mutation helper or change mutation score standards; exact path:line/source binding is sufficient for this issue. Deferred unifying blocker and target generation into one richer return type because tests now cover the recurrence path and a refactor would widen the slice.
- Targeted verification: PASS: pytest -q tests/quality_gates/test_changed_line_mutation_coverage.py tests/quality_gates/test_mutation_changed_line_targets.py tests/quality_gates/test_quality_mutation_score_validity.py tests/quality_gates/test_quality_mutation_sampling.py (55 passed); PASS: ruff on touched mutation scripts/tests; PASS: python3 -m py_compile touched mutation scripts; PASS: python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing (advisory warnings only); PASS: validate_packaging and validate_packaging_committed; PASS: python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review (completed; broad pytest 1872 passed, 4 skipped; usage episode slice-closeout-0830e843671449b79d3f07a682c55266).
- Test duplication pressure: Added one focused test file for changed-line target behavior and expanded two existing mutation gate test files; avoided adding more to near-limit test_quality_mutation_sampling.py; sample_mutation_files.py remains near-limit at 451/480 and should not grow in future slices.
- Critique: Causal review fresh-eye executed (parent-delegated): classified #270 as bug; root cause is missing proof-binding contract between the changed-line gate target and hand-mutant step. Full code critique recorded at charness-artifacts/critique/2026-05-31-270-exact-line-mutant-proof-critique.md; blockers fixed: source bound to head_sha, missing-target fail-closed invariant, stderr guidance, and plugin export drift.
- Off-goal findings: No new off-goal issues filed. Patch-by-line mutation helper and unified blocker/target return type remain deferred unless recurrence justifies them.
- Lessons carried forward: Proof helpers should bind operator-visible text to the same revision as the gate result; optional diagnostic fields are not enough when the workflow requires exact target proof.
- Metrics: Metrics: when available.

### Slice 6: Slice 4 continuation (#265/#261 coordination survivor triage)

- Objective: Exhaustively rerun the coordination-cues trio mutation scope and kill clearly real residual survivors without deciding equivalent-mutant policy.
- Why this approach: #265 explicitly asks for a scoped trio run after the prior bounded pass; the #270 exact-line proof guard is now in place, so the survivor inventory can be refreshed honestly before adding targeted tests.
- Commits: pending
- What changed: Added test-only hardening across `test_goal_coordination_floors.py`, `test_goal_disposition_gate.py`, and `test_goal_head_freshness.py`. New coverage pins absent Context Sources behavior, child-heading section spans, loader fail-closed paths, missing-`Created` coordination-floor fail-closed behavior, closeout token/narration helpers, order-independent narration scan, and `check_goal_artifact.py` CLI return/report paths for pursue-ready, missing file, missing evidence files, invalid skips, and unbound evidence.
- Alternatives rejected: Did not change production code or mutation score policy. Did not chase regex flag arithmetic, string-identity, release-span blank-count, or current-contract ordering survivors after fresh-eye critique classified them as equivalent or low-value. Did not mutate or close live GitHub issues.
- Targeted verification: PASS: scoped Cosmic Ray run before test hardening: 514/514 executed; 392 killed, 122 survived; score 76.3% (threshold report failed because invoked without the normal sample manifest, but the scoped inventory completed). PASS: focused pytest after first hardening: 75 passed. PASS: second scoped Cosmic Ray run: 514/514 executed; 459 killed, 55 survived; score 89.3%. PASS: focused pytest after second hardening: 79 passed. PASS: third scoped Cosmic Ray run: 514/514 executed; 465 killed, 49 survived; score 90.5%. PASS: focused pytest after final two pins: 80 passed. PASS: final scoped Cosmic Ray run: 514/514 executed; 467 killed, 47 survived; score 90.9%. PASS: `ruff check tests/quality_gates/test_goal_coordination_floors.py tests/quality_gates/test_goal_disposition_gate.py tests/quality_gates/test_goal_head_freshness.py`. PASS: `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing` (advisory warnings only). PASS: `pytest -q tests/quality_gates/test_goal_coordination_floors.py tests/quality_gates/test_goal_disposition_gate.py tests/quality_gates/test_goal_head_freshness.py` (80 passed). PASS: `python3 scripts/validate_packaging.py`. PASS: `python3 scripts/validate_packaging_committed.py --repo-root .`. PASS: `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review` (completed; broad pytest passed; usage episode `slice-closeout-db1a3456459d4c75ba1cee4deb20271d`).
- Test duplication pressure: Added focused assertions to three existing test files rather than new production helpers. `test_goal_head_freshness.py` now carries the CLI closeout-error cases but remains below the advisory file-length band.
- Critique: Fresh-eye critique recorded at `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`; no blockers. Caveat recorded: the fake-helper ordering test proves wrapper order independence, not a currently natural helper ordering.
- Off-goal findings: Equivalent-mutant classification and mutation-standard policy remain open policy decisions; this slice does not claim to close #261/#265 live on GitHub.
- Lessons carried forward: Residual survivor triage should report both score movement and non-claims; a passing scoped threshold does not by itself justify chasing low-value implementation-detail mutants.
- Metrics: Scoped trio mutation score moved from 76.3% to 90.9%; survivors moved from 122 to 47; executed count remained 514/514; filtered count remained 165.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/handoff.md` current `Workflow Trigger`, `Current State`, and ranked
  `Next Session` entries.
- Handoff chunker output from this session: `chunk-5` (#268), `chunk-1` (#264),
  `chunk-3` (#269/#270), `chunk-2` (#265/#261), then `chunk-4` broad backlog.
- Live issue list freshness: `gh issue list --state open --limit 50` read at
  2026-05-31T20:08:56+09:00; issue ids are treated as live issue workflow state,
  not gathered external source material.
- `charness-artifacts/quality/latest.md` for current validation posture and
  gate expectations.
- `charness-artifacts/retro/recent-lessons.md` for current repeat traps:
  exact-line mutation proof, stale mutable-HEAD wording, and mutation runner
  cleanup lessons.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md` for verify-before-commit,
  closeout-only handoff writes, critique, and commit discipline.
- Open issue ids in scope: #268, #264, #269, #270, #265, #261. Broad backlog
  issue ids are intentionally not pulled into this goal unless filed as
  off-goal findings.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only draft vs implementation-continuation. Chosen:
  implementation-continuation after explicit `/goal` activation, because the
  user asked to set the goal so all autonomous work can proceed. Rejected:
  artifact-only draft would strand the requested autonomy.
- Scope family: one chunk, all handoff chunks, or all open issues. Chosen: all
  handoff-ranked chunks in the current autonomous hardening tranche, with
  product/gate-policy decisions as stop conditions. Rejected: one chunk is too
  narrow for the user's wording; all open issues would overreach into product
  metrics and broad backlog churn.
- Ordering family: #264 first per handoff memo vs #268 first per chunker rank.
  Chosen: #268 first because closeout integrity should be hardened before this
  run creates more closeout evidence; this intentionally overrides the handoff
  memo's #264-first curation because the chunker read the live backlog and
  ranked #268 first. Rejected: #264 first remains reasonable but leaves the
  known closeout bypass active during subsequent slices.
- Sequencing family: #269/#270 as one process slice vs split by use point.
  Chosen: #269 immediately after #268 because it can affect this goal's own
  final proof wording; #270 immediately before #265/#261 because it is most
  useful as the targeted-mutation checklist. Rejected: bundling them as generic
  process work hides their different proof timing.
- Host/provider/environment axis: host-specific behavior is an axis in this
  repo. Chosen: keep host-specific behavior in adapters/hooks/manifests and
  write portable public skill/docs behavior. Rejected: Codex-only or
  Claude-only assumptions in shared surfaces.
- Release axis: release is not part of this goal. Chosen: `Release: n/a` unless
  a direct release-surface blocker is discovered. Rejected: opportunistic
  version bump during a maintenance/autonomy run.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Fresh-eye satisfaction: parent-delegated. Three bounded reviewers completed
  read-only lenses: sequencing, autonomy boundary, and proof/closeout risk.
- Act Before Ship findings folded: narrow wording from "all autonomous backlog"
  to a closed hardening tranche; fill the required sections; make #268 a hard
  first phase gate; split #265/#261 so autonomous work stops before
  equivalent-mutant or gate-policy decisions; explicitly exclude product,
  release, live mutation, and broad backlog expansion.
- Bundle Anyway findings folded: keep #268 first; move #269 immediately after
  #268; keep #270 adjacent to #265/#261; inline #264 discriminator/allowlist;
  add per-slice evidence and freshness.
- Same-agent preflight folded: the phrase "all autonomous work" can overreach.
  Folded into Non-Goals, Boundaries, and stop conditions so the agent cannot
  silently absorb product decisions, live issue mutation, release work, or broad
  backlog grooming.
- Same-agent preflight folded: #268 should precede #264 despite handoff curation
  because closeout-proof bypasses should be fixed before generating more
  closeout state.
- Valid but defer: #184/#185 product success work remains outside this goal
  because it requires product judgment, not only repo maintenance execution.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

## User Verification Instructions

## Auto-Retro
