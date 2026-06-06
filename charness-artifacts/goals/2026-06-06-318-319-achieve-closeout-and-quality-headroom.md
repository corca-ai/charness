# Achieve Goal: Fix #318 (orchestrator-owned achieve closeout proof) and #319 (SKILL.md headroom-buffer commit-boundary coverage)

Status: draft
Created: 2026-06-06
Activation: `/goal @charness-artifacts/goals/2026-06-06-318-319-achieve-closeout-and-quality-headroom.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: slice 2 (#318 orchestrator-owned closeout proof delegation) — next.
- Slice 1 (#319) status: implemented + verified (43 targeted tests, predict-commit
  aggregate green, broad gate 72/0), bounded fresh-eye review found one blocker
  (ratchet read working tree, not the staged index) — fixed and re-verified.
  `Close #319` carrier staged on the slice-1 commit; CLOSED state verified post-push.
- #319 mechanism (decided via `quality`): a changed-file-scoped commit-boundary
  **ratchet** in `check_skill_surface_preflight.py` (`--changed-skill-md`), wired
  path-scoped into `staged_commit_gate_plan.py`, plus the #308 preflight reference
  extension. Full-scan rejected: 5 public skills already sit under the 4-line
  buffer (issue/release/retro=0, debug/impl=2); the ratchet grandfathers existing
  debt and blocks only new erosion / brand-new skills without buffer.
- Next action: commit slice 1 (`Close #319`), then start slice 2 (#318).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve GitHub issues #319 and #318 as two independent committed slices. #319:
close the commit-boundary coverage gap so the per-surface SKILL.md
`core_nonempty` ≥4-line headroom-buffer test is no longer broad-gate-only
(mechanism decided via `quality`). #318: add an explicit orchestrator/sub-goal
external-proof delegation contract to `achieve`, with a machine-visible
delegated-proof checklist enforced in `check_goal_artifact.py` so a sub-goal can
honestly close at `local/proof-carrier complete` while a named orchestrator goal
owns deferred CI/apply/live/issue-CLOSED proof — without weakening standalone
goals or honest proof discipline.

## Non-Goals

- Not changing how a *standalone* `achieve` goal closes: the strict default
  stays; #318 adds an opt-in orchestrated mode and never relaxes the default.
- Not building a new orchestrator execution engine or run loop; `achieve` stays
  a goal operator, not a task runner.
- Not weakening honest proof discipline: delegated external proof must be an
  explicit non-claim plus a named orchestrator that owns it, never silent
  omission or an overclaim that local checks were live/release proof.
- Not pushing or closing #318/#319 out-of-band; the close is *staged* via
  `issue` (`Close #318` / `Close #319` on the respective closeout commits) and
  the maintainer's push closes them.
- Not a release / version bump: these are `achieve` + `quality` contract changes;
  no marketplace/version surface bump unless a later decision requires it.
- For #319: not lowering or removing the existing broad-gate headroom test; the
  goal adds *earlier* coverage, it does not relax the bar.
- Not bundling #318 and #319 into a single commit; each ships as its own slice.

## Boundaries

- Two independent committed slices, sequenced #319 → #318 (planning intent; the
  During slice-boundary-continuation logic may re-order on evidence). No
  cross-slice coupling; each commits and carries its own `Close #N`.
- #319 mechanism (commit-boundary checker vs #308 preflight reference vs both)
  is decided via the `quality` skill at slice time, honoring the issue's "route
  through quality" framing and the #307/#314 per-slice-latency caution — the
  mechanism is deliberately *not* pre-decided in this draft.
- #318 implements the full delegation contract: `achieve` docs/lifecycle +
  closeout-state taxonomy (impl/local · carrier · pushed/CI · applied/restarted ·
  live · issue-CLOSED) + a machine-visible delegated-proof checklist enforced in
  `check_goal_artifact.py` (and the `goal_artifact_closeout_evidence` helper),
  keeping the strict default for standalone goals as a hard constraint.
- #318 is a prompt/skill + validator surface change → a bounded fresh-eye
  critique is mandatory before the enforcement code locks in; the honesty
  boundary (no weakening of standalone closeout) is a hard, non-negotiable line.
- Generated/exported surfaces: any SKILL.md / skills / scripts edit must sync its
  `plugins/charness/...` mirror before validators run (mutate → sync → verify →
  publish); scripts mirror too (recent-lessons: `scripts/` mirrors to
  `plugins/charness/scripts/`, not only `skills/`).
- SKILL.md self-trap guard: before editing any SKILL.md (the #318 work may touch
  `achieve/SKILL.md`), check `recent-lessons.md` and grep for the per-skill
  budget test; the #319 surface *is* the `core_nonempty` ≥4 headroom buffer that
  bit the 306-317 run — do not author to the 160 hard limit with 0 headroom.
