# Achieve Goal: Capability-first generative-sequence skill redesign

Status: complete
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-capability-first-skill-redesign.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete; closeout binds retro, disposition review, and focused
  verification evidence for the capability-first skill redesign.
- Current slice intent: prove the shared lens, quality-move migration,
  target-skill packet, and one concrete `create-cli` hook without adding a
  blocking floor.
- Next action: separate follow-on work can continue with broader target pilots
  or resume the interrupted v0.56.7 release WIP, but neither is part of this
  closed goal.
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

Improve Charness skill-improvement behavior so agents design from capabilities
and generative sequencing rather than feature lists, gate proliferation, or
skill-authoring checklists. The result should:

- absorb `genseq3` as a shared sequencing lens with an applicability guard, not
  as `create-skill` doctrine;
- migrate `quality` from gate-centric recommendation language to quality-move
  recommendation language without adding new blocking floors;
- update target-skill structural review so recommended moves center consumer
  capability, current centers, next center, proof boundary, and enforcement
  posture;
- pilot the pattern on `create-cli` before spreading hooks into `ideation`,
  `spec`, or `create-skill`;
- preserve the north-star rule that the harness briefs a capable judge and keeps
  teeth only where a wrong answer escapes.

## Non-Goals

- No universal sequencing mandate: do not force the lens when the quality failure
  is not sequencing-shaped.
- No new blocking gate or deterministic floor in the first slice.
- No `create-skill` doctrine rewrite before the `create-cli` pilot produces
  evidence.
- No per-finding form-filling requirement; move cards apply only to recommended
  quality moves.
- No release publish, version bump, or v0.56.7 cleanup inside this goal unless
  explicitly re-scoped.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Dirty-worktree boundary: the repo currently contains interrupted v0.56.7
  release WIP. This goal may inspect it, but implementation slices should avoid
  release-version and release-artifact files unless the user explicitly asks to
  reconcile the release WIP.
- Floor-addition boundary: any `candidate-floor` recommendation requires an
  explicit north-star plus floor-addition-restraint record before it can become
  executable. The default enforcement posture is advisory, describe-first,
  existing-gate-reuse, or no-gate.

Timebox: 45m
Activation time: 2026-06-27T13:32:30+09:00
Closeout reserve: 25m
Done-early policy: continue_next_improvement within the same local, non-release
scope.

## User Acceptance

- Read the shared sequencing reference and see that it is applicability-gated:
  first name the capability failure, then use sequencing only when order affects
  correctness, uncertainty reduction, or downstream unlocks.
- Run or inspect the `quality` planner/scaffold/validator path and see
  `Recommended Next Quality Moves` as the new writer-facing contract, while old
  `Recommended Next Gates` remains a non-blocking compatibility alias during the
  migration.
- Review a `create-cli` pilot quality artifact and see whether the move-card
  vocabulary improves judgment rather than adding paperwork.
- Confirm no new blocking floor was added without an explicit floor-restraint
  call.

## Agent Verification Plan

### Low-Cost Checks

- skill/doc authoring preflight for every touched skill or reference surface;
- focused tests for quality scaffold/validator/planner changes;
- `rg` checks that new quality-move vocabulary does not leave active gate-centric
  output claims in the migrated surfaces;
- package/path checks for any newly referenced shared reference.

### High-Confidence Checks

- target-skill quality planner proof for `create-cli`;
- consumer-side dogfood suggestion/review where public-skill behavior is changed;
- fresh-eye critique for the first pilot artifact before broader rollout.

### External Or Live Proof

- None planned. This goal is local skill/design work. No publish, push, GitHub
  closeout, provider write, or live external side effect is required.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add shared generative-sequence reference with applicability guard | Prevent `genseq3` from becoming create-skill-specific or universal doctrine | New shared reference, referenced from owning surfaces, no new gate | completed |
| 2 | Migrate quality recommendation contract from gates to quality moves | Preserve recent gate-cost/north-star improvements while making quality propose skill improvements | Updated quality wording, scaffold/validator compatibility alias, focused tests | completed |
| 3 | Update quality target-skill structural packet around capability move cards | Make skill-improvement suggestions concrete without form-filling every finding | Planner output for `--target-skill create-cli`, tests, old packet compatibility if needed | completed |
| 4 | Pilot on `create-cli` | Prove vocabulary on one bounded workflow before broad hooks | Create-cli quality pilot artifact plus critique | completed |
| 5 | Add thin hooks to `ideation`, `spec`, and `create-skill` only if pilot holds | Avoid spreading untested vocabulary | Minimal references or explicit defer with reason | completed |

## Operator Decision Queue

none — the user approved starting this goal locally; release publication and
v0.56.7 cleanup remain out of scope for this goal.

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

