# Achieve Goal: Orchestrator: #324 (release-first) + #325 + #322 + handoff 2-4

Status: active
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-324-325-322-handoff-orchestrator.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: B1 RELEASED + B2 done & pushed; B3+B4 shaped as child `/achieve` goals.
- Status: **active** — the only remaining work is operator activation+completion
  of the two child goals; once both complete, this orchestrator can flip to
  `complete` (its After-phase: final verification + retro + Auto-Retro).
- Done & PUSHED (origin/main at `3201cccc`):
  - B1a/B1b/B1c (#324): provider-neutral external-source preservation contract +
    fixture + 12 tests; **v0.26.0 RELEASED** — pushed/tagged, GitHub release
    published (`https://github.com/corca-ai/charness/releases/tag/v0.26.0`),
    **#324 CLOSED**. Commits `7dcfb43d`, `e0043ac9`; verification `3201cccc`.
    (Operator explicitly authorized the push, overriding the stage-and-stop default.)
  - B2 (handoff-4): false-green changed-line dry-run warning + tests. Commit `2f9c5f8c`.
- Next action (operator): `/goal @charness-artifacts/goals/2026-06-07-325-provenance-policy-handoff3-gate-capability.md`,
  then `/goal @charness-artifacts/goals/2026-06-07-322-advisory-interpretation-rollout.md`.
- This orchestrator does **not** auto-execute the child goals (preserves the
  `/achieve` shape → `/goal` pursue boundary). After both child goals complete,
  a session flips this orchestrator to `complete`.
- Remaining non-claim: the v0.25.0/v0.26.0 real-host smoke (handoff item 1) is a
  human async step, still not run by the agent.
- Mode: implementation-continuation, **orchestrator** — one auditable goal that
  resolves five deduped objectives as a multi-goal run with **dynamic
  workflow**: the next bundle is re-picked at each boundary, and a spec-first
  objective may be spun out as a dedicated child `/achieve` goal.
- Hard first constraint: **#324 + its release run first** (downstream
  `corca-ai/ceal#276` is waiting). The rest proceed once #324's release is
  cut/staged; the human real-host smoke is async and does not block.
- Verification cadence: cheap deterministic checks (`run_slice_closeout.py`
  aggregate, not just `pytest`) at commit boundaries; broad `pytest` + fresh-eye
  critique at bundle boundaries; local `--release` gate as the #324 bundle proof.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Orchestrate the resolution of five deduped objectives as one auditable
multi-goal run, with **#324 + its release strictly first** because a downstream
repo (`corca-ai/ceal#276`) is waiting, then dynamically sequencing the rest and
spawning dedicated `/achieve` child goals where an objective needs its own deep
shaping (especially the spec-first issues). Dynamic workflow is explicitly
allowed: the orchestrator re-picks the next bundle at each boundary by
dependency and risk, not a frozen order.

Objectives (handoff "Next Session" item 2 **is** #322, so the unique set is five):

1. **#324 (FIRST + release-stage).** Preserve original external-source context in
   issue workflows. Stage the release surface + `Close #324`; stop before
   push/tag.
2. **handoff-4.** Changed-line gate false-green tripwire — warn in
   `check_changed_line_mutation_coverage.py`.
3. **#325.** Provenance-placement policy + portable check (standing docs bake
   issue numbers / dates into rule prose). Spec-first.
4. **#322.** Roll out the advisory-interpretation contract to the remaining
   inference-layer surfaces + the nose family classifier. Spec-light rollout.
5. **handoff-3.** Skill portability of the mutation-gate lessons (promote to
   `mutation-testing.md`; optionally offer the gate as a `quality` capability +
   adapter contract).

## Non-Goals

- **Handoff item 1** (human real-host smoke for v0.25.0) — cannot be done by the
  agent; runs async and does not block this goal.
- **Pushing/tagging or publishing the GitHub release for #324** — the agent
  stages the release surface and runs the local `--release` gate only; the
  maintainer pushes/tags (user decision; repo has "No push/tag CI").
