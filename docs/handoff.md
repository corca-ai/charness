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

- **North-Star Overhaul — the [overhaul-sweep goal](../charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md)
  is COMPLETE** (`check_goal_artifact` ok; 5 slices/commits; broad pytest 3428/0).
  Roadmap now: **P0 done, P1 landed, P2 done, P3 partial, P4 not started.** P2 (root-cause
  win): issue/PR close no longer greens on `CLOSED`+form — rung-1 block-the-silent
  behavioral-verdict + AI-provenance floors + rung-2 observer, **no terminal-green gate**;
  the cloned rung-1 grammar collapsed to one substrate `goal_artifact_floor_grammar.py`.
  P3 (WS-B): `unit-test-quality.md` graft + a lossless `find-skills` cure landed; deeper
  body redesign **deferred with cause** (cuts contract-pinned/lossy — see the goal+retro).
- **v0.52.6 still the released surface** — no release. **18 commits ahead of origin/main,
  unpushed**; push at maintainer cadence.

## Next Session

- **TOP PRIORITY — Phase 4: non-terminality at the REMAINING irreversible boundaries.**
  P2 made *one* boundary (issue/PR close) non-terminal; the others still carry the
  terminal-green pattern the diagnosis named. Extend the now-built rung-1/rung-2 +
  floor-grammar pattern to: **release publish**, **prod apply**, and **Direction-3**
  (`issue_tool.py verify-closeout` refuses on undispositioned HOTL entries — the second
  consumer #386 deferred). Mostly *reuse* of the proven pattern, not invention. Follow the
  [roadmap](./north-star-overhaul-roadmap.md) Phase 4 + the Phase-0 migration discipline
  (name failure-mode → land replacement → seeded proof → then delete + rollback ref).
  Shape it as an `achieve` goal (the overhaul-sweep goal is the template).
- **Deferred from the overhaul-sweep goal (operator items, both external writes):**
  (1) a **live GitHub R2 proof** — run a real `issue resolve`/PR-close exercising the new
  floors once a target is named + approved; (2) **file the P3 body-redesign follow-on
  issue** (impl/debug/quality/achieve concept-separation + a pre-cut lossless+contract-safe
  WS-B instrument) — captured in the goal's `## Operator Decision Queue` + the
  [retro](../charness-artifacts/retro/2026-06-20-north-star-overhaul-sweep.md).
- **Push decision:** 18 commits unpushed; review / push / cut a release at maintainer cadence.
- **ceal propagation (corca-ai/ceal#417):** charness now embodies the doctrine at the issue
  boundary; the doctrine can begin propagating to ceal once P4 lands the rest.
- **Secondary — gate demotions:** Track A = demote check_doc_links backtick/bare-mention
  to advisory, then critique/skill-ergonomics demotions. Plus: changed-line gate
  `--reuse-coverage` should skip a coverage file containing none of the changed paths.
- **Untouched:** [#391](https://github.com/corca-ai/charness/issues/391) extractions +
  tool_version stamp; #392 gather X; #371 agent-browser teardown.

## Discuss

- **Operator decided (2026-06-20):** finish the north-star overhaul in charness BEFORE
  propagating the doctrine to ceal — the skills must embody it first. ceal gets the
  already-shipped mechanisms now (separate issue); the overhaul doctrine waits.

## References

- [overhaul-sweep goal](../charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md)
  (the pursue-ready pickup),
- [design north star](./design-north-star.md),
  [north-star overhaul roadmap](./north-star-overhaul-roadmap.md),
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md),
  [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md)
