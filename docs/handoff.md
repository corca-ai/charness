# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over S2's scoped issues —
  and only then invoke `impl` on slice **S2** of the release contract. S1 is
  committed; S2 has not started.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)
  — the owner-approved wide scope, its S1-S7 sequence, and the SC3 deviation that
  is **waiting on an owner ruling** in `## Deviations Awaiting Owner Ruling`.
- [S1 retro](../charness-artifacts/retro/2026-08-15-session-retro.md)
  — what S1 cost, the three repairs that carried the class they fixed, and the
  measured instance of S3's SC6 that this session produced by accident.
- [Contract critique](../charness-artifacts/critique/2026-08-15-release-scope-contract.md)
  — the 21 findings behind the contract's revision 2.
- [Design retro](../charness-artifacts/retro/2026-08-15-release-scope-design.md)
  — why the same lesson failed on the same issue number two days running.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — prepared, and still **false for the tree they would ship**; S7 regenerates
  them, and the S1 gate now refuses them until it does.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
  — the digest a session reads before work.

## Current State

- **S1 is committed and the release tooling is live.** The notes generator, its
  notes-versus-tree gate, the narrative-containment lint, `what-reads-this`
  (#599), and the `check-markdown.sh` npm fallback (#630) all ship. Size and
  identity: `git log --oneline -1`; scope: `git show --stat HEAD`.
- Full suite green at that commit. Re-prove with
  `python3 -m pytest tests/ -q --no-header`; budget ~21 minutes and run it
  BACKGROUNDED — two runs were invalidated this session by editing under an open
  collection.
- Ruff is clean only cache-free. Prove with `ruff check --no-cache .`, never
  `ruff check .`.
- **Two gates are RED and neither is from S1**, both confirmed on a throwaway
  worktree at the pre-S1 HEAD: `check_dup_ratchet` hard-blocks (S1 adds no
  family; all six of its rotations are classified in
  [dup-review](../charness-artifacts/quality/dup-review.json)), and `check-shell`
  reports SC2016 in `run-quality.sh`, which S1 never touched. Somebody owns
  these; S2 should not inherit them silently.
- The release is still PREPARED: no bump, tag, or publish. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .` and
  `python3 skills/public/release/scripts/plan_release_run.py --repo-root . --part major --detail`.
- `plan_risk_interrupt.py` is still **blocked** on interrupt
  `lesson-presentation-compaction-2026-08-14`; this is S3's first item. Confirm
  with `python3 scripts/plan_risk_interrupt.py --repo-root .`.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#632](https://github.com/corca-ai/charness/issues/632):
  eight fixed in-repo and unreleased, three still broken
  ([#628](https://github.com/corca-ai/charness/issues/628),
  [#629](https://github.com/corca-ai/charness/issues/629),
  [#631](https://github.com/corca-ai/charness/issues/631)), four partly valid.
  That split still has no checked-in ledger; the closeout floor requires one.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer
readback, or issue closure. S2-S7 have not started.

## Next Session

1. **Before S2, confirm each scoped issue still reproduces on the current tree.**
   This is the standing remedy, and S1 shows why: the check refuted a live
   assumption about #599 within minutes. Use `python3 scripts/what_reads_this.py`
   — it exists now — for the consumer half of any removal question.
2. **S2** of the release contract: the producer-scaffold class, fixed by
   **subject identity, not date coherence**. The contract's Fixed Decision
   records why a generalized date-coherence guard is inert against
   [#628](https://github.com/corca-ai/charness/issues/628) and would break
   `debug`'s designed continue-in-place behavior. Read it before designing.
3. Then S3-S6 in order, then S7 publishes and closes
   [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record.

## Discuss

- **SC3's deviation needs an owner ruling.** S1 blocks on bare quantities and
  only advises on the six completeness words, because the refusing version
  rejected this repo's own honest-limits language. The criterion stands unamended
  and the evidence is attached; S7 cannot honestly claim SC3 until this is ruled.
- S5 (structural umbrellas) is the least bounded slice; decide its stopping rule
  before starting it, not during.
- Whether `link_only_lines` 0 is the right bar or an honest non-zero one is.

## References

- [Design north star](./design-north-star.md) — the P4 rule S1 leaned on hardest:
  every pre-existing-red attribution came from a different tree, not a re-read.
- [Operating contract](./conventions/operating-contract.md) — the two-round
  critique floor, which earned its keep in S1: round 2 caught three repairs that
  carried the class they fixed.
- [Parallel execution](./conventions/parallel-execution.md).
