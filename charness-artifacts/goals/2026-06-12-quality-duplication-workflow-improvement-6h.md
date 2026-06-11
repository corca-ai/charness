# Achieve Goal: Quality Duplication Workflow Improvement 6h

Status: active
Created: 2026-06-12
Activation: `/goal @charness-artifacts/goals/2026-06-12-quality-duplication-workflow-improvement-6h.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command. This artifact is active because the operator
created the host goal and asked the agent to continue.

## Active Operating Frame

- Current slice: Slice 2 - reduce the test-side pressure exposed by Slice 1 or
  pick another safe duplication/workflow cleanup.
- Next action: after committing Slice 1, inspect `tests/quality_gates/test_issue_skill.py`
  length/cohesion and the remaining nose top findings, then choose the next
  local slice without claiming total clone-line reduction from Slice 1.
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
| 1 | Pick and land one structural quality cleanup from current duplication/workflow pressure. | The user explicitly objected to low-yield goal execution; the next move must produce a concrete quality delta. | Committed code/test/doc change plus focused and surface-recommended gates. | implemented; commit pending |
| 2 | Continue to the next distinct safe cleanup if time remains. | Done-early policy requires continuation rather than stopping after one small win. | Another committed cleanup or a valid early-close ledger with distinct candidates and sufficiency check. | active |
| 3 | Final closeout with retro, host-log probe, disposition review, and broad verification. | The goal must prove honest completion, non-claims, and residual work. | Complete goal artifact passing `check_goal_artifact.py`. | planned |

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
- Commits: pending commit
- What changed: Added issue_local_import.py; converted issue_tool.py, issue_read.py, issue_close.py, issue_create.py, issue_verify_closeout.py, and describe_closeout_draft_shape.py to use it; moved preflight probe/payload helpers into issue_backend.py; synced plugins/charness issue export; added a focused non-JSON preflight config-error test.
- Alternatives rejected: Rejected broad init_adapter/resolve_adapter cleanup for this first slice because it spans many public skills and generated surfaces. Rejected a broader import framework because the remaining runpy one-liner is smaller than the duplicated spec loader bodies and avoids package-layout assumptions.
- Targeted verification: ruff changed issue files/tests; focused pytest 110 passed; broad pytest before the final cheap test was 2806 passed, 4 skipped, 26 deselected; changed-surface validators for packaging, skills, public-skill policy/dogfood, markdown/docs/secrets, py_compile, attention-state, gitignore scan hygiene, boundary ratchet passed.
- Test duplication pressure: issue_tool.py left the Python length warn band (358 -> 291 code lines). tests/quality_gates/test_issue_skill.py grew from 736 -> 761 and remains warn-band; this is an honest next-slice pressure, not hidden success.
- Critique: Fresh-eye critique: charness-artifacts/critique/2026-06-12-issue-skill-loader-probe-split.md. Counterweight found no code diff required before commit after the cheap preflight test; remaining Act Before Ship item is inclusion/staging of new helper and durable artifacts.
- Off-goal findings: nose total_dup_lines was not a clean win (baseline 3063 -> 3073 after helper/relocation), so this slice must not claim total clone-line reduction. Nose family count improved 525 -> 523 and the issue loader family disappeared from the top findings.
- Lessons carried forward: Metric-only claims are fragile; pair clone inventory with file-level pressure and reviewer triage. Next cleanup should avoid improving one source file by pushing unchecked pressure into a test file.
- Metrics: issue_tool.py 358 -> 291 code lines; Python length warn-band files 8 -> 7 before the added test, then 7 with test_issue_skill.py still warned; nose total_families 525 -> 523; nose total_dup_lines 3063 -> 3073.

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