- **#184** (제품 성공 기준과 핵심 메트릭 정의) — outside the requested set.
- **Out-of-band closing** of #324/#325/#322 — close keywords are *staged*;
  the issues stay OPEN until the maintainer's push auto-closes them.
- **Collapsing the spec-first issues into direct impl** — #325 and #322 follow
  their issue bodies' spec-first guidance.
- **Becoming a generic task runner / new execution engine** — this orchestrator
  coordinates existing skills around one goal artifact; it does not implement a
  separate run loop.
- **Blanket-stripping issue refs / dates** (#325) — the policy distinguishes
  standing-rule docs from tracking docs and keeps load-bearing provenance.
- **Attaching self-declaration to verified facts** (#322) — rollout is
  inference-layer only (green gates, exact counts, AST results stay trusted).

## Boundaries

- External side-effect scope: any approved publish / push / remote-CI / apply is
  phase-scoped and does **not** carry forward. For this goal the only release
  side effect is the **#324 release-stage bundle**, and even there the agent
  stops at the local `--release` gate — no push/tag/GitHub-release. After that
  bundle, later quality/test slices are proven **locally by default**.
- **#324 + release is a hard first bundle.** The rest of the objectives begin
  only once #324's release is cut/staged (local gate green); the human smoke is
  async and never gates this goal.
- **The #324 contract is provider-neutral** (`axis: external-source-provider`):
  the source-preservation invariant covers Slack / Notion / Google Workspace /
  browser-gathered pages and any external conversation source. Slack is one
  adapter instance, **not** the schema — do not anchor the contract to Slack.
- **The #324 release commit must ride a trustworthy gate.** Run its changed-line
  mutation-coverage closeout consumer over `base→worktree`, never
  `--head-sha HEAD` (the known false-green dry-run trap,
  `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`). handoff-4 (B2)
  then bakes this guard into a permanent gate warning so the next release inherits
  it instead of re-deriving it.
- **Dynamic sub-goal spawning preserves the achieve boundary.** When the
  orchestrator spins out a child `/achieve` goal, that child gets its own
  artifact under `charness-artifacts/goals/`, its own `/goal` activation, and
  reports a reference back into this orchestrator's `## Slice Log` /
  `## Off-Goal Findings`. The orchestrator does **not** auto-execute child goals
  — each child still obeys the `/achieve` (shape) → `/goal` (pursue) separation.
  **No child goal opens until B1's release surface is committed and quiesced** —
  a child-goal commit on top of an uncommitted staged release surface is a
  concurrency hazard on the default branch.
- **Portability is mandatory for #325 and handoff-3.** Both must produce
  inheritable surfaces (a `quality` capability / linter / `authoring-preflight`
  / `mutation-testing.md` reference / adapter contract), not charness-repo-local
  fixes — both carry the repeated portability-miss trap
  (`charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`).
- **#325 must distinguish standing-rule docs from tracking docs** and preserve
  load-bearing provenance as a terse trailing `(#NNN)`.
- **#322 stays inference-layer only** and keeps each surface low-noise
  (positive-form blind-spot declaration, not a repeated distrust banner).
- `mutate → sync → verify → publish` are hard phase barriers; sync generated /
  plugin / export surfaces before validators.
- Bounded fresh-eye reviewers run in the shared parent worktree, inspecting
  prior versions read-only (`git show <ref>:<path>`), never mutating the index.

## User Acceptance

What the user can do to verify completion directly (per objective):

- **#324** — a fixture covers an issue filed from a Slack-like thread where the
  immediate message references earlier context; the created issue body / local
  artifact preserves source text *or* a "must re-read source before resolving"
  obligation; a closeout path warns/blocks when external-source preservation is
  missing; the invariant is portable (charness owns it, adapters may satisfy it).
  The release surface (version bump + install manifest) is staged with
  `Close #324` on the default-branch commit and the local `--release` gate is
  green; `gh issue view 324` is still OPEN (staged-to-close on maintainer push).
- **#325** — a provenance-placement policy doc exists; a portable check (quality
  capability / linter / `authoring-preflight`) flags standing-doc rule prose
  carrying dates / multiple issue refs, with a standing-vs-tracking allowlist;
  the charness standing docs are swept against the policy. `Close #325` staged.
- **#322** — each named inference-layer surface emits the 4-field
  `interpretation` self-declaration; each consuming skill reference carries the
  consumer-must-answer requirement; verified facts untouched. `Close #322`
  staged. (If it grew a shared schema/validator, a `spec` exists.)
- **handoff-3** — `skills/public/quality/references/mutation-testing.md` carries
  the pattern + freshness-guard + producer-cost lesson; the gate-as-`quality`-
  capability + adapter-contract decision is recorded (built, or an explicit
  decision not to build it now with the reason).
- **handoff-4** — `check_changed_line_mutation_coverage.py` warns when the
  analyzed head == `HEAD` and the worktree has uncommitted mutation-pool
  changes; a test covers it (the false-green dry-run is killed).

## Agent Verification Plan

### Low-Cost Checks

- At commit boundaries: `run_slice_closeout.py` pre-commit gate **aggregate**
  (ruff, `check_python_lengths`, `validate_attention_state_visibility`,
  `check-markdown`, mirror-drift, `validate_skills`, `check_doc_links`) — a green
  `pytest` is necessary but not commit-ready.
- Targeted `pytest` for each new fixture / validator (#324 source-preservation
  validator + Slack-thread fixture; #325 portable check; handoff-4 warning).

### High-Confidence Checks

- Broad `pytest` suite at bundle boundaries.
- **#324 "closable" is bound to high-confidence checks, not just the `--release`
  gate** — all three acceptance criteria must pass before staging `Close #324`:
  (1) the external-thread fixture asserts source text *or* a re-read obligation
  is preserved; (2) the issue body / local artifact carries the source-context
  section; (3) the closeout path warns/blocks when external-source preservation
  is missing. The `--release` gate proves the *release surface*, not the
  *invariant*.
- One bounded fresh-eye `critique` per coherent bundle (the #324 fix, the merged
  #325 + handoff-3 policy/portability bundle, the #322 rollout schema), and a
  final cross-slice closeout review with the Auto-Retro disposition mandate.
- Changed-line mutation-coverage gate where source changed.
- A cheap test-duplication pressure sample whenever a slice adds/expands tests
  (carried forward in the Slice Log via `append_slice_log.py --test-pressure`).

### External Or Live Proof

- Local `--release` gate (`run_slice_closeout.py --release`) as the **#324
  release-stage bundle proof**.
- **Skipped (named here so closeout cannot silently claim them):** no
  push/tag/GitHub-release by the agent (maintainer's); no real-host smoke by the
  agent (handoff item 1, human, async); no provider/live proof.

## Slice Plan

Dynamic — the order after B1 is re-picked at each boundary by dependency and
risk. B3 + B4 may collapse into one child goal (shared portability root cause);
B3 and B5 may each become dedicated child `/achieve` goals.

| Slice / Bundle | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| B1a contract-gap analysis | #324 | precedes the fix (design gap, not a bug — `debug: n/a`) | short structured note: where the current issue workflow under-preserves external-source context | planned |
| B1b source-preservation contract + fixture | #324 | release-first; downstream waiting | **provider-neutral** source-context schema/section + closeout warn/block validator + external-thread fixture; targeted `pytest` green | planned |
| B1c release stage | #324 | user: release first | version bump + manifest staged, `Close #324` in commit, closeout consumer run **`base→worktree`** (never `--head-sha HEAD`), local `--release` gate PASS, stop before push/tag | planned |
| B2 tripwire | handoff-4 | bakes B1c's guard into a permanent gate warning | warn in `check_changed_line_mutation_coverage.py` when analyzed head == `HEAD` and the worktree has uncommitted mutation-pool changes + test | planned |
| B3 provenance policy + portable check + gate-lesson portability | #325 **+ handoff-3** | merged: both share the portability-checkpoint root cause | policy doc + portable check w/ standing-vs-tracking allowlist; dogfood sweep; `mutation-testing.md` updated; gate-as-`quality`-capability/adapter decision recorded; `Close #325` | planned (one child `/achieve` goal) |
| B4 advisory-interpretation rollout | #322 | independent, inference-layer, no dependency | 4-field self-declaration per surface + consumer requirement; `Close #322` | planned (likely child `/achieve` goal) |

## Coordination Cues

Phase-appropriate routing for this run is deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` engine) — the
cues below are planned expectations, **not** a hard-coded phase→skill map.
`achieve` owns this slot and the floors; `find-skills` owns *which* skill answers
a boundary. Fill the floor lines with concrete refs during the run.

- **Routing** — query `find-skills` per phase. Expected owners (to confirm at
  runtime): `impl` (#324 fix, handoff-4, #322 rollout), `spec` (#325 policy,
  #322 schema if it grows), `quality` (verification cadence, #325 portable check,
  handoff-3 capability), `create-skill` (handoff-3 if the gate becomes a
  `quality` capability), `release` (#324 release surface), `issue` (closeouts +
  any splits). `debug: n/a — #324 is a workflow-design gap (missing invariant),
  not a behavior defect, so the bug-class `debug` root-cause mandate is satisfied
  by this explicit opt-out, not a forced falsifiable hypothesis.` Record actual
  routes at completion.
- **Gather step** — GitHub issue bodies are fetched via `gh` (the `issue`
  backend), not the open web; but `#324`'s downstream `corca-ai/ceal#276` and any
  Slack/external source named while resolving #324 route through `gather`. Record
  `Gather: <ref>` or `Gather: n/a — <reason>` per phase.
- **Release step** — #324 touches a release surface → record `Release: <ref>`
  (local `--release` gate proof; **staged, not pushed**).
- **Issue closeout step** — #324 / #325 / #322 are tracked → record
  `Issue closeout:` naming the numbers, carrier (release commit for #324;
  direct-commit / PR for #325 / #322), close-keyword state, the
  `validate-closeout-draft` / `verify-closeout` proof, and per-issue
  `Critique #N:` binding.

## Discuss Before Activation

Discuss before activation: RESOLVED this session via the `/achieve` interview
(see `## Interview Decisions`). Consequential defaults raised and their
resolutions:

- **Broad bundled scope** (five objectives in one orchestrator) — **APPROVED**:
  the user requested a single multi-goal orchestrator with dynamic workflow.
- **Release of #324** (release-surface side effect) — **RESOLVED / confirmed**:
  the agent stages the release surface + `Close #324` + runs the local
  `--release` gate only; **no** push/tag/GitHub-release (maintainer's).
- **Issue close / split** for #324 / #325 / #322 — **RESOLVED**: close keywords
  are staged (issues stay OPEN until the maintainer's push); #325/#322 may split
  into tracked sub-issues mid-run, surfaced via `issue` with a stop-and-ask
  (status → `blocked`) whenever a policy/product decision is needed.
- **#324 → rest sequencing barrier** — **RESOLVED**: proceed once #324's release
  is cut/staged; the human real-host smoke is async and does not block.
- **Proof-level non-claims** — **CONFIRMED**: no push/tag, no GitHub release, no
  real-host smoke, no provider/live proof is claimed by the agent; each skipped
  level is named at closeout.

Remaining mid-run decisions (these stop-and-ask during the run; they are **not**
blockers to activation): whether #325 / #322 split into new tracked sub-issues,
and whether handoff-3 promotes the gate to a `quality` capability + adapter
contract versus a reference-only update.

## Slice Log

### Slice 1: B1a — #324 contract-gap analysis

- Objective: Map where the issue workflow under-preserves external-source context (design gap, not a bug; debug: n/a — design-gap).
- Why this approach: Sharpen the missing invariant into concrete code-level gaps before writing the contract.
- Commits:
- What changed: charness-artifacts/quality/2026-06-07-324-source-preservation-gap.md (G1-G5 gap table + B1b design implications).
- Alternatives rejected:
- Targeted verification: Code read of issue create/closeout path: issue_create.py (byte-identity only), issue_verify_closeout_body.py::_missing_ledger_fields (no source field), issue-shaping.md + closeout-discipline.md (identity-only, 'do not paste' contradicts form 1).
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward: Current Source block is identity-only and actively discourages verbatim preservation; closeout validators never consult any source field; portability needs axis: external-source-provider framing (Slack is one adapter, not the schema).
- Metrics:

### Slice 2: B1b — #324 source-preservation contract + fixture

- Objective: Provider-neutral source-preservation contract (axis: external-source-provider): externally-sourced issues must preserve original context as Source text / Re-read obligation / Source degraded reason; verify-closeout + validate-closeout-draft block when none; check-source-preservation covers the creation side.
- Why this approach: Add a pure presence-check in the body helper (reuses _body_fields) so both closeout validators inherit it; expose a creation-side subcommand for the fixture; keep Slack as one adapter instance, not the schema.
- Commits:
- What changed: issue_verify_closeout_body.py (evaluate_source_preservation), issue_verify_closeout.py (wire into ok+payload), issue_tool.py (check-source-preservation subcommand), references closeout-discipline.md/issue-shaping.md/SKILL.md, fixtures/slack-thread-source-preservation.json, tests/test_issue_source_preservation.py (11), docs/public-skill-dogfood.json (frozen evidence + reviewed_on 2026-06-07), charness-artifacts/quality/2026-06-07-324-source-preservation-gap.md. Plugin mirror synced.
- Alternatives rejected:
- Targeted verification: 11 new tests pass; existing issue closeout suite 32/32; full run_slice_closeout.py deterministic aggregate green (ruff, lengths, validate_skills, validate_skill_ergonomics incl. issue-anchor gate, markdown, doc-links, packaging, mirror-drift, dogfood). Broad pytest deferred to B1 bundle boundary.
- Test duplication pressure: 11 tests reuse the _bug_closeout_body pattern but assert a distinct surface (source-preservation); low duplication with existing closeout tests — no overlapping assertions. One pure-function unit test guards parser robustness (>-quoted multi-line).
- Critique: charness-artifacts/critique/2026-06-07-324-source-preservation.md — bounded fresh-eye subagent (read-only), VERDICT ship-as-is, no blockers; over-worries (fenced-excerpt false-neg, degraded declarability, discriminator evasion) ruled deliberate presence-gate design.
- Off-goal findings:
- Lessons carried forward: Issue numbers must NOT appear in standing skill package prose/refs/fixtures — validate_skill_ergonomics (issue_anchor_in_core / portable_package_issue_anchor) already enforces #325's principle; provenance belongs in commit/goal/dogfood tracking docs. Inline code spans must not wrap across source lines (check-markdown).
- Metrics:

### Slice 3: B1c — #324 release stage (v0.26.0, stage-only)

- Objective: Stage the v0.26.0 release surface (version bump + generated manifests + update_instructions + release record) carrying Close #324 + feature closeout ledger; prove locally; stop before push/tag.
- Why this approach: Minor bump (new check-source-preservation subcommand + new maintained closeout behavior, additive, no migration). Manual stage-only commit (publish helper pushes); B1b committed separately so the release-stage mutation analysis sees the #324 Python as committed history, not an uncommitted false-green dry-run.
- Commits:
- What changed: packaging/charness.json + generated plugin manifests + marketplace (0.25.0->0.26.0), .agents/release-adapter.yaml update_instructions (0.26.0 + #324, 0.25.0 demoted to carried-forward), charness-artifacts/release/latest.md (staged record, explicit non-claims), test_issue_closeout_discipline.py prose-pin fix + test_issue_source_preservation.py missing-body-file branch test.
- Alternatives rejected:
- Targeted verification: Broad pytest 2399 passed/4 skipped (-m 'not release_only') via the mutation-coverage producer; release_only 26 passed; changed-line mutation coverage ACTIVE+GREEN base->worktree (base b60d5c7c -> #324 Python in 7dcfb43d; ok:true, blocking:[]); commit message validated via validate-closeout-draft (draft_verified, feature ledger complete, Close #324, Critique bound).
- Test duplication pressure: +2 tests this slice: one prose-pin update (replaces a brittle exact-string SKILL.md pin with the new contract phrasing + Source origin/Re-read obligation asserts) and one error-branch test (missing body file) that the changed-line mutation gate required; no duplication.
- Critique: Rides B1b's bounded fresh-eye critique (charness-artifacts/critique/2026-06-07-324-source-preservation.md) — the release stage adds no new logic, only the version surface; a short release-hygiene critique scope (version drift none, generated surfaces synced, publish boundary = stage-only, operator risk = staged-to-publish).
- Off-goal findings:
- Lessons carried forward: Broad pytest at the bundle boundary caught a stale SKILL.md prose-pin (test_issue_closeout_discipline) that the skip-broad commit gate missed; the changed-line mutation gate caught an uncovered error branch (issue_tool.py 209-210). Committing B1b before the release stage made the release-commit mutation analysis trustworthy (committed history, not a false-green --head-sha HEAD dry-run).
- Metrics: 3 producer runs: run1 failed (prose-pin test), run2 blocked (uncovered 209-210), run3 green — each retry fixed a real gap, not waste; release_only run reused once.

### Slice 4: B2 — handoff-4 changed-line gate false-green tripwire

- Objective: Bake B1c's guard into a permanent non-blocking warning: check_changed_line_mutation_coverage.py warns when the analyzed head resolves to HEAD and an eligible mutation-pool file has uncommitted worktree changes (the base..HEAD false-green dry-run).
- Why this approach: false_green_warning() helper (testable with an injected eligible set, independent of list_eligible globbing a temp repo); threaded into all emitted reports + stderr; non-blocking (the in-range verdict stands).
- Commits:
- What changed: scripts/check_changed_line_mutation_coverage.py (false_green_warning + _head_resolves_to_head + uncommitted_pool_changes + _git_lines + _attach_warning + main wiring), tests/quality_gates/test_changed_line_mutation_coverage.py (+7 tests), docs/conventions/implementation-discipline.md (dry-run trap now warns), charness-artifacts/spec/mutation-changed-line-premerge-gate.md (handoff-4 update note).
- Alternatives rejected:
- Targeted verification: 20/20 changed-line gate tests pass (13 existing + 7 new: helper fires/silent x3, e2e report+stderr, two defensive _git_lines branches). New mutation-pool lines all test-covered so the gate stays green for the maintainer's eventual push.
- Test duplication pressure: +7 tests; reuse the existing _seed_repo_with_changed_pool_file/_write_coverage/_run harness (no new scaffolding); each test asserts a distinct branch (fires, 3 silent guards, e2e threading, 2 defensive).
- Critique: Deferred to the final cross-slice closeout review (handoff-4 is a small, well-tested non-blocking warning, not one of the goal's named critique bundles).
- Off-goal findings:
- Lessons carried forward: A warning surfaced in ALL emit paths (early-return + skip + final) via _attach_warning, since the false-green case often produces the 'no eligible changed' early return (the uncommitted changes are exactly what is excluded).
- Metrics:

### Slice 5: B3 — #325 + handoff-3 shaped as a child /achieve goal

- Objective: Per operator decision (shape as child goals), shape the #325 provenance-policy + portable-check + handoff-3 gate-as-quality-capability bundle as a dedicated child /achieve goal, inert until /goal.
- Why this approach: Spec-first deep-shaping objective; the orchestrator shapes but does not auto-execute child goals (preserves the /achieve shape -> /goal pursue boundary). handoff-3 scoped to BUILD the quality capability + adapter (operator decision).
- Commits:
- What changed: charness-artifacts/goals/2026-06-07-325-provenance-policy-handoff3-gate-capability.md (draft, pursue_ready=True). Seed found this session: validate_skill_ergonomics/skill_text_quality_lib already enforce issue-anchor/dated-incident prohibition for skill packages; #325 generalizes to standing docs with a standing-vs-tracking allowlist.
- Alternatives rejected:
- Targeted verification: check_goal_artifact.py --pursue-ready: pursue_ready=True, placeholders=0, discussion_ready=True. Child goal NOT activated/executed by the orchestrator.
- Test duplication pressure:
- Critique:
- Off-goal findings: Child goal reference: charness-artifacts/goals/2026-06-07-325-provenance-policy-handoff3-gate-capability.md — activate with /goal to pursue. Sub-issue split allowed if scope grows (operator).
- Lessons carried forward: Child goal Discuss-before-activation summary MUST sit before ## Slice Log; the validator (goal_artifact_discussion._summary_content) only scans the pre-Slice-Log region.
- Metrics:

### Slice 6: B4 — #322 shaped as a child /achieve goal

- Objective: Per operator decision, shape the #322 advisory-interpretation rollout (4-field self-declaration across the remaining inference-layer surfaces + paired consumer requirements) as a dedicated child /achieve goal, inert until /goal.
- Why this approach: Spec-light rollout; orchestrator shapes but does not auto-execute. Inference-layer only (verified facts stay trusted); spec-promotion deferred to a shared-schema decision slice.
- Commits:
- What changed: charness-artifacts/goals/2026-06-07-322-advisory-interpretation-rollout.md (draft, pursue_ready=True). Grounded in the #322 body's 6 remaining surfaces + the nose pilot template.
- Alternatives rejected:
- Targeted verification: check_goal_artifact.py --pursue-ready: pursue_ready=True, placeholders=0, discussion_ready=True. Child goal NOT activated/executed.
- Test duplication pressure:
- Critique:
- Off-goal findings: Child goal reference: charness-artifacts/goals/2026-06-07-322-advisory-interpretation-rollout.md — activate with /goal to pursue. Sub-issue split allowed if a shared schema/validator becomes spec-worthy.
- Lessons carried forward: Both spec-first objectives became child goals per the operator's explicit choice; the orchestrator's own completion now depends on the user activating + completing the two children (the achieve shape->pursue boundary is preserved across sessions).
- Metrics:

## Context Sources

A fresh session can reconstruct the originating context by following these in
order:

- **GitHub issues** (fetched via `gh`): #324 (bug/operations — preserve
  external-source context in issue workflows), #325 (documentation/enhancement —
  provenance-placement policy + portable check), #322 (advisory-interpretation
  rollout to remaining inference-layer surfaces).
- **Downstream waiter:** `corca-ai/ceal#276` (waiting on #324).
- **docs/handoff.md** "Next Session" items 2–4 — item 2 **is** #322; item 3 =
  skill portability of the gate lessons (handoff-3); item 4 = changed-line gate
  false-green tripwire (handoff-4). Item 1 (human smoke) and item 5 (#184) are
  out of scope.
- **Retros:** `charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md`
  (#325 + handoff-3 shared root cause), `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`
  (handoff-4 follow-up tag `follow-up:changed-line-gate-worktree-dryrun-warning`),
  `charness-artifacts/retro/recent-lessons.md`.
- **#322 saved analysis & contract:**
  `charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md`,
  `skills/shared/references/advisory-interpretation-contract.md`, the pilot
  `inventory_nose_clones.py` + `skills/public/quality/references/automation-promotion.md`.
- **Mutation-gate context:** `charness-artifacts/spec/mutation-changed-line-premerge-gate.md`,
  `skills/public/quality/references/mutation-testing.md` (handoff-3 target),
  `check_changed_line_mutation_coverage.py` (handoff-4 target).

## Interview Decisions

For each Before-phase question: family considered, chosen value, rejected
reason, and the anti-anchoring axis result.

1. **Orchestration structure** — family: {flat inline bundles, 1 orchestrator +
   dynamic sub-goals, pre-shape five child goals now}. **Chosen:** 1 orchestrator
   + dynamic sub-goals. Rejected *flat* (loses per-objective audit and cannot
   deep-shape the spec-first issues); rejected *pre-split* (over-shapes before
   learning and drops the dynamism the user asked to keep).
   `single-point: this goal's chosen orchestration shape.`
2. **#324 release authority** — family: {stage + stop before push/tag, cut
   end-to-end incl. push+tag}. **Chosen:** stage release surface + `Close #324` +
   local `--release` gate, stop before push/tag. Rejected *end-to-end push* (repo
   has "No push/tag CI"; v0.25.0 real-host smoke was left to a human; `achieve`
   never pushes). `axis: host` — release/closeout publication authority is
   adapter-owned (`audit-only` / `handoff-only` / publish-capable); this goal uses
   the safe stage-and-stop default and the maintainer holds push.
3. **#324 → rest barrier** — family: {proceed after release cut (smoke async),
   hard barrier through human smoke}. **Chosen:** proceed after release cut.
   Rejected *hard barrier* (would stall the whole goal on a human step; the user
   wants the rest to move). `single-point: this goal's sequencing choice.`

## Plan Critique Findings

Reviewer provenance: bounded fresh-eye `critique` subagent (general-purpose,
read-only), run this session against the draft plan.

### Blockers folded

- **#324 is a workflow-design gap, not a behavior defect** — do not force a
  `debug` falsifiable root-cause it cannot satisfy. Folded: B1a reframed to a
  short *contract-gap analysis*; Coordination Cues records
  `debug: n/a — design-gap` as an explicit opt-out (satisfies the bug-class
  mandate without theater).
- **The #324 release commit would ride a known false-green-capable gate** — its
  changed-line closeout consumer must run `base→worktree`, never
  `--head-sha HEAD`. Folded: B1c expected evidence + a Boundaries line; handoff-4
  (B2) sequenced immediately after to bake the guard into a permanent gate
  warning. (Reviewer suggested moving handoff-4 fully *ahead* of the release;
  resolved instead with the procedural `base→worktree` guard so #324 still goes
  first per the user's instruction, with handoff-4 right after to make it
  permanent.)
- **#324 "closable" verification was under-specified** — bound all three
  acceptance criteria (fixture, source-context section, closeout warn/block) to
  High-Confidence checks; the `--release` gate proves the release surface, not
  the invariant. Folded into Agent Verification Plan.
- **Child-goal-on-uncommitted-release concurrency hazard** — folded into
  Boundaries: no child goal opens until B1's release surface is committed and
  quiesced.
- **Empty skeleton sections would fail `--pursue-ready`** — already addressed:
  all template sections are filled in this draft (the reviewer read the
  pre-fill skeleton).

### Anti-anchoring axes recorded (folded)

- **#324 source-preservation contract** — `axis: external-source-provider`
  (Slack / Notion / Workspace / browser-gathered). Folded as provider-neutral in
  Boundaries; Slack is one adapter instance, not the schema.
- **#325 portable check home** — `axis: enforcement-surface` (quality capability
  vs. linter vs. `authoring-preflight`). Do **not** pre-pick; the child goal
  decides. Recorded here rather than locking it in the Slice Plan.
- **handoff-3 gate portability** — risks staying repo-local *again* (the very
  trap its retro names). Folded: B3 expected evidence requires a hard
  portability-classification of the gate lesson.

### Over-worry (raised, not folded)

- "achieve shouldn't stage a release / `Close #N`" — not a blocker; the
  coordination contract endorses staged-close + maintainer-push, and only forbids
  the *agent* pushing/tagging. The plan matches the contract.
- "Five objectives in one goal is too big" — not a blocker; dynamic re-pick +
  child-goal spawn is the designed escape valve. Do not pre-split.
- "Async human real-host smoke blocks B1" — not a blocker; handoff item 1 is
  already scoped async and agent-impossible.

### Sequencing confirmed

- **#325 + handoff-3 merged into one child goal** (B3) — both retros name the
  same root cause (portability-classification-as-closeout-checkpoint); handoff-3
  is the concrete instance #325's portable check would catch. Merging avoids
  deriving the policy twice.
- **#322 stays last** — independent, inference-layer, no dependency.

## Off-Goal Findings

(None yet — file off-goal findings via `issue`, recording only the reference and
reason here.)

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>` at the After-phase. The complete gate
rejects a literal `TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

(Final results recorded at closeout; the user-runnable checks per objective are
in `## User Acceptance`.) At closeout this section names, per objective: the
exact commands the user can run, what is staged versus pushed, and which proof
levels the agent did **not** run (push/tag, GitHub release, real-host smoke,
provider/live).

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
