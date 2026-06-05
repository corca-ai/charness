# Achieve Goal: Issues 299 300 and next improvements

Status: complete
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-issues-299-300-next-improvements.md`
Activation time: 2026-06-05T09:41:28+09:00

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: active; shape #299/#300 status, then implement #300 and the
  latest report-quality improvement.
- Next action: apply fresh-eye findings, finish validation, and close out with
  actual waste/decision reporting.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve the next-improvement work surfaced by the latest closeout feedback while carrying GitHub issues #299 and #300 through the current local achieve lifecycle.

## Non-Goals

- Do not treat GitHub publication or remote issue state as a routine user
  decision item in closeout; the operator already knows that surface.
- Do not rerun broad pytest during pre-lock slices; focused tests plus
  `run_slice_closeout.py --skip-broad-pytest` own pre-lock proof.
- Do not change the underlying AGENTS.md/CLAUDE.md policy for #300 unless the
  issue evidence proves the policy itself is wrong; the current gap is an
  explicit narrow execution path.
- Do not reopen #299's implementation unless local verification contradicts its
  existing direct-commit closeout evidence.

## Boundaries

- #299 is already implemented locally by commit `9e2ca12b` with a direct-commit
  closeout draft; this goal verifies and carries that state, not duplicate work.
- #300 is feature-class: add discoverable host-docs-only normalization behavior
  and focused tests without pausing on open product decisions unless the
  implementation exposes one.
- The user's latest feedback is in scope as a workflow-quality improvement:
  final reports must include the actual run waste and relevant decisions, and
  must not ask about push by default.
- Generated/plugin mirrors must be synced before validators.

## User Acceptance

What the user can do to verify completion directly.

- Run the new or updated setup host-docs-only command/helper on a temporary repo
  and see canonical `AGENTS.md` plus `CLAUDE.md -> AGENTS.md` behavior.
- Inspect the final report and see actual work-session waste, real user
  decisions, residual risk, and non-claims; no routine push question.
- Confirm #299 remains locally verified and #300 has a local closeout draft or
  explicit non-claim if remote state is not verified.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest for #299 inventory regressions and #300 setup host-docs path.
- `ruff` / `py_compile` for touched scripts.
- `check_python_lengths.py` for touched Python files before closeout.

### High-Confidence Checks

- `run_slice_closeout.py --repo-root . --skip-broad-pytest` as pre-lock
  rehearsal after sync.
- `check_goal_artifact.py` for this goal before completion.
- Required critique/fresh-eye review for the task-completing repo change.

### External Or Live Proof

- GitHub issue bodies are read through `gh issue view` and issue backend
  preflight passed with `gh`.
- No remote CLOSED verification is claimed in this local goal unless explicitly
  performed later.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Shape the active goal, classify #299/#300, and verify #299 local state | Avoid duplicate #299 work and keep user feedback in scope | goal artifact; issue_tool resolve-invocation; #299 closeout artifact | done |
| 2 | Implement #300 host-docs-only normalization path | #300 is the unresolved implementation target | setup docs/helper/tests; plugin mirror sync | in review |
| 3 | Encode report-quality improvement from the user's feedback | Prevent another summary-only closeout and routine push question | achieve/report contract update or focused artifact change with tests | in review |
| 4 | Verify, critique, retro, and complete the goal | Close with proof, non-claims, decisions, and waste | focused tests; closeout rehearsal; critique; retro; goal check | pending |

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

Routing: find-skills recommended `achieve` for the goal lifecycle; `issue` /
GitHub CLI for #299/#300 issue work; setup handled the host-docs-only
implementation surface; quality/closeout validation owned the deterministic
verification posture.
Routing: find-skills recommended `impl` for code/config/test changes in setup
and achieve surfaces.
Routing: find-skills recommended `quality` for deterministic validation posture
and closeout proof selection.
Routing: find-skills recommended `issue` for GitHub issues #299/#300 closeout
draft validation.
Gather: n/a — GitHub issue bodies were read directly through the issue backend
for this repo-local issue-resolution workflow; no external source needed a
durable gathered working asset.
Release: n/a — this goal does not touch release/version/install-manifest
surfaces.
Issue closeout: charness-artifacts/issue/2026-06-05-issue-300-closeout-commit-message.md

## Slice Log

Activation: started at 2026-06-05T09:41:28+09:00 after the user requested the
next improvement work plus issues #299 and #300 as an `achieve` goal.

### Slice 1: Shape issue bundle and verify #299 local state

- Objective: Shape the active goal, classify #299/#300, and avoid duplicate
  #299 implementation.
- What changed: Created this active goal artifact; read GitHub issue #299/#300
  bodies through `gh`; confirmed issue backend preflight and selector
  `299-300`; verified #299's existing direct-commit closeout draft.
- Verification: `issue_tool.py resolve-invocation -- 299-300` passed.
  `issue_tool.py validate-closeout-draft` for #299 passed with classification
  `feature`, carrier `direct-commit`, and bound critique evidence.

### Slice 2: Issue 300 host-docs-only normalization helper

- Objective: Add an explicit narrow setup path for host-docs-only/AGENTS-only
  normalization without changing the underlying AGENTS/CLAUDE policy.
- What changed: Added `scripts/setup_host_docs_lib.py` and setup skill wrapper
  `normalize_host_docs.py`. The helper dry-runs by default, writes only with
  `--execute`, creates compact canonical `AGENTS.md` plus `CLAUDE.md ->
  AGENTS.md` when both are missing, creates only the symlink when AGENTS exists,
  keeps an existing correct symlink, and blocks on real `CLAUDE.md` content.
- Verification so far: focused tests passed for dry-run, execute, symlink-only,
  existing symlink, and real-CLAUDE block paths. Fresh-eye review found one
  blocker: generic setup bootstrap originally used `--execute`; fixed by making
  bootstrap dry-run and reserving `--execute` for the explicit narrow mutation
  path.

### Slice 3: Closeout report-quality contract

- Objective: Encode the user's feedback that closeout reports must include the
  actual run waste and must not ask routine push questions by default.
- What changed: Updated `achieve` lifecycle closeout contract and focused test
  coverage so final reports carry real waste/decision separation and exclude
  routine publication/push prompts unless specifically requested.
- Verification so far: focused achieve contract test passed before the
  fresh-eye cleanup; will rerun after sync.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User feedback: final reports should include the actual work-session waste and
  decisions; routine push questions should be omitted.
- `gh issue view 299 --repo corca-ai/charness`: #299 release-only sentinel
  coverage inventory desired outcome.
- `gh issue view 300 --repo corca-ai/charness`: #300 setup host-docs-only
  normalization desired outcome.
- `charness-artifacts/issue/2026-06-05-issue-299-closeout-commit-message.md`
- `charness-artifacts/retro/recent-lessons.md`
- `docs/conventions/implementation-discipline.md`
- `docs/conventions/operating-contract.md`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Scope decision: chosen `#299 carry/verify + #300 implement + report-quality
  improvement`. Rejected redoing #299 because local commit `9e2ca12b` and its
  closeout draft already satisfy the local implementation boundary.
- Proof decision: chosen focused tests and pre-lock closeout rehearsal. Rejected
  repeating broad pytest before the mutation set is locked because the latest
  lesson says that is cost waste.
- Report decision: chosen to omit routine push questions from decision-needed
  sections. Rejected defaulting to publication/push prompts because the user
  explicitly said that is known and noisy.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Pre-mutation classification: #299 is already local-feature-resolved; #300 is
  feature-class with no current open product decision. The setup policy stays
  stable; discoverability/execution path changes are in scope.
- Fresh-eye review by Carson: Act Before Ship blocker on `setup/SKILL.md`
  generic bootstrap running `normalize_host_docs.py --execute`; applied by
  switching bootstrap to dry-run and documenting `--execute` only in the narrow
  host-docs mutation path. Medium stale-goal finding applied here. Low missing
  existing-symlink test applied.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

- Self-verification: #299 remains locally verified through commit `9e2ca12b` and
  its closeout draft; this goal did not duplicate that implementation. #300 was
  implemented locally with `normalize_host_docs.py`, `setup_host_docs_lib.py`,
  setup docs, plugin mirror sync, tests, and a direct-commit closeout draft.
- Focused tests: `pytest -q tests/quality_gates/test_setup_normalize_host_docs.py
  tests/quality_gates/test_setup_render_skill_routing.py
  tests/quality_gates/test_setup_inspect_policy.py::test_setup_inspect_repo_flags_targeted_missing_surface
  tests/quality_gates/test_achieve_before_activation.py
  tests/quality_gates/test_release_only_sentinel_inventory.py` passed with 19
  tests.
- Issue draft validation: #299 and #300 `issue_tool.py validate-closeout-draft`
  passed for classification `feature`, carrier `direct-commit`.
- Fresh-eye review: Carson found one Act Before Ship blocker and two smaller
  issues. All were applied: setup bootstrap now dry-runs, the goal artifact was
  updated, and the existing-symlink path gained test coverage.
- Closeout rehearsal: `python3 scripts/run_slice_closeout.py --repo-root .
  --skip-broad-pytest --ack-cautilus-skill-review` passed after sync and
  deterministic validators.
- Cautilus planner: `next_action: none`; no live Cautilus run is claimed. The
  required scenario-review/dogfood decision was recorded in
  `docs/public-skill-dogfood.json`.
- Broad pytest: not rerun by design for this pre-lock slice. The skipped broad
  command is not claimed as final broad proof.
- Remote issue state: not verified closed and not claimed closed.
Retro: charness-artifacts/retro/2026-06-05-issues-299-300-next-improvements.md
Host log probe: skipped: host-log-not-exposed: no goal metric window or session file was recorded for this short run, so a per-goal host-log total would be misleading
Disposition review: charness-artifacts/critique/2026-06-05-issues-299-300-next-improvements-disposition-review.md

## User Verification Instructions

- For #300, run `python3 skills/public/setup/scripts/normalize_host_docs.py
  --repo-root <tmp-repo>` and confirm it plans `write_agents` plus
  `create_claude_symlink` without writing. Rerun with `--execute` in a throwaway
  repo and confirm `CLAUDE.md -> AGENTS.md`.
- Inspect `skills/public/setup/SKILL.md`: the bootstrap example is dry-run, and
  `--execute` appears only in the explicit narrow host-docs mutation guidance.
- Inspect the final report: it should include actual run waste and true
  remaining decisions, with no routine push question.

## Auto-Retro

applied: #300 host-docs-only setup helper shipped with dry-run default, execute-only mutation, focused tests, and issue closeout draft.

applied: setup bootstrap mutation hazard found by fresh-eye review was fixed by removing `--execute` from the generic bootstrap command.

applied: achieve closeout report guidance now requires actual run waste and true unresolved decisions while avoiding routine publication/push prompts by default.

applied: #299 local resolution was revalidated rather than reimplemented, reducing duplicate work.
