# Achieve Goal: Workflow Review Efficiency And Generalization

Status: complete
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 5 validation, critique, and closeout is complete.
- Next action: commit and push the checked-in completion proof, then mark the
  host-level goal complete.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Improve Charness operating contracts so future sessions catch workflow-boundary bugs earlier without adding brittle one-off coupling or excessive subagent review. The goal should turn the recent #275/#276 lessons into general, testable guidance around capability routing, slice-level critique cadence, invariant-first review, similar-pattern scans, and disposition of follow-up improvements.

## Non-Goals

- Do not create a #275/#276-specific checklist that only recognizes those exact
  filenames or issue numbers.
- Do not make `find-skills` disappear from required session bootstrap while the
  root repo contract still requires one startup pass. The improvement is to stop
  repeated or over-visible inventory output when the operator is not making a
  capability-routing decision.
- Do not require a fresh-eye subagent critique for every commit, every small
  local edit, or every afterthought. Critique should be scaled and normally
  happen at meaningful slice or bundle boundaries.
- Do not weaken mandatory critique, release, issue-closeout, or goal-completion
  proof floors. The goal is less wasted review, not less review where it matters.
- Do not overfit resolver/readiness rules into one shared helper unless the
  codebase shows a real shared abstraction boundary.
- Do not file or close public GitHub issues during this goal unless activation
  explicitly decides that durable tracking is the right disposition.

## Boundaries

- In scope: revise the repo operating contract, implementation discipline,
  achieve/critique/find-skills references, validators, or tests that own these
  recurring workflow behaviors.
- In scope: define a general "invariant-first review" pattern for workflow
  bugs: name the cross-boundary invariant, test it at producer and final
  consumer, then scan siblings by interface shape rather than by issue-specific
  keywords.
- In scope: tighten when `find-skills` should write or surface inventory:
  startup bootstrap may stay read-only or quiet when possible; task-specific
  recommendation is used only at real routing boundaries; pointer rewrites with
  no canonical change are treated as drift.
- In scope: encode a slice-level fresh-eye cadence: use bounded subagent review
  for non-trivial workflow, release, issue-closeout, prompt/skill, validator, or
  export slices, and avoid per-commit review churn.
- In scope: audit whether the #275/#276 failure shapes have sibling patterns in
  adjacent surfaces, including cross-skill source resolution, diagnostic
  propagation, placeholder/readiness gates, and release/closeout disposition.
- In scope: ensure each improvement found by this goal is either applied,
  converted to a tracked issue, or explicitly rejected with a reason in the
  goal artifact.
- Out of scope unless required by evidence: a full rewrite of skill routing,
  a generic dependency-injection framework for all skills, migration of all
  historical goal artifacts, or broad release-version changes.
- Stop and ask before changing the standing AGENTS startup rule from "always
  call find-skills once" to a weaker rule; that is a repo-level operating
  contract decision, not a local helper tweak.

## User Acceptance

- A next operator can read this goal and see exactly which choices need human
  discussion before activation.
- The resulting repo rule distinguishes startup capability bootstrap from
  meaningful routing decisions, so `find-skills` inventory does not keep
  appearing as if it were the answer to ordinary workflow questions.
- The critique cadence is expressed as a general rule: bounded fresh-eye review
  at slice/bundle boundaries, scaled same-agent critique for small local-risk
  edits, and no per-commit subagent ritual unless the slice itself justifies it.
- The fix pattern is invariant-based, not bug-name-based: producer/final
  consumer proof, sibling scan by interface shape, and explicit non-claims for
  unproven hosts or adapters.
- Similar-pattern audit results are disposed: fixed now, filed as an issue, or
  rejected/deferred with rationale.
- Validators or tests cover any new deterministic rule. If a rule remains
  prose-only, the goal explains why code enforcement would be brittle.

## Agent Verification Plan

### Low-Cost Checks

- `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md --pursue-ready`
- `git status --short --branch` before and after each mutation slice.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after the first
  content-bearing edit to discover generated/export obligations.
- Focused tests for touched helpers or validators before any commit.
- If only docs/artifacts change, run the relevant markdown/artifact validators
  rather than a broad Python suite.

### High-Confidence Checks

- For skill/reference/validator changes, run the focused test modules that own
  goal readiness, find-skills artifact behavior, critique routing, and changed
  surface detection.
- Run `python3 scripts/run_slice_closeout.py --repo-root .` if the slice spans
  skill prose, helper code, tests, and plugin/export surfaces.
- Run a bounded fresh-eye critique once per substantial slice or final bundle,
  using a slice packet that includes intent, changed files, invariants, tests,
  non-claims, and explicit reviewer questions.
