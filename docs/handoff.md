# Charness Handoff

## Workflow Trigger

- The latest release is published and read back (`git describe --tags --abbrev=0`;
  `gh release view` reported draft=false). Do not re-run any release phase.
- The backlog goal is COMPLETE. Start from the two owed items in `## Next Session`.

## Current State

- 19 open issues, from 24. Eleven closed: nine consolidations render `NOT_PLANNED`,
  two resolutions (`#554`, `#571`) render `COMPLETED`.
- Four umbrellas filed — `#582` `#583` `#584` `#585` — each naming its members and
  each passing the consolidation readback against the live tracker before any close.
- `#514` was refused by the crosswalk (`matrix_incomplete`); that instance is now
  RETIRED by operator ruling — see
  [the retirement record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md).
  `#582` carries a correction saying it absorbed three of four members.
- New: `#586` (a check that never fires on the wired path), `#587` (serial pre-push
  aggregate), `#580` (budget measures fan-out), `#581` (shipped adapter example
  cannot create an issue). `#572` still the one open red; untouched.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

0. Read the closing
   [retro](../charness-artifacts/retro/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md)
   — measured waste, north-star alignment, and the axis that became `#586`.
1. **Design the successor goal.** The closing session declined it with a weak
   reason and said so. `#586` is the strongest axis: six measured instances, three
   candidate guards ranked, vocabulary-parity clearly cheapest.
2. `#546` has a refuted option, not a fix — a repair was built, reviewed HOLD,
   measured defective, and reverted; its comment carries the alternative. `#580`
   stays open on its root cause: the bar still measures fan-out, not the check.

## Discuss

- **`#514`/`#515`/`#518` are SETTLED and closed.** Operator ruling retired the
  crosswalk instance rather than building its matrix; do not rebuild it or re-open
  "protect all three at equal strength". Reasoning, lapsed protections, and
  non-claims are in the retirement record. The "consumer-repo measurement" blocker
  was false: only `#518` ever carried a `Re-read obligation` and its debug artifact
  discharged it.
- `#576` has no chosen direction; a comment records why it is honest silence.
- The `Premise-residue:` seam reads markers and nothing writes them; exactly one
  exists. If records do not start writing them the record channel stays empty.

## Continuation Capability

- **A check can exist, pass its tests, and never run on the caller's path.** Six
  instances in one goal. Coverage and reachability are different questions — the
  changed-line gate caught none of them, because the lines WERE covered by the
  direct-call test.
- **The round that reads the REPAIRS finds a different class than the round that
  reads the original.** Four for four; one returned HOLD and killed a repair.
- **Run the cheapest disconfirming probe BEFORE building a heuristic.** Two designs
  were built and deleted; both probes took under a minute and both ran too late. A
  constant whose tuning history you can narrate is a fitted constant.
- **Hardcoded prose in a portable skill fails silently in consumer repos.** Prefer a
  typed marker an author writes over wording a scanner infers.
- **Let the floors refuse your own work.** Three fired on this session's own
  mutations before they landed, and each was right.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
