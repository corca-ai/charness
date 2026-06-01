# Achieve Goal: Achieve long-goal efficiency and effectiveness

Status: complete
Created: 2026-06-01
Activation: `/goal @charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete.
- Next action: none for this goal; user may inspect the changed achieve,
  handoff auto-draft, and retro guidance surfaces.
- Verification cadence: cheap deterministic checks before commit; slice-level
  focused tests plus surface validators; final broad quality and fresh-eye
  critique at closeout.
- Slice review packet: provide intent, changed files, expected invariants,
  tests/proof, non-claims, and reviewer questions before fresh-eye critique.
- History boundary: this frame is the current control panel; completed detail
  stays in `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Make the achieve skill and the goal artifacts it creates help long-running, intentionally broad goals run with better active-context control, verification cadence, critique packets, and automatic efficiency retro suggestions without weakening proof.

## Non-Goals

- Do not make `achieve` reject broad goals merely because they are broad. The
  motivating case was intentionally large, and broad maintenance goals remain a
  supported shape.
- Do not weaken the proof bar: commit-level low-cost deterministic checks,
  slice-level higher-cost proof, fresh-eye critique when required, final broad
  gates, and live proof still stand.
- Do not treat cached input volume alone as waste. Cached input is expected in
  long goals; use it only as a context-pressure signal together with
  compactions, high-token turns, repeated commands, polling, and validation
  cadence.
- Do not turn `achieve` into a generic task runner or a hidden scheduler. It
  remains a goal operator that coordinates other skills and records evidence.
- Do not hard-code Codex-only behavior into public prose. Host-specific
  efficiency probes belong in adapters, scripts, or host-aware references.
- Do not require every goal to run the heaviest telemetry path. The extra
  efficiency review should scale with goal length and available host evidence.

## Boundaries

- In scope: `skills/public/achieve/SKILL.md`, achieve references, goal artifact
  templates/helpers, closeout evidence guidance, retro/host-log efficiency
  integration, tests for generated goal shape and complete-phase evidence, and
  the checked-in plugin mirror/surfaces these changes imply.
- In scope: make generated goals carry a short active operating frame that
  reduces repeated full-document rereads during long runs.
- In scope: make generated goals carry an explicit verification cadence:
  commit-level cheap deterministic checks, slice-level broader/fresh-eye
  checks, final-carrier broad/live proof, and rules for when previously passed
  checks do or do not need to rerun.
- In scope: make slice critique cheaper and more reliable by defining a
  bounded slice review packet: intent, changed files, expected invariants,
  tests/proof, non-claims, and reviewer questions.
- In scope: make After-phase auto-retro include an efficiency section when host
  evidence is available: tokens/time, compactions, tool-call counts, repeated
  VCS/check commands, polling, subagent count, and a distinction between
  necessary safety cost and reducible waste.
- In scope: ensure auto-retro improvements become applied changes or tracked
  issues, including efficiency improvements. A prose-only lesson is not enough.
- Out of scope unless discovered as required: reworking all historical goal
  artifacts, redesigning the whole retro skill, changing pre-push policy, or
  introducing remote telemetry.
- Stop and ask the user before reducing any existing mandatory verification,
  deleting required critique/fresh-eye review, or filing public issues that
  disclose private session metrics.

## User Acceptance

- A newly generated `achieve` goal artifact includes an active operating frame
  or equivalent bounded current-state section near the top, plus a clear
  archival boundary for older slice history.
- The `achieve` skill or its references tell agents how to run broad goals
  efficiently without reducing proof: cheap checks per commit, higher-cost
  checks per slice, and final broad/live proof.
- The After-phase contract tells agents to summarize efficiency metrics when
  available and to propose/apply/file concrete improvements after auto-retro.
- The retro/host-log path used by achieve can surface Codex rollout JSONL
  signals automatically: token snapshots, compactions, tool-call pressure, and
  repeated-command proxies.
- Tests prove the new goal shape and efficiency evidence expectations, including
  that cached input is not treated as waste by itself.
- Plugin/generated surfaces are synced and validators pass.
- The final report names what changed, which checks ran, and any honest
  non-claims around host metrics.

## Agent Verification Plan

### Low-Cost Checks

- At activation: `python3 skills/public/achieve/scripts/check_goal_artifact.py
  --repo-root . --goal-path
  charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md
  --pursue-ready`.
- Before each code commit: targeted tests for touched helpers/references,
  `ruff check` on touched Python, `python3 -m py_compile` on touched scripts,
  and doc/link checks for touched markdown.