- Final closeout should run the repo's appropriate quality gate for the changed
  surface, then `check_goal_artifact.py` without `--pursue-ready`.

### External Or Live Proof

- No external source gathering is planned; the motivating evidence is repo-local
  artifacts, recent retros, issue closeout artifacts, and the current handoff.
- No GitHub issue mutation is planned unless activation chooses issue filing as
  the disposition for deferred improvements.
- No release is planned. If the implementation touches version or install
  manifest surfaces, stop and route through `release`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Discuss and lock activation choices | The user explicitly questioned overuse of `find-skills`, overuse of subagents, and over-coupled fixes | `Discuss before activation` has concrete decisions and this artifact passes `--pursue-ready` | completed |
| 1 | Normalize capability-routing guidance | Prevent startup inventory from becoming repeated visible noise while preserving useful routing discovery | Updated owning contract/reference or helper behavior; focused tests/validators for no unnecessary pointer churn or output where applicable | completed |
| 2 | Encode slice-level critique cadence | The second critique caught real bugs, but per-commit subagents would become waste | Critique/achieve/operating guidance says when fresh-eye is required, when same-agent critique is enough, and what a slice packet must include | completed |
| 3 | Generalize invariant-first bug review | Future fixes should start from workflow invariants, not issue-specific patch memories | Review checklist/reference and tests that require producer plus final-consumer coverage for propagated diagnostics/readiness decisions | completed |
| 4 | Scan sibling patterns and disposition findings | The user asked whether similar patterns exist elsewhere and whether all improvements are disposed | Audit artifact lists scanned surfaces, findings, and dispositions as applied / issue / rejected / deferred-with-owner | completed |
| 5 | Validate, critique, and close out | Changes affect operating contracts and must not silently increase process cost | Surface sync if needed, focused/broad gate as appropriate, bounded final critique, complete goal artifact, handoff refreshed | completed |

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

- Routing: startup `find-skills` read-only recommendation pointed this request
  to `achieve`; `critique` is a bounded slice/final review mechanism, not a
  per-commit default.
- Gather: n/a — the context is repo-local conversation, retros, and artifacts.
- Release: n/a — no release surface is intended.
- Issue closeout: #277 via direct-commit carrier; close keywords, bug ledger,
  and `Critique #277:
  charness-artifacts/critique/2026-06-02-277-closeout-binding-resolution.md`
  passed `issue_tool.py validate-closeout-draft` before commit and
  `issue_tool.py verify-closeout --expect-state CLOSED` after push.

## Discuss before activation

The next session should resolve these choices with the user before pursuing the
goal:

1. Should the root repo rule remain "always call `find-skills` once at
   task-oriented session start", but prefer read-only/quiet bootstrap and only
   surface recommendations at real routing boundaries? Recommended default:
   yes, because changing the root rule is a repo-contract decision and the
   waste was repeated visible inventory, not the existence of one bootstrap.
2. What is the acceptable fresh-eye cadence? Recommended default: one bounded
   subagent critique per substantial slice or final bundle, plus same-agent
   scaled critique for small local edits; never every commit by default.
3. How strict should sibling-pattern scanning be? Recommended default: scan by
   shared interface shape and changed-boundary class, not whole-repo exhaustive
   grep. File deferred issues for broader audits that would exceed the slice.
4. How should deferred improvements be disposed? Recommended default: every
   surfaced improvement becomes `applied`, `issue #N`, or `rejected/deferred:
   reason + owner surface`; prose-only retro memory is not enough.

## Slice Log

- 2026-06-02 Slice 1 in progress: kept one startup `find-skills` pass but made
  recommendation-shaped calls read-only unless `--write-artifact` is explicit;
  added #277 per-issue resolution-critique binding for issue closeout carriers;
  filtered active-goal activation entries from handoff chunked routing; recorded
  public-skill dogfood review for the changed achieve/find-skills/issue/quality
  /handoff surfaces.
- 2026-06-02 Fresh-eye review for #277: causal review identified
  carrier-level critique evidence as the bug; post-implementation reviewers
  required source/plugin helper inclusion, stale issue carrier wording fixes,
  setup renderer sync, handoff reference sync, active-goal close-intent cue, and
  additional bundle/fence regression tests. Folded into the slice.
- 2026-06-02 Slice 1 follow-up: promoted the active-goal `Issue closeout:` cue
  into a deterministic achieve coordination floor for goals Created >=
  2026-06-02. Existing gather/release floors keep their 2026-05-31 cutoff, so
  completed historical goals are not retroactively refused.