Routing: find-skills recommended `quality` for final quality-move closeout and
verification; the executed route used `achieve` for the goal lifecycle, `gather`
for external source capture, `quality` for the target-skill quality contract,
`create-skill` as downstream consumer awareness only, `critique` for design and
disposition review, and `retro` for closeout learning.
Gather: `charness-artifacts/gather/2026-06-18-capabilities-over-features.md`
and `charness-artifacts/gather/2026-06-27-genseq3-skill.md`.
Release: n/a — this goal explicitly excludes release publish/version bump work.
Issue closeout: n/a — no GitHub issue closeout is in scope.

## Slice Log

- Slice 1 — shared sequencing lens and quality-move migration.
  - Routing: `achieve`, `gather`, `quality`, `critique`, and downstream
    `create-skill` consumer awareness.
  - Changed surfaces: `skills/shared/references/generative-sequence.md`,
    `skills/public/quality/SKILL.md`, quality planner/scaffold/validator
    scripts, quality references, tests, synced plugin mirror surfaces, and
    `docs/operator-progressive-path.md`.
  - Outcome: added applicability-gated shared generative sequence reference;
    migrated quality artifact contract to `Recommended Next Quality Moves`;
    retained legacy `Recommended Next Gates` parser compatibility; kept move
    cards advisory and scoped to recommended moves only.
  - Verification: focused pytest `80 passed`; ruff passed; `validate_skills.py`
    passed; markdown and doc links passed; pilot quality artifact validated.
  - Non-claims: no new blocking floor; no release publish/version bump; no
    broad pytest closeout yet.
