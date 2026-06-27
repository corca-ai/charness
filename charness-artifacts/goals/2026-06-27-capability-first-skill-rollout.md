# Achieve Goal: Capability-first public skill rollout

Status: active
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-capability-first-skill-rollout.md`

This file is the living goal scratchpad for the continued rollout. The host
goal is already active; keep this artifact current until closeout.

## Active Operating Frame

- Current slice: close the first rollout mutation on `create-skill`.
- Current slice intent: make the authoring skill start public-skill edits from
  consumer capability failure, proof boundary, and conditional sequence center
  rather than from form/gate vocabulary.
- Next action: commit the `create-skill` slice, then pick the next
  reviewed-but-deferred target (`ideation` or `spec`).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Continue beyond the `create-cli` pilot: audit public Charness skills for
capability-first, generative-sequence, and north-star alignment gaps; improve the
highest-leverage skill surfaces without adding reflexive blocking gates; and
leave explicit non-claims for skills not yet migrated.

## Non-Goals

- No claim that every public skill is fully migrated in this loop.
- No release publish, version bump, or v0.56.7 cleanup unless explicitly
  re-scoped.
- No new blocking gate or deterministic floor for capability language.
- No universal sequencing mandate: use the shared lens only when ordering
  changes correctness, uncertainty reduction, or downstream unlocks.
- No rewriting stable skills merely to add vocabulary.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Dirty-worktree boundary: existing v0.56.7 release WIP remains outside this
  goal. Do not stage or reinterpret release WIP as proof for this rollout.
- Scope boundary: public skill source, shared references, tests, and quality
  artifacts are in scope. Release surfaces and generated manifests are out of
  scope unless the slice explicitly touches a mirrored skill surface and must
  sync plugin exports.
- Floor-addition boundary: any candidate floor must carry a north-star and
  floor-addition-restraint call; default posture is advisory, describe-first,
  existing-gate reuse, or no-gate.

Timebox: 2h
Activation time: 2026-06-27T14:07:47+09:00
Closeout reserve: 25m
Done-early policy: continue_next_improvement within the same local, non-release
scope unless the user pauses.
Discuss before activation: resolved — this is a broad public-skill audit but not
a release/live-proof goal. External writes, release publish, version bump,
GitHub issue closeout, and v0.56.7 cleanup remain out of scope; the run may
mutate local skill/docs/tests and must leave explicit non-claims for unaudited or
unchanged skills.

## User Acceptance

- Inspect a rollout matrix that names which public skills were reviewed, which
  were changed, and which remain non-claimed.
- See at least one additional high-leverage skill surface improved beyond the
  earlier `create-cli` pilot, or an explicit critique-backed reason that no safe
  additional slice should mutate before release WIP is reconciled.
- Confirm the quality skill can propose capability/north-star skill improvement
  moves without drifting back into reflexive gate recommendations.
- Confirm no new blocking floor was added for capability/sequencing language.

## Agent Verification Plan

### Low-Cost Checks

- `rg --files skills/public` and focused reads of every public `SKILL.md`.
- Target-skill quality planner probes for likely high-leverage candidates.
- `check_skill_surface_preflight.py` before editing any skill or reference.
- Focused `validate_skills.py`, doc links, markdown, and relevant tests after
  each mutation slice.

### High-Confidence Checks

- Fresh-eye critique for the first rollout slice after audit.
- Quality artifact or rollout matrix recording recommended moves and non-claims.
- Pre-commit on any committed mutation.

### External Or Live Proof

- None planned. This is local skill/design work with no publish, push, GitHub
  closeout, provider write, or release.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Build public-skill rollout matrix | Prevent another premature "all skills done" closeout | Matrix artifact listing reviewed/changed/deferred skills and candidate next moves | complete |
| 2 | Mutate the highest-leverage non-release skill surface | Extend beyond `create-cli` while avoiding release WIP | Focused skill/reference diff, preflight, validate_skills/doc checks | complete |
| 3 | Dogfood quality-move recommendations on the changed target | Prove quality can make skill-improvement suggestions in the new language | Target-skill quality artifact or planner output | complete |
| 4 | Fresh-eye critique and focused closeout | Avoid overclaiming migration breadth | Critique artifact, goal update, non-claims | in progress |

## Operator Decision Queue

none — the user asked to continue locally; release/push remains out of scope for
this rollout loop.

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

Routing: find-skills returned `create-cli` as a phrase-match recommendation for
the continuation prompt; this was judged insufficient for the broader rollout.
Executed route is `achieve` for lifecycle, `quality` for target-skill review and
validation posture, `critique` for slice review, and `impl` for scoped skill
edits after the audit.
Gather: n/a — no new external source is introduced in this continuation; prior
source captures remain referenced below.
Release: n/a — release publish/version work is explicitly out of scope.
Issue closeout: n/a — no GitHub issue closeout is in scope.

## Slice Log

- Slice 1 — audit kickoff.
  - Routing: `achieve` + `quality` after `find-skills` phrase-match review.
  - Outcome so far: previous goal closed only a shared lens, quality-move
    contract, and `create-cli` pilot. This rollout starts from the non-claim
    that broader public skill migration remains open.
- Slice 2 — `create-skill` capability brief.
  - Changed: `skills/public/create-skill/SKILL.md` and generated plugin mirror
    now require a capability brief before edits, name consumer capability or
    capability failure, make current/next-center conditional, and require
    capability failure naming for `improve` slices.
  - Quality evidence: target-skill quality probes identified `create-skill` as
    the first mutation target; the quality artifact records reviewed-but-not
    migrated targets `ideation`, `spec`, and `impl`.
  - Dogfood/evaluator disposition: `create-skill` remains evaluator-required,
    with `representative-skill-contracts` scenario coverage. This diff does not
    change trigger/frontmatter routing or scenario mapping;
    `docs/public-skill-dogfood.json` now records the current contract freeze; no
    live Cautilus run or scenario registry mutation is claimed.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `create-skill` slice after
    the dogfood freeze.
  - Pre-commit repair: `run_evals.py` exposed a representative-contract
    sentence pin on the old preserve/improve wording. `check_skill_contracts.py`
    now pins the two behavior clauses separately: preserve/improve decision and
    capability-failure naming before trigger/contract changes.
  - Non-claim: this slice improves the authoring contract; it does not complete
    all public skill migration.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/design-north-star.md` — governing standard.