- 2026-06-02 Fresh-eye review for the issue-closeout floor:
  `charness-artifacts/critique/2026-06-02-issue-closeout-goal-floor-critique.md`.
  Folded blockers for GitHub issue URL / repo-qualified issue refs, overly broad
  planning-text close-keyword scanning, stale cutoff docs, handoff state, active
  goal proof, and context-only issue template guidance.
- 2026-06-02 Slice 2 complete: encoded critique cadence by risk boundary rather
  than commit count in `docs/conventions/operating-contract.md`,
  `skills/public/critique/references/cadence.md`, `skills/public/critique/SKILL.md`,
  and the `achieve` lifecycle/scaffold packet guidance. Fresh-eye review
  consumed
  `charness-artifacts/critique/2026-06-02-critique-cadence-slice-packet.md`
  and is recorded at
  `charness-artifacts/critique/2026-06-02-critique-cadence-slice.md`; blockers
  for stale packet wording, incomplete risk-class symmetry, active-goal status,
  handoff pickup state, and package durability were folded.
- 2026-06-02 Slice 3 complete: added
  `skills/public/debug/references/invariant-first-review.md` for
  producer-to-final-consumer workflow-boundary bugs, wired `debug` and
  `issue` causal review to consume the invariant substrate, and added
  `## Invariant Proof` to current debug artifacts through the scaffold and
  validator. Focused tests cover the artifact consumer path, scaffold output,
  and section-scoped causal-review references. Fresh-eye review consumed
  `charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice-packet.md`
  and is recorded at
  `charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice.md`;
  blockers for missing standalone debug consumer proof, prose-heavy tests,
  incomplete packet context, dogfood date drift, active-goal state, and handoff
  closeout were folded.
- 2026-06-02 Slice 4 complete: recorded
  `charness-artifacts/quality/2026-06-02-workflow-review-sibling-pattern-audit.md`
  as a static repo-local sibling-pattern audit across source resolution,
  diagnostic/status propagation, placeholder/readiness gates, closeout
  disposition, and source-guard/phrase-detector coupling. Dispositions are
  applied (F4-F6), rejected (F1/F2/F7/F8), deferred-with-owner (F3 via
  `docs/deferred-decisions.md` D19), and issue: none. Fresh-eye review consumed
  `charness-artifacts/critique/2026-06-02-sibling-pattern-audit-slice-packet.md`
  and is recorded at
  `charness-artifacts/critique/2026-06-02-sibling-pattern-audit-slice.md`.
  Reviewers found no Act Before Ship blockers; they required nuance that F1/F8
  are real coupling smells kept advisory by enforcement tier and consumer
  behavior, not absent coupling. Folded into the audit.
- 2026-06-02 Slice 4 user-correction follow-up: the phrase "expression
  difference" underweighted a real source-guard concern. The audit and critique
  were tightened to say prose-shape matching is coupling; the current
  no-code-change disposition rests only on the absence of a hard final consumer,
  not on the absence of coupling.