- Use `python3 scripts/check_changed_surfaces.py --repo-root .` to discover sync
  and verify obligations after each meaningful surface expansion.
- If generated/plugin mirrors are touched, run
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` before
  validators.
- Keep cheap token/tool metrics honest: record "when available" unless the probe
  output actually exposes the signal.

### High-Confidence Checks

- Slice-level: run focused tests for achieve/retro behavior, then the surface
  validators named by `check_changed_surfaces.py`.
- Run `python3 scripts/run_slice_closeout.py --repo-root .` when a slice spans
  code, skill prose, tests, and plugin exports.
- Final: `./scripts/run-quality.sh --read-only`.
- Final: bounded fresh-eye critique of the updated achieve lifecycle and a
  disposition review for auto-retro improvements.
- Final: `python3 skills/public/achieve/scripts/check_goal_artifact.py
  --repo-root . --goal-path
  charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`.

### External Or Live Proof

- No live GitHub issue mutation is planned for this goal unless implementation
  discovers a concrete off-goal issue that should be filed and the user accepts
  live issue creation.
- No release is planned. If plugin release/version surfaces are touched, stop
  and route through `release`.
- Host metrics are local host-log proof only. Do not claim remote CI, product
  success, or universal host behavior unless separately proven.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Lock the long-goal efficiency contract and current evidence | Prevent the implementation from solving the wrong problem, e.g. shrinking broad goals instead of managing them | This goal artifact passes `--pursue-ready`; current retro/probe evidence is cited; scope/non-goals are frozen | done |
| 1 | Add active operating frame support to achieve-generated goals | Long goals need a short current-state control panel so agents do not repeatedly re-read full history | Updated template/reference/helper behavior; tests proving new goals include the frame and archival slice-log boundary | done |
| 2 | Make verification cadence explicit in achieve guidance | The desired model is cheap commit-level checks plus heavier slice/final proof, not ad hoc repeated broad gates | `achieve` docs/reference updates; tests or validators ensuring generated artifacts carry cadence language | done |
| 3 | Define bounded slice review packets for fresh-eye critique | Subagent critique should stay high-signal without requiring the full goal history every time | Reference/template updates; tests or example packet; critique guidance distinguishes slice packet vs final review | done |
| 4 | Integrate efficiency metrics into After-phase auto-retro | Completion should surface token/tool/context pressure and propose improvements automatically | Retro/probe integration evidence; goal closeout docs require measured/proxy distinction and cached-input non-overclaim | done |
| 5 | Validate, critique, sync, and publish the improved achieve surface | The changes affect public workflow behavior and checked-in plugin exports | Surface sync; focused tests; broad quality; fresh-eye critique; final goal complete; handoff refreshed if next pickup changes | done |

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

- Routing: `find-skills` inventory points this request to `achieve`; likely
  implementation slices will coordinate with `retro`, `quality`, `critique`,
  and `impl` as selected by `find-skills` at activation time.
- Gather: n/a — the motivating evidence is repo-local artifacts and host logs,
  not an external source being imported.
- Release: n/a — no version or install-manifest release is planned.

## Slice Log

### Slice 0: Activate and lock contract

- Objective: Move the shaped long-goal efficiency artifact into active pursue
  mode and preserve the user-agreed contract.
- Why this approach: The user explicitly asked to make this an achieve goal;
  activation should not reopen the already-settled product/product-success
  boundaries.
- Commits: implementation commit `fe09061`; final artifact updates are carried
  by the closeout commit that records this section.
- What changed: Status flipped from `draft` to `active`; active operating frame
  seeded in this artifact.
- Alternatives rejected: Shrinking the broad goal or treating cached input as
  waste by itself.
- Targeted verification: `check_goal_artifact.py --pursue-ready` planned before
  the first implementation commit.
- Test duplication pressure: n/a — no tests added in activation.
- Critique: same-agent activation check; fresh-eye reserved for final
  workflow-surface review.
- Off-goal findings: none.
- Lessons carried forward: Keep active state near the top and archive completed
  detail in slice logs.
- Metrics: when available.

### Slice 1-4: Add long-goal control surfaces

- Objective: Make newly generated achieve goals carry an active operating frame,
  explicit verification cadence, bounded slice review packet guidance, and
  measured/proxy efficiency retro language.
- Why this approach: The user wanted broad goals to stay supported while making
  long runs cheaper and less ambiguous. The right fix is operating guidance and
  generated scaffold shape, not reducing proof.
- Commits: pending; slice closeout passed before commit.
- What changed: Updated achieve template/reference/SKILL surfaces, retro
  efficiency guidance, generated plugin mirrors, and handoff auto-draft goal
  generation so newly drafted goals include the same active frame.
- Alternatives rejected: Making `Active Operating Frame` a global
  `check_goal` required section was rejected after review because it would make
  historical goal artifacts fail retroactively. The generated-shape requirement
  is enforced by scaffold tests instead.
- Targeted verification: `pytest -q` focused achieve/goal/retro/handoff tests
  passed; full pytest passed once before the compatibility narrowing; focused
  tests passed again after narrowing. `run_slice_closeout.py
  --ack-cautilus-skill-review` passed after dogfood/scenario review notes were
  recorded.
- Test duplication pressure: no duplicate-pressure sample needed; this slice
  added assertions to existing test modules rather than large new fixtures.
- Critique: same-agent compatibility critique caught the retroactive
  `check_goal` risk and narrowed the deterministic contract.
- Off-goal findings: none.
- Lessons carried forward: When adding a new generated artifact section, update
  all generators but avoid turning a generated-shape improvement into a
  historical corpus breaker unless the goal explicitly asks for migration.
- Metrics: full pytest run took 287.64s; slice closeout aggregate pytest took
  272.0s; host token/tool metrics still deferred to final retro/probe.

### Slice 5: Final validation and closeout

- Objective: Prove the improved achieve surface, run fresh-eye disposition
  review, record auto-retro, and complete the goal artifact.
- Why this approach: The changes affect public workflow behavior and plugin
  exports, so closeout needs synced mirrors, deterministic gates, and review
  evidence rather than only prose.
- Commits: implementation commit `fe09061`; final artifact updates are carried
  by the closeout commit that records this section.
- What changed: Added final retro/probe/critique evidence, fixed the
  `goal-artifact.md` shape example to include portability sections, and marked
  this artifact complete.
- Alternatives rejected: Running live Cautilus proof was rejected by the repo
  planner result (`next_action: none`); dogfood/scenario review plus
  deterministic validation was the required closeout path.
- Targeted verification: focused pytest, markdown/link validation, skill
  validation, packaging validation, and `check_goal_artifact.py` passed after
  the fresh-eye doc-drift fix.
- Test duplication pressure: n/a — closeout added artifacts and reference
  wording only.
- Critique: fresh-eye subagent Hume reported non-blocking findings; both were
  dispositioned before complete status.
- Off-goal findings: none.
- Lessons carried forward: Closeout reviews should check documented artifact
  shape against deterministic helper requirements, not only new behavior.
- Metrics: host probe available at
  `charness-artifacts/probe/2026-06-01-achieve-long-goal-efficiency.json`;
  Codex audit exposes thread-wide pressure signals, not a goal-window total.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User direction on 2026-06-01: intentionally broad goals should remain
  supported; expected cadence is cheap deterministic checks per commit,
  higher-cost validation and subagent critique per slice, and final proof, while
  achieve/goal artifacts should help agents run more efficiently and propose
  auto-retro improvements after completion.
- Completed open-issue closeout goal:
  `charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`.
- Session retro:
  `charness-artifacts/retro/2026-06-01-open-issue-generative-closeout.md`.
- Host/codex evidence:
  `charness-artifacts/probe/2026-06-01-open-issue-generative-closeout.json`
  and
  `charness-artifacts/probe/2026-06-01-open-issue-generative-closeout-codex-audit.json`.
- Current achieve skill and references:
  `skills/public/achieve/SKILL.md`,
  `skills/public/achieve/references/goal-artifact.md`, and
  `skills/public/achieve/references/lifecycle.md`.
- Current retro skill and references:
  `skills/public/retro/SKILL.md` and
  `skills/public/retro/references/phase-aware-efficiency.md`.
- Operating rules:
  `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md`.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Goal size policy: chosen value is support intentionally broad goals with
  better control surfaces. Rejected shrinking or refusing broad goals as the
  default answer because the motivating run was intentionally broad and
  successful.
- Efficiency signal policy: chosen value is measured/proxy split. Goal tokens,
  elapsed time, context compactions, tool-call counts, repeated commands, and
  polling are useful; cached input alone is not waste. Rejected treating cached
  tokens as a direct waste bill.
- Verification cadence: chosen value is cheap deterministic checks at commit
  boundaries, heavier proof and fresh-eye critique at slice boundaries, final
  broad/live proof at closeout. Rejected always running broad gates after every
  small edit, and rejected deferring all proof to the end.
- Context management: chosen value is a short active operating frame plus
  archival slice history. Rejected making the entire goal history the normal
  active prompt surface once a run gets long.
- Critique packet: chosen value is bounded slice review packets for slice
  critique and a separate final review for cross-slice closure. Rejected giving
  subagents the whole run history by default.
- Auto-retro: chosen value is auto-retro must include efficiency findings and
  concrete dispositions when host evidence exists. Rejected path-only retro
  persistence and prose-only lessons.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Same-agent preflight folded: this goal could accidentally weaken proof under
  the banner of efficiency. Folded into Non-Goals and explicit verification
  cadence.
- Same-agent preflight folded: this goal could overfit to Codex host logs.
  Folded into host-specific boundary and measured/proxy language.
- Same-agent preflight folded: auto-retro suggestions could become another
  prose-only ritual. Folded into User Acceptance and Slice 4/5 disposition
  requirements.
- Same-agent preflight folded: active operating frame must not hide historical
  evidence. Folded into archival boundary requirement rather than deletion of
  slice logs.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

_None yet._

## Final Verification

Retro: charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md
Host log probe: charness-artifacts/probe/2026-06-01-achieve-long-goal-efficiency.json
Disposition review: charness-artifacts/critique/2026-06-01-achieve-long-goal-efficiency-disposition.md

- Implementation commit: `fe09061 Improve achieve long-goal operating frame`.
- Generated achieve goals now include `## Active Operating Frame` near the top
  with current slice, next action, verification cadence, slice review packet,
  and history-boundary cues.
