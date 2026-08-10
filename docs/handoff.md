# Charness Handoff

## Workflow Trigger

- No goal is running. The release is published and read back; do not re-run any
  release phase. Start from `## Next Session` item 0.
- Eight commits are UNPUSHED, from `93b2e1dc` through HEAD. Push needs its own
  grant; `git log --oneline origin/main..HEAD` lists them.

## Current State

- `#514`/`#515`/`#518` closed `NOT_PLANNED` on 2026-08-10 after the evidence-boundary
  crosswalk instance was RETIRED by operator ruling — see
  [the retirement record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md);
  do not rebuild that matrix.
- Filed 2026-08-10: `#588`, `#589`, `#590`, plus `#591`-`#594` from the matrix slice
  and the `#591` fix. `#591` is FIXED and awaiting closeout; `#592`-`#594` are open.
- `#572` is the one open red. `#590` diagnosed it and REPAIRED THE REPORTING at
  `739a2a3e`; the failure itself is untouched, so the lane is still red. `#586` stays
  open — the matrix slice covers instance 2 only.
- `dup-ratchet` and `check-changed-line-mutation-coverage` are red and BOTH predate the
  matrix slice, whose own files are clear: the dup families sit in untouched files and
  were already red at `ba899083`, and the blocked mutation-pool files are owned by
  `739a2a3e`. Recount with `bash scripts/run-quality.sh`; logs land under `.charness/`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

0. **`#572` needs the diagnostic ON MAIN before it can move.** The instrumentation
   that names the cause is at `739a2a3e`, which is UNPUSHED — so the cron run
   (`17 */12 * * *`) still executes the uninstrumented test and reports nothing new.
   The test passes locally, so it cannot be reproduced here either. This item is
   blocked on a push grant; do not re-diagnose it from this tree.
1. **Close `#591`** — the fix landed (both floors ungated, blast radius measured at
   zero across 87 historical carriers, two bounded rounds, 134 matrix cells firing).
   It needs the `issue` closeout floor run against it, nothing more.
2. **`#593` and `#594`** — both found by bounded review of that fix, both pre-existing,
   both false-refusal paths at the irreversible boundary. `#593` is the smaller and
   has its fix shape named on the issue. `#592` stays open and unbuilt by decision:
   no release has ever used `--close-issue`.
3. **`#590` left a gap, recorded on the issue:** the mutation workflow's inline script
   body has ZERO automated coverage. Item 0's cron run is the only check on it.
4. `#546` has a refuted option, not a fix — reviewed HOLD, measured defective, reverted.

## Discuss

- `#576` has no chosen direction; a comment records why it is honest silence.
- `#587` and `#580` were measured and both had a false premise; both are retitled
  with it. `#580` blocks nothing. `#587` asks one thing, answerable only from the
  original session's record, not this tree.
- The `Premise-residue:` seam reads markers and nothing writes them. If records do not
  start writing them the record channel stays empty.
- The matrix's `not_measured` names six gaps; two are worth a slice (the `commit-msg`
  sub-paths, and the `_missing_ledger_fields` asymmetry on `close-with-comment`).

## Continuation Capability

- **Read the exit code of the thing you ran, not the pipeline's.** `pytest …; echo $?;
  tail` reported green twice off `tail`'s exit; the real run had 19 failures.
- **The round that reads the REPAIRS finds a different class.** Eight for eight, twice
  more today — each time a round-1 repair had bought a smaller copy of its own defect.
- **A gate generated from its own measurement agrees by construction.** The pin that
  matters is "the observation MOVES when the code does", not "the gate is green". The
  matrix earned its keep on its first real change: 26 findings, unprompted.
- **When a floor widens, the surfaces that TELL authors what it wants are where the
  blockers are.** Both rounds of the `#591` fix found them there, not in the floors.
- **Adding a gate to the quality runner is four registrations:** the seeded harness
  stub, a timing verdict in
  [validator-timing-layers](./conventions/validator-timing-layers.md), `release_only`
  on any repo-copy test, and the surfaces entry. The suite names each one.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
