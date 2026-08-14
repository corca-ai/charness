# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over the scoped issues —
  and only then invoke `impl` on slice **S1** of the release contract. The commit
  that blocked everything is done; the release is scope-locked, not started.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)
  — the owner-approved wide scope, its S1-S7 sequence, and the three weaknesses
  it declares about itself.
- [Contract critique](../charness-artifacts/critique/2026-08-15-release-scope-contract.md)
  — the 21 recorded findings behind the contract's revision 2, including the six
  ruled over-worry and why acting on them would have been the wrong move.
- [Design retro](../charness-artifacts/retro/2026-08-15-release-scope-design.md)
  — why the same lesson failed on the same issue number two days running, and the
  three lessons that worked and could not be recorded.
- [Migration retro](../charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md)
  — what the `--json` removal cost, the four false-completeness claims and their one
  cause, and the two recurrences it scored.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — prepared, and **false for the tree they would ship**; S7 regenerates them.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
  — the digest a session reads before work.

## Current State

- The migration is committed at `eae80f660` and the tree is clean. Prove with
  `git status --porcelain | wc -l`; size it with `git show --stat eae80f660`.
- Full suite green at that commit: **9331 passed**. Prove with
  `python3 -m pytest tests/ -q --no-header`; budget ~22 minutes.
- Ruff is clean only when the cache is bypassed, and that distinction cost a
  false "ruff clean" claim in the 08-15 retro. Prove with
  `ruff check --no-cache .`, never `ruff check .`.
- The release is still PREPARED: no bump, tag, or publish, and the major-bump
  plan reports `blockers: []` with `next_action: needs_critique`. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .` and
  `python3 skills/public/release/scripts/plan_release_run.py --repo-root . --part major --detail`.
- `plan_risk_interrupt.py` is **blocked** on interrupt
  `lesson-presentation-compaction-2026-08-14`: #617's capability shipped but its
  spec and debug artifact still read open. This is S3's first item.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#632](https://github.com/corca-ai/charness/issues/632):
  eight fixed in-repo and unreleased, three still broken
  ([#628](https://github.com/corca-ai/charness/issues/628),
  [#629](https://github.com/corca-ai/charness/issues/629),
  [#631](https://github.com/corca-ai/charness/issues/631)), four partly valid.
  That split has no checked-in ledger yet; the closeout floor requires one.

- The release contract has been through a bounded three-angle review plus a
  counterweight pass; seven blockers were repaired and six findings ruled
  over-worry. Both boundary verifies returned `clean`, so nothing is quarantined.
  Rulings are in the contract's `## Critique`.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer
readback, or issue closure. No slice has been implemented — S1 has not started.

## Next Session

1. **Before S1, confirm each scoped issue still reproduces on the current tree.**
   Only [#608](https://github.com/corca-ai/charness/issues/608) was checked
   against source, and it was already fixed; the rest of the slice list carries
   the same risk. This is the standing remedy in
   [the design retro](../charness-artifacts/retro/2026-08-15-release-scope-design.md).
2. **S1** of the [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md):
   the release-notes generator plus its over-claim gate and narrative-containment
   lint FIRST — built at S1, run at S7, so every later slice lands under it. Then
   the `what-reads-this` command
   ([#599](https://github.com/corca-ai/charness/issues/599)), then
   [#630](https://github.com/corca-ai/charness/issues/630).
3. Then S2-S6 in order. **S2's mechanism is subject identity, not date
   coherence** — the review proved a generalized date-coherence guard is inert
   against [#628](https://github.com/corca-ai/charness/issues/628) and would
   break `debug`'s designed continue-in-place behavior.
4. S7 publishes and closes
   [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record.

## Discuss

- S5 (structural umbrellas) is the least bounded slice in the release; its probe
  question exists because "the class remains" umbrellas do not terminate on their
  own. Decide the stopping rule before starting it, not during.
- Whether `link_only_lines` 0 is the right bar or an honest non-zero one is; the
  contract accepts either, but somebody has to choose after the twenty-line probe.

## References

- [Design north star](./design-north-star.md) — the P4 rule this session leaned on hardest:
  the ruff false green was caught by a different command, not by re-reading.
- [Operating contract](./conventions/operating-contract.md) — the closeout, critique-round,
  and external-boundary floors every item above is measured by.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer rule the
  `git stash` incident tested.
