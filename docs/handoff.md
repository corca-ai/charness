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

- **North-Star Overhaul → a pursue-ready `achieve` goal.** This session moved it from
  roadmap-only to executable:
  [overhaul-sweep goal](../charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md)
  (`check_goal_artifact --pursue-ready = True`; Status: draft, inert until `/goal`). Done
  this session: Phase 0 diagnosis back-test (PARTIALLY CONFIRMED → proceed; sharpened to
  distinct-*channel* not anti-gate, + #385 mirror-image); Dynamic Workflows standing
  pre-authorization (AGENTS.md + wired via `setup`); matt-skills + craken + the arrived
  bug-hunt/better-UT absorbed under baseline discipline (small net-new core — notes under
  `charness-artifacts/audit/2026-06-20-*`).
- **v0.52.6 still the released surface** — no release this session; all commits are
  docs/artifacts. Several commits ahead of origin/main; push at maintainer cadence.

## Next Session

- **TOP PRIORITY — activate the overhaul-sweep goal:**
  `/goal @charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md` (pursue-ready;
  operator deferred activation to this session per the 2026-06-20 decision). Slices:
  **S0** concept spec + critique (gating) → **S1 R2** (wire the #386 distinct-channel
  observer + an AI-provenance marker onto the standalone `issue resolve`/PR-close path —
  the open escape: that path has no coded rung-2 today, `CLOSED` is the terminal-green
  proxy) → **S2 R1** (de-dup the rung-1 grammar cloned ~4x into one shared substrate) →
  **S3 WS-B** (capped-body redesign with the absorbed instruments + graft a new
  `quality/references/unit-test-quality.md`) → **S4** closeout. 6 consolidation
  risk-constraints are binding (see the goal). Design inputs: the
  [Phase-0 back-test](../charness-artifacts/audit/2026-06-20-north-star-phase0-diagnosis-backtest.md),
  the [reference-absorption note](../charness-artifacts/audit/2026-06-20-reference-absorption-overhaul-inputs.md),
  and cluster-survey `wf_f03ba5fe-62d` (per-unit-disposition family map; ephemeral — folded
  into S0). The [roadmap](./north-star-overhaul-roadmap.md) Phase 0 block is now resolved.
- **Reference absorption is current.** matt-skills first pass done; craken bug-hunt +
  better-UT (the pending-share arrivals) evaluated per-surface + folded (both MOSTLY-CONVERGENT;
  only net-new = the WS-B `unit-test-quality.md` graft). Re-run craken absorption only if
  new material arrives.
- **ceal propagation — issue filed (corca-ai/ceal#417)** — unchanged; the overhaul doctrine
  stays deferred there until charness embodies it (S0–S4 above).
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