- Slice 2 — `create-cli` pilot and thin hook propagation.
  - Routing: `quality` target-skill review plus `critique` fresh-eye pilot
    review.
  - Changed surfaces: `skills/public/create-cli/SKILL.md`,
    `charness-artifacts/quality/2026-06-27-create-cli-capability-move-pilot.md`,
    and thin references in `ideation`, `spec`, and `create-skill`.
  - Outcome: `create-cli` step 6 now selects gates from the command capability
    seam already established by operator contract, command surface, mutation
    rules, and distribution contract. Adjacent hooks only reference the shared
    lens lightly.
  - Verification: same focused pytest/ruff/skill/doc checks as Slice 1 after
    mirror sync.
  - Non-claims: no second target-skill pilot yet; no strict schema for move-card
    fields; no Cautilus run.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/design-north-star.md` — governing standard: brief a capable judge, teeth
  only where a wrong answer escapes.
- `docs/conventions/implementation-discipline.md` — floor-addition restraint and
  mutation/sync/verify/publish phase barriers.
- `charness-artifacts/gather/2026-06-18-capabilities-over-features.md` —
  capability-over-feature lens: orthogonal, composable, learnable capability
  instead of feature count.
- `charness-artifacts/gather/2026-06-27-genseq3-skill.md` — source capture for
  genseq3.
- `skills/public/quality/SKILL.md` and
  `skills/public/quality/references/skill-ergonomics.md` — current quality
  contract and advisory skill-ergonomics posture.
- `git log --since=2026-06-20 -- skills/public/quality ...` — recent quality
  history showing report-first planner, planner-catalog slimming, and structural
  review strengthening.
- `charness-artifacts/critique/2026-06-27-042558-packet.md` — prepare packet for
  the design critique run.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Decision: where to absorb `genseq3`.
  Chosen: shared sequencing reference with an applicability guard.
  Rejected: embedding it in `create-skill`, because sequencing is useful beyond
  skill authoring and would overcouple a common pattern to one public workflow.
  Rejected: universal doctrine, because the lens should fire only for
  sequencing-shaped capability failures.
- Decision: how `quality` should propose improvements.
  Chosen: `Recommended Next Quality Moves` with move types beyond gates.
  Rejected: strengthening `Recommended Next Gates`, because recent quality
  history and floor-addition restraint push away from reflexive gate expansion.
- Decision: rollout order.
  Chosen: shared reference, quality contract migration, target-skill packet,
  `create-cli` pilot, pilot critique, then thin hooks.
  Rejected: immediately updating `ideation`, `spec`, and `create-skill`, because
  that would spread untested vocabulary before a bounded pilot.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Fresh-Eye Satisfaction: parent-delegated.
Packet Consumed: `charness-artifacts/critique/2026-06-27-042558-packet.md`.
Target: decision lock-in critique.

Act Before Ship:

- Shared reference must say: use sequencing only when order changes correctness,
  uncertainty reduction, or downstream unlocks; first name the capability
  failure; if the failure is not sequencing-shaped, do not force the lens.
- Quality artifact contract must rename output to `Recommended Next Quality
  Moves` and move machinery with it; heading-only rename is cosmetic.
- Target-skill structural review must center consumer capability. Authoring/form
  questions are allowed only when they explain weak capability.
- Do not hook `ideation`, `spec`, or `create-skill` before one bounded pilot
  proves the packet is useful.

Bundle Anyway:

- Temporary parser alias: accept `Recommended Next Gates` with a non-blocking
  deprecation note; new scaffolds write only `Recommended Next Quality Moves`.
- Move cards apply only to recommended moves, not every finding. Missing or
  uncertain enforcement posture defaults to advisory or no-gate.

Over-Worry:

- Do not reject a shared reference entirely; bounded shared reference is cheaper
  than duplicating sequencing folklore across skills.
- Do not avoid the rename because of heading churn; compatibility alias handles
  churn without freezing the bad abstraction.

Valid but Defer:

- Full `create-skill` doctrine rewrite.
- Broad rollout to `ideation`, `spec`, and `create-skill` before the pilot.

Pilot critique:

- Fresh-eye capability/usefulness angle: vocabulary is not cosmetic because the
  planner now asks capability, sequencing applicability, centers, transformation,
  proof boundary, and posture questions; however the first pilot artifact was
  too meta. Folded fixes: `create-cli` received a concrete proof-seam hook, the
  pilot artifact now answers the packet fields directly, and the proof boundary
  names focused tests plus reviewer judgment.
- Fresh-eye paperwork/gate-churn angle: no new blocking floor was introduced;
  legacy heading compatibility is safe; move cards are not validator-required.
  Folded fixes: split `move_type` from `enforcement_posture`, reduced scaffold
  field density, and updated a stale operator doc mention.
  Fresh-Eye Satisfaction: parent-delegated.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Interrupted v0.56.7 release WIP remains in the worktree and is intentionally
  outside this goal unless the user re-scopes release cleanup.

## Final Verification

Retro: charness-artifacts/retro/2026-06-27-capability-first-skill-redesign-retro.md
Host log probe: skipped: host-log-not-exposed: this runtime exposes no stable goal-scoped token/time/session-log source for a provider-safe host-log probe; efficiency is reviewed through local proof boundaries in the retro.
Disposition review: charness-artifacts/critique/2026-06-27-capability-first-skill-redesign-disposition-review.md

Implementation commit: `10b048e7 Add capability-first quality move pilot`.

Focused verification recorded before commit:

- `python3 -m pytest -q tests/test_quality_scaffold.py tests/test_quality_artifact_report_all.py tests/test_quality_artifact.py tests/quality_gates/test_quality_run_planner.py tests/quality_gates/test_quality_handoff_inventory.py tests/quality_gates/test_quality_skill_docs.py`
  -> `80 passed`
- `python3 -m pytest -q tests/quality_gates/test_inference_interpretation_meta_validator.py tests/quality_gates/test_quality_skill_docs.py`
  -> `40 passed`
- `ruff check ...`, `python3 scripts/validate_skills.py --repo-root .`,
  `python3 scripts/check_doc_links.py --repo-root .`,
  `./scripts/check-markdown.sh ...`, and
  `python3 scripts/validate_attention_state_visibility.py --repo-root ...`
  passed.
- Pre-commit on `10b048e7` passed staged-reversion, staged/worktree
  consistency, py_compile, ruff, length, attention-state, skill validation,
  eval wrapper, adapter validation, mirror drift, doc links, markdown, skill
  contracts, inference/interpretation, bootstrap shim, skill ergonomics, and
  boundary-bypass checks.

Non-claims:

- No release publish, version bump, GitHub issue closeout, external write, or
  live host proof belongs to this goal.
- No broad `run_slice_closeout.py --verification-lock` claim is made here
  because unrelated v0.56.7 release WIP remains in the worktree.
- No new blocking floor was added; the quality-move fields remain advisory and
  the old `Recommended Next Gates` heading remains a compatibility alias.

## User Verification Instructions

- Read `skills/shared/references/generative-sequence.md` and confirm the lens is
  applicability-gated rather than `create-skill`-specific doctrine.
- Inspect `skills/public/quality/SKILL.md`,
  `skills/public/quality/scripts/scaffold_quality_artifact.py`,
  `skills/public/quality/scripts/plan_quality_run.py`, and
  `scripts/validate_quality_artifact.py` for `Recommended Next Quality Moves`
  plus legacy `Recommended Next Gates` compatibility.
- Inspect
  `charness-artifacts/quality/2026-06-27-create-cli-capability-move-pilot.md`
  and `skills/public/create-cli/SKILL.md` to judge whether the pilot improves
  command-capability review without creating gate paperwork.

## Auto-Retro

Retro dispositions: applied: the retro's three Next Improvements are
dispositioned in the retro itself and audited by the bound disposition review;
all are either applied in this goal or constrained by the existing dirty-worktree
boundary.
Structural follow-up: none — the retro names a transferable closeout-ordering
pattern, but the repo-local guard already exists through the goal template and
`describe_goal_closeout_shape.py`; this closeout applies the existing guard
without adding a new floor.