- Handoff chunked-routing auto-draft also emits the active operating frame, so
  sibling goal generators stay compatible with the new generated shape.
- `achieve` guidance now separates cheap commit checks, higher-cost/fresh-eye
  slice proof, and final broad/live proof without reducing the proof bar.
- `achieve`/`retro` guidance now separates measured, proxy, and unavailable
  efficiency signals and explicitly says cached input alone is not waste.
- Dogfood/scenario review recorded in `docs/public-skill-dogfood.json`; no
  maintained Cautilus scenario changed because routing and adapter behavior did
  not change.
- Plugin mirrors were synced with `python3 scripts/sync_root_plugin_manifests.py
  --repo-root .`.
- Verification run:
  - `pytest -q tests/quality_gates tests/control_plane tests/test_*.py
    tests/charness_cli/test_doctor_cache_selection.py
    tests/charness_cli/test_tool_lifecycle.py` passed: 1930 passed, 4 skipped.
  - `python3 scripts/run_slice_closeout.py --repo-root .
    --ack-cautilus-skill-review` passed.
  - `pytest -q tests/quality_gates/test_goal_artifact_lib.py
    tests/quality_gates/test_achieve_before_activation.py
    tests/test_handoff_chunker_auto_draft.py` passed.
  - `python3 scripts/validate_skills.py --repo-root .` passed.
  - `python3 scripts/validate_packaging.py --repo-root .` and
    `python3 scripts/validate_packaging_committed.py --repo-root .` passed.
  - `./scripts/check-markdown.sh` and `python3 scripts/check_doc_links.py
    --repo-root .` passed.
