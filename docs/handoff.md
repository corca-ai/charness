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

- **Skill-body redesign goal COMPLETE → released v0.53.0** (this session).
  [Goal](../charness-artifacts/goals/2026-06-20-skill-body-redesign-and-release.md)
  `complete`: **18 of 20 public bodies cured** (clarity-first guardrail-cluster
  collapses, every CORE/PACKAGE/test pin preserved verbatim), **2 deferred-with-cause**
  (`hotl` justified-density; `quality` anchor catalog is test-pinned → see ODQ).
  Built [check_skill_cut_safety.py](../scripts/check_skill_cut_safety.py) (pre-cut lossless+contract-safe check).
  Broad pytest 3453/0; per-slice + rung-2 closeout fresh-eye PASS.
- **v0.53.0 live** (operator-approved): the deferred **WS-1 live-floor proof** —
  rung-1 presence + rung-2 distinct-channel observer, confirmed via `git ls-remote`
  and `gh api` (channels distinct from `gh release view`); origin/main pushed, clean.
- **Metric discipline:** count is NOT the metric in either direction; proof =
  escape-closed + concept-clearer
  ([goodhart retro](../charness-artifacts/retro/2026-06-20-goodhart-not-line-count.md)).

## Next Session

- **`nose` new version — compat + leverage (operator-flagged).** `charness update all`
  IS the intended one-command path on other machines (it runs `charness tool update`,
  which re-runs nose's upstream installer = `releases/latest` → newest nose). But it is
  **not safe to roll out broadly until a charness-side compat pass** — `nose` has made
  breaking changes before (0.13.3 removed `nose scan`; code uses `nose query`), and the
  manifest pins only `>=0.13.3` (no upper bound). Do, via `quality`: install the new nose
  locally; run the nose consumers (`inventory_nose_clones.py`, `check_dup_ratchet.py`,
  doc-near-duplicate) and confirm `nose query` output still parses; **re-baseline the
  nose advisory baseline ([nose-baseline.json](../charness-artifacts/quality/nose-baseline.json))
  for the new scanner version**; bump the [nose manifest](../integrations/tools/nose.json)
  floor if warranted; leverage any new capability. THEN
  `update all` everywhere is safe.
- **`quality` anchor-split (Operator Decision Queue #2).** The diagnosed §5 anchor-split
  is deferred because `## Load-Bearing Anchors` is pinned by ~60
  [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py)
  assertions → a contract change. Unblock = operator approves moving those assertions to
  `quality/references/inventory-dispatch.md`, then collapse the catalog (pressure-exempt, so
  no headroom is at stake — pure clarity). See the goal ODQ.
- **Deferred proofs / open tracks:** overhaul-sweep R2 (a real `issue resolve`/PR-close
  through the floors); **ceal #417** (charness now embodies the full doctrine → propagate);
  gate demotions (`check_doc_links` backtick→advisory; `--reuse-coverage` skip);
  **untouched:** #391, #392, #371, #394, #395.

## Discuss

- **`nose` rollout:** is the new version safe to push to all machines via `update all`?
  Decision after the compat pass above — do not recommend broadly until the quality nose
  consumers are confirmed against it (a silent `nose query` change would break the gate on
  every updated machine).

## References

- [skill-body goal](../charness-artifacts/goals/2026-06-20-skill-body-redesign-and-release.md)
  (ODQ + final verification),
  [design north star](./design-north-star.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md)