- 2026-06-02 Slice 5 complete: final fresh-eye reviewers found the expected
  closeout-state gaps before the complete flip and one substantive process-cost
  gap: read-only `find-skills` recommendation calls reduced artifact churn but
  not visible output volume. Folded by adding opt-in `--summary` output for
  routing probes, skill docs, plugin mirror sync, public-skill dogfood evidence,
  and focused tests for task-text and recommendation-role summary output.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/handoff.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`
- `charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-postcommit-subagent-critique.md`
- `charness-artifacts/critique/2026-06-01-release-v0.13.5-reviewer-tier-critique.md`
- GitHub issue #277: goal-run issue closeout can miss auto-close carriers and
  over-satisfy bundled critique evidence.
- User prompt on 2026-06-02 asking to reduce unnecessary `find-skills`
  surfacing, generalize improvements without strong coupling, avoid excessive
  subagent critique, and set next-session work up as an achieve goal.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- `find-skills` use: considered removing startup bootstrap, keeping it but
  making it read-only/quiet, or leaving behavior unchanged. Chosen for draft:
  keep one startup bootstrap because AGENTS currently requires it, but make the
  improvement target repeated visible inventory and unnecessary recommendation
  calls. Reject unchanged behavior because it caused user-visible noise.
- Critique cadence: considered per-commit subagents, slice/bundle subagents, or
  same-agent-only critique. Chosen for draft: slice/bundle fresh-eye review
  because the second critique caught real bugs, while per-commit review would
  be process waste. Reject same-agent-only for non-trivial workflow surfaces
  because repo policy requires bounded fresh-eye in those scopes.
- Generalization strategy: considered one-off rules for #275/#276, a large
  shared framework, or invariant-first guidance plus focused validators. Chosen
  for draft: invariant-first guidance and focused validators. Reject one-off
  rules as brittle and reject large framework unless the sibling audit proves a
  real shared abstraction.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Same-agent before-phase critique: the main failure risk is turning the last
  incident into a hard-coded ritual. Folded into Non-Goals and Slice Plan by
  requiring interface-shape sibling scans and slice-level critique cadence.
- Same-agent before-phase critique: changing the root `find-skills` startup rule
  without discussion would violate the current repo contract. Folded into
  Boundaries and Discuss before activation.
- Same-agent before-phase critique: "dispose improvements" must be an artifact
  outcome, not a vague lesson. Folded into User Acceptance and Slice 4.
- Over-worry not folded: requiring a subagent critique before this draft would
  add process cost before any implementation surface exists. The bounded
  fresh-eye review belongs to substantial slices or final closeout after
  activation.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Non-`gh` issue backend live closeout remains unproven; existing handoff keeps
  the live-proof trigger.
- Goal-windowed host metrics were unavailable. The host probe is session-wide,
  so efficiency claims use it as proxy pressure, not goal-attributed cost.

## Final Verification

- Retro: charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md
- Host log probe: charness-artifacts/probe/2026-06-02-workflow-review-efficiency-and-generalization-host-log-probe.json
- Disposition review: charness-artifacts/critique/2026-06-02-workflow-review-efficiency-disposition-review.md
- Final critique: charness-artifacts/critique/2026-06-02-workflow-review-efficiency-final-closeout-critique.md
- 2026-06-02 final self-verification against User Acceptance: startup
  capability bootstrap remains mandatory but recommendation probes are
  read-only/summary-capable at routing boundaries; critique cadence is
  slice/bundle-scoped; invariant-first review requires producer and final
  consumer proof; sibling-pattern findings are applied, rejected, or
  deferred-with-owner; deterministic rules have focused tests, while prose
  rules document why hard gates would be brittle.
- 2026-06-02 Slice 5 final proof: changed-surface sync ran
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and
  `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write`.
  Focused `find-skills` tests passed for compact `--summary` task routing and
  recommendation-role routing; full `./scripts/run-quality.sh --read-only`
  passed 69 phases, 0 failed, in 41.6s. Cautilus planner reported
  `next_action: none`; no evaluator run was made. Scenario review inspected
  `evals/cautilus/scenarios.json` and `suggest_public_skill_dogfood.py` output:
  existing `find-skills-local-first` still covers the maintained routing
  scenario, while the new `--summary` output is frozen in
  `docs/public-skill-dogfood.json` and focused tests.
- 2026-06-02 final slice closeout aggregate passed with
  `python3 scripts/run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review` after removing a non-issue handoff candidate
  exposed by `test_current_handoff_pipeline_has_only_actionable_candidates`.
  The rerun synced plugin/retro surfaces and passed packaging, doc links,
  command docs, markdown, secrets, Cautilus proof policy, skill validation,
  py_compile, ownership overlap, public-skill validation/dogfood, critique
  artifacts, probe JSON, retro lesson index, ruff, Python lengths,
  attention-state visibility, broad pytest, and agent-browser runtime guard.
- 2026-06-02 final fresh-eye critique:
  `charness-artifacts/critique/2026-06-02-workflow-review-efficiency-final-closeout-critique.md`.
  Act-Before-Ship findings were folded: missing closeout evidence lines,
  uncommitted retro/probe evidence, stale Slice 5/handoff state, and the
  `find-skills` visible-output gap. Bundle Anyway recommendation-role summary
  regression was folded into `tests/test_find_skills.py`.
- 2026-06-02 source-guard framing correction proof: `inspect_repo.py
  --repo-root .` exited 0 and reported no current recommendations or prose-wrap
  source guards; changed-surface sync ran
  `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write`;
  markdown links, command docs, markdownlint, secrets, all critique artifacts,
  retro lesson-selection index check, the new retro artifact validator, and
  active-goal `check_goal_artifact.py --pursue-ready` all passed.
- 2026-06-02 Slice 4 focused proof: markdown links, command docs, markdownlint,
  secrets, critique packet validation, critique artifact validation (`--all`),
  active-goal `check_goal_artifact.py --pursue-ready`, and
  `check_changed_surfaces.py` all passed. `run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review` passed for the repo-markdown and
  critique-artifact surfaces; Cautilus planner reported `next_action: none`, so
  no evaluator run was made for this static audit slice.
- 2026-06-02 slice closeout aggregate passed with
  `python3 scripts/run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review`: packaging, committed packaging, doc links,
  command docs, markdown, secrets, Cautilus proof policy, skill validation,
  py_compile, ownership overlap, public-skill validation, public-skill dogfood,
  critique artifacts, integrations, support sync, tool update, ruff, Python
  lengths, attention-state visibility, broad pytest, and agent-browser runtime
  guard all passed.
- 2026-06-02 #277 draft closeout carrier passed
  `issue_tool.py validate-closeout-draft --repo-root . --repo
  corca-ai/charness --number 277 --classification bug --carrier pr-body
  --body-file charness-artifacts/issue/2026-06-02-277-closeout-binding.md`.
- 2026-06-02 #277 final closeout passed
  `issue_tool.py verify-closeout --repo-root . --repo corca-ai/charness
  --number 277 --classification bug --carrier direct-commit --commit-ref
  225898a3 --expect-state CLOSED`.
- 2026-06-02 deterministic `Issue closeout:` floor proof: focused coordination
  floor tests passed (`pytest -q tests/quality_gates/test_goal_coordination_floors.py`),
  broader achieve evidence tests passed (`pytest -q
  tests/quality_gates/test_goal_coordination_floors.py
  tests/quality_gates/test_goal_artifact_lib.py
  tests/quality_gates/test_achieve_before_activation.py`), markdown,
  `validate_skills`, `validate_public_skill_dogfood`, JSON syntax, active-goal
  `check_goal_artifact.py`, and line-headroom checks passed; a historical
  completed-goal scan produced no issue-floor failures after the 2026-06-02
  cutoff split.
- 2026-06-02 issue-closeout floor fresh-eye critique:
  `charness-artifacts/critique/2026-06-02-issue-closeout-goal-floor-critique.md`;
  all Act-Before-Ship findings folded before final changed-surface validation.
- 2026-06-02 issue-closeout floor changed-surface aggregate passed with
  `python3 scripts/run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review`: packaging, committed packaging, doc links,
  command docs, markdown, secrets, Cautilus proof policy, skill validation,
  py_compile, ownership overlap, public-skill validation, public-skill dogfood,
  critique artifacts, ruff, Python lengths, attention-state visibility, broad
  pytest, and agent-browser runtime guard all passed. Cautilus planner reported
  `next_action: none`; `python3 scripts/suggest_public_skill_dogfood.py
  --repo-root . --skill-id achieve --json` confirmed `achieve` remains the
  relevant hitl-recommended dogfood scenario.
- 2026-06-02 Slice 2 focused proof: `pytest -q
  tests/quality_gates/test_critique_skill.py
  tests/quality_gates/test_goal_artifact_lib.py`, `validate_skills`,
  `check-markdown.sh`, `validate_public_skill_dogfood`, critique artifact
  validation, critique packet validation, and active-goal
  `check_goal_artifact.py` passed after folding fresh-eye blockers.
- 2026-06-02 Slice 2 changed-surface aggregate passed with
  `python3 scripts/run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review`: packaging, committed packaging, doc links,
  command docs, markdown, secrets, Cautilus proof policy, skill validation,
  py_compile, ownership overlap, public-skill validation, public-skill dogfood,
  critique artifacts, ruff, Python lengths, attention-state visibility, broad
  pytest, and agent-browser runtime guard all passed. Cautilus planner reported
  `next_action: none`; `achieve` and `critique` remain hitl-recommended dogfood
  scenarios and their checked-in dogfood notes were updated.

## User Verification Instructions

- Inspect `Final Verification` for the full gate, closeout retro, host probe,
  and fresh-eye critique/disposition review.
- For the source-guard concern, inspect F1/F8 in
  `charness-artifacts/quality/2026-06-02-workflow-review-sibling-pattern-audit.md`;
  the claim is now "coupling exists, no hard consumer found", not "wording
  difference is harmless".
- For the `find-skills` cost claim, run
  `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "create a worktree" --summary`
  and confirm it emits counts plus recommendations without top-level full
  inventory arrays.

## Auto-Retro

- 2026-06-02 source-guard framing correction: applied. User caught that
  "expression difference" sounded like a dismissal of prose-shape coupling.
  The durable audit now separates "coupling exists" from "a hard source guard
  exists"; no new issue was filed because the reopen condition is already
  encoded on F1/F8 and no hard consumer was found.
- applied: Source-guard reviews now record the two distinct decisions
  `coupling present?` and `hard consumer present?` in the audit, critique,
  closeout retro, and this Auto-Retro.
- applied: Efficiency evidence now separates measured host signals, proxy
  pressure, and unavailable goal-window signals through the closeout retro and
  host probe citation.
- applied: `find-skills` routing probes can now use `--summary` to reduce
  visible inventory output while preserving the default full JSON contract.