- Non-claims: no live GitHub issue mutation, release, remote CI, product
  success, or universal host behavior was proven. Host metrics are local
  evidence; the Codex probe covers the broader rollout thread and should be read
  as pressure evidence, not exact per-goal cost.

## User Verification Instructions

1. Run `python3 skills/public/achieve/scripts/check_goal_artifact.py
   --repo-root . --goal-path
   charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`.
2. Generate a throwaway goal with `skills/public/achieve/scripts/upsert_goal.py`
   in a temp repo and confirm `## Active Operating Frame` appears before
   `## Goal`.
3. Inspect `skills/public/achieve/references/lifecycle.md` for the verification
   cadence and bounded slice review packet language.
4. Inspect `skills/public/retro/references/phase-aware-efficiency.md` and
   confirm cached input is treated as context pressure, not standalone waste.

## Auto-Retro

- applied: Generated achieve goals now carry `## Active Operating Frame`, while
  historical artifacts remain compatible because this was not added to
  `REQUIRED_SECTIONS`.
- applied: Sibling goal generator compatibility was fixed by updating handoff
  chunked-routing auto-draft and pinning it with tests.
- applied: Verification cadence and bounded slice review packets are now stated
  in achieve lifecycle/reference guidance.
- applied: Efficiency retro guidance now separates measured/proxy/unavailable
  signals and says cached input alone is not waste.
- applied: Dogfood/scenario-review decisions for changed public skills were
  recorded in `docs/public-skill-dogfood.json` before acknowledging slice
  closeout.
- applied: Fresh-eye review found two non-blocking closeout issues; both were
  fixed before completion.
