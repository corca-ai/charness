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

- **nose 0.14.0 compat pass COMPLETE → committed local, NOT pushed (ahead 1).**
  Commit `789d2d7d` (mechanics there). schema v4 query JSON parses **unchanged**
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

- **PUSH the nose compat commit, then roll out — operator-gated (see Discuss).**
  Compat is done + verified (Current State); the only open action is the push
  go/no-go + rollout, no re-verification needed. Pushing the `>=0.14.0` floor
  **couples pulling machines**: one still on an older nose reports `doctor` version
  `status: mismatch` (verified here: 0.14.0 → `matched`) and its clone/dup-ratchet
  baselines won't match the 0.14.0-seeded ids (version-coupled drift). Sequence:
  push → `charness update all` on each machine (re-runs nose's installer = latest
  = 0.14.0).
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

- **nose rollout — verdict: YES, now safe.** The compat blocker is cleared:
  consumers parse schema v4, baselines re-seeded to 0.14.0, `doctor` matches the
  new floor. The only remaining call is **operator go to push `789d2d7d` to
  origin/main** (after which a pulling machine on an older nose shows `doctor`
  version `mismatch` until it runs `update all`) and then recommend `update all`
  broadly.

## References

- [nose manifest](../integrations/tools/nose.json),
  [design north star](./design-north-star.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md)
