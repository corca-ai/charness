# Operator-acceptance items closed with Goal Run #765 — moved verbatim from `docs/operator-acceptance.md` on 2026-09-03 (link targets repointed to this directory).

### 1. Close Deferred Decisions

Focus: keep deferred product-boundary decisions closed unless a real reopen trigger is active.

Read first:

- [docs/goal-lifecycle.md](../../../docs/goal-lifecycle.md) — current Goal Run parent/cursor and continuation contract.
- [docs/deferred-decisions.md](../../../docs/deferred-decisions.md) — closed product-boundary decisions, record shape, and reopen triggers.
- [docs/host-packaging.md](../../../docs/host-packaging.md) — export contract for host plugin layouts and its source-of-truth surfaces.
- [docs/control-plane.md](../../../docs/control-plane.md) — external tool manifests, support capability metadata, and lock state rules.

Acceptance:

- [`docs/deferred-decisions.md`](../../../docs/deferred-decisions.md) stays in sync with current product-boundary choices.
- The active Goal Run parent/cursor is current and has no stale next-child claim.
- Any reopened decision records its new choice and impacted docs.
- [`./scripts/run-quality.sh`](../../../scripts/run-quality.sh) passes after the doc updates.

### 3. Raise `create-skill` / `spec` Workflow Gates

Focus: move `create-skill` and `spec` from marker-level checks to stronger workflow smoke.

Read first:

- [skills/public/create-skill/SKILL.md](../../../skills/public/create-skill/SKILL.md) — the portable skill authoring workflow and its bootstrap reads.
- [skills/public/spec/SKILL.md](../../../skills/public/spec/SKILL.md) — the implementation-contract workflow and its bootstrap reads.
- [docs/public-skill-dogfood.md](../../../docs/public-skill-dogfood.md) — human-readable contract for the reviewed consumer-prompt registry.
- [tools/check_skill_contracts.py](../../../tools/check_skill_contracts.py) — pinned SKILL.md contract phrases and the pin-deletion discipline.
- [tools/run_evals.py](../../../tools/run_evals.py) — runner for the repo-owned deterministic skill and adapter scenarios.
- [tools/validate_public_skill_dogfood.py](../../../tools/validate_public_skill_dogfood.py) — validator entrypoint for the dogfood registry JSON.

Acceptance:

- at least one stronger deterministic workflow check exists for each targeted
  skill
- docs and tests describe the stronger proof honestly
- [`./scripts/run-quality.sh`](../../../scripts/run-quality.sh) passes

### 4. Decide Adapter Requirements Per Public Skill

Focus: classify which public skills must fail closed on missing adapters and turn that into a deterministic rule.

Read first:

- [skills/public/impl/SKILL.md](../../../skills/public/impl/SKILL.md) — the slice implementation workflow and its conditional evidence route to `prove`.
- [skills/public/quality/SKILL.md](../../../skills/public/quality/SKILL.md) — the quality posture workflow, adapter bootstrap, and gate planning.
- [docs/public-skill-validation.md](../../../docs/public-skill-validation.md) — validation tiers plus per-skill adapter and missing-adapter rules.
- [charness-artifacts/quality/latest.md](../../../charness-artifacts/quality/latest.md) — the latest quality review: scope, gates, weak and missing areas.

Useful local commands:

```bash
for d in skills/public/*; do [ -f "$d/adapter.example.yaml" ] && echo "adapter $d" || echo "no-adapter $d"; done
python3 scripts/gates/validate_adapters.py --repo-root .
```

Acceptance:

- the classification is recorded in canonical docs and machine-readable policy
- missing-adapter behavior is explicit per public skill: `allow`, `visible`,
  or `block`
- high-leverage repo-truth, review-state, or release skills do not silently
  fall back when their adapter contract is missing
- [`./scripts/run-quality.sh`](../../../scripts/run-quality.sh) passes
