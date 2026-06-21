# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff entries + live open issues. `## Next Session` is
  sequencing judgment, not the full queue — **body-read the issues, don't trust it flat.**
- Refresh: `git status -sb`, `git log --oneline origin/main..HEAD`,
  `gh issue list --state open --limit 50`, and skim `git log --oneline -10`
  (de-stale the queue against what recently shipped). Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Essence/deletion redesign — the `impl` exemplar EXECUTED this session.** The
  steer: distill to essence and **DELETE** duplication, not relocate
  (`less but better`, progressive disclosure). Key lever: **the gate pins mark the
  load-bearing essence, so delete the unpinned duplication around them** — zero
  edits to `check_skill_contracts.py` or any test. Guardrails 9→2 via `achieve`'s
  name-the-rule template; Workflow step 4 13→4 by deferring to
  `references/verification-ladder.md`; 194→187 lines; 2 fresh-eye
  `ESSENCE-PRESERVED` / `CONTRACT-HONEST`.
  [critique](../charness-artifacts/critique/2026-06-21-impl-essence-deletion.md).
- **Recipe now proven** — supersedes the sweep goal's "deferred-with-cause: lossy"
  note. `quality`'s earlier anchor-split only **relocated** (191 body, 49 refs);
  real deletion is still owed there.
- **`main` red by one (environmental):** the `nose doctor` version-mismatch test
  fails on clean HEAD too (this machine's nose vs the manifest). Item B owns it.

## Next Session

> This session the operator redirected from the prior green-main-first queue to
> **skill essence**. The live thread is the exemplar rollout; the prior queue is
> parked-but-pending below. **Body-read each issue — titles undersell.**

- **A — Essence/deletion rollout (live thread).** Apply the proven recipe to
  `debug` then `quality`: (1) classify each block KEEP-essence / DISCLOSE-to-ref /
  DELETE-duplication; (2) gate pins mark essence — delete the unpinned duplication
  around them; (3) `achieve`'s Guardrails are the name-the-rule template;
  (4) verify full `tests/quality_gates/` + 2 fresh-eye. `debug`: the thrice-printed
  `issue resolve invokes the same substrate` cross-ref + helper-duplicating
  Bootstrap prose. `quality`: delete the anchors the split relocated-not-deleted.
  `achieve` already models the target.
- **B — Green `main` + #394 triage (parked from prior queue).** Diagnose the
  standing-red `nose doctor` version-mismatch (machine nose vs manifest); triage
  #394's 12 survived *config-literal* mutants
  (`init_adapter.py` / `resolve_adapter.py` `...: True`). Score passes (90% vs 80%).
- **C — #387 one-pass goal-closeout shape report.** Every missing/malformed
  required closeout line in one pass; fits `describe_goal_closeout_shape.py`
  (describe-first preflight), not a new blocking floor.
- **D — #392 gather-X honest-failure contract.** Typed result
  (`exact-acquired | blocked-by-X | auth/browser-route-required | unsupported`) +
  route-level trace + a regression fixture. Scope call at pickup (see Discuss).
- **Parked:** #371 (upstream-blocked vercel-labs/agent-browser#1334; verify
  `charness tool repair agent-browser`). #391 extraction candidates. D30/D31 in
  [deferred-decisions.md](./deferred-decisions.md).

## Discuss

- **#392 scope (decide at pickup of D):** attempt a real exact-X route
  (browser/auth — likely infeasible) vs commit to the typed-unsupported contract.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale (done again this session).

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [north-star sweep goal](../charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md),
  [deferred-decisions](./deferred-decisions.md)
