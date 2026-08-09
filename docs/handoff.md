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
- `#514` refused by the crosswalk (`matrix_incomplete`); `#582` carries a
  correction saying it absorbed three of four members.
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
2. **Settle `#514` / `#515` / `#518`** — see `## Discuss`.
3. `#546` has a refuted option, not a fix — a repair was built, reviewed HOLD,
   measured defective, and reverted; its comment carries the alternative. `#580`
   stays open on its root cause: the bar still measures fan-out, not the check.

## Discuss

- **The "consumer-repo measurement" blocker on `#514`/`#515`/`#518` is FALSE, and
  its recurrence is the defect.** The completed goal's Non-Goals says those repos
  "have been read repeatedly across sessions and their findings already sit in the
  issue bodies. Measurement is not the bottleneck." Its Verification Plan says the
  opposite; the closing session sided with the wrong one. It keeps resurfacing
  because each issue body carries a `Re-read obligation` that every session treats
  as binding without checking whether the measurement already happened.
- **So the question is what is missing to fold EXISTING findings into the
  crosswalk's acceptance matrix**, which is `matrix_state: bootstrap` with empty
  criteria. Draft criteria for `#518`/`#515` sit in 2026-08-10 comments on those
  issues; they lack `artifact_path` and `final_reader_route` — in-repo work. Trap
  recorded there: a criterion for declared browser/sync surfaces cannot be written
  against current code, so scope it down rather than write a false one.
- Also decide whether the crosswalk should protect all three at equal strength,
  given `#518`/`#515` were substantially repaired by `892d6b95` and `#514` was not.
  `#576` still has no chosen direction; a comment records why it is honest silence.
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
