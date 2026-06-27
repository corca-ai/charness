# Achieve Goal: Capability-first public skill rollout

Status: active
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-capability-first-skill-rollout.md`

This file is the living goal scratchpad for the continued rollout. The host
goal is active; keep this artifact current until closeout.

## Active Operating Frame

- Current slice: close the `issue` feature-capability slice.
- Current slice intent: keep feature/deferred-work issue resolution from
  proposing implementation before naming the capability or failure.
- Next action: validate and commit the `issue` slice, then keep scanning
  remaining non-release public skills.
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
| 4 | Fresh-eye critique and focused closeout | Avoid overclaiming migration breadth | Critique artifact, goal update, non-claims | complete |
| 5 | Add capability-over-feature hook to `ideation` | Move the source concept skill before improving downstream `spec` | Focused ideation diff, dogfood freeze, slice closeout | complete |
| 6 | Add capability-contract hook to `spec` | Preserve capability intent when moving from concept to implementation contract | Focused spec diff, dogfood freeze, slice closeout | complete |
| 7 | Add capability-delivery handoff to `impl` | Preserve capability intent during coding and closeout | Focused impl diff, dogfood freeze, slice closeout | complete |
| 8 | Add capability-claim hook to `narrative` | Prevent durable story alignment from becoming polished feature inventory | Focused narrative diff, dogfood freeze, slice closeout | complete |
| 9 | Add capability-failure hook to `debug` | Keep RCA anchored on the failed/restored user or operator capability | Focused debug diff, dogfood freeze, slice closeout | complete |
| 10 | Add capability-before-gate hook to `quality` | Prevent target-skill review from jumping to gates before capability diagnosis | Focused quality diff, dogfood freeze, slice closeout | complete |
| 11 | Add feature-capability hook to `issue` | Keep feature/deferred-work resolution briefs capability-first | Focused issue diff, dogfood freeze, slice closeout | complete |

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
- Slice 3 — `ideation` capability-over-feature hook.
  - Changed: `skills/public/ideation/SKILL.md` and generated plugin mirror now
    add a `capability lens`, flag feature lists that never name the new or
    failed capability, and add `Capability or Capability Failure` to the output
    shape.
  - Dogfood/evaluator disposition: `ideation` is `hitl-recommended` and
    adapter-free; the planner requested scenario review and current contract
    freeze, not live Cautilus. `docs/public-skill-dogfood.json` now records the
    current contract freeze.
  - Non-claim: this does not prove every ideation output will be capability-led;
    it gives the skill a first-use prompt surface that can be reviewed by a
    human operator.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `ideation` slice after the
    dogfood freeze.
- Slice 4 — `spec` capability-contract hook.
  - Changed: `skills/public/spec/SKILL.md` and generated plugin mirror now carry
    forward the capability or capability failure from `ideation`, require actor,
    capability delta, and acceptance boundary before feature enumeration when
    missing, and add `Capability Contract` to the output shape.
  - Dogfood/evaluator disposition: `spec` is evaluator-required and mapped to
    `representative-skill-contracts`; this diff does not change routing,
    frontmatter, or scenario mapping. `docs/public-skill-dogfood.json` now
    records the current contract freeze; no live Cautilus run or scenario
    registry mutation is claimed.
  - Non-claim: no new deterministic floor was added for capability vocabulary.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `spec` slice after the
    dogfood freeze and scenario mapping review.
- Slice 5 — `impl` capability-delivery handoff.
  - Changed: `skills/public/impl/SKILL.md` and generated plugin mirror now
    restate a `Capability Contract` as user/operator capability plus acceptance
    evidence before coding, and closeout includes `Capability Delivered`.
  - Dogfood/evaluator disposition: `impl` is evaluator-required and mapped to
    `impl-adapter-bootstrap`; this diff does not change routing, adapter
    bootstrap behavior, or scenario mapping. `docs/public-skill-dogfood.json`
    now records the current contract freeze; no live Cautilus run or scenario
    registry mutation is claimed.
  - Non-claim: this is handoff continuity, not proof that all implementation
    slices deliver the right capability without human judgment.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `impl` slice after the
    dogfood freeze and scenario mapping review.
- Slice 6 — `narrative` capability-claim hook.
  - Changed: `skills/public/narrative/SKILL.md` and generated plugin mirror now
    name the reader/operator capability the durable story must make true,
    separate capability claims from feature inventory, and include
    `Capability Claim` in the output shape.
  - Dogfood/evaluator disposition: `narrative` is `hitl-recommended`; the
    planner requested scenario review and current contract freeze, not live
    Cautilus. `docs/public-skill-dogfood.json` now records the current contract
    freeze.
  - Non-claim: this improves first-touch story alignment, not all audience
    delivery or announcement behavior.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `narrative` slice after the
    dogfood freeze.
- Slice 7 — `debug` capability-failure hook.
  - Changed: `skills/public/debug/SKILL.md` and generated plugin mirror now name
    the user/operator capability that failed when it matters, state the
    capability restored by correct behavior, and add `Capability Failure` to the
    durable artifact shape.
  - Dogfood/evaluator disposition: `debug` is evaluator-required and mapped to
    `debug-adapter-bootstrap`; this diff does not change routing, adapter
    bootstrap behavior, or scenario mapping. `docs/public-skill-dogfood.json`
    now records the current contract freeze; no live Cautilus run or scenario
    registry mutation is claimed.
  - Non-claim: this does not replace RCA mechanics; it keeps the capability loss
    visible while the existing diagnosis-first workflow remains authoritative.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `debug` slice after the
    dogfood freeze and scenario mapping review.
- Slice 8 — `quality` capability-before-gate hook.
  - Changed: `skills/public/quality/SKILL.md` and generated plugin mirror now
    require skill-design findings to name the capability or capability failure
    before proposing a gate, helper, or wording change.
  - Dogfood/evaluator disposition: `quality` is `hitl-recommended`; the planner
    requested scenario review and current contract freeze, not live Cautilus.
    `docs/public-skill-dogfood.json` now records the current contract freeze.
  - Non-claim: this reduces reflexive gate pressure; it does not ban gates when
    a capability failure truly needs a deterministic owner.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `quality` slice after the
    dogfood freeze.
- Slice 9 — `issue` feature-capability hook.
  - Changed: `skills/public/issue/SKILL.md` and generated plugin mirror now
    require feature/deferred-work resolution to name capability or capability
    failure before proposing implementation.
  - Dogfood/evaluator disposition: `issue` is evaluator-required and mapped to
    maintained issue scenarios; this diff does not change routing, GitHub
    source-of-truth selection, causal-review, or feature-brief behavior.
    `docs/public-skill-dogfood.json` now records the current contract freeze;
    no live GitHub/Cautilus run or scenario registry mutation is claimed.
  - Non-claim: this does not close or mutate any live issue.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `issue` slice after the
    dogfood freeze and scenario mapping review.

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

- `create-skill` frontmatter/topology wording can be reviewed later; the current
  trigger already routes correctly.
- Final rollout reviewer found the quality matrix stale after later slices; that
  was remediated in `charness-artifacts/quality/2026-06-27-public-skill-capability-rollout.md`.
- `achieve`, `critique`, `issue`, `release`, and other public skills remain
  non-claimed and need separate slices before any migration claim.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Existing v0.56.7 release WIP remains in the worktree and is intentionally
  outside this rollout loop. `run_slice_closeout.py --plan-only` reports
  prose-pin warnings from `charness-artifacts/release/latest.md`; they belong to
  that release WIP, not this `create-skill` slice.

## Final Verification

Focused closeout passed for each committed rollout slice:

- `create-skill`: `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`
- `ideation`: `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`
- `spec`: `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`
- `impl`: `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`

Fresh-eye rollout critique:
`charness-artifacts/critique/2026-06-27-capability-first-skill-rollout-final.md`.

Broad pytest/live proof: skipped by contract because this is local skill/design
work with no release, push, external write, or live behavior claim. Existing
v0.56.7 release WIP remains outside the proof.

## User Verification Instructions

Inspect changed skill surfaces for `create-skill`, `ideation`, `spec`, and
`impl`, plus the dogfood entries for those skills. Treat other public skills as
non-claimed.

## Auto-Retro

Retro dispositions: not run — no workflow miss or release boundary was closed in
this local rollout.
Structural follow-up: keep future rollout slices narrow and update the rollout
matrix after each later target, not only at the first mutation.
