# Setup Flat-Wiki Quality Bootstrap Contract

Date: 2026-08-25

## Problem

The existing `setup` skill creates a broad Charness operating surface, but it
does not make the Craken-style documentation topology or the quality/hook
approval boundary explicit. It can also make roadmap and operator-acceptance
files look universal when they are conditional.

## Capability Contract

`setup` must produce a read-only, approval-gated plan for a Craken-like
flat-wiki operating surface and a quality-owned bootstrap. It must show current
docs, language/code evidence, existing tools, hook manager, scope policy, and
quality adapter state. It must never write, install, move, register, or change a
ratchet before explicit approval of that exact plan.

## Fixed Decisions

- Core profile: minimal README, AGENTS/CLAUDE policy, and `docs/index.md`.
- New docs are flat under `docs/`; existing nested docs are not moved implicitly.
- Lefthook is recommended only when no hook manager exists, for declarative
  stages, parallelism, file filters, worktree install, and visible failure logs.
- Existing Git-native hooks, Husky, simple-git-hooks, and Lefthook are preserved
  and integrated; replacement needs a separate migration approval.
- Hooks prefer staged/related-file scope. Whole-repo checks belong to pre-push or
  CI unless explicitly approved. `lint-staged` is a fallback, not the target.
- Quality owns exact adapters, gates, ratchets, and verdicts; setup reports
  configured/unconfigured, never green/red quality claims.
- Roadmap and operator-acceptance are conditional surfaces.

## Probe Questions

- Which language-specific tool preset and native scoped command best fit a
  repository's detected code structure?
- Is `awiki` available and healthy on the target host, and can its graph result
  be read back by the quality consumer?

## Non-Goals

No product ideation, repo-wide quality audit, automatic document migration,
silent hook replacement, dependency installation, or ratchet baseline rewrite.

## Success Criteria

- `inspect_repo.py` emits `profile.approval_required`, `profile.plan_only`, and
  profile missing-surface facts.
- The same payload exposes `quality_setup.owner_skill == quality`, adapter
  status, quality bootstrap commands, tool evidence, hook preference/respect
  policy, and staged/related-file scope requirements.
- Setup prose explicitly requires approval before mutation and routes final
  quality judgment to `quality`.
- Existing setup inspection behavior remains compatible for legacy core-surface
  mode classification.

## Acceptance Checks

- Verification type: unit — setup inspection fixtures cover flat-wiki approval,
  quality owner state, package/linter evidence, and existing Husky preservation.
- Verification type: unit — setup docs contract pins the profile, Lefthook
  preference, hook respect, lint-staged scope fallback, and quality ownership.
- Verification type: integration — `validate_skills.py`, `check_skill_contracts.py`,
  source/plugin sync, and setup inspection tests pass.
- Verification type: manual — review a real consumer plan and approve or decline
  before applying it; this slice does not claim that live host setup ran.

## Boundary Ownership

- Producer: setup inspector and quality bootstrap planner.
- Consumer: setup operator deciding whether to apply the named plan.
- Owning surface: setup plan and quality adapter/plan commands.
- Verdict: cross-surface — setup proposes; quality owns quality verdicts; the user owns mutation approval.

## Critique

- Structural risk: “recommended Lefthook” could become silent replacement; fixed
  by emitting `preserve-and-integrate` for any detected manager.
- Proof risk: a passing linter command could be mistaken for approval or quality
  readiness; fixed by separate `approval_required`, adapter `status`, and quality
  non-claims.
- Scope risk: fast hooks could become whole-repo scans or mis-scoped `lint-staged`;
  fixed by a staged/related-file policy in the plan and profile reference.

## Canonical Artifact

`skills/public/setup/SKILL.md`,
`skills/public/setup/references/craken-like-profile.md`, and the setup inspection
payload are canonical for this slice.

## First Implementation Slice

Expose the plan and quality state in `inspect_repo.py`, update setup contracts and
references, mirror the plugin surface, and prove the read-only behavior before
adding any consumer-specific apply templates.
