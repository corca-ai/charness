# Achieve Goal: Capability-first public skill rollout

Status: complete
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-capability-first-skill-rollout.md`

This file is the living goal scratchpad for the continued rollout. The host
goal is active; keep this artifact current until closeout.

## Active Operating Frame

- Current slice: closeout artifact repair after fresh-eye review.
- Current slice intent: align the claim boundary with committed slices 1-19 and
  avoid pretending the rollout changed every public skill.
- Next action: no further non-release public-skill mutation in this loop; the
  remaining candidates are either already capability-native or blocked by dirty
  release WIP.
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
| 12 | Add outcome-capability hook to `achieve` | Prevent long-running goals from becoming feature checklists before slice planning | Focused achieve diff, dogfood freeze, slice closeout | complete |
| 13 | Add judgment-capability hook to `hitl` | Keep human review scoped to the judgment capability automation lacks | Focused hitl diff, dogfood freeze, slice closeout | complete |
| 14 | Add capability-at-stake hook to `critique` | Keep pre-lock review from stress-testing changes without naming the capability at risk | Focused critique diff, dogfood freeze, slice closeout | complete |
| 15 | Add operator-capability hook to `setup` | Keep operating-surface scaffolding from becoming boilerplate docs | Focused setup diff, dogfood freeze, slice closeout | complete |
| 16 | Add continuation-capability hook to `handoff` | Keep baton refresh continuation-first instead of history-first | Focused handoff diff, dogfood freeze, slice closeout | complete |
| 17 | Add knowledge-capability hook to `gather` | Keep durable source capture scoped to the later-session capability | Focused gather diff, dogfood freeze, slice closeout | complete |
| 18 | Add capability-claim hook to `hotl` | Keep live/applied closeout explicit about what capability claim is being verified | Focused hotl diff, dogfood freeze, slice closeout | complete |
| 19 | Add reader-value output to `announcement` | Keep human-facing communication value-first through closeout | Focused announcement diff, dogfood freeze, slice closeout | complete |

## Rollout Claim Boundary

Changed in this goal: `create-skill`, `ideation`, `spec`, `impl`,
`narrative`, `debug`, `quality`, `issue`, `achieve`, `hitl`, `critique`,
`setup`, `handoff`, `gather`, `hotl`, and `announcement`, with matching plugin
mirrors and dogfood contract freezes.

Prior pilot only: `create-cli` was already handled before this continuation and
is not re-claimed as new work here.

Intentionally unchanged in this loop:

- `find-skills`: already capability-discovery-first; additional wording looked
  like vocabulary churn without a concrete failure.
- `retro`: already names workflow/capability/memory improvements as the next
  self-improvement classes; no current failure justified another prompt edit.
- `release`: explicitly out of scope because v0.56.7 release WIP is dirty and
  release carries irreversible-boundary proof obligations.

Global non-claims:

- No claim that every referenced support file, scenario, or evaluator fixture was
  migrated to capability-first language.
- No new blocking gate or deterministic floor was added for capability,
  north-star, or generative-sequence vocabulary.
- No live Cautilus run, provider write, release proof, push, or GitHub issue
  closeout is claimed.
- `announcement` is a minor output-shape reinforcement, not a strong new
  workflow decision point.

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
- Slice 10 — `achieve` outcome-capability hook.
  - Routing: `find-skills` recommendation returned `achieve`; implementation
    used `impl` and validation posture used `quality`.
  - Changed: `skills/public/achieve/SKILL.md` and generated plugin mirror now
    require the Before-phase to establish the outcome capability or failed
    capability before proof cost and slice sequencing.
  - Dogfood/evaluator disposition: `achieve` is `hitl-recommended`; the Cautilus
    planner requested scenario review and current contract freeze, not a live
    Cautilus run. `docs/public-skill-dogfood.json` records that routing, inert
    draft artifact creation, and `/goal @...` activation remain unchanged.
  - Non-claim: this shapes goal artifacts around capability delivery; it does
    not prove every active goal will maintain capability discipline without
    operator judgment.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `achieve` slice after the
    dogfood freeze and scenario review disposition.
- Slice 11 — `hitl` judgment-capability hook.
  - Routing: `find-skills` recommendation returned `hitl`; target-skill
    quality planning resolved `hitl` for this review slice.
  - Changed: `skills/public/hitl/SKILL.md` and generated plugin mirror now ask
    what decision capability automation lacks or the human supplies, and expose
    `Judgment Capability` in the output shape.
  - Dogfood/evaluator disposition: `hitl` is `hitl-recommended`; the current
    dogfood contract is frozen in `docs/public-skill-dogfood.json`. No live
    human review loop, target edit, or Cautilus run is claimed.
  - Non-claim: this improves review-loop framing; it does not automate the
    human judgment or prove any particular review outcome.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `hitl` slice after the
    dogfood freeze and scenario review disposition.
- Slice 12 — `critique` capability-at-stake hook.
  - Routing: `find-skills` recommendation returned `critique`; target-skill
    quality planning resolved `critique` for this review slice.
  - Changed: `skills/public/critique/SKILL.md` and generated plugin mirror now
    ask what capability or failure is at stake and expose `Capability at Stake`
    in the output shape.
  - Dogfood/evaluator disposition: `critique` is `hitl-recommended`; the
    current dogfood contract is frozen in `docs/public-skill-dogfood.json`.
    No fresh subagent critique run or Cautilus run is claimed for this small
    prompt-surface framing change.
  - Non-claim: this does not make every critique use the
    `customer-of-this-capability` angle; it only makes the capability at risk
    visible before choosing angles.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `critique` slice after the
    dogfood freeze and scenario review disposition.
- Slice 13 — `setup` operator-capability hook.
  - Routing: `find-skills` recommendation returned `setup`; target-skill
    quality planning resolved `setup` for this review slice.
  - Changed: `skills/public/setup/SKILL.md` and generated plugin mirror now ask
    setup's short ideation pass to name the maintainer or operator capability
    the operating surface must enable.
  - Dogfood/evaluator disposition: `setup` is evaluator-required and has
    maintained setup scenarios; this small framing change does not alter
    routing, repo-mode detection, normalization behavior, or adjacent-skill
    boundaries. `docs/public-skill-dogfood.json` freezes the current contract;
    no Cautilus run is claimed.
  - Non-claim: this does not turn setup into ideation or quality; it only names
    the operator capability before scaffolding docs.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `setup` slice after dogfood
    freeze, scenario registry review, and maintained setup scenario execution.
- Slice 14 — `handoff` continuation-capability hook.
  - Routing: `find-skills` recommendation returned `handoff`; target-skill
    quality planning resolved `handoff` for this review slice.
  - Changed: `skills/public/handoff/SKILL.md` and generated plugin mirror now
    ask handoff refresh to name the continuation capability the next operator
    must have after reading, and expose `Continuation Capability` in the output
    shape.
  - Dogfood/evaluator disposition: `handoff` is evaluator-required and has a
    maintained adapter-bootstrap scenario; this small framing change does not
    alter routing, artifact ownership, chunked-routing behavior, or adapter
    bootstrap behavior. `docs/public-skill-dogfood.json` freezes the current
    contract; no Cautilus run is claimed.
  - Non-claim: this does not make handoff a history, proof, or metrics store;
    single-source detail still belongs in owning artifacts.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `handoff` slice after
    dogfood freeze, scenario registry review, and maintained handoff scenario
    execution.
- Slice 15 — `gather` knowledge-capability hook.
  - Routing: `find-skills` recommendation returned `gather`; target-skill
    quality planning resolved `gather` for this review slice.
  - Changed: `skills/public/gather/SKILL.md` and generated plugin mirror now
    ask gather to name the knowledge capability later sessions need from the
    source and expose `Knowledge Capability` in the output shape.
  - Dogfood/evaluator disposition: `gather` is evaluator-required and mapped to
    `gather-adapter-bootstrap`; this small framing change does not alter
    exact-source routing, typed stop conditions, artifact ownership, source
    identity, or provider ownership. `docs/public-skill-dogfood.json` freezes
    the current contract; no live external acquisition or Cautilus run is
    claimed.
  - Non-claim: this does not widen narrow gather requests into research; it is
    a scope-control hook for durable assets.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `gather` slice after dogfood
    freeze, scenario registry review, and maintained gather scenario execution.
- Slice 16 — `hotl` capability-claim hook.
  - Routing: `find-skills` recommendation returned `hotl`; target-skill
    quality planning resolved `hotl` for this review slice.
  - Changed: `skills/public/hotl/SKILL.md` and generated plugin mirror now ask
    proof packets to name the capability claim the applied behavior loop is
    closing as working, and expose `Capability Claim` in the output shape.
  - Dogfood/evaluator disposition: `hotl` is `hitl-recommended`; the current
    dogfood contract is frozen in `docs/public-skill-dogfood.json`. No live
    provider proof, ledger mutation, or Cautilus run is claimed.
  - Non-claim: this does not change adapter-owned proof commands or the
    seven-status disposition vocabulary.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `hotl` slice after dogfood
    freeze and scenario review disposition.
- Slice 17 — `announcement` reader-value output.
  - Routing: `find-skills` recommendation returned `announcement`;
    target-skill quality planning resolved `announcement` for this review
    slice.
  - Changed: `skills/public/announcement/SKILL.md` and generated plugin mirror
    now include `Reader Value` in the output shape.
  - Dogfood/evaluator disposition: `announcement` is `hitl-recommended`; the
    current dogfood contract is frozen in `docs/public-skill-dogfood.json`.
    No delivery, external write, or Cautilus run is claimed.
  - Non-claim: this does not change adapter-owned delivery or confirmation
    policy; drafting remains value-first and delivery remains explicit.
  - Closeout: `run_slice_closeout.py --skip-broad-pytest
    --ack-cautilus-skill-review` completed for the `announcement` slice after
    dogfood freeze and scenario review disposition.

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

Final fresh-eye review:

- Reviewer `019f07ba-7583-70b1-aec6-2b96bdaaaf01` found no reflexive gate
  addition in `ea4c70ee..HEAD`.
- Blocker found and folded: the goal and quality artifacts were stale after the
  later slices, which garbled the claim boundary.
- Low finding accepted: `announcement` is weaker than the other slices because
  it reinforces output shape rather than adding a workflow decision point.
- Stop condition accepted: excluding release WIP, the remaining unchanged public
  skills (`find-skills`, `retro`) do not currently offer an obvious
  high-leverage non-vocabulary slice.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Existing v0.56.7 release WIP remains in the worktree and is intentionally
  outside this rollout loop. `run_slice_closeout.py --plan-only` reports
  prose-pin warnings from `charness-artifacts/release/latest.md`; they belong to
  that release WIP, not this `create-skill` slice.

## Final Verification

Focused closeout passed for each committed mutation slice:

- `create-skill`, `ideation`, `spec`, `impl`, `narrative`, `debug`, `quality`,
  `issue`, `achieve`, `hitl`, `critique`, `setup`, `handoff`, `gather`, `hotl`,
  and `announcement`: `run_slice_closeout.py --skip-broad-pytest
  --ack-cautilus-skill-review`
- `setup`, `handoff`, and `gather`: maintained scenario registry review plus
  `run_evals.py` for the local evaluator suite.
- Every mutation slice: `check_skill_surface_preflight.py --run-checks`,
  `plan_cautilus_proof.py --repo-root . --json` disposition, dogfood contract
  freeze, `validate_public_skill_dogfood.py`, goal-artifact check, markdown
  check, and pre-commit before commit.

Fresh-eye rollout critiques:

- `charness-artifacts/critique/2026-06-27-capability-first-skill-rollout-final.md`
  covered the early rollout matrix.
- Reviewer `019f07ba-7583-70b1-aec6-2b96bdaaaf01` covered the later slices from
  `ea4c70ee..HEAD` and found the closeout artifact staleness fixed here.

Broad pytest/live proof: skipped by contract because this is local skill/design
work with no release, push, external write, or live behavior claim. Existing
v0.56.7 release WIP remains outside the proof.

## User Verification Instructions

Inspect changed skill surfaces for `create-skill`, `ideation`, `spec`, `impl`,
`narrative`, `debug`, `quality`, `issue`, `achieve`, `hitl`, `critique`,
`setup`, `handoff`, `gather`, `hotl`, and `announcement`, plus the matching
dogfood entries and plugin mirrors. Treat `find-skills`, `retro`, and `release`
as unchanged in this loop; `release` remains out of scope until dirty release
WIP is reconciled.

## Auto-Retro

Retro dispositions: not run — no workflow miss or release boundary was closed in
this local rollout.
Structural follow-up: keep future rollout slices narrow and update the rollout
matrix after each later target, not only at the first mutation.