- `docs/conventions/implementation-discipline.md` — phase barriers and
  floor-addition restraint.
- `docs/conventions/operating-contract.md` — commit/critique/skill discipline.
- `charness-artifacts/retro/recent-lessons.md` — recent repeat traps.
- `charness-artifacts/goals/2026-06-27-capability-first-skill-redesign.md` —
  completed pilot goal and explicit non-claims.
- `skills/shared/references/generative-sequence.md` — shared sequencing lens.
- `charness-artifacts/gather/2026-06-18-capabilities-over-features.md` and
  `charness-artifacts/gather/2026-06-27-genseq3-skill.md` — prior source
  captures.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Decision: whether to mark all skills migrated after the prior goal.
  Chosen: no; treat the prior goal as pattern plus `create-cli` pilot only.
  Rejected: complete all-skills claim, because most public skill surfaces have
  not yet been audited against the new capability/north-star lens.
- Decision: rollout breadth.
  Chosen: audit all public skills, then mutate the highest-leverage subset.
  Rejected: rewrite every skill body immediately, because vocabulary churn is
  not capability improvement and may violate north-star restraint.
- Decision: proof level.
  Chosen: focused skill validation plus fresh-eye critique for mutated surfaces.
  Rejected: broad release-style proof, because no release/push/external boundary
  is in scope and v0.56.7 WIP remains dirty.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Fresh-eye critique ran on the `create-skill` slice through bounded reviewers
`019f0780-e084-78e2-a6c5-a8f8ee9863d0`,
`019f0781-8c2f-7303-a39a-2fe9397a3f73`, and
`019f0781-573a-7902-954f-5915a5b4a7a8`.

Folded findings:

- Add consumer-side dogfood and Cautilus scenario-review disposition to the
  proof boundary.
- Make current/next-center language conditional so shared sequencing does not
  become a universal mandate.
- Run focused post-mutation validation and mirror proof before closeout.

Over-worry not folded:

- No live Cautilus run, broad pytest, release proof, or quality/latest pointer
  refresh is required for this local design-skill slice.

Valid but deferred:

- `ideation`, `spec`, and `impl` need later output-shape review after the
  `create-skill` authoring contract is used on another real slice.
- `create-skill` frontmatter/topology wording can be reviewed later; the current
  trigger already routes correctly.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Existing v0.56.7 release WIP remains in the worktree and is intentionally
  outside this rollout loop. `run_slice_closeout.py --plan-only` reports
  prose-pin warnings from `charness-artifacts/release/latest.md`; they belong to
  that release WIP, not this `create-skill` slice.

## Final Verification

Closeout pending. Replace the lines below with bound evidence paths or allowed
skips only when the rollout is actually ready to close.

Retro: pending-closeout — active rollout has not reached final retro yet.
Host log probe: pending-closeout — active rollout has not reached final host-log
probe decision yet.
Disposition review: pending-closeout — active rollout has not reached final
disposition review yet.

## User Verification Instructions

Pending closeout. During the run, inspect the rollout matrix and changed skill
surfaces rather than treating this artifact as a completion claim.

## Auto-Retro

Retro dispositions: pending-closeout — no final retro has been written for this
active rollout yet.
Structural follow-up: pending-closeout — classify after final retro if it names
transferable waste.
