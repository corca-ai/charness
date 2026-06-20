# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **nose 0.14.0 compat pass COMPLETE → committed + PUSHED to origin/main**
  (@ `8d5f9998`; compat commit `789d2d7d`, mechanics there). Push verified via
  `git ls-remote` + `gh api` (distinct channels). schema v4 query JSON parses **unchanged**
  (no consumer code touched); the family-id set shifted, so re-seeded
  [nose-baseline.json](../charness-artifacts/quality/nose-baseline.json) (487→491)
  and [dup-ratchet-baseline.json](../charness-artifacts/quality/dup-ratchet-baseline.json)
  (`--confirm-baseline-delta`, deliberate version swing). Tree was clean → all
  drift is scanner-version-attributable.
  [doc-nose-baseline.json](../charness-artifacts/quality/doc-nose-baseline.json)
  unchanged (signature-keyed, 0 drift). Floor bumped `>=0.13.3 → >=0.14.0` +
  synced mirror.
- **Verify:** 91 nose/dup-ratchet tests; clone advisory clean; dup-ratchet exit 0;
  `validate_integrations` ok; `doctor` ok; fresh-eye **SOUND**.
- **v0.53.0 live** (prior session): skill-body redesign released.

## Next Session

- **Roll out nose 0.14.0 to the other machines.** Push is done (origin/main @
  `8d5f9998`); the only remaining action is `charness update all` on each machine
  (re-runs nose's installer = latest = 0.14.0). Until a machine updates, its
  `doctor` shows nose version `mismatch` against the new `>=0.14.0` floor —
  expected, clears on `update all`.
- **Leverage 0.14.0 (optional, not compat-required).** New `nose query --root/-r`
  multi-root + advertised `query.capabilities.multi_root` could collapse the
  per-root loop in `collect_families`; hidden `nose gap-impact` diagnostic exists.
- **`quality` anchor-split (ODQ #2).** Still blocked: `## Load-Bearing Anchors` is
  pinned by ~60 [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py)
  assertions. Unblock = operator approves moving them to
  `quality/references/inventory-dispatch.md`, then collapse the catalog (pure
  clarity, pressure-exempt). See the skill-body goal ODQ.
- **Deferred proofs / open tracks:** overhaul-sweep R2 (a real `issue resolve`/
  PR-close through the floors); **ceal #417** (propagate the doctrine); gate
  demotions (`check_doc_links` backtick→advisory; `--reuse-coverage` skip);
  **untouched issues:** #387, #391, #392, #371, #394, #395.

## Discuss

- **nose rollout — DECIDED + EXECUTED this session.** Operator approved push;
  compat is on origin/main. No open decision remains — residual is purely the
  per-machine `charness update all` (Next Session). Re-open only if a machine
  reports unexpected nose breakage after updating.

## References

- [nose manifest](../integrations/tools/nose.json),
  [design north star](./design-north-star.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md)