- Closeout commits stage the issue close via `issue` (`validate-closeout-draft`
  / `verify-closeout`); `achieve` does not push or close GitHub state itself.

## User Acceptance

What the user can do to verify completion directly.

- `gh issue view 319` and `gh issue view 318` show the close-intended carriers,
  and the issues read CLOSED after the maintainer pushes the closeout commits.
- #319: author a SKILL.md to exactly the 160 `core_nonempty` limit (0 headroom)
  and confirm the per-slice/commit surface (checker and/or the #308 preflight
  reference, whichever `quality` selects) now flags the missing ≥4 buffer
  *before* the broad `./scripts/run-quality.sh` gate — i.e. the late-only gap the
  issue describes is closed. The exact repro is recorded in the slice report.
- #318: read the `achieve` docs/lifecycle for the orchestrator/sub-goal
  delegation contract; create a sub-goal that closes at `local/proof-carrier
  complete` with delegated items and confirm `check_goal_artifact.py` enforces
  the delegated-proof checklist (the orchestrator cannot silently forget them);
  confirm a standalone goal with *no* named orchestrator still hits the strict
  default.
- `./scripts/run-quality.sh` (or the repo's documented gate) runs green.

## Agent Verification Plan

### Low-Cost Checks

- At every commit boundary: `run_slice_closeout.py --predict-commit` (the
  pre-commit gate aggregate), `ruff`, `check_python_lengths`, mirror-drift gate.
- Targeted pytest for the touched surface: the #319 quality-gate test
  (`tests/quality_gates/test_skill_reference_index.py` and any new
  commit-boundary checker test), and for #318 the goal-artifact lib /
  closeout-evidence tests (`test_goal_artifact_producers.py` and the
  `goal_artifact_closeout_evidence` / `check_goal_artifact` suites).
- `validate_skills` / `check-markdown` / `check_doc_links` for SKILL.md and
  achieve docs edits.

### High-Confidence Checks

- Full `./scripts/run-quality.sh` at each slice boundary (and `--release` at the
  final boundary if the run added/expanded tests, with the duplicate/length
  pressure classified new-slice-local vs accumulated debt).
- #319: a test asserting the headroom check now runs at the commit-boundary
  surface (or that the #308 preflight reference names it), while the existing
  broad-gate `*_uses_reference_index_with_core_headroom` test still passes.
- #318: a new/updated test asserting the delegated-proof checklist enforcement —
  a sub-goal *without* a named orchestrator still gets the strict default; a
  sub-goal *with* an orchestrator + delegated items gets the enforced checklist
  (orchestrator cannot complete with unverified delegated items).
- Bounded fresh-eye slice critique for #318 (prompt/skill + validator change),
  with the slice review packet from the Active Operating Frame.

### External Or Live Proof

- n/a — both issues are repo-internal `achieve` / `quality`-contract changes; no
  production, live-provider, deploy, or release proof is in scope. The final
  report names this skipped proof level explicitly rather than implying it ran.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #319: close the commit-boundary coverage gap for the SKILL.md `core_nonempty` ≥4 headroom-buffer test (mechanism chosen via `quality`) | Cheapest, self-contained quality gate; handoff names it the cleanest next quality pickup; generalizes #308/#314 | quality-routed mechanism decision; a near-limit SKILL.md flagged before the broad gate; targeted + broad gate green; `Close #319` carrier staged | planned |
| 2 | #318: full orchestrator/sub-goal external-proof delegation contract — docs + closeout-state taxonomy + machine-visible delegated-proof checklist enforced in `check_goal_artifact.py`; strict standalone default preserved | Larger design-heavy `achieve`-contract change; honesty boundary critical, so it follows the cheap de-risking slice | new/updated goal-artifact + closeout-evidence tests; fresh-eye critique CLEAR; standalone strict default unchanged; `Close #318` carrier staged | planned |

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

Recorded during the run:

- Routing: session-start `find-skills` → `achieve` goal pursuit; slice-1 #319
  mechanism decided via `quality`; closeout carrier via `issue`; bounded
  fresh-eye review via subagent (CLAUDE.md pre-delegated quality/critique scope).
- Gather: n/a — no external source; both issues are repo-internal (read with
  `gh issue view 318/319`, not a `gather`-class external source).
- Release: n/a — no version bump or install-manifest edit; `achieve` + `quality`
  contract changes only.
- Issue closeout (#319): carrier = direct-commit (`Close #319` on the slice-1
  commit); `issue_tool.py validate-closeout-draft` rehearsed pre-commit;
  `verify-closeout --expect-state CLOSED` deferred to the maintainer's push
  (explicit non-claim, per Non-Goals — `achieve` does not push or close).

## Activation Discussion

Discuss before activation: CONFIRMED — the consequential decisions were surfaced
in the Before-phase interview and resolved with the user before offering `/goal`:
(1) **#318 honesty risk** — loosening sub-goal closeout could weaken honest
proof; resolved by choosing *full contract + enforcement*, which keeps the strict
standalone default as a hard constraint and makes delegated proof machine-visible
(the orchestrator cannot silently forget it), and by requiring a bounded
fresh-eye critique before the enforcement code lands (slice 2). (2) **Issue
close** — #318/#319 close is *staged* via `issue` (`Close #N` carriers), never
pushed or closed out-of-band by `achieve`. (3) **Two-issue scope** — #318 and
#319 are independent committed slices with separate carriers, not a bundled
commit. (4) **Proof non-claims** — both issues are repo-internal; no live /
prod / release proof is in scope, and the final report will name that skipped
proof level explicitly rather than implying it ran.

## Slice Log

### Slice 1: Slice 1 — #319 commit-boundary SKILL.md core-headroom coverage

- Objective: Close the commit-boundary coverage gap for the SKILL.md core_nonempty >=4 headroom buffer so authoring to the 160 hard limit no longer passes the per-slice gate and fails only the broad gate.
- Why this approach: Routed mechanism through quality: a changed-file-scoped ratchet, not a full-scan gate, because 5 public skills already sit under the buffer (issue/release/retro=0, debug/impl=2) so a full-scan gate would retroactively break unrelated commits. Matches the issue's 'changed SKILL.md files' framing and the repo's check_boundary_bypass_ratchet idiom; reuses the existing core_nonempty single source (no third copy).
- Commits:
- What changed: scripts/check_skill_surface_preflight.py (CORE_NONEMPTY_HEADROOM_BUFFER constant + evaluate_core_headroom ratchet + scan_changed_skill_md + --changed-skill-md mode, reads staged index blob for 'new'); scripts/staged_commit_gate_plan.py (_skill_core_headroom_gates path-scoped GateCommand); docs/conventions/authoring-preflight.md (#308 preflight reference extension); 4 test files; synced plugins/charness mirror.
- Alternatives rejected: Full-scan hard gate (rejected: retroactively breaks 5 grandfathered skills); #308 preflight-reference-only / prose-only (rejected by quality: leaves an automatable rule as prose); a new standalone checker script (rejected: would be a 3rd copy of core_nonempty).
- Targeted verification: 43 targeted tests pass (ratchet unit cases, git-backed staged-content scan, divergence test, CLI, plan labels, refactored broad-gate achieve test, authoring-preflight drift guard); run_slice_closeout --predict-commit aggregate green; ./scripts/run-quality.sh 72/0; end-to-end repro: staging a 0-headroom SKILL.md blocks even after the working tree is repaired (judges the staged index).
- Test duplication pressure:
- Critique: Bounded fresh-eye review (general-purpose subagent) found 1 BLOCKER: ratchet read the working tree for 'new' but HEAD for 'base', letting a healthy working tree mask a 0-headroom staged commit. Fixed: 'new' now reads the staged index blob (git show :<rel>) with worktree fallback; added test_scan_changed_skill_md_judges_staged_not_worktree. Re-review requested.
- Off-goal findings: None.
- Lessons carried forward: A new commit-boundary gate must judge the staged index, not the working tree, or it inherits the same bypass class it was built to close.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- GitHub issue #319 (`gh issue view 319`): "SKILL.md core-nonempty
  headroom-buffer test runs only in the broad gate, not the commit boundary
  (generalizes #308/#314)" — the bug this goal's slice 1 fixes; the issue body's
  "Suggested direction (not a decision)" routes through `quality`.
- GitHub issue #318 (`gh issue view 318`): "Support orchestrator-owned external
  proof for achieve sub-goal closeout" — the contract this goal's slice 2
  implements; its Acceptance Criteria require machine/checklist-visible delegated
  proof and that standalone goals keep the strict default.
- `docs/handoff.md` → "Next Session": names #319 as the cleanest next quality
  pickup and #318 as the orchestrator-proof follow-up.
- `charness-artifacts/retro/recent-lessons.md`: the #319 surface is the same
  `core_nonempty` ≥4 headroom-buffer trap that bit the 306-317 run; "before
  editing any SKILL.md, check recent-lessons + the per-skill budget test."
- `charness-artifacts/goals/2026-06-06-306-316-open-followups.md` and its
  closeout retro `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`:
  origin of #319 (filed at that goal's closeout) and the #308/#314 lineage.
- The `achieve` contract surfaces #318 modifies:
  `skills/public/achieve/references/lifecycle.md`,
  `skills/public/achieve/references/goal-artifact.md`, and the closeout-evidence
  enforcement in `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
  + `check_goal_artifact.py` (with mirrored `plugins/charness/...` copies).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Mode (artifact-only vs implementation-continuation):** family {artifact-only
  draft, implementation-continuation}. Chosen: artifact-only Before-phase draft —
  the prose "골 만들기" ("make a goal") names the shaping mode. Rejected
  implementation-continuation (would start executing slices the user only asked
  to be drafted). Anti-anchoring: mode is a shaping-time intent, host-invariant →
  `single-point: /achieve shapes, /goal pursues; this invocation was /achieve`.
- **Q1 — #318 depth:** family {full contract + enforcement, docs + honest
  language only, design + critique first}. Chosen: full contract + enforcement —
  #318's Acceptance Criteria explicitly require delegated proof be "machine/
  checklist visible enough that the orchestrator cannot silently forget"; a
  docs-only version would not satisfy that, and "design + critique first" folds in
  as the mandatory slice-2 critique rather than a separate, smaller scope.
  Anti-anchoring: closeout posture varies by goal-mode (standalone vs
  orchestrated) → `axis: goal-mode` (the new contract is the axis instance), not
  a global default that weakens all goals.
- **Q2 — #319 approach:** family {defer mechanism to quality, commit-boundary
  checker, preflight reference only, both}. Chosen: defer mechanism to `quality` —
  the issue explicitly routes through `quality` and calls the direction "not a
  decision"; the per-slice-latency tradeoff (#307/#314) is `quality`'s to own.
  Anti-anchoring: gate placement (commit-boundary vs broad) is a known
  validation-cost axis → `axis: validation-cadence`, not a singleton.
- **Q3 — sequencing:** family {#319 → #318, #318 → #319, agent picks at
  activation}. Chosen: #319 → #318 — handoff names #319 the cleanest next quality
  pickup; the cheap self-contained gate de-risks before the design-heavy #318.
  `single-point: planning intent only; During slice-boundary-continuation may
  re-order on evidence`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- **Folded blocker — #318 honesty risk:** loosening sub-goal closeout could
  weaken honest proof. Folded into Non-Goals ("never silent omission/overclaim")
  and Boundaries ("strict standalone default is a hard constraint"; machine-
  visible checklist; mandatory fresh-eye critique before enforcement lands).
  Provenance: shaping-time self-critique + the AskUserQuestion honesty framing
  the user resolved by choosing full + enforcement.
- **Folded blocker — #319 per-slice latency:** a new commit-boundary gate could
  slow every commit (the #307/#314 caution). Folded into Boundaries by deferring
  the mechanism to `quality`, which owns the latency tradeoff, instead of
  pre-committing to a checker.
- **Folded blocker — SKILL.md self-trap:** the #318 work may edit
  `achieve/SKILL.md`, which is governed by the same `core_nonempty` ≥4 headroom
  buffer #319 is about. Folded into Boundaries (check recent-lessons + per-skill
  budget test before SKILL.md edits) and Low-Cost Checks (`validate_skills`).
- **Over-worry raised, not folded:** combining #318 and #319 in one goal risks
  scope blur. Not folded into a split — they are independent committed slices
  with separate `Close #N` carriers and separate verification; one goal keeps a
  single activation surface the user asked for.
- **Reviewer provenance:** shaping-phase self-critique only. A bounded fresh-eye
  critique is *planned* at slice 2 (the #318 prompt/skill + validator change) per
  the Boundaries/Verification plan; it is not run at draft time because no code
  has changed yet.

## Off-Goal Findings

- Slice 1 (#319) resolution critique surfaced a recurrence idea: a meta-test that
  flags any *blocking* buffer/headroom assertion (distinct from a hard limit) that
  lacks a commit-boundary equivalent. Counterweight triage: **Valid but Defer,
  leaning Over-Worry** — the class currently has population 1 (the #319 surface
  itself, now fixed), a `remaining >= N` regex meta-test is the #305 brittleness
  trap and adds #307/#314 latency, and the generalization is already the
  `recent-lessons.md` line-19 disposition that #319 resolves. Disposition:
  **not built, no fresh issue filed** (per counterweight); revisit trigger = a
  *second* blocking buffer/headroom constant is introduced. Recorded as a
  non-claim in `charness-artifacts/critique/2026-06-06-319-commit-boundary-headroom.md`.

## Final Verification

Pending — completed in the After-phase after both slices, the final quality gate,
and the bounded fresh-eye + disposition review.

## User Verification Instructions

Pending — written at closeout. The `## User Acceptance` section above states the
intended user-facing checks; the closeout will confirm which actually ran.

## Auto-Retro

Pending — produced by the `retro` skill at closeout, with each surfaced
improvement dispositioned (`applied: <what>` or `issue #N`) or a single
`Retro dispositions: none — <reason>` line.
