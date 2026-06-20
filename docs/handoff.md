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

- **#395 dup-ratchet family_id churn — RESOLVED + CLOSED + PUSHED**
  (@ `6658acec`). The gate keyed code-newness on nose's family `id`, which folds
  member line-offset + file path (not just content), so member-file edits rotated
  ids and false-blocked with zero new duplication. Solution (a) is impossible
  (nose emits no position-independent id); shipped reporter solution (b): doc
  correction across 3 carriers + a real-nose characterization test + lockstep
  re-baseline. The affordance (solution c) is deferred as **D30** in
  [deferred-decisions.md](./deferred-decisions.md). Mechanics + RCA:
  [debug artifact](../charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md).
- **Chunk-2 multi-root resolver — DONE + PUSHED** (@ `91aae959`). `collect_families`
  now runs ONE nose 0.14.0 `--root` multi-root query (global clustering) instead of
  a per-root loop. **Quality-contract change**: family set 491→525 (gains 108
  cross-root clone families the per-root loop missed; both id-set baselines
  re-baselined lockstep, `--confirm-baseline-delta`). Critiqued (3 angles +
  counterweight):
  [critique](../charness-artifacts/critique/2026-06-21-quality-nose-multiroot-resolver.md).
- **nose 0.14.0 floor live** (@ `8d5f9998`); **this machine's installed plugin
  updated** (`charness update all`, doctor `matched` @ `>=0.14.0`). Other machines
  still pending their own `update all`.

## Next Session

- **Other-machine nose rollout (operator).** Run `charness update all` on each
  remaining machine. Low urgency — nothing is broken (binaries are fine); this
  just propagates the pushed repo state to each installed plugin.
- **D30 — dup-ratchet id-rotation affordance.** The real relief for #395's
  false-block (recognize a pure rotation by position-independent member set →
  downgrade hard-block to advisory). Needs a baseline schema migration + must guard
  the false-negative (a new clone reusing the same member files). See
  [deferred-decisions.md](./deferred-decisions.md) D30.
- **`quality` anchor-split (ODQ #2).** Still blocked: `## Load-Bearing Anchors` is
  pinned by ~60 [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py)
  assertions; unblock = operator approves moving them to
  `quality/references/inventory-dispatch.md`, then collapse the catalog.
- **Open issues:** #394 (mutation regression on main), #387, #391, #392, #371.
- **Deferred proofs:** overhaul-sweep R2 (a real `issue resolve`/PR-close through
  the floors); **ceal #417**; gate demotions (`check_doc_links` backtick→advisory;
  `--reuse-coverage` skip).

## Discuss

- **Multi-root clone model is now live (chunk-2).** It is a deliberate
  quality-contract change (per-root → global). If a consumer repo behaves oddly on
  the new global clone model, that is the first place to look — but it is verified,
  critiqued, and the coverage shift (51 marginal within-root spans dropped, 186
  cross-root spans gained) is documented in the commit body + critique.

## References

- [nose manifest](../integrations/tools/nose.json),
  [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [design north star](./design-north-star.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md)
